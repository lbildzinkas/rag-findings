"""End-to-end grid run on a synthetic corpus: every chunking at every
budget in both views and both scopes, n/a cells, the top-N cap flag,
query types, the per-question Parquet results and byte-identical tables."""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import pytest

from rag.config import parse_grid_config
from rag.grid import FIXED_K_SCHEMA, QUESTIONS_SCHEMA, RESULTS_SCHEMA, run_grid
from rag.paths import Paths
from rag.retrieval import BM25Index
from tests.conftest import FakeEncoding, make_answer, make_paper, make_qa, write_split

P1 = "Kerberos tickets carry session keys issued by the key distribution center for each service."
P2 = "Ticket renewal lets clients refresh tickets before expiry without new passwords or keys."
P3 = "Cross realm trust links distribution centers so tickets from one realm reach another service."
P4 = "Photosynthesis tickets aside, chloroplasts convert light into chemical energy for the plant cell."
P5 = "Leaves hold chloroplasts whose pigments absorb light; the plant stores the energy as sugar."

GRID = {
    "kind": "grid",
    "dataset": {"name": "qasper", "splits": ["dev", "test"]},
    "pipeline": "bm25",
    "chunkings": [
        {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        {"name": "fixed-32", "method": "fixed", "chunk_tokens": 32},
        {"name": "fixed-64", "method": "fixed", "chunk_tokens": 64},
        {"name": "section-aware", "method": "section_aware", "max_tokens": 128},
        {"name": "small-to-big", "method": "small_to_big", "max_tokens": 128, "child_tokens": 16},
    ],
    "budgets": [16, 32, 64, 128, 256],
    "top_n": 2,
    "side_top_n": 1,
    "scopes": ["collection", "document"],
    "fixed_k": [1, 2],
    "search_depth": 200,
    "seed": 0,
    "run_name": "grid",
}


def build_env(root: Path) -> None:
    dev = {
        "paperA": make_paper(
            "paperA",
            "Kerberos tickets abstract about keys.",
            [("Intro", [P1, P2]), ("Trust", [P3])],
            qas=[
                make_qa("qa1", "kerberos tickets session keys center", [make_answer(evidence=[P1])]),
                make_qa("qa2", "tickets renewal and cross realm trust", [make_answer(evidence=[P2, P3])]),
                make_qa(
                    "qa3",
                    "tickets keys service",
                    [make_answer(evidence=[P1]), make_answer(evidence=[P1, P3])],
                ),
                make_qa("qa4", "unanswerable tickets?", [make_answer(unanswerable=True)]),
            ],
        )
    }
    test = {
        "paperB": make_paper(
            "paperB",
            "Photosynthesis tickets abstract.",
            [("Intro", [P4]), ("Leaves", [P5])],
            qas=[make_qa("qb1", "chloroplasts light energy tickets", [make_answer(evidence=[P4])])],
        )
    }
    write_split(root / "data" / "qasper" / "qasper-dev-v0.3.json", dev)
    write_split(root / "data" / "qasper" / "qasper-test-v0.3.json", test)


def table_rows(text: str, heading: str) -> list[list[str]]:
    """Data rows of the markdown table under `heading`."""
    section = text.split(heading, 1)[1].split("\n\n", 2)[1]
    return [[c.strip() for c in line.strip("|").split("|")] for line in section.splitlines()[2:]]


@pytest.fixture
def grid_run(tmp_path):
    build_env(tmp_path)
    cfg = parse_grid_config(GRID)
    outcome = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding())
    return cfg, outcome, tmp_path


def test_query_types_are_stored_per_question_and_counted_in_r3(grid_run):
    _, outcome, root = grid_run
    assert outcome.n_questions == 4
    assert outcome.query_types == {"precise": 2, "context": 1, "mixed": 1}
    questions = pq.read_table(root / "runs" / "grid" / "questions.parquet").to_pydict()
    assert dict(zip(questions["question_id"], questions["query_type"], strict=True)) == {
        "qa1": "precise",
        "qa2": "context",
        "qa3": "mixed",
        "qb1": "precise",
    }
    r3 = (root / "results" / "qasper" / "r3-grid.md").read_text(encoding="utf-8")
    assert table_rows(r3, "## Questions") == [
        ["precise", "2"],
        ["context", "1"],
        ["mixed", "1"],
        ["total", "4"],
    ]


