"""`rag run <grid config>`: every chunking at every token budget, in both
views and both search scopes, under every configured retrieval pipeline
(BM25 alone, or the production line and its ablations per embedder).

For each question, chunking, search scope, pipeline and embedder, one
ranked list is retrieved (see rag.pipelines) and packed at every budget
three ways: the production view (top-N cap), the production view's side
table (a smaller cap) and the fair view (no cap). A fixed chunking whose
chunk is bigger than the budget is not scored at that budget. Retrieval
sees only the question text, never its query type.

Per-question results go to runs/<dataset>/<run_name>/ (git-ignored) as
Parquet, one row per pipeline and embedder (`pipeline`, `embedder`):

- questions.parquet: one row per question, with its query type and,
  for Natural Questions, whether it is a precise question with a
  short-answer span;
- results.parquet: one row per question x pipeline x embedder x chunking
  x scope x view x top-N cap x budget, with retrieval recall and
  precision (null when not scored), whether the top-N cap bound, the
  short-answer span recall for NQ precise questions (null elsewhere), the
  share of the chunking's chunks longer than the embedder's input limit
  (null without an embedder) and whether packing used the production
  line's unreranked tail (null for pipelines without the reranker);
- fixed_k.parquet: one row per question x pipeline x embedder x chunking
  x scope x k, with hit@k and recall@k (collection search only).

The result tables R2, R3, R4, R2w, R5 (when there are embedders) and -
for a Natural Questions run - R6 are rendered from those files. `sample`
restricts the run to a seeded sample of documents, written to
runs/<dataset>/<run_name>-sample<N>/ with its tables inside it, so the
committed tables under results/ are never overwritten.
"""

from __future__ import annotations

import json
import random
import time
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .cache import Cache
from .chunking import Chunk, chunk_text, fixed_windows, section_aware, small_to_big_children, verify_tiling
from .config import PRODUCTION_LINE, ChunkingSpec, GridConfig, config_hash
from .documents import Document
from .labels import question_query_type
from .metrics import score_fixed_k, score_question
from .models import EMBEDDERS, RERANKER, Models, ModelSource
from .packing import pack, pack_small_to_big
from .paths import Paths
from .pipelines import Ranking, Retriever
from .qasper import Question
from .query_type import PRECISE, QUERY_TYPES
from .retrieval import BM25Index
from .run import dataset_split_hashes, excluded_counts, gold_token_sets, library_versions, load_datasets
from .tables import write_tables
from .tokens import TokenText

SCHEMA_VERSION = "3"  # 2: short_recall; 3: truncated_share and used_tail

QUESTIONS_SCHEMA = pa.schema(
    [
        ("dataset", pa.string()),
        ("split", pa.string()),
        ("question_id", pa.string()),
        ("doc_id", pa.string()),
        ("query_type", pa.string()),
        ("annotators", pa.int32()),
        ("passages", pa.list_(pa.int32())),
        ("short_answer", pa.bool_()),  # NQ precise questions with a short-answer span
    ]
)

_KEYS = [
    ("dataset", pa.string()),
    ("split", pa.string()),
    ("question_id", pa.string()),
    ("doc_id", pa.string()),
    ("query_type", pa.string()),
    ("pipeline", pa.string()),
    ("embedder", pa.string()),  # null for pipelines without one (BM25)
    ("chunking", pa.string()),
    ("scope", pa.string()),
]

RESULTS_SCHEMA = pa.schema(
    _KEYS
    + [
        ("view", pa.string()),
        ("top_n", pa.int32()),  # null in the fair view
        ("budget", pa.int32()),
        ("scored", pa.bool_()),
        ("recall", pa.float64()),
        ("precision", pa.float64()),
        ("retrieved_tokens", pa.int32()),
        ("gold_tokens", pa.int32()),
        ("n_chunks", pa.int32()),
        ("kept_annotator", pa.int32()),
        ("cap_bound", pa.bool_()),  # null in the fair view
        ("short_recall", pa.float64()),  # NQ short-answer span recall, null elsewhere
        ("truncated_share", pa.float64()),  # null without an embedder
        ("used_tail", pa.bool_()),  # null without the reranker, or when not scored
    ]
)

