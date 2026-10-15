"""The v2 label-free routers: cross-chunking reciprocal rank fusion over
span keys, overlap-aware packing, scoring over merged text, the confidence
router's tie-break, the routers run end to end on the synthetic corpus
(routed.parquet, packed.parquet, the manifest), search-all reducing to a
single chunking's production line at rerank depth 50, and R11 rendering
byte-identically from the same runs, per dataset and pooled."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.chunking import Chunk
from rag.cli import main
from rag.config import parse_grid_config
from rag.grid import run_grid
from rag.metrics import score_question, union_token_count
from rag.packing import pack_union
from rag.paths import Paths
from rag.routers import (
    ROUTED_SCHEMA,
    SEARCH_ALL,
    confidence_pick,
    fuse_by_span,
    load_routers_config,
    load_routers_table_config,
    parse_routers_config,
    parse_routers_table_config,
    run_routers,
    run_routers_table,
)
from tests.conftest import FakeEncoding
from tests.test_budget_view import BUDGET_GRID
from tests.test_grid import build_env
from tests.test_production import FakeModels

SIZE_ORDER = ["fixed-16", "fixed-32", "fixed-64", "section-aware", "small-to-big"]

ROUTERS = {
    "kind": "routers",
    "dataset": {"name": "qasper", "splits": ["dev", "test"]},
    "embedders": ["nomic"],
    "rrf_k": 60,
    "rerank_depth": 3,
    "fused_rerank_depth": 5,
    "chunkings": [
        {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        {"name": "fixed-32", "method": "fixed", "chunk_tokens": 32},
        {"name": "fixed-64", "method": "fixed", "chunk_tokens": 64},
        {"name": "section-aware", "method": "section_aware", "max_tokens": 128},
        {"name": "small-to-big", "method": "small_to_big", "max_tokens": 128, "child_tokens": 16},
    ],
    "budgets": [16, 32, 64, 128, 256],
    "top_n": 2,
    "budget_top_n": 3,
    "scopes": ["collection"],
    "search_depth": 200,
    "seed": 0,
    "run_name": "routers",
    "size_order": SIZE_ORDER,
    "export_packed": [{"view": "budget", "budget": 64, "scope": "collection"}],
}

TABLE = {
    "kind": "routers-table",
    "runs": ["qasper/routers"],
    "baselines": ["qasper/grid"],
    "scope": "collection",
    "pipeline": "hybrid-rerank",
    "embedder": "nomic",
    "chunkings": SIZE_ORDER,
    "baseline_chunking": "section-aware",
    "top_n": 2,
    "budget_top_n": 3,
    "run_name": "routers",
}


def run_routers_on(root: Path, cfg_raw: dict | None = None):
    build_env(root)
    return run_routers(
        parse_routers_config(cfg_raw or ROUTERS), Paths(root=root), encoding=FakeEncoding(), models=FakeModels()
    )


# --- cross-chunking fusion -------------------------------------------------


def _fchunk(doc: str, start: int, end: int, parent_index: int = -1) -> Chunk:
    return Chunk(
        doc_id=doc,
        index=start,
        start=start,
        end=end,
        token_start=start,
        token_end=end,
        n_tokens=end - start,
        parent_index=parent_index,
    )


def _span(chunk: Chunk) -> tuple:
    return (chunk.doc_id, chunk.start, chunk.end)


def test_fusion_matches_a_hand_computed_rrf_example_and_merges_identical_spans():
    # chunking A: P rank 1, Q rank 2, R rank 3; chunking B: Q (the identical
    # span, so the same item) rank 1, R rank 2, P rank 3. With k = 60:
    # Q = 1/62 + 1/61, P = 1/61 + 1/63, R = 1/63 + 1/62, so Q > P > R.
    p, q, r = _fchunk("d", 0, 10), _fchunk("d", 20, 30), _fchunk("d", 40, 50)
    q_again = _fchunk("d", 20, 30)  # another chunking's chunk over the same span
    fused = fuse_by_span([[p, q, r], [q_again, r, p]], _span, ["A", "B"])
    assert len(fused) == 3  # the identical span merged into one item
    assert [(c.start, name) for c, name in fused] == [(20, "A"), (0, "A"), (40, "A")]
    assert fused[0][0] is q  # represented by the chunk that first contributed it
    scores = {20: 1 / 62 + 1 / 61, 0: 1 / 61 + 1 / 63, 40: 1 / 63 + 1 / 62}
    assert sorted(scores, key=lambda s: -scores[s]) == [20, 0, 40]


def test_fusion_breaks_ties_by_first_appearance_across_chunkings():
    x, y = _fchunk("d", 0, 10), _fchunk("d", 20, 30)
    fused = fuse_by_span([[x], [y]], _span, ["A", "B"])
    assert [c.start for c, _ in fused] == [0, 20]


# --- overlap-aware packing -------------------------------------------------


def test_nested_chunk_is_skipped_and_counts_nothing_toward_the_cap():
    a, b, c = _fchunk("d", 0, 100), _fchunk("d", 20, 80), _fchunk("d", 100, 200)
    assert pack_union([a, b, c], budget=300, top_n=20) == [a, c]
    assert pack_union([a, b, c], budget=300, top_n=1) == [a]  # b never reached the cap


def test_partly_overlapping_chunk_adds_only_its_new_tokens():
    a, b = _fchunk("d", 0, 100), _fchunk("d", 50, 150)
    packed = pack_union([a, b], budget=200, top_n=20)
    assert packed == [a, b]
    assert union_token_count(packed) == 150  # 100 + the 50 new tokens of b


def test_identical_chunks_from_two_chunkings_return_one_item():
    a, same = _fchunk("d", 0, 100), _fchunk("d", 0, 100)
    assert pack_union([a, same], budget=200, top_n=20) == [a]
    assert union_token_count([a]) == 100


def test_chunks_from_different_documents_never_overlap():
    a, b = _fchunk("d1", 0, 100), _fchunk("d2", 0, 100)
    assert pack_union([a, b], budget=200, top_n=20) == [a, b]
    assert union_token_count([a, b]) == 200


def test_a_chunk_whose_new_tokens_do_not_fit_is_skipped_and_filling_continues():
    a, b, c = _fchunk("d", 0, 90), _fchunk("d", 80, 120), _fchunk("d", 150, 160)
    # a uses 90; b would add 40 (only 10 remain); c adds 10 and fits
    assert pack_union([a, b, c], budget=100, top_n=20) == [a, c]


def test_the_cap_counts_only_chunks_that_added_text():
    a, same, c, d = _fchunk("d", 0, 100), _fchunk("d", 0, 100), _fchunk("d", 200, 300), _fchunk("d", 400, 500)
    assert pack_union([a, same, c, d], budget=1000, top_n=2) == [a, c]  # `same` skipped, so c still fits the cap


def test_small_to_big_children_return_parents_under_v1s_rule():
    parent = _fchunk("d", 0, 100)
    parents = {("d", 7): parent, ("d", 8): _fchunk("d", 200, 300)}
    c1, c2 = _fchunk("d", 0, 20, parent_index=7), _fchunk("d", 20, 40, parent_index=7)
    c3 = _fchunk("d", 200, 220, parent_index=8)
    assert pack_union([c1], budget=200, top_n=20, parents=parents) == [parent]  # the parent fits
    assert pack_union([c1], budget=50, top_n=20, parents=parents) == [c1]  # only the child fits
    assert pack_union([c1, c2], budget=200, top_n=20, parents=parents) == [parent]  # the sibling is inside it
    assert union_token_count([parent]) == 100
    # two children of different parents, neither parent fitting: the children
    assert pack_union([c1, c3], budget=50, top_n=20, parents=parents) == [c1, c3]


def test_a_wholly_covered_parent_adds_nothing_and_the_child_is_skipped():
    other = _fchunk("d", 0, 100)
    child = _fchunk("d", 0, 20, parent_index=0)
    parents = {("d", 0): _fchunk("d", 0, 100)}
    assert pack_union([other, child], budget=300, top_n=20, parents=parents) == [other]


def _merged(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


@pytest.mark.parametrize("seed", range(8))
def test_packing_never_exceeds_the_budget_the_cap_or_the_text(seed):
    rng = random.Random(seed)
    for _ in range(60):
        ranked = []
        for _ in range(rng.randrange(1, 14)):
            doc = rng.choice(["d1", "d2", "d3"])
            start = rng.randrange(0, 80)
            ranked.append(_fchunk(doc, start, start + rng.randrange(1, 60)))
        budget, top_n = rng.randrange(1, 300), rng.randrange(1, 21)
        packed = pack_union(ranked, budget=budget, top_n=top_n)
        assert len(packed) <= top_n
        assert union_token_count(packed) <= budget
        covered: dict[str, list[tuple[int, int]]] = {}
        for chunk in packed:  # every packed chunk added text no earlier chunk covered
            ranges = _merged(covered.get(chunk.doc_id, []))
            new = chunk.n_tokens - sum(min(e, chunk.token_end) - max(s, chunk.token_start) for s, e in ranges)
            assert new > 0
            covered.setdefault(chunk.doc_id, []).append(chunk.token_span)


# --- scoring over merged text ----------------------------------------------


def test_precision_counts_merged_tokens():
    a, b = _fchunk("d", 0, 50), _fchunk("d", 25, 75)
    gold = [tuple(range(50))]
    plain = score_question(gold, [a, b], "d")
    merged = score_question(gold, [a, b], "d", retrieved=union_token_count([a, b]))
    assert plain.recall == merged.recall == 1.0
    assert plain.retrieved_tokens == 100  # the sum: v1's denominator
    assert merged.retrieved_tokens == 75  # the union: every token once
    assert plain.precision == 50 / 100
    assert merged.precision == 50 / 75


def test_single_chunking_scores_are_unchanged_under_merged_scoring():
    # v1's chunks never overlap, so the union equals the sum and both scorers
    # agree exactly: the property behind the baseline's unchanged scores
    chunks = [_fchunk("d", 0, 30), _fchunk("d", 30, 60), _fchunk("e", 0, 20)]
    gold = [tuple(range(10, 40))]
    assert union_token_count(chunks) == sum(c.n_tokens for c in chunks)
    plain = score_question(gold, chunks, "d")
    merged = score_question(gold, chunks, "d", retrieved=union_token_count(chunks))
    assert (plain.recall, plain.precision, plain.retrieved_tokens) == (
        merged.recall,
        merged.precision,
        merged.retrieved_tokens,
    )


# --- the confidence router's pick ------------------------------------------


def test_confidence_picks_the_highest_top1_score_with_ties_to_the_smaller_chunk():
    top1 = {"fixed-64": 0.9, "fixed-16": 0.8, "fixed-32": 0.8, "section-aware": 0.1, "small-to-big": 0.0}
    assert confidence_pick(top1, SIZE_ORDER) == "fixed-64"
    tied = {"fixed-64": 0.8, "fixed-16": 0.8, "fixed-32": 0.9, "section-aware": 0.9, "small-to-big": 0.0}
    assert confidence_pick(tied, SIZE_ORDER) == "fixed-32"  # the tie goes to the smaller chunk


def test_confidence_picks_the_smallest_chunk_when_nothing_was_scored():
    top1 = {name: float("-inf") for name in SIZE_ORDER}
    assert confidence_pick(top1, SIZE_ORDER) == "fixed-16"


# --- the routers run end to end --------------------------------------------


def test_the_routers_run_writes_routed_and_packed_rows(tmp_path):
    cfg = parse_routers_config(ROUTERS)
    outcome = run_routers_on(tmp_path)
    routed = pq.read_table(outcome.run_dir / "routed.parquet")
    assert routed.schema.remove_metadata() == ROUTED_SCHEMA
    rows = routed.to_pylist()
    assert len(rows) == 4 * 2 * len(cfg.views) * len(cfg.budgets)  # questions x routers x views x budgets
    assert {r["pipeline"] for r in rows} == {SEARCH_ALL, "confidence"}
    assert {r["view"] for r in rows} == {"budget", "production"}
    assert all(r["scored"] and r["recall"] is not None for r in rows)
    assert all(r["picked_chunking"] in SIZE_ORDER for r in rows if r["pipeline"] == "confidence")
    assert all(r["picked_chunking"] is None for r in rows if r["pipeline"] == SEARCH_ALL)
    assert all(r["chunking"] is None for r in rows)  # the routers are not chunkings
    for row in rows:
        cap = cfg.budget_top_n if row["view"] == "budget" else cfg.top_n
        assert row["n_chunks"] <= cap
        assert row["retrieved_tokens"] <= row["budget"]

    packed = pq.read_table(outcome.run_dir / "packed.parquet").to_pylist()
    assert packed
    for row in packed:
        assert row["view"] == "budget" and row["budget"] == 64 and row["scope"] == "collection"
        assert row["pipeline"] in (SEARCH_ALL, "confidence")
        assert row["chunking"] in SIZE_ORDER  # the representative's (or the pick's) chunking
        assert 1 <= row["rank"] <= cfg.budget_top_n
    assert {r["question_id"] for r in packed if r["pipeline"] == "confidence"}  # the pick's packed spans

    manifest = json.loads((outcome.run_dir / "manifest.json").read_text())
    assert manifest["counts"]["questions"] == 4
    assert manifest["reranker"]["routers"]["pairs_per_question"] == {SEARCH_ALL: 5, "confidence": 15}
    assert manifest["reranker"]["lists_reranked"] == 6 * 4  # per chunking + the fused list, per question
    assert manifest["embeddings"]["queries_embedded"] == 4
    assert manifest["schema_version"] == "1"
    assert sum(outcome.picks.values()) == 4


def test_confidence_rows_equal_the_picked_chunkings_baseline_rows(tmp_path):
    """The confidence router's result is that chunking's own budget-view (and
    production-view) packing, so its scores equal the baseline grid's rows
    for the picked chunking exactly: single-chunking scores unchanged."""
    build_env(tmp_path)
    paths = Paths(root=tmp_path)
    models = FakeModels()
    grid = run_grid(parse_grid_config(BUDGET_GRID), paths, encoding=FakeEncoding(), models=models)
    baseline = {
        (r["question_id"], r["chunking"], r["view"], r["top_n"], r["budget"]): r
        for r in pq.read_table(grid.run_dir / "results.parquet").to_pylist()
        if r["scope"] == "collection" and r["pipeline"] == "hybrid-rerank" and r["embedder"] == "nomic"
    }
    outcome = run_routers(parse_routers_config(ROUTERS), paths, encoding=FakeEncoding(), models=FakeModels())
    checked = 0
    for row in pq.read_table(outcome.run_dir / "routed.parquet").to_pylist():
        if row["pipeline"] != "confidence":
            continue
        expected = baseline[(row["question_id"], row["picked_chunking"], row["view"], row["top_n"], row["budget"])]
        if expected["scored"]:
            assert (row["recall"], row["precision"], row["retrieved_tokens"], row["n_chunks"]) == (
                expected["recall"],
                expected["precision"],
                expected["retrieved_tokens"],
                expected["n_chunks"],
            )
        else:  # the pick's chunks exceed the budget: the router retrieves nothing there
            assert row["retrieved_tokens"] == 0 and row["n_chunks"] == 0
        checked += 1
    assert checked == 4 * len(ROUTERS["budgets"]) * 2


def test_search_all_over_one_chunking_reduces_to_its_production_line_at_depth_50(tmp_path):
    """With a single chunking, fusion is the identity and search-all is that
    chunking's production line with rerank depth 50, in both views."""
    build_env(tmp_path)
    paths = Paths(root=tmp_path)
    models = FakeModels()
    for chunking in (
        {"name": "fixed-32", "method": "fixed", "chunk_tokens": 32},
        {"name": "small-to-big", "method": "small_to_big", "max_tokens": 128, "child_tokens": 16},
    ):
        shared = {
            "dataset": {"name": "qasper", "splits": ["dev", "test"]},
            "embedders": ["nomic"],
            "rrf_k": 60,
            "budgets": [16, 32, 64, 128, 256],
            "top_n": 2,
            "budget_top_n": 3,
            "scopes": ["collection"],
            "search_depth": 200,
            "seed": 0,
            "size_order": [chunking["name"]],
        }
        grid = run_grid(
            parse_grid_config(
                {
                    **shared,
                    "kind": "grid",
                    "pipelines": ["hybrid-rerank"],
                    "rerank_depth": 50,
                    "chunkings": [chunking],
                    "side_top_n": 2,
                    "fixed_k": [1],
                    "run_name": f"depth50-{chunking['name']}",
                }
            ),
            paths,
            encoding=FakeEncoding(),
            models=models,
        )
        expected = {
            (r["question_id"], r["view"], r["budget"]): r
            for r in pq.read_table(grid.run_dir / "results.parquet").to_pylist()
            if r["scope"] == "collection" and r["pipeline"] == "hybrid-rerank" and r["embedder"] == "nomic"
        }
        outcome = run_routers(
            parse_routers_config(
                {
                    **shared,
                    "kind": "routers",
                    "rerank_depth": 30,
                    "fused_rerank_depth": 50,
                    "chunkings": [chunking],
                    "run_name": f"reduce-{chunking['name']}",
                }
            ),
            paths,
            encoding=FakeEncoding(),
            models=FakeModels(),
        )
        routed = [
            r for r in pq.read_table(outcome.run_dir / "routed.parquet").to_pylist() if r["pipeline"] == SEARCH_ALL
        ]
        assert routed
        for row in routed:
            match = expected[(row["question_id"], row["view"], row["budget"])]
            if match["scored"]:  # single-chunking scores are the production line's
                assert (row["recall"], row["precision"], row["retrieved_tokens"], row["n_chunks"]) == (
                    match["recall"],
                    match["precision"],
                    match["retrieved_tokens"],
                    match["n_chunks"],
                )
            else:  # the chunking's chunks exceed the budget: nothing is retrieved
                assert row["retrieved_tokens"] == 0 and row["n_chunks"] == 0


