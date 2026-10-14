"""The production line and its ablations on the synthetic grid corpus, with
fake embedders and a fake reranker (no model downloads): reciprocal rank
fusion, the reranked head and its unreranked tail, the truncation flag,
the reranker cache, R5 and the seeded sample."""

from __future__ import annotations

import json
import re
import zlib
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest

from rag.cache import Cache
from rag.cli import main
from rag.config import config_hash, parse_grid_config
from rag.grid import run_grid, sample_papers
from rag.models import EMBEDDERS, RERANKER, EmbedderSpec, RerankerSpec
from rag.paths import Paths
from rag.retrieval import reciprocal_rank_fusion, rerank_head
from tests.conftest import FakeEncoding, make_answer, make_paper, make_qa, write_split
from tests.test_grid import GRID, build_env, table_rows

PRODUCTION = {
    **{k: v for k, v in GRID.items() if k != "pipeline"},
    "pipelines": ["hybrid-rerank", "hybrid", "vector", "bm25"],
    "embedders": ["bge-small", "nomic"],
    "rrf_k": 60,
    "rerank_depth": 3,
}
BLOCKS = [
    ("hybrid-rerank", "bge-small"),
    ("hybrid-rerank", "nomic"),
    ("hybrid", "bge-small"),
    ("hybrid", "nomic"),
    ("vector", "bge-small"),
    ("vector", "nomic"),
    ("bm25", None),
]


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


class FakeEmbedder:
    """Hashed bag of words; `tokens_per_byte` sets how many of the model's
    own tokens each UTF-8 byte costs, to exercise the input limit."""

    def __init__(self, spec: EmbedderSpec, tokens_per_byte: int):
        self.spec = spec
        self.tokens_per_byte = tokens_per_byte

    def input_tokens(self, texts: Sequence[str]) -> list[int]:
        return [self.tokens_per_byte * len(t.encode("utf-8")) for t in texts]

    def _embed(self, texts: Sequence[str]) -> np.ndarray:
        out = np.zeros((len(texts), 32), dtype=np.float32)
        for row, text in enumerate(texts):
            out[row, 0] = 0.01
            for word in _words(text):
                out[row, zlib.crc32(f"{self.spec.name}:{word}".encode()) % 32] += 1.0
        return out / np.linalg.norm(out, axis=1, keepdims=True)

    embed_documents = _embed
    embed_queries = _embed


class FakeReranker:
    """Scores word overlap; records every pair it is asked to score."""

    spec: RerankerSpec = RERANKER

    def __init__(self):
        self.pairs: list[tuple[str, str]] = []

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        self.pairs += pairs
        return [len(set(_words(q)) & set(_words(p))) + 0.001 * len(p) for q, p in pairs]


class FakeModels:
    def __init__(self):
        self.embedders = {
            "bge-small": FakeEmbedder(EMBEDDERS["bge-small"], tokens_per_byte=8),  # > 64 bytes is over 512
            "nomic": FakeEmbedder(EMBEDDERS["nomic"], tokens_per_byte=1),
        }
        self.reranker_model = FakeReranker()

    def embedder(self, name: str) -> FakeEmbedder:
        return self.embedders[name]

    def reranker(self) -> FakeReranker:
        return self.reranker_model


@pytest.fixture
def production_run(tmp_path):
    build_env(tmp_path)
    cfg = parse_grid_config(PRODUCTION)
    models = FakeModels()
    outcome = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding(), models=models)
    return cfg, outcome, models, tmp_path


def test_rrf_matches_a_hand_computed_example():
    # a: rank 1 in the first list, rank 3 in the second: 1/61 + 1/63
    # b: rank 2 and rank 1: 1/62 + 1/61; c: rank 3 only: 1/63; d: rank 2 only: 1/62
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "d", "a"]], k=60)
    assert fused == ["b", "a", "d", "c"]
    expected = {"a": 1 / 61 + 1 / 63, "b": 1 / 62 + 1 / 61, "c": 1 / 63, "d": 1 / 62}
    assert expected["b"] > expected["a"] > expected["d"] > expected["c"]


