"""The v2 write-up's generated blocks and figures, read from the committed
v2 tables: the budget-view oracle ceiling (R7) next to v1's, each
contender's retrieval result (R11-R13, R17), the verdict, the secondary
results and the adoption profile (R16), the answer scores (R14), the
grader check (R15) and the context-prefix manifest. Like v1's, nothing
is computed beyond reading a cell: every difference and interval is the
one its table reports.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable

from . import figures
from .figures import Point, ScatterPanel, Whiskers
from .writeup import (
    BUDGETS,
    LICENCES,
    NAMES,
    NUMBER,
    PRIMARY_BUDGET,
    R7,
    Sources,
    Writeup,
    WriteupError,
    find,
    interval,
    md_table,
    number,
    one,
    section,
)

WRITEUP = "chunking/2026-10-18-v2-results.md"
R7_V2 = "results/routing/r7-v2-budget-view.md"
R11 = "results/pooled/r11-v2-routers.md"
R14 = "results/v2/r14-answers.md"
R15 = "results/v2/r15-grader.md"
R16 = "results/v2/r16-verdict.md"
PREFIXES = "results/prefixes/fixed-256-qwen3-8b.json"
LATE_COSINE = "results/late-single-chunk-cosine.md"
MODELS = "results/qasper/r2-v2-baseline.md"

# a contender's own table: the routers' pooled R11, or an indexing table's
# per-dataset files (each also carrying the pooled columns)
OWN = {"R12": "r12-v2-late", "R13": "r13-v2-contextual", "R17": "r17-v2-titles"}
REFERENCES = (
    ("R12", "late-128 - fixed-128"),
    ("R12", "late-256 - fixed-256"),
    ("R13", "contextual-256 - fixed-256"),
    ("R13", "contextual-256-prefixed - contextual-256"),
    ("R17", "section-aware-titles - section-aware"),
)
SETUPS = {"no-retrieval": "no retrieval", "section-aware": "section-aware", "oracle": "oracle router"}
BAR = 0.02
DATASET_FLOOR = -0.01
V2_LICENCES = LICENCES | {"mlx-community/Qwen3-8B-4bit": "Apache-2.0"}

# v2's prose also quotes shares and times, which must come from a block too
NUMBER_V2 = re.compile(rf"{NUMBER.pattern}|(?<![\d.])[+-]?\d+\.\d+(?=%| ms\b| s\b| h\b)")
PER_DATASET = re.compile(
    r"^- (?P<name>.+?): qasper (?P<qasper>\S+) (?P<qasper_ci>\[[^]]+\]), nq (?P<nq>\S+) (?P<nq_ci>\[[^]]+\])$",
    re.MULTILINE,
)
LATE_WINDOWS = re.compile(
    r"^- (?P<dataset>\w+): late chunking reads every document whole, (?P<windows>\d+) windows", re.MULTILINE
)
MODEL_LINE = re.compile(r"^- (?P<role>reader|grader): `(?P<model>[^`@]+)(?:@(?P<revision>[0-9a-f]+))?`", re.MULTILINE)


def _contenders(src: Sources) -> list[dict[str, str]]:
    return find(src.tables(R16), "Contenders against section-aware").records()


def _per_dataset(src: Sources) -> dict[str, dict[str, str]]:
    """Each contender's per-dataset differences and intervals, from R16's list."""
    text = section(src.text(R16), "## Contenders against section-aware")
    found = {m["name"]: m.groupdict() for m in PER_DATASET.finditer(text)}
    if not found:
        raise WriteupError(f"{R16}: no per-dataset intervals")
    return found


def _r7_reproduced(src: Sources, group: str) -> dict[str, str]:
    return dict(one(find(src.tables(R16), "R7 reproduced at the bar's cell"), {"group": group}))


def _own_recall(src: Sources, table: str, contender: str) -> str:
    """The contender's pooled recall at the bar's cell, from its own table."""
    if table == "R11":
        t = find(src.tables(R11), "Retrieval, budget view")
        return one(t, {"dataset": "pooled", "budget": PRIMARY_BUDGET, "system": contender})["recall"]
    t = find(src.tables(f"results/qasper/{OWN[table]}.md"), "Budget view (top-N cap 20)")
    return one(t, {"chunking": contender, "budget": PRIMARY_BUDGET})["pooled recall"]


def _r7_v2(src: Sources, heading: str, where: dict[str, str]) -> dict[str, str]:
    where = {"pipeline": "hybrid-rerank", "embedder": "nomic", "view": "budget"} | where
    return dict(one(find(src.tables(R7_V2), heading), where))


# generated blocks


def block_ceiling(src: Sources) -> str:
    v2 = find(src.tables(R7_V2), "Routing headroom")
    v1 = find(src.tables(R7), "Routing headroom")
    groups = [("pooled", b) for b in BUDGETS]
    groups += [("qasper", PRIMARY_BUDGET), ("nq", PRIMARY_BUDGET)]
    rows = []
    for dataset, budget in groups:
        where = {"dataset": dataset, "pipeline": "hybrid-rerank", "embedder": "nomic", "budget": budget}
        new = one(v2, where | {"view": "budget"})
        old = one(v1, where | {"view": "production"})
        row = [NAMES[dataset], budget]
        for r in (new, old):
            row += [f"{r['best single chunking']} {r['best single recall']}", r["oracle router recall"]]
            row.append(f"{r['routing headroom']} {r['CI']}")
        rows.append(row + [new["CI level"]])
    header = ["dataset", "budget"]
    for label in ("v2, budget view", "v1, production view"):
        header += [f"{label}: best single chunking", f"{label}: oracle router", f"{label}: routing headroom [CI]"]
    return f"Production line, nomic, collection search:\n\n{md_table(header + ['CI level'], rows)}"


def block_contenders(src: Sources) -> str:
    intervals = _per_dataset(src)
    reference = _r7_reproduced(src, "pooled")
    rows = [["section-aware (the reference)", "R7", reference["section-aware recall"], "-", "-", "-", "-"]]
    for r in _contenders(src):
        d = intervals[r["contender"]]
        rows.append(
            [r["contender"], r["own table"], _own_recall(src, r["own table"], r["contender"])]
            + [f"{r['pooled difference']} {r['CI']}", f"{d['qasper']} {d['qasper_ci']}", f"{d['nq']} {d['nq_ci']}"]
            + [r["share of oracle captured"]]
        )
    by_dataset = {d: _r7_reproduced(src, d) for d in ("qasper", "nq")}
    rows.append(
        ["oracle router (the ceiling)", "R7", reference["oracle router recall"]]
        + [f"{reference['routing headroom']} {reference['CI']}"]
        + [f"{by_dataset[d]['routing headroom']} {by_dataset[d]['CI']}" for d in ("qasper", "nq")]
        + ["(the ceiling)"]
    )
    header = ["setup", "table", "pooled recall", "pooled difference from section-aware [95% CI]"]
    header += ["QASPER difference [95% CI]", "NQ difference [95% CI]", "share of the oracle ceiling captured"]
    return (
        f"Budget view (top-N cap 20), {PRIMARY_BUDGET} tokens, production line, nomic, collection search:\n\n"
        f"{md_table(header, rows)}"
    )


def block_own_reference(src: Sources) -> str:
    rows = []
    for table, pair in REFERENCES:
        cells = {}
        for dataset in ("qasper", "nq"):
            t = find(src.tables(f"results/{dataset}/{OWN[table]}.md"), "Contender minus reference")
            r = one(t, {"contender - reference": pair, "view": "budget", "budget": PRIMARY_BUDGET})
            cells[dataset], cells["pooled"] = r[f"{dataset} recall"], r["pooled recall"]
        rows.append([pair, table] + [cells[d] for d in ("qasper", "nq", "pooled")])
    header = ["contender - its own chunking", "table", "QASPER", "NQ", "pooled"]
    return f"Recall difference, budget view, {PRIMARY_BUDGET} tokens (no CI is computed for these):\n\n{md_table(header, rows)}"


def block_confidence_picks(src: Sources) -> str:
    t = find(src.tables(R11), "Confidence routing's chunking picks")
    return md_table(t.header, t.rows)


def block_verdict(src: Sources) -> str:
    return section(src.text(R16), "## Verdict")


def block_bar(src: Sources) -> str:
    columns = ("contender", "pooled difference", "CI", "gain", "datasets", "answers", "tie-break")
    return md_table(columns, [[r[c] for c in columns] for r in _contenders(src)])


def block_budgets(src: Sources) -> str:
    other = find(src.tables(R16), "Other budgets, budget view")
    production = find(src.tables(R16), f"Production view (top-N cap 8), {PRIMARY_BUDGET} tokens")
    return (
        "Pooled recall difference from section-aware in the budget view at other budgets "
        f"(the level column gives each interval's level):\n\n{md_table(other.header, other.rows)}\n\n"
        f"The same at {PRIMARY_BUDGET} tokens in v1's production view (top-N cap 8):\n\n"
        f"{md_table(production.header, production.rows)}"
    )


def block_depth50(src: Sources) -> str:
    return section(src.text(R16), "### Depth-50 side run")


def block_answers(src: Sources) -> str:
    scores = find(src.tables(R14), "Answer score per setup and dataset")
    by_type = find(src.tables(R14), "Natural Questions by query type")
    return (
        f"{md_table(scores.header, scores.rows)}\n\n"
        "Natural Questions by query type (point estimates; precise questions also scored by contains-a-reference):\n\n"
        f"{md_table(by_type.header, by_type.rows)}"
    )


def block_grader(src: Sources) -> str:
    text = src.text(R15)
    ranking = find(src.tables(R15), "Does the setup ranking hold under the grader?")
    return (
        f"{section(text, '## Agreement per dataset')}\n\n{section(text, '## Per setup')}\n\n"
        f"Does the setup ranking hold under the grader?\n\n{md_table(ranking.header, ranking.rows)}"
    )


def block_latency(src: Sources) -> str:
    return section(src.text(R16), "### Query path, uncached")


def _bullets(text: str, heading: str) -> str:
    return "\n".join(line for line in section(text, heading).splitlines() if line.startswith("- "))


def block_costs(src: Sources) -> str:
    text = src.text(R16)
    return (
        f"Index-time cost:\n\n{_bullets(text, '### Index-time cost')}\n\n"
        f"Reader cost per question:\n\n{_bullets(text, '### Reader cost per question')}"
    )


def block_windows(src: Sources) -> str:
    manifest = json.loads(src.text(PREFIXES))
    windows = {m["dataset"]: m["windows"] for m in LATE_WINDOWS.finditer(section(src.text(R16), "### Index-time cost"))}
    rows = []
    for dataset in ("qasper", "nq"):
        d = manifest["datasets"][dataset]
        rows.append([NAMES[dataset], str(d["documents"]), str(d["documents_in_windows"]), str(d["truncated"])])
        rows[-1].append(windows[dataset])
    context, cut = manifest["config"]["context_tokens"], manifest["config"]["max_new_tokens"]
    header = ["dataset", "documents", f"prefix model: documents read in windows of at most {context} tokens"]
    header += [f"prefixes cut at {cut} tokens", "late chunking: windows of at most 8192 nomic tokens"]
    cosine = find(src.tables(LATE_COSINE), "The late-chunking single-chunk check")
    return (
        f"{md_table(header, rows)}\n\n"
        f"Late chunking's single-chunk check against the real model:\n\n{md_table(cosine.header, cosine.rows)}"
    )


def block_models(src: Sources) -> str:
    rows = [
        [r["role"], r["model"], r["revision"], V2_LICENCES[r["model"]]]
        for r in find(src.tables(MODELS), "Models").records()
    ]
    manifest = json.loads(src.text(PREFIXES))["config"]["model"]
    rows.append(["context prefixes", manifest["id"], f"`{manifest['revision']}`", V2_LICENCES[manifest["id"]]])
    lines = {m["role"]: m for m in MODEL_LINE.finditer(section(src.text(R14), "## Inputs"))}
    lines |= {m["role"]: m for m in MODEL_LINE.finditer(section(src.text(R15), "## Inputs"))}
    reader, grader = lines["reader"], lines["grader"]
    rows.append(["reader", reader["model"], f"`{reader['revision']}`", V2_LICENCES[reader["model"]]])
    rows.append(["grader (the check only)", grader["model"], "n/a (a hosted model)", "proprietary (Anthropic)"])
    return md_table(["role", "model", "revision", "licence"], rows)


BLOCKS: dict[str, Callable[[Sources], str]] = {
    "v2-ceiling": block_ceiling,
    "v2-contenders": block_contenders,
    "v2-own-reference": block_own_reference,
    "v2-confidence-picks": block_confidence_picks,
    "v2-verdict": block_verdict,
    "v2-bar": block_bar,
    "v2-budgets": block_budgets,
    "v2-depth50": block_depth50,
    "v2-answers": block_answers,
    "v2-grader": block_grader,
    "v2-latency": block_latency,
    "v2-costs": block_costs,
    "v2-windows": block_windows,
    "v2-models": block_models,
}


# figures


def figure_contenders(src: Sources) -> str:
    rows = _contenders(src)
    intervals = _per_dataset(src)

    def whiskers(estimate: str, ci: str) -> tuple[float, float, float]:
        low, high = interval(ci)
        return float(number(estimate)), float(low), float(high)

    series = [Whiskers("pooled", figures.BLUE, tuple(whiskers(r["pooled difference"], r["CI"]) for r in rows))]
    for dataset, color in (("qasper", figures.ORANGE), ("nq", figures.AQUA)):
        points = tuple(
            whiskers(intervals[r["contender"]][dataset], intervals[r["contender"]][f"{dataset}_ci"]) for r in rows
        )
        series.append(Whiskers(NAMES[dataset], color, points))
    return figures.dot_whiskers(
        title="Each contender's retrieval recall against section-aware",
        subtitle="Recall difference from section-aware with 95% CI; budget view, 1024 tokens, production line, nomic",
        description="Pooled, QASPER and NQ differences per contender, in the pre-registered tie-break order, with the "
        "+0.02 pooled bar and the -0.01 per-dataset floor. Values from results/v2/r16-verdict.md.",
        x_labels=[r["contender"] for r in rows],
        x_title="contender (pre-registered order, simplest first; section-aware-titles joined last)",
        series=series,
        y_step=0.02,
        references=[(BAR, "bar: +0.02 pooled"), (DATASET_FLOOR, "floor: -0.01 per dataset")],
    )


def figure_answers(src: Sources) -> str:
    scores = find(src.tables(R14), "Answer score per setup and dataset")
    colors = {"no-retrieval": figures.INK_2, "section-aware": figures.ORANGE, "oracle": figures.BLUE}
    panels = []
    for dataset in ("qasper", "nq", "pooled"):
        recall = {
            "no-retrieval": 0.0,
            "section-aware": float(
                _r7_v2(
                    src,
                    "Each chunking against",
                    {"dataset": dataset, "budget": PRIMARY_BUDGET, "chunking": "section-aware"},
                )["mean recall"]
            ),
            "oracle": float(
                _r7_v2(src, "Routing headroom", {"dataset": dataset, "budget": PRIMARY_BUDGET})["oracle router recall"]
            ),
        }
        points = []
        for setup, label in SETUPS.items():
            r = one(scores, {"dataset": dataset, "setup": setup})
            low, high = interval(r["CI"])
            points.append(Point(label, colors[setup], recall[setup], float(r["answer score"]), float(low), float(high)))
        panels.append(ScatterPanel(NAMES[dataset], tuple(points)))
    return figures.scatter_panels(
        title="Answer score against retrieval recall, per read setup",
        subtitle="Mean answer score (y, 95% CI) on the 1,000-question reader sample against retrieval recall (x) "
        "at 1024 tokens, budget view",
        description="The three setups the reader read: no retrieval (recall 0), section-aware and the oracle router. "
        "Recall is over every question (results/routing/r7-v2-budget-view.md), the answer score over the reader "
        "sample (results/v2/r14-answers.md).",
        x_title="retrieval recall",
        y_title="answer score",
        x_max=1.0,
        x_step=0.2,
        y_max=0.3,
        y_step=0.05,
        panels=panels,
        columns=3,
    )


FIGURES: dict[str, Callable[[Sources], str]] = {
    "v2-contender-recall.svg": figure_contenders,
    "v2-answer-vs-recall.svg": figure_answers,
}

V2 = Writeup(WRITEUP, BLOCKS, FIGURES, NUMBER_V2)
