"""`rag answers <config>`: the reader run (ADR 0009, amended 2026-10-17).

Every setup of the answers config reads the reader sample: the fixed
prompt of rag.reader, rendered from the setup's packed chunks by
rag.answers, answered by the local reader (rag.reader_model) through the
response cache under data/cache/answers.sqlite, so an interrupted run
resumes free and a warm re-run neither calls nor loads the model. Each
answer is scored with the dataset's standard answer metric.

Writes runs/<run_name>/answers.parquet (ids, hashes, scores and call
records, never answer text), the committed manifest
results/v2/answers-manifest.json (model and revision, settings, prompt
hashes, call counts, token usage, latencies and wall time) and the
answer table R14, results/v2/r14-answers.md.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .answer_score import score_answer
from .answers import (
    AnswersConfig,
    RenderedPrompt,
    answers_config_hash,
    load_sample,
    render_r14,
    render_setup_prompts,
    setup_missing,
    write_answers,
)
from .paths import Paths
from .reader import CachedReader, LazyReader, Reader, ResponseCache, settings_hash, template_hash

R14_PATH = ("v2", "r14-answers.md")
MANIFEST_PATH = ("v2", "answers-manifest.json")
PROGRESS_EVERY = 50


def response_cache_path(paths: Paths) -> Path:
    """Reader and grader responses (answer text: git-ignored, never committed)."""
    return paths.cache / "answers.sqlite"


def prompt_digest(prompts: list[RenderedPrompt]) -> str:
    """sha256 over a setup's prompt hashes in sample order."""
    return hashlib.sha256("\n".join(p.prompt_hash for p in prompts).encode("utf-8")).hexdigest()


def render_all_prompts(cfg: AnswersConfig, paths: Paths, sample, documents, encoding=None) -> list[RenderedPrompt]:
    """Every setup's prompts, in config then sample order; fails on a
    setup whose runs are missing or a prompt over the budget plus template."""
    prompts: list[RenderedPrompt] = []
    for setup in cfg.setups:
        if missing := setup_missing(setup, paths):
            raise ValueError(f"setup {setup.name} waits for {', '.join(missing)}")
        rendered = render_setup_prompts(cfg, setup, sample, documents, paths, encoding)
        if over := [p.question_id for p in rendered if not p.within_budget or p.context_tokens > cfg.budget]:
            raise ValueError(f"setup {setup.name}: {len(over)} prompts over the budget plus template, e.g. {over[0]}")
        prompts += rendered
    return prompts


def _default_backend(cfg: AnswersConfig, paths: Paths) -> Callable[[], Reader]:
    def load() -> Reader:
        from .reader_model import load_reader

        assert cfg.reader is not None
        return load_reader(cfg.reader.model_id, cfg.reader.revision, paths.data, cfg.reader.max_new_tokens)

    return load


def _runtime() -> dict[str, str]:
    """The installed mlx and mlx-lm versions (empty where they are not
    installed: Linux, or a run without the dependency group)."""
    out = {}
    for package in ("mlx", "mlx-lm"):
        try:
            out[package] = version(package)
        except PackageNotFoundError:
            pass
    return out


