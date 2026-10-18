"""`rag verdict <config>`: the verdict of ADR 0008, computed mechanically
from the v2 runs, as table R16 (results/v2/r16-verdict.md). No retrieval
runs here: the per-question results are read and joined by (dataset,
question id).

Every contender is paired with its section-aware reference: the
section-aware rows of the run behind the contender's own committed table
(R11 reads the baseline runs; R12, R13 and R17 their own runs), so each
contender's numbers agree with that table. The bar's cell is the budget
view at 1024 tokens, with the configured pipeline, embedder and search
scope. Intervals come from the paired, document-clustered bootstrap: each
dataset's documents are its clusters, drawn from the same stream whether
the dataset is analysed alone or pooled (as in R7 and R17).

The bar, read as the ADR 0008 amendments record it: a contender passes
when its pooled recall gain over section-aware is at least `min_gain`
with a `confidence` interval excluding 0, no dataset alone is below
section-aware by more than `max_loss` (point estimates), and, where its
answer score was measured, it is not below section-aware's by more than
`max_loss` (point estimate). The tie-break: among the contenders that
pass, the highest pooled recall wins unless a simpler one (earlier in the
config's order) is within `tie` of it; section-aware stays if none
passes.

Secondary results decide nothing: the other budgets (Holm-adjusted, as in
v1), the production view, side variants, the depth-50 side run and the
reader stage's answer scores. The adoption profile reads the latency
probe's committed output (`rag latency`) and the index-time manifests, so
the same runs and the same seed regenerate R16 byte-identically.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq
import yaml

from .answers import analyse_answers, read_answers
from .bootstrap import Estimate, Interval, analyse_cell, clustered_mean, percentile_interval, resample_counts
from .config import PRODUCTION_LINE
from .paths import Paths
from .query_type import QUERY_TYPES
from .routing import series_intervals

REFERENCE = "section-aware"
_TIE_TOLERANCE = 1e-9  # "within 0.01" includes the boundary despite float rounding

Key = tuple[str, str]  # (dataset, question id)
Cell = tuple[str, int]  # (view, budget)


# --- config ----------------------------------------------------------------


@dataclass(frozen=True)
class ContenderSpec:
    name: str
    table: str  # the contender's own committed table, such as r12
    run: str  # its run under runs/<dataset>/
    reference_run: str  # the run whose section-aware rows are its reference
    system: str  # its name in the run's rows: a chunking, or a router's pipeline
    routed: bool = False  # a router: rows in routed.parquet under pipeline `system`

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "table": self.table, "run": self.run}
        if self.system != self.name:
            out["system"] = self.system
        if self.reference_run != self.run:
            out["reference_run"] = self.reference_run
        return out | ({"routed": True} if self.routed else {})


@dataclass(frozen=True)
class VerdictConfig:
    run_name: str
    datasets: tuple[str, ...]
    contenders: tuple[ContenderSpec, ...]  # tie-break order, simplest first
    side_variants: tuple[ContenderSpec, ...]  # judged the same way, never deciding
    oracle_run: str  # the baseline runs of R7
    oracle_chunkings: tuple[str, ...]  # smallest chunk first: the oracle router's tie order
    answers_run: str
    answer_setups: tuple[str, ...]
    depth_runs: tuple[str, str]  # (the contender's run at rerank depth 30, the depth-50 run)
    depth_contender: str
    latency: str  # the latency probe's output, relative to the root
    prefixes_manifest: str
    pipeline: str = PRODUCTION_LINE
    embedder: str = "nomic"
    scope: str = "collection"
    budget: int = 1024
    budget_top_n: int = 20
    top_n: int = 8
    secondary_budgets: tuple[int, ...] = (512, 2048)
    min_gain: float = 0.02
    max_loss: float = 0.01
    tie: float = 0.01
    confidence: float = 0.95
    resamples: int = 10000
    seed: int = 0
    notes: tuple[str, ...] = ()  # printed under the verdict

    def as_dict(self) -> dict[str, Any]:
        out = {
            "kind": "verdict",
            "run_name": self.run_name,
            "datasets": list(self.datasets),
            "pipeline": self.pipeline,
            "embedder": self.embedder,
            "scope": self.scope,
            "budget": self.budget,
            "budget_top_n": self.budget_top_n,
            "top_n": self.top_n,
            "secondary_budgets": list(self.secondary_budgets),
            "bar": {
                "min_gain": self.min_gain,
                "max_loss": self.max_loss,
                "tie": self.tie,
                "confidence": self.confidence,
                "resamples": self.resamples,
                "seed": self.seed,
            },
            "contenders": [c.as_dict() for c in self.contenders],
            "side_variants": [c.as_dict() for c in self.side_variants],
            "oracle": {"run": self.oracle_run, "chunkings": list(self.oracle_chunkings)},
            "answers": {"run": self.answers_run, "setups": list(self.answer_setups)},
            "depth50": {"runs": list(self.depth_runs), "contender": self.depth_contender},
            "latency": self.latency,
            "prefixes_manifest": self.prefixes_manifest,
        }
        return out | ({"notes": list(self.notes)} if self.notes else {})


def _parse_contender(raw: dict[str, Any]) -> ContenderSpec:
    run = str(raw["run"])
    return ContenderSpec(
        name=str(raw["name"]),
        table=str(raw["table"]),
        run=run,
        reference_run=str(raw.get("reference_run", run)),
        system=str(raw.get("system", raw["name"])),
        routed=bool(raw.get("routed", False)),
    )


def parse_verdict_config(raw: dict[str, Any]) -> VerdictConfig:
    try:
        if raw.get("kind") != "verdict":
            raise ValueError("a verdict config needs `kind: verdict`")
        bar = raw.get("bar", {})
        cfg = VerdictConfig(
            run_name=str(raw["run_name"]),
            datasets=tuple(str(d) for d in raw["datasets"]),
            contenders=tuple(_parse_contender(c) for c in raw["contenders"]),
            side_variants=tuple(_parse_contender(c) for c in raw.get("side_variants", ())),
            oracle_run=str(raw["oracle"]["run"]),
            oracle_chunkings=tuple(str(c) for c in raw["oracle"]["chunkings"]),
            answers_run=str(raw["answers"]["run"]),
            answer_setups=tuple(str(s) for s in raw["answers"]["setups"]),
            depth_runs=tuple(str(r) for r in raw["depth50"]["runs"]),  # type: ignore[arg-type]
            depth_contender=str(raw["depth50"]["contender"]),
            latency=str(raw["latency"]),
            prefixes_manifest=str(raw["prefixes_manifest"]),
            pipeline=str(raw.get("pipeline", PRODUCTION_LINE)),
            embedder=str(raw.get("embedder", "nomic")),
            scope=str(raw.get("scope", "collection")),
            budget=int(raw.get("budget", 1024)),
            budget_top_n=int(raw.get("budget_top_n", 20)),
            top_n=int(raw.get("top_n", 8)),
            secondary_budgets=tuple(int(b) for b in raw.get("secondary_budgets", (512, 2048))),
            min_gain=float(bar.get("min_gain", 0.02)),
            max_loss=float(bar.get("max_loss", 0.01)),
            tie=float(bar.get("tie", 0.01)),
            confidence=float(bar.get("confidence", 0.95)),
            resamples=int(bar.get("resamples", 10000)),
            seed=int(bar.get("seed", 0)),
            notes=tuple(str(note) for note in raw.get("notes", ())),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid verdict config: {exc}") from exc
    names = [c.name for c in (*cfg.contenders, *cfg.side_variants)]
    if not cfg.contenders or len(set(names)) != len(names) or REFERENCE in names:
        raise ValueError("contenders must be a non-empty list of distinct names other than section-aware")
    if not cfg.datasets or len(set(cfg.datasets)) != len(cfg.datasets):
        raise ValueError("datasets must be a non-empty list of distinct names")
    if REFERENCE not in cfg.oracle_chunkings or REFERENCE not in cfg.answer_setups:
        raise ValueError("section-aware must be one of the oracle chunkings and the answer setups")
    if len(cfg.depth_runs) != 2 or cfg.depth_contender not in names:
        raise ValueError("depth50 needs two runs (depth 30, depth 50) and one of the contenders")
    if cfg.budget in cfg.secondary_budgets or cfg.min_gain <= 0 or cfg.max_loss < 0 or cfg.tie < 0:
        raise ValueError("the secondary budgets exclude the bar's budget; min_gain > 0, max_loss and tie >= 0")
    if not 0 < cfg.confidence < 1 or cfg.resamples <= 0:
        raise ValueError("confidence must be between 0 and 1 and resamples positive")
    return cfg


def load_verdict_config(path: Path) -> VerdictConfig:
    return parse_verdict_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def verdict_config_hash(cfg: VerdictConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --- the bar and the tie-break (dataset-agnostic) ----------------------------


@dataclass(frozen=True)
class Bar:
    min_gain: float = 0.02
    max_loss: float = 0.01
    tie: float = 0.01


@dataclass(frozen=True)
class Evidence:
    """One contender against section-aware at the bar's cell."""

    name: str
    pooled: float  # pooled recall difference
    interval: Interval  # its bootstrap interval
    per_dataset: dict[str, float]  # each dataset's recall difference
    answer: float | None = None  # answer-score difference; None: not measured


