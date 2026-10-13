"""Result tables R2, R3, R4 and R2w, rendered from a grid run's
per-question results (runs/<run_name>/*.parquet).

Every number is a mean over the included questions, summed with
math.fsum so the tables do not depend on row order, and printed to four
decimals; nothing run-specific (time, versions) enters a table, so the
same config over the same data regenerates them byte-identically.

- R2: chunking x budget, retrieval recall and precision, production view
  and fair view side by side, plus the side table with the smaller top-N
  cap; collection search.
- R2w: R2 with search within the question's own document.
- R3: chunking x budget, retrieval recall per query type and the
  difference between types (context minus precise); collection search.
  Mixed questions are counted but left out of the contrast.
- R4: fixed-k hit@k and recall@k, for comparison with the literature.

"n/a" marks a fixed chunking whose chunk is bigger than the budget (not
scored there). The top-N cap binds for a question when it stops packing
while a further ranked chunk would still have fit the budget; every
production-view cell gives the share of questions where it did, and "†"
marks the cells where that share is at least half, i.e. where the cap
rather than the budget limits the retrieved text. A cell can show a small
share without "†": a document's last window is shorter than the chunk
size, so N chunks can leave room for one more.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq

from .config import GridConfig, config_yaml
from .query_type import CONTEXT, MIXED, PRECISE, QUERY_TYPES

NA = "n/a"
CAP_MARK = "†"
CAP_MARK_SHARE = 0.5


@dataclass
class _Cell:
    scored: bool = True
    recall: list[float] = field(default_factory=list)
    precision: list[float] = field(default_factory=list)
    cap_bound: list[bool] = field(default_factory=list)
    recall_by_type: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))


def _mean(values: list[float]) -> float:
    return math.fsum(values) / len(values) if values else 0.0


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _cells(results: dict[str, list]) -> dict[tuple, _Cell]:
    cells: dict[tuple, _Cell] = defaultdict(_Cell)
    rows = zip(
        results["scope"],
        results["chunking"],
        results["view"],
        results["top_n"],
        results["budget"],
        results["scored"],
        results["recall"],
        results["precision"],
        results["cap_bound"],
        results["query_type"],
        strict=True,
    )
    for scope, chunking, view, top_n, budget, scored, recall, precision, cap_bound, qtype in rows:
        cell = cells[(scope, chunking, view, top_n, budget)]
        if not scored:
            cell.scored = False
            continue
        cell.recall.append(recall)
        cell.precision.append(precision)
        cell.recall_by_type[qtype].append(recall)
        if cap_bound is not None:
            cell.cap_bound.append(cap_bound)
    return cells


def _header(title: str, cfg: GridConfig, cfg_hash: str, dataset_hashes: dict[str, str], counts: dict[str, int]):
    lines = [title, "", f"Config hash: `{cfg_hash}`", "", "## Config", "", "```yaml", config_yaml(cfg), "```", ""]
    lines += ["## Dataset", "", "| split | sha256 |", "|---|---|"]
    lines += [f"| {split} | `{dataset_hashes[split]}` |" for split in sorted(dataset_hashes)]
    lines += ["", "## Questions", "", "| query type | n |", "|---|---|"]
    lines += [f"| {t} | {counts.get(t, 0)} |" for t in QUERY_TYPES]
    lines += [f"| total | {sum(counts.values())} |", ""]
    return lines


def _metric(cell: _Cell, values: list[float], capped: bool) -> str:
    if not cell.scored:
        return NA
    mark = CAP_MARK if capped and _cap_share(cell) >= CAP_MARK_SHARE else ""
    return _fmt(_mean(values)) + mark


def _cap_share(cell: _Cell) -> float:
    return _mean([1.0 if b else 0.0 for b in cell.cap_bound])


def _cap_cell(cell: _Cell) -> str:
    return _fmt(_cap_share(cell)) if cell.scored else NA


def _r2(cfg: GridConfig, cells: dict[tuple, _Cell], scope: str, header: list[str]) -> str:
    lines = list(header)
    lines += [
        f"## Production view (top-N cap {cfg.top_n}) and fair view (no cap)",
        "",
        "| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |",
        "|---|---|---|---|---|---|---|",
    ]
    for spec in cfg.chunkings:
        for budget in cfg.budgets:
            prod = cells[(scope, spec.name, "production", cfg.top_n, budget)]
            fair = cells[(scope, spec.name, "fair", None, budget)]
            lines.append(
                f"| {spec.name} | {budget} | {_metric(prod, prod.recall, True)} | "
                f"{_metric(prod, prod.precision, True)} | {_metric(fair, fair.recall, False)} | "
                f"{_metric(fair, fair.precision, False)} | {_cap_cell(prod)} |"
            )
    lines += [
        "",
        f"## Side table: production view, top-N cap {cfg.side_top_n}",
        "",
        "| chunking | budget | recall | precision | cap binds |",
        "|---|---|---|---|---|",
    ]
    for spec in cfg.chunkings:
        for budget in cfg.budgets:
            side = cells[(scope, spec.name, "production", cfg.side_top_n, budget)]
            lines.append(
                f"| {spec.name} | {budget} | {_metric(side, side.recall, True)} | "
                f"{_metric(side, side.precision, True)} | {_cap_cell(side)} |"
            )
    lines += [
        "",
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        (
            "`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would "
            f"still have fit the budget; {CAP_MARK}: the cap binds for at least half of the questions."
        ),
        "",
    ]
    return "\n".join(lines)


def _type_cells(cell: _Cell) -> tuple[str, str, str]:
    if not cell.scored:
        return NA, NA, NA
    precise = _mean(cell.recall_by_type[PRECISE])
    context = _mean(cell.recall_by_type[CONTEXT])
    return _fmt(precise), _fmt(context), f"{context - precise:+.4f}"


def _r3(cfg: GridConfig, cells: dict[tuple, _Cell], header: list[str]) -> str:
    lines = list(header)
    lines += [
        f"## Retrieval recall by query type, collection search (production view: top-N cap {cfg.top_n})",
        "",
        (
            "| chunking | budget | production precise | production context | production context - precise "
            "| fair precise | fair context | fair context - precise |"
        ),
        "|---|---|---|---|---|---|---|---|",
    ]
    for spec in cfg.chunkings:
        for budget in cfg.budgets:
            prod = _type_cells(cells[("collection", spec.name, "production", cfg.top_n, budget)])
            fair = _type_cells(cells[("collection", spec.name, "fair", None, budget)])
            lines.append(f"| {spec.name} | {budget} | " + " | ".join(prod + fair) + " |")
    lines += [
        "",
        (
            f"Precise: every usable annotation cites one passage; context: every one cites several; {MIXED}: "
            "otherwise. Mixed questions count in the means of R2 but not in this contrast."
        ),
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        "",
    ]
    return "\n".join(lines)


def _r4(cfg: GridConfig, fixed_k: dict[str, list], header: list[str]) -> str:
    hits: dict[tuple[str, int], list[float]] = defaultdict(list)
    recalls: dict[tuple[str, int], list[float]] = defaultdict(list)
    for chunking, scope, k, hit, recall in zip(
        fixed_k["chunking"], fixed_k["scope"], fixed_k["k"], fixed_k["hit"], fixed_k["recall"], strict=True
    ):
        if scope != "collection":
            continue
        hits[(chunking, k)].append(1.0 if hit else 0.0)
        recalls[(chunking, k)].append(recall)
    ks = cfg.fixed_k
    lines = list(header)
    lines += [
        "## Fixed-k retrieval, collection search (for comparison with the literature only)",
        "",
        "| chunking | " + " | ".join(f"hit@{k}" for k in ks) + " | " + " | ".join(f"recall@{k}" for k in ks) + " |",
        "|---|" + "---|" * (2 * len(ks)),
    ]
    for spec in cfg.chunkings:
        cols = [_fmt(_mean(hits[(spec.name, k)])) for k in ks] + [_fmt(_mean(recalls[(spec.name, k)])) for k in ks]
        lines.append(f"| {spec.name} | " + " | ".join(cols) + " |")
    lines += [
        "",
        (
            "Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched "
            "children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is "
            "relevant, recall@k the share of the document's relevant units in the top k, best annotator kept."
        ),
        "",
    ]
    return "\n".join(lines)


def write_tables(
    cfg: GridConfig, cfg_hash: str, dataset_hashes: dict[str, str], run_dir: Path, results_dir: Path
) -> tuple[Path, ...]:
    """Render R2, R3, R4 and R2w from the run's Parquet files; returns their paths."""
    questions = pq.read_table(run_dir / "questions.parquet").to_pydict()
    counts = {t: questions["query_type"].count(t) for t in QUERY_TYPES}
    cells = _cells(pq.read_table(run_dir / "results.parquet").to_pydict())
    fixed_k = pq.read_table(run_dir / "fixed_k.parquet").to_pydict()

    base = f"{cfg.dataset} {cfg.run_name}, {cfg.pipeline}"
    out_dir = results_dir / cfg.dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "r2": _r2(
            cfg,
            cells,
            "collection",
            _header(f"# R2 - {base}: chunking x budget, collection search", cfg, cfg_hash, dataset_hashes, counts),
        ),
        "r3": _r3(
            cfg,
            cells,
            _header(f"# R3 - {base}: chunk size x query type", cfg, cfg_hash, dataset_hashes, counts),
        ),
        "r4": _r4(cfg, fixed_k, _header(f"# R4 - {base}: fixed-k", cfg, cfg_hash, dataset_hashes, counts)),
    }
    if "document" in cfg.scopes:
        tables["r2w"] = _r2(
            cfg,
            cells,
            "document",
            _header(f"# R2w - {base}: chunking x budget, within the document", cfg, cfg_hash, dataset_hashes, counts),
        )
    paths: list[Path] = []
    for name, text in tables.items():
        path = out_dir / f"{name}-{cfg.run_name}.md"
        path.write_text(text, encoding="utf-8")
        paths.append(path)
    return tuple(paths)
