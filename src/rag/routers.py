"""The v2 label-free routers (ADR 0005): search-all routing and confidence
routing, each computed per question from the chunkings' rankings and
needing no labels.

`rag run <routers config>` (kind: routers) runs both routers on one
dataset: it builds the run's chunkings, searches every chunking's index
(the production line with its configured embedders), and writes
runs/<dataset>/<run_name>/ (git-ignored):

- routed.parquet: one row per question x router x embedder x scope x view
  (budget and production) x budget - the per-question results' columns
  plus `picked_chunking` (the confidence router's pick; null for
  search-all), so the oracle analysis over the baseline runs'
  results.parquet still sees only the seven chunkings;
- packed.parquet (only for cells under `export_packed`): the packed spans
  of the exported cells under pipelines `search-all` and `confidence`;
  for search-all the reader text is these spans merged per document, in
  order of first appearance, so no text is repeated.

Search-all routing fuses the chunkings' hybrid lists (BM25 and vector
search fused, before the reranker) by reciprocal rank fusion keyed by
document and character span - identical text from two chunkings is one
item, represented by the chunk that first contributed it, which carries
its chunking's packing rule - reranks the fused top `fused_rerank_depth`
(50) and packs by budget counting overlapping text once
(rag.packing.pack_union); small-to-big children return their parents
under v1's rule.

Confidence routing uses the chunking whose reranked top result scores
highest: the top-1 reranker score of each chunking's reranked top
`rerank_depth` (30), ties going to the smaller chunk in the size order.
Its result is that chunking's own budget-view (and production-view)
packing.

Reranker scores come through the existing cache, keyed by question and
character span, so a pair two chunkings share is scored once.

`rag routers <table config>` (kind: routers-table) reads the router runs
next to the v2 baseline grid runs and renders R11
(results/{dataset}/r11-<run_name>.md per dataset, plus results/pooled/
when several datasets are present): recall and precision of both routers
at every budget in both views, next to the baseline chunking and the
oracle router, and the confidence router's pick per chunking. No
retrieval runs there, and the tables are byte-identical for the same
runs.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

from .cache import Cache
from .chunking import Chunk
from .config import (
    PRODUCTION_LINE,
    ChunkingSpec,
    DatasetRef,
    GridConfig,
    PackedExport,
    _parse_chunking,
    _parse_dataset,
    _validate_pipelines,
)
from .grid import (
    PACKED_SCHEMA,
    RESULTS_SCHEMA,
    _build_chunking,
    _Chunking,
    _Columns,
    _model_manifest,
    _model_versions,
    sample_papers,
)
from .labels import question_query_type
from .metrics import score_question, union_token_count
from .models import EMBEDDERS, Models, ModelSource
from .packing import pack_union
from .paths import Paths
from .pipelines import Ranking, Retriever
from .qasper import Question
from .query_type import PRECISE, QUERY_TYPES
from .retrieval import reciprocal_rank_fusion, rerank_head
from .run import dataset_split_hashes, excluded_counts, gold_token_sets, library_versions, load_datasets
from .tokens import TokenText

SEARCH_ALL = "search-all"
CONFIDENCE = "confidence"
ROUTED_SCHEMA_VERSION = "1"  # routed.parquet: the results' columns plus picked_chunking
ROUTED_SCHEMA = pa.schema(list(RESULTS_SCHEMA) + [("picked_chunking", pa.string())])
ROUTER_VIEWS = ("budget", "production")  # the views the routers are scored in
NA = "n/a"


# --- the routers run config ------------------------------------------------


@dataclass(frozen=True)
class RoutersConfig:
    """One routers run: both label-free routers over the run's chunkings."""

    dataset: str
    sources: tuple[DatasetRef, ...]
    chunkings: tuple[ChunkingSpec, ...]
    budgets: tuple[int, ...]
    top_n: int  # production view cap
    budget_top_n: int  # budget view cap
    scopes: tuple[str, ...]
    size_order: tuple[str, ...]  # smallest chunk first: the confidence tie-break order
    search_depth: int
    seed: int
    run_name: str
    embedders: tuple[str, ...] = ()
    rrf_k: int = 60
    rerank_depth: int = 30  # per chunking (the confidence router's statistic)
    fused_rerank_depth: int = 50  # search-all reranks the fused top this many
    export_packed: tuple[PackedExport, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        from .config import _dataset_dict

        out: dict[str, Any] = {
            "kind": "routers",
            "dataset": _dataset_dict(self.dataset, self.sources),
            "embedders": list(self.embedders),
            "rrf_k": self.rrf_k,
            "rerank_depth": self.rerank_depth,
            "fused_rerank_depth": self.fused_rerank_depth,
            "chunkings": [c.as_dict() for c in self.chunkings],
            "budgets": list(self.budgets),
            "top_n": self.top_n,
            "budget_top_n": self.budget_top_n,
            "scopes": list(self.scopes),
            "search_depth": self.search_depth,
            "seed": self.seed,
            "run_name": self.run_name,
            "size_order": list(self.size_order),
        }
        if self.export_packed:
            out["export_packed"] = [cell.as_dict() for cell in self.export_packed]
        return out

    @property
    def views(self) -> tuple[tuple[str, int], ...]:
        """The scored (view, cap) cells: the budget view and the production view."""
        return (("budget", self.budget_top_n), ("production", self.top_n))

    def export_cells(self) -> set[tuple[str, int, int, str]]:
        """The exported (view, top_n, budget, scope) cells of the run."""
        caps = dict(self.views)
        return {(cell.view, caps[cell.view], cell.budget, cell.scope) for cell in self.export_packed}


def parse_routers_config(raw: dict[str, Any]) -> RoutersConfig:
    try:
        if raw.get("kind") != "routers":
            raise ValueError("a routers config needs `kind: routers`")
        label, sources = _parse_dataset(raw["dataset"])
        cfg = RoutersConfig(
            dataset=label,
            sources=sources,
            chunkings=tuple(_parse_chunking(c) for c in raw["chunkings"]),
            budgets=tuple(int(b) for b in raw["budgets"]),
            top_n=int(raw["top_n"]),
            budget_top_n=int(raw["budget_top_n"]),
            scopes=tuple(raw["scopes"]),
            size_order=tuple(str(c) for c in raw["size_order"]),
            search_depth=int(raw.get("search_depth", 1000)),
            seed=int(raw["seed"]),
            run_name=str(raw.get("run_name", "routers")),
            embedders=tuple(raw.get("embedders", ())),
            rrf_k=int(raw.get("rrf_k", 60)),
            rerank_depth=int(raw.get("rerank_depth", 30)),
            fused_rerank_depth=int(raw.get("fused_rerank_depth", 50)),
            export_packed=tuple(
                PackedExport(view=str(cell["view"]), budget=int(cell["budget"]), scope=str(cell["scope"]))
                for cell in raw.get("export_packed", ())
            ),
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"invalid routers config: {exc}") from exc
    _validate_routers(cfg)
    return cfg


def _validate_routers(cfg: RoutersConfig) -> None:
    from .config import SCOPES

    _validate_pipelines(_as_grid(cfg))
    names = [c.name for c in cfg.chunkings]
    if not names or len(set(names)) != len(names):
        raise ValueError("chunkings must be a non-empty list with unique names")
    if len([c for c in cfg.chunkings if c.method == "small_to_big"]) > 1:
        raise ValueError("search-all's parent rule takes parents of one small-to-big chunking")
    if sorted(cfg.size_order) != sorted(names):
        raise ValueError("size_order must list every chunking exactly once, smallest chunk first")
    if not cfg.budgets or any(b <= 0 for b in cfg.budgets) or list(cfg.budgets) != sorted(set(cfg.budgets)):
        raise ValueError("budgets must be positive, unique and ascending")
    if cfg.top_n <= 0 or cfg.budget_top_n <= 0:
        raise ValueError("top_n and budget_top_n must be positive")
    if "collection" not in cfg.scopes or not set(cfg.scopes) <= set(SCOPES) or len(set(cfg.scopes)) != len(cfg.scopes):
        raise ValueError(f"scopes must be distinct values of {list(SCOPES)}, including collection")
    if cfg.search_depth <= 0:
        raise ValueError("search_depth must be positive")
    smallest = [c.chunk_tokens for c in cfg.chunkings if c.method == "fixed"]
    smallest += [c.child_tokens for c in cfg.chunkings if c.method == "small_to_big"]
    if smallest and cfg.search_depth * min(smallest) < cfg.budgets[-1]:
        raise ValueError(
            f"search_depth {cfg.search_depth} x {min(smallest)}-token chunks cannot fill the {cfg.budgets[-1]} budget"
        )
    cells = {(cell.view, cell.budget, cell.scope) for cell in cfg.export_packed}
    if len(cells) != len(cfg.export_packed):
        raise ValueError("export_packed cells must be distinct")
    for cell in cfg.export_packed:
        if cell.view not in ROUTER_VIEWS:
            raise ValueError(f"export_packed view must be one of {list(ROUTER_VIEWS)}, got {cell.view}")
        if cell.budget not in cfg.budgets:
            raise ValueError(f"export_packed budget {cell.budget} is not one of the run's budgets")
        if cell.scope not in cfg.scopes:
            raise ValueError(f"export_packed scope {cell.scope} is not one of the run's scopes")


def _as_grid(cfg: RoutersConfig) -> GridConfig:
    """The grid config whose retrieval machinery the routers run reuses: the
    production line and the hybrid lists it reranks, at the run's settings."""
    return GridConfig(
        dataset=cfg.dataset,
        sources=cfg.sources,
        pipelines=(PRODUCTION_LINE, "hybrid"),
        chunkings=cfg.chunkings,
        budgets=cfg.budgets,
        top_n=cfg.top_n,
        side_top_n=cfg.top_n,
        scopes=cfg.scopes,
        fixed_k=(),
        search_depth=cfg.search_depth,
        seed=cfg.seed,
        run_name=cfg.run_name,
        embedders=cfg.embedders,
        rrf_k=cfg.rrf_k,
        rerank_depth=cfg.rerank_depth,
        budget_top_n=cfg.budget_top_n,
    )


def routers_config_hash(cfg: RoutersConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_routers_config(path: Path) -> RoutersConfig:
    return parse_routers_config(yaml.safe_load(path.read_text(encoding="utf-8")))


# --- cross-chunking fusion -------------------------------------------------


def fuse_by_span(
    rankings: Sequence[Sequence[Chunk]], span: Callable[[Chunk], tuple], names: Sequence[str], k: int = 60
) -> list[tuple[Chunk, str]]:
    """Fuse one ranking per chunking by reciprocal rank fusion, keyed by the
    chunks' span keys: identical text from two chunkings is one item,
    represented by the chunk that first contributed it (with its chunking's
    name, which carries its packing rule)."""
    representatives: dict[tuple, tuple[Chunk, str]] = {}
    keyed: list[list[tuple]] = []
    for name, ranking in zip(names, rankings, strict=True):
        keys: list[tuple] = []
        for chunk in ranking:
            key = span(chunk)
            if key not in representatives:
                representatives[key] = (chunk, name)
            keys.append(key)
        keyed.append(keys)
    fused = reciprocal_rank_fusion(keyed, k)
    return [representatives[key] for key in fused]


# --- the routers run -------------------------------------------------------


@dataclass(frozen=True)
class RoutersOutcome:
    config: RoutersConfig
    config_hash: str
    n_questions: int
    query_types: dict[str, int]
    run_dir: Path
    picks: dict[str, int]  # the confidence router's picks per chunking


def _pipeline(rankings: Sequence[Ranking], pipeline: str, embedder: str) -> Ranking:
    for ranking in rankings:
        if ranking.pipeline == pipeline and ranking.embedder == embedder:
            return ranking
    raise ValueError(f"no {pipeline} ranking for embedder {embedder}")


def confidence_pick(top1: Mapping[str, float], size_order: Sequence[str]) -> str:
    """The confidence router's pick: the chunking whose top-1 reranker score
    is highest, ties going to the smaller chunk in the size order (the
    oracle router's tie-break order)."""
    rank = {name: i for i, name in enumerate(size_order)}
    return min(top1, key=lambda name: (-top1[name], rank[name]))


def _short_gold(question: Question, qtype: str, tokenized: dict[str, TokenText]) -> list[tuple[int, ...]]:
    if qtype != PRECISE or not question.short_annotators:
        return []
    return [
        tuple(
            sorted(
                frozenset().union(
                    *(tokenized[question.doc_id].token_indices_overlapping(s.start, s.end) for s in annotator)
                )
            )
        )
        for annotator in question.short_annotators
    ]


def _score_packed(
    cell: dict,
    question: Question,
    gold: list[tuple[int, ...]],
    short_gold: list[tuple[int, ...]],
    packed_chunks: list[Chunk],
    view: str,
    top_n: int,
    budget: int,
    scope: str,
    fair: list[Chunk],
    head_only: list[Chunk],
    routed: _Columns,
    packed: _Columns,
    exports: set[tuple[str, int, int, str]],
    picked_chunking: str | None,
    chunking_of: dict[int, str] | None,
) -> None:
    """Score one packed list over merged text and record its routed row (and
    its packed spans for an exported cell)."""
    retrieved = union_token_count(packed_chunks)
    score = score_question(gold, packed_chunks, question.doc_id, retrieved=retrieved)
    short_recall = (
        score_question(short_gold, packed_chunks, question.doc_id, retrieved=retrieved).recall if short_gold else None
    )
    routed.add(
        **cell,
        chunking=None,
        view=view,
        top_n=top_n,
        budget=budget,
        scored=True,
        recall=score.recall,
        precision=score.precision,
        short_recall=short_recall,
        retrieved_tokens=score.retrieved_tokens,
        gold_tokens=score.gold_tokens,
        n_chunks=len(packed_chunks),
        kept_annotator=score.annotator,
        cap_bound=len(fair) > len(packed_chunks),
        used_tail=len(packed_chunks) > len(head_only),
        picked_chunking=picked_chunking,
    )
    if (view, top_n, budget, scope) in exports:
        for rank, chunk in enumerate(packed_chunks, start=1):
            packed.add(
                **{**cell, "doc_id": chunk.doc_id},
                chunking=picked_chunking if picked_chunking is not None else chunking_of[id(chunk)],
                view=view,
                budget=budget,
                rank=rank,
                start=chunk.start,
                end=chunk.end,
                tokens=chunk.n_tokens,
            )


def run_routers(
    cfg: RoutersConfig,
    paths: Paths,
    encoding=None,
    sample: int | None = None,
    models: ModelSource | None = None,
) -> RoutersOutcome:
    started = time.monotonic()
    cfg_hash = routers_config_hash(cfg)
    splits, documents, spans_verified = load_datasets(paths, cfg.sources)
    run_name = cfg.run_name
    if sample is not None:
        splits = sample_papers(splits, sample, cfg.seed)
        documents = {doc.doc_id: doc for split in splits for doc in split.documents}
        run_name = f"{cfg.run_name}-sample{sample}"
    tokenized = {doc_id: TokenText(documents[doc_id].text, encoding) for doc_id in sorted(documents)}
    run_dir = paths.run_dir(run_name, cfg.dataset)
    run_dir.mkdir(parents=True, exist_ok=True)
    cache = Cache(paths.cache / "rag-cache.sqlite")
    retriever = Retriever(
        _as_grid(cfg), documents, models if models is not None else Models(paths.data), cache, run_dir / "lance"
    )
    all_questions = [(split.dataset, question) for split in splits for question in split.questions]
    retriever.embed_questions([question for _, question in all_questions])
    chunkings: list[_Chunking] = []
    chunk_counts: dict[str, int] = {}
    for spec in cfg.chunkings:
        chunking, _ = _build_chunking(spec, documents, tokenized, run_dir / "lance")
        retriever.index_chunking(spec.name, [u for doc_id in sorted(documents) for u in chunking.units_by_doc[doc_id]])
        chunkings.append(chunking)
        chunk_counts[spec.name] = sum(len(units) for units in chunking.units_by_doc.values())
    small_to_big = [c for c in chunkings if c.spec.method == "small_to_big"]
    parents = small_to_big[0].parents if small_to_big else None
    names = [c.spec.name for c in chunkings]
    by_name = {c.spec.name: c for c in chunkings}
    exports = cfg.export_cells()
    indexed = time.monotonic()

    routed = _Columns(ROUTED_SCHEMA)
    packed = _Columns(PACKED_SCHEMA)
    query_types = {t: 0 for t in QUERY_TYPES}
    query_types_by_dataset: dict[str, dict[str, int]] = {}
    picks: Counter[str] = Counter()
    for done, (dataset, question) in enumerate(all_questions, start=1):
        qtype = question_query_type(question)
        query_types[qtype] += 1
        per_dataset = query_types_by_dataset.setdefault(dataset, {t: 0 for t in QUERY_TYPES})
        per_dataset[qtype] += 1
        keys = {
            "dataset": dataset,
            "split": question.split,
            "question_id": question.question_id,
            "doc_id": question.doc_id,
            "query_type": qtype,
        }
        gold = gold_token_sets(question, tokenized)
        short_gold = _short_gold(question, qtype, tokenized)
        rankings = retriever.rank(question, [(c.spec.name, c.index) for c in chunkings], cfg.scopes)
        for scope in cfg.scopes:
            for embedder in cfg.embedders:
                cell = {**keys, "embedder": embedder, "scope": scope, "truncated_share": None}
                hybrid = {name: _pipeline(rankings[(name, scope)], "hybrid", embedder).ranked for name in names}
                production = {name: _pipeline(rankings[(name, scope)], PRODUCTION_LINE, embedder) for name in names}

                # search-all: fuse the hybrid lists, rerank the fused top, pack over overlaps
                fused = fuse_by_span(
                    [hybrid[name] for name in names], lambda chunk: (chunk.doc_id, chunk.start, chunk.end), names, cfg.rrf_k
                )
                head = [chunk for chunk, _ in fused[: cfg.fused_rerank_depth]]
                fused_scores = retriever._rerank_scores(question.text, [head])
                ranked = rerank_head(
                    fused,
                    cfg.fused_rerank_depth,
                    lambda items, scores=fused_scores: [scores[retriever.span(chunk)] for chunk, _ in items],
                )
                ranked_chunks = [chunk for chunk, _ in ranked]
                chunking_of = {id(chunk): name for chunk, name in fused}
                if parents is not None:  # a packed parent belongs to the small-to-big chunking
                    for parent in parents.values():
                        chunking_of[id(parent)] = small_to_big[0].spec.name
                for budget in cfg.budgets:
                    fair = pack_union(ranked_chunks, budget, None, parents)
                    for view, top_n in cfg.views:
                        packed_chunks = pack_union(ranked_chunks, budget, top_n, parents)
                        head_only = pack_union(ranked_chunks[: cfg.fused_rerank_depth], budget, top_n, parents)
                        _score_packed(
                            {**cell, "pipeline": SEARCH_ALL},
                            question,
                            gold,
                            short_gold,
                            packed_chunks,
                            view,
                            top_n,
                            budget,
                            scope,
                            fair,
                            head_only,
                            routed,
                            packed,
                            exports,
                            picked_chunking=None,
                            chunking_of=chunking_of,
                        )

                # confidence: the chunking whose reranked top result scores highest
                top1 = {
                    name: production[name].scores[0] if production[name].scores else float("-inf") for name in names
                }
                pick = confidence_pick(top1, cfg.size_order)
                if scope == cfg.scopes[0] and embedder == cfg.embedders[0]:
                    picks[pick] += 1
                picked = production[pick]
                picked_chunking = by_name[pick]
                head_chunks = picked.ranked[: picked.reranked or 0]
                for budget in cfg.budgets:
                    fair = picked_chunking.packer(picked.ranked, budget, None)
                    for view, top_n in cfg.views:
                        packed_chunks = picked_chunking.packer(picked.ranked, budget, top_n)
                        head_only = picked_chunking.packer(head_chunks, budget, top_n)
                        _score_packed(
                            {**cell, "pipeline": CONFIDENCE},
                            question,
                            gold,
                            short_gold,
                            packed_chunks,
                            view,
                            top_n,
                            budget,
                            scope,
                            fair,
                            head_only,
                            routed,
                            packed,
                            exports,
                            picked_chunking=pick,
                            chunking_of=None,
                        )
        if done % 50 == 0 or done == len(all_questions):
            elapsed = time.monotonic() - indexed
            print(
                f"  questions {done}/{len(all_questions)}, {elapsed / 60:.1f} min, "
                f"~{elapsed / done * (len(all_questions) - done) / 60:.0f} min left, "
                f"reranker pairs scored {retriever.stats.pairs_scored}",
                flush=True,
            )
    cache.close()
    retrieved_at = time.monotonic()

    routed.write(run_dir / "routed.parquet")
    if cfg.export_packed:
        packed.write(run_dir / "packed.parquet")

    nq_split = next((split for split in splits if split.dataset == "nq"), None)
    manifest = {
        "config": cfg.as_dict(),
        "config_hash": cfg_hash,
        "schema_version": ROUTED_SCHEMA_VERSION,
        "sample": None if sample is None else {"documents": len(documents), "requested": sample, "seed": cfg.seed},
        "datasets": dataset_split_hashes(splits),
        "versions": library_versions() | _model_versions(),
        "counts": {
            "documents": len(documents),
            "chunks": chunk_counts,
            "questions": sum(query_types.values()),
            "query_types": query_types,
            "query_types_by_dataset": query_types_by_dataset,
            "excluded_by_reason": excluded_counts(splits),
            "labelled_spans_verified": spans_verified,
            "nq_subset": {
                "file": "configs/nq-subset.txt",
                "ids": nq_split.subset_size,
                "sha256": nq_split.subset_hash,
            }
            if nq_split is not None
            else None,
        },
        "models": _model_manifest(_as_grid(cfg)),
        "truncated_share": {
            spec.name: {e: retriever.truncated[(spec.name, e)] for e in cfg.embedders} for spec in cfg.chunkings
        },
        "reranker": retriever.stats.as_dict()
        | {
            "routers": {
                "per_chunking_rerank_depth": cfg.rerank_depth,
                "fused_rerank_depth": cfg.fused_rerank_depth,
                "pairs_per_question": {
                    SEARCH_ALL: cfg.fused_rerank_depth,
                    CONFIDENCE: len(cfg.chunkings) * cfg.rerank_depth,
                },
            }
        },
        "embeddings": retriever.embed_stats.as_dict(),
        "phase_seconds": {
            "load_embed_and_index": round(indexed - started, 3),
            "retrieve_rerank_and_score": round(retrieved_at - indexed, 3),
            "write": round(time.monotonic() - retrieved_at, 3),
        },
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    n_questions = sum(query_types.values())
    print(f"routers {run_name}: {n_questions} questions x {len(chunkings)} chunkings x {len(cfg.budgets)} budgets")
    print("  query types: " + ", ".join(f"{t} {n}" for t, n in query_types.items()))
    print("  confidence picks: " + ", ".join(f"{name} {picks[name]}" for name in cfg.size_order if picks[name]))
    print(f"  reranker: {retriever.stats.as_dict()}")
    print(f"  embeddings: {retriever.embed_stats.as_dict()}")
    print(f"  wall time: {manifest['duration_seconds'] / 60:.1f} min")
    print(f"  per-question rows: {run_dir / 'routed.parquet'}")
    return RoutersOutcome(
        config=cfg,
        config_hash=cfg_hash,
        n_questions=n_questions,
        query_types=query_types,
        run_dir=run_dir,
        picks=dict(picks),
    )


# --- the R11 table config --------------------------------------------------


@dataclass(frozen=True)
class RoutersTableConfig:
    runs: tuple[str, ...]  # routers runs under runs/, one per dataset
    baselines: tuple[str, ...]  # the baseline grid runs the routers are measured against
    scope: str
    pipeline: str  # the production line's name in the baselines
    embedder: str
    chunkings: tuple[str, ...]  # smallest chunk first: the oracle router's tie-break order
    baseline_chunking: str  # the single chunking the routers are measured against
    top_n: int  # the production view's cap
    budget_top_n: int  # the budget view's cap
    run_name: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "routers-table",
            "runs": list(self.runs),
            "baselines": list(self.baselines),
            "scope": self.scope,
            "pipeline": self.pipeline,
            "embedder": self.embedder,
            "chunkings": list(self.chunkings),
            "baseline_chunking": self.baseline_chunking,
            "top_n": self.top_n,
            "budget_top_n": self.budget_top_n,
            "run_name": self.run_name,
        }

    @property
    def views(self) -> tuple[tuple[str, int], ...]:
        return (("budget", self.budget_top_n), ("production", self.top_n))


def parse_routers_table_config(raw: dict[str, Any]) -> RoutersTableConfig:
    try:
        if raw.get("kind") != "routers-table":
            raise ValueError("a routers table config needs `kind: routers-table`")
        cfg = RoutersTableConfig(
            runs=tuple(str(r) for r in raw["runs"]),
            baselines=tuple(str(r) for r in raw["baselines"]),
            scope=str(raw.get("scope", "collection")),
            pipeline=str(raw.get("pipeline", PRODUCTION_LINE)),
            embedder=str(raw.get("embedder", "nomic")),
            chunkings=tuple(str(c) for c in raw["chunkings"]),
            baseline_chunking=str(raw["baseline_chunking"]),
            top_n=int(raw["top_n"]),
            budget_top_n=int(raw["budget_top_n"]),
            run_name=str(raw.get("run_name", "routers")),
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"invalid routers table config: {exc}") from exc
    for values, label in ((cfg.runs, "runs"), (cfg.baselines, "baselines")):
        if not values or len(set(values)) != len(values):
            raise ValueError(f"{label} must be a non-empty list of distinct run names")
    if not cfg.chunkings or len(set(cfg.chunkings)) != len(cfg.chunkings):
        raise ValueError("chunkings must be a non-empty list of distinct names, smallest chunk first")
    if cfg.baseline_chunking not in cfg.chunkings:
        raise ValueError("baseline_chunking must be one of the chunkings")
    if cfg.top_n <= 0 or cfg.budget_top_n <= 0:
        raise ValueError("top_n and budget_top_n must be positive")
    if cfg.embedder not in EMBEDDERS:
        raise ValueError(f"unknown embedder: {cfg.embedder}")
    return cfg


def load_routers_table_config(path: Path) -> RoutersTableConfig:
    return parse_routers_table_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def routers_table_config_hash(cfg: RoutersTableConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --- loading the runs ------------------------------------------------------


def _run_hash(run_dir: Path) -> str:
    manifest = run_dir / "manifest.json"
    return json.loads(manifest.read_text(encoding="utf-8")).get("config_hash", NA) if manifest.exists() else NA


def _filter(table: pa.Table, **equal: Any) -> pa.Table:
    """Keep the rows whose columns equal the given values (None: is null)."""
    mask = pa.scalar(True)
    for name, value in equal.items():
        condition = pc.is_null(table[name]) if value is None else pc.equal(table[name].fill_null(NA), value)
        mask = pc.and_kleene(mask, condition)
    return table.filter(mask.fill_null(False))


@dataclass
class _Cell:
    """One system's per-question values in one (view, budget) cell."""

    recall: list[float] = field(default_factory=list)
    precision: list[float] = field(default_factory=list)
    retrieved: list[int] = field(default_factory=list)
    chunks: list[int] = field(default_factory=list)


@dataclass
class _Dataset:
    name: str  # a dataset, or "pooled"
    members: tuple[str, ...]  # the datasets pooled into this group
    n_questions: int
    documents: int
    type_counts: dict[str, int]
    cells: dict[tuple[str, int, int], dict[str, _Cell]]  # (view, top_n, budget) -> system -> values
    picks: Counter[str]
    budgets: tuple[int, ...]


def _load_routers_rows(cfg: RoutersTableConfig, run_dir: Path, dataset: str) -> list[dict]:
    rows = _filter(
        pq.read_table(
            run_dir / "routed.parquet",
            columns=[
                "dataset",
                "question_id",
                "doc_id",
                "query_type",
                "pipeline",
                "embedder",
                "scope",
                "picked_chunking",
                "view",
                "top_n",
                "budget",
                "recall",
                "precision",
                "retrieved_tokens",
                "n_chunks",
            ],
        ),
        dataset=dataset,
        scope=cfg.scope,
        embedder=cfg.embedder,
    ).to_pylist()
    if not rows:
        raise ValueError(f"no routed rows for dataset {dataset} in {run_dir}")
    return rows


def _load_baseline_rows(cfg: RoutersTableConfig, run_dir: Path, dataset: str) -> list[dict]:
    rows = _filter(
        pq.read_table(
            run_dir / "results.parquet",
            columns=[
                "dataset",
                "question_id",
                "doc_id",
                "query_type",
                "pipeline",
                "embedder",
                "scope",
                "chunking",
                "view",
                "top_n",
                "budget",
                "scored",
                "recall",
                "precision",
                "retrieved_tokens",
                "n_chunks",
            ],
        ),
        dataset=dataset,
        scope=cfg.scope,
        pipeline=cfg.pipeline,
        embedder=cfg.embedder,
    ).to_pylist()
    rows = [row for row in rows if (row["view"], row["top_n"]) in cfg.views]
    scored = [row for row in rows if row["scored"]]
    if not scored:
        raise ValueError(f"no scored baseline rows for dataset {dataset} in {run_dir}")
    return scored


def _dataset_group(
    cfg: RoutersTableConfig, dataset: str, routers_rows: list[dict], baseline_rows: list[dict]
) -> _Dataset:
    """One dataset's group: the two routers, the baseline chunking and the
    oracle router, per (view, cap, budget) cell."""
    size_rank = {name: i for i, name in enumerate(cfg.chunkings)}
    budgets = tuple(sorted({row["budget"] for row in routers_rows}))
    views = {row["view"]: row["top_n"] for row in routers_rows}
    if set(views) != {view for view, _ in cfg.views}:
        raise ValueError(f"dataset {dataset}: the routed rows cover views {sorted(views)}, not both analysed views")

    questions: dict[str, dict] = {}  # the routers' questions, in first-appearance order
    picks: Counter[str] = Counter()
    cells: dict[tuple[str, int, int], dict[str, _Cell]] = {}
    for row in routers_rows:
        question = questions.setdefault(row["question_id"], {"query_type": row["query_type"], "doc_id": row["doc_id"]})
        if question["query_type"] != row["query_type"] or question["doc_id"] != row["doc_id"]:
            raise ValueError(f"dataset {dataset}: question {row['question_id']} has inconsistent rows")
        if row["pipeline"] == CONFIDENCE:
            pick = row["picked_chunking"]
            if pick not in cfg.chunkings:
                raise ValueError(f"confidence pick {pick} is not one of the chunkings")
            previous = question.setdefault("pick", pick)
            if previous != pick:
                raise ValueError(
                    f"dataset {dataset}: the confidence pick differs across cells for {row['question_id']}"
                )
        cell = cells.setdefault((row["view"], row["top_n"], row["budget"]), {}).setdefault(row["pipeline"], _Cell())
        cell.recall.append(row["recall"])
        cell.precision.append(row["precision"])
        cell.retrieved.append(row["retrieved_tokens"])
        cell.chunks.append(row["n_chunks"])
    if any("pick" not in q for q in questions.values()):
        raise ValueError(f"dataset {dataset}: a question has no confidence rows")
    for question in questions.values():
        picks[question["pick"]] += 1
    for key, systems in cells.items():
        for pipeline in (SEARCH_ALL, CONFIDENCE):
            if pipeline not in systems or len(systems[pipeline].recall) != len(questions):
                raise ValueError(f"dataset {dataset}: cell {key} lacks {pipeline} rows for some questions")

    # the baseline chunking and the oracle router, from the baseline run's per-question rows
    baseline: dict[tuple[str, int, int], dict[str, dict[str, dict]]] = {}
    baseline_questions = {row["question_id"] for row in baseline_rows}
    if baseline_questions != set(questions):
        raise ValueError(f"dataset {dataset}: the routers and baseline runs cover different questions")
    for row in baseline_rows:
        baseline.setdefault((row["view"], row["top_n"], row["budget"]), {}).setdefault(row["chunking"], {})[
            row["question_id"]
        ] = row
    for key, systems in cells.items():
        by_chunking = baseline.get(key, {})
        systems[cfg.baseline_chunking] = _Cell()
        oracle = _Cell()
        for question_id in questions:
            row = by_chunking.get(cfg.baseline_chunking, {}).get(question_id)
            if row is None:
                raise ValueError(f"dataset {dataset}: the baseline lacks {cfg.baseline_chunking} for {question_id}")
            systems[cfg.baseline_chunking].recall.append(row["recall"])
            systems[cfg.baseline_chunking].precision.append(row["precision"])
            systems[cfg.baseline_chunking].retrieved.append(row["retrieved_tokens"])
            systems[cfg.baseline_chunking].chunks.append(row["n_chunks"])
            candidates = [name for name in cfg.chunkings if question_id in by_chunking.get(name, {})]
            if not candidates:
                raise ValueError(f"dataset {dataset}: no chunking scored for {question_id} in cell {key}")
            best = min(candidates, key=lambda name: (-by_chunking[name][question_id]["recall"], size_rank[name]))
            oracle.recall.append(by_chunking[best][question_id]["recall"])
            oracle.precision.append(by_chunking[best][question_id]["precision"])
            oracle.retrieved.append(by_chunking[best][question_id]["retrieved_tokens"])
            oracle.chunks.append(by_chunking[best][question_id]["n_chunks"])
        systems["oracle"] = oracle

    return _Dataset(
        name=dataset,
        members=(dataset,),
        n_questions=len(questions),
        documents=len({q["doc_id"] for q in questions.values()}),
        type_counts=Counter(q["query_type"] for q in questions.values()),
        cells=cells,
        picks=picks,
        budgets=budgets,
    )


def _pooled_group(datasets: Sequence[_Dataset]) -> _Dataset:
    """The pooled group: every dataset's per-question values together."""
    if len({dataset.budgets for dataset in datasets}) > 1:
        raise ValueError("the routers runs cover different budgets; pool runs with the same budgets")
    cells: dict[tuple[str, int, int], dict[str, _Cell]] = {}
    picks: Counter[str] = Counter()
    for dataset in datasets:
        for key, systems in dataset.cells.items():
            pooled = cells.setdefault(key, {name: _Cell() for name in systems})
            for name, cell in systems.items():
                pooled[name].recall += cell.recall
                pooled[name].precision += cell.precision
                pooled[name].retrieved += cell.retrieved
                pooled[name].chunks += cell.chunks
        picks += dataset.picks
    type_counts: Counter[str] = Counter()
    for dataset in datasets:
        type_counts += Counter(dataset.type_counts)
    return _Dataset(
        name="pooled",
        members=tuple(d.name for d in datasets),
        n_questions=sum(d.n_questions for d in datasets),
        documents=sum(d.documents for d in datasets),
        type_counts=dict(type_counts),
        cells=cells,
        picks=picks,
        budgets=datasets[0].budgets,
    )


# --- rendering -------------------------------------------------------------


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values) if values else 0.0


def _pick_share(picks: Counter[str], name: str, total: int) -> str:
    return f"{picks[name] / total:.4f} ({picks[name]})" if total else NA


def _r11(cfg: RoutersTableConfig, cfg_hash: str, inputs: list[tuple[str, str, str]], group: _Dataset) -> str:
    systems = [
        (cfg.baseline_chunking, cfg.baseline_chunking),
        ("oracle", "oracle router"),
        (SEARCH_ALL, "search-all routing"),
        (CONFIDENCE, "confidence routing"),
    ]
    lines = [
        "# R11 - v2 routers: search-all and confidence routing",
        "",
        f"Config hash: `{cfg_hash}`",
        "",
        "## Config",
        "",
        "```yaml",
        yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n"),
        "```",
        "",
        "## Inputs",
        "",
        "| run | kind | run config hash |",
        "|---|---|---|",
    ]
    lines += [f"| {run} | {kind} | `{run_hash}` |" for run, kind, run_hash in inputs]
    lines += [
        "",
        "| dataset | documents | " + " | ".join(QUERY_TYPES) + " | questions |",
        "|---|---|---|---|---|---|",
    ]
    counts = [group.type_counts.get(t, 0) for t in QUERY_TYPES]
    lines.append(
        f"| {group.name} | {group.documents} | " + " | ".join(str(n) for n in counts) + f" | {group.n_questions} |"
    )
    lines += [
        "",
        (
            f"Systems: `search-all` and `confidence` (embedder {cfg.embedder}) from the routers runs; "
            f"`{cfg.pipeline}` (the production line) from the baseline runs, {cfg.scope} search."
        ),
        "",
    ]
    note = (
        "Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); "
        "the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per "
        "question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are "
        "means per question."
    )
    for view, top_n in cfg.views:
        title = "budget view" if view == "budget" else "production view"
        lines += [
            f"## Retrieval, {title} (top-N cap {top_n})",
            "",
            note,
            "",
            "| dataset | budget | system | recall | precision | retrieved tokens | chunks |",
            "|---|---|---|---|---|---|---|",
        ]
        for budget in group.budgets:
            cell = group.cells[(view, top_n, budget)]
            for key, label in systems:
                values = cell[key]
                lines.append(
                    f"| {group.name} | {budget} | {label} | {_fmt(_mean(values.recall))} | "
                    f"{_fmt(_mean(values.precision))} | {_mean(values.retrieved):.1f} | "
                    f"{_mean(values.chunks):.2f} |"
                )
        lines += ["", ""]
    lines += [
        "## Confidence routing's chunking picks",
        "",
        (
            "The pick is the chunking whose reranked top result scores highest (the top-1 reranker score of each "
            "chunking's reranked top 30), ties to the smaller chunk; it does not depend on the budget or the view."
        ),
        "",
        "| dataset | " + " | ".join(cfg.chunkings) + " | all |",
        "|---|" + "---|" * (len(cfg.chunkings) + 1),
    ]
    shares = [_pick_share(group.picks, name, group.n_questions) for name in cfg.chunkings]
    lines.append(f"| {group.name} | " + " | ".join(shares) + f" | {group.n_questions} |")
    lines += [
        "",
        "## Notes",
        "",
        (
            "- Reranker pairs per question: 30 for one chunking's production line, 50 for search-all routing "
            "(the fused top 50) and 210 for confidence routing (seven chunkings x reranked top 30)."
        ),
        (
            "- Search-all routing fuses the seven chunkings' hybrid lists by reciprocal rank fusion (k = 60) keyed "
            "by document and character span, so identical text from two chunkings is one item; it reranks the fused "
            "top 50 and packs by budget counting overlapping text once. Small-to-big children return their parents "
            "under v1's rule."
        ),
        (
            "- For search-all the reader text is the packed spans merged per document, in order of first "
            "appearance, so no text is repeated."
        ),
        (
            "- Both routers are scored at every budget even when the confidence pick's chunks exceed it: a "
            "fixed-1024 pick at a 128-token budget retrieves nothing there."
        ),
        (
            "- These tables regenerate byte-identically from the same runs: means are summed with math.fsum and "
            "nothing run-specific enters a table."
        ),
        "",
    ]
    return "\n".join(lines)


# --- entry points ----------------------------------------------------------


@dataclass(frozen=True)
class RoutersTableOutcome:
    config_hash: str
    groups: tuple[str, ...]
    tables: tuple[Path, ...]


def run_routers_table(cfg: RoutersTableConfig, paths: Paths) -> RoutersTableOutcome:
    started = time.monotonic()
    cfg_hash = routers_table_config_hash(cfg)

    def datasets_of(run: str, file: str) -> set[str]:
        table = pq.read_table(paths.run_dir(run) / file, columns=["dataset"])
        return set(pc.unique(table["dataset"]).fill_null(NA).to_pylist())

    routers_runs: dict[str, str] = {}
    for run in cfg.runs:
        for dataset in datasets_of(run, "routed.parquet"):
            if dataset in routers_runs:
                raise ValueError(f"dataset {dataset} appears in several routers runs")
            routers_runs[dataset] = run
    baseline_runs: dict[str, str] = {}
    for run in cfg.baselines:
        for dataset in datasets_of(run, "results.parquet"):
            if dataset in baseline_runs:
                raise ValueError(f"dataset {dataset} appears in several baseline runs")
            baseline_runs[dataset] = run
    datasets = sorted(routers_runs)
    if not datasets:
        raise ValueError("the routers runs hold no datasets")
    unknown = sorted(set(baseline_runs) - set(routers_runs))
    if unknown:
        raise ValueError(f"baseline runs cover datasets with no routers run: {unknown}")
    missing = [d for d in datasets if d not in baseline_runs]
    if missing:
        raise ValueError(f"datasets with no baseline run: {missing}")

    inputs: list[tuple[str, str, str]] = []
    groups: list[_Dataset] = []
    for dataset in datasets:
        routers_rows = _load_routers_rows(cfg, paths.run_dir(routers_runs[dataset]), dataset)
        baseline_rows = _load_baseline_rows(cfg, paths.run_dir(baseline_runs[dataset]), dataset)
        groups.append(_dataset_group(cfg, dataset, routers_rows, baseline_rows))
        inputs.append((routers_runs[dataset], "routers", _run_hash(paths.run_dir(routers_runs[dataset]))))
        inputs.append((baseline_runs[dataset], "grid", _run_hash(paths.run_dir(baseline_runs[dataset]))))
    rendered = list(groups) + ([_pooled_group(groups)] if len(groups) > 1 else [])

    tables: list[Path] = []
    for group in rendered:
        out_dir = paths.results / group.name
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"r11-{cfg.run_name}.md"
        path.write_text(_r11(cfg, cfg_hash, inputs, group), encoding="utf-8")
        tables.append(path)
    print(f"routers table {cfg.run_name}: {len(rendered)} groups over {len(datasets)} datasets")
    for dataset in datasets:
        group = next(g for g in groups if g.name == dataset)
        picks = ", ".join(f"{name} {group.picks[name]}" for name in cfg.chunkings if group.picks[name])
        print(f"  {dataset}: {group.n_questions} questions, confidence picks {picks}")
    for path in tables:
        print(f"  result table: {path}")
    print(f"  {time.monotonic() - started:.1f} s")
    return RoutersTableOutcome(config_hash=cfg_hash, groups=tuple(g.name for g in rendered), tables=tuple(tables))