@dataclass(frozen=True)
class Judgement:
    evidence: Evidence
    gain: bool  # pooled gain at least min_gain, with the interval excluding 0
    datasets: bool  # no dataset alone below -max_loss
    answers: bool | None  # None: the answer score was not measured
    reasons: tuple[str, ...]  # why it fails, in words

    @property
    def passed(self) -> bool:
        return self.gain and self.datasets and self.answers is not False


def judge(evidence: Evidence, bar: Bar) -> Judgement:
    reasons = []
    if evidence.pooled < bar.min_gain:
        reasons.append(f"its pooled gain is below +{bar.min_gain:.4f}")
    if not evidence.interval.excludes_zero:
        reasons.append("its CI includes 0")
    worse = sorted(ds for ds, d in evidence.per_dataset.items() if d < -bar.max_loss)
    if worse:
        reasons.append(f"{' and '.join(worse)} alone {'is' if len(worse) == 1 else 'are'} below -{bar.max_loss:.4f}")
    answers = None if evidence.answer is None else evidence.answer >= -bar.max_loss
    if answers is False:
        reasons.append(f"its answer score is below section-aware's by more than {bar.max_loss:.4f}")
    return Judgement(
        evidence=evidence,
        gain=evidence.pooled >= bar.min_gain and evidence.interval.excludes_zero,
        datasets=not worse,
        answers=answers,
        reasons=tuple(reasons),
    )


