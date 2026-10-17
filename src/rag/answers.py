"""`rag answers <config>`: the v2 reader stage (ADR 0009, amended
2026-10-17).

Assembles every reader setup from the runs' `packed.parquet` at the
budget view's primary cell (v2: budget view, 1024 tokens, collection
search), renders the fixed reader prompt for every setup and question,
and - with `--dry-run` - reports prompt token counts without calling a
model. Without `--dry-run`, rag.reading runs this stage: every prompt is
answered by the local reader (rag.reader_model) and the answer table R14
is filled.

Setups (config `kind: answers`):

- `packed`: one chunking (or pipeline) of a grid run; the packed chunks
  come from that run's packed.parquet;
- `oracle`: per question, the chunking with the highest retrieval recall
  at the cell, ties to the smaller chunk (`oracle_chunkings` order,
  smallest first), read from the baseline runs' results.parquet; the
  reader text is the picked chunking's packed chunks;
- `none`: the no-retrieval floor, the same prompt without a context.

The reader text of a packed chunk is its chunk text, except for the
side variant of contextual chunks (a chunking with `prefix_in_budget` in
its run's config), whose reader receives the chunk's prefix, a blank
line and its text, read from the prefix store (see rag.contextual); its
packed `tokens` already count the prefix.

A setup whose source runs are not on disk yet is reported as pending.

Answer scores live in runs/<run_name>/answers.parquet (one row per
question x setup: ids, hashes, scores and the reader call's record,
never answer text);
`render_r14` turns them into the answer table R14: answer score per
setup and dataset with document-clustered bootstrap CIs and the paired
difference from section-aware.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml

from .bootstrap import Estimate, Interval, percentile_interval, resample_counts
from .cache import SpanKey
from .config import PRODUCTION_LINE, DatasetRef, _parse_chunking, _parse_dataset
from .contextual import load_prefixes, search_text
from .documents import Document
from .labels import Question
from .paths import Paths
from .query_type import CONTEXT, PRECISE
from .reader import CHUNK_SEPARATOR, prompt_hash, render_prompt, template_hash
from .reader_sample import read_sample
from .run import load_datasets
from .tokens import TokenText

SECTION_AWARE = "section-aware"
SETUP_KINDS = ("packed", "oracle", "none")
DATASETS = ("qasper", "nq")

# --- config ----------------------------------------------------------------


@dataclass(frozen=True)
class SetupSpec:
    """One reader setup: where its packed chunks come from and how they are
    chosen. `runs` maps each dataset to the grid run under runs/<dataset>/."""

    name: str
    kind: str
    runs: tuple[tuple[str, str], ...] = ()
    chunking: str | None = None
    pipeline: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "kind": self.kind}
        if self.kind != "none":
            out["runs"] = {dataset: run for dataset, run in self.runs}
        if self.chunking is not None:
            out["chunking"] = self.chunking
        if self.pipeline is not None:
            out["pipeline"] = self.pipeline
        return out


@dataclass(frozen=True)
class ReaderSpec:
    """The reader model and its fixed generation settings (ADR 0009, amended
    2026-10-17): thinking off and greedy decoding, the same for every setup."""

    model_id: str
    revision: str
    max_new_tokens: int

    @property
    def model_key(self) -> str:
        return f"{self.model_id}@{self.revision}"

    def settings(self) -> dict[str, Any]:
        """The generation settings: hashed into the response cache key."""
        return {"decoding": "greedy", "thinking": False, "max_new_tokens": self.max_new_tokens}

    def as_dict(self) -> dict[str, Any]:
        return {"model": {"id": self.model_id, "revision": self.revision}, "max_new_tokens": self.max_new_tokens}


@dataclass(frozen=True)
class GraderSpec:
    """The model-graded check: `questions_per_dataset` seeded questions per
    dataset (Natural Questions half precise, half context), every setup's
    answer graded pass/fail through the `claude` command-line tool with the
    committed grader prompt, `pause_seconds` between calls."""

    model: str
    effort: str
    prompt: tuple[str, ...]  # the committed prompt file's path parts
    prompt_sha256: str
    questions_per_dataset: int
    seed: int
    pause_seconds: float
    max_attempts: int
    threshold: float  # an answer score at or above this counts as a pass

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "effort": self.effort,
            "prompt": str(Path(*self.prompt)),
            "prompt_sha256": self.prompt_sha256,
            "questions_per_dataset": self.questions_per_dataset,
            "seed": self.seed,
            "pause_seconds": self.pause_seconds,
            "max_attempts": self.max_attempts,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class AnswersConfig:
    run_name: str
    sources: tuple[DatasetRef, ...]
    sample: tuple[str, ...]  # the committed id list's path parts
    view: str
    budget: int
    top_n: int  # the analysed view's top-N cap, checked against the runs' rows
    scope: str
    pipeline: str
    embedder: str
    oracle_chunkings: tuple[str, ...]  # smallest chunk first: the tie-break order
    setups: tuple[SetupSpec, ...]
    resamples: int
    seed: int
    confidence: float
    reader: ReaderSpec | None = None  # absent: dry runs only
    grader: GraderSpec | None = None

    def as_dict(self) -> dict[str, Any]:
        dataset: dict[str, Any] = {"name": "pooled", "sources": [source.as_dict() for source in self.sources]}
        out = {
            "kind": "answers",
            "run_name": self.run_name,
            "dataset": dataset,
            "sample": str(Path(*self.sample)),
            "view": self.view,
            "budget": self.budget,
            "top_n": self.top_n,
            "scope": self.scope,
            "pipeline": self.pipeline,
            "embedder": self.embedder,
            "oracle_chunkings": list(self.oracle_chunkings),
            "setups": [setup.as_dict() for setup in self.setups],
            "resamples": self.resamples,
            "seed": self.seed,
            "confidence": self.confidence,
        }
        if self.reader is not None:
            out["reader"] = self.reader.as_dict()
        if self.grader is not None:
            out["grader"] = self.grader.as_dict()
        return out


def _parse_reader(raw: dict[str, Any] | None) -> ReaderSpec | None:
    if raw is None:
        return None
    return ReaderSpec(
        model_id=str(raw["model"]["id"]),
        revision=str(raw["model"]["revision"]),
        max_new_tokens=int(raw["max_new_tokens"]),
    )


def _parse_grader(raw: dict[str, Any] | None) -> GraderSpec | None:
    if raw is None:
        return None
    return GraderSpec(
        model=str(raw["model"]),
        effort=str(raw["effort"]),
        prompt=tuple(str(raw["prompt"]).split("/")),
        prompt_sha256=str(raw["prompt_sha256"]),
        questions_per_dataset=int(raw["questions_per_dataset"]),
        seed=int(raw["seed"]),
        pause_seconds=float(raw["pause_seconds"]),
        max_attempts=int(raw["max_attempts"]),
        threshold=float(raw["threshold"]),
    )


def parse_answers_config(raw: dict[str, Any]) -> AnswersConfig:
    try:
        label, sources = _parse_dataset(raw["dataset"])
        if label != "pooled":
            raise ValueError("the answers stage reads every dataset: name the dataset block pooled")
        cfg = AnswersConfig(
            run_name=str(raw["run_name"]),
            sources=sources,
            sample=tuple(str(raw["sample"]).split("/")),
            view=str(raw.get("view", "budget")),
            budget=int(raw["budget"]),
            top_n=int(raw["top_n"]),
            scope=str(raw.get("scope", "collection")),
            pipeline=str(raw.get("pipeline", PRODUCTION_LINE)),
            embedder=str(raw["embedder"]),
            oracle_chunkings=tuple(str(c) for c in raw["oracle_chunkings"]),
            setups=tuple(
                SetupSpec(
                    name=str(setup["name"]),
                    kind=str(setup.get("kind", "packed")),
                    runs=tuple(sorted((str(d), str(r)) for d, r in dict(setup.get("runs", {})).items())),
                    chunking=str(setup["chunking"]) if "chunking" in setup else None,
                    pipeline=str(setup["pipeline"]) if "pipeline" in setup else None,
                )
                for setup in raw["setups"]
            ),
            resamples=int(raw["resamples"]),
            seed=int(raw["seed"]),
            confidence=float(raw["confidence"]),
            reader=_parse_reader(raw.get("reader")),
            grader=_parse_grader(raw.get("grader")),
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f"invalid answers config: {exc}") from exc
    _validate_answers_config(cfg)
    return cfg


def load_answers_config(path: Path) -> AnswersConfig:
    return parse_answers_config(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def _validate_answers_config(cfg: AnswersConfig) -> None:
    if {source.name for source in cfg.sources} != set(DATASETS):
        raise ValueError(f"the answers stage needs the {DATASETS} sources")
    if cfg.view != "budget":
        raise ValueError("the answers stage reads the budget view (ADR 0006)")
    if cfg.budget <= 0 or cfg.top_n <= 0 or cfg.resamples <= 0:
        raise ValueError("budget, top_n and resamples must be positive")
    if not 0 < cfg.confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if not cfg.oracle_chunkings or len(set(cfg.oracle_chunkings)) != len(cfg.oracle_chunkings):
        raise ValueError("oracle_chunkings must be a non-empty list of distinct names, smallest chunk first")
    if SECTION_AWARE not in cfg.oracle_chunkings:
        raise ValueError("oracle_chunkings must include section-aware")
    names = [setup.name for setup in cfg.setups]
    if not names or len(set(names)) != len(names):
        raise ValueError("setups must be a non-empty list with unique names")
    if SECTION_AWARE not in names:
        raise ValueError(f"the difference from {SECTION_AWARE} needs a {SECTION_AWARE} setup")
    for setup in cfg.setups:
        if setup.kind not in SETUP_KINDS:
            raise ValueError(f"setup {setup.name}: kind must be one of {list(SETUP_KINDS)}")
        if setup.kind == "none":
            if setup.runs:
                raise ValueError(f"setup {setup.name}: the no-retrieval floor reads no runs")
            continue
        if set(dict(setup.runs)) != set(DATASETS):
            raise ValueError(f"setup {setup.name}: runs must name each dataset once")
        if setup.kind == "packed" and setup.chunking is None and setup.pipeline is None:
            raise ValueError(f"setup {setup.name}: a packed setup filters by chunking or pipeline")
        if setup.kind == "oracle" and setup.chunking is not None:
            raise ValueError(f"setup {setup.name}: the oracle picks its chunkings itself")
    if cfg.reader is not None and cfg.reader.max_new_tokens <= 0:
        raise ValueError("reader max_new_tokens must be positive")
    if cfg.grader is not None:
        grader = cfg.grader
        if grader.questions_per_dataset <= 0 or grader.questions_per_dataset % 2:
            raise ValueError(
                "grader questions_per_dataset must be positive and even (Natural Questions: half per type)"
            )
        if grader.max_attempts <= 0 or grader.pause_seconds < 0:
            raise ValueError("grader max_attempts must be positive and pause_seconds not negative")
        if not 0 < grader.threshold <= 1:
            raise ValueError("grader threshold must be in (0, 1]")


def answers_config_hash(cfg: AnswersConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def answers_config_yaml(cfg: AnswersConfig) -> str:
    return yaml.safe_dump(cfg.as_dict(), sort_keys=True, default_flow_style=False).rstrip("\n")


# --- the sample ------------------------------------------------------------


@dataclass(frozen=True)
class SampledQuestion:
    question: Question
    dataset: str

    @property
    def short_prompt(self) -> bool:
        """Natural Questions precise questions ask for a short answer."""
        return self.dataset == "nq" and self.question.query_type == PRECISE


@dataclass(frozen=True)
class Sample:
    """The reader sample, in sample order per dataset, with its header."""

    seed: int
    per_dataset: dict[str, tuple[SampledQuestion, ...]] = field(default_factory=dict)


def load_sample(cfg: AnswersConfig, paths: Paths) -> tuple[Sample, dict[str, Document]]:
    """Load both datasets and cut them to the committed reader sample."""
    splits, documents, _ = load_datasets(paths, cfg.sources)
    seed, wanted = read_sample(paths.root.joinpath(*cfg.sample))
    loaded: dict[str, dict[str, Question]] = {dataset: {} for dataset in DATASETS}
    for split in splits:
        for question in split.questions:
            loaded.setdefault(split.dataset, {})[question.question_id] = question
    per_dataset: dict[str, tuple[SampledQuestion, ...]] = {}
    for dataset in DATASETS:
        if dataset not in wanted:
            raise ValueError(f"the sample file holds no {dataset} ids")
        selected = loaded.get(dataset, {})
        missing = [qid for qid in wanted[dataset] if qid not in selected]
        if missing:
            raise ValueError(f"sample question(s) not in the dataset: {missing[:5]}")
        per_dataset[dataset] = tuple(
            SampledQuestion(question=selected[qid], dataset=dataset) for qid in wanted[dataset]
        )
    return Sample(seed=seed, per_dataset=per_dataset), documents


# --- packed spans ----------------------------------------------------------


@dataclass(frozen=True)
class PackedSpan:
    """One packed chunk of a run's packed.parquet, in packed order."""

    doc_id: str
    rank: int
    start: int
    end: int
    tokens: int


