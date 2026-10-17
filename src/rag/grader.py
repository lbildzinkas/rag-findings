"""`rag grade <config>`: the model-graded check on the reader's answers
(ADR 0009, amended 2026-10-17).

A seeded subset of the reader sample - `questions_per_dataset` questions
per dataset, Natural Questions half precise and half context, ranked by
sha256(f"{seed}:{question id}") - has every setup's answer graded pass or
fail by the **grader**: the committed grader prompt (question, reference
answers, answer; fixed before any answer existed, its sha256 checked in
the config) sent through the `claude` command-line tool in headless mode.

The tool runs with no tools, no MCP servers, no settings files and no
saved session, from an empty temporary directory, on its own subscription
login: the child process gets no Anthropic API key variable, so it never
falls back to a paid API key. Nothing here reads or prints a credential.
Calls are paced `pause_seconds` apart and retried with exponential
backoff on a failed call or an unreadable verdict. Every verdict is
cached beside the reader's answers, so a re-run makes no call.

Writes runs/<run_name>/grades.parquet (ids, scores and verdicts), the
committed manifest results/v2/grader-manifest.json and the grader table
R15, results/v2/r15-grader.md: per dataset, the mean answer score of
passes against fails, the AUC of the answer score for predicting a
pass and how often the answer score (pass at or above the threshold)
and the grader agree; per setup, the grader pass rate next to the mean
answer score; and whether the setup ranking holds under the grader.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .answer_score import score_answer
from .answers import AnswersConfig, GraderSpec, Sample, answers_config_hash, answers_config_yaml, load_sample
from .nq import selection_key
from .paths import Paths
from .query_type import CONTEXT, PRECISE
from .reader import CachedReader, Reading, ResponseCache, prompt_hash, settings_hash
from .reading import render_all_prompts, response_cache_path

R15_PATH = ("v2", "r15-grader.md")
MANIFEST_PATH = ("v2", "grader-manifest.json")
SYSTEM_PROMPT = "You grade answers to questions. Reply with exactly one word: PASS or FAIL."
# removed from the child's environment (never read): the tool then uses its
# subscription login and cannot bill a paid API key
API_KEY_VARIABLES = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
CALL_TIMEOUT_SECONDS = 300.0
BACKOFF_SECONDS = 10.0

Runner = Callable[[Sequence[str], str, dict[str, str], Path, float], tuple[int, str, str]]


class GraderError(RuntimeError):
    pass


# --- the graded subset and the prompt ----------------------------------------


def grader_sample(sample: Sample, seed: int, per_dataset: int) -> list[tuple[str, str]]:
    """(dataset, question id) pairs: the first `per_dataset` QASPER questions
    in seeded order, and `per_dataset / 2` Natural Questions questions of
    each query type, in seeded order."""
    picked: list[tuple[str, str]] = []
    for dataset in ("qasper", "nq"):
        rows = sample.per_dataset[dataset]
        strata = (
            [(None, per_dataset)] if dataset == "qasper" else [(PRECISE, per_dataset // 2), (CONTEXT, per_dataset // 2)]
        )
        for query_type, count in strata:
            ids = [s.question.question_id for s in rows if query_type is None or s.question.query_type == query_type]
            if len(ids) < count:
                raise ValueError(f"the {dataset} sample has {len(ids)} questions; the grader needs {count}")
            ranked = sorted(ids, key=lambda qid: (selection_key(seed, qid), qid))
            picked += [(dataset, qid) for qid in ranked[:count]]
    return picked


def load_grader_prompt(paths: Paths, spec: GraderSpec) -> str:
    text = paths.root.joinpath(*spec.prompt).read_text(encoding="utf-8")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != spec.prompt_sha256:
        raise ValueError(f"the grader prompt {Path(*spec.prompt)} no longer matches its configured sha256")
    return text


def render_grader_prompt(template: str, question: str, references: Sequence[str], answer: str) -> str:
    unique = list(dict.fromkeys(reference.strip() for reference in references))
    filled = template.replace("{references}", "\n".join(f"- {reference}" for reference in unique))
    return filled.replace("{question}", question).replace("{answer}", answer.strip() or "(empty)")


def parse_verdict(text: str) -> bool:
    """PASS -> True, FAIL -> False; anything else is unreadable."""
    word = text.strip().split()[0].strip("*.:!`'\"").upper() if text.strip() else ""
    if word not in ("PASS", "FAIL"):
        raise GraderError(f"unreadable verdict: {text[:80]!r}")
    return word == "PASS"


# --- the headless claude CLI -----------------------------------------------


def run_subprocess(
    argv: Sequence[str], stdin: str, env: dict[str, str], cwd: Path, timeout: float
) -> tuple[int, str, str]:
    done = subprocess.run(
        list(argv), input=stdin, capture_output=True, text=True, env=env, cwd=cwd, timeout=timeout, check=False
    )
    return done.returncode, done.stdout, done.stderr


def child_environment() -> dict[str, str]:
    return {name: value for name, value in os.environ.items() if name not in API_KEY_VARIABLES}


class ClaudeCliGrader:
    """One grader call per prompt through `claude -p`, retried with
    exponential backoff; the answer is the verdict word."""

    def __init__(
        self,
        model: str,
        effort: str,
        max_attempts: int,
        runner: Runner = run_subprocess,
        sleep: Callable[[float], None] = time.sleep,
        binary: str = "claude",
    ):
        self.model = model
        self.effort = effort
        self.max_attempts = max_attempts
        self.runner = runner
        self.sleep = sleep
        self.binary = binary

    def flags(self) -> list[str]:
        return [
            "-p",
            "--model",
            self.model,
            "--effort",
            self.effort,
            "--output-format",
            "json",
            "--tools",
            "",
            "--strict-mcp-config",
            "--setting-sources",
            "",
            "--no-session-persistence",
            "--system-prompt",
            SYSTEM_PROMPT,
        ]

    def version(self) -> str:
        with tempfile.TemporaryDirectory() as cwd:
            code, out, _ = self.runner([self.binary, "--version"], "", child_environment(), Path(cwd), 60.0)
        return out.strip() if code == 0 else "unknown"

    def _call(self, prompt: str) -> Reading:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory() as cwd:
            code, out, err = self.runner(
                [self.binary, *self.flags()], prompt, child_environment(), Path(cwd), CALL_TIMEOUT_SECONDS
            )
        if code != 0:
            raise GraderError(f"claude exited with {code}: {err.strip()[-300:] or out.strip()[-300:]}")
        try:
            result = json.loads(out)
        except json.JSONDecodeError as exc:
            raise GraderError(f"claude printed no JSON result: {out.strip()[:120]!r}") from exc
        if result.get("is_error") or result.get("subtype") != "success":
            raise GraderError(f"claude reported an error: {str(result.get('result'))[:300]}")
        text = str(result.get("result", ""))
        parse_verdict(text)
        usage = result.get("usage") or {}
        return Reading(
            answer=text.strip(),
            meta={
                "latency_seconds": round(time.perf_counter() - started, 4),
                "models": sorted((result.get("modelUsage") or {}).keys()),
                "input_tokens": usage.get("input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
                + usage.get("cache_read_input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            },
        )

    def read(self, prompt: str) -> Reading:
        for attempt in range(1, self.max_attempts + 1):
            try:
                reading = self._call(prompt)
                return Reading(answer=reading.answer, meta=reading.meta | {"attempts": attempt})
            except (GraderError, subprocess.TimeoutExpired) as exc:
                if attempt == self.max_attempts:
                    raise GraderError(f"grader failed after {attempt} attempts: {exc}") from exc
                self.sleep(BACKOFF_SECONDS * 2 ** (attempt - 1))
        raise AssertionError("unreachable")  # pragma: no cover


def grader_settings(grader: ClaudeCliGrader) -> dict[str, Any]:
    return {"flags": grader.flags()}


# --- the run ---------------------------------------------------------------


GRADES_SCHEMA = pa.schema(
    [
        ("dataset", pa.string()),
        ("question_id", pa.string()),
        ("doc_id", pa.string()),
        ("query_type", pa.string()),
        ("setup", pa.string()),
        ("metric", pa.string()),
        ("score", pa.float64()),
        ("secondary", pa.float64()),
        ("grader_pass", pa.bool_()),
        ("grader_prompt_hash", pa.string()),
        ("input_tokens", pa.int64()),
        ("output_tokens", pa.int64()),
        ("latency_seconds", pa.float64()),
    ]
)


def run_grader(
    cfg: AnswersConfig,
    paths: Paths,
    loader=load_sample,
    runner: Runner = run_subprocess,
    sleep: Callable[[float], None] = time.sleep,
    encoding=None,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Grade every setup's cached answer on the graded subset; write the
    grades parquet, the manifest and R15; returns the manifest."""
    if cfg.reader is None or cfg.grader is None:
        raise ValueError("the answers config needs reader and grader blocks")
    spec = cfg.grader
    started = time.monotonic()
    template = load_grader_prompt(paths, spec)
    sample, documents = loader(cfg, paths)
    prompts = {
        (p.dataset, p.question_id, p.setup): p for p in render_all_prompts(cfg, paths, sample, documents, encoding)
    }
    questions = {
        (dataset, s.question.question_id): s.question for dataset, rows in sample.per_dataset.items() for s in rows
    }
    graded = grader_sample(sample, spec.seed, spec.questions_per_dataset)

    grader = ClaudeCliGrader(spec.model, spec.effort, spec.max_attempts, runner=runner, sleep=sleep)
    cache = ResponseCache(response_cache_path(paths))
    answers = CachedReader(cache, cfg.reader.model_key, settings_hash(cfg.reader.model_key, cfg.reader.settings()))
    verdicts = CachedReader(
        cache, f"claude-cli/{spec.model}", settings_hash(spec.model, grader_settings(grader)), grader
    )
    total = len(graded) * len(cfg.setups)
    log(
        f"grade {cfg.run_name}: {total} answers ({len(graded)} questions x {len(cfg.setups)} setups), model {spec.model}"
    )
    rows: list[dict[str, Any]] = []
    served: set[str] = set()
    try:
        for dataset, question_id in graded:
            question = questions[(dataset, question_id)]
            for setup in cfg.setups:
                try:
                    answer = answers.read(prompts[(dataset, question_id, setup.name)].prompt)
                except RuntimeError as exc:
                    raise ValueError(
                        f"no cached answer for {dataset} {question_id} {setup.name}: run `rag answers` first"
                    ) from exc
                scored = score_answer(dataset, question.query_type, answer, question.references)
                grader_prompt = render_grader_prompt(template, question.text, question.references, answer)
                calls = verdicts.calls
                reading = verdicts.reading(grader_prompt)
                if verdicts.calls > calls:
                    sleep(spec.pause_seconds)
                served.update(reading.meta.get("models", []))
                rows.append(
                    {
                        "dataset": dataset,
                        "question_id": question_id,
                        "doc_id": question.doc_id,
                        "query_type": question.query_type,
                        "setup": setup.name,
                        "metric": scored.metric,
                        "score": scored.score,
                        "secondary": scored.secondary,
                        "grader_pass": parse_verdict(reading.answer),
                        "grader_prompt_hash": prompt_hash(grader_prompt),
                        "input_tokens": reading.meta.get("input_tokens"),
                        "output_tokens": reading.meta.get("output_tokens"),
                        "latency_seconds": reading.meta.get("latency_seconds"),
                    }
                )
                if len(rows) % 25 == 0:
                    log(f"  {len(rows)}/{total} graded ({verdicts.calls} grader calls)")
    finally:
        cache.close()

    run_dir = paths.run_dir(cfg.run_name)
    run_dir.mkdir(parents=True, exist_ok=True)
    columns = {name: [row.get(name) for row in rows] for name in GRADES_SCHEMA.names}
    pq.write_table(pa.Table.from_pydict(columns, schema=GRADES_SCHEMA), run_dir / "grades.parquet")
    manifest = {
        "config_hash": answers_config_hash(cfg),
        "grader": spec.as_dict()
        | {
            "cli_version": grader.version(),
            "served_by": sorted(served),
            "settings": grader_settings(grader),
            "system_prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest(),
        },
        "graded": {
            "questions": len(graded),
            "answers": len(rows),
            "calls": verdicts.calls,
            "cached": len(rows) - verdicts.calls,
        },
        "tokens": {
            "input": sum(row["input_tokens"] or 0 for row in rows),
            "output": sum(row["output_tokens"] or 0 for row in rows),
        },
        "latency_seconds": round(sum(row["latency_seconds"] or 0.0 for row in rows), 2),
        "wall_seconds": round(time.monotonic() - started, 2),
    }
    manifest_path = paths.results.joinpath(*MANIFEST_PATH)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    r15 = paths.results.joinpath(*R15_PATH)
    r15.write_text(render_r15(cfg, manifest, rows), encoding="utf-8")
    log(f"  wrote {r15.relative_to(paths.root)} and {manifest_path.relative_to(paths.root)}")
    return manifest


