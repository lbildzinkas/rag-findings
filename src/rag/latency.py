"""`rag latency <config>`: the adoption profile's query path, timed
uncached on a seeded question sample (the v2 verdict, R16).

Each system answers each sampled question through its query path in
three timed stages, with no cache anywhere:

- the query embedding: the model embeds the question;
- the searches: BM25 and vector search of each of the system's chunkings
  in the run's own LanceDB tables, `search_depth` deep, fused by
  reciprocal rank fusion (search-all routing then fuses the chunkings'
  lists by span);
- the reranker: the model scores every distinct pair - one chunking's
  fused top `rerank_depth`, search-all routing's cross-chunking fused top
  `fused_rerank_depth`, or every chunking's top `rerank_depth` for
  confidence routing.

The reranker's search texts (a contextual chunk's stored prefix, a titled
chunk's header, from the chunking's spec in the run manifest) are built
between the timed stages; packing is not timed. One untimed pass per
system and dataset comes first, so model loading and first-call setup
stay out of the numbers.

The output records the hardware and the library versions. `rag verdict`
reads it, so R16 is regenerated from it and never re-measures.
"""

from __future__ import annotations

import hashlib
import json
import platform
import random
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .chunking import Chunk, chunk_text
from .config import ChunkingSpec, DatasetRef, _dataset_dict, _parse_chunking, _parse_dataset
from .contextual import load_prefixes, search_text
from .documents import Document
from .models import Embedder, Models, Reranker, _device
from .paths import Paths
from .pipelines import model_key
from .retrieval import BM25Index, VectorIndex, reciprocal_rank_fusion
from .routers import fuse_by_span
from .run import library_versions, load_datasets
from .titles import chunk_headers

ROUTES = ("single", "search-all", "confidence")


@dataclass(frozen=True)
class SystemSpec:
    name: str
    run: str  # the run under runs/<dataset>/ whose indexes are searched
    chunkings: tuple[str, ...]
    route: str = "single"

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "run": self.run, "chunkings": list(self.chunkings)}
        return out | ({"route": self.route} if self.route != "single" else {})


@dataclass(frozen=True)
class LatencyConfig:
    dataset: str
    sources: tuple[DatasetRef, ...]
    systems: tuple[SystemSpec, ...]
    out: str  # relative to the root
    questions_per_dataset: int = 50
    seed: int = 0
    embedder: str = "nomic"
    rrf_k: int = 60
    rerank_depth: int = 30
    fused_rerank_depth: int = 50
    search_depth: int = 1000

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "latency",
            "dataset": _dataset_dict(self.dataset, self.sources),
            "questions_per_dataset": self.questions_per_dataset,
            "seed": self.seed,
            "embedder": self.embedder,
            "rrf_k": self.rrf_k,
            "rerank_depth": self.rerank_depth,
            "fused_rerank_depth": self.fused_rerank_depth,
            "search_depth": self.search_depth,
            "systems": [s.as_dict() for s in self.systems],
            "out": self.out,
        }