FIXED_K_SCHEMA = pa.schema(
    _KEYS
    + [
        ("k", pa.int32()),
        ("hit", pa.bool_()),
        ("recall", pa.float64()),
        ("relevant_units", pa.int32()),
    ]
)


@dataclass
class _Columns:
    schema: pa.Schema
    data: dict[str, list] = field(default_factory=dict)

    def add(self, **row) -> None:
        for name in self.schema.names:
            self.data.setdefault(name, []).append(row.get(name))

    def write(self, path: Path) -> None:
        columns = {name: self.data.get(name, []) for name in self.schema.names}
        table = pa.Table.from_pydict(columns, schema=self.schema)
        table = table.replace_schema_metadata({"rag.schema_version": SCHEMA_VERSION})
        pq.write_table(table, path)


@dataclass
class _Chunking:
    """One chunking over the collection: its indexed units (children for
    small-to-big), its parents (small-to-big only), and its BM25 index."""

    spec: ChunkingSpec
    units_by_doc: dict[str, list[Chunk]]
    parents_by_doc: dict[str, list[Chunk]]
    parents: dict[tuple[str, int], Chunk]
    index: BM25Index

    def packer(self, ranked: Sequence[Chunk], budget: int, top_n: int | None) -> list[Chunk]:
        if self.spec.method == "small_to_big":
            return pack_small_to_big(ranked, self.parents, budget, top_n)
        return pack(ranked, budget, top_n)

    def returned_units(self, ranked: Sequence[Chunk]) -> list[Chunk]:
        """Retrieved units in rank order, without a budget: small-to-big
        returns the distinct parents of its matched children."""
        if self.spec.method != "small_to_big":
            return list(ranked)
        seen: set[tuple[str, int]] = set()
        units: list[Chunk] = []
        for child in ranked:
            key = (child.doc_id, child.parent_index)
            if key not in seen:
                seen.add(key)
                units.append(self.parents[key])
        return units

    def doc_units(self, doc_id: str) -> list[Chunk]:
        """All returnable units of one document (parents for small-to-big)."""
        by_doc = self.parents_by_doc if self.spec.method == "small_to_big" else self.units_by_doc
        return by_doc.get(doc_id, [])


def _chunk_document(spec: ChunkingSpec, doc: Document, tokens: TokenText) -> tuple[list[Chunk], list[Chunk]]:
    """(indexed units, parents); parents are empty except for small-to-big."""
    if spec.method == "fixed":
        return fixed_windows(doc, tokens, spec.chunk_tokens), []
    sections = section_aware(doc, tokens, spec.max_tokens)
    if spec.method == "section_aware":
        return sections, []
    return small_to_big_children(doc, tokens, sections, spec.child_tokens), sections


def _build_chunking(
    spec: ChunkingSpec, documents: dict[str, Document], tokenized: dict[str, TokenText], lance_dir: Path
) -> tuple[_Chunking, int]:
    units_by_doc: dict[str, list[Chunk]] = {}
    parents_by_doc: dict[str, list[Chunk]] = {}
    texts: dict[str, str] = {}
    shared_characters = 0
    for doc_id in sorted(documents):
        doc, tokens = documents[doc_id], tokenized[doc_id]
        units, doc_parents = _chunk_document(spec, doc, tokens)
        shared_characters += verify_tiling(doc, tokens, units)
        if doc_parents:
            verify_tiling(doc, tokens, doc_parents)
            parents_by_doc[doc_id] = doc_parents
        units_by_doc[doc_id] = units
        for unit in units:
            texts[f"{doc_id}:{unit.index}"] = chunk_text(doc, unit)
    index = BM25Index(lance_dir, table=spec.name)
    index.build([u for doc_id in sorted(units_by_doc) for u in units_by_doc[doc_id]], texts)
    parents = {(p.doc_id, p.index): p for doc_parents in parents_by_doc.values() for p in doc_parents}
    chunking = _Chunking(
        spec=spec, units_by_doc=units_by_doc, parents_by_doc=parents_by_doc, parents=parents, index=index
    )
    return chunking, shared_characters