def tie_break(judgements: Sequence[Judgement], tie: float) -> Judgement | None:
    """The winner among `judgements` (simplest first): the highest pooled
    recall among those that pass, unless a simpler one is within `tie` of
    it; None when none passes (section-aware stays)."""
    passed = [j for j in judgements if j.passed]
    if not passed:
        return None
    best = max(j.evidence.pooled for j in passed)
    return next(j for j in passed if best - j.evidence.pooled <= tie + _TIE_TOLERANCE)


def tie_break_words(judgement: Judgement, judgements: Sequence[Judgement], winner: Judgement | None) -> str:
    if not judgement.passed:
        return "does not enter"
    passed = [j for j in judgements if j.passed]
    best = max(passed, key=lambda j: j.evidence.pooled)
    if judgement is winner:
        if len(passed) == 1:
            return "wins: the only contender that passes"
        if judgement is best:
            return "wins: the highest pooled recall, no simpler contender within the tie margin"
        return f"wins: simpler than {best.evidence.name} and within the tie margin of it"
    assert winner is not None
    return f"loses to {winner.evidence.name}"


def verdict_sentence(judgement: Judgement, winner: Judgement | None) -> str:
    name = judgement.evidence.name
    if judgement is winner:
        return f"{name} clears the bar and replaces section-aware."
    if judgement.passed:
        return f"{name} clears the bar but loses the tie-break; section-aware is replaced by {winner.evidence.name}."
    return f"{name} does not clear the bar ({'; '.join(judgement.reasons)})."


# --- the paired, document-clustered bootstrap ----------------------------------


@dataclass(frozen=True)
class Difference:
    pooled: Estimate
    per_dataset: dict[str, Estimate]


def paired_difference(
    a: dict[Key, float],
    b: dict[Key, float],
    docs: dict[Key, str],
    datasets: Sequence[str],
    resamples: int,
    seed: int,
) -> Difference:
    """mean(a - b) per dataset and pooled over `datasets` (in that order),
    each dataset's documents its clusters, drawn per (seed, dataset)."""
    if a.keys() != b.keys():
        raise ValueError("the two systems cover different questions")
    per_dataset: dict[str, Estimate] = {}
    values, clusters, draws = [], [], []
    offset = 0
    for dataset in datasets:
        keys = sorted(k for k in a if k[0] == dataset)
        if not keys:
            raise ValueError(f"no questions of {dataset}")
        diffs = np.array([a[k] - b[k] for k in keys])
        names = sorted({docs[k] for k in keys})
        index = {name: i for i, name in enumerate(names)}
        cluster = np.array([index[docs[k]] for k in keys])
        counts = resample_counts(len(names), resamples, seed, dataset)
        per_dataset[dataset] = clustered_mean(diffs, cluster, counts)
        values.append(diffs)
        clusters.append(cluster + offset)
        draws.append(counts)
        offset += len(names)
    pooled = clustered_mean(np.concatenate(values), np.concatenate(clusters), np.hstack(draws))
    return Difference(pooled=pooled, per_dataset=per_dataset)


# --- loading the runs ------------------------------------------------------


@dataclass
class Rows:
    """One system's per-question recall per cell, each question's document
    and query type, and whether packing reached past the reranked head."""

    recall: dict[Cell, dict[Key, float]]
    used_tail: dict[Cell, dict[Key, bool]]
    docs: dict[Key, str]
    qtypes: dict[Key, str]


def _load(
    cfg: VerdictConfig, paths: Paths, run: str, system: str, routed: bool, cells: Sequence[Cell]
) -> tuple[Rows, dict[str, str]]:
    """A system's rows at `cells` from `run` on every dataset, and each
    run directory's config hash."""
    caps = {"budget": cfg.budget_top_n, "production": cfg.top_n}
    file, filters = (
        ("routed.parquet", [("pipeline", "=", system)])
        if routed
        else ("results.parquet", [("pipeline", "=", cfg.pipeline), ("chunking", "=", system)])
    )
    rows = Rows(recall={c: {} for c in cells}, used_tail={c: {} for c in cells}, docs={}, qtypes={})
    hashes: dict[str, str] = {}
    for dataset in cfg.datasets:
        run_dir = paths.run_dir(run, dataset)
        hashes[f"{dataset}/{run}"] = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["config_hash"]
        table = pq.read_table(
            run_dir / file,
            columns=["question_id", "doc_id", "query_type", "view", "top_n", "budget", "scored", "recall", "used_tail"],
            filters=[("embedder", "=", cfg.embedder), ("scope", "=", cfg.scope), *filters],
        ).to_pydict()
        for qid, doc, qtype, view, top_n, budget, scored, recall, tail in zip(*table.values(), strict=True):
            cell = (view, budget)
            if cell not in rows.recall or top_n != caps[view]:
                continue
            key = (dataset, qid)
            if not scored:
                raise ValueError(f"{dataset}/{run}: {system} is not scored for {qid} at {budget} tokens, {view} view")
            rows.recall[cell][key] = recall
            rows.used_tail[cell][key] = bool(tail)
            rows.docs[key] = doc
            rows.qtypes[key] = qtype
        for cell in cells:
            if not any(k[0] == dataset for k in rows.recall[cell]):
                raise ValueError(f"{dataset}/{run} has no {system} rows at {cell[1]} tokens in the {cell[0]} view")
    return rows, hashes


