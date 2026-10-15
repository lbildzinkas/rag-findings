"""`rag prefixes`: the index-time half of contextual chunks (ADR 0005).

A local model writes one short context prefix per chunk of the configured
chunking (fixed-256 in v2) from one fixed prompt: the document, then the
chunk, then the request for a succinct context. The prompt is a committed
file whose sha256 the config pins, so a prompt edited after the fact
fails the run instead of mixing two prompts in one prefix set.

Document context. A document of at most `context_tokens` tokens (cl100k,
the experiment's one tokenizer) is given whole; a longer one is cut into
the fewest consecutive windows of whole chunks that each fit, of near-equal
size, and each chunk is given the window that holds it. The writer
prefills each document or window once and every chunk in it reuses that
prompt cache.

Store. Prefixes live in a SQLite table under data/ (git-ignored), keyed by
prefix model and revision, prompt hash, document source hash and chunk
span, so any later run can find a chunk's prefix from its span (and
documents with the same text, such as a page several Natural Questions
questions share, share their prefixes). A
document's records commit in one transaction with its row in
`prefix_documents`, so an interrupted run resumes at the first document
without that row and never rewrites a stored prefix. The committed
manifest holds counts, prefix-length statistics, wall time and a digest
of the stored prefixes, never their text.

The model is behind the small `PrefixWriter` interface: the MLX writer
(macOS only, `rag.prefix_model`) in real runs, a fake in tests.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sqlite3
import sys
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import yaml

from .chunking import Chunk, chunk_text, fixed_windows
from .config import ChunkingSpec, DatasetRef, _dataset_dict, _parse_chunking, _parse_dataset
from .documents import Document
from .paths import Paths
from .tokens import TokenText

DOCUMENT_SLOT = "{document}"
CHUNK_SLOT = "{chunk}"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prefixes (
    model TEXT NOT NULL, prompt_hash TEXT NOT NULL, doc_hash TEXT NOT NULL, start INTEGER NOT NULL,
    end INTEGER NOT NULL, prefix TEXT NOT NULL, n_tokens INTEGER NOT NULL, truncated INTEGER NOT NULL,
    context_start INTEGER NOT NULL, context_end INTEGER NOT NULL,
    PRIMARY KEY (model, prompt_hash, doc_hash, start, end)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS prefix_documents (
    model TEXT NOT NULL, prompt_hash TEXT NOT NULL, doc_hash TEXT NOT NULL, n_chunks INTEGER NOT NULL,
    seconds REAL NOT NULL, PRIMARY KEY (model, prompt_hash, doc_hash)
) WITHOUT ROWID;
"""


def _log(line: str) -> None:
    """Progress lines reach a redirected log as they happen."""
    print(line, flush=True)


@dataclass(frozen=True)
class PromptTemplate:
    """The committed prompt: `{document}` then `{chunk}`, each exactly once."""

    text: str

    def __post_init__(self) -> None:
        if self.text.count(DOCUMENT_SLOT) != 1 or self.text.count(CHUNK_SLOT) != 1:
            raise ValueError(f"the prompt must hold {DOCUMENT_SLOT} and {CHUNK_SLOT} exactly once each")
        if self.text.index(DOCUMENT_SLOT) > self.text.index(CHUNK_SLOT):
            raise ValueError(f"the prompt must give {DOCUMENT_SLOT} before {CHUNK_SLOT}")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

    def split(self, context: str) -> tuple[str, str]:
        """The user message around the chunk: (head with the context, tail).
        The file's final newline is not part of the message."""
        message = self.text.removesuffix("\n")
        head, tail = message.split(CHUNK_SLOT)
        return head.replace(DOCUMENT_SLOT, context), tail


@dataclass(frozen=True)
class Prefix:
    text: str
    n_tokens: int  # new tokens the model wrote, end-of-turn excluded
    truncated: bool  # cut at the new-token limit before the model ended its turn


class PrefixWriter(Protocol):
    model_key: str  # model id @ revision

    def write(self, context: str, chunks: Sequence[str]) -> list[Prefix]:
        """One prefix per chunk, every chunk situated in the same context."""
        ...


