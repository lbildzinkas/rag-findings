"""The retrieval pipelines of a grid run: the production line and its ablations.

- bm25: keyword search only, the chunking's full-text index;
- vector: vector search only, one ranking per embedder;
- hybrid: the BM25 and vector rankings fused by reciprocal rank fusion;
- hybrid-rerank (the production line): hybrid, then the reranker reorders the fused top
  `rerank_depth` (30). The list continues in fused order after them: the
  unreranked tail, there so the fair view can fill the largest budgets.

Every ranking is `search_depth` deep per search, deep enough to fill the
largest budget. Small-to-big ranks (and the reranker scores) the matched
children; packing then returns their parents. All of a question's
reranking is one batch: the uncached (question, chunk) pairs of every
chunking, embedder and search scope, each list contributing only its own
fused top `rerank_depth`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .cache import Cache, SpanKey
from .chunking import Chunk, chunk_text
from .config import PIPELINES, PRODUCTION_LINE, GridConfig
from .documents import Document
from .models import Embedder, EmbedderSpec, ModelSource, RerankerSpec
from .qasper import Question
from .retrieval import BM25Index, VectorIndex, reciprocal_rank_fusion, rerank_head

EMBED_BATCH = 1024  # chunks embedded (and committed to the cache) per step


@dataclass(frozen=True)
class Ranking:
    pipeline: str
    embedder: str | None  # None for BM25
    ranked: list[Chunk]
    reranked: int | None = None  # leading chunks ordered by the reranker (None: no reranker); the tail follows
    scores: tuple[float, ...] | None = None  # the reranker's scores of the head, in ranked order (None: none kept)


@dataclass
class RerankStats:
    pairs_scored: int = 0  # reranker passes: pairs the model scored (cache misses)
    pairs_cached: int = 0
    lists: int = 0
    max_candidates: int = 0  # the most chunks the reranker saw for one ranked list

    def as_dict(self) -> dict[str, int]:
        return {
            "pairs_scored": self.pairs_scored,
            "pairs_cached": self.pairs_cached,
            "lists_reranked": self.lists,
            "max_candidates_per_list": self.max_candidates,
        }


@dataclass
class EmbedStats:
    """Cache misses and hits of the embedding stage, so a manifest records
    how many new vectors a run computed (zero on a fully cached re-run)."""

    chunk_vectors_embedded: int = 0  # chunk texts the model embedded (cache misses)
    chunk_vectors_cached: int = 0
    queries_embedded: int = 0  # question vectors the model embedded (cache misses)
    queries_cached: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "chunk_vectors_embedded": self.chunk_vectors_embedded,
            "chunk_vectors_cached": self.chunk_vectors_cached,
            "queries_embedded": self.queries_embedded,
            "queries_cached": self.queries_cached,
        }


def _log(message: str) -> None:
    print(message, flush=True)


def model_key(spec: EmbedderSpec | RerankerSpec) -> str:
    return f"{spec.model_id}@{spec.revision}"


@dataclass
class Retriever:
    cfg: GridConfig
    documents: dict[str, Document]
    models: ModelSource
    cache: Cache
    lance_dir: Path
    stats: RerankStats = field(default_factory=RerankStats)
    embed_stats: EmbedStats = field(default_factory=EmbedStats)
    truncated: dict[tuple[str, str], float] = field(default_factory=dict)  # (chunking, embedder) -> share

    def __post_init__(self) -> None:
        self._embedders = {name: self.models.embedder(name) for name in self.cfg.embedders}
        self._reranker = self.models.reranker() if PRODUCTION_LINE in self.cfg.pipelines else None
        self._doc_hashes = {doc_id: doc.source_hash for doc_id, doc in self.documents.items()}
        self._vectors: dict[tuple[str, str], VectorIndex] = {}
        self._queries: dict[str, dict[str, np.ndarray]] = {}

    def span(self, chunk: Chunk) -> SpanKey:
        return (self._doc_hashes[chunk.doc_id], chunk.start, chunk.end)

    def _text(self, chunk: Chunk) -> str:
        return chunk_text(self.documents[chunk.doc_id], chunk)

    def index_chunking(self, name: str, units: Sequence[Chunk], log=_log) -> None:
        """Embed one chunking's units under every embedder (from the cache
        where possible), index them, and record the share of units longer
        than each embedder's input limit."""
        texts = [self._text(u) for u in units]
        for embedder_name, embedder in self._embedders.items():
            spec = embedder.spec
            lengths = embedder.input_tokens(texts)
            over = sum(n > spec.max_tokens for n in lengths)
            self.truncated[(name, embedder_name)] = over / len(units) if units else 0.0
            vectors = self._unit_vectors(embedder, units, texts, log, f"{name} x {embedder_name}")
            index = VectorIndex(self.lance_dir, table=f"{name}--{embedder_name}")
            index.build(units, vectors)
            self._vectors[(name, embedder_name)] = index

    def _unit_vectors(self, embedder: Embedder, units: Sequence[Chunk], texts: list[str], log, label: str):
        key = model_key(embedder.spec)
        cached: dict[str, dict[tuple[int, int], np.ndarray]] = {}
        vectors: list[np.ndarray | None] = []
        for unit in units:
            doc_hash = self._doc_hashes[unit.doc_id]
            if doc_hash not in cached:
                cached[doc_hash] = self.cache.vectors(key, doc_hash)
            vectors.append(cached[doc_hash].get((unit.start, unit.end)))
        missing = [i for i, v in enumerate(vectors) if v is None]
        self.embed_stats.chunk_vectors_cached += len(units) - len(missing)
        self.embed_stats.chunk_vectors_embedded += len(missing)
        if missing:
            log(f"  embedding {label}: {len(missing)} of {len(units)} chunks not cached")
        for step in range(0, len(missing), EMBED_BATCH):
            batch = missing[step : step + EMBED_BATCH]
            new = embedder.embed_documents([texts[i] for i in batch])
            self.cache.put_vectors(key, [(self.span(units[i]), v) for i, v in zip(batch, new, strict=True)])
            for i, v in zip(batch, new, strict=True):
                vectors[i] = v
        if not vectors:
            return np.zeros((0, 1), dtype=np.float32)
        return np.stack(vectors).astype(np.float32)

    def embed_questions(self, questions: Sequence[Question]) -> None:
        texts = sorted({q.text for q in questions})
        for name, embedder in self._embedders.items():
            key = model_key(embedder.spec)
            vectors = self.cache.query_vectors(key, texts)
            missing = [t for t in texts if t not in vectors]
            self.embed_stats.queries_cached += len(texts) - len(missing)
            self.embed_stats.queries_embedded += len(missing)
            if missing:
                new = embedder.embed_queries(missing)
                self.cache.put_query_vectors(key, zip(missing, new, strict=True))
                vectors.update(zip(missing, new, strict=True))
            self._queries[name] = vectors

    def rank(
        self, question: Question, chunkings: Sequence[tuple[str, BM25Index]], scopes: Sequence[str]
    ) -> dict[tuple[str, str], list[Ranking]]:
        """Every pipeline's ranking of one question, per (chunking, scope),
        in table order: the production line first, then the ablations."""
        cfg, depth = self.cfg, self.cfg.search_depth
        out: dict[tuple[str, str], list[Ranking]] = {}
        to_rerank: list[tuple[tuple[str, str], str, list[Chunk]]] = []
        for name, bm25_index in chunkings:
            for scope in scopes:
                doc_filter = question.doc_id if scope == "document" else None
                bm25 = [r.chunk for r in bm25_index.search(question.text, depth, doc_filter)]
                rankings = [Ranking("bm25", None, bm25)]
                for embedder in cfg.embedders:
                    query = self._queries[embedder][question.text]
                    vector = [r.chunk for r in self._vectors[(name, embedder)].search(query, depth, doc_filter)]
                    fused = reciprocal_rank_fusion([bm25, vector], cfg.rrf_k)
                    rankings += [Ranking("vector", embedder, vector), Ranking("hybrid", embedder, fused)]
                    to_rerank.append(((name, scope), embedder, fused))
                out[(name, scope)] = rankings
        if self._reranker is not None:
            scores = self._rerank_scores(question.text, [fused[: cfg.rerank_depth] for _, _, fused in to_rerank])
            for key, embedder, fused in to_rerank:
                ranked = rerank_head(fused, cfg.rerank_depth, lambda head: [scores[self.span(c)] for c in head])
                head_scores = tuple(scores[self.span(c)] for c in ranked[: min(cfg.rerank_depth, len(fused))])
                out[key].append(
                    Ranking(
                        PRODUCTION_LINE,
                        embedder,
                        ranked,
                        reranked=min(cfg.rerank_depth, len(fused)),
                        scores=head_scores,
                    )
                )
        order = {p: i for i, p in enumerate(PIPELINES)}
        embedder_order = {e: i for i, e in enumerate(cfg.embedders)}
        for key, rankings in out.items():
            kept = [r for r in rankings if r.pipeline in cfg.pipelines]
            kept.sort(key=lambda r: (order[r.pipeline], embedder_order.get(r.embedder, -1)))
            out[key] = kept
        return out

    def _rerank_scores(self, question: str, heads: Sequence[Sequence[Chunk]]) -> dict[SpanKey, float]:
        assert self._reranker is not None
        key = model_key(self._reranker.spec)
        scores = self.cache.scores(key, question)
        candidates: dict[SpanKey, Chunk] = {}
        for head in heads:
            self.stats.lists += 1
            self.stats.max_candidates = max(self.stats.max_candidates, len(head))
            for chunk in head:
                candidates.setdefault(self.span(chunk), chunk)
        missing = [span for span in candidates if span not in scores]
        self.stats.pairs_cached += len(candidates) - len(missing)
        if missing:
            new = self._reranker.score([(question, self._text(candidates[span])) for span in missing])
            self.cache.put_scores(key, question, zip(missing, new, strict=True))
            scores.update(zip(missing, new, strict=True))
            self.stats.pairs_scored += len(missing)
        return scores