def _read_packed_cell(run_dir: Path, pipeline: str, embedder: str, view: str, budget: int, scope: str) -> pa.Table:
    """The packed.parquet rows of one cell, every chunking, validated ranks."""
    path = run_dir / "packed.parquet"
    table = pq.read_table(
        path,
        columns=[
            "question_id",
            "doc_id",
            "pipeline",
            "embedder",
            "chunking",
            "scope",
            "view",
            "budget",
            "rank",
            "start",
            "end",
            "tokens",
        ],
    )
    mask = pc.and_kleene(
        pc.and_kleene(
            pc.and_kleene(pc.equal(table["pipeline"], pipeline), pc.equal(table["embedder"], embedder)),
            pc.and_kleene(pc.equal(table["scope"], scope), pc.equal(table["view"], view)),
        ),
        pc.equal(table["budget"], budget),
    ).fill_null(False)
    table = table.filter(mask)
    if table.num_rows == 0:
        raise ValueError(f"no packed spans for pipeline {pipeline} in {path}")
    return table


def _group_packed(table: pa.Table, chunking: str | None) -> dict[str, tuple[PackedSpan, ...]]:
    """Packed spans by question id (and chunking when given), rank order.
    Ranks must be unique and increasing per question; a single chunking's
    list is 1..n (the packer's output), a merged cell only needs distinct
    ranks (search-all writes one merged list per question)."""
    rows = table.to_pylist()
    if chunking is not None:
        rows = [row for row in rows if row["chunking"] == chunking]
    if not rows:
        raise ValueError(f"no packed spans for chunking {chunking}")
    by_question: dict[str, list[PackedSpan]] = {}
    single_chunking = (
        {row["chunking"] for row in rows} == {chunking} if chunking else len({r["chunking"] for r in rows}) == 1
    )
    for row in rows:
        by_question.setdefault(row["question_id"], []).append(
            PackedSpan(doc_id=row["doc_id"], rank=row["rank"], start=row["start"], end=row["end"], tokens=row["tokens"])
        )
    out: dict[str, tuple[PackedSpan, ...]] = {}
    for question_id, spans in by_question.items():
        spans.sort(key=lambda s: s.rank)
        ranks = [s.rank for s in spans]
        if ranks != sorted(set(ranks)) or ranks[0] != 1:
            raise ValueError(f"packed ranks are not distinct and 1-based for question {question_id}")
        if single_chunking and ranks != list(range(1, len(spans) + 1)):
            raise ValueError(f"packed ranks are not 1..n for question {question_id}")
        out[question_id] = tuple(spans)
    return out


