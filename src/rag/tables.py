"""Result tables R2, R3, R4, R2w, R5 and R6, rendered from a grid run's
per-question results (runs/<dataset>/<run_name>/*.parquet).

Every number is a mean over the included questions, summed with
math.fsum so the tables do not depend on row order, and printed to four
decimals; nothing run-specific (time, versions) enters a table, so the
same config over the same data regenerates them byte-identically.

- R2: chunking x budget, retrieval recall and precision, production view
  and fair view side by side, plus the budget view (top-N cap
  `budget_top_n`, v2: 20, when it is set) and the side table with the
  smaller top-N cap; collection search.
- R2w: R2 with search within the question's own document.
- R3: chunking x budget, retrieval recall per query type and the
  difference between types (context minus precise); collection search.
  Mixed questions are counted but left out of the contrast.
- R4: fixed-k hit@k and recall@k, for comparison with the literature.
- R5 (runs with embedders): pipeline x embedder x chunking at each
  budget, the production line first and the ablations after, with each
  chunking's truncation share under the embedder and how often packing
  reached the production line's unreranked tail; the budget view's recall
  and precision join when `budget_top_n` is set; collection search.
- R6: NQ short-answer span recall per chunking and budget (Natural
  Questions runs only), the same packing scored against the
  short-answer spans of precise questions that have one.

R2, R3, R4, R2w and R6 hold one block per pipeline and embedder, in R5's
order; a BM25-only run has a single block and no block headings.

Pooled runs keep each dataset's n visible: the Questions section breaks
the query-type counts down per dataset, and means run over all the
loaded questions together.

"n/a" marks a fixed chunking whose chunk is bigger than the budget (not
scored there). The top-N cap binds for a question when it stops packing
while a further ranked chunk would still have fit the budget; every
production-view cell gives the share of questions where it did, and "†"
marks the cells where that share is at least half, i.e. where the cap
rather than the budget limits the retrieved text. A cell can show a small
share without "†": a document's last window is shorter than the chunk
size, so N chunks can leave room for one more. "§" marks production-line
cells where packing used the unreranked tail for at least one question,
and "‡" a chunking some of whose chunks exceed the embedder's input limit.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow.parquet as pq

from .config import PIPELINES, PRODUCTION_LINE, GridConfig, config_yaml
from .models import EMBEDDERS, RERANKER
from .query_type import CONTEXT, MIXED, PRECISE, QUERY_TYPES

NA = "n/a"
CAP_MARK = "†"
CAP_MARK_SHARE = 0.5
TAIL_MARK = "§"
TRUNCATION_MARK = "‡"

Block = tuple[str, str | None]  # (pipeline, embedder); BM25 has no embedder

_PIPELINE_TITLES = {
    PRODUCTION_LINE: "Production line: hybrid, then the reranker over the fused top {depth}",
    "hybrid": "Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker",
    "vector": "Ablation: vector search only",
    "bm25": "Ablation: BM25 only",
}


@dataclass
class _Cell:
    scored: bool = True
    recall: list[float] = field(default_factory=list)
    precision: list[float] = field(default_factory=list)
    short_recall: list[float] = field(default_factory=list)
    cap_bound: list[bool] = field(default_factory=list)
    used_tail: list[bool] = field(default_factory=list)
    short_cap_bound: list[bool] = field(default_factory=list)
    recall_by_type: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))


def _mean(values: list[float]) -> float:
    return math.fsum(values) / len(values) if values else 0.0


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _share(values: list[bool]) -> float:
    return _mean([1.0 if v else 0.0 for v in values])


def blocks(cfg: GridConfig) -> list[Block]:
    """The pipeline x embedder blocks of a run, the production line first."""
    out: list[Block] = []
    for pipeline in PIPELINES:
        if pipeline in cfg.pipelines:
            out += [(pipeline, None)] if pipeline == "bm25" else [(pipeline, e) for e in cfg.embedders]
    return out


def _cells(results: dict[str, list]) -> dict[tuple, _Cell]:
    """Cells keyed by (pipeline, embedder, scope, chunking, view, top_n, budget), aggregated
    over every dataset in the run: pooled tables are the means over all
    loaded questions together."""
    cells: dict[tuple, _Cell] = defaultdict(_Cell)
    rows = zip(
        results["pipeline"],
        results["embedder"],
        results["scope"],
        results["chunking"],
        results["view"],
        results["top_n"],
        results["budget"],
        results["scored"],
        results["recall"],
        results["precision"],
        results["short_recall"],
        results["cap_bound"],
        results["used_tail"],
        results["query_type"],
        strict=True,
    )
    for (
        pipeline,
        embedder,
        scope,
        chunking,
        view,
        top_n,
        budget,
        scored,
        recall,
        precision,
        short,
        cap,
        tail,
        qtype,
    ) in rows:
        cell = cells[(pipeline, embedder, scope, chunking, view, top_n, budget)]
        if not scored:
            cell.scored = False
            continue
        cell.recall.append(recall)
        cell.precision.append(precision)
        if short is not None:
            cell.short_recall.append(short)
            if cap is not None:
                cell.short_cap_bound.append(cap)
        cell.recall_by_type[qtype].append(recall)
        if cap is not None:
            cell.cap_bound.append(cap)
        if tail is not None:
            cell.used_tail.append(tail)
    return cells


def _truncation(results: dict[str, list]) -> dict[tuple[str, str], float]:
    """(chunking, embedder) -> share of the chunking's chunks over the embedder's input limit."""
    out: dict[tuple[str, str], float] = {}
    for chunking, embedder, share in zip(
        results["chunking"], results["embedder"], results["truncated_share"], strict=True
    ):
        if embedder is not None and share is not None:
            out[(chunking, embedder)] = share
    return out


def _question_counts(questions: dict[str, list]) -> dict:
    """Query-type counts, per dataset when more than one is loaded."""
    datasets = sorted(set(questions["dataset"]))
    if len(datasets) == 1:
        return {"": {t: questions["query_type"].count(t) for t in QUERY_TYPES}}
    counts: dict[str, dict[str, int]] = {d: {t: 0 for t in QUERY_TYPES} for d in datasets}
    for dataset, qtype in zip(questions["dataset"], questions["query_type"], strict=True):
        counts[dataset][qtype] += 1
    return counts


def _header(
    title: str,
    cfg: GridConfig,
    cfg_hash: str,
    dataset_hashes: dict[str, str],
    questions: dict[str, list],
    sample: int | None = None,
):
    lines = [title, "", f"Config hash: `{cfg_hash}`", ""]
    if sample is not None:
        lines += [
            f"Development run on a seeded sample of {sample} documents (seed {cfg.seed}), not the full dataset.",
            "",
        ]
    lines += ["## Config", "", "```yaml", config_yaml(cfg), "```", ""]
    if cfg.embedders:
        lines += ["## Models", "", "| role | name | model | revision | input limit |", "|---|---|---|---|---|"]
        for name in cfg.embedders:
            spec = EMBEDDERS[name]
            lines.append(f"| embedder | {name} | {spec.model_id} | `{spec.revision}` | {spec.max_tokens} tokens |")
        if PRODUCTION_LINE in cfg.pipelines:
            lines.append(f"| reranker | {RERANKER.name} | {RERANKER.model_id} | `{RERANKER.revision}` | {NA} |")
        lines.append("")
    lines += ["## Dataset", "", "| split | sha256 |", "|---|---|"]
    lines += [f"| {split} | `{dataset_hashes[split]}` |" for split in sorted(dataset_hashes)]
    counts = _question_counts(questions)
    lines += ["", "## Questions", ""]
    if len(counts) == 1:
        only = next(iter(counts.values()))
        lines += ["| query type | n |", "|---|---|"]
        lines += [f"| {t} | {n} |" for t, n in only.items()]
        lines += [f"| total | {sum(only.values())} |", ""]
        return lines
    lines += ["| dataset | query type | n |", "|---|---|---|"]
    for dataset in sorted(counts):
        for t, n in counts[dataset].items():
            lines.append(f"| {dataset} | {t} | {n} |")
    lines += [f"| total | | {sum(sum(c.values()) for c in counts.values())} |", ""]
    return lines


def _metric(
    cell: _Cell, values: list[float], capped: bool, bound: list[bool] | None = None, tail_mark: bool = True
) -> str:
    if not cell.scored:
        return NA
    share = _cap_share(cell.cap_bound if bound is None else bound)
    mark = CAP_MARK if capped and share >= CAP_MARK_SHARE else ""
    if tail_mark and any(cell.used_tail):
        mark += TAIL_MARK
    return _fmt(_mean(values)) + mark


def _cap_share(bound: list[bool]) -> float:
    return _share(bound)


def _cap_cell(cell: _Cell, bound: list[bool] | None = None) -> str:
    return _fmt(_cap_share(cell.cap_bound if bound is None else bound)) if cell.scored else NA


def _block_title(cfg: GridConfig, block: Block) -> str:
    pipeline, embedder = block
    title = _PIPELINE_TITLES[pipeline].format(depth=cfg.rerank_depth)
    return f"{title}, {embedder}" if embedder else title


def _truncation_note(cfg: GridConfig, embedder: str, truncation: dict[tuple[str, str], float]) -> str:
    limit = EMBEDDERS[embedder].max_tokens
    over = [f"{spec.name} {_fmt(share)}" for spec in cfg.chunkings if (share := truncation[(spec.name, embedder)]) > 0]
    if not over:
        return f"No chunk exceeds {embedder}'s {limit}-token input."
    return f"Share of chunks longer than {embedder}'s {limit}-token input, embedded truncated: {', '.join(over)}."


def _blocked(cfg: GridConfig, truncation: dict[tuple[str, str], float], render) -> list[str]:
    """Each block's lines in order; with several blocks, each under its own
    heading (and its sections one level down)."""
    run_blocks = blocks(cfg)
    multi = len(run_blocks) > 1
    lines: list[str] = []
    for i, block in enumerate(run_blocks):
        if i:
            lines.append("")
        if multi:
            lines += [f"## {_block_title(cfg, block)}", ""]
            if block[1] is not None:
                lines += [_truncation_note(cfg, block[1], truncation), ""]
        lines += render(block, "###" if multi else "##")
    return lines


def _notes(cfg: GridConfig) -> list[str]:
    notes: list[str] = []
    if PRODUCTION_LINE in cfg.pipelines:
        notes.append(
            f"{TAIL_MARK}: production line only; for at least one question, packing went past the reranked top "
            f"{cfg.rerank_depth} into the unreranked tail, which continues in fused (hybrid) order."
        )
    return notes


def _r2(
    cfg: GridConfig, cells: dict[tuple, _Cell], scope: str, header: list[str], truncation: dict[tuple[str, str], float]
) -> str:
    def render(block: Block, h: str) -> list[str]:
        lines = [
            f"{h} Production view (top-N cap {cfg.top_n}) and fair view (no cap)",
            "",
            "| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |",
            "|---|---|---|---|---|---|---|",
        ]
        for spec in cfg.chunkings:
            for budget in cfg.budgets:
                prod = cells[(*block, scope, spec.name, "production", cfg.top_n, budget)]
                fair = cells[(*block, scope, spec.name, "fair", None, budget)]
                lines.append(
                    f"| {spec.name} | {budget} | {_metric(prod, prod.recall, True)} | "
                    f"{_metric(prod, prod.precision, True)} | {_metric(fair, fair.recall, False)} | "
                    f"{_metric(fair, fair.precision, False)} | {_cap_cell(prod)} |"
                )
        if cfg.budget_top_n is not None:
            lines += [
                "",
                f"{h} Budget view (top-N cap {cfg.budget_top_n})",
                "",
                "| chunking | budget | recall | precision | cap binds |",
                "|---|---|---|---|---|",
            ]
            for spec in cfg.chunkings:
                for budget in cfg.budgets:
                    view = cells[(*block, scope, spec.name, "budget", cfg.budget_top_n, budget)]
                    lines.append(
                        f"| {spec.name} | {budget} | {_metric(view, view.recall, True)} | "
                        f"{_metric(view, view.precision, True)} | {_cap_cell(view)} |"
                    )
        lines += [
            "",
            f"{h} Side table: production view, top-N cap {cfg.side_top_n}",
            "",
            "| chunking | budget | recall | precision | cap binds |",
            "|---|---|---|---|---|",
        ]
        for spec in cfg.chunkings:
            for budget in cfg.budgets:
                side = cells[(*block, scope, spec.name, "production", cfg.side_top_n, budget)]
                lines.append(
                    f"| {spec.name} | {budget} | {_metric(side, side.recall, True)} | "
                    f"{_metric(side, side.precision, True)} | {_cap_cell(side)} |"
                )
        return lines

    lines = list(header) + _blocked(cfg, truncation, render)
    lines += [
        "",
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        (
            "`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would "
            f"still have fit the budget; {CAP_MARK}: the cap binds for at least half of the questions."
        ),
        *_notes(cfg),
        "",
    ]
    return "\n".join(lines)


def _type_cells(cell: _Cell) -> tuple[str, str, str]:
    if not cell.scored:
        return NA, NA, NA
    precise = _mean(cell.recall_by_type[PRECISE])
    context = _mean(cell.recall_by_type[CONTEXT])
    return _fmt(precise), _fmt(context), f"{context - precise:+.4f}"


def _r3(cfg: GridConfig, cells: dict[tuple, _Cell], header: list[str], truncation: dict[tuple[str, str], float]) -> str:
    def render(block: Block, h: str) -> list[str]:
        lines = [
            f"{h} Retrieval recall by query type, collection search (production view: top-N cap {cfg.top_n})",
            "",
            (
                "| chunking | budget | production precise | production context | production context - precise "
                "| fair precise | fair context | fair context - precise |"
            ),
            "|---|---|---|---|---|---|---|---|",
        ]
        for spec in cfg.chunkings:
            for budget in cfg.budgets:
                prod = _type_cells(cells[(*block, "collection", spec.name, "production", cfg.top_n, budget)])
                fair = _type_cells(cells[(*block, "collection", spec.name, "fair", None, budget)])
                lines.append(f"| {spec.name} | {budget} | " + " | ".join(prod + fair) + " |")
        return lines

    lines = list(header) + _blocked(cfg, truncation, render)
    lines += [
        "",
        (
            "Query types are assigned from the labels: for Natural Questions, short answer means precise and "
            "long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, "
            f"context that every one cites several and {MIXED} otherwise (only that rule produces mixed questions, "
            "which count in the means of R2 but not in this contrast)."
        ),
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        "",
    ]
    return "\n".join(lines)


def _r4(cfg: GridConfig, fixed_k: dict[str, list], header: list[str], truncation: dict[tuple[str, str], float]) -> str:
    hits: dict[tuple, list[float]] = defaultdict(list)
    recalls: dict[tuple, list[float]] = defaultdict(list)
    for pipeline, embedder, chunking, scope, k, hit, recall in zip(
        fixed_k["pipeline"],
        fixed_k["embedder"],
        fixed_k["chunking"],
        fixed_k["scope"],
        fixed_k["k"],
        fixed_k["hit"],
        fixed_k["recall"],
        strict=True,
    ):
        if scope != "collection":
            continue
        hits[(pipeline, embedder, chunking, k)].append(1.0 if hit else 0.0)
        recalls[(pipeline, embedder, chunking, k)].append(recall)
    ks = cfg.fixed_k

    def render(block: Block, h: str) -> list[str]:
        lines = [
            f"{h} Fixed-k retrieval, collection search (for comparison with the literature only)",
            "",
            "| chunking | " + " | ".join(f"hit@{k}" for k in ks) + " | " + " | ".join(f"recall@{k}" for k in ks) + " |",
            "|---|" + "---|" * (2 * len(ks)),
        ]
        for spec in cfg.chunkings:
            cols = [_fmt(_mean(hits[(*block, spec.name, k)])) for k in ks]
            cols += [_fmt(_mean(recalls[(*block, spec.name, k)])) for k in ks]
            lines.append(f"| {spec.name} | " + " | ".join(cols) + " |")
        return lines

    lines = list(header) + _blocked(cfg, truncation, render)
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


def _r5(cfg: GridConfig, cells: dict[tuple, _Cell], header: list[str], truncation: dict[tuple[str, str], float]) -> str:
    unscored = f"{NA}: chunk > budget"
    lines = list(header)
    lines += [
        "## Retrieval recall and precision by pipeline, embedder and chunking, collection search",
        "",
        (
            f"Production view: top-N cap {cfg.top_n}; fair view: no cap"
            + (f"; budget view: top-N cap {cfg.budget_top_n}" if cfg.budget_top_n is not None else "")
            + ". The production line comes first, then its ablations. Every cell is filled or n/a with its reason."
        ),
        "",
    ]
    for budget in cfg.budgets:
        has_budget = cfg.budget_top_n is not None
        header_cells = ["pipeline", "embedder", "chunking", "production recall", "production precision"]
        header_cells += ["budget recall", "budget precision"] if has_budget else []
        header_cells += ["fair recall", "fair precision", "truncated chunks"]
        header_cells += ["tail used, production view"] + (["tail used, budget view"] if has_budget else [])
        header_cells += ["tail used, fair view"]
        lines += [
            f"### Budget {budget} tokens",
            "",
            "| " + " | ".join(header_cells) + " |",
            "|" + "---|" * len(header_cells),
        ]
        for pipeline, embedder in blocks(cfg):
            for spec in cfg.chunkings:
                prod = cells[(pipeline, embedder, "collection", spec.name, "production", cfg.top_n, budget)]
                fair = cells[(pipeline, embedder, "collection", spec.name, "fair", None, budget)]
                view_cells = [prod]
                if has_budget:
                    view_cells.append(
                        cells[(pipeline, embedder, "collection", spec.name, "budget", cfg.budget_top_n, budget)]
                    )
                view_cells.append(fair)
                if embedder is None:
                    truncated = f"{NA}: no embedder"
                else:
                    share = truncation[(spec.name, embedder)]
                    truncated = _fmt(share) + (f" {TRUNCATION_MARK}" if share > 0 else "")
                # recall then precision per capped view (production, budget), then the fair view
                metrics = [
                    value
                    for c in view_cells[:-1]
                    for value in (
                        _metric(c, c.recall, True, tail_mark=False) if c.scored else unscored,
                        _metric(c, c.precision, True, tail_mark=False) if c.scored else unscored,
                    )
                ] + [
                    _fmt(_mean(fair.recall)) if fair.scored else unscored,
                    _fmt(_mean(fair.precision)) if fair.scored else unscored,
                ]
                if pipeline != PRODUCTION_LINE:
                    tails = [f"{NA}: no reranker"] * len(view_cells)
                else:
                    tails = [_fmt(_share(c.used_tail)) if c.scored else unscored for c in view_cells]
                row = [pipeline, embedder or "none", spec.name, *metrics, truncated, *tails]
                lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    lines += [
        f"`{unscored}`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        f"`{NA}: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.",
        f"`{NA}: no reranker`: only the production line reranks, so only it has an unreranked tail.",
        (
            "`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own "
            f"tokens, task prefix included), which it embeds truncated; {TRUNCATION_MARK} marks a share above zero."
        ),
        (
            f"`tail used`: share of questions whose packing went past the reranked top {cfg.rerank_depth} into the "
            "unreranked tail (fused order)."
        ),
        f"{CAP_MARK}: the top-N cap binds for at least half of the questions (see R2).",
        "",
    ]
    return "\n".join(lines)


def _r6(
    cfg: GridConfig,
    cells: dict[tuple, _Cell],
    header: list[str],
    n_short: int,
    truncation: dict[tuple[str, str], float],
) -> str:
    def render(block: Block, h: str) -> list[str]:
        lines = [
            f"{h} Short-answer span recall, collection search, n = {n_short} precise questions with a short-answer span",
            "",
            (
                f"The same packing as R2 (production view: top-N cap {cfg.top_n}; fair view: no cap) scored against "
                "the short-answer spans instead of the long-answer paragraph."
            ),
            "",
            "| chunking | budget | production short recall | fair short recall | cap binds |",
            "|---|---|---|---|---|",
        ]
        for spec in cfg.chunkings:
            for budget in cfg.budgets:
                prod = cells[(*block, "collection", spec.name, "production", cfg.top_n, budget)]
                fair = cells[(*block, "collection", spec.name, "fair", None, budget)]
                lines.append(
                    f"| {spec.name} | {budget} | {_metric(prod, prod.short_recall, True, prod.short_cap_bound)} | "
                    f"{_metric(fair, fair.short_recall, False)} | {_cap_cell(prod, prod.short_cap_bound)} |"
                )
        return lines

    lines = list(header) + _blocked(cfg, truncation, render)
    lines += [
        "",
        (
            "Precise questions whose short answers are yes or no only have no short-answer span and stay out of "
            "these means; they count in R2 and R3."
        ),
        f"{NA}: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.",
        *_notes(cfg),
        "",
    ]
    return "\n".join(lines)


def write_tables(
    cfg: GridConfig,
    cfg_hash: str,
    dataset_hashes: dict[str, str],
    run_dir: Path,
    results_dir: Path,
    sample: int | None = None,
) -> tuple[Path, ...]:
    """Render R2, R3, R4, R2w, R5 (with embedders) and R6 (for a Natural
    Questions run) from the run's Parquet files; returns their paths."""
    questions = pq.read_table(run_dir / "questions.parquet").to_pydict()
    results = pq.read_table(run_dir / "results.parquet").to_pydict()
    cells = _cells(results)
    truncation = _truncation(results)
    fixed_k = pq.read_table(run_dir / "fixed_k.parquet").to_pydict()

    def header(title: str) -> list[str]:
        return _header(f"# {title}", cfg, cfg_hash, dataset_hashes, questions, sample)

    base = f"{cfg.dataset} {cfg.run_name}, {cfg.pipeline}"
    out_dir = results_dir / cfg.dataset
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "r2": _r2(cfg, cells, "collection", header(f"R2 - {base}: chunking x budget, collection search"), truncation),
        "r3": _r3(cfg, cells, header(f"R3 - {base}: chunk size x query type"), truncation),
        "r4": _r4(cfg, fixed_k, header(f"R4 - {base}: fixed-k"), truncation),
    }
    if "document" in cfg.scopes:
        tables["r2w"] = _r2(
            cfg, cells, "document", header(f"R2w - {base}: chunking x budget, within the document"), truncation
        )
    if cfg.dataset == "nq":
        n_short = sum(1 for flag in questions["short_answer"] if flag)
        tables["r6"] = _r6(cfg, cells, header(f"R6 - {base}: short-answer span recall"), n_short, truncation)
    if cfg.embedders:
        tables["r5"] = _r5(cfg, cells, header(f"R5 - {base}: pipeline x embedder x chunking"), truncation)
    paths: list[Path] = []
    for name, text in tables.items():
        path = out_dir / f"{name}-{cfg.run_name}.md"
        path.write_text(text, encoding="utf-8")
        paths.append(path)
    return tuple(paths)
