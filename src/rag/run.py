"""`rag run`: one end-to-end retrieval eval from a config file.

Loads the configured dataset splits, builds the document store, chunks
every document with the configured chunking, indexes the whole
collection for BM25, retrieves per question, packs whole chunks into the
budget (production view), scores retrieval recall and precision against
the labelled spans, writes per-question results and a run manifest under
runs/ (git-ignored) and the committed markdown result table R1 under
results/.
"""

from __future__ import annotations

import json
import platform
import time
from dataclasses import dataclass
from pathlib import Path

from . import __version__
from .chunking import Chunk, chunk_text, fixed_windows
from .config import RunConfig, config_hash, config_yaml, load_config
from .documents import Document
from .metrics import QuestionScore, mean, score_question
from .packing import pack
from .paths import Paths
from .qasper import (
    EVIDENCE_UNANCHORED,
    FIGURE_OR_TABLE_ONLY,
    UNANSWERABLE,
    QasperSplit,
    load_split,
    verify_spans,
)
from .retrieval import BM25Index
from .setup_cmd import ensure_split_files
from .tokens import TokenText

EXCLUSION_ORDER = (UNANSWERABLE, FIGURE_OR_TABLE_ONLY, EVIDENCE_UNANCHORED)


@dataclass(frozen=True)
class RunOutcome:
    config: RunConfig
    config_hash: str
    n_questions: int
    excluded_by_reason: dict[str, int]
    mean_recall: float
    mean_precision: float
    result_table: Path


def _library_versions() -> dict[str, str]:
    import lancedb
    import tiktoken
    import yaml

    try:
        import pyarrow

        pyarrow_version = pyarrow.__version__
    except ImportError:  # pragma: no cover - pyarrow is a lancedb dependency
        pyarrow_version = "unknown"
    return {
        "python": platform.python_version(),
        "rag-findings": __version__,
        "lancedb": lancedb.__version__,
        "tiktoken": tiktoken.__version__,
        "pyarrow": pyarrow_version,
        "pyyaml": yaml.__version__,
    }


def _all_documents(splits: list[QasperSplit]) -> dict[str, Document]:
    documents: dict[str, Document] = {}
    for split in splits:
        for doc in split.documents:
            if doc.doc_id in documents:
                raise ValueError(f"duplicate document id across splits: {doc.doc_id}")
            documents[doc.doc_id] = doc
    return documents


def _build_chunks(
    documents: dict[str, Document], chunk_tokens: int, encoding=None
) -> tuple[list[Chunk], dict[str, TokenText], dict[str, str]]:
    chunks: list[Chunk] = []
    tokenized: dict[str, TokenText] = {}
    texts: dict[str, str] = {}
    for doc_id in sorted(documents):
        doc = documents[doc_id]
        tokens = TokenText(doc.text, encoding)
        tokenized[doc_id] = tokens
        for chunk in fixed_windows(doc, tokens, chunk_tokens):
            chunks.append(chunk)
            texts[f"{chunk.doc_id}:{chunk.index}"] = chunk_text(doc, chunk)
    return chunks, tokenized, texts


def _gold_sets(question, tokenized: dict[str, TokenText]) -> list[frozenset[int]]:
    tokens = tokenized[question.doc_id]
    return [
        frozenset().union(*(tokens.token_indices_overlapping(span.start, span.end) for span in annotator))
        for annotator in question.annotators
    ]


