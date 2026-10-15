"""Run configs (YAML) and their content hash.

Two kinds: a single-cell run (`RunConfig`: dataset, chunking, pipeline,
budget, view, seed), and a grid run (`GridConfig`, `kind: grid`: every
chunking at every budget, in both views and both search scopes, under one
or more retrieval pipelines). The config hash is the sha256 of the
config's canonical JSON, so the same settings always hash identically
whatever the file's formatting.

The dataset block names either one dataset with its splits (`qasper`,
`nq`) or several sources labelled `pooled`, whose questions and
documents are loaded together so every table is computed over both
while each dataset's n stays visible. A single dataset renders exactly
as before, so existing config hashes are unchanged.

A grid names its pipelines with `pipelines:` (and the embedders the
vector-based ones use with `embedders:`); the BM25-only form
`pipeline: bm25` stays valid and keeps its canonical JSON, and so its hash.

An optional `budget_top_n` adds the budget view (as many reranked whole
chunks as fit the token budget, at most that many per question) next to
the production and fair views, and an optional `export_packed` lists the
(view, budget, scope) cells whose packed chunks are written to the run's
`packed.parquet`. A config without these keys keeps its canonical JSON,
and so its hash: v1 configs render exactly as before.

A fixed chunking can set `embedding: late` (default `chunk`): late
chunking, the same spans with vectors pooled from the whole document's
token embeddings (see rag.late). Only that chunking's canonical JSON
gains the key.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

KNOWN_DATASETS = {"qasper", "nq"}
DATASET_SPLITS = {"qasper": {"train", "dev", "test"}, "nq": {"dev"}}
POOLED = "pooled"


@dataclass(frozen=True)
class DatasetRef:
    """One dataset with the splits the run loads."""

    name: str
    splits: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "splits": list(self.splits)}


def _parse_dataset(raw: dict[str, Any]) -> tuple[str, tuple[DatasetRef, ...]]:
    """The dataset label and its sources: one `{name, splits}` block or a
    `{name: pooled, sources: [...]}` block."""
    try:
        label = raw["name"]
        if "sources" in raw:
            sources = tuple(DatasetRef(s["name"], tuple(s["splits"])) for s in raw["sources"])
        else:
            sources = (DatasetRef(label, tuple(raw["splits"])),)
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid dataset block: {exc}") from exc
    if not isinstance(label, str) or not label:
        raise ValueError("dataset name must be a non-empty string")
    if "sources" in raw:
        if len(sources) < 2:
            raise ValueError("a sources list needs at least two datasets")
        if label != POOLED:
            raise ValueError(f"a multi-source dataset must be labelled {POOLED}, got {label}")
        if len({s.name for s in sources}) != len(sources):
            raise ValueError("pooled sources must name each dataset once")
    for source in sources:
        if source.name not in KNOWN_DATASETS:
            raise ValueError(f"unknown dataset: {source.name}")
        known_splits = DATASET_SPLITS[source.name]
        if not source.splits or not set(source.splits) <= known_splits:
            raise ValueError(f"{source.name} splits must be a non-empty subset of {sorted(known_splits)}")
    return label, sources


def _dataset_dict(label: str, sources: tuple[DatasetRef, ...]) -> dict[str, Any]:
    if len(sources) == 1:
        return sources[0].as_dict()
    return {"name": label, "sources": [s.as_dict() for s in sources]}


@dataclass(frozen=True)
class RunConfig:
    dataset: str
    sources: tuple[DatasetRef, ...]
    chunking_method: str
    chunk_tokens: int
    overlap: int
    pipeline: str
    budget: int
    view: str
    top_n: int
    seed: int
    search_depth: int
    run_name: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "dataset": _dataset_dict(self.dataset, self.sources),
            "chunking": {
                "method": self.chunking_method,
                "chunk_tokens": self.chunk_tokens,
                "overlap": self.overlap,
            },
            "pipeline": self.pipeline,
            "budget": self.budget,
            "view": self.view,
            "top_n": self.top_n,
            "seed": self.seed,
            "search_depth": self.search_depth,
            "run_name": self.run_name,
        }


def load_config(path: Path) -> RunConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return parse_config(raw)


def load_any_config(path: Path) -> RunConfig | GridConfig:
    """A grid config when the file says `kind: grid`, else a single-cell run."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and raw.get("kind") == "grid":
        return parse_grid_config(raw)
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> RunConfig:
    try:
        label, sources = _parse_dataset(raw["dataset"])
        cfg = RunConfig(
            dataset=label,
            sources=sources,
            chunking_method=raw["chunking"]["method"],
            chunk_tokens=int(raw["chunking"]["chunk_tokens"]),
            overlap=int(raw["chunking"].get("overlap", 0)),
            pipeline=raw["pipeline"],
            budget=int(raw["budget"]),
            view=raw["view"],
            top_n=int(raw["top_n"]),
            seed=int(raw["seed"]),
            search_depth=int(raw.get("search_depth", 100)),
            run_name=raw.get("run_name", "run"),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid run config: {exc}") from exc
    _validate(cfg)
    return cfg


def _validate(cfg: RunConfig) -> None:
    if cfg.dataset not in KNOWN_DATASETS and cfg.dataset != POOLED:
        raise ValueError(f"unknown dataset: {cfg.dataset}")
    if cfg.chunking_method != "fixed":
        raise ValueError(f"unknown chunking method: {cfg.chunking_method}")
    if cfg.chunk_tokens <= 0:
        raise ValueError("chunk_tokens must be positive")
    if cfg.overlap != 0:
        raise ValueError("only overlap 0 is supported")
    if cfg.pipeline != "bm25":
        raise ValueError(f"unknown pipeline: {cfg.pipeline}")
    if cfg.budget <= 0:
        raise ValueError("budget must be positive")
    if cfg.view not in {"production", "fair"}:
        raise ValueError(f"unknown view: {cfg.view}")
    if cfg.view == "production" and cfg.top_n <= 0:
        raise ValueError("top_n must be positive in the production view")
    if cfg.search_depth <= 0:
        raise ValueError("search_depth must be positive")


CHUNKING_METHODS = ("fixed", "section_aware", "small_to_big")
EMBEDDINGS = ("chunk", "late")  # each chunk embedded alone, or late chunking
SCOPES = ("collection", "document")
# the production line first, then its ablations: the order of every table
PRODUCTION_LINE = "hybrid-rerank"  # hybrid search, then the reranker
PIPELINES = (PRODUCTION_LINE, "hybrid", "vector", "bm25")
EMBEDDING_PIPELINES = (PRODUCTION_LINE, "hybrid", "vector")


@dataclass(frozen=True)
class ChunkingSpec:
    """One chunking of the grid: fixed windows (`chunk_tokens`),
    section-aware chunks capped at `max_tokens`, or small-to-big children
    of `child_tokens` under section-aware parents capped at `max_tokens`.
    `embedding` is `late` for late chunking (fixed windows only)."""

    name: str
    method: str
    chunk_tokens: int = 0
    max_tokens: int = 0
    child_tokens: int = 0
    embedding: str = "chunk"

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "method": self.method}
        if self.method == "fixed":
            out["chunk_tokens"] = self.chunk_tokens
        else:
            out["max_tokens"] = self.max_tokens
        if self.method == "small_to_big":
            out["child_tokens"] = self.child_tokens
        if self.late:
            out["embedding"] = self.embedding
        return out

    @property
    def late(self) -> bool:
        return self.embedding == "late"

    @property
    def fixed_size(self) -> int | None:
        """The nominal chunk size of a fixed chunking (None when variable)."""
        return self.chunk_tokens if self.method == "fixed" else None


