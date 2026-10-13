"""The headroom analysis end to end on synthetic per-question results in
the grid's Parquet schema: views and scopes filtered, unscored chunkings
left out, pooled and per-dataset groups, the router gate in plain words,
the BM25-only case and byte-identical tables for the same seed."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.cli import main
from rag.grid import RESULTS_SCHEMA
from rag.paths import Paths
from rag.routing import analyse, gate_verdict, load_results, parse_headroom_config, run_headroom

CHUNKINGS = ["fixed-16", "fixed-32", "section-aware", "fixed-64"]
BUDGETS = [32, 64]

CONFIG = {
    "kind": "headroom",
    "runs": ["grid"],
    "scope": "collection",
    "top_n": 8,
    "chunkings": CHUNKINGS,
    "interaction_reference": "fixed-16",
    "gate": {
        "pipeline": "hybrid-rerank",
        "datasets": ["qasper", "nq"],
        "budget": 32,
        "min_headroom": 0.05,
        "confidence": 0.95,
    },
    "resamples": 400,
    "seed": 0,
    "run_name": "headroom",
}


def _recall(pipeline: str, embedder: str | None, chunking: int, q: int, rng: np.random.Generator) -> float:
    """complementary chunkings (big headroom) for embedder e1, one dominant
    chunking (zero headroom) everywhere else"""
    if pipeline == "hybrid-rerank" and embedder == "e1":
        return 0.9 if q % 3 == chunking else 0.1
    base = 0.2 + 0.6 * ((q * 7) % 11) / 10
    return base if chunking == 0 else base * 0.5


def write_results(run_dir: Path, datasets: dict[str, int], pipelines: list[tuple[str, str | None]]) -> None:
    rng = np.random.default_rng(0)
    rows: dict[str, list] = {name: [] for name in RESULTS_SCHEMA.names}
    for dataset, n_docs in datasets.items():
        for q in range(n_docs * 3):
            qtype = ("precise", "context", "mixed", "precise")[q % 4]
            for pipeline, embedder in pipelines:
                for c, chunking in enumerate(CHUNKINGS):
                    for scope in ("collection", "document"):
                        for view, top_n in (("production", 8), ("production", 5), ("fair", None)):
                            for budget in BUDGETS:
                                scored = not (chunking == "fixed-64" and budget < 64)
                                row = {
                                    "dataset": dataset,
                                    "split": "dev",
                                    "question_id": f"{dataset}-q{q}",
                                    "doc_id": f"{dataset}-d{q // 3}",
                                    "query_type": qtype,
                                    "pipeline": pipeline,
                                    "embedder": embedder,
                                    "chunking": chunking,
                                    "scope": scope,
                                    "view": view,
                                    "top_n": top_n,
                                    "budget": budget,
                                    "scored": scored,
                                    # off-view rows score 0 so filtering mistakes show up
                                    "recall": (
                                        _recall(pipeline, embedder, c, q, rng)
                                        if scope == "collection" and top_n != 5
                                        else 0.0
                                    )
                                    if scored
                                    else None,
                                }
                                for name in RESULTS_SCHEMA.names:
                                    rows[name].append(row.get(name))
    run_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pydict(rows, schema=RESULTS_SCHEMA), run_dir / "results.parquet")


FULL = [("bm25", None), ("hybrid-rerank", "e1"), ("hybrid-rerank", "e2")]


def test_gate_verdict_per_embedder_on_pooled_results(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 30, "nq": 30}, FULL)
    cfg = parse_headroom_config(CONFIG)
    results = analyse(cfg, load_results(cfg, Paths(root=tmp_path)))

    assert {r.group.name for r in results} == {"pooled", "qasper", "nq"}
    assert results[0].group.name == "pooled" and results[0].pipeline == "hybrid-rerank"
    small_budget = [r for r in results if r.budget == 32]
    assert all("fixed-64" not in r.candidates for r in small_budget)  # not scored at 32
    assert all("fixed-64" in r.candidates for r in results if r.budget == 64)
    assert all(r.n_questions == 180 for r in results if r.group.name == "pooled")

    verdict = gate_verdict(cfg, results)
    assert verdict[0].startswith("Judged on the production line (`hybrid-rerank`)")
    e1 = next(line for line in verdict if line.startswith("- e1, pooled over nq + qasper"))
    e2 = next(line for line in verdict if line.startswith("- e2, pooled over nq + qasper"))
    assert "which clears the gate" in e1
    assert "does not clear the gate: the headroom is below +0.0500" in e2
    assert verdict[-1] == "**Verdict: build the router in v2** (e1 clears the gate)."
    assert not any(line.startswith("**Provisional") for line in verdict)


def test_side_table_and_within_document_rows_are_ignored(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 20}, [("hybrid-rerank", "e2")])
    cfg = parse_headroom_config(CONFIG)
    results = analyse(cfg, load_results(cfg, Paths(root=tmp_path)))
    # only collection-search rows at top-N 8 and the fair view carry non-zero recall
    assert {r.view for r in results} == {"production", "fair"}
    assert all(r.analysis.oracle > 0.2 for r in results)
    assert [r.group.name for r in results] == ["qasper"] * 4  # no pooled group for one dataset


def test_bm25_only_results_say_the_gate_is_not_judged(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 20}, [("bm25", None)])
    cfg = parse_headroom_config(CONFIG)
    outcome = run_headroom(cfg, Paths(root=tmp_path))
    assert outcome.verdict[0].startswith("**Gate not judged:**")
    r7 = (tmp_path / "results" / "routing" / "r7-headroom.md").read_text(encoding="utf-8")
    assert "**Gate not judged:**" in r7
    assert "| bm25 | - | fixed-16 | +0.0000 |" in r7  # the reference table: one dominant chunking


def test_missing_gate_dataset_makes_the_verdict_provisional(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 20}, FULL)
    cfg = parse_headroom_config(CONFIG)
    verdict = gate_verdict(cfg, analyse(cfg, load_results(cfg, Paths(root=tmp_path))))
    assert verdict[1].startswith("**Provisional:**") and "lack nq" in verdict[1]


def test_same_seed_gives_byte_identical_tables(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 25, "nq": 20}, FULL)
    config = tmp_path / "headroom.yaml"
    import yaml

    config.write_text(yaml.safe_dump(CONFIG), encoding="utf-8")
    assert main(["headroom", str(config), "--root", str(tmp_path)]) == 0
    out = tmp_path / "results" / "routing"
    first = {p.name: p.read_bytes() for p in sorted(out.iterdir())}
    assert sorted(first) == ["r7-headroom.md", "r8-headroom.md", "r9-headroom.md"]
    assert main(["headroom", str(config), "--root", str(tmp_path)]) == 0
    assert {p.name: p.read_bytes() for p in sorted(out.iterdir())} == first

    r7 = first["r7-headroom.md"].decode("utf-8")
    assert "**Verdict: build the router in v2** (e1 clears the gate)." in r7
    assert "## Query-type oracle (secondary; does not change the gate)" in r7
    assert "| pooled | hybrid-rerank | e1 | production | 32 |" in r7
    r8 = first["r8-headroom.md"].decode("utf-8")
    assert "| pooled | hybrid-rerank | e1 | production | 32 | fixed-32 |" in r8
    r9 = first["r9-headroom.md"].decode("utf-8")
    assert "every chunking tied" in r9 and "| 64 |" not in r9  # primary budget only

    config.write_text(yaml.safe_dump({**CONFIG, "seed": 1}), encoding="utf-8")
    main(["headroom", str(config), "--root", str(tmp_path)])
    assert (out / "r7-headroom.md").read_bytes() != first["r7-headroom.md"]


def test_incomplete_or_unknown_inputs_fail_loudly(tmp_path: Path):
    write_results(tmp_path / "runs" / "grid", {"qasper": 10}, [("bm25", None)])
    cfg = parse_headroom_config({**CONFIG, "chunkings": CHUNKINGS[:-1]})
    with pytest.raises(ValueError, match="not in the config's size order"):
        load_results(cfg, Paths(root=tmp_path))

    table = pq.read_table(tmp_path / "runs" / "grid" / "results.parquet")
    keep = [
        i
        for i, (q, p) in enumerate(zip(table["question_id"].to_pylist(), table["chunking"].to_pylist(), strict=True))
        if not (q == "qasper-q0" and p == "fixed-32")
    ]
    pq.write_table(table.take(keep), tmp_path / "runs" / "grid" / "results.parquet")
    cfg = parse_headroom_config(CONFIG)
    with pytest.raises(ValueError, match="scored for only some questions"):
        analyse(cfg, load_results(cfg, Paths(root=tmp_path)))


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "grid"},
        {"interaction_reference": "fixed-8"},
        {"chunkings": ["fixed-16", "fixed-16"]},
        {"runs": []},
        {"resamples": 0},
        {"gate": {**CONFIG["gate"], "confidence": 1.5}},
        {"gate": {"pipeline": "hybrid-rerank"}},
    ],
)
def test_invalid_configs_are_rejected(change):
    with pytest.raises(ValueError):
        parse_headroom_config({**CONFIG, **change})
