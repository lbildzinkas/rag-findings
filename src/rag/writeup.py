"""`rag writeup`: the v1 and v2 write-ups' tables and figures, regenerated
from the committed result tables under results/ (and the pilot tables in
the research report), so a write-up never drifts from the data. This
module holds the shared readers, v1's blocks and figures, and the
regeneration; v2's blocks and figures are in `writeup_v2`.

A write-up marks each generated block with a pair of HTML comments,
`<!-- generated: NAME -->` and `<!-- end generated: NAME -->`. `rag
writeup` re-renders every marked block in place and rewrites the figures
under chunking/figures/; `rag writeup --check` changes nothing and fails
when a block or a figure differs from what the tables give, or when a
four-decimal number in the prose (in v2 also a percentage, or a time in
ms, s or h) appears in no generated block. Nothing is computed beyond
reading a cell or subtracting two cells (the ablation contrasts): no
retrieval or bootstrap runs here.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from . import figures
from .figures import Panel, Series, Whiskers

WRITEUP = "chunking/2026-10-14-v1-results.md"
FIGURE_DIR = "chunking/figures"
PILOT_REPORT = "chunking/2026-10-10-chunk-size-vs-query-type.md"
R7 = "results/routing/r7-headroom.md"
R8 = "results/routing/r8-headroom.md"
R9 = "results/routing/r9-headroom.md"

PRODUCTION_LINE = "hybrid-rerank"
EMBEDDERS = ("bge-small", "nomic")
VIEWS = ("production", "fair")
DATASETS = ("qasper", "nq", "pooled")
NAMES = {"qasper": "QASPER", "nq": "NQ", "pooled": "pooled"}
CHUNKINGS = ("fixed-64", "fixed-128", "fixed-256", "fixed-512", "fixed-1024", "section-aware", "small-to-big")
BUDGETS = ("128", "256", "512", "1024", "2048", "4096", "8192")
PRIMARY_BUDGET = "1024"
GATE_THRESHOLD = 0.05
LICENCES = {
    "BAAI/bge-small-en-v1.5": "MIT",
    "nomic-ai/nomic-embed-text-v1.5": "Apache-2.0",
    "Alibaba-NLP/gte-reranker-modernbert-base": "Apache-2.0",
}
PIPELINE_LABELS = {
    ("bm25", "-"): "BM25 only",
    ("vector", "bge-small"): "vector only, bge-small",
    ("vector", "nomic"): "vector only, nomic",
    ("hybrid", "bge-small"): "hybrid without the reranker, bge-small",
    ("hybrid", "nomic"): "hybrid without the reranker, nomic",
    ("hybrid-rerank", "bge-small"): "production line, bge-small",
    ("hybrid-rerank", "nomic"): "production line, nomic",
}
MARKS = " †§‡"

BLOCK = re.compile(
    r"(?P<open><!-- generated: (?P<name>[a-z0-9-]+) -->\n)(?P<body>.*?)(?P<close><!-- end generated: (?P=name) -->)",
    re.DOTALL,
)
NUMBER = re.compile(r"(?<![\d.])[+-]?\d+\.\d{4}(?!\.?\d)")
DECIMAL = re.compile(r"(?<![\d.])[+-]?\d+\.\d+(?!\.?\d)")


class WriteupError(ValueError):
    """A results table the write-up reads is missing, ambiguous or malformed."""


@dataclass(frozen=True)
class Table:
    headings: tuple[str, ...]  # the headings above the table, outermost first
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def records(self) -> list[dict[str, str]]:
        """Rows keyed by column name; a repeated column name gets " (2)", " (3)" ..."""
        keys: list[str] = []
        for name in self.header:
            count = sum(1 for k in keys if k == name or k.startswith(f"{name} ("))
            keys.append(name if count == 0 else f"{name} ({count + 1})")
        return [dict(zip(keys, row)) for row in self.rows]


def _cells(line: str) -> tuple[str, ...]:
    return tuple(cell.strip() for cell in line.strip().removeprefix("|").removesuffix("|").split("|"))


def parse_tables(text: str) -> list[Table]:
    """Every pipe table in a markdown text, with the headings it sits under
    (headings inside fenced code are ignored)."""
    tables: list[Table] = []
    headings: list[tuple[int, str]] = []
    lines = text.splitlines()
    in_fence = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            headings = [h for h in headings if h[0] < level] + [(level, line[level:].strip())]
        elif not in_fence and line.startswith("|") and i + 1 < len(lines) and set(lines[i + 1]) <= set("|-: "):
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = tuple(_cells(row) for row in lines[i + 2 : j])
            tables.append(Table(tuple(h for _, h in headings), _cells(line), rows))
            i = j
            continue
        i += 1
    return tables


@dataclass
class Sources:
    """The committed files the write-up reads, each read and parsed once."""

    root: Path
    _texts: dict[str, str] = field(default_factory=dict)
    _tables: dict[str, tuple[Table, ...]] = field(default_factory=dict)

    def text(self, relative: str) -> str:
        if relative not in self._texts:
            self._texts[relative] = (self.root / relative).read_text(encoding="utf-8")
        return self._texts[relative]

    def tables(self, relative: str) -> Sequence[Table]:
        if relative not in self._tables:
            self._tables[relative] = tuple(parse_tables(self.text(relative)))
        return self._tables[relative]


def find(tables: Sequence[Table], heading: str, under: str | None = None, column: str | None = None) -> Table:
    """The one table whose innermost heading starts with `heading`, with an
    outer heading starting with `under` and a `column`, when given."""
    found = [
        t
        for t in tables
        if t.headings
        and t.headings[-1].startswith(heading)
        and (under is None or any(h.startswith(under) for h in t.headings[:-1]))
        and (column is None or column in t.header)
    ]
    if len(found) != 1:
        raise WriteupError(f"expected one table under {heading!r} (in {under!r}), found {len(found)}")
    return found[0]


def select(table: Table, where: Mapping[str, str]) -> list[dict[str, str]]:
    return [r for r in table.records() if all(r[k] == v for k, v in where.items())]


def pick(records: Sequence[Mapping[str, str]], where: Mapping[str, str]) -> Mapping[str, str]:
    """The one record matching every `where` value."""
    found = [r for r in records if all(r[k] == v for k, v in where.items())]
    if len(found) != 1:
        raise WriteupError(f"expected one row matching {dict(where)}, found {len(found)}")
    return found[0]


def one(table: Table, where: Mapping[str, str]) -> Mapping[str, str]:
    return pick(table.records(), where)


def bare(cell: str) -> str:
    """A cell without its table marks (†, §, ‡)."""
    return cell.strip(MARKS)


def number(cell: str) -> Decimal | None:
    value = bare(cell)
    return None if value.startswith("n/a") else Decimal(value)


def interval(cell: str) -> tuple[Decimal, Decimal]:
    low, high = cell.strip("[]").split(",")
    return Decimal(low), Decimal(high)


def section(text: str, heading: str) -> str:
    """The text under a heading line, up to the next heading of any level."""
    lines = text.splitlines()
    if heading not in lines:
        raise WriteupError(f"no heading {heading!r}")
    start = lines.index(heading) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("#")), len(lines))
    return "\n".join(lines[start:end]).strip("\n")


def md_table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(lines + ["| " + " | ".join(row) + " |" for row in rows])


def _grid(dataset: str, scope: str = "r2") -> str:
    return f"results/{dataset}/{scope}-grid.md"


def _production_line(embedder: str) -> str:
    return f"Production line: hybrid, then the reranker over the fused top 30, {embedder}"


def _r2_rows(src: Sources, dataset: str, embedder: str, scope: str = "r2") -> list[dict[str, str]]:
    return find(
        src.tables(_grid(dataset, scope)), "Production view (top-N cap 8)", under=_production_line(embedder)
    ).records()


def _r2_cell(rows: list[dict[str, str]], chunking: str, budget: str, column: str) -> str:
    return bare(pick(rows, {"chunking": chunking, "budget": budget})[column])


# generated blocks: each renders markdown from the committed tables


def block_datasets(src: Sources) -> str:
    inputs = find(src.tables(R7), "Inputs", column="documents")
    names = {"qasper": "QASPER v0.3, dev + test", "nq": "Natural Questions, dev subset"}
    rows = []
    for dataset in ("qasper", "nq"):
        r = one(inputs, {"dataset": dataset})
        questions = find(src.tables(f"results/{dataset}/r1-tracer.md"), "Questions").records()
        excluded = [
            f"{q['n']} {q[''].removeprefix('excluded: ').replace('_', ' ')}"
            for q in questions
            if q[""].startswith("excluded:") and q["n"] != "0"
        ]
        rows.append(
            [names[dataset], r["documents"], r["questions"], r["precise"], r["context"], r["mixed"]]
            + [", ".join(excluded) or "none"]
        )
    return md_table(["dataset", "documents", "questions", "precise", "context", "mixed", "excluded"], rows)


def block_best_single(src: Sources) -> str:
    t = find(src.tables(R7), "Routing headroom")
    header = ["budget"] + [f"{NAMES[d]}, {v} view" for d in DATASETS for v in VIEWS]
    parts = []
    for embedder in EMBEDDERS:
        rows = []
        for budget in BUDGETS:
            row = [budget]
            for dataset in DATASETS:
                for view in VIEWS:
                    where = {"dataset": dataset, "pipeline": PRODUCTION_LINE, "embedder": embedder}
                    r = one(t, where | {"view": view, "budget": budget})
                    row.append(f"{r['best single chunking']} {r['best single recall']}")
            rows.append(row)
        parts.append(f"Production line, {embedder}:\n\n{md_table(header, rows)}")
    return "\n\n".join(parts)


def block_best_margins(src: Sources) -> str:
    t = find(src.tables(R7), "Each chunking against the best single chunking")
    rows = []
    for chunking in CHUNKINGS:
        row = [chunking]
        for embedder in EMBEDDERS:
            where = {"dataset": "pooled", "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
            r = one(t, where | {"budget": PRIMARY_BUDGET, "chunking": chunking})
            row += [r["mean recall"], f"{r['difference from best']} {r['CI']}", r["best in resamples"]]
        rows.append(row)
    header = ["chunking"] + [
        f"{e} {c}" for e in EMBEDDERS for c in ("recall", "difference from the best [95% CI]", "best in resamples")
    ]
    return md_table(header, rows)


def block_scope(src: Sources) -> str:
    rows_1024 = []
    rows_8192 = []
    collection = {d: _r2_rows(src, d, "bge-small") for d in ("qasper", "nq")}
    document = {d: _r2_rows(src, d, "bge-small", "r2w") for d in ("qasper", "nq")}
    for chunking in CHUNKINGS:
        rows_1024.append(
            [chunking]
            + [
                _r2_cell(rows[d], chunking, PRIMARY_BUDGET, "production recall")
                for d in ("qasper", "nq")
                for rows in (collection, document)
            ]
        )
        rows_8192.append(
            [chunking] + [_r2_cell(document[d], chunking, "8192", "fair recall") for d in ("qasper", "nq")]
        )
    header = ["chunking"] + [
        f"{NAMES[d]}, {s}" for d in ("qasper", "nq") for s in ("collection", "within the document")
    ]
    return (
        f"Production line, bge-small, production view, {PRIMARY_BUDGET} tokens:\n\n{md_table(header, rows_1024)}\n\n"
        f"Within the document, fair view, 8192 tokens:\n\n{md_table(['chunking', 'QASPER', 'NQ'], rows_8192)}"
    )


def block_pilot(src: Sources) -> str:
    measured = find(src.tables(PILOT_REPORT), "4. Local pilot", column="Contrast")
    interaction = one(measured, {"Contrast": "**Interaction** (multi − single) of (512 − 64)"})
    prior = find(src.tables(PILOT_REPORT), "5.6 Expected table", column="Interaction")
    fixed_512 = one(prior, {"Config @ B=1024": "fixed-512"})
    scope = "BM25, within the paper"
    pilot_contrast = "(512 − 64 words), multi − single paragraph"
    rows = [
        ["pilot, QASPER dev", scope, pilot_contrast, "512 words", interaction["dev"]],
        ["pilot, QASPER test", scope, pilot_contrast, "512 words", interaction["test"]],
        ["prior for v1 (report, section 5.6)", "BM25", "(fixed-512 − fixed-128), context − precise", "1024 tokens"]
        + [fixed_512["Interaction"]],
    ]
    return md_table(["source", "retrieval", "contrast", "budget", "interaction"], rows)


def block_interaction_h1(src: Sources) -> str:
    t = find(src.tables(R8), "Chunk size x query type interaction")
    rows = []
    for dataset in DATASETS:
        for pipeline, embedder in (("hybrid-rerank", "bge-small"), ("hybrid-rerank", "nomic"), ("bm25", "-")):
            for budget in ("512", PRIMARY_BUDGET):
                where = {"dataset": dataset, "pipeline": pipeline, "embedder": embedder, "view": "production"}
                r = one(t, where | {"budget": budget, "chunking": "fixed-512"})
                rows.append(
                    [NAMES[dataset], PIPELINE_LABELS[(pipeline, embedder)], budget]
                    + [r["Δ context"], r["Δ precise"], r["interaction"], r["CI"], r["CI level"]]
                )
    header = ["dataset", "pipeline", "budget", "Δ context", "Δ precise", "interaction", "CI", "CI level"]
    return md_table(header, rows)


def block_interaction_all(src: Sources) -> str:
    t = find(src.tables(R8), "Chunk size x query type interaction")
    rows = []
    for dataset in DATASETS:
        for chunking in CHUNKINGS:
            if chunking == "fixed-128":
                continue
            row = [NAMES[dataset], chunking]
            for embedder in EMBEDDERS:
                where = {"dataset": dataset, "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
                r = one(t, where | {"budget": PRIMARY_BUDGET, "chunking": chunking})
                if embedder == "bge-small":
                    row += [r["Δ context"], r["Δ precise"]]
                row.append(f"{r['interaction']} {r['CI']}")
            rows.append(row)
    header = ["dataset", "chunking", "bge-small Δ context", "bge-small Δ precise"]
    header += [f"{e} interaction [95% CI]" for e in EMBEDDERS]
    return md_table(header, rows)


def block_short_answer(src: Sources) -> str:
    rows = find(
        src.tables(_grid("nq", "r6")), "Short-answer span recall", under=_production_line("bge-small")
    ).records()
    budgets = ("128", "256", "512", PRIMARY_BUDGET)
    cells = {
        (c, b): bare(pick(rows, {"chunking": c, "budget": b})["production short recall"])
        for c in CHUNKINGS
        for b in budgets
    }
    best = {b: max(number(cells[c, b]) for c in CHUNKINGS if number(cells[c, b]) is not None) for b in budgets}
    table = [
        [c] + [f"**{cells[c, b]}**" if number(cells[c, b]) == best[b] else cells[c, b] for b in budgets]
        for c in CHUNKINGS
    ]
    return md_table(["chunking"] + [f"{b} tokens" for b in budgets], table)


def block_query_type_oracle(src: Sources) -> str:
    t = find(src.tables(R7), "Query-type oracle")
    rows = []
    for dataset in DATASETS:
        for embedder in EMBEDDERS:
            where = {"dataset": dataset, "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
            r = one(t, where | {"budget": PRIMARY_BUDGET})
            rows.append(
                [NAMES[dataset], embedder, r["precise pick"], r["context pick"], r["mixed pick"]]
                + [r["query-type oracle recall"], f"{r['gain over best single']} {r['CI']}"]
                + [f"{r['oracle router minus query-type oracle']} {r['CI (2)']}"]
            )
    header = ["dataset", "embedder", "precise pick", "context pick", "mixed pick", "query-type oracle recall"]
    header += ["gain over the best single chunking [95% CI]", "oracle router minus query-type oracle [95% CI]"]
    return md_table(header, rows)


def _headroom_row(r: dict[str, str]) -> list[str]:
    return [r["best single chunking"], r["best single recall"], r["oracle router recall"]] + [
        r["routing headroom"],
        r["CI"],
        r["CI level"],
    ]


def block_headroom(src: Sources) -> str:
    t = find(src.tables(R7), "Routing headroom")
    rows = []
    for budget in BUDGETS:
        for embedder in EMBEDDERS:
            where = {"dataset": "pooled", "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
            rows.append(["pooled", budget, embedder] + _headroom_row(one(t, where | {"budget": budget})))
    for dataset in ("qasper", "nq"):
        for embedder in EMBEDDERS:
            where = {"dataset": dataset, "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
            rows.append([NAMES[dataset], PRIMARY_BUDGET, embedder] + _headroom_row(one(t, where | {"budget": "1024"})))
    header = ["dataset", "budget", "embedder", "best single chunking", "best single recall", "oracle router recall"]
    return md_table(header + ["routing headroom", "CI", "CI level"], rows)


def block_gate(src: Sources) -> str:
    """R7's gate rule and verdict, verbatim (one sentence per embedder), with
    a blank line before the verdict so it renders as its own paragraph."""
    return section(src.text(R7), "## Router gate (pre-registered)").replace("\n**Verdict", "\n\n**Verdict")


def block_gate_pipelines(src: Sources) -> str:
    t = find(src.tables(R7), "The same test on the other pipelines")
    return md_table(t.header, t.rows)


def block_oracle_picks(src: Sources) -> str:
    where = {"dataset": "pooled", "pipeline": PRODUCTION_LINE, "embedder": "bge-small", "view": "production"}
    where |= {"budget": PRIMARY_BUDGET}
    differ = find(src.tables(R9), "The same, among the questions where the chunkings differ")
    picks = [
        [c] + [one(differ, where | {"chunking": c})[k] for k in ("precise", "context", "mixed", "all")]
        for c in CHUNKINGS
    ]
    every = find(src.tables(R9), "The oracle router's chunking per query type")
    tied = [
        [NAMES[d]]
        + [
            one(every, where | {"dataset": d, "chunking": "every chunking tied"})[k]
            for k in ("precise", "context", "mixed", "all")
        ]
        for d in DATASETS
    ]
    header = ["precise", "context", "mixed", "all"]
    return (
        "Questions on which every chunking scores the same (production line, bge-small, "
        f"{PRIMARY_BUDGET} tokens; share and count):\n\n{md_table(['dataset'] + header, tied)}\n\n"
        "The oracle router's pick among the other questions, pooled:\n\n"
        f"{md_table(['chunking'] + header, picks)}"
    )


def block_ablations(src: Sources) -> str:
    t = find(src.tables(R7), "Routing headroom")
    best: dict[tuple[str, str, str], dict[str, str]] = {}
    rows = []
    for (pipeline, embedder), label in PIPELINE_LABELS.items():
        row = [label]
        for dataset in DATASETS:
            where = {"dataset": dataset, "pipeline": pipeline, "embedder": embedder, "view": "production"}
            r = best[pipeline, embedder, dataset] = one(t, where | {"budget": PRIMARY_BUDGET})
            row.append(f"{r['best single chunking']} {r['best single recall']}")
        rows.append(row)

    def recall(pipeline: str, embedder: str, dataset: str) -> Decimal:
        return Decimal(best[pipeline, embedder, dataset]["best single recall"])

    contrasts = (
        ("the reranker: production line − hybrid", "hybrid-rerank", "hybrid", False),
        ("fusion: hybrid − vector only", "hybrid", "vector", False),
        ("fusion: hybrid − BM25 only", "hybrid", "bm25", True),
        ("the whole line: production line − vector only", "hybrid-rerank", "vector", False),
    )
    diffs = []
    for label, a, b, b_is_bm25 in contrasts:
        for embedder in EMBEDDERS:
            values = [recall(a, embedder, d) - recall(b, "-" if b_is_bm25 else embedder, d) for d in DATASETS]
            diffs.append([label, embedder] + [f"{v:+.4f}" for v in values])
    header = [NAMES[d] for d in DATASETS]
    return (
        f"Best single chunking and its recall, production view, {PRIMARY_BUDGET} tokens:\n\n"
        f"{md_table(['pipeline'] + header, rows)}\n\n"
        "Differences between those recalls (no CI is computed for them):\n\n"
        f"{md_table(['what is added', 'embedder'] + header, diffs)}"
    )


def _r5_rows(src: Sources, dataset: str) -> list[dict[str, str]]:
    return select(
        find(src.tables(_grid(dataset, "r5")), f"Budget {PRIMARY_BUDGET} tokens"), {"pipeline": PRODUCTION_LINE}
    )


def block_truncation(src: Sources) -> str:
    rows = []
    for dataset in ("qasper", "nq"):
        r5 = _r5_rows(src, dataset)
        for chunking in ("fixed-512", "fixed-1024", "section-aware"):
            bge, nomic = (pick(r5, {"embedder": e, "chunking": chunking}) for e in EMBEDDERS)
            bge_recall, nomic_recall = bare(bge["production recall"]), bare(nomic["production recall"])
            difference = Decimal(nomic_recall) - Decimal(bge_recall)
            rows.append(
                [
                    NAMES[dataset],
                    chunking,
                    bare(bge["truncated chunks"]),
                    bge_recall,
                    nomic_recall,
                    f"{difference:+.4f}",
                ]
            )
    header = ["dataset", "chunking", "chunks truncated by bge-small", "recall, bge-small", "recall, nomic"]
    return f"Production line, production view, {PRIMARY_BUDGET} tokens:\n\n{md_table(header + ['nomic − bge-small'], rows)}"


def block_tail(src: Sources) -> str:
    rows = []
    for dataset in ("qasper", "nq"):
        r5 = _r5_rows(src, dataset)
        for chunking in CHUNKINGS:
            shares = [pick(r5, {"embedder": e, "chunking": chunking})["tail used, production view"] for e in EMBEDDERS]
            rows.append([NAMES[dataset], chunking] + shares)
    header = ["dataset", "chunking"] + [f"questions using the tail, {e}" for e in EMBEDDERS]
    return f"Production line, production view, {PRIMARY_BUDGET} tokens:\n\n{md_table(header, rows)}"


def block_models(src: Sources) -> str:
    rows = find(src.tables(_grid("qasper")), "Models").records()
    table = [[r["role"], r["model"], r["revision"], r["input limit"], LICENCES[r["model"]]] for r in rows]
    return md_table(["role", "model", "revision", "input limit", "licence"], table)


BLOCKS: dict[str, Callable[[Sources], str]] = {
    "datasets": block_datasets,
    "best-single": block_best_single,
    "best-margins": block_best_margins,
    "scope": block_scope,
    "pilot": block_pilot,
    "interaction-h1": block_interaction_h1,
    "interaction-all": block_interaction_all,
    "short-answer": block_short_answer,
    "query-type-oracle": block_query_type_oracle,
    "gate": block_gate,
    "headroom": block_headroom,
    "gate-pipelines": block_gate_pipelines,
    "oracle-picks": block_oracle_picks,
    "ablations": block_ablations,
    "truncation": block_truncation,
    "tail": block_tail,
    "models": block_models,
}


# figures


def _chunking_colors() -> dict[str, str]:
    fixed = [c for c in CHUNKINGS if c.startswith("fixed-")]
    return dict(zip(fixed, figures.FIXED_RAMP)) | {"section-aware": figures.ORANGE, "small-to-big": figures.AQUA}


def figure_recall_vs_budget(src: Sources) -> str:
    colors = _chunking_colors()
    panels = []
    for view in VIEWS:
        for dataset, y_max, y_step in (("qasper", 0.4, 0.1), ("nq", 1.0, 0.2)):
            rows = _r2_rows(src, dataset, "bge-small")
            series = tuple(
                Series(
                    chunking,
                    colors[chunking],
                    tuple(
                        None if (v := number(_r2_cell(rows, chunking, b, f"{view} recall"))) is None else float(v)
                        for b in BUDGETS
                    ),
                )
                for chunking in CHUNKINGS
            )
            panels.append(Panel(f"{NAMES[dataset]}, {view} view", y_max, y_step, series))
    return figures.line_panels(
        title="Retrieval recall by token budget, per chunking",
        subtitle="Production line with bge-small, collection search; mean retrieval recall (y) per budget in tokens (x)",
        description="Four panels: QASPER and NQ, production view (top 8 chunks) and fair view (no cap). "
        "Values from results/qasper/r2-grid.md and results/nq/r2-grid.md.",
        x_labels=BUDGETS,
        x_title="token budget",
        panels=panels,
        columns=2,
    )


def figure_headroom(src: Sources) -> str:
    t = find(src.tables(R7), "Routing headroom")
    series = []
    for embedder, color in zip(EMBEDDERS, (figures.BLUE, figures.ORANGE)):
        points = []
        for budget in BUDGETS:
            where = {"dataset": "pooled", "pipeline": PRODUCTION_LINE, "embedder": embedder, "view": "production"}
            r = one(t, where | {"budget": budget})
            low, high = interval(r["CI"])
            points.append((float(r["routing headroom"]), float(low), float(high)))
        series.append(Whiskers(embedder, color, tuple(points)))
    return figures.dot_whiskers(
        title="Routing headroom over the best single chunking",
        subtitle="Production line, production view, QASPER + NQ pooled; 95% CI at 1024 tokens, Holm-adjusted elsewhere",
        description="Oracle router recall minus best single chunking recall per budget, both embedders, with CIs. "
        "Values from results/routing/r7-headroom.md.",
        x_labels=BUDGETS,
        x_title="token budget",
        series=series,
        y_step=0.05,
        references=[(GATE_THRESHOLD, "gate threshold +0.05")],
        highlight=(BUDGETS.index(PRIMARY_BUDGET), "pre-registered budget"),
    )


def figure_interaction(src: Sources) -> str:
    t = find(src.tables(R8), "Chunk size x query type interaction")
    chunkings = [c for c in CHUNKINGS if c != "fixed-128"]
    series = []
    for dataset, color in (("qasper", figures.BLUE), ("nq", figures.ORANGE)):
        points = []
        for chunking in chunkings:
            where = {"dataset": dataset, "pipeline": PRODUCTION_LINE, "embedder": "bge-small", "view": "production"}
            r = one(t, where | {"budget": PRIMARY_BUDGET, "chunking": chunking})
            low, high = interval(r["CI"])
            points.append((float(r["interaction"]), float(low), float(high)))
        series.append(Whiskers(NAMES[dataset], color, tuple(points)))
    return figures.dot_whiskers(
        title="Chunk size × query type interaction at 1024 tokens",
        subtitle="Each chunking against fixed-128: (Δ on context questions) − (Δ on precise questions), with 95% CI; "
        "production line, bge-small",
        description="Above 0, a chunking gains more over fixed-128 on context questions than on precise ones. "
        "Values from results/routing/r8-headroom.md.",
        x_labels=chunkings,
        x_title="chunking (reference: fixed-128)",
        series=series,
        y_step=0.05,
    )


FIGURES: dict[str, Callable[[Sources], str]] = {
    "v1-recall-vs-budget.svg": figure_recall_vs_budget,
    "v1-routing-headroom.svg": figure_headroom,
    "v1-interaction.svg": figure_interaction,
}


# regeneration and the drift check


@dataclass(frozen=True)
class Writeup:
    """One write-up: its file, its generated blocks, its figures under
    chunking/figures/, and the numbers in its prose that must come from a block."""

    path: str
    blocks: Mapping[str, Callable[[Sources], str]]
    figures: Mapping[str, Callable[[Sources], str]]
    numbers: re.Pattern[str] = NUMBER


V1 = Writeup(WRITEUP, BLOCKS, FIGURES)


def writeups() -> tuple[Writeup, ...]:
    """Every write-up `rag writeup` regenerates and checks, oldest first."""
    from .writeup_v2 import V2  # v2's blocks build on this module's readers

    return (V1, V2)


def apply_blocks(text: str, blocks: Mapping[str, str]) -> str:
    """Replace the body of every generated block; every block must appear exactly once."""
    seen: list[str] = []

    def replace(match: re.Match[str]) -> str:
        name = match["name"]
        if name not in blocks:
            raise WriteupError(f"the write-up has an unknown generated block {name!r}")
        seen.append(name)
        return f"{match['open']}{blocks[name]}\n{match['close']}"

    rendered = BLOCK.sub(replace, text)
    missing = sorted(set(blocks) - set(seen))
    repeated = sorted({name for name in seen if seen.count(name) > 1})
    if missing or repeated:
        raise WriteupError(f"generated blocks missing: {missing}; repeated: {repeated}")
    return rendered


def unsourced_numbers(text: str, pattern: re.Pattern[str] = NUMBER) -> list[str]:
    """Numbers in the prose matching `pattern` (by default four-decimal ones)
    that appear as a number in no generated block (a leading + is ignored;
    a minus sign must match)."""
    sourced = {n.removeprefix("+") for m in BLOCK.finditer(text) for n in DECIMAL.findall(m["body"])}
    prose = BLOCK.sub("", text)
    return sorted({n for n in pattern.findall(prose) if n.removeprefix("+") not in sourced})


def render(src: Sources, doc: Writeup) -> tuple[str, dict[str, str]]:
    """The write-up with every block re-rendered, and each figure's SVG."""
    rendered = apply_blocks(src.text(doc.path), {name: block(src) for name, block in doc.blocks.items()})
    return rendered, {name: figure(src) for name, figure in doc.figures.items()}