@dataclass(frozen=True)
class PackedExport:
    """One (view, budget, scope) cell whose packed chunks are written to
    `packed.parquet`: one row per packed chunk, for every pipeline,
    embedder and chunking of the run."""

    view: str
    budget: int
    scope: str

    def as_dict(self) -> dict[str, Any]:
        return {"view": self.view, "budget": self.budget, "scope": self.scope}


@dataclass(frozen=True)
class GridConfig:
    dataset: str
    sources: tuple[DatasetRef, ...]
    pipelines: tuple[str, ...]
    chunkings: tuple[ChunkingSpec, ...]
    budgets: tuple[int, ...]
    top_n: int  # production view
    side_top_n: int  # production view side table
    scopes: tuple[str, ...]
    fixed_k: tuple[int, ...]
    search_depth: int
    seed: int
    run_name: str
    embedders: tuple[str, ...] = ()
    rrf_k: int = 60
    rerank_depth: int = 30

    budget_top_n: int | None = None  # budget view (v2): cap on reranked chunks per question
    export_packed: tuple[PackedExport, ...] = ()  # cells written to packed.parquet

    @property
    def bm25_only(self) -> bool:
        return self.pipelines == ("bm25",)

    @property
    def pipeline(self) -> str:
        """A label for the pipelines, used in table titles."""
        return "bm25" if self.bm25_only else "production line and ablations"

    def as_dict(self) -> dict[str, Any]:
        if self.bm25_only:
            pipelines: dict[str, Any] = {"pipeline": "bm25"}
        else:
            pipelines = {
                "pipelines": list(self.pipelines),
                "embedders": list(self.embedders),
                "rrf_k": self.rrf_k,
                "rerank_depth": self.rerank_depth,
            }
        out: dict[str, Any] = {
            "kind": "grid",
            "dataset": _dataset_dict(self.dataset, self.sources),
            **pipelines,
            "chunkings": [c.as_dict() for c in self.chunkings],
            "budgets": list(self.budgets),
            "top_n": self.top_n,
            "side_top_n": self.side_top_n,
            "scopes": list(self.scopes),
            "fixed_k": list(self.fixed_k),
            "search_depth": self.search_depth,
            "seed": self.seed,
            "run_name": self.run_name,
        }
        if self.budget_top_n is not None:
            out["budget_top_n"] = self.budget_top_n
        if self.export_packed:
            out["export_packed"] = [cell.as_dict() for cell in self.export_packed]
        return out