# --- R11 --------------------------------------------------------------------


def _write_baseline_and_routers(root: Path) -> None:
    build_env(root)
    paths = Paths(root=root)
    models = FakeModels()
    run_grid(parse_grid_config(BUDGET_GRID), paths, encoding=FakeEncoding(), models=models)
    run_routers(parse_routers_config(ROUTERS), paths, encoding=FakeEncoding(), models=models)


def _copy_run_as(root: Path, run: str, dataset: str, new_run: str) -> None:
    """Copy a run's parquets under another dataset label (and run name)."""
    source = Paths(root=root).run_dir(run)
    target = Paths(root=root).run_dir(new_run, dataset)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("routed.parquet", "results.parquet"):
        if not (source / name).exists():
            continue
        table = pq.read_table(source / name)
        table = table.set_column(
            table.schema.get_field_index("dataset"), table.schema.field("dataset"), pa.array([dataset] * table.num_rows)
        )
        pq.write_table(table, target / name)


def test_r11_renders_both_routers_next_to_the_baseline_and_the_oracle(tmp_path):
    _write_baseline_and_routers(tmp_path)
    outcome = run_routers_table(parse_routers_table_config(TABLE), Paths(root=tmp_path))
    (path,) = outcome.tables
    assert path == tmp_path / "results" / "qasper" / "r11-routers.md"
    text = path.read_text(encoding="utf-8")
    for heading in (
        "## Retrieval, budget view (top-N cap 3)",
        "## Retrieval, production view (top-N cap 2)",
        "## Confidence routing's chunking picks",
    ):
        assert heading in text
    rows = re.findall(
        r"^\| qasper \| \d+ \| (section-aware|oracle router|search-all routing|confidence routing) \| [^|]+ \|",
        text,
        flags=re.MULTILINE,
    )
    assert len(rows) == 2 * 5 * 4  # both views x every budget x four systems
    cells = {
        (int(budget), system): float(recall)
        for budget, system, recall in re.findall(
            r"^\| qasper \| (\d+) \| (section-aware|oracle router|search-all routing|confidence routing) \| ([^|]+) \|",
            text,
            flags=re.MULTILINE,
        )
    }
    for budget in ROUTERS["budgets"]:
        oracle = cells[(budget, "oracle router")]
        assert oracle >= cells[(budget, "section-aware")]
        assert oracle >= cells[(budget, "search-all routing")]
        assert oracle >= cells[(budget, "confidence routing")]
    assert re.search(r"^\| qasper \| [0-9.]+ \([0-9]+\) \|", text, flags=re.MULTILINE)  # the pick distribution


