"""Retrieval recall and precision against labelled spans.

Both are token overlaps in cl100k tokens, by token position inside the
question's document:

- retrieval recall = share of the question's labelled relevant tokens
  found within the retrieved budget;
- retrieval precision = share of the retrieved tokens that are relevant.

Retrieved chunks from other documents still count toward precision's
denominator (they are retrieved text) but cannot overlap the gold spans.
When the packed chunks overlap (the v2 routers mix chunkings), precision's
denominator counts every retrieved token once: pass `union_token_count`
to `score_question` as the retrieved-token count. Each question is
scored against each annotator's spans and the annotator with the highest
recall is kept (QASPER convention); ties go to the earlier annotator,
then the higher precision.

Fixed-k measures (for comparison with the literature only) work on whole
retrieved units, with no token budget: a unit is relevant when it
overlaps the annotator's labelled spans; hit@k is whether any of the top
k units is relevant, and recall@k the share of the document's relevant
units found in the top k. The annotator with the highest recall@k is kept.
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from .chunking import Chunk


def _merged(ranges: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def overlap_tokens(gold: Collection[int], ranges: Sequence[tuple[int, int]]) -> int:
    """Gold token positions that fall inside any [start, end) token range.

    `gold` may be any collection; a sorted tuple avoids re-sorting it."""
    positions = gold if isinstance(gold, tuple) else tuple(sorted(gold))
    return sum(bisect_left(positions, end) - bisect_left(positions, start) for start, end in _merged(ranges))


@dataclass(frozen=True)
class QuestionScore:
    recall: float
    precision: float
    annotator: int  # index of the kept annotator
    retrieved_tokens: int
    gold_tokens: int


def union_token_count(packed: Sequence[Chunk]) -> int:
    """Tokens covered by the packed chunks, counting overlapping text once:
    the union of their token ranges per document (chunks of different
    documents never overlap). Single chunkings never overlap, so this
    equals the sum of their chunks' tokens there."""
    by_doc: dict[str, list[tuple[int, int]]] = {}
    for chunk in packed:
        by_doc.setdefault(chunk.doc_id, []).append(chunk.token_span)
    return sum(e - s for ranges in by_doc.values() for s, e in _merged(ranges))


def score_question(
    gold_sets: Sequence[Collection[int]],
    packed: Sequence[Chunk],
    gold_doc_id: str,
    retrieved: int | None = None,
) -> QuestionScore:
    """Score one question: best annotator by recall, then precision.

    `retrieved` overrides the retrieved-token count (the default sums the
    packed chunks' tokens); the routers pass the union of the packed token
    ranges, so overlapping chunks count once in precision's denominator."""
    if not gold_sets:
        raise ValueError("a question needs at least one annotator's spans")
    retrieved_tokens = sum(c.n_tokens for c in packed) if retrieved is None else retrieved
    ranges = [(c.token_start, c.token_end) for c in packed if c.doc_id == gold_doc_id]

    best: QuestionScore | None = None
    for i, gold in enumerate(gold_sets):
        gold_n = len(gold)
        overlap = overlap_tokens(gold, ranges)
        recall = overlap / gold_n if gold_n else 0.0
        precision = overlap / retrieved_tokens if retrieved_tokens else 0.0
        candidate = QuestionScore(
            recall=recall,
            precision=precision,
            annotator=i,
            retrieved_tokens=retrieved_tokens,
            gold_tokens=gold_n,
        )
        if best is None or (candidate.recall, candidate.precision) > (best.recall, best.precision):
            best = candidate
    assert best is not None
    return best


@dataclass(frozen=True)
class FixedKScore:
    k: int
    hit: bool
    recall: float
    relevant_units: int


def score_fixed_k(
    gold_sets: Sequence[Collection[int]],
    ranked_units: Sequence[Chunk],
    doc_units: Sequence[Chunk],
    gold_doc_id: str,
    ks: Sequence[int],
) -> list[FixedKScore]:
    """hit@k and recall@k for each k, over whole retrieved units.

    `ranked_units` are the retrieved units in rank order (distinct, from
    any document); `doc_units` are all units of the question's document.
    """
    if not gold_sets:
        raise ValueError("a question needs at least one annotator's spans")
    relevant_sets = [{u.index for u in doc_units if overlap_tokens(gold, [u.token_span])} for gold in gold_sets]
    scores: list[FixedKScore] = []
    for k in ks:
        top = {u.index for u in ranked_units[:k] if u.doc_id == gold_doc_id}
        best: FixedKScore | None = None
        for relevant in relevant_sets:
            found = top & relevant
            candidate = FixedKScore(
                k=k,
                hit=bool(found),
                recall=len(found) / len(relevant) if relevant else 0.0,
                relevant_units=len(relevant),
            )
            if best is None or (candidate.recall, candidate.hit) > (best.recall, best.hit):
                best = candidate
        assert best is not None
        scores.append(best)
    return scores


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0
