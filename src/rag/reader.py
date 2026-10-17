"""The reader prompt and the reader interface with its response cache.

One fixed prompt, written before any result (ADR 0009): the instruction
"Answer the question from the context only, briefly.", then the packed
chunks in packed order under a Context heading, then the question.
Natural Questions precise questions add "Give a short answer."; the
no-retrieval floor uses the same template with the context section and
"from the context only" removed. The template's sha256 is recorded in
every manifest before any answer exists, and tests/test_reader.py pins
it, so changing the prompt is a visible change.

The reader itself is an interface: `read(prompt) -> answer`, or a
`Reading` (the answer plus its call record: latency, token counts,
finish reason). A `CachedReader` wraps a backend model with the SQLite
response cache under data/ (keyed by model, settings hash and prompt
hash; the call record is stored beside the answer), so an interrupted
run resumes free and a warm re-run reports the original latencies; a
`LazyReader` loads the backend only on the first cache miss, so a warm
re-run never loads the model; a `FakeReader` serves tests. The model
client is rag.reader_model (local, MLX).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

INSTRUCTION = "Answer the question from the context only, briefly."
SHORT_INSTRUCTION = "Give a short answer."
FLOOR_INSTRUCTION = "Answer the question, briefly."
CONTEXT_HEADING = "Context:"
QUESTION_PREFIX = "Question:"
CHUNK_SEPARATOR = "\n\n"

TEMPLATE_PARTS = (
    INSTRUCTION,
    SHORT_INSTRUCTION,
    FLOOR_INSTRUCTION,
    CONTEXT_HEADING,
    QUESTION_PREFIX,
    CHUNK_SEPARATOR,
)


def template_hash() -> str:
    """sha256 of the fixed template parts, recorded before any answer exists."""
    return hashlib.sha256("\x1f".join(TEMPLATE_PARTS).encode("utf-8")).hexdigest()


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def settings_hash(model: str, settings: dict) -> str:
    """sha256 of the model and its generation settings (canonical JSON)."""
    canonical = json.dumps({"model": model, "settings": settings}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def instruction(short: bool, retrieval: bool) -> str:
    base = INSTRUCTION if retrieval else FLOOR_INSTRUCTION
    return f"{base} {SHORT_INSTRUCTION}" if short else base


def render_prompt(question: str, chunks: tuple[str, ...], short: bool, retrieval: bool = True) -> str:
    """The reader prompt: instruction, the packed chunks in packed order,
    then the question. The floor drops the context section."""
    lines = [instruction(short, retrieval)]
    if retrieval:
        lines.append("")
        lines.append(CONTEXT_HEADING)
        for chunk in chunks:
            lines.append("")
            lines.append(chunk)
    lines.append("")
    lines.append(f"{QUESTION_PREFIX} {question}")
    return "\n".join(lines)


@dataclass(frozen=True)
class Reading:
    """One answer and its call record (latency, token counts, finish
    reason; empty for a backend that records none). `cached` is True when
    the answer came from the response cache, not a model call."""

    answer: str
    meta: dict[str, Any] = field(default_factory=dict)
    cached: bool = False


class ResponseCache:
    """SQLite cache of reader answers under data/, keyed by model, settings
    hash and prompt hash, with each call's record as JSON (git-ignored;
    holds answer text, never keys)."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path))
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS responses (
                model TEXT NOT NULL, settings_hash TEXT NOT NULL, prompt_hash TEXT NOT NULL,
                answer TEXT NOT NULL, meta TEXT NOT NULL DEFAULT '{}',
                PRIMARY KEY (model, settings_hash, prompt_hash)
            ) WITHOUT ROWID;
            """
        )

    def close(self) -> None:
        self._db.close()

    def get_reading(self, model: str, settings: str, prompt: str) -> Reading | None:
        row = self._db.execute(
            "SELECT answer, meta FROM responses WHERE model = ? AND settings_hash = ? AND prompt_hash = ?",
            (model, settings, prompt_hash(prompt)),
        ).fetchone()
        return None if row is None else Reading(answer=row[0], meta=json.loads(row[1]), cached=True)

    def get(self, model: str, settings: str, prompt: str) -> str | None:
        reading = self.get_reading(model, settings, prompt)
        return None if reading is None else reading.answer

    def put(self, model: str, settings: str, prompt: str, answer: str, meta: dict[str, Any] | None = None) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO responses VALUES (?, ?, ?, ?, ?)",
            (model, settings, prompt_hash(prompt), answer, json.dumps(meta or {}, sort_keys=True)),
        )
        self._db.commit()


class Reader(Protocol):
    """The language model that answers a question from the retrieved chunks:
    an answer string, or a `Reading` carrying the call record too."""

    def read(self, prompt: str) -> str | Reading: ...


def as_reading(result: str | Reading) -> Reading:
    return result if isinstance(result, Reading) else Reading(answer=result)


class FakeReader:
    """A deterministic reader for tests: answers from a fixed mapping."""

    def __init__(self, answers: dict[str, str] | None = None, default: str = "fake answer"):
        self.answers = answers or {}
        self.default = default
        self.prompts: list[str] = []

    def read(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answers.get(prompt_hash(prompt), self.default)


class LazyReader:
    """A backend loaded on the first read, so a run served wholly from the
    cache never loads the model; `loads` counts the loads."""

    def __init__(self, load: Callable[[], Reader]):
        self._load = load
        self._backend: Reader | None = None
        self.loads = 0

    def read(self, prompt: str) -> str | Reading:
        if self._backend is None:
            self._backend = self._load()
            self.loads += 1
        return self._backend.read(prompt)


class CachedReader:
    """A reader whose answers persist in the response cache: a hit never
    calls the backend, a miss is stored on its way back. `calls` counts
    the backend calls."""

    def __init__(self, cache: ResponseCache, model: str, settings: str, backend: Reader | None = None):
        self.cache = cache
        self.model = model
        self.settings = settings
        self.backend = backend
        self.calls = 0

    def reading(self, prompt: str) -> Reading:
        cached = self.cache.get_reading(self.model, self.settings, prompt)
        if cached is not None:
            return cached
        if self.backend is None:
            raise RuntimeError("no reader backend configured and the answer is not cached")
        reading = as_reading(self.backend.read(prompt))
        self.calls += 1
        self.cache.put(self.model, self.settings, prompt, reading.answer, reading.meta)
        return reading

    def read(self, prompt: str) -> str:
        return self.reading(prompt).answer
