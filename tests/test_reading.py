"""The reader run: every setup's prompts answered through the response
cache by a fake backend, scored, and written to the answers parquet, the
manifest and R14; a warm re-run neither loads nor calls the model."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from rag.answers import Sample, SampledQuestion, parse_answers_config, read_answers
from rag.reader import Reading
from rag.reading import MANIFEST_PATH, R14_PATH, response_cache_path, run_reader
from tests.test_answers import DOCUMENTS, NQ_CONTEXT, NQ_PRECISE, QASPER_QUESTION, build_answers_env, make_config


@pytest.fixture
def env(tmp_path):
    return build_answers_env(tmp_path)


READER = {"model": {"id": "fake/reader-4bit", "revision": "abc123"}, "max_new_tokens": 16}
ANSWER = "zebra quokka 100 members"


def with_references(question, *references):
    return replace(question, references=references)


def make_sample() -> Sample:
    return Sample(
        seed=0,
        per_dataset={
            "qasper": (SampledQuestion(with_references(QASPER_QUESTION, "they renew"), "qasper"),),
            "nq": (
                SampledQuestion(with_references(NQ_PRECISE, "100"), "nq"),
                SampledQuestion(with_references(NQ_CONTEXT, "The Senate consists of 100 members."), "nq"),
            ),
        },
    )


def loader(_cfg, _paths):
    return make_sample(), DOCUMENTS


class CountingBackend:
    def __init__(self):
        self.prompts: list[str] = []

    def read(self, prompt: str) -> Reading:
        self.prompts.append(prompt)
        meta = {"latency_seconds": 0.5, "prompt_tokens": 40, "completion_tokens": 4, "finish_reason": "stop"}
        return Reading(answer=ANSWER, meta=meta)


def reader_config(paths):
    return parse_answers_config(make_config(paths).as_dict() | {"reader": READER})


def test_run_reader_answers_every_setup_and_writes_the_records(env, fake_encoding):
    cfg = reader_config(env)
    backend = CountingBackend()
    manifest = run_reader(
        cfg, env, loader=loader, backend_loader=lambda: backend, encoding=fake_encoding, log=lambda _: None
    )

    # 3 questions x 3 setups; the oracle picks fixed-128, the section-aware
    # setup's chunking here, so those prompts are identical and answered once
    assert len(backend.prompts) == 6
    rows = read_answers(env.run_dir("test-answers") / "answers.parquet")
    assert {(r["dataset"], r["setup"]) for r in rows} == {
        (d, s) for d in ("qasper", "nq") for s in ("section-aware", "oracle", "none")
    }
    precise = next(r for r in rows if r["question_id"] == "nq1" and r["setup"] == "none")
    assert precise["metric"] == "short_match" and precise["score"] == 0.0 and precise["secondary"] == 1.0
    assert all(r["latency_seconds"] == 0.5 and r["finish_reason"] == "stop" for r in rows)

    reader = manifest["reader"]
    assert reader["model"] == "fake/reader-4bit@abc123"
    assert reader["revision"] == "abc123"
    assert reader["settings"] == {"decoding": "greedy", "thinking": False, "max_new_tokens": 16}
    assert reader["totals"]["answers"] == 9 and reader["totals"]["distinct_prompts"] == 6
    assert reader["totals"]["calls"] == 6 and reader["totals"]["cached"] == 3
    assert reader["totals"]["prompt_tokens"] == 240 and reader["totals"]["completion_tokens"] == 24
    assert reader["totals"]["latency_seconds"] == 3.0
    assert reader["model_loads"] == 1 and reader["wall_seconds"] >= 0
    assert set(manifest["setups"]) == {"section-aware", "oracle", "none"}
    assert all(len(entry["prompt_digest"]) == 64 for entry in manifest["setups"].values())
    assert len(manifest["template_hash"]) == 64

    committed = json.loads(env.results.joinpath(*MANIFEST_PATH).read_text(encoding="utf-8"))
    assert committed == manifest
    r14 = env.results.joinpath(*R14_PATH).read_text(encoding="utf-8")
    for group in ("pooled", "qasper", "nq"):
        for setup in ("section-aware", "oracle", "none"):
            assert f"| {group} | {setup} | " in r14
    assert "## Reader latency per answer" in r14
    assert "`fake/reader-4bit@abc123`" in r14
    # answers stay in the git-ignored cache: never in the parquet, manifest or table
    for text in (r14, json.dumps(manifest), json.dumps(rows, default=str)):
        assert ANSWER not in text
    assert response_cache_path(env).is_file()


def test_warm_rerun_neither_loads_nor_calls_the_model(env, fake_encoding):
    cfg = reader_config(env)
    first = run_reader(
        cfg, env, loader=loader, backend_loader=CountingBackend, encoding=fake_encoding, log=lambda _: None
    )
    r14_first = env.results.joinpath(*R14_PATH).read_text(encoding="utf-8")

    def refuse():
        raise AssertionError("a warm re-run must not load the model")

    second = run_reader(cfg, env, loader=loader, backend_loader=refuse, encoding=fake_encoding, log=lambda _: None)
    assert second["reader"]["totals"]["calls"] == 0 and second["reader"]["totals"]["cached"] == 9
    assert second["reader"]["model_loads"] == 0
    assert second["reader"]["totals"]["latency_seconds"] == first["reader"]["totals"]["latency_seconds"]
    r14_second = env.results.joinpath(*R14_PATH).read_text(encoding="utf-8")
    strip = [line for line in r14_first.splitlines() if "run that wrote this table" not in line]
    assert strip == [line for line in r14_second.splitlines() if "run that wrote this table" not in line]


def test_a_changed_setting_misses_the_cache(env, fake_encoding):
    cfg = reader_config(env)
    run_reader(cfg, env, loader=loader, backend_loader=CountingBackend, encoding=fake_encoding, log=lambda _: None)
    longer = parse_answers_config(cfg.as_dict() | {"reader": READER | {"max_new_tokens": 32}})
    backend = CountingBackend()
    run_reader(longer, env, loader=loader, backend_loader=lambda: backend, encoding=fake_encoding, log=lambda _: None)
    assert len(backend.prompts) == 6


def test_run_reader_needs_a_reader_block_and_every_run(env, fake_encoding):
    with pytest.raises(ValueError, match="no reader block"):
        run_reader(make_config(env), env, loader=loader, encoding=fake_encoding, log=lambda _: None)
    cfg = reader_config(env)
    pending = parse_answers_config(
        cfg.as_dict()
        | {"setups": cfg.as_dict()["setups"] + [{"name": "late", "runs": {"qasper": "x", "nq": "x"}, "chunking": "a"}]}
    )
    with pytest.raises(ValueError, match="setup late waits for"):
        run_reader(pending, env, loader=loader, encoding=fake_encoding, log=lambda _: None)


def test_reader_config_round_trips_and_validates(env):
    cfg = reader_config(env)
    assert parse_answers_config(cfg.as_dict()) == cfg
    assert cfg.reader.model_key == "fake/reader-4bit@abc123"
    with pytest.raises(ValueError, match="max_new_tokens"):
        parse_answers_config(cfg.as_dict() | {"reader": READER | {"max_new_tokens": 0}})
