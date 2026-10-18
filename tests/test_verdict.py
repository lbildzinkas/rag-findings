"""The v2 verdict (R16): the pre-registered bar and the tie-break on
synthetic contenders, the paired document-clustered bootstrap, R16 from
synthetic runs (byte-identical on a re-run, "section-aware stays" when
nothing passes), and, where the real baseline runs exist, R7's numbers
reproduced at the bar's cell."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.bootstrap import Interval, clustered_mean, resample_counts
from rag.paths import Paths
from rag.verdict import (
    Bar,
    Evidence,
    _oracle,
    judge,
    load_verdict_config,
    paired_difference,
    parse_verdict_config,
    run_verdict,
    tie_break,
    tie_break_words,
    verdict_config_hash,
    verdict_sentence,
)

BAR = Bar(min_gain=0.02, max_loss=0.01, tie=0.01)
ROOT = Path(__file__).resolve().parents[1]


def _evidence(name, pooled, low, high, qasper=0.0, nq=0.0, answer=None):
    return Evidence(
        name=name,
        pooled=pooled,
        interval=Interval(low=low, high=high, confidence=0.95),
        per_dataset={"qasper": qasper, "nq": nq},
        answer=answer,
    )


# --- the bar ---------------------------------------------------------------


def test_a_contender_with_the_gain_a_ci_excluding_0_and_no_dataset_loss_passes():
    j = judge(_evidence("a", 0.025, 0.012, 0.033, qasper=0.017, nq=0.036), BAR)
    assert j.passed and j.gain and j.datasets and j.answers is None and j.reasons == ()


def test_a_gain_whose_ci_includes_0_fails_on_the_ci():
    j = judge(_evidence("a", 0.025, -0.001, 0.05, qasper=0.02, nq=0.03), BAR)
    assert not j.passed and not j.gain and j.datasets
    assert j.reasons == ("its CI includes 0",)


def test_a_gain_below_the_bar_fails_even_with_a_ci_excluding_0():
    j = judge(_evidence("a", 0.015, 0.005, 0.025, qasper=0.01, nq=0.02), BAR)
    assert not j.passed and j.reasons == ("its pooled gain is below +0.0200",)


def test_one_dataset_more_than_0_01_below_fails_on_that_dataset():
    j = judge(_evidence("a", 0.03, 0.02, 0.04, qasper=0.06, nq=-0.0101), BAR)
    assert j.gain and not j.datasets and not j.passed
    assert j.reasons == ("nq alone is below -0.0100",)
    # exactly 0.01 worse is "no worse by more than 0.01"
    assert judge(_evidence("a", 0.03, 0.02, 0.04, qasper=0.06, nq=-0.01), BAR).passed


def test_an_answer_score_more_than_0_01_below_fails_on_the_answer_guard():
    j = judge(_evidence("a", 0.03, 0.02, 0.04, qasper=0.02, nq=0.04, answer=-0.02), BAR)
    assert j.gain and j.datasets and j.answers is False and not j.passed
    assert j.reasons == ("its answer score is below section-aware's by more than 0.0100",)
    assert judge(_evidence("a", 0.03, 0.02, 0.04, qasper=0.02, nq=0.04, answer=-0.005), BAR).passed


def test_an_unmeasured_answer_score_does_not_decide():
    assert judge(_evidence("a", 0.03, 0.02, 0.04, qasper=0.02, nq=0.04, answer=None), BAR).answers is None


# --- the tie-break ---------------------------------------------------------


def test_of_two_passing_contenders_within_0_01_the_simpler_wins():
    simple = judge(_evidence("late-128", 0.030, 0.02, 0.04, 0.03, 0.03), BAR)
    complex_ = judge(_evidence("contextual-256", 0.038, 0.03, 0.05, 0.03, 0.04), BAR)
    winner = tie_break([simple, complex_], BAR.tie)
    assert winner is simple
    assert tie_break_words(simple, [simple, complex_], winner) == (
        "wins: simpler than contextual-256 and within the tie margin of it"
    )
    assert tie_break_words(complex_, [simple, complex_], winner) == "loses to late-128"
    assert verdict_sentence(complex_, winner).endswith("section-aware is replaced by late-128.")


def test_a_simpler_contender_further_than_0_01_behind_loses():
    simple = judge(_evidence("late-128", 0.025, 0.02, 0.03, 0.02, 0.03), BAR)
    complex_ = judge(_evidence("contextual-256", 0.040, 0.03, 0.05, 0.03, 0.05), BAR)
    winner = tie_break([simple, complex_], BAR.tie)
    assert winner is complex_
    assert tie_break_words(complex_, [simple, complex_], winner).startswith("wins: the highest pooled recall")


def test_a_failing_contender_never_enters_the_tie_break():
    failing = judge(_evidence("late-128", 0.05, -0.01, 0.1, 0.05, 0.05), BAR)
    passing = judge(_evidence("titles", 0.0228, 0.0128, 0.0331, 0.0168, 0.0361), BAR)
    winner = tie_break([failing, passing], BAR.tie)
    assert winner is passing
    assert tie_break_words(failing, [failing, passing], winner) == "does not enter"
    assert tie_break_words(passing, [failing, passing], winner) == "wins: the only contender that passes"


def test_section_aware_stays_when_nothing_passes():
    judged = [judge(_evidence("a", -0.02, -0.03, -0.01, -0.02, -0.02), BAR)]
    assert tie_break(judged, BAR.tie) is None
    assert verdict_sentence(judged[0], None).startswith("a does not clear the bar (")


# --- the bootstrap ---------------------------------------------------------


def test_paired_difference_pools_each_dataset_with_its_own_draws():
    a = {("x", "q1"): 0.5, ("x", "q2"): 0.7, ("y", "q3"): 0.2, ("y", "q4"): 0.4, ("y", "q5"): 0.0}
    b = {("x", "q1"): 0.4, ("x", "q2"): 0.7, ("y", "q3"): 0.1, ("y", "q4"): 0.1, ("y", "q5"): 0.0}
    docs = {("x", "q1"): "d1", ("x", "q2"): "d2", ("y", "q3"): "d3", ("y", "q4"): "d3", ("y", "q5"): "d4"}
    diff = paired_difference(a, b, docs, ["x", "y"], resamples=200, seed=0)
    assert diff.pooled.point == pytest.approx(0.5 / 5)
    assert diff.per_dataset["x"].point == pytest.approx(0.05)
    # a dataset's draws are the same alone or pooled
    alone = clustered_mean(np.array([0.1, 0.0]), np.array([0, 1]), resample_counts(2, 200, 0, "x"))
    assert np.allclose(diff.per_dataset["x"].samples, alone.samples)
    with pytest.raises(ValueError, match="different questions"):
        paired_difference(a, {**b, ("y", "q6"): 0.0}, docs, ["x", "y"], 10, 0)


# --- R16 from synthetic runs -------------------------------------------------

CELLS = [("budget", 20, 512), ("budget", 20, 1024), ("budget", 20, 2048), ("production", 8, 1024)]
DATASETS = ("qasper", "nq")


def _questions():
    rng = np.random.default_rng(0)
    out = []
    for dataset in DATASETS:
        for q in range(30):
            out.append((dataset, f"{dataset}-q{q:02d}", f"{dataset}-d{q // 3}", ["precise", "context"][q % 2]))
    return out, rng


def _write_run(root: Path, dataset: str, run: str, rows: list[dict], file="results.parquet", chunks=None):
    run_dir = root / "runs" / dataset / run
    run_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), run_dir / file)
    manifest = {"config_hash": f"hash-{run}", "counts": {"chunks": chunks or {}}, "config": {"chunkings": []}}
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _rows(questions, system, recall_of, routed=False):
    rows = []
    for dataset, qid, doc, qtype in questions:
        for view, top_n, budget in CELLS:
            rows.append(
                {
                    "dataset": dataset,
                    "question_id": qid,
                    "doc_id": doc,
                    "query_type": qtype,
                    "pipeline": system if routed else "hybrid-rerank",
                    "embedder": "nomic",
                    "chunking": None if routed else system,
                    "scope": "collection",
                    "view": view,
                    "top_n": top_n,
                    "budget": budget,
                    "scored": True,
                    "recall": float(recall_of(qid, budget)),
                    "used_tail": qid.endswith("0"),
                }
            )
    return rows


def _build(root: Path, gain: float) -> None:
    questions, rng = _questions()
    base = {q[1]: float(v) for q, v in zip(questions, rng.uniform(0.0, 0.8, len(questions)), strict=True)}
    small = {q[1]: float(v) for q, v in zip(questions, rng.uniform(0.0, 0.9, len(questions)), strict=True)}

    def section_aware(qid, budget):
        return base[qid]

    for dataset in DATASETS:
        qs = [q for q in questions if q[0] == dataset]
        _write_run(
            root,
            dataset,
            "base",
            _rows(qs, "fixed-128", lambda qid, b: small[qid]) + _rows(qs, "section-aware", section_aware),
            chunks={"fixed-128": 40, "section-aware": 20},
        )
        _write_run(
            root,
            dataset,
            "titled",
            _rows(qs, "section-aware", section_aware) + _rows(qs, "good", lambda qid, b: base[qid] + gain),
        )
        _write_run(
            root,
            dataset,
            "deep",
            _rows(qs, "section-aware", lambda qid, b: base[qid] + 0.01)
            + _rows(qs, "good", lambda qid, b: base[qid] + gain + 0.005),
        )
        _write_run(
            root, dataset, "routers", _rows(qs, "router", lambda qid, b: base[qid] - 0.1, True), file="routed.parquet"
        )
    answers = [
        {"dataset": d, "question_id": qid, "doc_id": doc, "setup": setup, "score": float(score)}
        for (d, qid, doc, _), s in zip(questions, rng.uniform(0, 1, len(questions)), strict=True)
        for setup, score in (("section-aware", s), ("oracle", s * 0.9 + 0.1), ("no-retrieval", s * 0.5))
    ]
    (root / "runs" / "answers").mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(answers), root / "runs" / "answers" / "answers.parquet")
    manifest = {
        "config_hash": "hash-answers",
        "reader": {"model": "reader@rev"},
        "setups": {"section-aware": {"latency_seconds": 3.5, "prompts": 1, "prompt_tokens": 1000}},
    }
    (root / "runs" / "answers" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    stats = {"mean": 1.0, "p50": 1.0, "p90": 2.0}
    latency = {
        "config_hash": "hash-latency",
        "questions": {"nq": 2, "qasper": 2},
        "seed": 0,
        "warmup": 1,
        "search_depth": 1000,
        "hardware": {"machine": "test"},
        "versions": {"python": "3"},
        "models": {"embedder": "e@1"},
        "systems": [
            {
                "name": n,
                "searches": 2,
                "pairs": 30.0,
                **{f"{k}_ms": stats for k in ("embed", "search", "rerank", "total")},
            }
            for n in ("section-aware", "good")
        ],
    }
    (root / "results" / "v2").mkdir(parents=True)
    (root / "results" / "v2" / "latency.json").write_text(json.dumps(latency), encoding="utf-8")
    prefixes = {
        "model": {"id": "writer", "revision": "0123456789abcdef"},
        "chunks": 10,
        "wall_hours": 1.0,
        "datasets": {d: {"wall_hours": 0.5} for d in DATASETS},
    }
    (root / "results" / "prefixes.json").write_text(json.dumps(prefixes), encoding="utf-8")


SYNTHETIC = {
    "kind": "verdict",
    "run_name": "v2-verdict",
    "datasets": list(DATASETS),
    "bar": {"resamples": 200},
    "contenders": [
        {
            "name": "router routing",
            "system": "router",
            "table": "r11",
            "run": "routers",
            "reference_run": "base",
            "routed": True,
        },
        {"name": "good", "table": "r17", "run": "titled"},
    ],
    "oracle": {"run": "base", "chunkings": ["fixed-128", "section-aware"]},
    "answers": {"run": "answers", "setups": ["section-aware", "oracle", "no-retrieval"]},
    "depth50": {"runs": ["titled", "deep"], "contender": "good"},
    "latency": "results/v2/latency.json",
    "prefixes_manifest": "results/prefixes.json",
}


def test_r16_states_the_winner_and_regenerates_byte_identically(tmp_path):
    _build(tmp_path, gain=0.05)
    cfg = parse_verdict_config(SYNTHETIC)
    path = run_verdict(cfg, Paths(root=tmp_path))
    first = path.read_bytes()
    assert run_verdict(cfg, Paths(root=tmp_path)).read_bytes() == first
    text = first.decode("utf-8")
    assert "**Verdict: good replaces section-aware.**" in text
    assert "| good | R17 | +0.0500 |" in text
    assert "wins: the only contender that passes | good clears the bar and replaces section-aware. |" in text
    assert "router routing does not clear the bar (its pooled gain is below +0.0200; " in text
    assert "No contender's answers were measured (router routing, good)" in text
    assert "| 50 | +0.0450 |" in text  # the depth-50 margin
    assert f"Config hash: `{verdict_config_hash(cfg)}`" in text


def test_r16_says_section_aware_stays_when_nothing_passes(tmp_path):
    _build(tmp_path, gain=0.01)
    text = run_verdict(parse_verdict_config(SYNTHETIC), Paths(root=tmp_path)).read_text(encoding="utf-8")
    assert "**Verdict: section-aware stays: no contender clears the bar.**" in text
    assert "good does not clear the bar (its pooled gain is below +0.0200)." in text


def test_config_validation():
    with pytest.raises(ValueError, match="kind: verdict"):
        parse_verdict_config({**SYNTHETIC, "kind": "grid"})
    with pytest.raises(ValueError, match="distinct names other than section-aware"):
        parse_verdict_config({**SYNTHETIC, "contenders": [{"name": "section-aware", "table": "r2", "run": "x"}]})
    with pytest.raises(ValueError, match="depth50"):
        parse_verdict_config({**SYNTHETIC, "depth50": {"runs": ["a"], "contender": "good"}})


def test_the_committed_config_parses_in_tie_break_order():
    cfg = load_verdict_config(ROOT / "configs" / "v2" / "verdict.yaml")
    assert [c.name for c in cfg.contenders] == [
        "late-128",
        "late-256",
        "confidence routing",
        "search-all routing",
        "contextual-256",
        "section-aware-titles",
    ]
    assert (cfg.min_gain, cfg.max_loss, cfg.tie, cfg.confidence, cfg.resamples, cfg.seed) == (
        0.02,
        0.01,
        0.01,
        0.95,
        10000,
        0,
    )


# --- R7 reproduced on the real runs ------------------------------------------

_BASELINE = ROOT / "runs" / "qasper" / "v2-baseline" / "results.parquet"


@pytest.mark.skipif(not _BASELINE.exists(), reason="needs the git-ignored v2 baseline runs")
def test_the_bootstrap_reproduces_r7_for_section_aware_and_the_oracle_router():
    committed = {}
    r7 = (ROOT / "results" / "routing" / "r7-v2-budget-view.md").read_text(encoding="utf-8")
    for line in r7.splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 12 and cells[3:5] == ["budget", "1024"]:
            committed.setdefault(cells[0], cells)
    cfg = load_verdict_config(ROOT / "configs" / "v2" / "verdict.yaml")
    oracle = _oracle(cfg, Paths(root=ROOT), ("budget", 1024))
    for group, best, reference, oracle_recall, headroom, interval in oracle.rows:
        row = committed[group]
        assert row[5] == best == "section-aware"
        assert row[6] == f"{reference:.4f}"
        assert row[7] == f"{oracle_recall:.4f}"
        assert row[8] == f"{headroom.point:+.4f}"
        assert row[9] == f"[{interval.low:+.4f}, {interval.high:+.4f}]"
    assert re.search(r"\| pooled \| hybrid-rerank \| nomic \| budget \| 1024 \|", r7)