def _parse_chunking(raw: dict[str, Any]) -> ChunkingSpec:
    method = raw["method"]
    if method not in CHUNKING_METHODS:
        raise ValueError(f"unknown chunking method: {method}")
    if int(raw.get("overlap", 0)) != 0:
        raise ValueError("only overlap 0 is supported")
    spec = ChunkingSpec(
        name=str(raw["name"]),
        method=method,
        chunk_tokens=int(raw["chunk_tokens"]) if method == "fixed" else 0,
        max_tokens=int(raw["max_tokens"]) if method != "fixed" else 0,
        child_tokens=int(raw["child_tokens"]) if method == "small_to_big" else 0,
        embedding=str(raw.get("embedding", "chunk")),
    )
    if spec.embedding not in EMBEDDINGS:
        raise ValueError(f"chunking {spec.name}: embedding must be one of {list(EMBEDDINGS)}")
    if spec.late and method != "fixed":
        raise ValueError(f"chunking {spec.name}: late chunking needs fixed windows")
    sizes = {"fixed": [spec.chunk_tokens], "section_aware": [spec.max_tokens]}.get(
        method, [spec.max_tokens, spec.child_tokens]
    )
    if any(n <= 0 for n in sizes):
        raise ValueError(f"chunking {spec.name}: token sizes must be positive")
    return spec


