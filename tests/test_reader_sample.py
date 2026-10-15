"""The reader sample: whole QASPER papers in seeded order with the
overshoot-skip rule, per-type Natural Questions pages, and the committed
id list's round trip."""

from __future__ import annotations

from types import SimpleNamespace

from rag.labels import LabelledSpan, Question
from rag.reader_sample import (
    draw_nq_sample,
    draw_qasper_sample,
    draw_reader_sample,
    read_sample,
    reference_counts,
    write_sample,
)

SPAN = LabelledSpan(doc_id="d", start=0, end=1, quote="x", source_hash="h")


def qasper_paper(doc_id: str, n: int) -> list[Question]:
    return [
        Question(question_id=f"{doc_id}-q{i}", doc_id=doc_id, split="dev", text="?", annotators=((SPAN,),))
        for i in range(n)
    ]


def nq_question(question_id: str, query_type: str, with_short: bool = False) -> Question:
    return Question(
        question_id=question_id,
        doc_id=question_id,  # one question per page
        split="dev",
        text="?",
        annotators=((SPAN,),),
        query_type=query_type,
        short_annotators=((SPAN,),) if with_short else (),
    )


def test_qasper_sample_takes_whole_papers_and_skips_overshooters():
    # sizes 1, 2, 2: every seeded order fills exactly 5 with whole papers
    questions = [*qasper_paper("a", 1), *qasper_paper("b", 2), *qasper_paper("c", 2)]
    drawn = draw_qasper_sample(questions, seed=0, per_dataset=5)
    assert len(drawn) == 5
    papers = {qid.rsplit("-q", 1)[0] for qid in drawn}
    assert papers == {"a", "b", "c"}
    assert draw_qasper_sample(questions, seed=0, per_dataset=5) == drawn  # reproducible from the seed
    for seed in range(5):
        assert len(draw_qasper_sample(questions, seed=seed, per_dataset=5)) == 5


def test_qasper_sample_skipping_fills_across_papers():
    # the 6-question paper always overshoots 5; the other two always fill it
    questions = [*qasper_paper("a", 4), *qasper_paper("b", 6), *qasper_paper("c", 1)]
    drawn = draw_qasper_sample(questions, seed=0, per_dataset=5)
    assert sorted(drawn) == ["a-q0", "a-q1", "a-q2", "a-q3", "c-q0"]
    for seed in range(5):
        assert sorted(draw_qasper_sample(questions, seed=seed, per_dataset=5)) == sorted(drawn)


def test_qasper_sample_fails_when_exact_fill_is_impossible():
    questions = qasper_paper("a", 3)
    try:
        draw_qasper_sample(questions, seed=0, per_dataset=2)
    except ValueError as exc:
        assert "cannot fill exactly" in str(exc)
    else:
        raise AssertionError("expected a ValueError")


def test_nq_sample_takes_per_type_pages_in_seeded_order():
    questions = [nq_question(f"p{i}", "precise" if i % 2 else "context") for i in range(20)]
    drawn = draw_nq_sample(questions, seed=0, per_type=4)
    assert len(drawn) == 8
    pages = {qid for qid in drawn}
    assert len(pages) == 8  # one per page
    assert draw_nq_sample(questions, seed=0, per_type=4) == drawn
    try:
        draw_nq_sample(questions[:3], seed=0, per_type=4)
    except ValueError as exc:
        assert "needs 4" in str(exc)
    else:
        raise AssertionError("expected a ValueError")


def test_nq_sample_rejects_two_questions_on_one_page():
    question = Question(question_id="p1", doc_id="p1", split="dev", text="?", annotators=((SPAN,),), query_type="precise")
    same_page = Question(question_id="p1-b", doc_id="p1", split="dev", text="?", annotators=((SPAN,),), query_type="precise")
    try:
        draw_nq_sample([question, same_page], seed=0, per_type=1)
    except ValueError as exc:
        assert "more than one question" in str(exc)
    else:
        raise AssertionError("expected a ValueError")


def test_sample_file_round_trip(tmp_path):
    path = tmp_path / "reader-sample.txt"
    write_sample(path, seed=7, qasper_ids=["b", "a"], nq_ids=["y", "x"])
    seed, ids = read_sample(path)
    assert seed == 7
    assert ids == {"qasper": ("a", "b"), "nq": ("x", "y")}
    assert "# seed=7" in path.read_text(encoding="utf-8")


def test_read_sample_rejects_bad_lines_and_duplicates(tmp_path):
    path = tmp_path / "reader-sample.txt"
    path.write_text("# seed=0\nc4:x\n", encoding="utf-8")
    try:
        read_sample(path)
    except ValueError as exc:
        assert "bad sample line" in str(exc)
    else:
        raise AssertionError("expected a ValueError")
    path.write_text("# seed=0\nnq:a\nnq:a\n", encoding="utf-8")
    try:
        read_sample(path)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("expected a ValueError")
    path.write_text("nq:a\n", encoding="utf-8")  # no seed header
    try:
        read_sample(path)
    except ValueError as exc:
        assert "seed header" in str(exc)
    else:
        raise AssertionError("expected a ValueError")


def test_draw_reader_sample_and_reference_counts():
    qasper_split = SimpleNamespace(
        dataset="qasper",
        questions=[*qasper_paper("a", 2), *qasper_paper("b", 3)],
        evidence_counts={"answer_extractive": 3, "answer_free_form": 1, "answer_yes_no": 2},
    )
    nq_split = SimpleNamespace(
        dataset="nq",
        questions=[
            nq_question("p1", "precise", with_short=True),
            nq_question("p2", "context"),
            nq_question("p4", "context"),
        ],
        evidence_counts={"reference_short_span": 2, "reference_yes_no": 1, "reference_long_answer": 5},
    )
    # a precise yes/no-only question: no short-answer spans
    yes_only = Question(
        question_id="p3", doc_id="p3", split="dev", text="?", annotators=((SPAN,),), query_type="precise"
    )
    nq_split.questions.append(yes_only)
    drawn = draw_reader_sample([qasper_split, nq_split], seed=0, per_dataset=5, per_type=2)
    assert set(drawn) == {"qasper", "nq"}
    assert len(drawn["qasper"]) == 5
    counts = reference_counts([qasper_split, nq_split])
    assert counts["qasper"] == {"extractive": 3, "free_form": 1, "yes_no": 2}
    assert counts["nq"] == {"short_span": 2, "yes_no": 1, "long_answer": 5, "precise_yes_no_only": 1}
