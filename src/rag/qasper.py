"""QASPER v0.3 loading: canonical documents, labelled spans, exclusions.

For every paper the canonical text is the abstract followed by every
section paragraph joined with blank lines. Every answerable question's
evidence is anchored into that text:

- an evidence string equal to a paragraph anchors exactly, at that
  paragraph's character span;
- otherwise a fuzzy fallback anchors it to the best-matching paragraph
  (difflib similarity >= 0.8), covering the 7-8.5% of evidence strings
  that differ by whitespace or encoding;
- `FLOAT SELECTED: <caption>` strings cite a figure or table, and
  `section ::: subsection` strings cite a section, so neither anchors
  into the canonical text.

A question is kept when at least one annotator has a paragraph-anchored
span; questions whose answers are all unanswerable, or whose evidence is
only figures, tables or sections, are excluded and counted by reason.

Each answering annotator also contributes one reference answer for the
reader stage (never read by retrieval): the extractive spans joined
with ", " (the QASPER evaluator's convention), else the free-form
answer, else "Yes"/"No". The three fields never co-occur in QASPER,
so the order does not change the references. Unanswerable annotations
are not references.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .documents import Document, build_document
from .labels import LabelledSpan, Question, verify_spans

__all__ = [
    "ExcludedQuestion",
    "LabelledSpan",
    "QasperSplit",
    "Question",
    "anchor_evidence",
    "load_split",
    "verify_spans",
]

FUZZY_THRESHOLD = 0.8
FLOAT_PREFIX = "FLOAT SELECTED: "
SECTION_MARK = " ::: "

UNANSWERABLE = "unanswerable"
FIGURE_OR_TABLE_ONLY = "figure_or_table_only"
EVIDENCE_UNANCHORED = "evidence_unanchored"


@dataclass(frozen=True)
class ExcludedQuestion:
    question_id: str
    doc_id: str
    split: str
    reason: str


@dataclass(frozen=True)
class QasperSplit:
    split: str
    documents: tuple[Document, ...]
    questions: tuple[Question, ...]
    excluded: tuple[ExcludedQuestion, ...]
    dataset_hash: str
    evidence_counts: dict[str, int]
    dataset: str = "qasper"


@dataclass
class _Anchor:
    """Resolution of one evidence string."""

    span: tuple[int, int] | None  # paragraph char span, when anchored
    kind: str  # paragraph | figure_table | section | unanchored
    method: str = "exact"  # how a paragraph anchor was found: exact | fuzzy


def _best_fuzzy_paragraph(ev: str, paragraphs: list[str]) -> tuple[float, int]:
    """Best difflib similarity of ev against the paper's paragraphs."""
    best_ratio = 0.0
    best_index = -1
    for i, para in enumerate(paragraphs):
        matcher = difflib.SequenceMatcher(None, ev, para)
        if matcher.real_quick_ratio() < FUZZY_THRESHOLD or matcher.quick_ratio() < FUZZY_THRESHOLD:
            continue
        ratio = matcher.ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_index = i
    return best_ratio, best_index


def anchor_evidence(
    ev: str,
    paragraph_spans: list[tuple[int, int]],
    paragraphs: list[str],
    captions: list[str],
) -> _Anchor:
    """Anchor one evidence string into the canonical text (or classify it)."""
    candidate = ev
    stripped_float = False
    if candidate.startswith(FLOAT_PREFIX):
        candidate = candidate[len(FLOAT_PREFIX) :]
        stripped_float = True
    for i, para in enumerate(paragraphs):
        if candidate == para:
            return _Anchor(span=paragraph_spans[i], kind="paragraph", method="exact")
    if stripped_float and any(candidate == c for c in captions):
        return _Anchor(span=None, kind="figure_table")
    if not stripped_float and SECTION_MARK in ev:
        return _Anchor(span=None, kind="section")
    ratio, i = _best_fuzzy_paragraph(candidate, paragraphs)
    if i >= 0 and ratio >= FUZZY_THRESHOLD:
        return _Anchor(span=paragraph_spans[i], kind="paragraph", method="fuzzy")
    return _Anchor(span=None, kind="figure_table" if stripped_float else "unanchored")