# --- the analysis ----------------------------------------------------------


@dataclass(frozen=True)
class OracleCheck:
    """R7's numbers at the bar's cell, recomputed: per group (pooled first),
    the best single chunking, section-aware's and the oracle router's
    recall, and the routing headroom with its interval."""

    rows: tuple[tuple[str, str, float, float, Estimate, Interval], ...]
    oracle_minus_reference: Estimate  # pooled, paired


@dataclass(frozen=True)
class ContenderResult:
    spec: ContenderSpec
    primary: Difference
    interval: Interval
    judgement: Judgement
    share: float  # of the oracle ceiling captured
    secondary: dict[int, tuple[Estimate, Interval]]  # budget -> pooled difference, Holm-adjusted interval
    production: tuple[Difference, Interval]
    reference_mismatch: dict[Cell, int]  # cells where its reference differs from the baseline's section-aware


def _oracle(cfg: VerdictConfig, paths: Paths, primary: Cell) -> OracleCheck:
    loaded = [_load(cfg, paths, cfg.oracle_run, c, False, [primary]) for c in cfg.oracle_chunkings]
    keys = sorted(loaded[0][0].recall[primary])
    recall = np.array([[rows.recall[primary][k] for rows, _ in loaded] for k in keys])
    reference = loaded[cfg.oracle_chunkings.index(REFERENCE)][0]
    docs, qtypes = reference.docs, reference.qtypes
    datasets = sorted(cfg.datasets)  # R7's group order
    out = []
    for group, members in [("pooled", datasets), *((d, [d]) for d in datasets)]:
        rows = [i for i, k in enumerate(keys) if k[0] in members]
        clusters, counts, offset = np.zeros(len(rows), dtype=int), [], 0
        for dataset in members:
            names = sorted({docs[keys[i]] for i in rows if keys[i][0] == dataset})
            index = {name: j for j, name in enumerate(names)}
            for pos, i in enumerate(rows):
                if keys[i][0] == dataset:
                    clusters[pos] = index[docs[keys[i]]] + offset
            counts.append(resample_counts(len(names), cfg.resamples, cfg.seed, dataset))
            offset += len(names)
        qtype = np.array([QUERY_TYPES.index(qtypes[keys[i]]) for i in rows])
        cell = analyse_cell(recall[rows], clusters, qtype, np.hstack(counts))
        out.append(
            (
                group,
                cfg.oracle_chunkings[cell.best],
                float(cell.means[cfg.oracle_chunkings.index(REFERENCE)]),
                cell.oracle,
                cell.headroom,
                percentile_interval(cell.headroom.samples, cfg.confidence),
            )
        )
    oracle = {k: float(v) for k, v in zip(keys, recall.max(axis=1), strict=True)}
    gap = paired_difference(oracle, reference.recall[primary], docs, cfg.datasets, cfg.resamples, cfg.seed)
    return OracleCheck(rows=tuple(out), oracle_minus_reference=gap.pooled)


def _analyse_contender(
    cfg: VerdictConfig,
    paths: Paths,
    spec: ContenderSpec,
    baseline: Rows,
    headroom: float,
    hashes: dict[str, str],
) -> ContenderResult:
    primary: Cell = ("budget", cfg.budget)
    cells = [primary, *(("budget", b) for b in cfg.secondary_budgets), ("production", cfg.budget)]
    rows, run_hashes = _load(cfg, paths, spec.run, spec.system, spec.routed, cells)
    reference, ref_hashes = _load(cfg, paths, spec.reference_run, REFERENCE, False, cells)
    hashes.update(run_hashes | ref_hashes)
    diffs = {
        cell: paired_difference(
            rows.recall[cell], reference.recall[cell], rows.docs, cfg.datasets, cfg.resamples, cfg.seed
        )
        for cell in cells
    }
    main = diffs[primary]
    interval = percentile_interval(main.pooled.samples, cfg.confidence)
    evidence = Evidence(
        name=spec.name,
        pooled=main.pooled.point,
        interval=interval,
        per_dataset={d: e.point for d, e in main.per_dataset.items()},
        answer=None,  # no contender's answers are read (ADR 0008 and 0009 amendments)
    )
    bar = Bar(min_gain=cfg.min_gain, max_loss=cfg.max_loss, tie=cfg.tie)
    series = {cfg.budget: main.pooled} | {b: diffs[("budget", b)].pooled for b in cfg.secondary_budgets}
    intervals = series_intervals(series, cfg.budget, cfg.confidence)
    production = diffs[("production", cfg.budget)]
    mismatch = {
        cell: sum(1 for k, v in reference.recall[cell].items() if baseline.recall.get(cell, {}).get(k, v) != v)
        for cell in cells
    }
    return ContenderResult(
        spec=spec,
        primary=main,
        interval=interval,
        judgement=judge(evidence, bar),
        share=main.pooled.point / headroom,
        secondary={b: (series[b], intervals[b]) for b in cfg.secondary_budgets},
        production=(production, percentile_interval(production.pooled.samples, cfg.confidence)),
        reference_mismatch={c: n for c, n in mismatch.items() if n},
    )


# --- rendering -------------------------------------------------------------


def _f(value: float) -> str:
    return f"{value:.4f}"


def _s(value: float) -> str:
    return f"{value:+.4f}"


def _ci(interval: Interval) -> str:
    return f"[{_s(interval.low)}, {_s(interval.high)}]"


