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

An optional `gate` block adds the pre-registered contender bar of
ADR 0008, judged per pair at one view and budget: the contender's
pooled recall difference from its reference must reach `min_gain` with
a `confidence` interval from the paired, document-clustered bootstrap
(`resamples`, `seed`) excluding 0, and no dataset alone may fall below
`-max_loss`. The verdict is printed under the tables (a config without
a gate keeps its canonical JSON).

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

import numpy as np
import pyarrow.parquet as pq
import yaml

from .bootstrap import Estimate, Interval, clustered_mean, percentile_interval, resample_counts
from .config import PRODUCTION_LINE
from .paths import Paths

NA = "n/a"
POOLED = "pooled"
VIEWS = ("budget", "production")


@dataclass(frozen=True)
class ContendersGate:
    """The pre-registered contender bar of ADR 0008, judged per pair at one
    view and budget: a pooled recall gain of at least `min_gain` whose
    `confidence` interval (paired, document-clustered bootstrap) excludes
    0, and no dataset alone below `-max_loss`."""

    view: str = "budget"
    budget: int = 1024
    min_gain: float = 0.02
    max_loss: float = 0.01
    confidence: float = 0.95
    resamples: int = 10000
    seed: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "view": self.view,
            "budget": self.budget,
            "min_gain": self.min_gain,
            "max_loss": self.max_loss,
            "confidence": self.confidence,
            "resamples": self.resamples,
            "seed": self.seed,
        }


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
    gate: ContendersGate | None = None  # the pre-registered bar verdict

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
        if self.gate is not None:
            out["gate"] = self.gate.as_dict()
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
            gate=_parse_gate(raw["gate"]) if "gate" in raw else None,
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


def _parse_gate(raw: dict[str, Any]) -> ContendersGate:
    gate = ContendersGate(
        view=str(raw.get("view", "budget")),
        budget=int(raw["budget"]) if "budget" in raw else 1024,
        min_gain=float(raw.get("min_gain", 0.02)),
        max_loss=float(raw.get("max_loss", 0.01)),
        confidence=float(raw.get("confidence", 0.95)),
        resamples=int(raw.get("resamples", 10000)),
        seed=int(raw.get("seed", 0)),
    )
    if gate.view not in VIEWS:
        raise ValueError(f"the gate's view must be one of {list(VIEWS)}, got {gate.view}")
    if gate.budget <= 0:
        raise ValueError("the gate's budget must be positive")
    if not 0 < gate.confidence < 1:
        raise ValueError("the gate's confidence must be between 0 and 1")
    if gate.resamples <= 0:
        raise ValueError("the gate's resamples must be positive")
    if gate.min_gain <= 0 or gate.max_loss < 0:
        raise ValueError("the gate's min_gain must be positive and its max_loss at least 0")
    return gate


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


@dataclass
class _Run:
    name: str
    dataset: str
    config_hash: str
    datasets: dict[str, str]  # split -> sha256
    questions: int
    cells: dict[tuple[str, str, int], _Cell]  # (chunking, view, budget)
    # a gate's cell: per-question recall by chunking, and each question's document
    recalls: dict[tuple[str, str, int], dict[str, float]] = field(default_factory=dict)
    docs: dict[str, str] = field(default_factory=dict)


def _load_run(cfg: ContendersConfig, paths: Paths, name: str) -> tuple[_Run, dict[str, Any]]:
    run_dir = paths.runs / name
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    grid = manifest["config"]
    if grid.get("budget_top_n") is None:
        raise ValueError(f"run {name} has no budget view (budget_top_n)")
    caps = {"budget": grid["budget_top_n"], "production": grid["top_n"]}
    gate = cfg.gate
    gate_cell = (gate.view, gate.budget) if gate is not None else None
    columns = [
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
    ]
    if gate is not None:  # the gate pairs per-question values, keyed by question and document
        columns += ["question_id", "doc_id"]
    rows = pq.read_table(run_dir / "results.parquet", columns=columns).to_pydict()
    cells: dict[tuple[str, str, int], _Cell] = defaultdict(_Cell)
    recalls: dict[tuple[str, str, int], dict[str, float]] = defaultdict(dict)
    docs: dict[str, str] = {}
    for row in zip(*rows.values(), strict=True):
        pipeline, embedder, scope, chunking, view, top_n, budget, scored, recall, precision = row[:10]
        qid = row[10] if gate is not None else None
        doc_id = row[11] if gate is not None else None
        if (pipeline, embedder, scope) != (cfg.pipeline, cfg.embedder, cfg.scope) or chunking not in cfg.chunkings:
            continue
        if view not in caps or top_n != caps[view]:
            continue
        if gate_cell == (view, budget) and not scored:
            raise ValueError(
                f"run {name}: {chunking} is not scored for every question at {budget} tokens in the {view} view; "
                "the gate needs every question scored"
            )
        cell = cells[(chunking, view, budget)]
        if not scored:
            cell.scored = False
            continue
        cell.recall.append(recall)
        cell.precision.append(precision)
        if gate_cell == (view, budget):
            recalls[(chunking, view, budget)][qid] = recall
            docs[qid] = doc_id
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
        recalls=dict(recalls),
        docs=docs,
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


# --- the pre-registered bar (ADR 0008) -----------------------------------------


@dataclass(frozen=True)
class _GatePair:
    contender: str
    reference: str
    pooled: Estimate  # the pooled recall difference from the reference
    interval: Interval  # its document-clustered bootstrap interval
    per_dataset: dict[str, Estimate]  # each dataset's difference