def _views(cfg: GridConfig) -> list[tuple[str, int | None]]:
    return [("production", cfg.top_n), ("production", cfg.side_top_n), ("fair", None)]


def _score_question(
    cfg: GridConfig,
    question: Question,
    dataset: str,
    qtype: str,
    gold: list[tuple[int, ...]],
    short_gold: list[tuple[int, ...]],
    chunkings: list[_Chunking],
    retriever: Retriever,
    results: _Columns,
    fixed_k: _Columns,
) -> None:
    keys = {
        "dataset": dataset,
        "split": question.split,
        "question_id": question.question_id,
        "doc_id": question.doc_id,
        "query_type": qtype,
    }
    rankings = retriever.rank(question, [(c.spec.name, c.index) for c in chunkings], cfg.scopes)
    for chunking in chunkings:
        for scope in cfg.scopes:
            for ranking in rankings[(chunking.spec.name, scope)]:
                truncated = retriever.truncated.get((chunking.spec.name, ranking.embedder or ""))
                cell = {
                    **keys,
                    "pipeline": ranking.pipeline,
                    "embedder": ranking.embedder,
                    "chunking": chunking.spec.name,
                    "scope": scope,
                    "truncated_share": truncated,
                }
                _score_ranking(cfg, question, gold, short_gold, chunking, scope, ranking, cell, results, fixed_k)


def _score_ranking(
    cfg: GridConfig,
    question: Question,
    gold: list[tuple[int, ...]],
    short_gold: list[tuple[int, ...]],
    chunking: _Chunking,
    scope: str,
    ranking: Ranking,
    cell: dict,
    results: _Columns,
    fixed_k: _Columns,
) -> None:
    """Score one ranked list at every budget and view. For the production
    line, packing used the unreranked tail exactly when packing the whole
    list returns more chunks than packing its reranked head alone (packing
    is greedy in rank order, so both agree up to the end of the head)."""
    nominal = chunking.spec.fixed_size
    ranked = ranking.ranked
    head = None if ranking.reranked is None else ranked[: ranking.reranked]
    if scope == "collection":
        for s in score_fixed_k(
            gold,
            chunking.returned_units(ranked),
            chunking.doc_units(question.doc_id),
            question.doc_id,
            cfg.fixed_k,
        ):
            fixed_k.add(**cell, k=s.k, hit=s.hit, recall=s.recall, relevant_units=s.relevant_units)
    for budget in cfg.budgets:
        if nominal is not None and nominal > budget:
            for view, top_n in _views(cfg):
                results.add(**cell, view=view, top_n=top_n, budget=budget, scored=False)
            continue
        fair = chunking.packer(ranked, budget, None)
        for view, top_n in _views(cfg):
            packed = fair if top_n is None else chunking.packer(ranked, budget, top_n)
            used_tail = None if head is None else len(packed) > len(chunking.packer(head, budget, top_n))
            score = score_question(gold, packed, question.doc_id)
            short_recall = score_question(short_gold, packed, question.doc_id).recall if short_gold else None
            results.add(
                **cell,
                view=view,
                top_n=top_n,
                budget=budget,
                scored=True,
                recall=score.recall,
                precision=score.precision,
                short_recall=short_recall,
                retrieved_tokens=score.retrieved_tokens,
                gold_tokens=score.gold_tokens,
                n_chunks=len(packed),
                kept_annotator=score.annotator,
                cap_bound=None if top_n is None else len(fair) > len(packed),
                used_tail=used_tail,
            )


@dataclass(frozen=True)
class GridOutcome:
    config: GridConfig
    config_hash: str
    n_questions: int
    query_types: dict[str, int]
    run_dir: Path
    tables: tuple[Path, ...]


