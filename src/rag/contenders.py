"""`rag contenders <config>`: an indexing contender's retrieval recall and
precision next to the chunkings it is compared with, per dataset and
pooled, read from the per-question results of one grid run per dataset
(runs/<dataset>/<run_name>/results.parquet). No retrieval runs here.

Each cell is the mean over the questions of one dataset, or of every
run's questions pooled, for one chunking, view and budget under the
configured pipeline, embedder and search scope. Two views are read: the
budget view (each run's `budget_top_n`) and the production view (its
`top_n`). A `pairs` entry (contender, reference) adds the contender's
difference from the reference, as for late-128 against fixed-128, which
share every span and differ only in their vectors. Optional `notes`
are printed under the tables (a config without them keeps its hash).

One table per run's dataset, results/<dataset>/<table>-<run_name>.md,
each with that dataset's cells and the pooled ones. Means use math.fsum
and nothing run-specific enters a table, so the same runs regenerate
the tables byte-identically.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import yaml

from .config import PRODUCTION_LINE
from .paths import Paths

NA = "n/a"
POOLED = "pooled"
VIEWS = ("budget", "production")


@dataclass(frozen=True)
class ContendersConfig:
    table: str  # table id, such as r12
    title: str
    runs: tuple[str, ...]  # one grid run per dataset, under runs/
    chunkings: tuple[str, ...]  # table order
    pairs: tuple[tuple[str, str], ...]  # (contender, reference)
    run_name: str
    scope: str = "collection"
    pipeline: str = PRODUCTION_LINE
    embedder: str = "nomic"
    notes: tuple[str, ...] = ()  # printed under the tables

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "kind": "contenders",
            "table": self.table,
            "title": self.title,
            "runs": list(self.runs),
            "scope": self.scope,
            "pipeline": self.pipeline,
            "embedder": self.embedder,
            "chunkings": list(self.chunkings),
            "pairs": [list(p) for p in self.pairs],
            "run_name": self.run_name,
        }
        if self.notes:
            out["notes"] = list(self.notes)
        return out


def load_contenders_config(path: Path) -> ContendersConfig:
    return parse_contenders_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def parse_contenders_config(raw: dict[str, Any]) -> ContendersConfig:
    try:
        if raw.get("kind") != "contenders":
            raise ValueError("a contenders config needs `kind: contenders`")
        cfg = ContendersConfig(
            table=str(raw["table"]),
            title=str(raw["title"]),
            runs=tuple(str(r) for r in raw["runs"]),
            chunkings=tuple(str(c) for c in raw["chunkings"]),
            pairs=tuple((str(a), str(b)) for a, b in raw.get("pairs", ())),
            run_name=str(raw["run_name"]),
            scope=str(raw.get("scope", "collection")),
            pipeline=str(raw.get("pipeline", PRODUCTION_LINE)),
            embedder=str(raw.get("embedder", "nomic")),
            notes=tuple(str(note) for note in raw.get("notes", ())),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid contenders config: {exc}") from exc
    if not cfg.runs or len(set(cfg.runs)) != len(cfg.runs):
        raise ValueError("runs must be a non-empty list of distinct run names")
    if not cfg.chunkings or len(set(cfg.chunkings)) != len(cfg.chunkings):
        raise ValueError("chunkings must be a non-empty list of distinct names")
    if any(name not in cfg.chunkings for pair in cfg.pairs for name in pair):
        raise ValueError("every pair must name two of the chunkings")
    return cfg


def contenders_config_hash(cfg: ContendersConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class _Cell:
    scored: bool = True
    recall: list[float] = field(default_factory=list)
    precision: list[float] = field(default_factory=list)

    def mean(self, metric: str) -> float | None:
        values = getattr(self, metric)
        return math.fsum(values) / len(values) if self.scored and values else None


@dataclass(frozen=True)
class _Run:
    name: str
    dataset: str
    config_hash: str
    datasets: dict[str, str]  # split -> sha256
    questions: int
    cells: dict[tuple[str, str, int], _Cell]  # (chunking, view, budget)


def _load_run(cfg: ContendersConfig, paths: Paths, name: str) -> tuple[_Run, dict[str, Any]]:
    run_dir = paths.runs / name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    grid = manifest["config"]
    if grid.get("budget_top_n") is None:
        raise ValueError(f"run {name} has no budget view (budget_top_n)")
    caps = {"budget": grid["budget_top_n"], "production": grid["top_n"]}
    rows = pq.read_table(
        run_dir / "results.parquet",
        columns=[
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
        ],
    ).to_pydict()
    cells: dict[tuple[str, str, int], _Cell] = defaultdict(_Cell)
    for pipeline, embedder, scope, chunking, view, top_n, budget, scored, recall, precision in zip(
        *rows.values(), strict=True
    ):
        if (pipeline, embedder, scope) != (cfg.pipeline, cfg.embedder, cfg.scope) or chunking not in cfg.chunkings:
            continue
        if view not in caps or top_n != caps[view]:
            continue
        cell = cells[(chunking, view, budget)]
        if not scored:
            cell.scored = False
            continue
        cell.recall.append(recall)
        cell.precision.append(precision)
    missing = [c for c in cfg.chunkings if not any(key[0] == c for key in cells)]
    if missing:
        raise ValueError(f"run {name} has no {cfg.pipeline} x {cfg.embedder} rows for {missing}")
    run = _Run(
        name=name,
        dataset=grid["dataset"]["name"],
        config_hash=manifest["config_hash"],
        datasets=manifest["datasets"],
        questions=manifest["counts"]["questions"],
        cells=dict(cells),
    )
    return run, grid


def _pool(runs: list[_Run]) -> dict[tuple[str, str, int], _Cell]:
    pooled: dict[tuple[str, str, int], _Cell] = defaultdict(_Cell)
    for run in runs:
        for key, cell in run.cells.items():
            target = pooled[key]
            target.scored = target.scored and cell.scored
            target.recall += cell.recall
            target.precision += cell.precision
    return dict(pooled)


def _fmt(value: float | None, signed: bool = False) -> str:
    if value is None:
        return NA
    return f"{value:+.4f}" if signed else f"{value:.4f}"


def _render(
    cfg: ContendersConfig,
    cfg_hash: str,
    run: _Run,
    runs: list[_Run],
    pooled: dict[tuple[str, str, int], _Cell],
    budgets: list[int],
    caps: dict[str, int],
) -> str:
    groups = [(run.dataset, run.cells), (POOLED, pooled)]
    n_pooled = sum(r.questions for r in runs)
    pooled_label = f"{POOLED} ({' + '.join(r.dataset for r in runs)})"
    lines = [
        f"# {cfg.table.upper()} - {run.dataset} {cfg.run_name}: {cfg.title}",
        "",
        f"Config hash: `{cfg_hash}`",
        "",
        "## Config",
        "",
        "```yaml",
        yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n"),
        "```",
        "",
        "## Runs",
        "",
        "| run | dataset | questions | config hash |",
        "|---|---|---|---|",
        *(f"| {r.name} | {r.dataset} | {r.questions} | `{r.config_hash}` |" for r in runs),
        "",
        "## Dataset",
        "",
        "| dataset | split | sha256 |",
        "|---|---|---|",
        *(f"| {r.dataset} | {split} | `{r.datasets[split]}` |" for r in runs for split in sorted(r.datasets)),
        "",
        (
            f"Retrieval recall and precision, {cfg.pipeline} with {cfg.embedder}, {cfg.scope} search: "
            f"{run.dataset} (n = {run.questions}) and {pooled_label} (n = {n_pooled}), means over questions."
        ),
    ]
    for view in VIEWS:
        lines += [
            "",
            f"## {view.capitalize()} view (top-N cap {caps[view]})",
            "",
            f"| chunking | budget | {run.dataset} recall | {run.dataset} precision | pooled recall | pooled precision |",
            "|---|---|---|---|---|---|",
        ]
        for chunking in cfg.chunkings:
            for budget in budgets:
                values = [
                    _fmt(cells[(chunking, view, budget)].mean(metric))
                    for _, cells in groups
                    for metric in ("recall", "precision")
                ]
                lines.append(f"| {chunking} | {budget} | " + " | ".join(values) + " |")
    if cfg.pairs:
        lines += [
            "",
            "## Contender minus reference",
            "",
            (
                "| contender - reference | view | budget | "
                f"{run.dataset} recall | {run.dataset} precision | pooled recall | pooled precision |"
            ),
            "|---|---|---|---|---|---|---|",
        ]
        for contender, reference in cfg.pairs:
            for view in VIEWS:
                for budget in budgets:
                    values = []
                    for _, cells in groups:
                        for metric in ("recall", "precision"):
                            a = cells[(contender, view, budget)].mean(metric)
                            b = cells[(reference, view, budget)].mean(metric)
                            values.append(_fmt(None if a is None or b is None else a - b, signed=True))
                    lines.append(f"| {contender} - {reference} | {view} | {budget} | " + " | ".join(values) + " |")
    lines += [
        "",
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        *(line for note in cfg.notes for line in ("", note)),
        "",
    ]
    return "\n".join(lines)


def run_contenders(cfg: ContendersConfig, paths: Paths) -> tuple[Path, ...]:
    """Render one table per run's dataset; returns their paths."""
    loaded = [_load_run(cfg, paths, name) for name in cfg.runs]
    runs = [run for run, _ in loaded]
    if len({r.dataset for r in runs}) != len(runs):
        raise ValueError("each run must be of a different dataset")
    grids = [grid for _, grid in loaded]
    shape = {(tuple(g["budgets"]), g["budget_top_n"], g["top_n"]) for g in grids}
    if len(shape) != 1:
        raise ValueError("the runs must share budgets and top-N caps")
    budgets, budget_top_n, top_n = next(iter(shape))
    caps = {"budget": budget_top_n, "production": top_n}
    pooled = _pool(runs)
    cfg_hash = contenders_config_hash(cfg)
    out: list[Path] = []
    for run in runs:
        path = paths.results / run.dataset / f"{cfg.table}-{cfg.run_name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render(cfg, cfg_hash, run, runs, pooled, list(budgets), caps), encoding="utf-8")
        print(f"  result table: {path}")
        out.append(path)
    return tuple(out)