def parse_grid_config(raw: dict[str, Any]) -> GridConfig:
    try:
        if ("pipeline" in raw) == ("pipelines" in raw):
            raise ValueError("give exactly one of `pipeline` and `pipelines`")
        pipelines = tuple(raw["pipelines"]) if "pipelines" in raw else (raw["pipeline"],)
        label, sources = _parse_dataset(raw["dataset"])
        cfg = GridConfig(
            dataset=label,
            sources=sources,
            pipelines=pipelines,
            chunkings=tuple(_parse_chunking(c) for c in raw["chunkings"]),
            budgets=tuple(int(b) for b in raw["budgets"]),
            top_n=int(raw["top_n"]),
            side_top_n=int(raw["side_top_n"]),
            scopes=tuple(raw["scopes"]),
            fixed_k=tuple(int(k) for k in raw["fixed_k"]),
            search_depth=int(raw.get("search_depth", 1000)),
            seed=int(raw["seed"]),
            run_name=raw.get("run_name", "grid"),
            embedders=tuple(raw.get("embedders", ())),
            rrf_k=int(raw.get("rrf_k", 60)),
            rerank_depth=int(raw.get("rerank_depth", 30)),
            budget_top_n=int(raw["budget_top_n"]) if "budget_top_n" in raw else None,
            export_packed=tuple(
                PackedExport(view=str(cell["view"]), budget=int(cell["budget"]), scope=str(cell["scope"]))
                for cell in raw.get("export_packed", ())
            ),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid grid config: {exc}") from exc
    _validate_grid(cfg)
    return cfg


def _validate_grid(cfg: GridConfig) -> None:
    if cfg.dataset not in KNOWN_DATASETS and cfg.dataset != POOLED:
        raise ValueError(f"unknown dataset: {cfg.dataset}")
    _validate_pipelines(cfg)
    names = [c.name for c in cfg.chunkings]
    if not names or len(set(names)) != len(names):
        raise ValueError("chunkings must be a non-empty list with unique names")
    for name, values in (("budgets", cfg.budgets), ("fixed_k", cfg.fixed_k)):
        if not values or any(v <= 0 for v in values) or list(values) != sorted(set(values)):
            raise ValueError(f"{name} must be positive, unique and ascending")
    if cfg.top_n <= 0 or cfg.side_top_n <= 0:
        raise ValueError("top_n and side_top_n must be positive")
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
    _validate_late(cfg)
    if cfg.budget_top_n is not None and cfg.budget_top_n <= 0:
        raise ValueError("budget_top_n must be positive")
    cells = {(cell.view, cell.budget, cell.scope) for cell in cfg.export_packed}
    if len(cells) != len(cfg.export_packed):
        raise ValueError("export_packed cells must be distinct")
    for cell in cfg.export_packed:
        if cell.view not in {"production", "fair", "budget"}:
            raise ValueError(f"export_packed view must be production, fair or budget, got {cell.view}")
        if cell.budget not in cfg.budgets:
            raise ValueError(f"export_packed budget {cell.budget} is not one of the run's budgets")
        if cell.scope not in cfg.scopes:
            raise ValueError(f"export_packed scope {cell.scope} is not one of the run's scopes")
        if cell.view == "budget" and cfg.budget_top_n is None:
            raise ValueError("export_packed view budget needs budget_top_n")


def _validate_pipelines(cfg: GridConfig) -> None:
    from .models import EMBEDDERS

    if not cfg.pipelines or len(set(cfg.pipelines)) != len(cfg.pipelines) or not set(cfg.pipelines) <= set(PIPELINES):
        raise ValueError(f"pipelines must be distinct values of {list(PIPELINES)}")
    if len(set(cfg.embedders)) != len(cfg.embedders) or not set(cfg.embedders) <= set(EMBEDDERS):
        raise ValueError(f"embedders must be distinct values of {sorted(EMBEDDERS)}")
    needs_embedder = bool(set(cfg.pipelines) & set(EMBEDDING_PIPELINES))
    if needs_embedder != bool(cfg.embedders):
        raise ValueError("embedders are required by, and only by, the vector, hybrid and hybrid-rerank pipelines")
    if cfg.rrf_k <= 0 or cfg.rerank_depth <= 0:
        raise ValueError("rrf_k and rerank_depth must be positive")


def _validate_late(cfg: GridConfig) -> None:
    from .late import LATE_WINDOW, WINDOW_BLOCK_TOKENS
    from .models import EMBEDDERS

    late = [c for c in cfg.chunkings if c.late]
    if not late:
        return
    if not cfg.embedders:
        raise ValueError("late chunking needs an embedder")
    short = [e for e in cfg.embedders if EMBEDDERS[e].max_tokens < LATE_WINDOW]
    if short:
        raise ValueError(f"late chunking needs embedders that read {LATE_WINDOW} tokens; {short} read fewer")
    for spec in late:
        if WINDOW_BLOCK_TOKENS % spec.chunk_tokens:
            raise ValueError(
                f"chunking {spec.name}: late chunks must divide the {WINDOW_BLOCK_TOKENS}-token blocks windows are cut at"
            )


def config_hash(cfg: RunConfig | GridConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def config_yaml(cfg: RunConfig | GridConfig) -> str:
    """Canonical YAML rendering used in the result table (sorted keys)."""
    return yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n")