def load_packed(
    run_dir: Path, pipeline: str, embedder: str, chunking: str | None, view: str, budget: int, scope: str
) -> dict[str, tuple[PackedSpan, ...]]:
    """The packed chunks of one cell and chunking, by question id, in packed
    order (chunking None: every chunking merged, ranks unique per question)."""
    return _group_packed(_read_packed_cell(run_dir, pipeline, embedder, view, budget, scope), chunking)


def oracle_picks(
    run_dir: Path,
    chunkings: Sequence[str],
    pipeline: str,
    embedder: str,
    view: str,
    top_n: int,
    budget: int,
    scope: str,
) -> dict[str, str]:
    """Per question, the chunking with the highest retrieval recall at the
    cell, ties to the smaller chunk (the `chunkings` order)."""
    table = pq.read_table(
        run_dir / "results.parquet",
        columns=[
            "question_id",
            "pipeline",
            "embedder",
            "chunking",
            "scope",
            "view",
            "top_n",
            "budget",
            "scored",
            "recall",
        ],
    )
    mask = pc.and_kleene(
        pc.and_kleene(
            pc.and_kleene(
                pc.and_kleene(pc.equal(table["pipeline"], pipeline), pc.equal(table["embedder"], embedder)),
                pc.and_kleene(pc.equal(table["scope"], scope), pc.equal(table["view"], view)),
            ),
            pc.and_kleene(pc.equal(table["top_n"], top_n), pc.equal(table["budget"], budget)),
        ),
        pc.equal(table["scored"], True),
    ).fill_null(False)
    table = table.filter(mask)
    if table.num_rows == 0:
        raise ValueError(f"no scored results at the cell in {run_dir}")
    recall: dict[str, dict[str, float]] = {}
    seen: set[str] = set()
    for question_id, chunking, value in zip(
        table["question_id"].to_pylist(), table["chunking"].to_pylist(), table["recall"].to_pylist(), strict=True
    ):
        recall.setdefault(question_id, {})[chunking] = value
        seen.add(chunking)
    if unknown := seen - set(chunkings):
        raise ValueError(f"chunkings in the results but not in the tie-break order: {sorted(unknown)}")
    picks: dict[str, str] = {}
    for question_id, by_chunking in recall.items():
        ranked = sorted(by_chunking.items(), key=lambda kv: (-kv[1], chunkings.index(kv[0])))
        picks[question_id] = ranked[0][0]
    return picks


