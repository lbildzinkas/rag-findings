"""The document-clustered bootstrap on synthetic cells with known answers:
zero headroom, clustering widening the CI, re-selection of the best single
chunking inside every resample, tie-breaks, the query-type oracle, the
interaction and Holm-adjusted intervals."""

from __future__ import annotations

import numpy as np
import pytest

from rag.bootstrap import (
    analyse_cell,
    bootstrap_p,
    holm_intervals,
    percentile_interval,
    resample_counts,
)
from rag.query_type import QUERY_TYPES

PRECISE, CONTEXT, MIXED = (QUERY_TYPES.index(t) for t in ("precise", "context", "mixed"))


def _cell(n_docs: int, per_doc: int, seed: int = 1):
    rng = np.random.default_rng(seed)
    cluster = np.repeat(np.arange(n_docs), per_doc)
    qtype = rng.integers(0, 2, size=n_docs * per_doc)  # precise and context only
    return rng, cluster, qtype


def test_resample_counts_draw_every_cluster_count_with_replacement():
    counts = resample_counts(7, 500, seed=3, stratum="qasper")
    assert counts.shape == (500, 7)
    assert (counts.sum(axis=1) == 7).all()
    assert np.array_equal(counts, resample_counts(7, 500, seed=3, stratum="qasper"))
    assert not np.array_equal(counts, resample_counts(7, 500, seed=4, stratum="qasper"))
    assert not np.array_equal(counts, resample_counts(7, 500, seed=3, stratum="nq"))
    with pytest.raises(ValueError):
        resample_counts(0, 10, seed=0, stratum="qasper")


def test_zero_headroom_gives_a_ci_covering_zero():
    rng, cluster, qtype = _cell(40, 5)
    small = rng.uniform(0.2, 1.0, size=len(cluster))
    recall = np.column_stack([small, small * 0.5])  # the first chunking is never beaten
    analysis = analyse_cell(recall, cluster, qtype, resample_counts(40, 2000, 0, "s"))
    assert analysis.headroom.point == 0.0
    assert analysis.oracle == pytest.approx(analysis.means[0])
    interval = percentile_interval(analysis.headroom.samples, 0.95)
    assert interval.low <= 0.0 <= interval.high
    assert not interval.excludes_zero


def test_identical_chunkings_have_zero_headroom_and_tie_to_the_smaller():
    rng, cluster, qtype = _cell(20, 4)
    column = rng.uniform(size=len(cluster))
    analysis = analyse_cell(np.column_stack([column, column, column]), cluster, qtype, resample_counts(20, 500, 0, "s"))
    assert analysis.best == 0
    assert (analysis.picks == 0).all()
    assert analysis.all_tied.all()
    assert np.allclose(analysis.headroom.samples, 0.0)


def test_clustered_data_gives_wider_cis_than_unclustered():
    n_docs, per_doc = 60, 10
    rng, cluster, qtype = _cell(n_docs, per_doc, seed=7)
    base = rng.uniform(0.3, 0.7, size=len(cluster))
    doc_effect = rng.normal(0.0, 0.2, size=n_docs)[cluster]  # questions on one document move together
    other = np.clip(base + doc_effect + rng.normal(0.0, 0.02, size=len(cluster)), 0.0, 1.0)
    recall = np.column_stack([base, other])

    by_document = analyse_cell(recall, cluster, qtype, resample_counts(n_docs, 4000, 0, "docs"))
    by_question = analyse_cell(
        recall, np.arange(len(cluster)), qtype, resample_counts(len(cluster), 4000, 0, "questions")
    )

    def width(samples):
        interval = percentile_interval(samples, 0.95)
        return interval.high - interval.low

    worse = 1 - by_document.best
    assert by_document.headroom.point == pytest.approx(by_question.headroom.point)
    assert width(by_document.headroom.samples) > 1.5 * width(by_question.headroom.samples)
    assert width(by_document.differences[worse].samples) > 1.5 * width(by_question.differences[worse].samples)


def test_best_single_chunking_is_reselected_inside_every_resample():
    n_docs = 30
    rng, cluster, qtype = _cell(n_docs, 4, seed=11)
    a = rng.uniform(size=len(cluster))
    b = np.clip(a + rng.normal(0.0, 0.3, size=len(cluster)), 0.0, 1.0)
    b += a.mean() - b.mean()  # equal means: the best flips between resamples
    recall = np.column_stack([a, b])
    counts = resample_counts(n_docs, 300, 0, "s")
    analysis = analyse_cell(recall, cluster, qtype, counts)

    assert analysis.best_share.sum() == pytest.approx(1.0)
    assert 0.05 < analysis.best_share[0] < 0.95  # each chunking is the best in some resamples
    oracle = recall.max(axis=1)
    for row, weights in enumerate(counts):
        w = weights[cluster]
        means = (w[:, None] * recall).sum(axis=0) / w.sum()
        expected = (w * oracle).sum() / w.sum() - means.max()
        assert analysis.headroom.samples[row] == pytest.approx(expected)
        assert analysis.differences[0].samples[row] == pytest.approx(means[0] - means.max())