def run_reader(
    cfg: AnswersConfig,
    paths: Paths,
    loader=load_sample,
    backend_loader: Callable[[], Reader] | None = None,
    encoding=None,
    log: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Read every setup on the sample, score the answers, write the
    answers parquet, the manifest and R14; returns the manifest."""
    if cfg.reader is None:
        raise ValueError("the answers config has no reader block")
    started = time.monotonic()
    sample, documents = loader(cfg, paths)
    prompts = render_all_prompts(cfg, paths, sample, documents, encoding)
    questions = {(dataset, s.question.question_id): s for dataset, rows in sample.per_dataset.items() for s in rows}
    settings = cfg.reader.settings()
    settings_digest = settings_hash(cfg.reader.model_key, settings)
    backend = LazyReader(backend_loader or _default_backend(cfg, paths))
    cache = ResponseCache(response_cache_path(paths))
    reader = CachedReader(cache, cfg.reader.model_key, settings_digest, backend)
    log(f"answers {cfg.run_name}: {len(prompts)} prompts over {len(cfg.setups)} setups")

    rows: list[dict[str, Any]] = []
    loop_started = time.monotonic()
    try:
        for i, prompt in enumerate(prompts, start=1):
            reading = reader.reading(prompt.prompt)
            sampled = questions[(prompt.dataset, prompt.question_id)]
            question = sampled.question
            scored = score_answer(prompt.dataset, question.query_type, reading.answer, question.references)
            rows.append(
                {
                    "dataset": prompt.dataset,
                    "question_id": question.question_id,
                    "doc_id": question.doc_id,
                    "query_type": question.query_type,
                    "setup": prompt.setup,
                    "metric": scored.metric,
                    "score": scored.score,
                    "secondary": scored.secondary,
                    "prompt_hash": prompt.prompt_hash,
                    "answer_hash": hashlib.sha256(reading.answer.encode("utf-8")).hexdigest(),
                    "latency_seconds": reading.meta.get("latency_seconds"),
                    "prompt_tokens": reading.meta.get("prompt_tokens"),
                    "completion_tokens": reading.meta.get("completion_tokens"),
                    "finish_reason": reading.meta.get("finish_reason"),
                }
            )
            if i % PROGRESS_EVERY == 0 or i == len(prompts):
                elapsed = time.monotonic() - loop_started
                eta = elapsed / i * (len(prompts) - i)
                log(
                    f"  {i}/{len(prompts)} answers ({reader.calls} model calls), {elapsed / 60:.1f} min, ~{eta / 60:.0f} min left"
                )
    finally:
        cache.close()

    run_dir = paths.run_dir(cfg.run_name)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_answers(run_dir / "answers.parquet", rows)
    manifest = _manifest(cfg, prompts, rows, settings, settings_digest, reader.calls, backend.loads, started)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    manifest_path = paths.results.joinpath(*MANIFEST_PATH)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    r14 = paths.results.joinpath(*R14_PATH)
    r14.write_text(render_r14(cfg, manifest["config_hash"], rows, reader=manifest["reader"]), encoding="utf-8")
    log(f"  wrote {r14.relative_to(paths.root)} and {manifest_path.relative_to(paths.root)}")
    return manifest


def _manifest(
    cfg: AnswersConfig,
    prompts: list[RenderedPrompt],
    rows: list[dict[str, Any]],
    settings: dict[str, Any],
    settings_digest: str,
    calls: int,
    loads: int,
    started: float,
) -> dict[str, Any]:
    assert cfg.reader is not None
    # setups can share a prompt (the oracle picks section-aware for some
    # questions): one model call answers both, so reader time and tokens
    # count each distinct prompt once
    distinct = list({row["prompt_hash"]: row for row in rows}.values())
    totals = {
        "answers": len(rows),
        "distinct_prompts": len(distinct),
        "calls": calls,
        "cached": len(rows) - calls,
        "latency_seconds": round(sum(row["latency_seconds"] or 0.0 for row in distinct), 2),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in distinct),
        "completion_tokens": sum(row["completion_tokens"] or 0 for row in distinct),
        "truncated": sum(1 for row in rows if row["finish_reason"] == "length"),
    }
    per_setup = {}
    for setup in cfg.setups:
        mine = [p for p in prompts if p.setup == setup.name]
        setup_rows = [row for row in rows if row["setup"] == setup.name]
        per_setup[setup.name] = {
            "prompts": len(mine),
            "prompt_digest": prompt_digest(mine),
            "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in setup_rows),
            "completion_tokens": sum(row["completion_tokens"] or 0 for row in setup_rows),
            "latency_seconds": round(sum(row["latency_seconds"] or 0.0 for row in setup_rows), 2),
        }
    return {
        "config_hash": answers_config_hash(cfg),
        "template_hash": template_hash(),
        "reader": {
            "model": cfg.reader.model_key,
            "model_id": cfg.reader.model_id,
            "revision": cfg.reader.revision,
            "settings": settings,
            "settings_hash": settings_digest,
            "runtime": _runtime(),
            "model_loads": loads,
            "totals": totals,
            "wall_seconds": round(time.monotonic() - started, 2),
        },
        "setups": per_setup,
    }