def test_r11_regenerates_byte_identically_from_the_same_runs(tmp_path):
    _write_baseline_and_routers(tmp_path)
    paths = Paths(root=tmp_path)
    first = run_routers_table(parse_routers_table_config(TABLE), paths)
    second = run_routers_table(parse_routers_table_config(TABLE), paths)
    assert [p.name for p in first.tables] == [p.name for p in second.tables]
    for a, b in zip(first.tables, second.tables, strict=True):
        assert a == b
        assert a.read_bytes() == b.read_bytes()


def test_r11_pools_both_datasets_next_to_each_one(tmp_path):
    _write_baseline_and_routers(tmp_path)
    _copy_run_as(tmp_path, "qasper/routers", "nq", "routers")
    _copy_run_as(tmp_path, "qasper/grid", "nq", "grid")
    cfg = parse_routers_table_config(
        {**TABLE, "runs": ["qasper/routers", "nq/routers"], "baselines": ["qasper/grid", "nq/grid"]}
    )
    outcome = run_routers_table(cfg, Paths(root=tmp_path))
    assert [p.parent.name for p in outcome.tables] == ["nq", "qasper", "pooled"]
    pooled = (tmp_path / "results" / "pooled" / "r11-routers.md").read_text(encoding="utf-8")
    qasper = (tmp_path / "results" / "qasper" / "r11-routers.md").read_text(encoding="utf-8")

    def recall(text: str, dataset: str, budget: int, system: str) -> float:
        match = re.search(rf"^\| {dataset} \| {budget} \| {system} \| ([^|]+) \|", text, flags=re.MULTILINE)
        return float(match.group(1))

    # the pooled run is two identical copies, so every pooled mean equals
    # the per-dataset mean and the pooled counts are doubled
    for budget in ROUTERS["budgets"]:
        for system in ("section-aware", "oracle router", "search-all routing", "confidence routing"):
            assert recall(pooled, "pooled", budget, system) == recall(qasper, "qasper", budget, system)
    assert "| pooled | 4 |" in pooled  # the documents of both datasets
    assert re.search(r"^\| pooled \| .*\| 8 \|$", pooled, flags=re.MULTILINE)  # questions


