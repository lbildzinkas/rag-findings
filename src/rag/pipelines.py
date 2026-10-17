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

A late chunking (see rag.late) is indexed from vectors pooled out of
whole-document token embeddings, cached under the model key plus
`#late-8192`; its BM25 index, reranker scores, packing and scoring are
those of the fixed chunking with the same spans.

A contextual chunking (see rag.contextual) is searched by its search text,
prefix and chunk text: BM25 (built by the grid), its vectors and its
reranker pairs read it, and its vectors and scores are cached under the
model key plus the prefix set's id. Packing and scoring see only the
chunk's span.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .cache import Cache, SpanKey
from .chunking import Chunk, chunk_text
from .config import PIPELINES, PRODUCTION_LINE, GridConfig
from .contextual import search_text
from .documents import Document
from .late import LATE_KEY_SUFFIX, LATE_WINDOW, Span, WindowStats, late_vectors, plan_windows
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
    late_windows_embedded: int = 0  # late chunking: windows the model read (documents not fully cached)

    def as_dict(self) -> dict[str, int]:
        out = {
            "chunk_vectors_embedded": self.chunk_vectors_embedded,
            "chunk_vectors_cached": self.chunk_vectors_cached,
            "queries_embedded": self.queries_embedded,
            "queries_cached": self.queries_cached,
        }
        return out | ({"late_windows_embedded": self.late_windows_embedded} if self.late_windows_embedded else {})


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
    late_windows: dict[str, WindowStats] = field(default_factory=dict)  # embedder -> late chunking's windows
    # contextual chunkings: name -> (cache key suffix, prefix by span)
    contextual: dict[str, tuple[str, dict[SpanKey, str]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._embedders = {name: self.models.embedder(name) for name in self.cfg.embedders}
        self._reranker = self.models.reranker() if PRODUCTION_LINE in self.cfg.pipelines else None
        self._doc_hashes = {doc_id: doc.source_hash for doc_id, doc in self.documents.items()}
        self._vectors: dict[tuple[str, str], VectorIndex] = {}
        self._queries: dict[str, dict[str, np.ndarray]] = {}

    def span(self, chunk: Chunk) -> SpanKey:
        return (self._doc_hashes[chunk.doc_id], chunk.start, chunk.end)

    def key_suffix(self, chunking: str | None) -> str:
        """The cache-key suffix of a chunking's vectors and reranker scores
        (empty except for contextual chunkings)."""
        return self.contextual[chunking][0] if chunking in self.contextual else ""

    def search_text(self, chunk: Chunk, chunking: str | None = None) -> str:
        """What search reads for a chunk: its text, or for a contextual
        chunking its prefix, a blank line and its text."""
        text = chunk_text(self.documents[chunk.doc_id], chunk)
        if chunking not in self.contextual:
            return text
        return search_text(self.contextual[chunking][1][self.span(chunk)], text)

    def index_chunking(self, name: str, units: Sequence[Chunk], log=_log) -> None:
        """Embed one chunking's units under every embedder (from the cache
        where possible), index them, and record the share of units longer
        than each embedder's input limit."""
        texts = [self.search_text(u, name) for u in units]
        for embedder_name, embedder in self._embedders.items():
            spec = embedder.spec
            lengths = embedder.input_tokens(texts)
            over = sum(n > spec.max_tokens for n in lengths)
            self.truncated[(name, embedder_name)] = over / len(units) if units else 0.0
            key = model_key(spec) + self.key_suffix(name)
            vectors = self._unit_vectors(embedder, key, units, texts, log, f"{name} x {embedder_name}")
            index = VectorIndex(self.lance_dir, table=f"{name}--{embedder_name}")
            index.build(units, vectors)
            self._vectors[(name, embedder_name)] = index

    def _unit_vectors(self, embedder: Embedder, key: str, units: Sequence[Chunk], texts: list[str], log, label: str):
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

    def index_late(self, chunkings: Sequence[tuple[str, Sequence[Chunk]]], blocks: dict[str, list[Span]], log=_log):
        """Embed and index the late chunkings under every embedder: per
        document, one model pass per window serves all of them. A document
        whose late vectors are all cached is not read again; its windows
        are still planned, so the manifest's window counts never depend on
        the cache."""
        by_doc: list[dict[str, list[Chunk]]] = []
        for _, units in chunkings:
            groups: dict[str, list[Chunk]] = {}
            for unit in units:
                groups.setdefault(unit.doc_id, []).append(unit)
            by_doc.append(groups)
        for embedder_name, embedder in self._embedders.items():
            key = model_key(embedder.spec) + LATE_KEY_SUFFIX
            stats = self.late_windows.setdefault(embedder_name, WindowStats())
            vectors: dict[tuple[int, str, int, int], np.ndarray] = {}
            for doc_id in sorted(self.documents):
                doc, doc_hash = self.documents[doc_id], self._doc_hashes[doc_id]
                spans = [[(u.start, u.end) for u in groups.get(doc_id, [])] for groups in by_doc]
                windows = plan_windows(doc.text, blocks[doc_id], embedder.input_tokens, LATE_WINDOW)
                stats.add(windows)
                cached = self.cache.vectors(key, doc_hash)
                wanted = {span for doc_spans in spans for span in doc_spans}
                if wanted <= cached.keys():
                    self.embed_stats.chunk_vectors_cached += sum(map(len, spans))
                else:
                    pooled = late_vectors(doc.text, spans, windows, embedder, stats)  # type: ignore[arg-type]
                    new = {
                        span: v
                        for doc_spans, vs in zip(spans, pooled, strict=True)
                        for span, v in zip(doc_spans, vs, strict=True)
                    }
                    self.cache.put_vectors(key, [((doc_hash, s, e), v) for (s, e), v in new.items()])
                    cached = new
                    self.embed_stats.chunk_vectors_embedded += sum(map(len, spans))
                    self.embed_stats.late_windows_embedded += len(windows)
                for c, doc_spans in enumerate(spans):
                    for s, e in doc_spans:
                        vectors[(c, doc_id, s, e)] = cached[(s, e)]
            if self.embed_stats.late_windows_embedded:
                log(f"  late chunking x {embedder_name}: {self.embed_stats.late_windows_embedded} windows embedded")
            for c, (name, units) in enumerate(chunkings):
                rows = [vectors[(c, u.doc_id, u.start, u.end)] for u in units]
                index = VectorIndex(self.lance_dir, table=f"{name}--{embedder_name}")
                index.build(units, np.stack(rows).astype(np.float32) if rows else np.zeros((0, 1), dtype=np.float32))
                self._vectors[(name, embedder_name)] = index
                self.truncated[(name, embedder_name)] = 0.0  # no window exceeds the embedder's input

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
            # one batch per cache key: chunkings with the same search texts share their scores
            by_suffix: dict[str, list[tuple[tuple[str, str], str, list[Chunk]]]] = {}
            for entry in to_rerank:
                by_suffix.setdefault(self.key_suffix(entry[0][0]), []).append(entry)
            scores: dict[tuple[str, SpanKey], float] = {}
            for suffix, entries in by_suffix.items():
                heads = [fused[: cfg.rerank_depth] for _, _, fused in entries]
                found = self._rerank_scores(question.text, heads, chunking=entries[0][0][0])
                scores.update(((suffix, span), score) for span, score in found.items())
            for key, embedder, fused in to_rerank:
                suffix = self.key_suffix(key[0])
                ranked = rerank_head(
                    fused, cfg.rerank_depth, lambda head, s=suffix: [scores[(s, self.span(c))] for c in head]
                )
                head = ranked[: min(cfg.rerank_depth, len(fused))]
                head_scores = tuple(scores[(suffix, self.span(c))] for c in head)
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

    def _rerank_scores(
        self, question: str, heads: Sequence[Sequence[Chunk]], chunking: str | None = None
    ) -> dict[SpanKey, float]:
        """Reranker scores of every chunk in `heads`, from the cache where
        possible, under `chunking`'s cache key and search texts (every head
        must share them)."""
        assert self._reranker is not None
        key = model_key(self._reranker.spec) + self.key_suffix(chunking)
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
            new = self._reranker.score([(question, self.search_text(candidates[span], chunking)) for span in missing])
            self.cache.put_scores(key, question, zip(missing, new, strict=True))
            scores.update(zip(missing, new, strict=True))
            self.stats.pairs_scored += len(missing)
        return scores