def reader_prefixes(
    run_dir: Path,
    chunking: str | None,
    packed: dict[str, tuple[PackedSpan, ...]],
    documents: dict[str, Document],
    paths: Paths,
) -> dict[SpanKey, str] | None:
    """The prefixes the reader receives with the packed chunks: those of the
    side variant of contextual chunks (`prefix_in_budget` in the run's
    config), by span; None for every other chunking, and for a run without
    a manifest (only test fixtures lack one)."""
    manifest = run_dir / "manifest.json"
    if chunking is None or not manifest.is_file():
        return None
    config = json.loads(manifest.read_text(encoding="utf-8"))["config"]
    specs = [_parse_chunking(raw) for raw in config["chunkings"] if raw["name"] == chunking]
    if not specs or not specs[0].prefix_in_budget or specs[0].prefixes is None:
        return None
    spans = [(s.doc_id, s.start, s.end) for question_spans in packed.values() for s in question_spans]
    return load_prefixes(paths.prefixes, specs[0].prefixes, documents, spans, chunking)


def setup_missing(setup: SetupSpec, paths: Paths) -> list[str]:
    """The source files a setup waits for (empty when all are on disk)."""
    if setup.kind == "none":
        return []
    missing = []
    for dataset, run in sorted(setup.runs):
        run_dir = paths.run_dir(run, dataset)
        if not (run_dir / "packed.parquet").is_file():
            missing.append(f"{dataset}: {run} (packed.parquet)")
        elif setup.kind == "oracle" and not (run_dir / "results.parquet").is_file():
            missing.append(f"{dataset}: {run} (results.parquet)")
    return missing


# --- prompts ---------------------------------------------------------------