def _yes(flag: bool | None) -> str:
    return {True: "pass", False: "fail", None: "not measured"}[flag]


def _datasets(diff: Difference) -> str:
    return ", ".join(f"{d} {_s(e.point)}" for d, e in diff.per_dataset.items())


@dataclass(frozen=True)
class DepthResult:
    """The depth-50 side run: each system's recall at rerank depth 30 and
    50, the contender's margin at each depth, and how often section-aware's
    packed list reaches past the reranked head."""

    means: dict[tuple[str, int], float]  # (system, depth) -> pooled mean recall
    margins: dict[int, tuple[Difference, Interval]]  # depth -> contender minus section-aware
    shifts: dict[str, tuple[Difference, Interval]]  # system -> depth 50 minus depth 30
    tail_share: dict[int, float]  # depth -> share of questions where section-aware used the tail
    judgements: dict[int, Judgement]  # depth -> the bar's retrieval checks on the margin


def _depth(cfg: VerdictConfig, paths: Paths, cell: Cell, hashes: dict[str, str]) -> DepthResult:
    systems = (REFERENCE, cfg.depth_contender)
    loaded: dict[tuple[str, int], Rows] = {}
    for depth, run in zip((30, 50), cfg.depth_runs, strict=True):
        for system in systems:
            loaded[(system, depth)], run_hashes = _load(cfg, paths, run, system, False, [cell])
            hashes.update(run_hashes)
    docs = loaded[(REFERENCE, 30)].docs

    def diff(a: Rows, b: Rows) -> tuple[Difference, Interval]:
        d = paired_difference(a.recall[cell], b.recall[cell], docs, cfg.datasets, cfg.resamples, cfg.seed)
        return d, percentile_interval(d.pooled.samples, cfg.confidence)

    bar = Bar(min_gain=cfg.min_gain, max_loss=cfg.max_loss, tie=cfg.tie)
    margins = {depth: diff(loaded[(cfg.depth_contender, depth)], loaded[(REFERENCE, depth)]) for depth in (30, 50)}
    return DepthResult(
        means={k: float(np.mean(list(rows.recall[cell].values()))) for k, rows in loaded.items()},
        margins=margins,
        shifts={s: diff(loaded[(s, 50)], loaded[(s, 30)]) for s in systems},
        tail_share={
            depth: float(np.mean(list(loaded[(REFERENCE, depth)].used_tail[cell].values()))) for depth in (30, 50)
        },
        judgements={
            depth: judge(
                Evidence(
                    name=cfg.depth_contender,
                    pooled=d.pooled.point,
                    interval=interval,
                    per_dataset={ds: e.point for ds, e in d.per_dataset.items()},
                ),
                bar,
            )
            for depth, (d, interval) in margins.items()
        },
    )


def _index_costs(cfg: VerdictConfig, paths: Paths) -> dict[str, Any]:
    """Index-time work from the run manifests and the prefix manifest."""

    def manifest(run: str, dataset: str) -> dict[str, Any]:
        return json.loads((paths.run_dir(run, dataset) / "manifest.json").read_text(encoding="utf-8"))

    runs = {spec.name: spec.run for spec in (*cfg.contenders, *cfg.side_variants)}
    out: dict[str, Any] = {"chunks": {}, "late_windows": {}}
    for dataset in cfg.datasets:
        counts = manifest(cfg.oracle_run, dataset)["counts"]["chunks"]
        out["chunks"][dataset] = {name: counts[name] for name in cfg.oracle_chunkings}
        late = [name for name, run in runs.items() if "late_windows" in manifest(run, dataset)]
        if late:
            windows = manifest(runs[late[0]], dataset)["late_windows"][cfg.embedder]
            out["late_windows"][dataset] = {"windows": windows["windows"], "documents": windows["documents"]}
    prefixes = json.loads((paths.root / cfg.prefixes_manifest).read_text(encoding="utf-8"))
    out["prefixes"] = {
        "model": f"{prefixes['model']['id']}@{prefixes['model']['revision'][:12]}",
        "chunks": prefixes["chunks"],
        "wall_hours": prefixes["wall_hours"],
        "per_dataset": {d: prefixes["datasets"][d]["wall_hours"] for d in cfg.datasets},
    }
    return out


def _verdict_lines(cfg: VerdictConfig, results: Sequence[ContenderResult], winner: Judgement | None) -> list[str]:
    order = ", ".join(r.spec.name for r in results)
    headline = (
        f"**Verdict: {winner.evidence.name} replaces section-aware.**"
        if winner is not None
        else "**Verdict: section-aware stays: no contender clears the bar.**"
    )
    return [
        "## Verdict",
        "",
        headline,
        "",
        (
            f"Judged on the {cfg.pipeline} pipeline with {cfg.embedder}, {cfg.scope} search, budget view (top-N cap "
            f"{cfg.budget_top_n}) at {cfg.budget} tokens, pooled over {' and '.join(cfg.datasets)}, with a "
            f"{cfg.confidence:.0%} CI from the paired, document-clustered bootstrap ({cfg.resamples} resamples, seed "
            f"{cfg.seed})."
        ),
        "",
        "The bar (ADR 0008, read as its amendments record):",
        "",
        f"1. Gain: pooled retrieval recall at least +{cfg.min_gain:.4f} over section-aware, with the CI excluding 0.",
        (
            f"2. Datasets: on each dataset alone, recall no worse than section-aware's by more than {cfg.max_loss:.4f} "
            "(point estimate, the CI reported beside it)."
        ),
        (
            f"3. Answers: an answer score no worse than section-aware's by more than {cfg.max_loss:.4f} (point estimate), "
            "where the contender's answers were measured."
        ),
        "",
        (
            f"Tie-break: among the contenders that pass, the highest pooled recall wins unless a simpler one is "
            f"within {cfg.tie:.4f} of it (point estimates). Simplest first: {order}. Section-aware stays if none passes."
        ),
        *(line for note in cfg.notes for line in ("", note)),
        "",
    ]