def write_result_table(
    path: Path, cfg: RunConfig, cfg_hash: str, splits: list[QasperSplit], outcome: RunOutcome
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    title = (
        f"# R1 - {cfg.dataset} {cfg.run_name}: "
        f"{cfg.chunking_method}-{cfg.chunk_tokens}, {cfg.pipeline}, "
        f"budget {cfg.budget}, {cfg.view} view"
    )
    lines.append(title)
    lines.append("")
    lines.append(f"Config hash: `{cfg_hash}`")
    lines.append("")
    lines.append("## Config")
    lines.append("")
    lines.append("```yaml")
    lines.append(config_yaml(cfg))
    lines.append("```")
    lines.append("")
    lines.append("## Dataset")
    lines.append("")
    lines.append("| split | sha256 |")
    lines.append("|---|---|")
    for split in splits:
        lines.append(f"| {split.split} | `{split.dataset_hash}` |")
    lines.append("")
    lines.append("## Questions")
    lines.append("")
    total = outcome.n_questions + sum(outcome.excluded_by_reason.values())
    lines.append("| | n |")
    lines.append("|---|---|")
    lines.append(f"| included | {outcome.n_questions} |")
    for reason in EXCLUSION_ORDER:
        lines.append(f"| excluded: {reason} | {outcome.excluded_by_reason.get(reason, 0)} |")
    lines.append(f"| total | {total} |")
    lines.append("")
    lines.append("## Retrieval")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    lines.append(f"| mean retrieval recall | {outcome.mean_recall:.4f} |")
    lines.append(f"| mean retrieval precision | {outcome.mean_precision:.4f} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run(config_path: Path, paths: Paths, encoding=None) -> RunOutcome:
    started = time.monotonic()
    cfg = load_config(config_path)
    cfg_hash = config_hash(cfg)

    split_paths = ensure_split_files(paths.data, cfg.splits)
    splits = [load_split(name, split_paths[name]) for name in sorted(split_paths)]
    documents = _all_documents(splits)

    seen_ids: set[str] = set()
    for split in splits:
        for question in split.questions:
            if question.question_id in seen_ids:
                raise ValueError(f"duplicate question id: {question.question_id}")
            seen_ids.add(question.question_id)

    # every labelled span round-trips: offsets slice back to the quote and
    # the source hash matches the document's
    spans_verified = sum(verify_spans(split, documents_by_id=documents) for split in splits)

    chunks, tokenized, texts = _build_chunks(documents, cfg.chunk_tokens, encoding)

    run_dir = paths.run_dir(cfg.run_name)
    run_dir.mkdir(parents=True, exist_ok=True)
    index = BM25Index(run_dir / "lance")
    index.build(chunks, texts)

    records: list[dict] = []
    recalls: list[float] = []
    precisions: list[float] = []
    for split in splits:
        for question in split.questions:
            ranked = index.search(question.text, cfg.search_depth)
            top_n = cfg.top_n if cfg.view == "production" else max(len(ranked), 1)
            packed = pack([item.chunk for item in ranked], cfg.budget, top_n)
            score: QuestionScore = score_question(_gold_sets(question, tokenized), packed, question.doc_id)
            recalls.append(score.recall)
            precisions.append(score.precision)
            records.append(
                {
                    "question_id": question.question_id,
                    "doc_id": question.doc_id,
                    "split": question.split,
                    "question": question.text,
                    "annotators": len(question.annotators),
                    "kept_annotator": score.annotator,
                    "recall": score.recall,
                    "precision": score.precision,
                    "gold_tokens": score.gold_tokens,
                    "retrieved_tokens": score.retrieved_tokens,
                    "n_chunks_packed": len(packed),
                    "packed": [
                        {
                            "doc_id": c.doc_id,
                            "chunk_index": c.index,
                            "n_tokens": c.n_tokens,
                        }
                        for c in packed
                    ],
                }
            )

    questions_path = run_dir / "questions.jsonl"
    with questions_path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")

    excluded_by_reason = {reason: 0 for reason in EXCLUSION_ORDER}
    for split in splits:
        for item in split.excluded:
            excluded_by_reason[item.reason] = excluded_by_reason.get(item.reason, 0) + 1

    outcome = RunOutcome(
        config=cfg,
        config_hash=cfg_hash,
        n_questions=len(records),
        excluded_by_reason=excluded_by_reason,
        mean_recall=mean(recalls),
        mean_precision=mean(precisions),
        result_table=paths.results / cfg.dataset / f"r1-{cfg.run_name}.md",
    )

    manifest = {
        "config": cfg.as_dict(),
        "config_hash": cfg_hash,
        "datasets": {split.split: split.dataset_hash for split in splits},
        "versions": _library_versions(),
        "counts": {
            "documents": len(documents),
            "chunks": len(chunks),
            "questions": outcome.n_questions,
            "excluded_by_reason": excluded_by_reason,
            "labelled_spans_verified": spans_verified,
            "evidence_anchoring": {split.split: split.evidence_counts for split in splits},
        },
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    write_result_table(outcome.result_table, cfg, cfg_hash, splits, outcome)

    print(f"run {cfg.run_name}: {outcome.n_questions} questions scored")
    print(f"  labelled spans verified: {spans_verified}")
    for reason in EXCLUSION_ORDER:
        print(f"  excluded {reason}: {excluded_by_reason.get(reason, 0)}")
    print(f"  chunks indexed: {len(chunks)} over {len(documents)} documents")
    print(f"  mean retrieval recall:    {outcome.mean_recall:.4f}")
    print(f"  mean retrieval precision: {outcome.mean_precision:.4f}")
    print(f"  per-question results: {questions_path}")
    print(f"  result table: {outcome.result_table}")
    return outcome