@dataclass(frozen=True)
class RenderedPrompt:
    dataset: str
    question_id: str
    setup: str
    prompt: str
    prompt_hash: str
    prompt_tokens: int
    template_tokens: int
    context_tokens: int
    chunks: int
    budget: int
    separator_tokens: int  # per chunk: one separator token plus one for cross-boundary effects

    @property
    def within_budget(self) -> bool:
        """The prompt fits the retrieval budget plus the template. Packing
        keeps the chunks' own token count within the budget (checked
        separately, on the packing's token counts); around them the prompt
        adds only the template (instruction, headings, question) and, per
        chunk, one separator token and one for cross-boundary tokenizer
        effects - packing counts chunks with the chunker's tokenizer, and
        re-tokenizing the rendered text differs by at most that."""
        return self.prompt_tokens <= self.budget + self.template_tokens + self.separator_tokens


def render_setup_prompts(
    cfg: AnswersConfig,
    setup: SetupSpec,
    sample: Sample,
    documents: dict[str, Document],
    paths: Paths,
    encoding=None,
) -> list[RenderedPrompt]:
    """Every prompt of one setup, in sample order, without calling a model."""
    separator_tokens = len(TokenText(CHUNK_SEPARATOR, encoding).token_ids)
    packed_by_dataset: dict[str, dict[str, dict[str, tuple[PackedSpan, ...]]]] = {}
    picks_by_dataset: dict[str, dict[str, str]] = {}
    prefixes_by_dataset: dict[str, dict[SpanKey, str]] = {}
    if setup.kind == "oracle":
        for dataset, run in setup.runs:
            run_dir = paths.run_dir(run, dataset)
            picks_by_dataset[dataset] = oracle_picks(
                run_dir, cfg.oracle_chunkings, cfg.pipeline, cfg.embedder, cfg.view, cfg.top_n, cfg.budget, cfg.scope
            )
            cell = _read_packed_cell(run_dir, cfg.pipeline, cfg.embedder, cfg.view, cfg.budget, cfg.scope)
            packed_by_dataset[dataset] = {
                chunking: _group_packed(cell, chunking)
                for chunking in cfg.oracle_chunkings
                if chunking in set(cell["chunking"].to_pylist())
            }
    elif setup.kind == "packed":
        for dataset, run in setup.runs:
            run_dir = paths.run_dir(run, dataset)
            packed = load_packed(
                run_dir, setup.pipeline or cfg.pipeline, cfg.embedder, setup.chunking, cfg.view, cfg.budget, cfg.scope
            )
            packed_by_dataset[dataset] = {"": packed}
            prefixes = reader_prefixes(run_dir, setup.chunking, packed, documents, paths)
            if prefixes is not None:
                prefixes_by_dataset[dataset] = prefixes

    rendered: list[RenderedPrompt] = []
    for dataset in DATASETS:
        if dataset not in sample.per_dataset:
            continue
        sources = packed_by_dataset.get(dataset, {})
        picks = picks_by_dataset.get(dataset, {})
        prefixes = prefixes_by_dataset.get(dataset)
        for sampled in sample.per_dataset[dataset]:
            question = sampled.question
            if setup.kind == "none":
                spans: Sequence[PackedSpan] = ()
            elif setup.kind == "oracle":
                picked = picks.get(question.question_id)
                if picked is None:
                    raise ValueError(f"no scored chunkings at the cell for {question.question_id} in {dataset}")
                if picked not in sources:
                    raise ValueError(f"the oracle picked {picked}, which has no packed spans in {dataset}")
                spans = sources[picked].get(question.question_id, ())
            else:
                spans = sources[""].get(question.question_id, ())
            chunks = tuple(documents[s.doc_id].text[s.start : s.end] for s in spans)
            if prefixes is not None:
                hashes = [documents[s.doc_id].source_hash for s in spans]
                chunks = tuple(
                    search_text(prefixes[(h, s.start, s.end)], text)
                    for h, s, text in zip(hashes, spans, chunks, strict=True)
                )
            retrieval = setup.kind != "none"
            prompt = render_prompt(question.text, chunks, sampled.short_prompt, retrieval=retrieval)
            template = render_prompt(question.text, (), sampled.short_prompt, retrieval=retrieval)
            rendered.append(
                RenderedPrompt(
                    dataset=dataset,
                    question_id=question.question_id,
                    setup=setup.name,
                    prompt=prompt,
                    prompt_hash=prompt_hash(prompt),
                    prompt_tokens=len(TokenText(prompt, encoding)),
                    template_tokens=len(TokenText(template, encoding)),
                    context_tokens=sum(s.tokens for s in spans),
                    chunks=len(chunks),
                    budget=cfg.budget,
                    separator_tokens=len(chunks) * separator_tokens * 2,
                )
            )
    return rendered


# --- the dry run -----------------------------------------------------------


