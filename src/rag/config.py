"""Run config (YAML) and its content hash.

Ticket keys: dataset, chunking, pipeline, budget, view, seed. The config
hash is the sha256 of the config's canonical JSON, so the same settings
always hash identically whatever the file's formatting.
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


def config_hash(cfg: RunConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def config_yaml(cfg: RunConfig) -> str:
    """Canonical YAML rendering used in the result table (sorted keys)."""
    return yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n")
