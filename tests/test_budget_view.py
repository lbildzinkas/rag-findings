"""The budget view (v2) and the packed-span export: budget-view rows in the
per-question results, the cap binding exactly where it should, packed.parquet
written for the exported cells, re-scoring its spans reproducing the
results' recall, the embedding cache counts in the manifest, the v2 configs
parsing, v1 config hashes unchanged, the headroom analysis reading the
budget view without a gate block, and a gate judged in the budget view
naming that view in its rule and verdict."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import yaml

from rag.chunking import Chunk
from rag.config import config_hash, load_any_config, parse_grid_config
from rag.grid import PACKED_SCHEMA, run_grid
from rag.metrics import score_question
from rag.paths import Paths
from rag.routing import analyse, gate_verdict, load_results, parse_headroom_config, run_headroom
from rag.run import gold_token_sets, load_datasets
from rag.tokens import TokenText
from tests.conftest import FakeEncoding
from tests.test_grid import build_env, table_rows
from tests.test_production import PRODUCTION, FakeModels
from tests.test_routing import CONFIG, write_results

BUDGET_TOP_N = 3
EXPORT_BUDGET = 128

BUDGET_GRID = {
    **PRODUCTION,  # the production line with fake embedders and a fake reranker
    "budget_top_n": BUDGET_TOP_N,
    "export_packed": [{"view": "budget", "budget": EXPORT_BUDGET, "scope": "collection"}],
}

# v1's configs must keep their hashes: their canonical JSON cannot change
V1_HASHES = {
    "configs/grid.yaml": "97bc8de66def0c97a34aaefe87bc535bd43e7b8f2f2320a696721ee5ab74df62",
    "configs/nq-grid.yaml": "b9cc99a6120a5b239138af5ab75b41aeb4cbebda4ffa6792299a0066f496cc92",
    "configs/tracer.yaml": "90a2ec4c41511bbf65bc26dace554a345166d9bbfc741ac37099197015c61e8b",
    "configs/nq-tracer.yaml": "4c25f5e98514852169e2938da9d5fecce3a555189e73b51f57ae4e2233a6acb1",
    "configs/pooled-grid.yaml": "f694a2158845007eb97e12458bd026cf20f009ae800d81a5bac1c7896c2d70b2",
    "configs/pooled-tracer.yaml": "3acca43f6ccc26ed855366f6d9d71de56c5bf8e245174be1b9690c6b84c94681",
}


def run_budget_grid(root: Path, cfg_raw: dict | None = None):
    build_env(root)
    cfg = parse_grid_config(cfg_raw or BUDGET_GRID)
    outcome = run_grid(cfg, Paths(root=root), encoding=FakeEncoding(), models=FakeModels())
    return cfg, outcome, root


def budget_rows(root: Path) -> list[dict]:
    results = pq.read_table(root / "runs" / "qasper" / "grid" / "results.parquet").to_pylist()
    return [r for r in results if r["view"] == "budget"]


def test_v1_config_hashes_are_unchanged():
    """The optional keys must not enter v1's canonical JSON."""
    for relative, expected in V1_HASHES.items():
        assert config_hash(load_any_config(Path(relative))) == expected, relative


def test_a_config_without_budget_top_n_renders_exactly_as_before(tmp_path):
    from tests.test_grid import GRID

    build_env(tmp_path)
    cfg = parse_grid_config(GRID)
    outcome = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding(), models=FakeModels())
    assert not outcome.run_dir.joinpath("packed.parquet").exists()
    r2 = (tmp_path / "results" / "qasper" / "r2-grid.md").read_text(encoding="utf-8")
    assert "Budget view" not in r2
    assert pq.read_table(outcome.run_dir / "results.parquet").num_rows == 4 * 5 * 2 * 5 * 3  # three views only


def test_budget_view_packing_respects_the_budget_and_cap(tmp_path):
    _, _, _ = run_budget_grid(tmp_path)
    rows = budget_rows(tmp_path)
    assert rows
    for row in rows:
        assert row["top_n"] == BUDGET_TOP_N
        if row["scored"]:
            assert row["n_chunks"] <= BUDGET_TOP_N
            assert row["retrieved_tokens"] <= row["budget"]
        else:  # a fixed chunk bigger than the budget is not scored there
            assert row["recall"] is None and row["cap_bound"] is None
    assert {r["view"] for r in rows} == {"budget"}


