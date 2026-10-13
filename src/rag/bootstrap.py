"""Paired, document-clustered bootstrap of the best single chunking, the
oracle router and the chunk size x query type interaction.

Dataset-agnostic core: one cell is a recall matrix (questions x
chunkings, columns ordered smallest chunk first), each question's
cluster (its document) and query type. Every statistic is computed from
per-cluster sums, once on the original sample (weight 1 per cluster) and
once per resample (the number of times each cluster was drawn), so the
point estimate and the resamples share one code path. Clusters are drawn
with replacement, and all statistics of a resample use the same draw
(paired).

- The best single chunking is the one with the highest mean recall; it is
  re-selected inside every resample, so the selection is part of each
  interval.
- The oracle router takes, per question, the chunking with the highest
  recall; ties go to the smaller chunk (the first column).
- The query-type oracle takes the best chunking per labelled query type.
- The interaction of chunking c against a smaller reference r is
  [mean(c) - mean(r) | context] - [mean(c) - mean(r) | precise].

Ties are exact float equality: recall is a ratio of token counts, so equal
retrieved text gives equal floats.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .query_type import CONTEXT, PRECISE, QUERY_TYPES

_PRECISE = QUERY_TYPES.index(PRECISE)
_CONTEXT = QUERY_TYPES.index(CONTEXT)


def resample_counts(n_clusters: int, resamples: int, seed: int, stratum: str) -> np.ndarray:
    """(resamples, n_clusters): how often each cluster is drawn when
    n_clusters clusters are drawn with replacement. The stream depends only
    on (seed, stratum), so a dataset's draws are the same whether or not
    other datasets are pooled with it."""
    if n_clusters <= 0 or resamples <= 0:
        raise ValueError("resample_counts needs at least one cluster and one resample")
    key = int.from_bytes(hashlib.sha256(stratum.encode("utf-8")).digest()[:8], "big")
    rng = np.random.default_rng([seed, key])
    return rng.multinomial(n_clusters, np.full(n_clusters, 1.0 / n_clusters), size=resamples).astype(np.float64)


@dataclass(frozen=True)
class Estimate:
    """A point estimate on the original sample and its bootstrap replicates."""

    point: float
    samples: np.ndarray


@dataclass(frozen=True)
class Interaction:
    delta_context: Estimate
    delta_precise: Estimate
    interaction: Estimate


@dataclass(frozen=True)
class CellAnalysis:
    means: np.ndarray  # (chunkings,) mean recall on the original sample
    best: int  # best single chunking
    best_share: np.ndarray  # (chunkings,) share of resamples where each was the best single chunking
    oracle: float  # oracle router mean recall
    headroom: Estimate  # oracle router minus best single chunking
    differences: tuple[Estimate, ...]  # per chunking: its mean minus the best single chunking's
    picks: np.ndarray  # (questions,) the oracle router's chunking per question
    all_tied: np.ndarray  # (questions,) every chunking scored the same for the question
    type_best: dict[str, int]  # query-type oracle: best chunking per query type present
    type_oracle: float  # query-type oracle mean recall
    oracle_gap: Estimate  # oracle router minus query-type oracle
    type_headroom: Estimate  # query-type oracle minus best single chunking
    interactions: dict[int, Interaction]  # chunking -> its interaction against the reference


def analyse_cell(
    recall: np.ndarray,
    cluster: np.ndarray,
    qtype: np.ndarray,
    counts: np.ndarray,
    reference: int | None = None,
) -> CellAnalysis:
    """Bootstrap one cell.

    recall: (questions, chunkings), columns smallest chunk first;
    cluster: (questions,) cluster index in [0, clusters);
    qtype: (questions,) index into QUERY_TYPES;
    counts: (resamples, clusters) draws per cluster, from resample_counts;
    reference: column of the smaller chunking the interactions are taken
    against (None: no interactions).
    """
    n_questions, n_chunkings = recall.shape
    if n_questions == 0 or n_chunkings == 0:
        raise ValueError("a cell needs at least one question and one chunking")
    if cluster.shape != (n_questions,) or qtype.shape != (n_questions,):
        raise ValueError("cluster and qtype need one entry per question")
    n_clusters = counts.shape[1]
    if cluster.min() < 0 or cluster.max() >= n_clusters:
        raise ValueError("cluster index outside the resampled clusters")

    oracle_q = recall.max(axis=1)
    picks = np.argmax(recall, axis=1)  # first maximum: the smaller chunk wins ties
    all_tied = (recall == oracle_q[:, None]).all(axis=1)

    n_types = len(QUERY_TYPES)
    onehot = (qtype[:, None] == np.arange(n_types)[None, :]).astype(np.float64)
    per_question = np.hstack([recall * onehot[:, [t]] for t in range(n_types)] + [oracle_q[:, None], onehot])
    per_cluster = np.zeros((n_clusters, per_question.shape[1]))
    np.add.at(per_cluster, cluster, per_question)

    # row 0: the original sample; rows 1..: the resamples
    weights = np.vstack([np.ones((1, n_clusters)), counts])
    sums = weights @ per_cluster
    by_type = [sums[:, t * n_chunkings : (t + 1) * n_chunkings] for t in range(n_types)]
    total = np.sum(by_type, axis=0)
    oracle_sum = sums[:, n_types * n_chunkings]
    type_n = sums[:, n_types * n_chunkings + 1 :]
    n = type_n.sum(axis=1)

    means = total / n[:, None]
    best = np.argmax(total, axis=1)  # re-selected in every resample
    best_mean = np.take_along_axis(means, best[:, None], axis=1)[:, 0]
    oracle = oracle_sum / n
    type_oracle = np.sum([s.max(axis=1) for s in by_type], axis=0) / n

    def estimate(values: np.ndarray) -> Estimate:
        return Estimate(point=float(values[0]), samples=values[1:])

    present = [t for t in range(n_types) if type_n[0, t] > 0]
    interactions: dict[int, Interaction] = {}
    if reference is not None and type_n[0, _PRECISE] > 0 and type_n[0, _CONTEXT] > 0:
        if (type_n[:, _PRECISE] == 0).any() or (type_n[:, _CONTEXT] == 0).any():
            raise ValueError("a resample drew no precise or no context question; the interaction is undefined")
        context = by_type[_CONTEXT] / type_n[:, [_CONTEXT]]
        precise = by_type[_PRECISE] / type_n[:, [_PRECISE]]
        for c in range(n_chunkings):
            if c == reference:
                continue
            d_context = context[:, c] - context[:, reference]
            d_precise = precise[:, c] - precise[:, reference]
            interactions[c] = Interaction(
                delta_context=estimate(d_context),
                delta_precise=estimate(d_precise),
                interaction=estimate(d_context - d_precise),
            )

    resampled_best = best[1:]
    return CellAnalysis(
        means=means[0],
        best=int(best[0]),
        best_share=np.bincount(resampled_best, minlength=n_chunkings) / len(resampled_best),
        oracle=float(oracle[0]),
        headroom=estimate(oracle - best_mean),
        differences=tuple(estimate(means[:, c] - best_mean) for c in range(n_chunkings)),
        picks=picks,
        all_tied=all_tied,
        type_best={QUERY_TYPES[t]: int(np.argmax(by_type[t][0])) for t in present},
        type_oracle=float(type_oracle[0]),
        oracle_gap=estimate(oracle - type_oracle),
        type_headroom=estimate(type_oracle - best_mean),
        interactions=interactions,
    )


@dataclass(frozen=True)
class Interval:
    low: float
    high: float
    confidence: float

    @property
    def excludes_zero(self) -> bool:
        return self.low > 0 or self.high < 0


def percentile_interval(samples: np.ndarray, confidence: float) -> Interval:
    alpha = 1.0 - confidence
    low, high = np.quantile(samples, [alpha / 2, 1 - alpha / 2])
    return Interval(low=float(low), high=float(high), confidence=confidence)


def bootstrap_p(samples: np.ndarray) -> float:
    """Two-sided bootstrap p-value for a statistic of 0."""
    return float(min(1.0, 2 * min(np.mean(samples <= 0), np.mean(samples >= 0))))


def holm_intervals(samples: Sequence[np.ndarray], confidence: float) -> list[Interval]:
    """Holm-adjusted percentile intervals for a family of statistics.

    In ascending order of bootstrap p-value, the i-th of m statistics gets
    the interval at level alpha / (m - i + 1). Once one interval covers 0,
    Holm stops rejecting, so it and every later statistic keep that level
    (none of them can then exclude 0)."""
    alpha = 1.0 - confidence
    m = len(samples)
    order = sorted(range(m), key=lambda i: (bootstrap_p(samples[i]), i))
    out: list[Interval | None] = [None] * m
    stopped_alpha: float | None = None
    for rank, i in enumerate(order):
        step_alpha = stopped_alpha if stopped_alpha is not None else alpha / (m - rank)
        interval = percentile_interval(samples[i], 1.0 - step_alpha)
        if stopped_alpha is None and not interval.excludes_zero:
            stopped_alpha = step_alpha
        out[i] = interval
    return [interval for interval in out if interval is not None]