def test_rrf_breaks_ties_by_first_appearance():
    assert reciprocal_rank_fusion([["x", "y"], ["y", "x"]], k=60) == ["x", "y"]
    assert reciprocal_rank_fusion([["p"], ["q"]], k=60) == ["p", "q"]


def test_rerank_head_scores_only_the_head_and_keeps_the_tail_in_order():
    seen: list[list[int]] = []

    def scores(head):
        seen.append(list(head))
        return [float(item) for item in head]  # higher item, higher score

    ranked = list(range(10))
    assert rerank_head(ranked, 3, scores) == [2, 1, 0, 3, 4, 5, 6, 7, 8, 9]
    assert seen == [[0, 1, 2]]
    assert rerank_head([1, 2], 30, lambda head: [0.0] * len(head)) == [1, 2]  # ties keep fused order


def test_every_pipeline_and_embedder_is_scored_in_both_scopes(production_run):
    cfg, outcome, _, root = production_run
    results = pq.read_table(root / "runs" / "qasper" / "grid" / "results.parquet").to_pylist()
    per_cell = len(cfg.chunkings) * len(cfg.scopes) * len(cfg.budgets) * 3
    assert len(results) == outcome.n_questions * len(BLOCKS) * per_cell
    assert {(r["pipeline"], r["embedder"]) for r in results} == set(BLOCKS)
    assert {r["scope"] for r in results} == {"collection", "document"}
    fixed_k = pq.read_table(root / "runs" / "qasper" / "grid" / "fixed_k.parquet").to_pylist()
    assert {(r["pipeline"], r["embedder"]) for r in fixed_k} == set(BLOCKS)


def test_truncation_flag_marks_chunkings_with_chunks_over_the_input_limit(production_run):
    _, _, _, root = production_run
    results = pq.read_table(root / "runs" / "qasper" / "grid" / "results.parquet").to_pylist()
    shares = {(r["chunking"], r["embedder"]): r["truncated_share"] for r in results}
    # bge-small reads 8 tokens per byte: chunks over 64 bytes exceed its 512-token input
    for chunking in ("fixed-16", "fixed-32", "fixed-64", "small-to-big"):
        assert shares[(chunking, "bge-small")] == 0.0
    assert shares[("section-aware", "bge-small")] > 0.0
    assert all(shares[(c, "nomic")] == 0.0 for c, _ in shares if c)
    assert shares[("section-aware", None)] is None  # BM25 has no embedder

    r5 = (root / "results" / "qasper" / "r5-grid.md").read_text(encoding="utf-8")
    for row in table_rows(r5, "### Budget 256 tokens"):
        embedder, chunking, truncated = row[1], row[2], row[7]
        if embedder == "none":
            assert truncated == "n/a: no embedder"
        else:
            assert truncated.endswith("‡") == (chunking == "section-aware" and embedder == "bge-small"), row