def sample_papers(splits: list, n: int, seed: int) -> list:
    """Keep a seeded random sample of `n` documents (all of them when
    fewer), with their questions and exclusions."""
    if n <= 0:
        raise ValueError(f"sample must be positive, got {n}")
    doc_ids = sorted(doc.doc_id for split in splits for doc in split.documents)
    kept = set(random.Random(seed).sample(doc_ids, min(n, len(doc_ids))))
    return [
        replace(
            split,
            documents=tuple(d for d in split.documents if d.doc_id in kept),
            questions=tuple(q for q in split.questions if q.doc_id in kept),
            excluded=tuple(e for e in split.excluded if e.doc_id in kept),
        )
        for split in splits
    ]


def _model_manifest(cfg: GridConfig) -> dict:
    embedders = {
        name: {
            "model_id": EMBEDDERS[name].model_id,
            "revision": EMBEDDERS[name].revision,
            "max_input_tokens": EMBEDDERS[name].max_tokens,
            "document_prefix": EMBEDDERS[name].document_prefix,
            "query_prefix": EMBEDDERS[name].query_prefix,
        }
        for name in cfg.embedders
    }
    out: dict = {"embedders": embedders}
    if PRODUCTION_LINE in cfg.pipelines:
        out["reranker"] = {"model_id": RERANKER.model_id, "revision": RERANKER.revision}
    return out


def _model_versions() -> dict[str, str]:
    import sentence_transformers
    import torch
    import transformers

    return {
        "sentence-transformers": sentence_transformers.__version__,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
    }