def _contender_table(cfg: VerdictConfig, results: Sequence[ContenderResult], winner: Judgement | None) -> list[str]:
    judgements = [r.judgement for r in results]
    head = " | ".join(f"{d} difference" for d in cfg.datasets)
    lines = [
        "## Contenders against section-aware",
        "",
        (
            f"Recall differences from section-aware at the bar's cell. Share of the oracle ceiling captured: (contender "
            f"- section-aware) / (oracle router - section-aware), point estimates, the oracle router from {cfg.oracle_run}."
        ),
        "",
        (
            f"| contender | own table | pooled difference | CI | {head} | gain | datasets | answers | "
            "share of oracle captured | tie-break | verdict |"
        ),
        "|---|---|---|---|" + "---|" * len(cfg.datasets) + "---|---|---|---|---|---|",
    ]
    for r in results:
        j = r.judgement
        per_dataset = " | ".join(_s(r.primary.per_dataset[d].point) for d in cfg.datasets)
        lines.append(
            f"| {r.spec.name} | {r.spec.table.upper()} | {_s(r.primary.pooled.point)} | {_ci(r.interval)} | "
            f"{per_dataset} | {_yes(j.gain)} | {_yes(j.datasets)} | {_yes(j.answers)} | {r.share:.1%} | "
            f"{tie_break_words(j, judgements, winner)} | {verdict_sentence(j, winner)} |"
        )
    lines += ["", "Per-dataset intervals (the datasets check reads the point estimates):", ""]
    lines += [
        f"- {r.spec.name}: "
        + ", ".join(
            f"{d} {_s(e.point)} {_ci(percentile_interval(e.samples, cfg.confidence))}"
            for d, e in r.primary.per_dataset.items()
        )
        for r in results
    ]
    return [*lines, ""]


def _references(cfg: VerdictConfig, results: Sequence[ContenderResult]) -> list[str]:
    lines = [
        "## Section-aware references",
        "",
        (
            "Each contender is paired with the section-aware rows of the run behind its own table, so its numbers "
            "agree with that table."
        ),
        "",
        (
            "| contender | own table | contender run | section-aware reference run | "
            f"differs from {cfg.oracle_run} (R7) |"
        ),
        "|---|---|---|---|---|",
    ]
    for r in results:
        mismatch = (
            "; ".join(f"{n} questions at {b} tokens, {v} view" for (v, b), n in sorted(r.reference_mismatch.items()))
            or "no question at any cell read here"
        )
        lines.append(f"| {r.spec.name} | {r.spec.table.upper()} | {r.spec.run} | {r.spec.reference_run} | {mismatch} |")
    return [*lines, ""]


def _oracle_lines(oracle: OracleCheck) -> list[str]:
    lines = [
        "## R7 reproduced at the bar's cell",
        "",
        (
            "The same bootstrap, recomputed from the baseline runs: the best single chunking is re-selected inside every "
            "resample, as in R7."
        ),
        "",
        "| group | best single chunking | section-aware recall | oracle router recall | routing headroom | CI |",
        "|---|---|---|---|---|---|",
    ]
    for group, best, reference, oracle_recall, headroom, interval in oracle.rows:
        lines.append(
            f"| {group} | {best} | {_f(reference)} | {_f(oracle_recall)} | {_s(headroom.point)} | {_ci(interval)} |"
        )
    lines += [
        "",
        (
            f"Oracle router minus section-aware, pooled (the share's denominator): "
            f"{_s(oracle.oracle_minus_reference.point)}."
        ),
        "",
    ]
    return lines


def _answer_lines(cfg: VerdictConfig, answers: dict, results: Sequence[ContenderResult]) -> list[str]:
    lines = [
        "## Answer scores (the reader stage, R14)",
        "",
        "| group | setup | n | answer score | CI | difference from section-aware | CI |",
        "|---|---|---|---|---|---|---|",
    ]
    groups = ["pooled", *sorted(cfg.datasets)] if len(cfg.datasets) > 1 else list(cfg.datasets)
    for group in groups:
        for setup in cfg.answer_setups:
            e = answers.get((group, setup))
            if e is None:
                continue
            diff = "- | -" if e.difference is None else f"{_s(e.difference.point)} | {_ci(e.difference_interval)}"
            lines.append(f"| {group} | {setup} | {e.n} | {_f(e.score.point)} | {_ci(e.score_interval)} | {diff} |")
    unread = [r.spec.name for r in results if r.judgement.answers is None]
    lines += [
        "",
        (
            f"The reader stage read {', '.join(cfg.answer_setups)} only. No contender's answers were measured "
            f"({', '.join(unread)}): the answer guard was dropped by the 2026-10-17 amendment to ADR 0008, and the "
            "reader stage's three setups were fixed before section-aware-titles ran, so the answers check reads "
            '"not measured" and decides nothing.'
        ),
        "",
    ]
    return lines