@dataclass(frozen=True)
class PrefixConfig:
    dataset: str
    sources: tuple[DatasetRef, ...]
    chunking: ChunkingSpec
    model_id: str
    revision: str
    prompt: str  # path of the prompt file, relative to the project root
    prompt_sha256: str
    context_tokens: int
    max_new_tokens: int
    batch_size: int
    seed: int
    manifest: str  # path of the committed manifest, relative to the project root

    @property
    def model_key(self) -> str:
        return f"{self.model_id}@{self.revision}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "prefixes",
            "dataset": _dataset_dict(self.dataset, self.sources),
            "chunking": self.chunking.as_dict(),
            "model": {"id": self.model_id, "revision": self.revision},
            "prompt": self.prompt,
            "prompt_sha256": self.prompt_sha256,
            "context_tokens": self.context_tokens,
            "max_new_tokens": self.max_new_tokens,
            "batch_size": self.batch_size,
            "seed": self.seed,
            "manifest": self.manifest,
        }


def parse_prefix_config(raw: dict[str, Any]) -> PrefixConfig:
    try:
        if raw.get("kind") != "prefixes":
            raise ValueError("a prefix config says `kind: prefixes`")
        label, sources = _parse_dataset(raw["dataset"])
        cfg = PrefixConfig(
            dataset=label,
            sources=sources,
            chunking=_parse_chunking(raw["chunking"]),
            model_id=str(raw["model"]["id"]),
            revision=str(raw["model"]["revision"]),
            prompt=str(raw["prompt"]),
            prompt_sha256=str(raw["prompt_sha256"]),
            context_tokens=int(raw["context_tokens"]),
            max_new_tokens=int(raw["max_new_tokens"]),
            batch_size=int(raw["batch_size"]),
            seed=int(raw["seed"]),
            manifest=str(raw["manifest"]),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"invalid prefix config: {exc}") from exc
    if cfg.chunking.method != "fixed":
        raise ValueError("prefixes are written for fixed chunkings only")
    if len(cfg.revision) != 40:
        raise ValueError("the prefix model's revision must be a full 40-character commit id")
    if min(cfg.context_tokens, cfg.max_new_tokens, cfg.batch_size) <= 0:
        raise ValueError("context_tokens, max_new_tokens and batch_size must be positive")
    if cfg.chunking.chunk_tokens > cfg.context_tokens:
        raise ValueError("a chunk must fit the document context")
    return cfg


def load_prefix_config(path: Path) -> PrefixConfig:
    return parse_prefix_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_prompt(cfg: PrefixConfig, root: Path) -> PromptTemplate:
    """The committed prompt, checked against the hash the config pins."""
    prompt = PromptTemplate((root / cfg.prompt).read_text(encoding="utf-8"))
    if prompt.sha256 != cfg.prompt_sha256:
        raise ValueError(f"{cfg.prompt} hashes to {prompt.sha256}, not the pinned {cfg.prompt_sha256}")
    return prompt


def context_windows(chunks: Sequence[Chunk], limit: int) -> list[tuple[int, int]]:
    """Consecutive groups of whole chunks, as [first, last + 1) chunk index
    ranges: one group when the chunks fit `limit` tokens together, else
    the fewest groups of near-equal size that each fit."""
    if any(c.n_tokens > limit for c in chunks):
        raise ValueError(f"a chunk is longer than the {limit}-token context")
    n = len(chunks)
    if n == 0:
        return []
    groups = max(1, math.ceil(sum(c.n_tokens for c in chunks) / limit))
    while True:
        cuts = [round(i * n / groups) for i in range(groups + 1)]
        bounds = list(pairwise(cuts))
        if all(sum(c.n_tokens for c in chunks[a:b]) <= limit for a, b in bounds):
            return bounds
        groups += 1


@dataclass(frozen=True)
class DocumentChunks:
    dataset: str
    doc: Document
    chunks: tuple[Chunk, ...]


def chunk_documents(
    documents_by_dataset: dict[str, dict[str, Document]], spec: ChunkingSpec, encoding=None
) -> list[DocumentChunks]:
    """Every document's chunks under `spec`, by dataset then document id."""
    out: list[DocumentChunks] = []
    for dataset in sorted(documents_by_dataset):
        documents = documents_by_dataset[dataset]
        for doc_id in sorted(documents):
            doc = documents[doc_id]
            chunks = fixed_windows(doc, TokenText(doc.text, encoding), spec.chunk_tokens)
            out.append(DocumentChunks(dataset, doc, tuple(chunks)))
    return out


