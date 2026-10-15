"""QASPER loading: canonical text, evidence anchoring (exact and fuzzy),
exclusions by reason, and span round-trips."""

from __future__ import annotations

from pathlib import Path

from rag.documents import build_document
from rag.qasper import (
    EVIDENCE_UNANCHORED,
    FIGURE_OR_TABLE_ONLY,
    UNANSWERABLE,
    anchor_evidence,
    load_split,
    verify_spans,
)
from tests.conftest import make_answer, make_paper, make_qa, write_split

PARA_A = "Kerberos tickets grant authentication rights through a trusted key distribution center."
PARA_B = "Renewal windows let clients refresh tickets before expiry without re-authenticating."
PARA_C = "Photosynthesis converts light energy into chemical energy inside chloroplasts."


def build_corpus(tmp_path: Path) -> Path:
    papers = {
        "paperA": make_paper(
            "paperA",
            "Kerberos abstract.",
            [("Intro", [PARA_A]), ("Details", [PARA_B])],
            figures_and_tables=[{"file": "f1.png", "caption": "Figure 1: ticket lifetimes."}],
            qas=[
                # exact paragraph evidence
                make_qa("qa1", "how do kerberos tickets work?", [make_answer(evidence=[PARA_A])]),
                # fuzzy evidence: doubled whitespace
                make_qa(
                    "qa2",
                    "how are tickets renewed?",
                    [make_answer(evidence=[PARA_B.replace(" before ", "  before  ")])],
                ),
                # unanswerable
                make_qa("qa3", "what year was it invented?", [make_answer(unanswerable=True)]),
                # figure/table only
                make_qa(
                    "qa4",
                    "what do ticket lifetimes look like?",
                    [make_answer(evidence=["FLOAT SELECTED: Figure 1: ticket lifetimes."])],
                ),
                # section-path evidence only
                make_qa("qa5", "overview of details?", [make_answer(evidence=["Details ::: Intro"])]),
                # unanchored evidence
                make_qa("qa6", "strange question?", [make_answer(evidence=["zebra crossings"])]),
                # two annotators citing different paragraphs: annotator 1 wins on PARA_B
                make_qa(
                    "qa7",
                    "tickets and renewal?",
                    [make_answer(evidence=[PARA_A]), make_answer(evidence=[PARA_B])],
                ),
                # duplicated evidence anchors once
                make_qa("qa8", "renewal windows?", [make_answer(evidence=[PARA_B, PARA_B])]),
            ],
        ),
        "paperB": make_paper(
            "paperB",
            "Photosynthesis abstract.",
            [("Intro", [PARA_C])],
            qas=[
                make_qa("qb1", "what converts light energy?", [make_answer(evidence=[PARA_C])]),
            ],
        ),
    }
    path = tmp_path / "qasper-dev-v0.3.json"
    write_split(path, papers)
    return path


def test_canonical_text_layout(tmp_path):
    path = build_corpus(tmp_path)
    split = load_split("dev", path)
    doc = {d.doc_id: d for d in split.documents}["paperA"]
    assert doc.text == "Kerberos abstract.\n\n" + PARA_A + "\n\n" + PARA_B
    assert [p.section for p in doc.paragraphs] == ["Abstract", "Intro", "Details"]


def test_exact_and_fuzzy_evidence_anchor(tmp_path):
    split = load_split("dev", build_corpus(tmp_path))
    questions = {q.question_id: q for q in split.questions}
    doc = {d.doc_id: d for d in split.documents}["paperA"]

    q1 = questions["qa1"]
    assert q1.annotators[0][0].quote == PARA_A
    assert doc.text[q1.annotators[0][0].start : q1.annotators[0][0].end] == PARA_A

    q2 = questions["qa2"]
    assert q2.annotators[0][0].quote == PARA_B  # fuzzy anchored to the paragraph

    q8 = questions["qa8"]
    assert len(q8.annotators[0]) == 1  # duplicate evidence deduped


def test_exclusions_by_reason(tmp_path):
    split = load_split("dev", build_corpus(tmp_path))
    reasons = {e.question_id: e.reason for e in split.excluded}
    assert reasons["qa3"] == UNANSWERABLE
    assert reasons["qa4"] == FIGURE_OR_TABLE_ONLY
    assert reasons["qa5"] == FIGURE_OR_TABLE_ONLY
    assert reasons["qa6"] == EVIDENCE_UNANCHORED
    included = {q.question_id for q in split.questions}
    assert included == {"qa1", "qa2", "qa7", "qa8", "qb1"}