def run_grid(
    cfg: GridConfig,
    paths: Paths,
    encoding=None,
    sample: int | None = None,
    models: ModelSource | None = None,
) -> GridOutcome:
    started = time.monotonic()
    cfg_hash = config_hash(cfg)
    splits, documents, spans_verified = load_datasets(paths, cfg.sources)
    run_name = cfg.run_name
    if sample is not None:
        splits = sample_papers(splits, sample, cfg.seed)
        documents = {doc.doc_id: doc for split in splits for doc in split.documents}
        run_name = f"{cfg.run_name}-sample{sample}"
    tokenized = {doc_id: TokenText(documents[doc_id].text, encoding) for doc_id in sorted(documents)}

    run_dir = paths.run_dir(run_name, cfg.dataset)
    results_dir = paths.results if sample is None else run_dir / "results"
    run_dir.mkdir(parents=True, exist_ok=True)
    cache = Cache(paths.cache / "rag-cache.sqlite")
    retriever = Retriever(
        cfg, documents, models if models is not None else Models(paths.data), cache, run_dir / "lance"
    )
    all_questions = [(split.dataset, question) for split in splits for question in split.questions]
    retriever.embed_questions([question for _, question in all_questions])
    chunkings: list[_Chunking] = []
    chunk_counts: dict[str, int] = {}
    shared_characters: dict[str, int] = {}
    for spec in cfg.chunkings:
        chunking, shared = _build_chunking(spec, documents, tokenized, run_dir / "lance")
        retriever.index_chunking(spec.name, [u for doc_id in sorted(documents) for u in chunking.units_by_doc[doc_id]])
        chunkings.append(chunking)
        chunk_counts[spec.name] = sum(len(units) for units in chunking.units_by_doc.values())
        shared_characters[spec.name] = shared
    indexed = time.monotonic()

    questions = _Columns(QUESTIONS_SCHEMA)
    results = _Columns(RESULTS_SCHEMA)
    fixed_k = _Columns(FIXED_K_SCHEMA)
    query_types = {t: 0 for t in QUERY_TYPES}
    query_types_by_dataset: dict[str, dict[str, int]] = {}
    for done, (dataset, question) in enumerate(all_questions, start=1):
        passages = [len(annotator) for annotator in question.annotators]
        qtype = question_query_type(question)
        query_types[qtype] += 1
        per_dataset = query_types_by_dataset.setdefault(dataset, {t: 0 for t in QUERY_TYPES})
        per_dataset[qtype] += 1
        short_scored = qtype == PRECISE and bool(question.short_annotators)
        questions.add(
            dataset=dataset,
            split=question.split,
            question_id=question.question_id,
            doc_id=question.doc_id,
            query_type=qtype,
            annotators=len(passages),
            passages=passages,
            short_answer=short_scored or None,
        )
        gold = gold_token_sets(question, tokenized)
        short_gold = (
            [
                tuple(
                    sorted(
                        frozenset().union(
                            *(tokenized[question.doc_id].token_indices_overlapping(s.start, s.end) for s in annotator)
                        )
                    )
                )
                for annotator in question.short_annotators
            ]
            if short_scored
            else []
        )
        _score_question(cfg, question, dataset, qtype, gold, short_gold, chunkings, retriever, results, fixed_k)
        if not cfg.bm25_only and (done % 50 == 0 or done == len(all_questions)):
            elapsed = time.monotonic() - indexed
            print(
                f"  questions {done}/{len(all_questions)}, {elapsed / 60:.1f} min, "
                f"~{elapsed / done * (len(all_questions) - done) / 60:.0f} min left, "
                f"reranker pairs scored {retriever.stats.pairs_scored}",
                flush=True,
            )
    cache.close()
    retrieved = time.monotonic()

    questions.write(run_dir / "questions.parquet")
    results.write(run_dir / "results.parquet")
    fixed_k.write(run_dir / "fixed_k.parquet")

    dataset_hashes = dataset_split_hashes(splits)
    tables = write_tables(cfg, cfg_hash, dataset_hashes, run_dir, results_dir, sample=sample)
    n_questions = sum(query_types.values())
    nq_split = next((split for split in splits if split.dataset == "nq"), None)
    manifest = {
        "config": cfg.as_dict(),
        "config_hash": cfg_hash,
        "schema_version": SCHEMA_VERSION,
        "sample": None if sample is None else {"documents": len(documents), "requested": sample, "seed": cfg.seed},
        "datasets": dataset_hashes,
        "versions": library_versions() | ({} if cfg.bm25_only else _model_versions()),
        "counts": {
            "documents": len(documents),
            "chunks": chunk_counts,
            "questions": n_questions,
            "query_types": query_types,
            "query_types_by_dataset": query_types_by_dataset,
            "excluded_by_reason": excluded_counts(splits),
            "labelled_spans_verified": spans_verified,
            "documents_tiled_per_chunking": len(documents),
            "multibyte_characters_shared_at_chunk_boundaries": shared_characters,
            "evidence_anchoring": {
                key: split.evidence_counts for key, split in zip(dataset_hashes, splits, strict=True)
            },
            "nq_subset": {
                "file": "configs/nq-subset.txt",
                "ids": nq_split.subset_size,
                "sha256": nq_split.subset_hash,
            }
            if nq_split is not None
            else None,
        },
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    if not cfg.bm25_only:
        manifest["models"] = _model_manifest(cfg)
        manifest["truncated_share"] = {
            spec.name: {e: retriever.truncated[(spec.name, e)] for e in cfg.embedders} for spec in cfg.chunkings
        }
        manifest["reranker"] = retriever.stats.as_dict()
        manifest["phase_seconds"] = {
            "load_embed_and_index": round(indexed - started, 3),
            "retrieve_rerank_and_score": round(retrieved - indexed, 3),
            "write": round(time.monotonic() - retrieved, 3),
        }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"run {run_name}: {n_questions} questions x {len(chunkings)} chunkings x {len(cfg.budgets)} budgets")
    print(f"  labelled spans verified: {spans_verified}")
    print("  query types: " + ", ".join(f"{t} {n}" for t, n in query_types.items()))
    for name, n in chunk_counts.items():
        print(f"  chunks indexed, {name}: {n} over {len(documents)} documents (tiling verified)")
    if not cfg.bm25_only:
        print(f"  reranker: {retriever.stats.as_dict()}")
        print(f"  wall time: {manifest['duration_seconds'] / 60:.1f} min")
    print(f"  per-question results: {run_dir}")
    for path in tables:
        print(f"  result table: {path}")
    return GridOutcome(
        config=cfg,
        config_hash=cfg_hash,
        n_questions=n_questions,
        query_types=query_types,
        run_dir=run_dir,
        tables=tables,
    )