def distinct(items: Sequence[DocumentChunks]) -> list[DocumentChunks]:
    """The first document of each source text: documents with the same text
    (several Natural Questions questions share a page) share their prefixes."""
    seen: set[str] = set()
    out: list[DocumentChunks] = []
    for item in items:
        if item.doc.source_hash not in seen:
            seen.add(item.doc.source_hash)
            out.append(item)
    return out


class PrefixStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path))
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def done(self, model: str, prompt_hash: str) -> dict[str, tuple[int, float]]:
        """(chunks, seconds) of every finished document, by source hash."""
        rows = self._db.execute(
            "SELECT doc_hash, n_chunks, seconds FROM prefix_documents WHERE model = ? AND prompt_hash = ?",
            (model, prompt_hash),
        )
        return {h: (n, s) for h, n, s in rows}

    def put_document(
        self,
        model: str,
        prompt_hash: str,
        doc_hash: str,
        records: Sequence[tuple[Chunk, tuple[int, int], Prefix]],
        seconds: float,
    ) -> None:
        """One document's prefixes and its finished row, in one transaction;
        a prefix already stored is never replaced."""
        with self._db:
            self._db.executemany(
                "INSERT OR IGNORE INTO prefixes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (model, prompt_hash, doc_hash, c.start, c.end, p.text, p.n_tokens, int(p.truncated), cs, ce)
                    for c, (cs, ce), p in records
                ],
            )
            self._db.execute(
                "INSERT INTO prefix_documents VALUES (?, ?, ?, ?, ?)",
                (model, prompt_hash, doc_hash, len(records), seconds),
            )

    def prefixes(self, model: str, prompt_hash: str, doc_hash: str) -> dict[tuple[int, int], tuple[str, int, bool]]:
        """(text, new tokens, truncated) of one document's stored prefixes, by chunk span."""
        rows = self._db.execute(
            "SELECT start, end, prefix, n_tokens, truncated FROM prefixes "
            "WHERE model = ? AND prompt_hash = ? AND doc_hash = ?",
            (model, prompt_hash, doc_hash),
        )
        return {(s, e): (text, n, bool(t)) for s, e, text, n, t in rows}


def write_document(item: DocumentChunks, writer: PrefixWriter, context_tokens: int) -> list:
    """Every chunk's prefix, each window of whole chunks prefilled once."""
    records = []
    for first, last in context_windows(item.chunks, context_tokens):
        window = item.chunks[first:last]
        span = (window[0].start, window[-1].end)
        context = item.doc.text[span[0] : span[1]]
        prefixes = writer.write(context, [chunk_text(item.doc, c) for c in window])
        if len(prefixes) != len(window):
            raise ValueError(
                f"{item.doc.doc_id}: the writer returned {len(prefixes)} prefixes for {len(window)} chunks"
            )
        records.extend((c, span, p) for c, p in zip(window, prefixes, strict=True))
    return records


def write_prefixes(
    items: Sequence[DocumentChunks],
    store: PrefixStore,
    writer: PrefixWriter,
    cfg: PrefixConfig,
    prompt_hash: str,
    log: Callable[[str], None] = _log,
) -> int:
    """Write and commit, one document at a time, the prefixes of every
    document text not yet finished; returns the number of documents written."""
    items = distinct(items)
    done = store.done(writer.model_key, prompt_hash)
    todo = [item for item in items if item.doc.source_hash not in done]
    total_chunks = sum(len(item.chunks) for item in items)
    stored = sum(len(item.chunks) for item in items if item.doc.source_hash in done)
    started = time.perf_counter()
    written_chunks = 0
    for i, item in enumerate(todo, start=1):
        tic = time.perf_counter()
        records = write_document(item, writer, cfg.context_tokens)
        seconds = time.perf_counter() - tic
        store.put_document(writer.model_key, prompt_hash, item.doc.source_hash, records, seconds)
        written_chunks += len(item.chunks)
        rate = (time.perf_counter() - started) / written_chunks
        left = total_chunks - stored - written_chunks
        log(
            f"[{i}/{len(todo)}] {item.dataset} {item.doc.doc_id}: {len(item.chunks)} chunks in {seconds:.1f} s; "
            f"{stored + written_chunks}/{total_chunks} chunks stored, about {left * rate / 3600:.1f} h left"
        )
    return len(todo)