def test_multi_annotator_spans_kept_separately(tmp_path):
    split = load_split("dev", build_corpus(tmp_path))
    q7 = {q.question_id: q for q in split.questions}["qa7"]
    assert len(q7.annotators) == 2
    assert q7.annotators[0][0].quote == PARA_A
    assert q7.annotators[1][0].quote == PARA_B


def test_every_span_round_trips(tmp_path):
    path = build_corpus(tmp_path)
    split = load_split("dev", path)
    documents = {d.doc_id: d for d in split.documents}
    checked = verify_spans(split, documents)
    assert checked == 6  # qa1, qa2, qa7 (x2), qa8, qb1


def test_dataset_hash_is_file_hash(tmp_path):
    import hashlib

    path = build_corpus(tmp_path)
    split = load_split("dev", path)
    assert split.dataset_hash == hashlib.sha256(path.read_bytes()).hexdigest()


def test_answerable_but_evidenceless_counts_unanswerable(tmp_path):
    papers = {
        "paperA": make_paper(
            "paperA",
            "Abstract.",
            [("Intro", [PARA_A])],
            qas=[make_qa("qz", "what?", [make_answer(evidence=[])])],
        )
    }
    path = tmp_path / "qasper-dev-v0.3.json"
    write_split(path, papers)
    split = load_split("dev", path)
    assert [e.reason for e in split.excluded] == [UNANSWERABLE]


def test_anchor_evidence_direct_cases():
    doc = build_document("d", "abs", [("S", [PARA_A, PARA_B])])
    spans = doc.paragraph_spans()
    paragraphs = [p.text for p in doc.paragraphs]
    assert anchor_evidence(PARA_A, spans, paragraphs, []).kind == "paragraph"
    assert anchor_evidence(PARA_A.replace(" rights", "  rights"), spans, paragraphs, []).kind == "paragraph"
    assert anchor_evidence("FLOAT SELECTED: Figure 1", spans, paragraphs, ["Figure 1"]).kind == "figure_table"
    assert anchor_evidence("S ::: T", spans, paragraphs, []).kind == "section"
    assert anchor_evidence("totally unrelated zebra", spans, paragraphs, []).kind == "unanchored"
    # float prefix stripped before paragraph matching
    anchor = anchor_evidence("FLOAT SELECTED: " + PARA_B, spans, paragraphs, [])
    assert anchor.kind == "paragraph"
    assert anchor.span == spans[2]


def test_answer_reference_direct_cases():
    from rag.qasper import answer_reference

    assert answer_reference({"unanswerable": True, "extractive_spans": [], "free_form_answer": "", "yes_no": None}) is None
    assert (
        answer_reference({"unanswerable": False, "extractive_spans": ["BIBREF19", "BIBREF20"], "free_form_answer": "", "yes_no": None})
        == "BIBREF19, BIBREF20"  # the QASPER evaluator's join
    )
    assert answer_reference({"unanswerable": False, "extractive_spans": [], "free_form_answer": "about 40%", "yes_no": None}) == "about 40%"
    assert answer_reference({"unanswerable": False, "extractive_spans": [], "free_form_answer": "", "yes_no": True}) == "Yes"
    # yes_no False means a "No" answer; truthiness must not decide
    assert answer_reference({"unanswerable": False, "extractive_spans": [], "free_form_answer": "", "yes_no": False}) == "No"
    assert answer_reference({"unanswerable": False, "extractive_spans": [], "free_form_answer": "", "yes_no": None}) is None


def test_references_loaded_per_answering_annotator(tmp_path):
    papers = {
        "paperR": make_paper(
            "paperR",
            "Abstract.",
            [("S", [PARA_A])],
            qas=[
                make_qa(
                    "qr1",
                    "what is the answer?",
                    [
                        make_answer(evidence=[PARA_A], extractive_spans=["span one", "span two"]),
                        make_answer(evidence=[PARA_A], free_form_answer="free form"),
                        make_answer(evidence=[PARA_A], yes_no=True),
                        make_answer(evidence=[PARA_A], yes_no=False),
                        make_answer(unanswerable=True),
                    ],
                )
            ],
        )
    }
    path = tmp_path / "qasper-dev-v0.3.json"
    write_split(path, papers)
    split = load_split("dev", path)
    (question,) = split.questions
    assert question.references == ("span one, span two", "free form", "Yes", "No")
    assert split.evidence_counts["answer_extractive"] == 1
    assert split.evidence_counts["answer_free_form"] == 1
    assert split.evidence_counts["answer_yes_no"] == 2  # True and False both count