# --- agreement -------------------------------------------------------------


def auc(passes: Sequence[float], fails: Sequence[float]) -> float | None:
    """The answer score's AUC for predicting a pass: the chance that a
    random pass scores above a random fail, ties counting half."""
    if not passes or not fails:
        return None
    wins = sum((p > f) + 0.5 * (p == f) for p in passes for f in fails)
    return wins / (len(passes) * len(fails))


def summarize(rows: Sequence[dict], threshold: float, column: str = "score") -> dict[str, Any]:
    passes = [row[column] for row in rows if row["grader_pass"]]
    fails = [row[column] for row in rows if not row["grader_pass"]]
    agree = sum((row[column] >= threshold) == row["grader_pass"] for row in rows)
    return {
        "n": len(rows),
        "pass_rate": len(passes) / len(rows),
        "mean_score": sum(row[column] for row in rows) / len(rows),
        "mean_pass": sum(passes) / len(passes) if passes else None,
        "mean_fail": sum(fails) / len(fails) if fails else None,
        "auc": auc(passes, fails),
        "agreement": agree / len(rows),
    }


def _groups(rows: Sequence[dict]) -> list[tuple[str, list[dict]]]:
    return [
        ("pooled", list(rows)),
        ("qasper", [r for r in rows if r["dataset"] == "qasper"]),
        ("nq", [r for r in rows if r["dataset"] == "nq"]),
        ("nq precise", [r for r in rows if r["dataset"] == "nq" and r["query_type"] == PRECISE]),
        ("nq context", [r for r in rows if r["dataset"] == "nq" and r["query_type"] == CONTEXT]),
    ]