def test_results_are_columnar_and_cover_the_grid(grid_run):
    cfg, _, root = grid_run
    run_dir = root / "runs" / "grid"
    results = pq.read_table(run_dir / "results.parquet")
    fixed_k = pq.read_table(run_dir / "fixed_k.parquet")
    assert results.schema.remove_metadata() == RESULTS_SCHEMA
    assert fixed_k.schema.remove_metadata() == FIXED_K_SCHEMA
    assert pq.read_table(run_dir / "questions.parquet").schema.remove_metadata() == QUESTIONS_SCHEMA
    assert results.schema.metadata[b"rag.schema_version"] == b"2"
    assert results.num_rows == 4 * len(cfg.chunkings) * 2 * len(cfg.budgets) * 3
    assert fixed_k.num_rows == 4 * len(cfg.chunkings) * len(cfg.fixed_k)

    rows = results.to_pylist()
    for row in rows:
        size = int(row["chunking"].split("-")[1]) if row["chunking"].startswith("fixed-") else None
        assert row["scored"] == (size is None or size <= row["budget"])
        if not row["scored"]:
            assert row["recall"] is None and row["precision"] is None
            continue
        assert row["retrieved_tokens"] <= row["budget"]
        if row["view"] == "fair":
            assert row["top_n"] is None and row["cap_bound"] is None
        else:
            assert row["n_chunks"] <= row["top_n"]


def test_r2_marks_na_exactly_where_a_fixed_chunk_exceeds_the_budget(grid_run):
    _, _, root = grid_run
    for name in ("r2", "r2w"):
        r2 = (root / "results" / "qasper" / f"{name}-grid.md").read_text(encoding="utf-8")
        for heading in ("## Production view", "## Side table"):
            for row in table_rows(r2, heading):
                chunking, budget = row[0], int(row[1])
                size = int(chunking.split("-")[1]) if chunking.startswith("fixed-") else None
                is_na = size is not None and size > budget
                assert all((cell == "n/a") == is_na for cell in row[2:]), row


def test_r2_flags_the_smallest_fixed_row_where_the_cap_binds(grid_run):
    _, _, root = grid_run
    r2 = (root / "results" / "qasper" / "r2-grid.md").read_text(encoding="utf-8")
    rows = {(r[0], int(r[1])): r for r in table_rows(r2, "## Production view")}
    # cap 2 x 16 tokens fills a 32-token budget; above it the cap binds
    for budget in (16, 32):
        assert "†" not in rows[("fixed-16", budget)][2]
    for budget in (64, 128, 256):
        recall, precision = rows[("fixed-16", budget)][2:4]
        assert recall.endswith("†") and precision.endswith("†")
        assert float(rows[("fixed-16", budget)][6]) >= 0.5
    for row in rows.values():
        if row[6] != "n/a":
            assert row[2].endswith("†") == (float(row[6]) >= 0.5)
        assert not row[4].endswith("†")  # the fair view has no cap


def test_tables_regenerate_byte_identically(grid_run, tmp_path_factory):
    cfg, outcome, root = grid_run
    first = {p.name: p.read_bytes() for p in outcome.tables}
    assert sorted(first) == ["r2-grid.md", "r2w-grid.md", "r3-grid.md", "r4-grid.md"]

    again = run_grid(cfg, Paths(root=root), encoding=FakeEncoding())
    assert {p.name: p.read_bytes() for p in again.tables} == first

    other = tmp_path_factory.mktemp("other")
    build_env(other)
    fresh = run_grid(cfg, Paths(root=other), encoding=FakeEncoding())
    assert {p.name: p.read_bytes() for p in fresh.tables} == first


def test_r4_reports_fixed_k_per_chunking(grid_run):
    cfg, _, root = grid_run
    r4 = (root / "results" / "qasper" / "r4-grid.md").read_text(encoding="utf-8")
    rows = table_rows(r4, "## Fixed-k retrieval")
    assert [r[0] for r in rows] == [c.name for c in cfg.chunkings]
    for row in rows:
        values = [float(v) for v in row[1:]]
        assert all(0.0 <= v <= 1.0 for v in values)
        assert values[0] <= values[1]  # hit@1 <= hit@2


def test_document_scope_searches_only_the_question_document(tmp_path):
    from rag.chunking import fixed_windows
    from rag.documents import build_document
    from rag.tokens import TokenText

    docs = [build_document(d, "", [("Body", [P1, P2])]) for d in ("dA", "dB")]
    chunks, texts = [], {}
    for doc in docs:
        for c in fixed_windows(doc, TokenText(doc.text, FakeEncoding()), 16):
            chunks.append(c)
            texts[f"{c.doc_id}:{c.index}"] = doc.text[c.start : c.end]
    index = BM25Index(tmp_path / "lance", table="fixed-16")
    index.build(chunks, texts)
    assert {r.doc_id for r in index.search("tickets keys", 100)} == {"dA", "dB"}
    assert {r.doc_id for r in index.search("tickets keys", 100, doc_id="dB")} == {"dB"}