def dry_run(cfg: AnswersConfig, paths: Paths, encoding=None, loader=load_sample) -> dict[str, Any]:
    """Render every prompt of every setup and report token counts, without
    calling a model. Writes runs/<run_name>/dry-run.json (counts and hashes
    only, never prompt text) and returns the report."""
    started = time.monotonic()
    sample, documents = loader(cfg, paths)
    report: dict[str, Any] = {
        "config_hash": answers_config_hash(cfg),
        "template_hash": template_hash(),
        "sample": {
            "seed": sample.seed,
            "counts": {dataset: len(questions) for dataset, questions in sample.per_dataset.items()},
        },
        "setups": {},
    }
    over_budget = 0
    for setup in cfg.setups:
        missing = setup_missing(setup, paths)
        if missing:
            report["setups"][setup.name] = {"pending": missing}
            continue
        prompts = render_setup_prompts(cfg, setup, sample, documents, paths, encoding)
        stats: dict[str, Any] = {}
        for dataset in sorted(sample.per_dataset):
            rows = [p for p in prompts if p.dataset == dataset]
            if not rows:
                continue
            tokens = [p.prompt_tokens for p in rows]
            context = [p.context_tokens for p in rows]
            stats[dataset] = {
                "questions": len(rows),
                "prompt_tokens": {"min": min(tokens), "mean": round(sum(tokens) / len(tokens), 2), "max": max(tokens)},
                "template_tokens_max": max(p.template_tokens for p in rows),
                "context_tokens": {
                    "min": min(context),
                    "mean": round(sum(context) / len(context), 2),
                    "max": max(context),
                },
                "over_budget": sum(1 for p in rows if not p.within_budget),
            }
            if any(p.context_tokens > cfg.budget for p in rows):
                raise ValueError(f"setup {setup.name}: packed chunks exceed the {cfg.budget}-token budget on {dataset}")
            over_budget += stats[dataset]["over_budget"]
        report["setups"][setup.name] = stats
    report["over_budget_prompts"] = over_budget
    report["duration_seconds"] = round(time.monotonic() - started, 3)
    run_dir = paths.run_dir(cfg.run_name)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "dry-run.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def print_dry_run(cfg: AnswersConfig, report: dict[str, Any]) -> None:
    print(f"answers {cfg.run_name}: dry run, template hash {report['template_hash']}")
    for dataset, count in sorted(report["sample"]["counts"].items()):
        print(f"  sample {dataset}: {count} questions")
    for setup in cfg.setups:
        entry = report["setups"][setup.name]
        if "pending" in entry:
            print(f"  {setup.name}: pending (waiting for {', '.join(entry['pending'])})")
            continue
        for dataset, stats in sorted(entry.items()):
            tokens = stats["prompt_tokens"]
            print(
                f"  {setup.name} {dataset}: {stats['questions']} prompts, "
                f"tokens {tokens['min']}-{tokens['max']} (mean {tokens['mean']}), "
                f"context {stats['context_tokens']['max']} max, over budget {stats['over_budget']}"
            )
    print(f"  prompts over budget plus template: {report['over_budget_prompts']}")


# --- answer scores and the R14 scaffold ------------------------------------


ANSWERS_SCHEMA = pa.schema(
    [
        ("dataset", pa.string()),
        ("question_id", pa.string()),
        ("doc_id", pa.string()),
        ("query_type", pa.string()),
        ("setup", pa.string()),
        ("metric", pa.string()),
        ("score", pa.float64()),
        ("secondary", pa.float64()),  # contains-a-reference (NQ precise), null elsewhere
        ("prompt_hash", pa.string()),
        # the reader call's record (null in scaffold rows): latency of the call
        # that produced the answer, even when this run read it from the cache
        ("answer_hash", pa.string()),
        ("latency_seconds", pa.float64()),
        ("prompt_tokens", pa.int64()),
        ("completion_tokens", pa.int64()),
        ("finish_reason", pa.string()),
    ]
)


def write_answers(path: Path, rows: list[dict]) -> None:
    columns = {name: [row.get(name) for row in rows] for name in ANSWERS_SCHEMA.names}
    pq.write_table(pa.Table.from_pydict(columns, schema=ANSWERS_SCHEMA), path)


def read_answers(path: Path) -> list[dict]:
    return pq.read_table(path).to_pylist()


def clustered_mean(values: np.ndarray, cluster: np.ndarray, counts: np.ndarray) -> Estimate:
    """Mean of per-question values with a document-clustered bootstrap: the
    point estimate on the original sample and one mean per resample."""
    n_clusters = counts.shape[1]
    sums = np.zeros(n_clusters)
    np.add.at(sums, cluster, values)
    ones = np.zeros(n_clusters)
    np.add.at(ones, cluster, 1.0)
    weights = np.vstack([np.ones((1, n_clusters)), counts])
    means = (weights @ sums) / (weights @ ones)
    return Estimate(point=float(means[0]), samples=means[1:])


@dataclass(frozen=True)
class SetupEstimate:
    setup: str
    n: int
    score: Estimate
    score_interval: Interval
    difference: Estimate | None
    difference_interval: Interval | None