def _pair_diffs(run: _Run, gate: ContendersGate, contender: str, reference: str) -> tuple[np.ndarray, np.ndarray]:
    """One run's paired per-question differences at the gate's cell, and
    the document of each question."""
    cells = {name: run.recalls.get((name, gate.view, gate.budget), {}) for name in (contender, reference)}
    if not all(cells.values()):
        missing = [name for name, values in cells.items() if not values]
        raise ValueError(
            f"run {run.name} has no {' or '.join(missing)} rows at {gate.budget} tokens in the {gate.view} view; "
            f"the gate's budget must be one of the run's budgets"
        )
    if sorted(cells[contender]) != sorted(cells[reference]):
        raise ValueError(
            f"run {run.name}: {contender} and {reference} cover different questions at {gate.budget} tokens "
            f"in the {gate.view} view"
        )
    order = sorted(cells[contender])
    diffs = np.array([cells[contender][q] - cells[reference][q] for q in order])
    return diffs, np.array([run.docs[q] for q in order])


def _gate_estimates(cfg: ContendersConfig, runs: list[_Run]) -> list[_GatePair]:
    """Each pair's pooled recall difference with its interval from the
    paired, document-clustered bootstrap, and each dataset's difference.
    As in the answers stage, a dataset's draws are the same whether it is
    analysed alone or pooled (the resample stratum is the dataset)."""
    gate = cfg.gate
    assert gate is not None
    out: list[_GatePair] = []
    for contender, reference in cfg.pairs:
        per_dataset: dict[str, Estimate] = {}
        diffs_parts: list[np.ndarray] = []
        cluster_parts: list[np.ndarray] = []
        draws_parts: list[np.ndarray] = []
        offset = 0
        for run in runs:
            diffs, docs = _pair_diffs(run, gate, contender, reference)
            names = sorted(set(docs.tolist()))
            cluster = np.array([names.index(d) for d in docs.tolist()])
            draws = resample_counts(len(names), gate.resamples, gate.seed, run.dataset)
            per_dataset[run.dataset] = clustered_mean(diffs, cluster, draws)
            diffs_parts.append(diffs)
            cluster_parts.append(cluster + offset)
            draws_parts.append(draws)
            offset += len(names)
        pooled = clustered_mean(np.concatenate(diffs_parts), np.concatenate(cluster_parts), np.hstack(draws_parts))
        out.append(
            _GatePair(
                contender=contender,
                reference=reference,
                pooled=pooled,
                interval=percentile_interval(pooled.samples, gate.confidence),
                per_dataset=per_dataset,
            )
        )
    return out


def _gate_lines(cfg: ContendersConfig, pairs: list[_GatePair], caps: dict[str, int]) -> list[str]:
    """The pre-registered bar in plain words: where it was judged, each
    pair's differences and the verdict."""
    gate = cfg.gate
    assert gate is not None
    lines = [
        "## Bar verdict (pre-registered)",
        "",
        (
            f"Judged on the {cfg.pipeline} pipeline with {cfg.embedder}, {gate.view} view (top-N cap {caps[gate.view]}), "
            f"{gate.budget}-token budget, pooled over the runs' datasets, with a {gate.confidence:.0%} CI from the "
            f"paired, document-clustered bootstrap ({gate.resamples} resamples, seed {gate.seed})."
        ),
        "",
    ]
    for pair in pairs:
        per_dataset = ", ".join(f"{ds} {_fmt(e.point, signed=True)}" for ds, e in sorted(pair.per_dataset.items()))
        lines.append(
            f"- {pair.contender} - {pair.reference}, pooled: {_fmt(pair.pooled.point, signed=True)} "
            f"[{_fmt(pair.interval.low, signed=True)}, {_fmt(pair.interval.high, signed=True)}]; {per_dataset}."
        )
        reasons = []
        if pair.pooled.point < gate.min_gain:
            reasons.append(f"the pooled gain is below +{gate.min_gain:.4f}")
        if not pair.interval.excludes_zero:
            reasons.append("its CI includes 0")
        worse = sorted(ds for ds, e in pair.per_dataset.items() if e.point < -gate.max_loss)
        if worse:
            reasons.append(
                f"{' and '.join(worse)} alone {'is' if len(worse) == 1 else 'are'} below -{gate.max_loss:.4f}"
            )
        if reasons:
            lines.append(f"- **Verdict: {pair.contender} does not clear the bar** ({'; '.join(reasons)}).")
        else:
            lines.append(
                f"- **Verdict: {pair.contender} clears the bar** (pooled gain at least +{gate.min_gain:.4f} with a "
                f"CI excluding 0, and neither dataset alone below -{gate.max_loss:.4f})."
            )
    lines.append("")
    return lines


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
    gate_pairs: list[_GatePair] | None = None,
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
    if gate_pairs is not None:
        lines += _gate_lines(cfg, gate_pairs, caps)
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
    gate_pairs = _gate_estimates(cfg, runs) if cfg.gate is not None else None
    cfg_hash = contenders_config_hash(cfg)
    out: list[Path] = []
    for run in runs:
        path = paths.results / run.dataset / f"{cfg.table}-{cfg.run_name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_render(cfg, cfg_hash, run, runs, pooled, list(budgets), caps, gate_pairs), encoding="utf-8")
        print(f"  result table: {path}")
        out.append(path)
    return tuple(out)