def test_reranker_sees_at_most_the_fused_top_depth_and_a_rerun_scores_nothing(production_run):
    cfg, outcome, models, root = production_run
    manifest = json.loads((root / "runs" / "qasper" / "grid" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["reranker"]["max_candidates_per_list"] <= cfg.rerank_depth
    assert manifest["reranker"]["pairs_scored"] == len(models.reranker_model.pairs) > 0
    assert manifest["duration_seconds"] > 0
    assert manifest["models"]["reranker"]["model_id"] == RERANKER.model_id

    again = FakeModels()
    rerun = run_grid(parse_grid_config(PRODUCTION), Paths(root=root), encoding=FakeEncoding(), models=again)
    assert again.reranker_model.pairs == []
    manifest = json.loads((root / "runs" / "qasper" / "grid" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["reranker"]["pairs_scored"] == 0
    assert manifest["reranker"]["pairs_cached"] > 0
    assert {p.name: p.read_bytes() for p in rerun.tables} == {p.name: p.read_bytes() for p in outcome.tables}


def test_small_to_big_reranks_the_matched_children_not_the_parents(tmp_path):
    build_env(tmp_path)
    raw = {**PRODUCTION, "chunkings": [c for c in PRODUCTION["chunkings"] if c["name"] == "small-to-big"]}
    models = FakeModels()
    run_grid(parse_grid_config(raw), Paths(root=tmp_path), encoding=FakeEncoding(), models=models)
    passages = {p for _, p in models.reranker_model.pairs}
    assert passages and all(len(p.encode("utf-8")) <= 16 for p in passages)  # children are 16 bytes, parents 128


def test_the_unreranked_tail_is_flagged_only_on_the_production_line(production_run):
    _, _, _, root = production_run
    results = pq.read_table(root / "runs" / "qasper" / "grid" / "results.parquet").to_pylist()
    for row in results:
        if row["pipeline"] != "hybrid-rerank" or not row["scored"]:
            assert row["used_tail"] is None
        else:
            assert row["used_tail"] is not None
            if row["used_tail"] and row["chunking"] == "fixed-16" and row["budget"] >= 64:
                assert row["n_chunks"] > 3  # every head chunk fits, so the tail comes after all three
    tail = [r for r in results if r["used_tail"]]
    assert tail and {r["view"] for r in tail} >= {"fair"}
    # three 16-token chunks hold 48 tokens: a 256 budget needs the tail
    assert any(r["chunking"] == "fixed-16" and r["budget"] == 256 for r in tail)


TIE_PARAGRAPH = "Kerberos tickets carry session keys issued by the center for every service realm."


def build_tie_env(root: Path) -> None:
    """A corpus whose chunks nearly all share one text, so every search
    cutoff (search_depth 4) falls well inside a tie group."""

    def papers(label: str, n: int) -> dict:
        return {
            f"paper{label}{i:02d}": make_paper(
                f"paper{label}{i:02d}",
                TIE_PARAGRAPH,
                [("S", [TIE_PARAGRAPH, TIE_PARAGRAPH])],
                qas=[
                    make_qa(f"q{label}{i:02d}", "tickets session keys center", [make_answer(evidence=[TIE_PARAGRAPH])])
                ],
            )
            for i in range(n)
        }

    write_split(root / "data" / "qasper" / "qasper-dev-v0.3.json", papers("dev", 6))
    write_split(root / "data" / "qasper" / "qasper-test-v0.3.json", papers("test", 6))


def test_two_independent_runs_render_byte_identical_result_tables(tmp_path):
    """Two full grid runs over the same fixture, each with its own indexes,
    caches and run directory, must render byte-identical result tables:
    which tied rows a search cutoff keeps may not leak into the tables."""
    raw = {**PRODUCTION, "budgets": [16, 32, 64], "search_depth": 4}
    rendered = {}
    for run in ("first", "second"):
        root = tmp_path / run
        build_tie_env(root)
        outcome = run_grid(parse_grid_config(raw), Paths(root=root), encoding=FakeEncoding(), models=FakeModels())
        rendered[run] = {path.name: path.read_bytes() for path in outcome.tables}
    assert rendered["first"]
    assert rendered["first"] == rendered["second"]


def test_r5_lists_production_first_and_fills_or_explains_every_cell(production_run):
    cfg, outcome, _, root = production_run
    assert sorted(p.name for p in outcome.tables) == sorted(
        ["r2-grid.md", "r2w-grid.md", "r3-grid.md", "r4-grid.md", "r5-grid.md"]
    )
    r5 = (root / "results" / "qasper" / "r5-grid.md").read_text(encoding="utf-8")
    for budget in cfg.budgets:
        rows = table_rows(r5, f"### Budget {budget} tokens")
        expected = [(p, e or "none", c.name) for p, e in BLOCKS for c in cfg.chunkings]
        assert [tuple(r[:3]) for r in rows] == expected
        for row in rows:
            assert len(row) == 10 and all(row)
            for cell in row[3:]:
                assert not cell.startswith("n/a") or cell.startswith("n/a: "), row
            size = int(row[2].split("-")[1]) if row[2].startswith("fixed-") else None
            unscored = size is not None and size > budget
            assert all((cell == "n/a: chunk > budget") == unscored for cell in row[3:7]), row
            if row[0] != "hybrid-rerank":
                assert row[8:] == ["n/a: no reranker", "n/a: no reranker"]


def test_r2_to_r4_gain_one_block_per_pipeline_and_embedder(production_run):
    _, _, _, root = production_run
    for name in ("r2", "r2w", "r3", "r4"):
        text = (root / "results" / "qasper" / f"{name}-grid.md").read_text(encoding="utf-8")
        titles = [line for line in text.splitlines() if line.startswith(("## Production line", "## Ablation"))]
        assert len(titles) == len(BLOCKS), name
        assert titles[0].startswith("## Production line") and titles[0].endswith("bge-small")
        assert titles[-1] == "## Ablation: BM25 only"


def test_bm25_only_configs_keep_their_hash():
    legacy = parse_grid_config(GRID)
    explicit = parse_grid_config({**{k: v for k, v in GRID.items() if k != "pipeline"}, "pipelines": ["bm25"]})
    assert legacy.as_dict()["pipeline"] == "bm25" and "pipelines" not in legacy.as_dict()
    assert config_hash(legacy) == config_hash(explicit)
    assert config_hash(parse_grid_config(PRODUCTION)) != config_hash(legacy)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"pipelines": ["hybrid-rerank"], "embedders": []}, "embedders are required"),
        ({"pipelines": ["bm25"], "embedders": ["nomic"]}, "embedders are required"),
        ({"pipelines": ["rerank"]}, "pipelines must be"),
        ({"embedders": ["e5"]}, "embedders must be"),
        ({"rerank_depth": 0}, "must be positive"),
        ({"search_depth": 2}, "cannot fill"),
        ({"pipeline": "bm25"}, "exactly one of"),
    ],
)
def test_invalid_pipeline_configs_are_rejected(change, message):
    with pytest.raises(ValueError, match=message):
        parse_grid_config({**PRODUCTION, **change})


