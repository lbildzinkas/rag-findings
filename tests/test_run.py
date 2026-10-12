"""End-to-end run on a synthetic two-paper corpus: exclusions, packing
limits, per-question results, manifest, and a byte-identical R1 re-run."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from rag.paths import Paths
from rag.run import run
from tests.conftest import FakeEncoding, make_answer, make_paper, make_qa, write_split

PARA_A = (
    "Kerberos tickets grant authentication rights through a trusted key "
    "distribution center and session keys."
)
PARA_B = (
    "Renewal windows let clients refresh tickets before expiry without "
    "re-authenticating against the center."
)
PARA_C = (
    "Photosynthesis converts light energy into chemical energy stored in "
    "sugar molecules inside chloroplasts."
)


def build_env(root: Path) -> Path:
    dev = {
        "paperA": make_paper(
            "paperA",
            "Kerberos authentication abstract.",
            [("Intro", [PARA_A]), ("Details", [PARA_B])],
            figures_and_tables=[{"file": "f1.png", "caption": "Figure 1: ticket lifetimes."}],
            qas=[
                make_qa("qa1", "trusted key distribution center session keys", [make_answer(evidence=[PARA_A])]),
                make_qa("qa2", "renewal windows refresh expiry", [make_answer(evidence=[PARA_B])]),
                make_qa("qa3", "invention year?", [make_answer(unanswerable=True)]),
                make_qa(
                    "qa4",
                    "ticket lifetimes figure",
                    [make_answer(evidence=["FLOAT SELECTED: Figure 1: ticket lifetimes."])],
                ),
                make_qa("qa5", "overview?", [make_answer(evidence=["Details ::: Intro"])]),
                make_qa("qa6", "zebras?", [make_answer(evidence=["zebra crossings"])]),
            ],
        )
    }
    test = {
        "paperB": make_paper(
            "paperB",
            "Photosynthesis abstract.",
            [("Intro", [PARA_C])],
            qas=[make_qa("qb1", "light energy chemical energy chloroplasts", [make_answer(evidence=[PARA_C])])],
        )
    }
    write_split(root / "data" / "qasper" / "qasper-dev-v0.3.json", dev)
    write_split(root / "data" / "qasper" / "qasper-test-v0.3.json", test)
    config = {
        "dataset": {"name": "qasper", "splits": ["dev", "test"]},
        "chunking": {"method": "fixed", "chunk_tokens": 16, "overlap": 0},
        "pipeline": "bm25",
        "budget": 256,
        "view": "production",
        "top_n": 8,
        "seed": 0,
        "search_depth": 10,
        "run_name": "tracer",
    }
    config_path = root / "configs" / "tracer.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def read_r1(root: Path) -> str:
    return (root / "results" / "qasper" / "r1-tracer.md").read_text(encoding="utf-8")


def test_end_to_end_run(tmp_path):
    config_path = build_env(tmp_path)
    outcome = run(config_path, Paths(root=tmp_path), encoding=FakeEncoding())

    assert outcome.n_questions == 3  # qa1, qa2 (dev) and qb1 (test)
    assert outcome.excluded_by_reason == {
        "unanswerable": 1,
        "figure_or_table_only": 2,  # figure-only and section-only
        "evidence_unanchored": 1,
    }

    r1 = read_r1(tmp_path)
    assert "| included | 3 |" in r1
    assert "| excluded: unanswerable | 1 |" in r1
    assert "| excluded: figure_or_table_only | 2 |" in r1
    assert "| excluded: evidence_unanchored | 1 |" in r1
    assert "mean retrieval recall" in r1
    assert "mean retrieval precision" in r1

    # per-question results: packing respects budget and cap
    lines = (tmp_path / "runs" / "tracer" / "questions.jsonl").read_text().splitlines()
    records = [json.loads(line) for line in lines]
    assert len(records) == outcome.n_questions
    for record in records:
        assert record["retrieved_tokens"] <= 256
        assert record["n_chunks_packed"] <= 8
        assert 0.0 <= record["recall"] <= 1.0
        assert 0.0 <= record["precision"] <= 1.0

    # the direct-hit questions retrieve mostly their own document's evidence
    by_id = {r["question_id"]: r for r in records}
    assert by_id["qa1"]["recall"] > 0.3
    assert by_id["qb1"]["recall"] > 0.3
    assert all(p["doc_id"] == "paperB" for p in by_id["qb1"]["packed"])

    manifest = json.loads((tmp_path / "runs" / "tracer" / "manifest.json").read_text())
    assert manifest["config_hash"] == outcome.config_hash
    assert set(manifest["datasets"]) == {"dev", "test"}
    assert manifest["versions"]["lancedb"]
    assert manifest["counts"]["questions"] == outcome.n_questions

    assert outcome.mean_recall > 0.0


def test_rerun_is_byte_identical(tmp_path):
    config_path = build_env(tmp_path)
    run(config_path, Paths(root=tmp_path), encoding=FakeEncoding())
    first = read_r1(tmp_path)
    first_questions = (tmp_path / "runs" / "tracer" / "questions.jsonl").read_bytes()
    run(config_path, Paths(root=tmp_path), encoding=FakeEncoding())
    assert read_r1(tmp_path) == first
    assert (tmp_path / "runs" / "tracer" / "questions.jsonl").read_bytes() == first_questions


def test_cli_run_command(tmp_path, capsys, monkeypatch, fake_encoding):
    from rag.cli import main

    monkeypatch.setattr("rag.tokens.get_encoding", lambda: fake_encoding)
    config_path = build_env(tmp_path)
    assert main(["run", str(config_path), "--root", str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "mean retrieval recall" in captured.out
    assert (tmp_path / "results" / "qasper" / "r1-tracer.md").is_file()


def test_run_requires_setup(tmp_path):
    config_path = tmp_path / "configs" / "tracer.yaml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        yaml.safe_dump(
            {
                "dataset": {"name": "qasper", "splits": ["dev", "test"]},
                "chunking": {"method": "fixed", "chunk_tokens": 16, "overlap": 0},
                "pipeline": "bm25",
                "budget": 256,
                "view": "production",
                "top_n": 8,
                "seed": 0,
                "run_name": "tracer",
            }
        ),
        encoding="utf-8",
    )
    import pytest

    with pytest.raises(FileNotFoundError, match="rag setup"):
        run(config_path, Paths(root=tmp_path), encoding=FakeEncoding())