def parse_latency_config(raw: dict[str, Any]) -> LatencyConfig:
    try:
        if raw.get("kind") != "latency":
            raise ValueError("a latency config needs `kind: latency`")
        dataset, sources = _parse_dataset(raw["dataset"])
        cfg = LatencyConfig(
            dataset=dataset,
            sources=sources,
            systems=tuple(
                SystemSpec(
                    name=str(s["name"]),
                    run=str(s["run"]),
                    chunkings=tuple(str(c) for c in s["chunkings"]),
                    route=str(s.get("route", "single")),
                )
                for s in raw["systems"]
            ),
            out=str(raw["out"]),
            questions_per_dataset=int(raw.get("questions_per_dataset", 50)),
            seed=int(raw.get("seed", 0)),
            embedder=str(raw.get("embedder", "nomic")),
            rrf_k=int(raw.get("rrf_k", 60)),
            rerank_depth=int(raw.get("rerank_depth", 30)),
            fused_rerank_depth=int(raw.get("fused_rerank_depth", 50)),
            search_depth=int(raw.get("search_depth", 1000)),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid latency config: {exc}") from exc
    names = [s.name for s in cfg.systems]
    if not names or len(set(names)) != len(names):
        raise ValueError("systems must be a non-empty list of distinct names")
    for s in cfg.systems:
        if s.route not in ROUTES or not s.chunkings or (s.route == "single") != (len(s.chunkings) == 1):
            raise ValueError(f"system {s.name}: a single route searches one chunking, a router several")
    if cfg.questions_per_dataset <= 0:
        raise ValueError("questions_per_dataset must be positive")
    return cfg


def load_latency_config(path: Path) -> LatencyConfig:
    return parse_latency_config(yaml.safe_load(path.read_text(encoding="utf-8")))


def latency_config_hash(cfg: LatencyConfig) -> str:
    canonical = json.dumps(cfg.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sample_questions(questions: Sequence, n: int, seed: int) -> list:
    """`n` questions drawn without replacement, by question id order, the
    same for the same seed."""
    ordered = sorted(questions, key=lambda q: q.question_id)
    return random.Random(seed).sample(ordered, min(n, len(ordered)))


# --- one system's query path ------------------------------------------------


@dataclass
class _Index:
    spec: ChunkingSpec
    bm25: BM25Index
    vectors: VectorIndex


@dataclass(frozen=True)
class Timing:
    embed: float
    search: float
    rerank: float
    pairs: int


def _search_texts(spec: ChunkingSpec, chunks: Sequence[Chunk], documents: dict[str, Document], paths: Paths):
    texts = [chunk_text(documents[c.doc_id], c) for c in chunks]
    if spec.prefixes is not None:
        spans = [(c.doc_id, c.start, c.end) for c in chunks]
        front = load_prefixes(paths.prefixes, spec.prefixes, documents, spans, spec.name)
    elif spec.titles:
        front = chunk_headers(documents, chunks)
    else:
        return texts
    keys = [(documents[c.doc_id].source_hash, c.start, c.end) for c in chunks]
    return [search_text(front[key], text) for key, text in zip(keys, texts, strict=True)]


def time_query(
    cfg: LatencyConfig,
    system: SystemSpec,
    indexes: dict[str, _Index],
    question: str,
    embedder: Embedder,
    reranker: Reranker,
    documents: dict[str, Document],
    paths: Paths,
) -> Timing:
    started = time.perf_counter()
    query = embedder.embed_queries([question])[0]
    embedded = time.perf_counter()
    fused: dict[str, list[Chunk]] = {}
    for name in system.chunkings:
        index = indexes[name]
        bm25 = [r.chunk for r in index.bm25.search(question, cfg.search_depth)]
        vector = [r.chunk for r in index.vectors.search(query, cfg.search_depth)]
        fused[name] = reciprocal_rank_fusion([bm25, vector], cfg.rrf_k)
    if system.route == "search-all":
        across = fuse_by_span(
            [fused[n] for n in system.chunkings], lambda c: (c.doc_id, c.start, c.end), system.chunkings, cfg.rrf_k
        )
        heads = [(name, [chunk]) for chunk, name in across[: cfg.fused_rerank_depth]]
    else:
        heads = [(name, fused[name][: cfg.rerank_depth]) for name in system.chunkings]
    searched = time.perf_counter()
    pairs: dict[tuple[str, int, int], str] = {}  # distinct spans, as the run's reranker batch
    for name, chunks in heads:
        for chunk, text in zip(chunks, _search_texts(indexes[name].spec, chunks, documents, paths), strict=True):
            pairs.setdefault((chunk.doc_id, chunk.start, chunk.end), text)
    built = time.perf_counter()
    reranker.score([(question, text) for text in pairs.values()])
    scored = time.perf_counter()
    return Timing(embed=embedded - started, search=searched - embedded, rerank=scored - built, pairs=len(pairs))


# --- the probe -------------------------------------------------------------


def hardware() -> dict[str, str]:
    def sysctl(name: str) -> str:
        try:
            return subprocess.run(["sysctl", "-n", name], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return "unknown"

    memory = sysctl("hw.memsize")
    mac = platform.mac_ver()[0]
    return {
        "machine": sysctl("hw.model"),
        "chip": sysctl("machdep.cpu.brand_string"),
        "memory": f"{int(memory) / 2**30:.0f} GB" if memory.isdigit() else "unknown",
        "os": f"macOS {mac}" if mac else f"{platform.system()} {platform.release()}",
        "device": _device(),
    }


def _stats(values: Sequence[float]) -> dict[str, float]:
    ms = np.array(values) * 1000.0
    return {
        "mean": round(float(ms.mean()), 1),
        "p50": round(float(np.percentile(ms, 50)), 1),
        "p90": round(float(np.percentile(ms, 90)), 1),
    }


def _open_indexes(cfg: LatencyConfig, paths: Paths, dataset: str) -> dict[str, dict[str, _Index]]:
    out: dict[str, dict[str, _Index]] = {}
    for system in cfg.systems:
        run_dir = paths.run_dir(system.run, dataset)
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        specs = {raw["name"]: _parse_chunking(raw) for raw in manifest["config"]["chunkings"]}
        out[system.name] = {
            name: _Index(
                spec=specs[name],
                bm25=BM25Index(run_dir / "lance", table=name),
                vectors=VectorIndex(run_dir / "lance", table=f"{name}--{cfg.embedder}"),
            )
            for name in system.chunkings
        }
    return out


def run_latency(cfg: LatencyConfig, paths: Paths, models=None) -> Path:
    models = models if models is not None else Models(paths.data)
    embedder, reranker = models.embedder(cfg.embedder), models.reranker()
    splits, documents, _ = load_datasets(paths, cfg.sources)
    by_dataset: dict[str, list] = {}
    for split in splits:
        by_dataset.setdefault(split.dataset, []).extend(split.questions)
    timings: dict[str, list[Timing]] = {s.name: [] for s in cfg.systems}
    counts: dict[str, int] = {}
    for dataset in sorted(by_dataset):
        sample = sample_questions(by_dataset[dataset], cfg.questions_per_dataset, cfg.seed)
        counts[dataset] = len(sample)
        indexes = _open_indexes(cfg, paths, dataset)
        for system in cfg.systems:  # the untimed pass
            time_query(cfg, system, indexes[system.name], sample[0].text, embedder, reranker, documents, paths)
        for done, question in enumerate(sample, start=1):
            for system in cfg.systems:
                timings[system.name].append(
                    time_query(cfg, system, indexes[system.name], question.text, embedder, reranker, documents, paths)
                )
            if done % 10 == 0:
                print(f"  {dataset}: {done}/{len(sample)} questions", flush=True)
    versions = library_versions() | {name: version(name) for name in ("torch", "transformers", "sentence-transformers")}
    report = {
        "config_hash": latency_config_hash(cfg),
        "questions": counts,
        "seed": cfg.seed,
        "warmup": 1,
        "search_depth": cfg.search_depth,
        "hardware": hardware(),
        "versions": dict(sorted(versions.items())),
        "models": {"embedder": model_key(embedder.spec), "reranker": model_key(reranker.spec)},
        "systems": [
            {
                "name": s.name,
                "searches": 2 * len(s.chunkings),
                "pairs": round(float(np.mean([t.pairs for t in timings[s.name]])), 1),
                "embed_ms": _stats([t.embed for t in timings[s.name]]),
                "search_ms": _stats([t.search for t in timings[s.name]]),
                "rerank_ms": _stats([t.rerank for t in timings[s.name]]),
                "total_ms": _stats([t.embed + t.search + t.rerank for t in timings[s.name]]),
            }
            for s in cfg.systems
        ],
    }
    path = paths.root / cfg.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"  latency profile: {path}")
    return path
