"""Run configs (YAML) and their content hash.

Two kinds: a single-cell run (`RunConfig`: dataset, chunking, pipeline,
budget, view, seed), and a grid run (`GridConfig`, `kind: grid`: every
chunking at every budget, in both views and both search scopes, under one
or more retrieval pipelines). The config hash is the sha256 of the
config's canonical JSON, so the same settings always hash identically
whatever the file's formatting.

A grid names its pipelines with `pipelines:` (and the embedders the
vector-based ones use with `embedders:`); the BM25-only form
`pipeline: bm25` stays valid and keeps its canonical JSON, and so its hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RunConfig:
    dataset: str
    splits: tuple[str, ...]
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
            "dataset": {"name": self.dataset, "splits": list(self.splits)},
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
        dataset = raw["dataset"]
        cfg = RunConfig(
            dataset=dataset["name"],
            splits=tuple(dataset["splits"]),
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
    if cfg.dataset != "qasper":
        raise ValueError(f"unknown dataset: {cfg.dataset}")
    known_splits = {"train", "dev", "test"}
    if not cfg.splits or not set(cfg.splits) <= known_splits:
        raise ValueError(f"splits must be a non-empty subset of {sorted(known_splits)}")
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
SCOPES = ("collection", "document")
# the production line first, then its ablations: the order of every table
PIPELINES = ("production", "hybrid", "vector", "bm25")
EMBEDDING_PIPELINES = ("production", "hybrid", "vector")


@dataclass(frozen=True)
class ChunkingSpec:
    """One chunking of the grid: fixed windows (`chunk_tokens`),
    section-aware chunks capped at `max_tokens`, or small-to-big children
    of `child_tokens` under section-aware parents capped at `max_tokens`."""

    name: str
    method: str
    chunk_tokens: int = 0
    max_tokens: int = 0
    child_tokens: int = 0

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "method": self.method}
        if self.method == "fixed":
            out["chunk_tokens"] = self.chunk_tokens
        else:
            out["max_tokens"] = self.max_tokens
        if self.method == "small_to_big":
            out["child_tokens"] = self.child_tokens
        return out

    @property
    def fixed_size(self) -> int | None:
        """The nominal chunk size of a fixed chunking (None when variable)."""
        return self.chunk_tokens if self.method == "fixed" else None


@dataclass(frozen=True)
class GridConfig:
    dataset: str
    splits: tuple[str, ...]
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
        return {
            "kind": "grid",
            "dataset": {"name": self.dataset, "splits": list(self.splits)},
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
    )
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
        cfg = GridConfig(
            dataset=raw["dataset"]["name"],
            splits=tuple(raw["dataset"]["splits"]),
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
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid grid config: {exc}") from exc
    _validate_grid(cfg)
    return cfg


def _validate_grid(cfg: GridConfig) -> None:
    if cfg.dataset != "qasper":
        raise ValueError(f"unknown dataset: {cfg.dataset}")
    known_splits = {"train", "dev", "test"}
    if not cfg.splits or not set(cfg.splits) <= known_splits:
        raise ValueError(f"splits must be a non-empty subset of {sorted(known_splits)}")
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


def _validate_pipelines(cfg: GridConfig) -> None:
    from .models import EMBEDDERS

    if not cfg.pipelines or len(set(cfg.pipelines)) != len(cfg.pipelines) or not set(cfg.pipelines) <= set(PIPELINES):
        raise ValueError(f"pipelines must be distinct values of {list(PIPELINES)}")
    if len(set(cfg.embedders)) != len(cfg.embedders) or not set(cfg.embedders) <= set(EMBEDDERS):
        raise ValueError(f"embedders must be distinct values of {sorted(EMBEDDERS)}")
    needs_embedder = bool(set(cfg.pipelines) & set(EMBEDDING_PIPELINES))
    if needs_embedder != bool(cfg.embedders):
        raise ValueError("embedders are required by, and only by, the vector, hybrid and production pipelines")
    if cfg.rrf_k <= 0 or cfg.rerank_depth <= 0:
        raise ValueError("rrf_k and rerank_depth must be positive")


def config_hash(cfg: RunConfig | GridConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def config_yaml(cfg: RunConfig | GridConfig) -> str:
    """Canonical YAML rendering used in the result table (sorted keys)."""
    return yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n")