def check(root: Path) -> list[str]:
    """Every way the committed write-ups and figures differ from the tables."""
    src = Sources(root)
    problems = []
    for doc in writeups():
        rendered, svgs = render(src, doc)
        bodies = {m["name"]: m["body"] for m in BLOCK.finditer(src.text(doc.path))}
        problems += [
            f"{doc.path}: block {m['name']!r} differs from the tables"
            for m in BLOCK.finditer(rendered)
            if bodies.get(m["name"]) != m["body"]
        ]
        for name, svg in svgs.items():
            path = root / FIGURE_DIR / name
            if not path.exists() or path.read_text(encoding="utf-8") != svg:
                problems.append(f"{FIGURE_DIR}/{name}: differs from the tables")
        problems += [
            f"{doc.path}: {n} appears in the prose but in no generated block"
            for n in unsourced_numbers(rendered, doc.numbers)
        ]
    return problems


def write(root: Path) -> list[str]:
    """Re-render every write-up's blocks and figures in place; returns the files that changed."""
    src = Sources(root)
    outputs: dict[str, str] = {}
    for doc in writeups():
        rendered, svgs = render(src, doc)
        outputs |= {doc.path: rendered} | {f"{FIGURE_DIR}/{name}": svg for name, svg in svgs.items()}
    changed = []
    for relative, content in outputs.items():
        path = root / relative
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        changed.append(relative)
    return changed
