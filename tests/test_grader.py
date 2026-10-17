"""The model-graded check: the seeded graded subset, the committed grader
prompt, verdict parsing, the headless `claude` call through a fake
process runner (flags, environment, retries with backoff), the agreement
statistics, and a full grading run whose warm re-run makes no call."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from rag.answers import Sample, SampledQuestion, load_answers_config, parse_answers_config
from rag.grader import (
    API_KEY_VARIABLES,
    MANIFEST_PATH,
    R15_PATH,
    ClaudeCliGrader,
    GraderError,
    auc,
    grader_sample,
    load_grader_prompt,
    parse_verdict,
    render_grader_prompt,
    run_grader,
    summarize,
)
from rag.labels import Question
from rag.paths import Paths
from rag.query_type import CONTEXT, PRECISE
from rag.reader import Reading
from rag.reading import run_reader
from tests.test_answers import DOCUMENTS, NQ_CONTEXT, NQ_PRECISE, QASPER_QUESTION, build_answers_env, make_config


@pytest.fixture
def env(tmp_path):
    return build_answers_env(tmp_path)


REPO = Path(__file__).resolve().parents[1]
FAKE_KEY = "sk-ant-fake-0123456789-never-printed"
TEMPLATE = "Q: {question}\nRefs:\n{references}\nA: {answer}\nPASS or FAIL?"


def ok(result: str = "PASS", model: str = "claude-fake-1") -> tuple[int, str, str]:
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "result": result,
        "usage": {
            "input_tokens": 3,
            "cache_creation_input_tokens": 100,
            "cache_read_input_tokens": 0,
            "output_tokens": 2,
        },
        "modelUsage": {model: {}},
    }
    return 0, json.dumps(payload), ""


class FakeRunner:
    """Records every call; answers from a script of outcomes, then PASS."""

    def __init__(self, outcomes=()):
        self.outcomes = list(outcomes)
        self.calls: list[dict] = []

    def __call__(self, argv, stdin, env, cwd, timeout):
        self.calls.append({"argv": list(argv), "stdin": stdin, "env": dict(env), "cwd": cwd})
        if argv[1:] == ["--version"]:
            return 0, "9.9.9 (Claude Code)\n", ""
        return self.outcomes.pop(0) if self.outcomes else ok()


# --- the graded subset and the prompt --------------------------------------


def big_sample() -> Sample:
    qasper = tuple(
        SampledQuestion(Question(f"p{i}", f"paper{i % 3}", "dev", f"question {i}", (), references=("r",)), "qasper")
        for i in range(10)
    )
    nq = tuple(
        SampledQuestion(
            Question(
                f"n{i}", f"n{i}", "dev", f"nq {i}", (), query_type=PRECISE if i % 2 else CONTEXT, references=("r",)
            ),
            "nq",
        )
        for i in range(10)
    )
    return Sample(seed=0, per_dataset={"qasper": qasper, "nq": nq})


def test_grader_sample_is_seeded_and_stratified():
    sample = big_sample()
    picked = grader_sample(sample, seed=0, per_dataset=4)
    assert picked == grader_sample(sample, seed=0, per_dataset=4)
    assert picked != grader_sample(sample, seed=1, per_dataset=4)
    assert sum(1 for d, _ in picked if d == "qasper") == 4
    nq = {qid for d, qid in picked if d == "nq"}
    types = [q.question.query_type for q in sample.per_dataset["nq"] if q.question.question_id in nq]
    assert sorted(types) == [CONTEXT, CONTEXT, PRECISE, PRECISE]
    with pytest.raises(ValueError, match="the grader needs 12"):
        grader_sample(sample, seed=0, per_dataset=12)


def test_committed_grader_prompt_matches_the_config_hash():
    cfg = load_answers_config(REPO / "configs" / "v2" / "answers.yaml")
    template = load_grader_prompt(Paths(root=REPO), cfg.grader)
    for slot in ("{question}", "{references}", "{answer}"):
        assert template.count(slot) == 1
    with pytest.raises(ValueError, match="no longer matches"):
        load_grader_prompt(Paths(root=REPO), replace(cfg.grader, prompt_sha256="0" * 64))


def test_render_grader_prompt_fills_every_slot_and_dedupes_references():
    text = render_grader_prompt(TEMPLATE, "Who?", ["Ann", "Ann ", "Bo"], "  Ann.  ")
    assert text == "Q: Who?\nRefs:\n- Ann\n- Bo\nA: Ann.\nPASS or FAIL?"
    assert "A: (empty)" in render_grader_prompt(TEMPLATE, "Who?", ["Ann"], " ")


@pytest.mark.parametrize(
    ("text", "verdict"), [("PASS", True), ("FAIL", False), ("**Pass**", True), ("fail.", False), ("PASS\n", True)]
)
def test_parse_verdict(text, verdict):
    assert parse_verdict(text) is verdict


@pytest.mark.parametrize("text", ["", "Maybe", "The answer passes"])
def test_parse_verdict_rejects_anything_else(text):
    with pytest.raises(GraderError):
        parse_verdict(text)


# --- the headless call -----------------------------------------------------


def test_cli_call_flags_and_environment_carry_no_key(monkeypatch):
    for name in API_KEY_VARIABLES:
        monkeypatch.setenv(name, FAKE_KEY)
    runner = FakeRunner()
    reading = ClaudeCliGrader("claude-fake-1", "low", max_attempts=1, runner=runner).read("grade this")
    assert reading.answer == "PASS"
    assert reading.meta["models"] == ["claude-fake-1"]
    assert reading.meta["input_tokens"] == 103 and reading.meta["output_tokens"] == 2
    call = runner.calls[0]
    argv = call["argv"]
    assert argv[:2] == ["claude", "-p"]
    assert argv[argv.index("--tools") + 1] == ""  # no tools
    assert argv[argv.index("--model") + 1] == "claude-fake-1"
    assert "--no-session-persistence" in argv and "--strict-mcp-config" in argv
    assert call["stdin"] == "grade this"
    assert not set(API_KEY_VARIABLES) & set(call["env"])
    assert FAKE_KEY not in json.dumps({"argv": argv, "env": call["env"], "meta": reading.meta, "stdin": call["stdin"]})


def test_cli_call_retries_with_backoff_then_succeeds():
    error = json.dumps({"subtype": "success", "is_error": True, "result": "overloaded"})
    runner = FakeRunner([(1, "", "rate limited"), (0, error, ""), ok("I think so"), (0, "not json", ""), ok("FAIL")])
    sleeps: list[float] = []
    reading = ClaudeCliGrader("m", "low", max_attempts=5, runner=runner, sleep=sleeps.append).read("p")
    assert reading.answer == "FAIL" and reading.meta["attempts"] == 5
    assert sleeps == [10.0, 20.0, 40.0, 80.0]


def test_cli_call_gives_up_after_max_attempts():
    runner = FakeRunner([(1, "", "boom")] * 3)
    with pytest.raises(GraderError, match="after 3 attempts"):
        ClaudeCliGrader("m", "low", max_attempts=3, runner=runner, sleep=lambda _: None).read("p")


# --- agreement -------------------------------------------------------------


def test_auc_counts_ties_half():
    assert auc([1.0, 0.8], [0.0, 0.2]) == 1.0
    assert auc([0.0], [1.0]) == 0.0
    assert auc([0.5], [0.5]) == 0.5
    assert auc([1.0], []) is None


def test_summarize_agreement_and_means():
    rows = [
        {"score": 1.0, "grader_pass": True},
        {"score": 0.6, "grader_pass": False},
        {"score": 0.0, "grader_pass": False},
        {"score": 0.2, "grader_pass": True},
    ]
    s = summarize(rows, threshold=0.5)
    assert s["n"] == 4 and s["pass_rate"] == 0.5
    assert s["mean_pass"] == pytest.approx(0.6) and s["mean_fail"] == pytest.approx(0.3)
    assert s["agreement"] == 0.5  # rows 1 and 3 agree
    assert s["auc"] == pytest.approx(0.75)  # 3 of the 4 pass-fail pairs order correctly


# --- the run ---------------------------------------------------------------


GRADER = {
    "model": "claude-fake-1",
    "effort": "low",
    "prompt": "configs/v2/grader-prompt.txt",
    "questions_per_dataset": 2,
    "seed": 0,
    "pause_seconds": 3,
    "max_attempts": 2,
    "threshold": 0.5,
}
READER = {"model": {"id": "fake/reader", "revision": "r1"}, "max_new_tokens": 8}


def run_sample() -> Sample:
    q1 = replace(QASPER_QUESTION, references=("they renew",))
    q2 = replace(QASPER_QUESTION, question_id="q2", text="Who renews?", references=("the office",))
    return Sample(
        seed=0,
        per_dataset={
            "qasper": (SampledQuestion(q1, "qasper"), SampledQuestion(q2, "qasper")),
            "nq": (
                SampledQuestion(replace(NQ_PRECISE, references=("100",)), "nq"),
                SampledQuestion(replace(NQ_CONTEXT, references=("The Senate has 100 members.",)), "nq"),
            ),
        },
    )


class Backend:
    def read(self, prompt: str) -> Reading:
        answer = "100" if "Context:" in prompt else "no idea"
        return Reading(
            answer=answer,
            meta={"latency_seconds": 1.0, "prompt_tokens": 9, "completion_tokens": 1, "finish_reason": "stop"},
        )


def test_run_grader_grades_every_setup_and_a_warm_rerun_makes_no_call(env, fake_encoding):
    template_path = env.root / "configs" / "v2" / "grader-prompt.txt"
    template_path.write_text(TEMPLATE, encoding="utf-8")
    base = make_config(env).as_dict()
    setups = [s for s in base["setups"] if s["name"] != "oracle"]  # q2 has no packed spans for the oracle
    grader = GRADER | {"prompt_sha256": hashlib.sha256(TEMPLATE.encode("utf-8")).hexdigest()}
    cfg = parse_answers_config(base | {"setups": setups, "reader": READER, "grader": grader})

    def loader(_cfg, _paths):
        return run_sample(), DOCUMENTS

    quiet = {"loader": loader, "encoding": fake_encoding, "log": lambda _: None}
    with pytest.raises(ValueError, match="run `rag answers` first"):
        run_grader(cfg, env, runner=FakeRunner(), sleep=lambda _: None, **quiet)
    run_reader(cfg, env, backend_loader=Backend, **quiet)

    runner = FakeRunner([ok("PASS"), ok("FAIL")] * 4)
    sleeps: list[float] = []
    manifest = run_grader(cfg, env, runner=runner, sleep=sleeps.append, **quiet)
    graded_calls = [c for c in runner.calls if c["argv"][1:] != ["--version"]]
    assert len(graded_calls) == 8  # 4 questions x 2 setups
    assert sleeps == [3.0] * 8  # paced after every call
    assert manifest["graded"] == {"questions": 4, "answers": 8, "calls": 8, "cached": 0}
    assert manifest["grader"]["served_by"] == ["claude-fake-1"]
    assert manifest["grader"]["cli_version"] == "9.9.9 (Claude Code)"
    assert manifest["tokens"] == {"input": 8 * 103, "output": 8 * 2}
    assert json.loads(env.results.joinpath(*MANIFEST_PATH).read_text(encoding="utf-8")) == manifest

    r15 = env.results.joinpath(*R15_PATH).read_text(encoding="utf-8")
    for group in ("pooled", "qasper", "nq", "nq precise", "nq context"):
        assert f"| {group} | " in r15
    for group in ("pooled", "qasper", "nq"):
        for setup in ("section-aware", "none"):
            assert f"| {group} | {setup} | " in r15
    assert "## Does the setup ranking hold under the grader?" in r15
    assert "no idea" not in r15  # answers are never committed

    rerun = FakeRunner()
    again = run_grader(cfg, env, runner=rerun, sleep=sleeps.append, **quiet)
    assert [c["argv"][1:] for c in rerun.calls] == [["--version"]]
    assert again["graded"]["calls"] == 0 and again["graded"]["cached"] == 8
    assert len(sleeps) == 8
