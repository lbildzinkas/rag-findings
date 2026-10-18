"""The adoption profile's latency probe on a synthetic corpus with fake
models: every system's query path runs uncached (each question embedded
and every pair scored by the model), the reranker sees the configured
number of pairs per route, the sample is seeded, and the report records
the hardware and versions."""

from __future__ import annotations

import json

import pytest

from rag.config import parse_grid_config
from rag.grid import run_grid
from rag.latency import parse_latency_config, run_latency, sample_questions
from rag.paths import Paths
from tests.conftest import FakeEncoding
from tests.test_grid import build_env
from tests.test_production import PRODUCTION, FakeModels

SEVEN = ["fixed-16", "fixed-32", "section-aware", "small-to-big"]
LATENCY = {
    "kind": "latency",
    "dataset": {"name": "qasper", "splits": ["dev", "test"]},
    "questions_per_dataset": 3,
    "seed": 0,
    "rerank_depth": 3,
    "fused_rerank_depth": 5,
    "search_depth": 200,
    "systems": [
        {"name": "section-aware", "run": "grid", "chunkings": ["section-aware"]},
        {"name": "confidence routing", "run": "grid", "route": "confidence", "chunkings": SEVEN},
        {"name": "search-all routing", "run": "grid", "route": "search-all", "chunkings": SEVEN},
    ],
    "out": "results/v2/latency-profile.json",
}


class CountingModels(FakeModels):
    def __init__(self):
        super().__init__()
        self.queries = 0
        embedder = self.embedders["nomic"]
        embed = embedder.embed_queries

        def counted(texts):
            self.queries += len(texts)
            return embed(texts)

        embedder.embed_queries = counted


def test_the_probe_times_every_route_uncached(tmp_path):
    build_env(tmp_path)
    run_grid(parse_grid_config(PRODUCTION), Paths(root=tmp_path), encoding=FakeEncoding(), models=FakeModels())
    models = CountingModels()
    path = run_latency(parse_latency_config(LATENCY), Paths(root=tmp_path), models=models)
    report = json.loads(path.read_text(encoding="utf-8"))
    n = sum(report["questions"].values())
    assert report["questions"] == {"qasper": 3}
    # one untimed pass, then every question; no query vector or score is cached
    assert models.queries == 3 * (1 + n)
    pairs = {row["name"]: row["pairs"] for row in report["systems"]}
    assert 0 < pairs["section-aware"] <= 3
    assert 0 < pairs["search-all routing"] <= 5
    assert pairs["section-aware"] < pairs["confidence routing"] <= 3 * len(SEVEN)
    # every timed pair reached the model
    assert len(models.reranker_model.pairs) >= round(sum(pairs.values()) * n)
    searches = {row["name"]: row["searches"] for row in report["systems"]}
    assert searches == {"section-aware": 2, "confidence routing": 8, "search-all routing": 8}
    assert {"machine", "chip", "memory", "os", "device"} <= report["hardware"].keys()
    assert {"torch", "transformers", "sentence-transformers", "lancedb"} <= report["versions"].keys()
    for row in report["systems"]:
        for stage in ("embed_ms", "search_ms", "rerank_ms", "total_ms"):
            assert set(row[stage]) == {"mean", "p50", "p90"}


def test_the_sample_is_seeded_and_order_free():
    class Q:
        def __init__(self, qid):
            self.question_id = qid

    questions = [Q(f"q{i}") for i in range(20)]
    first = [q.question_id for q in sample_questions(questions, 5, seed=0)]
    assert first == [q.question_id for q in sample_questions(list(reversed(questions)), 5, seed=0)]
    assert first != [q.question_id for q in sample_questions(questions, 5, seed=1)]


def test_a_single_route_searches_one_chunking():
    bad = {**LATENCY, "systems": [{"name": "x", "run": "grid", "chunkings": SEVEN}]}
    with pytest.raises(ValueError, match="a single route searches one chunking"):
        parse_latency_config(bad)