def analyse_answers(
    scores: Sequence[dict],
    setups: Sequence[str],
    datasets: Sequence[str],
    reference: str = SECTION_AWARE,
    resamples: int = 10000,
    seed: int = 0,
    confidence: float = 0.95,
) -> dict[tuple[str, str], SetupEstimate]:
    """Answer score per setup and dataset (each dataset, then pooled), with
    document-clustered bootstrap CIs and the paired difference from the
    reference setup. A dataset's draws are the same whether it is analysed
    alone or pooled (the resample stratum is the dataset)."""
    by_key: dict[tuple[str, str], dict[str, dict]] = {}
    for row in scores:
        by_key.setdefault((row["dataset"], row["setup"]), {})[row["question_id"]] = row
    groups = ([("pooled", tuple(sorted(datasets)))] if len(datasets) > 1 else []) + [
        (dataset, (dataset,)) for dataset in sorted(datasets)
    ]
    out: dict[tuple[str, str], SetupEstimate] = {}
    for group, members in groups:
        rows_by_setup = {setup: {} for setup in setups}
        for dataset in members:
            for setup in setups:
                rows_by_setup[setup].update(by_key.get((dataset, setup), {}))
        order = sorted(rows_by_setup[setups[0]])
        for setup in setups:
            if not rows_by_setup[setup] and setup != setups[0]:
                continue  # a setup with no rows is absent, not mismatched
            if sorted(rows_by_setup[setup]) != order:
                raise ValueError(f"setups cover different questions in {group}")
        if not order:
            continue
        dataset_of = {qid: rows_by_setup[setups[0]][qid]["dataset"] for qid in order}
        doc_of = {qid: rows_by_setup[setups[0]][qid]["doc_id"] for qid in order}
        docs_by_dataset = {
            dataset: sorted({doc_of[qid] for qid in order if dataset_of[qid] == dataset}) for dataset in members
        }
        offsets = np.cumsum([0] + [len(docs) for docs in docs_by_dataset.values()])
        cluster = np.empty(len(order), dtype=np.int64)
        for i, qid in enumerate(order):
            dataset = dataset_of[qid]
            cluster[i] = docs_by_dataset[dataset].index(doc_of[qid]) + offsets[list(docs_by_dataset).index(dataset)]
        draws = np.hstack(
            [resample_counts(len(docs_by_dataset[dataset]), resamples, seed, dataset) for dataset in docs_by_dataset]
        )
        reference_rows = rows_by_setup[reference]
        for setup in setups:
            if not rows_by_setup[setup]:
                continue  # a setup without rows here gets no estimate (rendered as pending)
            rows = [rows_by_setup[setup][qid] for qid in order]
            values = np.array([row["score"] for row in rows])
            score = clustered_mean(values, cluster, draws)
            difference = difference_interval = None
            if setup != reference and reference_rows:
                diffs = np.array(
                    [row["score"] - reference_rows[qid]["score"] for row, qid in zip(rows, order, strict=True)]
                )
                difference = clustered_mean(diffs, cluster, draws)
                difference_interval = percentile_interval(difference.samples, confidence)
            out[(group, setup)] = SetupEstimate(
                setup=setup,
                n=len(rows),
                score=score,
                score_interval=percentile_interval(score.samples, confidence),
                difference=difference,
                difference_interval=difference_interval,
            )
    return out


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def _signed(value: float) -> str:
    return f"{value:+.4f}"


def _ci(interval: Interval) -> str:
    return f"[{_signed(interval.low)}, {_signed(interval.high)}]"


