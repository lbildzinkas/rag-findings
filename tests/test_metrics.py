"""Retrieval recall and precision on hand-built spans: full, partial and
zero overlap, several annotators, cross-document retrieval."""

from __future__ import annotations

import pytest

from rag.chunking import Chunk
from rag.metrics import mean, overlap_tokens, score_fixed_k, score_question


def chunk(doc_id: str, token_start: int, n_tokens: int, index: int = 0) -> Chunk:
    return Chunk(
        doc_id=doc_id,
        index=index,
        start=0,
        end=n_tokens,
        token_start=token_start,
        token_end=token_start + n_tokens,
        n_tokens=n_tokens,
    )


def test_full_overlap():
    gold = frozenset(range(100))
    packed = [chunk("d1", 0, 100)]
    score = score_question([gold], packed, "d1")
    assert score.recall == pytest.approx(1.0)
    assert score.precision == pytest.approx(1.0)
    assert score.annotator == 0


def test_partial_overlap():
    gold = frozenset(range(100))
    packed = [chunk("d1", 50, 100)]  # tokens 50..150
    score = score_question([gold], packed, "d1")
    assert score.recall == pytest.approx(0.5)
    assert score.precision == pytest.approx(0.5)
    assert score.retrieved_tokens == 100


def test_zero_overlap():
    gold = frozenset(range(10))
    packed = [chunk("d1", 100, 10)]
    score = score_question([gold], packed, "d1")
    assert score.recall == 0.0
    assert score.precision == 0.0


def test_empty_retrieval_scores_zero():
    gold = frozenset(range(10))
    score = score_question([gold], [], "d1")
    assert score.recall == 0.0
    assert score.precision == 0.0
    assert score.retrieved_tokens == 0


def test_several_annotators_keep_highest_recall():
    gold_a = frozenset(range(10))
    gold_b = frozenset(range(20, 30))
    packed = [chunk("d1", 20, 10)]
    score = score_question([gold_a, gold_b], packed, "d1")
    assert score.annotator == 1
    assert score.recall == pytest.approx(1.0)
    assert score.precision == pytest.approx(1.0)


def test_annotator_tie_goes_to_earlier_then_precision():
    gold_a = frozenset(range(10))
    gold_c = frozenset(range(5))
    packed = [chunk("d1", 0, 10)]
    # annotator 0: recall 1.0, precision 1.0; annotator 1: recall 1.0, precision 0.5
    score = score_question([gold_a, gold_c], packed, "d1")
    assert score.annotator == 0


def test_other_documents_dilute_precision_but_not_recall():
    gold = frozenset(range(10))
    packed = [chunk("d1", 0, 10), chunk("d2", 0, 30)]
    score = score_question([gold], packed, "d1")
    assert score.recall == pytest.approx(1.0)
    assert score.precision == pytest.approx(10 / 40)
    assert score.retrieved_tokens == 40


def test_disjoint_chunks_of_same_document_union():
    gold = frozenset(range(20))
    packed = [chunk("d1", 0, 10, index=0), chunk("d1", 10, 10, index=1)]
    score = score_question([gold], packed, "d1")
    assert score.recall == pytest.approx(1.0)


def test_overlap_tokens_helper():
    gold = frozenset({1, 5, 9})
    assert overlap_tokens(gold, [(0, 10)]) == 3
    assert overlap_tokens(gold, [(2, 6)]) == 1
    assert overlap_tokens(gold, []) == 0
    assert overlap_tokens((1, 5, 9), [(0, 2), (4, 10)]) == 3  # sorted tuple input


def test_overlap_tokens_counts_overlapping_ranges_once():
    gold = frozenset(range(10))
    assert overlap_tokens(gold, [(0, 6), (4, 10), (2, 3)]) == 10


def test_question_requires_gold():
    with pytest.raises(ValueError):
        score_question([], [], "d1")


def test_mean():
    assert mean([1.0, 0.5, 0.5]) == pytest.approx(2 / 3)
    assert mean([]) == 0.0


def units(doc_id: str, n: int, size: int = 10) -> list[Chunk]:
    return [chunk(doc_id, i * size, size, index=i) for i in range(n)]


def test_fixed_k_hit_and_recall():
    doc_units = units("d1", 5)  # tokens 0-50 in 10-token units
    gold = frozenset(range(10, 30))  # units 1 and 2 relevant
    ranked = [doc_units[4], doc_units[1], doc_units[0], doc_units[2]]
    k1, k2, k4 = score_fixed_k([gold], ranked, doc_units, "d1", [1, 2, 4])
    assert (k1.hit, k1.recall) == (False, 0.0)
    assert (k2.hit, k2.recall) == (True, pytest.approx(0.5))
    assert (k4.hit, k4.recall) == (True, pytest.approx(1.0))
    assert k4.relevant_units == 2


def test_fixed_k_ignores_other_documents_and_keeps_best_annotator():
    doc_units = units("d1", 3)
    other = units("d2", 3)
    gold_a = frozenset(range(5))  # unit 0
    gold_b = frozenset(range(20, 25))  # unit 2
    ranked = [other[0], doc_units[2], doc_units[0]]
    (k2,) = score_fixed_k([gold_a, gold_b], ranked, doc_units, "d1", [2])
    assert k2.hit
    assert k2.recall == pytest.approx(1.0)  # annotator b's only relevant unit is in the top 2
    with pytest.raises(ValueError):
        score_fixed_k([], ranked, doc_units, "d1", [1])