def test_the_cap_binds_only_where_the_budget_fits_more_chunks_than_the_cap(tmp_path):
    """fixed-16 at 256 tokens: 16 chunks would fit, the cap of 3 binds (the
    synthetic mirror of fixed-64 at 2048 tokens under the cap of 20);
    fixed-64 at 128 tokens: only 2 chunks fit, so the cap of 3 never binds."""
    run_budget_grid(tmp_path)
    rows = [
        r
        for r in budget_rows(tmp_path)
        if r["scored"] and r["scope"] == "collection" and r["pipeline"] == "hybrid-rerank" and r["embedder"] == "nomic"
    ]
    binds = [r for r in rows if (r["chunking"], r["budget"]) == ("fixed-16", 256)]
    free = [r for r in rows if (r["chunking"], r["budget"]) == ("fixed-64", 128)]
    assert binds, "the cap must bind for fixed-16 at 512 tokens"
    assert all(r["cap_bound"] and r["n_chunks"] == BUDGET_TOP_N for r in binds)
    assert free, "fixed-64 at 128 tokens must be scored"
    assert all(not r["cap_bound"] and r["n_chunks"] <= 2 for r in free)
    # the budget view's packing is the first cap chunks of the fair view's
    fair = {
        (r["chunking"], r["budget"], r["question_id"]): r
        for r in pq.read_table(tmp_path / "runs" / "qasper" / "grid" / "results.parquet").to_pylist()
        if r["view"] == "fair"
        and r["scope"] == "collection"
        and r["pipeline"] == "hybrid-rerank"
        and r["embedder"] == "nomic"
    }
    for row in binds:
        key = (row["chunking"], row["budget"], row["question_id"])
        assert row["n_chunks"] == min(BUDGET_TOP_N, fair[key]["n_chunks"])


def test_r2_renders_a_budget_view_section_only_when_configured(tmp_path):
    run_budget_grid(tmp_path)
    r2 = (tmp_path / "results" / "qasper" / "r2-grid.md").read_text(encoding="utf-8")
    rows = table_rows(r2, "## Budget view")
    budgets = PRODUCTION["budgets"]
    assert [r[0] for r in rows] == [c.name for c in parse_grid_config(BUDGET_GRID).chunkings for _ in budgets]
    for row in rows:
        chunking, budget = row[0], int(row[1])
        size = int(chunking.split("-")[1]) if chunking.startswith("fixed-") else None
        is_na = size is not None and size > budget
        assert all((cell == "n/a") == is_na for cell in row[2:]), row
    r5 = (tmp_path / "results" / "qasper" / "r5-grid.md").read_text(encoding="utf-8")
    assert "| hybrid-rerank | nomic | fixed-16 |" in r5
    header = r5.split("### Budget 16 tokens", 1)[1].split("\n\n", 2)[1].splitlines()[0]
    assert "budget recall | budget precision" in header and "tail used, budget view" in header


def test_packed_parquet_covers_the_exported_cell_and_reproduces_recall(tmp_path):
    cfg, outcome, _ = run_budget_grid(tmp_path)
    packed_path = outcome.run_dir / "packed.parquet"
    assert packed_path.exists()
    packed = pq.read_table(packed_path)
    assert packed.schema.remove_metadata() == PACKED_SCHEMA
    rows = packed.to_pylist()
    assert rows
    for row in rows:
        assert row["view"] == "budget" and row["budget"] == EXPORT_BUDGET and row["scope"] == "collection"
        assert 1 <= row["rank"] <= BUDGET_TOP_N
        assert 0 <= row["start"] < row["end"]
        assert row["tokens"] > 0

    # re-score the exported spans: rebuild each packed chunk from its span and
    # check the recall equals the results.parquet row for the same cell
    paths = Paths(root=tmp_path)
    splits, documents, _ = load_datasets(paths, cfg.sources)
    questions = {q.question_id: q for split in splits for q in split.questions}
    tokenized = {doc_id: TokenText(doc.text, FakeEncoding()) for doc_id, doc in documents.items()}
    results = {
        (r["question_id"], r["pipeline"], r["embedder"], r["chunking"]): r
        for r in pq.read_table(outcome.run_dir / "results.parquet").to_pylist()
        if r["view"] == "budget" and r["budget"] == EXPORT_BUDGET and r["scope"] == "collection"
    }
    grouped: dict[tuple, list[dict]] = {}
    for row in rows:
        grouped.setdefault((row["question_id"], row["pipeline"], row["embedder"], row["chunking"]), []).append(row)
    assert set(grouped) == set(results)
    for key, group in grouped.items():
        question = questions[key[0]]
        gold = gold_token_sets(question, tokenized)
        chunks = sorted(group, key=lambda r: r["rank"])
        # a chunk starts at a token start; its row's token count gives the end
        rebuilt = [
            Chunk(
                doc_id=r["doc_id"],
                index=-1,
                start=r["start"],
                end=r["end"],
                token_start=tokenized[r["doc_id"]].token_at_char(r["start"]),
                token_end=tokenized[r["doc_id"]].token_at_char(r["start"]) + r["tokens"],
                n_tokens=r["tokens"],
            )
            for r in chunks
        ]
        score = score_question(gold, rebuilt, question.doc_id)
        assert score.recall == results[key]["recall"], key
        assert score.retrieved_tokens == results[key]["retrieved_tokens"], key
        assert len(chunks) == results[key]["n_chunks"], key