def render_r14(
    cfg: AnswersConfig,
    cfg_hash: str,
    scores: Sequence[dict],
    reader: dict[str, Any] | None = None,
) -> str:
    """Table R14: answer score per setup and dataset, with document-clustered
    CIs and the difference from section-aware, plus the Natural Questions
    breakdown by query type (short-answer match with contains, token F1)."""
    datasets = sorted({row["dataset"] for row in scores}) or sorted(source.name for source in cfg.sources)
    analysis = analyse_answers(
        scores,
        [setup.name for setup in cfg.setups],
        datasets,
        resamples=cfg.resamples,
        seed=cfg.seed,
        confidence=cfg.confidence,
    )
    lines = [f"# R14 - {cfg.run_name}: answer score per setup and dataset", "", f"Config hash: `{cfg_hash}`", ""]
    lines += ["## Config", "", "```yaml", answers_config_yaml(cfg), "```", ""]
    lines += [
        "## Inputs",
        "",
        f"- reader prompt template hash: `{template_hash()}`",
        f"- reader sample: `{Path(*cfg.sample)}` (seed {cfg.seed})",
    ]
    if reader:
        settings = ", ".join(f"{key} {value}" for key, value in sorted(reader["settings"].items()))
        runtime = ", ".join(f"{name} {value}" for name, value in sorted(reader.get("runtime", {}).items()))
        lines.append(f"- reader: `{reader['model']}` ({settings}; settings hash `{reader['settings_hash']}`)")
        if runtime:
            lines.append(f"- reader runtime: {runtime}")
    else:
        lines.append("- reader: filled by the reader run")
    lines += [
        "",
        "## Answer score per setup and dataset",
        "",
        (
            "Answer score: the dataset's standard answer metric per question (QASPER: answer F1; Natural Questions: "
            "short-answer match on precise questions, token F1 against the long-answer paragraph on context questions). "
            f"CIs: paired bootstrap over documents ({cfg.resamples} resamples, seed {cfg.seed}), percentile intervals "
            f"at {cfg.confidence:.0%}."
        ),
        "",
        "| dataset | setup | n | answer score | CI | difference from section-aware | CI |",
        "|---|---|---|---|---|---|---|",
    ]
    for group in (["pooled"] if len(datasets) > 1 else []) + datasets:
        for setup in cfg.setups:
            estimate = analysis.get((group, setup.name))
            if estimate is None:
                lines.append(f"| {group} | {setup.name} | - | - | - | - | - |")
                continue
            difference = "-" if estimate.difference is None else _signed(estimate.difference.point)
            difference_ci = "-" if estimate.difference_interval is None else _ci(estimate.difference_interval)
            lines.append(
                f"| {group} | {setup.name} | {estimate.n} | {_fmt(estimate.score.point)} | "
                f"{_ci(estimate.score_interval)} | {difference} | {difference_ci} |"
            )
    lines += [
        "",
        "## Natural Questions by query type (point estimates)",
        "",
        (
            "Precise questions: short-answer match, with contains-a-reference as the secondary column. "
            "Context questions: token F1 against the long-answer paragraph."
        ),
        "",
        "| setup | precise n | short-answer match | contains | context n | token F1 |",
        "|---|---|---|---|---|---|",
    ]
    for setup in cfg.setups:
        cells = [setup.name]
        for query_type in (PRECISE, CONTEXT):
            rows = [
                row
                for row in scores
                if row["setup"] == setup.name and row["dataset"] == "nq" and row["query_type"] == query_type
            ]
            if rows:
                cells.append(str(len(rows)))
                cells.append(_fmt(sum(row["score"] for row in rows) / len(rows)))
                if query_type == PRECISE:
                    cells.append(_fmt(sum(row["secondary"] or 0.0 for row in rows) / len(rows)))
            elif query_type == PRECISE:
                cells += ["-", "-", "-"]
            else:
                cells += ["-", "-"]
        lines.append("| " + " | ".join(cells) + " |")
    if reader:
        lines += _latency_section(cfg, scores, reader)
    lines += ["", "No dataset text, prompt or answer is committed: only ids, hashes and scores.", ""]
    return "\n".join(lines)


def _latency_section(cfg: AnswersConfig, scores: Sequence[dict], reader: dict[str, Any]) -> list[str]:
    """Latency per answer (the call that produced it, prefill plus
    generation, one prompt at a time) and generated tokens, per setup and
    dataset; then the run's totals."""
    lines = [
        "",
        "## Reader latency per answer",
        "",
        (
            "Seconds per answer for the call that produced it (prompt prefill plus generation, one prompt at a "
            "time); generated tokens include the stop token; truncated: answers that hit the new-token limit."
        ),
        "",
        (
            "| dataset | setup | n | mean s | median s | p90 s | max s | prompt tokens (mean) | generated tokens (mean) "
            "| truncated |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    datasets = sorted({row["dataset"] for row in scores})
    for group in (["pooled"] if len(datasets) > 1 else []) + datasets:
        for setup in cfg.setups:
            rows = [
                row
                for row in scores
                if row["setup"] == setup.name
                and (group == "pooled" or row["dataset"] == group)
                and row.get("latency_seconds") is not None
            ]
            if not rows:
                continue
            latency = np.array([row["latency_seconds"] for row in rows])
            prompt = np.mean([row["prompt_tokens"] for row in rows])
            generated = np.mean([row["completion_tokens"] for row in rows])
            truncated = sum(1 for row in rows if row["finish_reason"] == "length")
            lines.append(
                f"| {group} | {setup.name} | {len(rows)} | {latency.mean():.2f} | {np.median(latency):.2f} | "
                f"{np.percentile(latency, 90):.2f} | {latency.max():.2f} | {prompt:.0f} | {generated:.1f} | "
                f"{truncated} |"
            )
    totals = reader["totals"]
    lines += [
        "",
        (
            f"- answers: {totals['answers']} from {totals['distinct_prompts']} distinct prompts (setups that "
            f"hand the reader the same chunks share one answer); {totals['calls']} model calls in the run that wrote "
            f"this table, {totals['cached']} answers from the response cache"
        ),
        f"- reader time, the sum of the distinct prompts' latencies: {totals['latency_seconds'] / 3600:.2f} h",
        f"- wall time of the run that wrote this table: {reader['wall_seconds'] / 60:.1f} min",
        (
            f"- tokens: {totals['prompt_tokens']} prompt, {totals['completion_tokens']} generated; "
            "a local model, so no per-call cost"
        ),
    ]
    return lines