def test_the_v2_routers_configs_parse_with_the_settled_shape():
    for path in ("configs/v2/qasper-routers.yaml", "configs/v2/nq-routers.yaml"):
        cfg = load_routers_config(Path(path))
        assert cfg.dataset in ("qasper", "nq")
        assert cfg.embedders == ("nomic",)
        assert cfg.scopes == ("collection",)
        assert cfg.rerank_depth == 30 and cfg.fused_rerank_depth == 50
        assert cfg.top_n == 8 and cfg.budget_top_n == 20
        assert cfg.size_order == (
            "fixed-64",
            "fixed-128",
            "fixed-256",
            "fixed-512",
            "section-aware",
            "small-to-big",
            "fixed-1024",
        )
        assert sorted(cfg.size_order) == sorted(c.name for c in cfg.chunkings)
        assert [(c.view, c.budget, c.scope) for c in cfg.export_packed] == [("budget", 1024, "collection")]
    table = load_routers_table_config(Path("configs/v2/routers.yaml"))
    assert table.runs == ("qasper/v2-routers", "nq/v2-routers")
    assert table.baselines == ("qasper/v2-baseline", "nq/v2-baseline")
    assert table.baseline_chunking == "section-aware"
    assert table.top_n == 8 and table.budget_top_n == 20