def test_manifest_records_the_new_embeddings_and_reranker_pairs(tmp_path):
    _, outcome, _ = run_budget_grid(tmp_path)
    manifest = json.loads((outcome.run_dir / "manifest.json").read_text())
    embed = manifest["embeddings"]
    assert embed["chunk_vectors_embedded"] > 0  # the first run embeds everything
    assert embed["queries_embedded"] > 0
    assert manifest["reranker"]["pairs_scored"] > 0
    assert embed["chunk_vectors_embedded"] + embed["chunk_vectors_cached"] == sum(
        manifest["counts"]["chunks"].values()
    ) * len(parse_grid_config(BUDGET_GRID).embedders)

    # a second run over the warm cache embeds and scores nothing new
    cfg = parse_grid_config(BUDGET_GRID)
    again = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding(), models=FakeModels())
    warm = json.loads((again.run_dir / "manifest.json").read_text())
    assert warm["embeddings"]["chunk_vectors_embedded"] == 0
    assert warm["embeddings"]["queries_embedded"] == 0
    assert warm["reranker"]["pairs_scored"] == 0


def test_v2_configs_parse_with_the_settled_shape():
    qasper = load_any_config(Path("configs/v2/qasper-baseline.yaml"))
    nq = load_any_config(Path("configs/v2/nq-baseline.yaml"))
    for cfg, dataset in ((qasper, "qasper"), (nq, "nq")):
        assert cfg.dataset == dataset
        assert cfg.pipelines == ("hybrid-rerank",)
        assert cfg.embedders == ("nomic",)
        assert cfg.scopes == ("collection",)
        assert cfg.budgets == (128, 256, 512, 1024, 2048, 4096, 8192)
        assert [c.name for c in cfg.chunkings] == [
            "fixed-64",
            "fixed-128",
            "fixed-256",
            "fixed-512",
            "fixed-1024",
            "section-aware",
            "small-to-big",
        ]
        assert cfg.top_n == 8 and cfg.budget_top_n == 20 and cfg.rerank_depth == 30
        assert [(c.view, c.budget, c.scope) for c in cfg.export_packed] == [("budget", 1024, "collection")]
    headroom = parse_headroom_config(yaml.safe_load(Path("configs/v2/budget-view.yaml").read_text()))
    assert headroom.view == "budget" and headroom.top_n == 20
    assert not headroom.gated and headroom.primary_budget == 1024


def test_headroom_reads_the_budget_view_without_a_gate(tmp_path):
    write_results(
        Paths(root=tmp_path).run_dir("grid", "qasper"),
        {"qasper": 10},
        [("hybrid-rerank", "nomic")],
        budget_top_n=20,
    )
    config = {**CONFIG, "view": "budget", "top_n": 20, "gate": None, "primary_budget": 32}
    config.pop("gate")
    cfg = parse_headroom_config(config)
    assert not cfg.gated
    outcome = run_headroom(cfg, Paths(root=tmp_path))
    assert outcome.verdict[0].startswith("No gate block configured")
    r7 = (tmp_path / "results" / "routing" / "r7-headroom.md").read_text(encoding="utf-8")
    assert "Router gate" not in r7 and "Verdict" not in r7
    assert "| qasper | hybrid-rerank | nomic | budget | 32 |" in r7
    assert "| qasper | hybrid-rerank | nomic | fair | 32 |" in r7  # the fair view is analysed alongside


def test_a_gate_in_a_non_production_view_names_that_view(tmp_path):
    """The pre-registered rule and the verdict must say where the gate was
    judged: the analysed view, not the production view it was written for."""
    write_results(
        Paths(root=tmp_path).run_dir("grid", "qasper"),
        {"qasper": 10},
        [("bm25", None)],
        budget_top_n=20,
    )
    config = {
        **CONFIG,
        "view": "budget",
        "top_n": 20,
        "gate": {**CONFIG["gate"], "pipeline": "bm25", "datasets": ["qasper"], "budget": 32},
        "resamples": 50,
    }
    cfg = parse_headroom_config(config)
    assert cfg.gated
    outcome = run_headroom(cfg, Paths(root=tmp_path))
    assert outcome.verdict[0].startswith("Judged on the production line (`bm25`), budget view")
    r7 = (tmp_path / "results" / "routing" / "r7-headroom.md").read_text(encoding="utf-8")
    assert "in the budget view, at the primary budget of 32 tokens" in r7

    no_line = {**config, "gate": {**config["gate"], "pipeline": "hybrid-rerank"}}
    cfg2 = parse_headroom_config(no_line)
    verdict = gate_verdict(cfg2, analyse(cfg2, load_results(cfg2, Paths(root=tmp_path))))
    assert verdict[0].startswith("**Gate not judged:**")
    assert "tokens in the budget view" in verdict[0]
