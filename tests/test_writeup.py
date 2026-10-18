"""The write-up regenerator: markdown tables read under their headings,
generated blocks replaced in place, prose numbers traced to a generated
block, deterministic SVG figures, and the committed v1 and v2 write-ups in
sync with the committed result tables."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from rag import figures
from rag.cli import main
from rag.writeup import (
    WriteupError,
    apply_blocks,
    check,
    find,
    interval,
    number,
    one,
    parse_tables,
    section,
    unsourced_numbers,
)
from rag.writeup_v2 import NUMBER_V2

REPO = Path(__file__).resolve().parents[1]

DOC = """# R7 - title

```yaml
# a comment inside a fence, not a heading
budgets: [128]
```

## Inputs

| run | hash |
|---|---|
| qasper/grid | `abc` |

| dataset | documents |
|---|---|
| qasper | 684 |

## Routing headroom

### Block, bge-small

| dataset | budget | CI | value | CI |
|---|---|---|---|---|
| pooled | 1024 | [+0.1187, +0.1402] | 0.4256§ | [-0.0010, +0.0020] |
| nq | 1024 | [+0.1145, +0.1551] | n/a | [+0.0000, +0.0000] |
"""


def test_tables_keep_their_headings_and_ignore_fenced_comments():
    tables = parse_tables(DOC)
    assert [t.headings for t in tables] == [
        ("R7 - title", "Inputs"),
        ("R7 - title", "Inputs"),
        ("R7 - title", "Routing headroom", "Block, bge-small"),
    ]
    assert tables[0].rows == (("qasper/grid", "`abc`"),)


def test_find_picks_one_table_by_heading_parent_and_column():
    tables = parse_tables(DOC)
    assert find(tables, "Inputs", column="documents").rows == (("qasper", "684"),)
    assert find(tables, "Block", under="Routing headroom").header[0] == "dataset"
    with pytest.raises(WriteupError):
        find(tables, "Inputs")  # two tables under it
    with pytest.raises(WriteupError):
        find(tables, "Missing")


def test_repeated_columns_and_cell_values():
    table = find(parse_tables(DOC), "Block")
    row = one(table, {"dataset": "pooled"})
    assert row["CI"] == "[+0.1187, +0.1402]"
    assert row["CI (2)"] == "[-0.0010, +0.0020]"
    assert str(number(row["value"])) == "0.4256"
    assert number(one(table, {"dataset": "nq"})["value"]) is None
    assert [str(v) for v in interval(row["CI (2)"])] == ["-0.0010", "0.0020"]
    with pytest.raises(WriteupError):
        one(table, {"budget": "1024"})


def _doc(*names: str, body: str = "") -> str:
    return "\n".join(f"<!-- generated: {n} -->\n{body}<!-- end generated: {n} -->" for n in names)


def test_blocks_are_replaced_in_place_and_must_all_appear_once():
    text = "intro\n" + _doc("a", "b", body="stale\n") + "\noutro\n"
    rendered = apply_blocks(text, {"a": "fresh a", "b": "fresh b"})
    assert rendered == "intro\n" + _doc("a", body="fresh a\n") + "\n" + _doc("b", body="fresh b\n") + "\noutro\n"
    assert apply_blocks(rendered, {"a": "fresh a", "b": "fresh b"}) == rendered
    with pytest.raises(WriteupError):
        apply_blocks(_doc("a"), {"a": "x", "b": "y"})  # b missing
    with pytest.raises(WriteupError):
        apply_blocks(_doc("a", "a"), {"a": "x"})  # a repeated
    with pytest.raises(WriteupError):
        apply_blocks(_doc("a", "c"), {"a": "x"})  # c unknown


def test_prose_numbers_must_come_from_a_generated_block():
    text = _doc("t", body="| +0.1295 | -0.0174 | 0.4256 |\n")
    assert unsourced_numbers(text + "\nheadroom 0.1295, best 0.4256, gap -0.0174, 2,197 questions, 0.05 bar") == []
    assert unsourced_numbers(text + "\na gap of 0.0174 and a recall of 0.4257.") == ["0.0174", "0.4257"]


def test_v2_prose_also_traces_shares_and_times_to_a_block():
    text = _doc("t", body="| -18.2% | 843.8 / 787.2 | 3.52 s | 30.4 h | +0.0228 |\n")
    prose = "\nshares -18.2%, 843.8 ms and 3.52 s per answer, 30.4 h, a gain of 0.0228, 8192 tokens, 1,000 questions"
    assert unsourced_numbers(text + prose, NUMBER_V2) == []
    assert unsourced_numbers(text + "\n18.2% captured, 787.3 ms, 1.5 h", NUMBER_V2) == ["1.5", "18.2", "787.3"]
    assert unsourced_numbers(text + "\n18.2% captured, 787.3 ms") == []  # v1 checks four-decimal numbers only


def test_section_reads_the_text_under_a_heading():
    text = "# T\n\n## Verdict\n\n**Verdict: x.**\n\nWhy.\n\n### Next\n\nmore\n"
    assert section(text, "## Verdict") == "**Verdict: x.**\n\nWhy."
    assert section(text, "### Next") == "more"
    with pytest.raises(WriteupError):
        section(text, "## Missing")


def test_figures_are_deterministic_well_formed_svg():
    panel = figures.Panel(
        "QASPER, production view",
        0.4,
        0.1,
        (
            figures.Series("fixed-512", figures.FIXED_RAMP[3], (None, 0.1, 0.3)),
            figures.Series("section-aware", figures.ORANGE, (0.03, 0.2, 0.31)),
        ),
    )
    lines = figures.line_panels("t", "s", "d", ("128", "256", "512"), "token budget", [panel], columns=1)
    assert lines == figures.line_panels("t", "s", "d", ("128", "256", "512"), "token budget", [panel], columns=1)
    root = ET.fromstring(lines)
    ns = "{http://www.w3.org/2000/svg}"
    paths = [p.get("d") for p in root.iter(f"{ns}path")]
    assert paths[0].startswith("M") and paths[0].count("L") == 1  # the n/a budget leaves a gap
    assert len(list(root.iter(f"{ns}circle"))) == 5 + 2  # five points plus two legend swatches

    whiskers = figures.dot_whiskers(
        "t",
        "s",
        "d",
        ("128", "1024"),
        "token budget",
        [figures.Whiskers("bge-small", figures.BLUE, ((0.08, 0.07, 0.09), (0.13, 0.12, 0.14)))],
        y_step=0.05,
        references=[(0.05, "gate threshold +0.05")],
        highlight=(1, "pre-registered budget"),
    )
    texts = [t.text for t in ET.fromstring(whiskers).iter(f"{ns}text")]
    assert "gate threshold +0.05" in texts and "pre-registered budget" in texts
    assert "bge-small" not in texts  # a single series needs no legend


def test_scatter_panels_draw_each_point_with_its_whisker():
    points = (
        figures.Point("no retrieval", figures.INK_2, 0.0, 0.12, 0.11, 0.13),
        figures.Point("section-aware", figures.ORANGE, 0.43, 0.18, 0.17, 0.2),
    )
    panels = [figures.ScatterPanel("QASPER", points), figures.ScatterPanel("pooled", points)]
    args = ("t", "s", "d", "retrieval recall", "answer score", 1.0, 0.2, 0.3, 0.05, panels)
    svg = figures.scatter_panels(*args, columns=2)
    assert svg == figures.scatter_panels(*args, columns=2)
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    assert len(list(root.iter(f"{ns}circle"))) == 4 + 2  # four points plus two legend swatches
    tips = [t.text for c in root.iter(f"{ns}circle") for t in c.iter(f"{ns}title")]
    assert "pooled, section-aware: retrieval recall 0.4300, answer score 0.1800 [0.1700, 0.2000]" in tips
    texts = [t.text for t in root.iter(f"{ns}text")]
    assert texts.count("retrieval recall") == 2 and "0.30" in texts and "1.0" in texts


def test_committed_writeup_and_figures_match_the_result_tables():
    assert check(REPO) == []


def _copy_repo(tmp_path: Path) -> Path:
    """The committed results/ and chunking/ trees, the only inputs `rag writeup` reads."""
    for relative in ("results", "chunking"):
        target = tmp_path / relative
        target.mkdir()
        for path in (REPO / relative).rglob("*"):
            if path.is_file():
                (target / path.relative_to(REPO / relative)).parent.mkdir(parents=True, exist_ok=True)
                (target / path.relative_to(REPO / relative)).write_bytes(path.read_bytes())
    return tmp_path


def test_check_reports_a_stale_block_a_stale_figure_and_an_unsourced_number(tmp_path):
    _copy_repo(tmp_path)
    writeup = tmp_path / "chunking" / "2026-10-14-v1-results.md"
    text = writeup.read_text(encoding="utf-8")
    text = text.replace("| fixed-64 | 0.2325 |", "| fixed-64 | 0.9999 |", 1)
    writeup.write_text(text + "\nA made-up recall of 0.1234.\n", encoding="utf-8")
    (tmp_path / "chunking" / "figures" / "v1-interaction.svg").write_text("<svg/>", encoding="utf-8")

    assert main(["writeup", "--check", "--root", str(tmp_path)]) == 1
    problems = check(tmp_path)
    assert any("'best-margins'" in p for p in problems)
    assert any("v1-interaction.svg" in p for p in problems)
    assert any("0.1234" in p for p in problems)

    assert main(["writeup", "--root", str(tmp_path)]) == 0
    assert check(tmp_path) == [
        "chunking/2026-10-14-v1-results.md: 0.1234 appears in the prose but in no generated block"
    ]


def test_check_covers_the_v2_write_up_and_its_figures(tmp_path):
    _copy_repo(tmp_path)
    writeup = tmp_path / "chunking" / "2026-10-18-v2-results.md"
    text = writeup.read_text(encoding="utf-8")
    assert "**Verdict: section-aware-titles replaces section-aware.**" in text
    text = text.replace(
        "**Verdict: section-aware-titles replaces section-aware.**", "**Verdict: section-aware stays.**", 1
    )
    writeup.write_text(text + "\nA made-up share of 12.3% and a query path of 99.9 ms.\n", encoding="utf-8")
    (tmp_path / "chunking" / "figures" / "v2-answer-vs-recall.svg").unlink()

    problems = check(tmp_path)
    assert any("'v2-verdict'" in p for p in problems)
    assert any("v2-answer-vs-recall.svg" in p for p in problems)
    assert any("12.3 appears" in p for p in problems) and any("99.9 appears" in p for p in problems)

    assert main(["writeup", "--root", str(tmp_path)]) == 0
    assert check(tmp_path) == [
        "chunking/2026-10-18-v2-results.md: 12.3 appears in the prose but in no generated block",
        "chunking/2026-10-18-v2-results.md: 99.9 appears in the prose but in no generated block",
    ]
