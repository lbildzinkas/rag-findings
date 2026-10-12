"""Retrieval recall and precision against labelled spans.

Both are token overlaps in cl100k tokens, by token position inside the
question's document:

- retrieval recall = share of the question's labelled relevant tokens
  found within the retrieved budget;
- retrieval precision = share of the retrieved tokens that are relevant.

Retrieved chunks from other documents still count toward precision's
denominator (they are retrieved text) but cannot overlap the gold spans.
Each question is scored against each annotator's spans and the annotator
with the highest recall is kept (QASPER convention); ties go to the
earlier annotator, then the higher precision.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .chunking import Chunk


def overlap_tokens(gold: frozenset[int], ranges: Sequence[tuple[int, int]]) -> int:
    """Gold token positions that fall inside any [start, end) token range."""
    return sum(1 for g in gold if any(start <= g < end for start, end in ranges))


@dataclass(frozen=True)
class QuestionScore:
    recall: float
    precision: float
    annotator: int  # index of the kept annotator
    retrieved_tokens: int
    gold_tokens: int


def score_question(
    gold_sets: Sequence[frozenset[int]],
    packed: Sequence[Chunk],
    gold_doc_id: str,
) -> QuestionScore:
    """Score one question: best annotator by recall, then precision."""
    if not gold_sets:
        raise ValueError("a question needs at least one annotator's spans")
    retrieved_tokens = sum(c.n_tokens for c in packed)
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


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0
