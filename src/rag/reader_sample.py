"""The reader sample: 1,000 questions, 500 per dataset, drawn by document
with a fixed seed and committed as ids only (configs/v2/reader-sample.txt).

- QASPER: papers in seeded order with all their questions. A paper that
  would overshoot the per-dataset count is skipped, and filling
  continues with the next paper, so the sample holds whole papers and
  exactly 500 questions.
- Natural Questions: 250 precise and 250 context questions, one per
  page (each subset question is its own page), in seeded order.

The seeded order ranks document ids by sha256(f"{seed}:{id}") - the same
convention as the Natural Questions subset sampler - so the sample is a
pure function of the data and the seed, reproducible on any machine.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from .labels import Question
from .nq import selection_key
from .query_type import CONTEXT, PRECISE

READER_SAMPLE_RELATIVE_PATH = ("configs", "v2", "reader-sample.txt")
QASPER_PER_DATASET = 500
NQ_PER_TYPE = 250
READER_SAMPLE_SEED = 0


def sample_path(root: Path) -> Path:
    return root.joinpath(*READER_SAMPLE_RELATIVE_PATH)


def draw_qasper_sample(
    questions: Sequence[Question], seed: int, per_dataset: int = QASPER_PER_DATASET
) -> tuple[str, ...]:
    """Whole papers in seeded order until exactly `per_dataset` questions;
    a paper that would overshoot is skipped and filling continues."""
    by_paper: dict[str, list[str]] = {}
    for question in questions:
        by_paper.setdefault(question.doc_id, []).append(question.question_id)
    order = sorted(by_paper, key=lambda doc_id: (selection_key(seed, doc_id), doc_id))
    drawn: list[str] = []
    for doc_id in order:
        ids = by_paper[doc_id]
        if len(drawn) + len(ids) > per_dataset:
            continue
        drawn.extend(ids)
        if len(drawn) == per_dataset:
            return tuple(drawn)
    raise ValueError(f"the papers cannot fill exactly {per_dataset} questions: reached {len(drawn)}")


def draw_nq_sample(questions: Sequence[Question], seed: int, per_type: int = NQ_PER_TYPE) -> tuple[str, ...]:
    """`per_type` precise and `per_type` context questions, one per page,
    in seeded order."""
    by_type: dict[str, list[str]] = {PRECISE: [], CONTEXT: []}
    for question in questions:
        if question.doc_id != question.question_id:
            raise ValueError(f"a Natural Questions page holds more than one question: {question.question_id}")
        by_type[question.query_type].append(question.question_id)
    drawn: list[str] = []
    for query_type in (PRECISE, CONTEXT):
        ranked = sorted(by_type[query_type], key=lambda qid: (selection_key(seed, qid), qid))
        if len(ranked) < per_type:
            raise ValueError(f"only {len(ranked)} {query_type} questions; the sample needs {per_type}")
        drawn.extend(ranked[:per_type])
    return tuple(drawn)


def write_sample(path: Path, seed: int, qasper_ids: Sequence[str], nq_ids: Sequence[str]) -> None:
    """Write the sample id list: a header recording the seed and counts,
    then one `dataset:id` line per question, sorted within each dataset."""
    lines = [f"# seed={seed}", f"# qasper={len(qasper_ids)} nq={len(nq_ids)}"]
    lines += [f"qasper:{qid}" for qid in sorted(qasper_ids)]
    lines += [f"nq:{qid}" for qid in sorted(nq_ids)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_sample(path: Path) -> tuple[int, dict[str, tuple[str, ...]]]:
    """Read the committed sample: (seed, ids per dataset)."""
    seed: int | None = None
    ids: dict[str, list[str]] = {"qasper": [], "nq": []}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            if line.startswith("# seed="):
                seed = int(line[len("# seed=") :])
            continue
        dataset, _, question_id = line.partition(":")
        if dataset not in ids or not question_id:
            raise ValueError(f"bad sample line: {line}")
        ids[dataset].append(question_id)
    if seed is None:
        raise ValueError(f"sample file lacks a seed header: {path}")
    for dataset, dataset_ids in ids.items():
        if len(set(dataset_ids)) != len(dataset_ids):
            raise ValueError(f"duplicate question id in the {dataset} sample")
    return seed, {dataset: tuple(sorted(dataset_ids)) for dataset, dataset_ids in ids.items()}


# --- drawing over loaded splits ---------------------------------------------


def draw_reader_sample(
    splits: Sequence, seed: int, per_dataset: int = QASPER_PER_DATASET, per_type: int = NQ_PER_TYPE
) -> dict[str, tuple[str, ...]]:
    """Draw the reader sample from loaded splits: whole QASPER papers in
    seeded order, and per-type Natural Questions pages in seeded order."""
    questions = {"qasper": [], "nq": []}
    for split in splits:
        questions.setdefault(split.dataset, []).extend(split.questions)
    return {
        "qasper": draw_qasper_sample(questions["qasper"], seed, per_dataset),
        "nq": draw_nq_sample(questions["nq"], seed, per_type),
    }


def reference_counts(splits: Sequence) -> dict[str, dict[str, int]]:
    """Reference-answer counts per dataset, for the sample command's report
    and the manifests: QASPER by answer type, Natural Questions by reference
    kind plus the precise questions that are yes/no only."""
    qasper = {"extractive": 0, "free_form": 0, "yes_no": 0}
    nq = {"short_span": 0, "yes_no": 0, "long_answer": 0, "precise_yes_no_only": 0}
    for split in splits:
        if split.dataset == "qasper":
            qasper["extractive"] += split.evidence_counts.get("answer_extractive", 0)
            qasper["free_form"] += split.evidence_counts.get("answer_free_form", 0)
            qasper["yes_no"] += split.evidence_counts.get("answer_yes_no", 0)
        elif split.dataset == "nq":
            nq["short_span"] += split.evidence_counts.get("reference_short_span", 0)
            nq["yes_no"] += split.evidence_counts.get("reference_yes_no", 0)
            nq["long_answer"] += split.evidence_counts.get("reference_long_answer", 0)
            nq["precise_yes_no_only"] += sum(
                1 for q in split.questions if q.query_type == PRECISE and not q.short_annotators
            )
    return {"qasper": qasper, "nq": nq}