def estimate_sample(items: Sequence[DocumentChunks], n: int, seed: int) -> list[DocumentChunks]:
    """`n` seeded documents of each dataset, distinct texts only."""
    out: list[DocumentChunks] = []
    items = distinct(items)
    for dataset in sorted({item.dataset for item in items}):
        pool = [item for item in items if item.dataset == dataset]
        out.extend(random.Random(f"{seed}:{dataset}").sample(pool, min(n, len(pool))))
    return out


def projected_hours(
    items: Sequence[DocumentChunks], sample: Sequence[DocumentChunks], done: dict[str, tuple[int, float]]
) -> dict[str, dict[str, float]]:
    """Per dataset: seconds per chunk over the sample, and the projected
    hours of the full run and of what is not yet stored, over the chunks
    of distinct texts (the prefixes to write)."""
    out: dict[str, dict[str, float]] = {}
    items = distinct(items)
    for dataset in sorted({item.dataset for item in items}):
        picked = [done[item.doc.source_hash] for item in sample if item.dataset == dataset]
        per_chunk = sum(s for _, s in picked) / sum(n for n, _ in picked)
        pool = [item for item in items if item.dataset == dataset]
        chunks = sum(len(item.chunks) for item in pool)
        left = sum(len(item.chunks) for item in pool if item.doc.source_hash not in done)
        out[dataset] = {
            "documents": len(picked),
            "seconds_per_chunk": per_chunk,
            "chunks": chunks,
            "hours": per_chunk * chunks / 3600,
            "hours_left": per_chunk * left / 3600,
        }
    return out


def _length_stats(lengths: Sequence[int]) -> dict[str, float]:
    if not lengths:
        return {}
    values = np.asarray(lengths)
    quantiles = {f"p{q}": float(np.percentile(values, q)) for q in (10, 50, 90, 99)}
    return {"min": int(values.min()), **quantiles, "max": int(values.max()), "mean": round(float(values.mean()), 2)}


def build_manifest(
    items: Sequence[DocumentChunks],
    store: PrefixStore,
    cfg: PrefixConfig,
    prompt_hash: str,
    runtime: dict[str, str],
) -> dict[str, Any]:
    """Counts, prefix-length statistics (in the prefix model's tokens), the
    chunks cut at the new-token limit or left without a prefix (by document
    id and chunk index), wall time and a digest of every stored prefix; no
    prefix text. Lengths, wall time and the digest count each distinct
    text's prefixes once; the chunk counts cover every document."""
    done = store.done(cfg.model_key, prompt_hash)
    firsts = {id(item) for item in distinct(items)}
    digest = hashlib.sha256()
    datasets: dict[str, dict[str, Any]] = {}
    truncated: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    all_lengths: list[int] = []
    for dataset in sorted({item.dataset for item in items}):
        pool = [item for item in items if item.dataset == dataset]
        lengths: list[int] = []
        with_prefix = windowed = 0
        for item in sorted(pool, key=lambda it: (it.doc.source_hash, it.doc.doc_id)):
            stored = store.prefixes(cfg.model_key, prompt_hash, item.doc.source_hash)
            is_first = id(item) in firsts
            windowed += is_first and len(context_windows(item.chunks, cfg.context_tokens)) > 1
            for chunk in item.chunks:
                record = stored.get((chunk.start, chunk.end))
                where = {"dataset": dataset, "doc_id": item.doc.doc_id, "chunk": chunk.index}
                if record is None or not record[0].strip():
                    missing.append(where)
                    continue
                text, n_tokens, cut = record
                with_prefix += 1
                if cut:
                    truncated.append(where)
                if is_first:
                    lengths.append(n_tokens)
                    digest.update(f"{item.doc.source_hash}\t{chunk.start}\t{chunk.end}\t{text}\n".encode())
        written = [item for item in pool if id(item) in firsts]
        datasets[dataset] = {
            "documents": len(pool),
            "distinct_documents": len(written),
            "documents_in_windows": windowed,
            "chunks": sum(len(item.chunks) for item in pool),
            "chunks_with_prefix": with_prefix,
            "distinct_prefixes": len(lengths),
            "truncated": sum(1 for t in truncated if t["dataset"] == dataset),
            "prefix_tokens": _length_stats(lengths),
            "wall_hours": round(sum(done.get(item.doc.source_hash, (0, 0.0))[1] for item in written) / 3600, 3),
        }
        all_lengths.extend(lengths)
    return {
        "config": cfg.as_dict(),
        "model": {"id": cfg.model_id, "revision": cfg.revision},
        "prompt_sha256": prompt_hash,
        "runtime": runtime,
        "store": {"table": "prefixes", "key": ["model", "prompt_hash", "doc_hash", "start", "end"]},
        "datasets": datasets,
        "chunks": sum(d["chunks"] for d in datasets.values()),
        "chunks_with_prefix": sum(d["chunks_with_prefix"] for d in datasets.values()),
        "distinct_prefixes": len(all_lengths),
        "prefix_tokens": _length_stats(all_lengths),
        "truncated": truncated,
        "missing": missing,
        "wall_hours": round(sum(d["wall_hours"] for d in datasets.values()), 3),
        "prefix_digest": digest.hexdigest(),
    }