def _secondary_lines(cfg: VerdictConfig, results: Sequence[ContenderResult], sides: Sequence[ContenderResult]):
    budgets = sorted((*cfg.secondary_budgets, cfg.budget))
    lines = [
        "## Secondary results (they decide nothing)",
        "",
        "### Other budgets, budget view",
        "",
        (
            f"Pooled recall difference from section-aware. CIs: {cfg.confidence:.0%} unadjusted at {cfg.budget} tokens, "
            "Holm-adjusted over the other budgets per system, as in v1 (the level column gives each interval's level)."
        ),
        "",
        "| system | " + " | ".join(f"{b} difference | CI | level" for b in budgets) + " |",
        "|---|" + "---|---|---|" * len(budgets),
    ]
    for r in (*results, *sides):
        series = r.secondary | {cfg.budget: (r.primary.pooled, r.interval)}
        cells = [f"{_s(series[b][0].point)} | {_ci(series[b][1])} | {series[b][1].confidence:.2%}" for b in budgets]
        lines.append(f"| {r.spec.name} | " + " | ".join(cells) + " |")
    head = " | ".join(f"{d} difference" for d in cfg.datasets)
    lines += [
        "",
        f"### Production view (top-N cap {cfg.top_n}), {cfg.budget} tokens",
        "",
        f"| system | pooled difference | CI | {head} |",
        "|---|---|---|" + "---|" * len(cfg.datasets),
    ]
    for r in (*results, *sides):
        diff, interval = r.production
        per_dataset = " | ".join(_s(diff.per_dataset[d].point) for d in cfg.datasets)
        lines.append(f"| {r.spec.name} | {_s(diff.pooled.point)} | {_ci(interval)} | {per_dataset} |")
    if sides:
        lines += ["", "### Side variants at the bar's cell", ""]
        for r in sides:
            j = r.judgement
            would = "would clear the bar" if j.passed else f"would not clear the bar ({'; '.join(j.reasons)})"
            lines.append(
                f"- {r.spec.name} ({r.spec.table.upper()}, not a contender): {_s(r.primary.pooled.point)} "
                f"{_ci(r.interval)}; {_datasets(r.primary)}; {would}."
            )
    return [*lines, ""]


def _depth_lines(cfg: VerdictConfig, depth: DepthResult) -> list[str]:
    name = cfg.depth_contender
    lines = [
        "### Depth-50 side run",
        "",
        (
            f"Section-aware and {name} reranked to depth 50 ({cfg.depth_runs[1]}) next to depth 30 ({cfg.depth_runs[0]}), "
            "at the bar's cell, pooled."
        ),
        "",
        "| system | recall, depth 30 | recall, depth 50 | depth 50 - depth 30 | CI |",
        "|---|---|---|---|---|",
    ]
    for system in (REFERENCE, name):
        diff, interval = depth.shifts[system]
        lines.append(
            f"| {system} | {_f(depth.means[(system, 30)])} | {_f(depth.means[(system, 50)])} | "
            f"{_s(diff.pooled.point)} | {_ci(interval)} |"
        )
    lines += ["", f"| rerank depth | {name} - section-aware | CI | per dataset | bar's retrieval checks |"]
    lines.append("|---|---|---|---|---|")
    for d in (30, 50):
        diff, interval = depth.margins[d]
        j = depth.judgements[d]
        checks = "pass" if j.passed else f"fail ({'; '.join(j.reasons)})"
        lines.append(f"| {d} | {_s(diff.pooled.point)} | {_ci(interval)} | {_datasets(diff)} | {checks} |")
    same = depth.judgements[30].passed == depth.judgements[50].passed
    lines += [
        "",
        (
            f"Section-aware's budget-view list packs chunks from past the reranked head for "
            f"{depth.tail_share[30]:.1%} of questions at depth 30 and {depth.tail_share[50]:.1%} at depth 50. "
            f"A depth-50 rerank moves the margin from {_s(depth.margins[30][0].pooled.point)} to "
            f"{_s(depth.margins[50][0].pooled.point)}; "
            + (
                "it does not change whether the margin clears the bar's retrieval checks."
                if same
                else "it changes whether the margin clears the bar's retrieval checks."
            )
        ),
        "",
    ]
    return lines


def _ms(stats: dict[str, float]) -> str:
    return f"{stats['mean']:.1f} / {stats['p50']:.1f} / {stats['p90']:.1f}"