def _num(value: float | None) -> str:
    return "-" if value is None else f"{value:.4f}"


def render_r15(cfg: AnswersConfig, manifest: dict[str, Any], rows: Sequence[dict]) -> str:
    assert cfg.grader is not None
    spec = cfg.grader
    threshold = spec.threshold
    setups = [setup.name for setup in cfg.setups]
    lines = [
        f"# R15 - {cfg.run_name}: the model-graded check of the answer score",
        "",
        f"Config hash: `{manifest['config_hash']}`",
        "",
        "## Config",
        "",
        "```yaml",
        answers_config_yaml(cfg),
        "```",
        "",
        "## Inputs",
        "",
        (
            f"- grader: `{spec.model}` (served by {', '.join(f'`{m}`' for m in manifest['grader']['served_by']) or '-'}) "
            f"through the `claude` command-line tool in headless mode ({manifest['grader']['cli_version']}), effort "
            f"{spec.effort}, no tools, on a subscription login; never a paid API"
        ),
        f"- grader prompt: `{Path(*spec.prompt)}` (sha256 `{spec.prompt_sha256}`), fixed before any answer existed",
        (
            f"- graded: {manifest['graded']['questions']} questions ({spec.questions_per_dataset} per dataset, Natural "
            f"Questions half precise and half context, seed {spec.seed}) x {len(setups)} setups = "
            f"{manifest['graded']['answers']} answers; {manifest['graded']['calls']} grader calls in the run that wrote "
            f"this table, {manifest['graded']['cached']} from the cache"
        ),
        f"- tokens: {manifest['tokens']['input']} input, {manifest['tokens']['output']} output",
        (
            f"- agreement: the answer score counts as a pass at or above {threshold} (short-answer match: an exact "
            "match), and agrees when that matches the grader's verdict"
        ),
        "",
        "## Agreement per dataset",
        "",
        (
            "AUC: the chance that a random answer the grader passes has a higher answer score than a random one it "
            "fails, ties counting half (1.0: the score separates them perfectly; 0.5: no better than chance)."
        ),
        "",
        (
            "| dataset | answers | grader pass rate | mean answer score | mean score, passes | mean score, fails | AUC "
            "| agreement |"
        ),
        "|---|---|---|---|---|---|---|---|",
    ]
    for group, members in _groups(rows):
        if not members:
            continue
        s = summarize(members, threshold)
        lines.append(
            f"| {group} | {s['n']} | {_num(s['pass_rate'])} | {_num(s['mean_score'])} | {_num(s['mean_pass'])} | "
            f"{_num(s['mean_fail'])} | {_num(s['auc'])} | {_num(s['agreement'])} |"
        )
    precise = [r for r in rows if r["dataset"] == "nq" and r["query_type"] == PRECISE and r["secondary"] is not None]
    if precise:
        s = summarize(precise, threshold, column="secondary")
        lines += [
            "",
            (
                f"Natural Questions precise questions scored by contains-a-reference instead: agreement "
                f"{_num(s['agreement'])}, AUC {_num(s['auc'])}, mean of passes {_num(s['mean_pass'])} against fails "
                f"{_num(s['mean_fail'])}."
            ),
        ]
    lines += [
        "",
        "## Per setup",
        "",
        "| dataset | setup | answers | grader pass rate | mean answer score | agreement |",
        "|---|---|---|---|---|---|",
    ]
    ranking_lines = []
    for group, members in _groups(rows)[:3]:
        by_setup = {}
        for setup in setups:
            mine = [r for r in members if r["setup"] == setup]
            if not mine:
                continue
            by_setup[setup] = summarize(mine, threshold)
            s = by_setup[setup]
            lines.append(
                f"| {group} | {setup} | {s['n']} | {_num(s['pass_rate'])} | {_num(s['mean_score'])} | "
                f"{_num(s['agreement'])} |"
            )
        if by_setup:
            by_score = sorted(by_setup, key=lambda name: -by_setup[name]["mean_score"])
            by_grader = sorted(by_setup, key=lambda name: -by_setup[name]["pass_rate"])
            holds = "yes" if by_score == by_grader else "no"
            ranking_lines.append(f"| {group} | {' > '.join(by_score)} | {' > '.join(by_grader)} | {holds} |")
    lines += [
        "",
        "## Does the setup ranking hold under the grader?",
        "",
        "| dataset | by mean answer score | by grader pass rate | same order |",
        "|---|---|---|---|",
        *ranking_lines,
        "",
        "No dataset text, prompt or answer is committed: only ids, hashes, scores and verdicts.",
        "",
    ]
    return "\n".join(lines)