def _runtime() -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version

    out: dict[str, str] = {}
    for package in ("mlx", "mlx-lm"):
        try:
            out[package] = version(package)
        except PackageNotFoundError:
            pass
    return out


def load_documents(paths: Paths, sources: Iterable[DatasetRef]) -> dict[str, dict[str, Document]]:
    from .run import load_datasets

    return {source.name: load_datasets(paths, (source,))[1] for source in sources}


def run_prefixes(
    cfg: PrefixConfig,
    paths: Paths,
    writer: PrefixWriter | None = None,
    estimate: int | None = None,
    encoding=None,
    log: Callable[[str], None] = _log,
) -> dict[str, Any]:
    """Write every missing prefix (or, with `estimate`, a seeded sample's
    and the projected hours), then the manifest; returns the manifest or
    the projection. The real writer is loaded only when there is work."""
    prompt = load_prompt(cfg, paths.root)
    items = chunk_documents(load_documents(paths, cfg.sources), cfg.chunking, encoding)
    store = PrefixStore(paths.prefixes)
    try:
        sample = estimate_sample(items, estimate, cfg.seed) if estimate is not None else items
        done = store.done(cfg.model_key, prompt.sha256)
        if any(item.doc.source_hash not in done for item in sample):
            if writer is None:
                from .prefix_model import load_writer

                writer = load_writer(cfg, paths.data, prompt)
            if writer.model_key != cfg.model_key:
                raise ValueError(f"the writer is {writer.model_key}, the config names {cfg.model_key}")
            write_prefixes(sample, store, writer, cfg, prompt.sha256, log)
        if estimate is not None:
            projection = projected_hours(items, sample, store.done(cfg.model_key, prompt.sha256))
            for dataset, p in projection.items():
                log(
                    f"{dataset}: {p['documents']} sampled documents, {p['seconds_per_chunk']:.2f} s per chunk; "
                    f"{p['chunks']} chunks, projected {p['hours']:.1f} h ({p['hours_left']:.1f} h not yet stored)"
                )
            total = sum(p["hours"] for p in projection.values())
            left = sum(p["hours_left"] for p in projection.values())
            log(f"projected full run: {total:.1f} h ({left:.1f} h not yet stored)")
            return projection
        manifest = build_manifest(items, store, cfg, prompt.sha256, _runtime())
    finally:
        store.close()
    out = paths.root / cfg.manifest
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    log(
        f"{manifest['chunks_with_prefix']}/{manifest['chunks']} chunks have a prefix "
        f"({manifest['distinct_prefixes']} distinct); "
        f"{len(manifest['truncated'])} cut at {cfg.max_new_tokens} tokens; manifest {cfg.manifest}"
    )
    if manifest["missing"]:
        print(f"{len(manifest['missing'])} chunks have no prefix (see the manifest)", file=sys.stderr)
    return manifest