def test_cache_round_trips_vectors_and_scores(tmp_path):
    cache = Cache(tmp_path / "c.sqlite")
    cache.put_vectors("m@1", [(("h", 0, 5), np.array([0.5, 0.25], dtype=np.float32))])
    assert list(cache.vectors("m@1", "h")) == [(0, 5)]
    assert cache.vectors("m@2", "h") == {}
    cache.put_scores("r@1", "why?", [(("h", 0, 5), 1.5)])
    assert cache.scores("r@1", "why?") == {("h", 0, 5): 1.5}
    assert cache.scores("r@1", "how?") == {}
    cache.close()


def test_sample_is_seeded_and_written_beside_the_run(tmp_path, monkeypatch):
    build_env(tmp_path)
    from rag.config import DatasetRef
    from rag.run import load_datasets

    splits, _, _ = load_datasets(Paths(root=tmp_path), (DatasetRef("qasper", ("dev", "test")),))
    first = sample_papers(splits, 1, seed=0)
    assert sample_papers(splits, 1, seed=0) == first
    assert sum(len(s.documents) for s in first) == 1
    kept = {d.doc_id for s in first for d in s.documents}
    assert all(q.doc_id in kept for s in first for q in s.questions)

    monkeypatch.setattr("rag.tokens.get_encoding", lambda: FakeEncoding())
    config = tmp_path / "grid.yaml"
    config.write_text(json.dumps(GRID), encoding="utf-8")
    assert main(["run", str(config), "--root", str(tmp_path), "--sample", "1"]) == 0
    assert (tmp_path / "runs" / "qasper" / "grid-sample1" / "results" / "qasper" / "r2-grid.md").is_file()
    assert not (tmp_path / "results").exists()
    r2 = (tmp_path / "runs" / "qasper" / "grid-sample1" / "results" / "qasper" / "r2-grid.md").read_text(
        encoding="utf-8"
    )
    assert "seeded sample of 1 documents (seed 0)" in r2