def _adoption_lines(
    cfg: VerdictConfig, latency: dict[str, Any], index_costs: dict[str, Any], answers_manifest: dict[str, Any]
) -> list[str]:
    hardware, versions = latency["hardware"], latency["versions"]
    sample = ", ".join(f"{n} {d}" for d, n in latency["questions"].items())
    lines = [
        "## Adoption profile",
        "",
        "### Query path, uncached",
        "",
        (
            f"Milliseconds per question, mean / median / p90, over {sum(latency['questions'].values())} seeded "
            f"questions ({sample}; seed {latency['seed']}), after {latency['warmup']} untimed warm-up question per "
            "system. Every query vector and reranker score is computed by the model (the embedding and score caches "
            f"are not used); searches run over the runs' own indexes, {latency['search_depth']} deep. Probe config "
            f"hash `{latency['config_hash']}`."
        ),
        "",
        "| system | searches | reranker pairs (mean) | query embedding ms | searches ms | reranker ms | total ms |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in latency["systems"]:
        lines.append(
            f"| {row['name']} | {row['searches']} | {row['pairs']:.1f} | {_ms(row['embed_ms'])} | "
            f"{_ms(row['search_ms'])} | {_ms(row['rerank_ms'])} | {_ms(row['total_ms'])} |"
        )
    lines += [
        "",
        "- hardware: " + ", ".join(f"{k} {v}" for k, v in hardware.items()),
        "- versions: " + ", ".join(f"{k} {v}" for k, v in versions.items()),
        "- models: " + ", ".join(f"{k} `{v}`" for k, v in latency["models"].items()),
        "",
        "### Index-time cost",
        "",
    ]
    chunks = index_costs["chunks"]
    for dataset in cfg.datasets:
        counts = chunks[dataset]
        lines.append(
            f"- {dataset}: section-aware indexes {counts[REFERENCE]} chunks; search-all and confidence routing index "
            f"all {len(counts)} chunkings, {sum(counts.values())} chunks."
        )
    for dataset, w in index_costs["late_windows"].items():
        lines.append(
            f"- {dataset}: late chunking reads every document whole, {w['windows']} windows of at most 8192 tokens "
            f"over {w['documents']} documents, one embedding pass serving late-128 and late-256."
        )
    p = index_costs["prefixes"]
    per_dataset = ", ".join(f"{d} {h:.1f} h" for d, h in p["per_dataset"].items())
    lines += [
        (
            f"- contextual-256: one prefix per fixed-256 chunk written by `{p['model']}`, {p['chunks']} chunks in "
            f"{p['wall_hours']:.1f} h of generation ({per_dataset})."
        ),
        "- section-aware-titles: a header per chunk from the dataset's own document and section titles; no model.",
        "",
        "### Reader cost per question",
        "",
    ]
    reader = answers_manifest["reader"]
    for setup, s in sorted(answers_manifest["setups"].items()):
        lines.append(
            f"- {setup}: {s['latency_seconds'] / s['prompts']:.2f} s per answer, "
            f"{s['prompt_tokens'] / s['prompts']:.0f} prompt tokens on average ({reader['model']}, local, "
            "no per-call cost)."
        )
    return [*lines, ""]


def render_r16(
    cfg: VerdictConfig,
    cfg_hash: str,
    hashes: dict[str, str],
    oracle: OracleCheck,
    results: Sequence[ContenderResult],
    sides: Sequence[ContenderResult],
    answers: dict,
    answers_manifest: dict[str, Any],
    depth: DepthResult,
    latency: dict[str, Any],
    index_costs: dict[str, Any],
) -> str:
    winner = tie_break([r.judgement for r in results], cfg.tie)
    lines = [
        f"# R16 - {cfg.run_name}: the pre-registered bar, the tie-break, answers, latency and cost",
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
        "| run | config hash |",
        "|---|---|",
        *(f"| {run} | `{h}` |" for run, h in sorted(hashes.items())),
        f"| {cfg.answers_run} | `{answers_manifest['config_hash']}` |",
        "",
        *_verdict_lines(cfg, results, winner),
        *_contender_table(cfg, results, winner),
        *_references(cfg, results),
        *_oracle_lines(oracle),
        *_answer_lines(cfg, answers, results),
        *_secondary_lines(cfg, results, sides),
        *_depth_lines(cfg, depth),
        *_adoption_lines(cfg, latency, index_costs, answers_manifest),
        "These tables regenerate byte-identically from the same runs and seed: nothing run-specific enters them.",
        "",
    ]
    return "\n".join(lines)


def run_verdict(cfg: VerdictConfig, paths: Paths) -> Path:
    """Write R16; returns its path."""
    primary: Cell = ("budget", cfg.budget)
    oracle_check = _oracle(cfg, paths, primary)
    cells = [primary, *(("budget", b) for b in cfg.secondary_budgets), ("production", cfg.budget)]
    baseline, hashes = _load(cfg, paths, cfg.oracle_run, REFERENCE, False, cells)
    headroom = oracle_check.oracle_minus_reference.point
    results = [_analyse_contender(cfg, paths, spec, baseline, headroom, hashes) for spec in cfg.contenders]
    sides = [_analyse_contender(cfg, paths, spec, baseline, headroom, hashes) for spec in cfg.side_variants]
    answers_dir = paths.runs / cfg.answers_run
    answer_rows = [r for r in read_answers(answers_dir / "answers.parquet") if r["setup"] in cfg.answer_setups]
    answers = analyse_answers(
        answer_rows,
        cfg.answer_setups,
        cfg.datasets,
        reference=REFERENCE,
        resamples=cfg.resamples,
        seed=cfg.seed,
        confidence=cfg.confidence,
    )
    depth = _depth(cfg, paths, primary, hashes)
    text = render_r16(
        cfg=cfg,
        cfg_hash=verdict_config_hash(cfg),
        hashes=hashes,
        oracle=oracle_check,
        results=results,
        sides=sides,
        answers=answers,
        answers_manifest=json.loads((answers_dir / "manifest.json").read_text(encoding="utf-8")),
        depth=depth,
        latency=json.loads((paths.root / cfg.latency).read_text(encoding="utf-8")),
        index_costs=_index_costs(cfg, paths),
    )
    path = paths.results / "v2" / "r16-verdict.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  result table: {path}")
    return path