def answer_reference(ans: dict) -> str | None:
    """One answering annotation's reference answer, or None.

    Extractive spans join with ", " (the QASPER evaluator's convention);
    `yes_no` is a JSON boolean (`False` means "No", so truthiness must
    not decide); an annotation with no answer text at all is no
    reference.
    """
    if ans.get("unanswerable", False):
        return None
    spans = ans.get("extractive_spans") or []
    if spans:
        return ", ".join(spans)
    free_form = ans.get("free_form_answer") or ""
    if free_form:
        return free_form
    yes_no = ans.get("yes_no")
    if yes_no is None:
        return None
    return "Yes" if yes_no else "No"


def load_split(split: str, path: Path) -> QasperSplit:
    """Load one QASPER split json into documents, questions and exclusions."""
    dataset_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    raw = json.loads(path.read_text(encoding="utf-8"))

    documents: list[Document] = []
    questions: list[Question] = []
    excluded: list[ExcludedQuestion] = []
    evidence_counts: dict[str, int] = {
        "paragraph_exact": 0,
        "paragraph_fuzzy": 0,
        "figure_table": 0,
        "section": 0,
        "unanchored": 0,
        "answer_extractive": 0,
        "answer_free_form": 0,
        "answer_yes_no": 0,
    }

    for doc_id in sorted(raw):
        paper = raw[doc_id]
        sections = [(sec["section_name"] or "", sec["paragraphs"]) for sec in paper.get("full_text", [])]
        doc = build_document(doc_id, paper.get("abstract", ""), sections, title=paper.get("title") or "")
        documents.append(doc)
        paragraph_spans = doc.paragraph_spans()
        paragraphs = [p.text for p in doc.paragraphs]
        captions = [ft.get("caption", "") for ft in paper.get("figures_and_tables", [])]

        for qa in paper.get("qas", []):
            question_id = qa["question_id"]
            annotator_spans: list[tuple[LabelledSpan, ...]] = []
            references: list[tuple[str, str]] = []  # (reference answer, its kind)
            any_answerable = False
            any_figure_table = False
            any_section = False
            any_unanchored = False
            for answer in qa.get("answers", []):
                ans = answer["answer"]
                if ans.get("unanswerable", False):
                    continue
                any_answerable = True
                reference = answer_reference(ans)
                if reference is not None:
                    kind = (
                        "answer_extractive"
                        if ans.get("extractive_spans")
                        else "answer_free_form"
                        if ans.get("free_form_answer")
                        else "answer_yes_no"
                    )
                    references.append((reference, kind))
                spans: list[LabelledSpan] = []
                for ev in ans.get("evidence", []):
                    anchor = anchor_evidence(ev, paragraph_spans, paragraphs, captions)
                    key = f"paragraph_{anchor.method}" if anchor.kind == "paragraph" else anchor.kind
                    evidence_counts[key] += 1
                    if anchor.kind == "paragraph":
                        assert anchor.span is not None
                        start, end = anchor.span
                        spans.append(
                            LabelledSpan(
                                doc_id=doc_id,
                                start=start,
                                end=end,
                                quote=doc.text[start:end],
                                source_hash=doc.source_hash,
                            )
                        )
                    elif anchor.kind == "figure_table":
                        any_figure_table = True
                    elif anchor.kind == "section":
                        any_section = True
                    else:
                        any_unanchored = True
                if spans:
                    deduped = tuple(sorted(set(spans), key=lambda s: (s.start, s.end)))
                    annotator_spans.append(deduped)

            if annotator_spans:
                for _, kind in references:
                    evidence_counts[kind] += 1
                questions.append(
                    Question(
                        question_id=question_id,
                        doc_id=doc_id,
                        split=split,
                        text=qa["question"],
                        annotators=tuple(annotator_spans),
                        references=tuple(reference for reference, _ in references),
                    )
                )
            elif any_answerable and (any_figure_table or any_section or any_unanchored):
                reason = FIGURE_OR_TABLE_ONLY if (any_figure_table or any_section) else EVIDENCE_UNANCHORED
                excluded.append(ExcludedQuestion(question_id=question_id, doc_id=doc_id, split=split, reason=reason))
            else:
                excluded.append(
                    ExcludedQuestion(question_id=question_id, doc_id=doc_id, split=split, reason=UNANSWERABLE)
                )

    return QasperSplit(
        split=split,
        documents=tuple(documents),
        questions=tuple(questions),
        excluded=tuple(excluded),
        dataset_hash=dataset_hash,
        evidence_counts=evidence_counts,
        dataset="qasper",
    )
