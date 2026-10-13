"""Shared label structures: labelled spans, questions and their checks.

A labelled span is the exact source text that answers a question,
identified by its document, start and end character offsets, quoted text
and source hash, so it can be scored against any chunking (glossary).
Both datasets build these: QASPER from anchored evidence paragraphs,
Natural Questions from the long-answer paragraph and short-answer spans.

A question keeps one span tuple per usable annotator, so scoring can
keep the best annotator. Two fields are optional and only set by
datasets that have them:

- `query_type`, when the dataset's labels decide it directly (Natural
  Questions: short answer means precise, long-answer-only means context);
  the passage-count rule in `rag.query_type` covers the rest;
- `short_annotators`, per-annotator short-answer spans kept for a
  secondary metric (R6), never for the primary recall and precision.
"""

from __future__ import annotations

from dataclasses import dataclass

from .query_type import query_type


@dataclass(frozen=True)
class LabelledSpan:
    """The exact source text that answers a question."""

    doc_id: str
    start: int
    end: int
    quote: str
    source_hash: str


@dataclass(frozen=True)
class Question:
    question_id: str
    doc_id: str
    split: str
    text: str
    annotators: tuple[tuple[LabelledSpan, ...], ...]
    query_type: str | None = None
    short_annotators: tuple[tuple[LabelledSpan, ...], ...] = ()


def question_query_type(question: Question) -> str:
    """A question's query type: the dataset's own label when its labels
    decide one (Natural Questions), else the passage-count rule."""
    if question.query_type is not None:
        return question.query_type
    return query_type([len(annotator) for annotator in question.annotators])


def verify_spans(split, documents_by_id: dict) -> int:
    """Check every labelled span round-trips; return the number checked.

    A span round-trips when its offsets slice the document's canonical
    text back to its quote and its source hash matches the document's.
    Short-answer spans are checked the same way.
    """
    checked = 0
    for question in split.questions:
        doc = documents_by_id[question.doc_id]
        doc_hash = doc.source_hash
        for annotator in (*question.annotators, *question.short_annotators):
            for span in annotator:
                if doc.text[span.start : span.end] != span.quote:
                    raise ValueError(f"span does not round-trip: {question.question_id}")
                if span.source_hash != doc_hash:
                    raise ValueError(f"span source hash mismatch: {question.question_id}")
                checked += 1
    return checked