def test_the_cli_runs_the_routers_and_renders_r11(tmp_path, monkeypatch):
    _write_baseline_and_routers(tmp_path)
    calls = []

    def fake_run(cfg, paths, sample=None):
        calls.append((cfg.run_name, sample))
        return run_routers(cfg, paths, encoding=FakeEncoding(), models=FakeModels(), sample=sample)

    monkeypatch.setattr("rag.routers.run_routers", fake_run)
    config = tmp_path / "routers.yaml"
    config.write_text(json.dumps(ROUTERS), encoding="utf-8")
    assert main(["run", str(config), "--root", str(tmp_path)]) == 0
    assert calls == [("routers", None)]
    assert (tmp_path / "runs" / "qasper" / "routers" / "routed.parquet").exists()
    table = tmp_path / "table.yaml"
    table.write_text(json.dumps(TABLE), encoding="utf-8")
    assert main(["routers", str(table), "--root", str(tmp_path)]) == 0
    assert (tmp_path / "results" / "qasper" / "r11-routers.md").exists()
    # a table asking for an embedder the runs do not cover fails clearly
    with pytest.raises(ValueError, match="no routed rows"):
        run_routers_table(parse_routers_table_config({**TABLE, "embedder": "bge-small"}), Paths(root=tmp_path))
