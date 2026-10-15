"""`rag headroom <config>`: the best single chunking, the oracle router's
routing headroom over it and the chunk size x query type interaction,
each with a paired, document-clustered bootstrap CI, read from the
per-question results of one or more grid runs (runs/<run>/results.parquet).
No retrieval runs here.

The config's `view` selects which view the analysis reads (production,
the default, fair or budget); for a capped view `top_n` names its cap,
so the production view's side-table rows stay out. The pre-registered
router gate is an optional `gate` block: with it, R7 reports its verdict
as before; without it, R7 reports the best single chunking, the oracle
router and the routing headroom with no gate verdict.

A cell is one dataset group (each dataset, and all of them pooled when
there are several), pipeline, embedder, view and budget, under one search
scope. Its candidate chunkings are those scored at that budget for every
question; a fixed chunking bigger than the budget is not a candidate.
Documents are the clusters: each dataset's documents are drawn with
replacement, and a pooled resample draws every dataset's documents at
once with the same draws as that dataset alone.

The 95% CI at the pre-registered primary budget is unadjusted; at every
other budget a statistic gets Holm-adjusted CIs over its family of
non-primary budgets (same group, pipeline, embedder, view and chunking).

Tables, written to results/routing/ and byte-identical for the same seed
and inputs:

- R7: routing headroom, the router gate verdict per embedder, the
  query-type oracle and every chunking's difference from the best single
  chunking;
- R8: the interaction of each chunking against a smaller reference;
- R9: which chunking the oracle router picks, by query type, at the
  primary budget.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

from .bootstrap import (
    CellAnalysis,
    Estimate,
    Interaction,
    Interval,
    analyse_cell,
    holm_intervals,
    percentile_interval,
    resample_counts,
)
from .config import PRODUCTION_LINE
from .paths import Paths
from .query_type import CONTEXT, MIXED, PRECISE, QUERY_TYPES

VIEWS = ("production", "fair", "budget")
NA = "n/a"
NO_EMBEDDER = "-"


@dataclass(frozen=True)
class HeadroomConfig:
    runs: tuple[str, ...]  # grid runs under runs/ whose results are pooled
    scope: str
    top_n: int  # the analysed capped view's top-N cap (production or budget view)
    chunkings: tuple[str, ...]  # smallest chunk first: the tie-break order
    interaction_reference: str
    production_line: str  # pipeline name of the production line
    view: str  # which view the analysis reads: production (default), fair or budget
    primary_budget: int  # unadjusted CI at this budget, Holm elsewhere
    gate_datasets: tuple[str, ...]  # empty when no gate block is configured
    min_headroom: float
    confidence: float
    resamples: int
    seed: int
    run_name: str

    @property
    def gated(self) -> bool:
        """Whether the config pre-registers the router gate."""
        return bool(self.gate_datasets)

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "kind": "headroom",
            "runs": list(self.runs),
            "scope": self.scope,
        }
        if self.view != "production":
            out["view"] = self.view
        out |= {
            "top_n": self.top_n,
            "chunkings": list(self.chunkings),
            "interaction_reference": self.interaction_reference,
        }
        if self.gated:
            out["gate"] = {
                "pipeline": self.production_line,
                "datasets": list(self.gate_datasets),
                "budget": self.primary_budget,
                "min_headroom": self.min_headroom,
                "confidence": self.confidence,
            }
        else:
            out["primary_budget"] = self.primary_budget
        out |= {
            "resamples": self.resamples,
            "seed": self.seed,
            "run_name": self.run_name,
        }
        return out


def load_headroom_config(path: Path) -> HeadroomConfig:
    return parse_headroom_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def parse_headroom_config(raw: dict[str, Any]) -> HeadroomConfig:
    try:
        if raw.get("kind") != "headroom":
            raise ValueError("a headroom config needs `kind: headroom`")
        gate = raw.get("gate")
        if gate is not None and not gate["datasets"]:
            raise ValueError("gate datasets must not be empty")
        primary_budget = int(raw["primary_budget"]) if "primary_budget" in raw else None
        if gate is not None:
            gate_budget = int(gate["budget"])
            if primary_budget is not None and primary_budget != gate_budget:
                raise ValueError("primary_budget and gate budget disagree; give one or make them equal")
            primary_budget = gate_budget
        if primary_budget is None:
            raise ValueError("give the gate budget, or primary_budget when the gate block is absent")
        cfg = HeadroomConfig(
            runs=tuple(str(r) for r in raw["runs"]),
            scope=str(raw.get("scope", "collection")),
            top_n=int(raw["top_n"]),
            chunkings=tuple(str(c) for c in raw["chunkings"]),
            interaction_reference=str(raw["interaction_reference"]),
            production_line=str(gate["pipeline"]) if gate is not None else str(raw.get("pipeline", PRODUCTION_LINE)),
            view=str(raw.get("view", "production")),
            primary_budget=primary_budget,
            gate_datasets=tuple(str(d) for d in gate["datasets"]) if gate is not None else (),
            min_headroom=float(gate["min_headroom"]) if gate is not None else 0.0,
            confidence=float(gate["confidence"]) if gate is not None else 0.95,
            resamples=int(raw["resamples"]),
            seed=int(raw["seed"]),
            run_name=str(raw.get("run_name", "headroom")),
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"invalid headroom config: {exc}") from exc
    if not cfg.runs or len(set(cfg.runs)) != len(cfg.runs):
        raise ValueError("runs must be a non-empty list of distinct run names")
    if not cfg.chunkings or len(set(cfg.chunkings)) != len(cfg.chunkings):
        raise ValueError("chunkings must be a non-empty list of distinct names, smallest chunk first")
    if cfg.interaction_reference not in cfg.chunkings:
        raise ValueError("interaction_reference must be one of the chunkings")
    if cfg.view not in VIEWS:
        raise ValueError(f"view must be one of {list(VIEWS)}, got {cfg.view}")
    if cfg.top_n <= 0 or cfg.primary_budget <= 0 or cfg.resamples <= 0:
        raise ValueError("top_n, primary budget and resamples must be positive")
    if not 0 < cfg.confidence < 1:
        raise ValueError("gate confidence must be between 0 and 1")
    return cfg


def headroom_config_hash(cfg: HeadroomConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --- loading ---------------------------------------------------------------

_COLUMNS = ["dataset", "question_id", "doc_id", "query_type", "pipeline", "embedder", "chunking"]
_COLUMNS += ["scope", "view", "top_n", "budget", "scored", "recall"]


@dataclass(frozen=True)
class Questions:
    """Every question in the inputs, sorted by (dataset, question id)."""

    dataset: list[str]
    query_type: np.ndarray  # index into QUERY_TYPES
    cluster: dict[str, np.ndarray]  # dataset -> per-question document index within the dataset (-1 elsewhere)
    documents: dict[str, int]  # dataset -> documents with at least one question


@dataclass(frozen=True)
class CellRows:
    """One (pipeline, embedder, view, budget) cell: recall per question and
    chunking, and whether each was scored (both questions x chunkings)."""

    recall: np.ndarray
    scored: np.ndarray
    present: np.ndarray  # (questions,) the cell has rows for the question


@dataclass(frozen=True)
class Results:
    questions: Questions
    cells: dict[tuple[str, str, str, int], CellRows]
    run_hashes: dict[str, str]


def _strings(column: pa.ChunkedArray) -> np.ndarray:
    return np.asarray(column.fill_null(NO_EMBEDDER).to_pylist(), dtype=object)


def load_results(cfg: HeadroomConfig, paths: Paths) -> Results:
    tables = []
    run_hashes: dict[str, str] = {}
    for run in cfg.runs:
        run_dir = paths.run_dir(run)
        table = pq.read_table(run_dir / "results.parquet", columns=_COLUMNS)
        # the analysed capped view at its own cap, plus the fair view (which has none)
        in_view = pc.equal(table["view"], "fair")
        if cfg.view != "fair":
            in_view = pc.or_kleene(
                in_view, pc.and_kleene(pc.equal(table["view"], cfg.view), pc.equal(table["top_n"], cfg.top_n))
            )
        mask = pc.and_kleene(pc.equal(table["scope"], cfg.scope), in_view).fill_null(False)
        tables.append(table.filter(mask))
        manifest = run_dir / "manifest.json"
        run_hashes[run] = (
            json.loads(manifest.read_text(encoding="utf-8")).get("config_hash", NA) if manifest.exists() else NA
        )
    table = pa.concat_tables(tables)
    if table.num_rows == 0:
        raise ValueError(f"no results for scope {cfg.scope} in runs {list(cfg.runs)}")

    dataset = _strings(table["dataset"])
    question_id = _strings(table["question_id"])
    keys = np.char.add(np.char.add(dataset.astype(str), "\x1f"), question_id.astype(str))
    unique_keys, first, q_index = np.unique(keys, return_index=True, return_inverse=True)
    doc_id = _strings(table["doc_id"])[first]
    q_dataset = [str(d) for d in dataset[first]]
    raw_types = _strings(table["query_type"])[first]
    unknown = sorted(set(raw_types) - set(QUERY_TYPES))
    if unknown:
        raise ValueError(f"unknown query types in results: {unknown}")
    query_type = np.array([QUERY_TYPES.index(t) for t in raw_types])

    cluster: dict[str, np.ndarray] = {}
    documents: dict[str, int] = {}
    for ds in sorted(set(q_dataset)):
        in_ds = np.array([d == ds for d in q_dataset])
        docs, doc_index = np.unique(doc_id[in_ds].astype(str), return_inverse=True)
        index = np.full(len(unique_keys), -1)
        index[in_ds] = doc_index
        cluster[ds] = index
        documents[ds] = len(docs)
    questions = Questions(
        dataset=q_dataset,
        query_type=query_type,
        cluster=cluster,
        documents=documents,
    )

    chunking = _strings(table["chunking"])
    unknown = sorted(set(chunking) - set(cfg.chunkings))
    if unknown:
        raise ValueError(f"chunkings in the results but not in the config's size order: {unknown}")
    c_index = np.array([cfg.chunkings.index(c) for c in chunking])
    cell_key = np.char.add(
        np.char.add(_strings(table["pipeline"]).astype(str), "\x1f"),
        np.char.add(np.char.add(_strings(table["embedder"]).astype(str), "\x1f"), _strings(table["view"]).astype(str)),
    )
    cell_key = np.char.add(np.char.add(cell_key, "\x1f"), table["budget"].to_numpy().astype(str))
    scored = table["scored"].to_numpy(zero_copy_only=False).astype(bool)
    recall = table["recall"].fill_null(0.0).to_numpy()

    cells: dict[tuple[str, str, str, int], CellRows] = {}
    order = np.argsort(cell_key, kind="stable")
    boundaries = np.flatnonzero(cell_key[order][1:] != cell_key[order][:-1]) + 1
    for rows in np.split(order, boundaries):
        pipeline, embedder, view, budget = str(cell_key[rows[0]]).split("\x1f")
        shape = (len(unique_keys), len(cfg.chunkings))
        cell_recall, cell_scored, seen = np.zeros(shape), np.zeros(shape, dtype=bool), np.zeros(shape, dtype=bool)
        q, c = q_index[rows], c_index[rows]
        if len(np.unique(q * len(cfg.chunkings) + c)) != len(rows):
            raise ValueError(f"duplicate rows for cell {pipeline} {embedder} {view} {budget}")
        seen[q, c] = True
        cell_recall[q, c] = recall[rows]
        cell_scored[q, c] = scored[rows]
        cells[(pipeline, embedder, view, int(budget))] = CellRows(
            recall=cell_recall, scored=cell_scored, present=seen.any(axis=1)
        )
    return Results(questions=questions, cells=cells, run_hashes=run_hashes)


# --- analysis --------------------------------------------------------------


@dataclass(frozen=True)
class Group:
    name: str  # a dataset, or "pooled"
    datasets: tuple[str, ...]


@dataclass(frozen=True)
class CellResult:
    group: Group
    pipeline: str
    embedder: str
    view: str
    budget: int
    candidates: tuple[str, ...]  # chunking names, smallest chunk first
    n_questions: int
    qtype: np.ndarray  # (questions,) index into QUERY_TYPES, in the analysis's question order
    type_counts: dict[str, int]
    analysis: CellAnalysis


def _groups(datasets: Sequence[str]) -> list[Group]:
    singles = [Group(name=ds, datasets=(ds,)) for ds in sorted(datasets)]
    return ([Group(name="pooled", datasets=tuple(sorted(datasets)))] if len(datasets) > 1 else []) + singles


def analyse(cfg: HeadroomConfig, results: Results) -> list[CellResult]:
    qs = results.questions
    counts = {ds: resample_counts(qs.documents[ds], cfg.resamples, cfg.seed, ds) for ds in sorted(qs.documents)}
    q_dataset = np.array(qs.dataset, dtype=object)
    out: list[CellResult] = []
    for (pipeline, embedder, view, budget), cell in sorted(
        results.cells.items(), key=lambda kv: _cell_order(cfg, kv[0])
    ):
        datasets = sorted({qs.dataset[i] for i in np.flatnonzero(cell.present)})
        for ds in datasets:
            missing = int(((q_dataset == ds) & ~cell.present).sum())
            if missing:
                raise ValueError(f"cell {pipeline} {embedder} {view} {budget} lacks {missing} questions of {ds}")
        for group in _groups(datasets):
            rows = np.flatnonzero(np.isin(q_dataset, group.datasets))
            scored = cell.scored[rows]
            partial = [cfg.chunkings[c] for c in range(len(cfg.chunkings)) if 0 < scored[:, c].sum() < len(rows)]
            if partial:
                raise ValueError(f"chunkings scored for only some questions in {pipeline} {view} {budget}: {partial}")
            columns = [c for c in range(len(cfg.chunkings)) if scored[:, c].all()]
            if not columns:
                continue
            offsets = np.cumsum([0] + [qs.documents[ds] for ds in group.datasets])
            cluster = np.zeros(len(rows), dtype=int)
            for ds, offset in zip(group.datasets, offsets, strict=False):
                in_ds = q_dataset[rows] == ds
                cluster[in_ds] = qs.cluster[ds][rows[in_ds]] + offset
            reference = cfg.chunkings.index(cfg.interaction_reference)
            qtype = qs.query_type[rows]
            analysis = analyse_cell(
                cell.recall[np.ix_(rows, columns)],
                cluster,
                qtype,
                np.hstack([counts[ds] for ds in group.datasets]),
                reference=columns.index(reference) if reference in columns else None,
            )
            out.append(
                CellResult(
                    group=group,
                    pipeline=pipeline,
                    embedder=embedder,
                    view=view,
                    budget=budget,
                    candidates=tuple(cfg.chunkings[c] for c in columns),
                    n_questions=len(rows),
                    qtype=qtype,
                    type_counts={t: int((qtype == i).sum()) for i, t in enumerate(QUERY_TYPES)},
                    analysis=analysis,
                )
            )
    group_rank = {name: i for i, name in enumerate(["pooled", *sorted(qs.documents)])}
    return sorted(
        out, key=lambda r: (group_rank[r.group.name], *_cell_order(cfg, (r.pipeline, r.embedder, r.view, r.budget)))
    )


def _cell_order(cfg: HeadroomConfig, key: tuple[str, str, str, int]) -> tuple:
    pipeline, embedder, view, budget = key
    return (pipeline != cfg.production_line, pipeline, embedder, VIEWS.index(view) if view in VIEWS else 99, budget)


def series_intervals(estimates: dict[int, Estimate], primary_budget: int, confidence: float) -> dict[int, Interval]:
    """CIs for one statistic across budgets: unadjusted at the primary budget,
    Holm-adjusted over the other budgets."""
    out = {b: percentile_interval(e.samples, confidence) for b, e in estimates.items() if b == primary_budget}
    others = sorted(b for b in estimates if b != primary_budget)
    for b, interval in zip(others, holm_intervals([estimates[b].samples for b in others], confidence), strict=True):
        out[b] = interval
    return out


def _series(
    results: list[CellResult], cfg: HeadroomConfig, pick: Callable[[CellResult], Estimate | None]
) -> dict[tuple[int, int], Interval]:
    """Intervals keyed by (result index, budget), Holm families formed per
    group, pipeline, embedder and view."""
    families: dict[tuple, dict[int, tuple[int, Estimate]]] = {}
    for i, r in enumerate(results):
        estimate = pick(r)
        if estimate is not None:
            families.setdefault((r.group.name, r.pipeline, r.embedder, r.view), {})[r.budget] = (i, estimate)
    out: dict[tuple[int, int], Interval] = {}
    for members in families.values():
        intervals = series_intervals({b: e for b, (_, e) in members.items()}, cfg.primary_budget, cfg.confidence)
        for b, (i, _) in members.items():
            out[(i, b)] = intervals[b]
    return out


# --- gate ------------------------------------------------------------------


@dataclass(frozen=True)
class GateRow:
    pipeline: str
    embedder: str
    datasets: tuple[str, ...]
    best: str
    headroom: float
    interval: Interval
    clears: bool


def gate_rows(cfg: HeadroomConfig, results: list[CellResult], pipelines: Sequence[str]) -> list[GateRow]:
    """The gate test (headroom >= min_headroom and the CI excludes 0) per
    pipeline and embedder, in the analysed view at the primary budget, on
    the widest group (pooled when the cell has several datasets)."""
    widest: dict[tuple[str, str], CellResult] = {}
    for r in results:
        if r.pipeline not in pipelines or r.view != cfg.view or r.budget != cfg.primary_budget:
            continue
        key = (r.pipeline, r.embedder)
        if key not in widest or len(r.group.datasets) > len(widest[key].group.datasets):
            widest[key] = r
    rows: list[GateRow] = []
    for r in widest.values():
        interval = percentile_interval(r.analysis.headroom.samples, cfg.confidence)
        headroom = r.analysis.headroom.point
        rows.append(
            GateRow(
                pipeline=r.pipeline,
                embedder=r.embedder,
                datasets=r.group.datasets,
                best=r.candidates[r.analysis.best],
                headroom=headroom,
                interval=interval,
                clears=headroom >= cfg.min_headroom and interval.low > 0,
            )
        )
    return rows


def gate_verdict(cfg: HeadroomConfig, results: list[CellResult]) -> list[str]:
    """The router gate in plain words: where it was judged, one line per
    embedder and the decision."""
    rows = gate_rows(cfg, results, [cfg.production_line])
    if not rows:
        pipelines = sorted({r.pipeline for r in results})
        return [
            f"**Gate not judged:** these results hold no production-line pipeline (`{cfg.production_line}`) at "
            f"{cfg.primary_budget} tokens in the {cfg.view} view; pipelines present: "
            + ", ".join(f"`{p}`" for p in pipelines)
            + ". The verdict comes from the re-run on the full results."
        ]
    lines = [
        (
            f"Judged on the production line (`{cfg.production_line}`), {cfg.view} view (top-N cap {cfg.top_n}), "
            f"{cfg.primary_budget}-token budget, {cfg.confidence:.0%} CI."
        )
    ]
    missing = sorted({ds for row in rows for ds in cfg.gate_datasets if ds not in row.datasets})
    if missing:
        lines.append(
            f"**Provisional:** the gate is pre-registered on {' + '.join(cfg.gate_datasets)} pooled, and these "
            f"results lack {', '.join(missing)}."
        )
    for row in rows:
        if row.clears:
            reason = "clears the gate"
        elif row.headroom < cfg.min_headroom:
            reason = f"does not clear the gate: the headroom is below +{cfg.min_headroom:.4f}"
        else:
            reason = "does not clear the gate: its CI includes 0"
        lines.append(
            f"- {row.embedder}, pooled over {' + '.join(row.datasets)}: routing headroom {_signed(row.headroom)} "
            f"{_ci(row.interval)} over the best single chunking ({row.best}), which {reason}."
        )
    cleared = [row.embedder for row in rows if row.clears]
    verb = "clears" if len(cleared) == 1 else "clear"
    lines.append(
        f"**Verdict: build the router in v2** ({', '.join(cleared)} {verb} the gate)."
        if cleared
        else "**Verdict: do not build the router in v2** (no embedder clears the gate)."
    )
    return lines


# --- tables ----------------------------------------------------------------


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _signed(value: float) -> str:
    return f"{value:+.4f}"


def _ci(interval: Interval) -> str:
    return f"[{_signed(interval.low)}, {_signed(interval.high)}]"


def _level(interval: Interval) -> str:
    return f"{interval.confidence * 100:.2f}%"


def _yes(flag: bool) -> str:
    return "yes" if flag else "no"


def _prefix(r: CellResult) -> str:
    return f"| {r.group.name} | {r.pipeline} | {r.embedder} | {r.view} | {r.budget} |"


def _header(title: str, cfg: HeadroomConfig, cfg_hash: str, results: Results) -> list[str]:
    qs = results.questions
    lines = [title, "", f"Config hash: `{cfg_hash}`", "", "## Config", "", "```yaml"]
    lines += [yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n"), "```", ""]
    lines += ["## Inputs", "", "| run | run config hash |", "|---|---|"]
    lines += [f"| {run} | `{h}` |" for run, h in results.run_hashes.items()]
    lines += ["", "| dataset | documents | " + " | ".join(QUERY_TYPES) + " | questions |", "|---|---|---|---|---|---|"]
    for ds in sorted(qs.documents):
        types = [qs.query_type[i] for i, d in enumerate(qs.dataset) if d == ds]
        n = [sum(1 for t in types if t == i) for i in range(len(QUERY_TYPES))]
        lines.append(f"| {ds} | {qs.documents[ds]} | " + " | ".join(str(x) for x in n) + f" | {len(types)} |")
    pipelines = sorted({(p, e) for p, e, _, _ in results.cells})
    lines += ["", "Pipelines: " + ", ".join(f"`{p}` (embedder {e})" for p, e in pipelines) + ".", ""]
    return lines


_CI_NOTE = (
    "CIs: paired bootstrap over documents ({resamples} resamples, seed {seed}), percentile intervals; "
    "{confidence:.0%} unadjusted at the primary budget of {budget} tokens, Holm-adjusted over the other budgets "
    "(the CI level column gives each interval's level)."
)


def _r7(cfg: HeadroomConfig, results: list[CellResult], header: list[str]) -> str:
    lines = list(header)
    if cfg.gated:
        lines += ["## Router gate (pre-registered)", ""]
        lines += [
            (
                f"Rule: build the router in v2 if, on the production line, in the {cfg.view} view, at the primary "
                f"budget of {cfg.primary_budget} tokens, pooled over {' + '.join(cfg.gate_datasets)}, either embedder's "
                f"routing headroom is at least +{cfg.min_headroom:.4f} retrieval recall with a {cfg.confidence:.0%} CI "
                "that excludes 0."
            ),
            "",
        ]
        lines += gate_verdict(cfg, results) + [""]
        reference = gate_rows(cfg, results, sorted({r.pipeline for r in results} - {cfg.production_line}))
        if reference:
            lines += [
                "### The same test on the other pipelines (for reference, not the gate)",
                "",
                f"| pipeline | embedder | best single chunking | routing headroom | {cfg.confidence:.0%} CI | meets the bar |",
                "|---|---|---|---|---|---|",
            ]
            lines += [
                f"| {g.pipeline} | {g.embedder} | {g.best} | {_signed(g.headroom)} | {_ci(g.interval)} | {_yes(g.clears)} |"
                for g in reference
            ]
            lines.append("")

    note = _CI_NOTE.format(resamples=cfg.resamples, seed=cfg.seed, confidence=cfg.confidence, budget=cfg.primary_budget)
    headroom = _series(results, cfg, lambda r: r.analysis.headroom)
    lines += [
        "## Routing headroom",
        "",
        (
            "Best single chunking: highest mean retrieval recall at the budget. Oracle router: per question, the "
            "chunking with the highest recall (ties to the smaller chunk). Routing headroom: oracle router minus best "
            "single chunking; the best single chunking is re-selected inside every resample."
        ),
        "",
        (
            "| dataset | pipeline | embedder | view | budget | best single chunking | best single recall "
            "| oracle router recall | routing headroom | CI | CI level | CI excludes 0 |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(results):
        a = r.analysis
        interval = headroom[(i, r.budget)]
        lines.append(
            f"{_prefix(r)} {r.candidates[a.best]} | {_fmt(a.means[a.best])} | {_fmt(a.oracle)} | "
            f"{_signed(a.headroom.point)} | {_ci(interval)} | {_level(interval)} | {_yes(interval.excludes_zero)} |"
        )
    lines += ["", note, ""]

    gain = _series(results, cfg, lambda r: r.analysis.type_headroom)
    gap = _series(results, cfg, lambda r: r.analysis.oracle_gap)
    types = [PRECISE, CONTEXT, MIXED]
    lines += [
        "## Query-type oracle (secondary; does not change the gate)",
        "",
        (
            "The best chunking per labelled query type, applied to every question of that type. Query types come "
            "from the labels in hindsight, so no real router has them."
        ),
        "",
        "| dataset | pipeline | embedder | view | budget | "
        + " | ".join(f"{t} pick" for t in types)
        + " | query-type oracle recall | gain over best single | CI | CI level "
        "| oracle router minus query-type oracle | CI | CI level |",
        "|---|---|---|---|---|" + "---|" * (len(types) + 7),
    ]
    for i, r in enumerate(results):
        a = r.analysis
        picks = [r.candidates[a.type_best[t]] if t in a.type_best else NA for t in types]
        g, o = gain[(i, r.budget)], gap[(i, r.budget)]
        lines.append(
            f"{_prefix(r)} " + " | ".join(picks) + f" | {_fmt(a.type_oracle)} | {_signed(a.type_headroom.point)} | "
            f"{_ci(g)} | {_level(g)} | {_signed(a.oracle_gap.point)} | {_ci(o)} | {_level(o)} |"
        )
    lines += ["", note, ""]

    lines += [
        "## Each chunking against the best single chunking",
        "",
        (
            "Difference: the chunking's mean recall minus the best single chunking's, with the best re-selected "
            "inside every resample (so the best chunking's own difference is 0 with a CI at or below 0). Best in "
            "resamples: the share of resamples in which the chunking was the best single chunking."
        ),
        "",
        (
            "| dataset | pipeline | embedder | view | budget | chunking | mean recall | difference from best | CI "
            "| CI level | CI excludes 0 | best in resamples |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    by_chunking = {
        name: _series(
            results,
            cfg,
            lambda r, name=name: r.analysis.differences[r.candidates.index(name)] if name in r.candidates else None,
        )
        for name in cfg.chunkings
    }
    for i, r in enumerate(results):
        a = r.analysis
        for c, name in enumerate(r.candidates):
            interval = by_chunking[name][(i, r.budget)]
            lines.append(
                f"{_prefix(r)} {name} | {_fmt(a.means[c])} | {_signed(a.differences[c].point)} | {_ci(interval)} | "
                f"{_level(interval)} | {_yes(interval.excludes_zero)} | {_fmt(a.best_share[c])} |"
            )
    lines += ["", note, ""]
    return "\n".join(lines)


def _r8(cfg: HeadroomConfig, results: list[CellResult], header: list[str]) -> str:
    ref = cfg.interaction_reference
    lines = list(header)
    lines += [
        f"## Chunk size x query type interaction against {ref}",
        "",
        (
            f"For each chunking: Δ context = mean recall (chunking − {ref}) on context questions, Δ precise = the "
            f"same on precise questions, and interaction = Δ context − Δ precise. A positive interaction means the "
            f"chunking does relatively better than {ref} on context questions than on precise ones. Mixed questions "
            "are left out."
        ),
        "",
        (
            "| dataset | pipeline | embedder | view | budget | chunking | precise n | context n | Δ context "
            "| Δ precise | interaction | CI | CI level | CI excludes 0 |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    def interaction_of(r: CellResult, name: str) -> Interaction | None:
        return r.analysis.interactions.get(r.candidates.index(name)) if name in r.candidates else None

    series = {
        name: _series(
            results,
            cfg,
            lambda r, name=name: i.interaction if (i := interaction_of(r, name)) is not None else None,
        )
        for name in cfg.chunkings
        if name != ref
    }
    for i, r in enumerate(results):
        for name in r.candidates:
            interaction = interaction_of(r, name)
            if interaction is None:
                continue
            interval = series[name][(i, r.budget)]
            lines.append(
                f"{_prefix(r)} {name} | {r.type_counts[PRECISE]} | {r.type_counts[CONTEXT]} | "
                f"{_signed(interaction.delta_context.point)} | {_signed(interaction.delta_precise.point)} | "
                f"{_signed(interaction.interaction.point)} | {_ci(interval)} | {_level(interval)} | "
                f"{_yes(interval.excludes_zero)} |"
            )
    lines += [
        "",
        _CI_NOTE.format(resamples=cfg.resamples, seed=cfg.seed, confidence=cfg.confidence, budget=cfg.primary_budget),
        f"Budgets where {ref} is not scored (its chunk is bigger than the budget) have no interaction rows.",
        "",
    ]
    return "\n".join(lines)


def _share(n: int, total: int) -> str:
    return f"{n / total:.4f} ({n})" if total else NA


def _counts_by_type(r: CellResult, mask: np.ndarray) -> list[int]:
    """Questions under mask per query type, then in total."""
    return [int((mask & (r.qtype == i)).sum()) for i in range(len(QUERY_TYPES))] + [int(mask.sum())]


def _pick_rows(r: CellResult, among: np.ndarray, label_tied: bool) -> list[str]:
    a = r.analysis
    totals = _counts_by_type(r, among)
    rows = []
    for c, name in enumerate(r.candidates):
        n = _counts_by_type(r, among & (a.picks == c))
        rows.append(f"{_prefix(r)} {name} | " + " | ".join(_share(x, t) for x, t in zip(n, totals, strict=True)) + " |")
    if label_tied:
        n = _counts_by_type(r, among & a.all_tied)
        rows.append(
            f"{_prefix(r)} every chunking tied | "
            + " | ".join(_share(x, t) for x, t in zip(n, totals, strict=True))
            + " |"
        )
    return rows


def _r9(cfg: HeadroomConfig, results: list[CellResult], header: list[str]) -> str:
    at_primary = [r for r in results if r.budget == cfg.primary_budget]
    columns = "| dataset | pipeline | embedder | view | budget | chunking | " + " | ".join(QUERY_TYPES) + " | all |"
    rule = "|---|---|---|---|---|---|" + "---|" * (len(QUERY_TYPES) + 1)
    lines = list(header)
    lines += [
        f"## The oracle router's chunking per query type, at {cfg.primary_budget} tokens",
        "",
        (
            "Each cell: the share of the query type's questions for which the oracle router picks the chunking, and "
            "their count. Ties go to the smaller chunk, so a question on which every chunking scores the same goes "
            "to the smallest candidate; the last row of each block counts those questions."
        ),
        "",
        columns,
        rule,
    ]
    for r in at_primary:
        lines += _pick_rows(r, np.ones(r.n_questions, dtype=bool), label_tied=True)
    lines += [
        "",
        "## The same, among the questions where the chunkings differ",
        "",
        "Leaves out the questions on which every chunking scores the same, so the tie-break does not decide the picks.",
        "",
        columns,
        rule,
    ]
    for r in at_primary:
        lines += _pick_rows(r, ~r.analysis.all_tied, label_tied=False)
    lines.append("")
    return "\n".join(lines)


# --- entry point -----------------------------------------------------------


@dataclass(frozen=True)
class HeadroomOutcome:
    config_hash: str
    results: tuple[CellResult, ...]
    verdict: tuple[str, ...]
    tables: tuple[Path, ...]


def run_headroom(cfg: HeadroomConfig, paths: Paths) -> HeadroomOutcome:
    started = time.monotonic()
    cfg_hash = headroom_config_hash(cfg)
    loaded = load_results(cfg, paths)
    results = analyse(cfg, loaded)
    if not results:
        raise ValueError("no cell has a scored chunking")
    tables = write_headroom_tables(cfg, cfg_hash, loaded, results, paths.results)
    verdict = (
        gate_verdict(cfg, results)
        if cfg.gated
        else (
            (
                f"No gate block configured: the {cfg.view} view results report the best single chunking, the oracle "
                "router and the routing headroom without a gate verdict."
            ),
        )
    )
    print(f"headroom {cfg.run_name}: {len(results)} cells, {cfg.resamples} resamples, seed {cfg.seed}")
    for line in verdict:
        print(f"  {line}")
    for path in tables:
        print(f"  result table: {path}")
    print(f"  {time.monotonic() - started:.1f} s")
    return HeadroomOutcome(config_hash=cfg_hash, results=tuple(results), verdict=tuple(verdict), tables=tables)


def write_headroom_tables(
    cfg: HeadroomConfig, cfg_hash: str, loaded: Results, results: list[CellResult], results_dir: Path
) -> tuple[Path, ...]:
    out_dir = results_dir / "routing"
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "r7": _r7(cfg, results, _header("# R7 - routing headroom and the router gate", cfg, cfg_hash, loaded)),
        "r8": _r8(cfg, results, _header("# R8 - chunk size x query type interaction", cfg, cfg_hash, loaded)),
        "r9": _r9(cfg, results, _header("# R9 - the oracle router's chunking by query type", cfg, cfg_hash, loaded)),
    }
    paths: list[Path] = []
    for name, text in tables.items():
        path = out_dir / f"{name}-{cfg.run_name}.md"
        path.write_text(text, encoding="utf-8")
        paths.append(path)
    return tuple(paths)