def test_oracle_ties_go_to_the_smaller_chunk():
    recall = np.array([[0.5, 0.5, 0.2], [0.1, 0.9, 0.9], [0.0, 0.0, 0.0], [0.3, 0.4, 0.8]])
    cluster = np.array([0, 1, 2, 3])
    qtype = np.array([PRECISE, CONTEXT, PRECISE, CONTEXT])
    analysis = analyse_cell(recall, cluster, qtype, resample_counts(4, 50, 0, "s"))
    assert analysis.picks.tolist() == [0, 1, 0, 2]
    assert analysis.all_tied.tolist() == [False, False, True, False]
    assert analysis.oracle == pytest.approx((0.5 + 0.9 + 0.0 + 0.8) / 4)
    assert analysis.best == 2  # means 0.225, 0.45, 0.475
    assert analysis.headroom.point == pytest.approx(analysis.oracle - 0.475)


def test_query_type_oracle_and_interaction_point_estimates():
    # precise questions favour the small chunk, context questions the large one
    # (repeated over 100 documents, so every resample draws both query types)
    recall = np.tile([[0.8, 0.4], [0.6, 0.2], [0.2, 0.7], [0.3, 0.9], [0.5, 0.5]], (20, 1))
    cluster = np.arange(100)
    qtype = np.tile([PRECISE, PRECISE, CONTEXT, CONTEXT, MIXED], 20)
    analysis = analyse_cell(recall, cluster, qtype, resample_counts(100, 400, 0, "s"), reference=0)

    assert analysis.type_best == {"precise": 0, "context": 1, "mixed": 0}
    assert analysis.type_oracle == pytest.approx((0.8 + 0.6 + 0.7 + 0.9 + 0.5) / 5)
    assert analysis.oracle_gap.point == pytest.approx(analysis.oracle - analysis.type_oracle)
    interaction = analysis.interactions[1]
    assert interaction.delta_context.point == pytest.approx(0.8 - 0.25)
    assert interaction.delta_precise.point == pytest.approx(0.3 - 0.7)
    assert interaction.interaction.point == pytest.approx(0.55 + 0.4)
    assert 0 not in analysis.interactions  # the reference has no interaction with itself


def test_no_interaction_without_both_query_types():
    recall = np.array([[0.1, 0.2], [0.3, 0.4]])
    analysis = analyse_cell(recall, np.array([0, 1]), np.array([PRECISE, PRECISE]), resample_counts(2, 20, 0, "s"), 0)
    assert analysis.interactions == {}
    assert analysis.type_best == {"precise": 1}


def test_invalid_cells_are_rejected():
    counts = resample_counts(2, 10, 0, "s")
    with pytest.raises(ValueError):
        analyse_cell(np.zeros((0, 2)), np.array([], dtype=int), np.array([], dtype=int), counts)
    with pytest.raises(ValueError):
        analyse_cell(np.zeros((2, 2)), np.array([0, 5]), np.array([PRECISE, CONTEXT]), counts)


def test_bootstrap_p_value():
    assert bootstrap_p(np.array([1.0, 2.0, 3.0, 4.0])) == 0.0
    assert bootstrap_p(np.zeros(10)) == 1.0
    assert bootstrap_p(np.array([-1.0, 1.0, 2.0, 3.0])) == pytest.approx(0.5)


def test_holm_intervals_step_down_and_stop_at_the_first_non_rejection():
    rng = np.random.default_rng(0)
    strong = rng.normal(1.0, 0.1, size=5000)
    weaker = rng.normal(0.5, 0.1, size=5000)
    null = rng.normal(0.0, 0.1, size=5000)
    later = rng.normal(0.05, 0.1, size=5000)
    intervals = holm_intervals([null, strong, weaker, later], 0.95)

    # strong and weaker are rejected first, at 0.05/4 and 0.05/3; the null stops Holm at 0.05/2 and later keeps it
    levels = {round(1 - i.confidence, 6) for i in intervals}
    assert levels == {round(0.05 / 4, 6), round(0.05 / 3, 6), round(0.05 / 2, 6)}
    assert intervals[1].excludes_zero and intervals[2].excludes_zero
    assert not intervals[0].excludes_zero and not intervals[3].excludes_zero
    assert intervals[0].confidence == intervals[3].confidence
    assert intervals[1].confidence > intervals[2].confidence  # the first step is the strictest
    assert holm_intervals([], 0.95) == []
