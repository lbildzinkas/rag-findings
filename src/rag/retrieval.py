"""Retrieval: BM25 with a LanceDB full-text index, vector search with a
LanceDB vector table, reciprocal rank fusion, and reranking.

All papers' chunks of one chunking go into one table (one per embedder for
vectors). A search runs over the whole collection, or, given a document id,
only within that document (the table is prefiltered to it; BM25 statistics
stay those of the collection). Vector search is exact (a flat scan, no
approximate index) by cosine similarity.

Search results are deterministic everywhere a ranked list is cut: rows are
re-sorted by (-score, doc_id, chunk index), and the search over-fetches
past the cutoff, extending the fetch while the engine's arbitrary tie
order could still decide which tied rows make the cut (see
`_deterministic_cut`); the scoring itself is untouched.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .chunking import Chunk

_CHUNK_COLUMNS = ["doc_id", "chunk_index", "start", "end", "token_start", "token_end", "n_tokens", "parent_index"]


@dataclass(frozen=True)
class RankedChunk:
    chunk: Chunk
    score: float

    @property
    def doc_id(self) -> str:
        return self.chunk.doc_id

    @property
    def index(self) -> int:
        return self.chunk.index


def _row(chunk: Chunk) -> dict:
    return {
        "doc_id": chunk.doc_id,
        "chunk_index": chunk.index,
        "start": chunk.start,
        "end": chunk.end,
        "token_start": chunk.token_start,
        "token_end": chunk.token_end,
        "n_tokens": chunk.n_tokens,
        "parent_index": chunk.parent_index,
    }


def _ranked(rows: list[dict], scores: list[float]) -> list[RankedChunk]:
    ranked = [
        RankedChunk(
            chunk=Chunk(
                doc_id=row["doc_id"],
                index=row["chunk_index"],
                start=row["start"],
                end=row["end"],
                token_start=row["token_start"],
                token_end=row["token_end"],
                n_tokens=row["n_tokens"],
                parent_index=row.get("parent_index", -1),
            ),
            score=score,
        )
        for row, score in zip(rows, scores, strict=True)
    ]
    ranked.sort(key=lambda r: (-r.score, r.doc_id, r.index))
    return ranked


def _doc_filter(doc_id: str) -> str:
    escaped = doc_id.replace("'", "''")
    return f"doc_id = '{escaped}'"


_OVERFETCH = 64  # rows fetched past the cutoff before ties force an extension


def _deterministic_cut(fetch: Callable[[int], list[RankedChunk]], limit: int) -> list[RankedChunk]:
    """The top `limit` of the engine's ranking, the same every run.

    `fetch(n)` returns the engine's top `n` rows re-sorted by
    (-score, doc_id, chunk index). The engine cuts its top `n` by score in
    an arbitrary tie order, and that cut is the one place a ranked list
    can flip between identical runs (the re-sort cannot fix which tied
    rows were kept). So fetch past the cutoff and keep extending the fetch
    while the worst fetched score still ties the score at the cutoff: once
    it is strictly below, every unfetched row scores at most that too, so
    no tie can straddle the cut and the first `limit` re-sorted rows are
    stable whatever tie subset the engine happened to return.
    """
    if limit <= 0:
        return []
    n = limit + _OVERFETCH
    while True:
        ranked = fetch(n)
        if len(ranked) < n or len(ranked) <= limit or ranked[limit - 1].score > ranked[-1].score:
            return ranked[:limit]
        n *= 2


class BM25Index:
    """A LanceDB full-text index over every chunk of the collection."""

    def __init__(self, path: Path, table: str = "chunks"):
        import lancedb

        self._db = lancedb.connect(str(path))
        self._table = table

    def build(self, chunks: list[Chunk], texts: dict[str, str]) -> None:
        """Index chunks in a deterministic order (doc_id, chunk index)."""
        from lancedb.index import FTS

        rows = [
            {**_row(chunk), "text": texts[f"{chunk.doc_id}:{chunk.index}"]}
            for chunk in sorted(chunks, key=lambda c: (c.doc_id, c.index))
        ]
        table = self._db.create_table(self._table, data=rows, mode="overwrite")
        table.create_index("text", config=FTS())

    def search(self, query: str, limit: int, doc_id: str | None = None) -> list[RankedChunk]:
        """Return up to `limit` chunks ranked by BM25, deterministically;
        only chunks of `doc_id` when it is given."""
        table = self._db.open_table(self._table)

        def fetch(n: int) -> list[RankedChunk]:
            search = table.search(query, query_type="fts")
            if doc_id is not None:
                search = search.where(_doc_filter(doc_id), prefilter=True)
            rows = search.limit(n).to_list()
            return _ranked(rows, [float(row["_score"]) for row in rows])

        return _deterministic_cut(fetch, limit)


class VectorIndex:
    """A LanceDB table of one chunking's chunk vectors under one embedder,
    searched exactly by cosine similarity."""

    def __init__(self, path: Path, table: str):
        import lancedb

        self._db = lancedb.connect(str(path))
        self._table = table

    def build(self, chunks: Sequence[Chunk], vectors: np.ndarray) -> None:
        """Index chunks with their vectors (row i of `vectors` is chunks[i])."""
        import pyarrow as pa

        if len(chunks) != len(vectors):
            raise ValueError(f"{len(chunks)} chunks but {len(vectors)} vectors")
        order = sorted(range(len(chunks)), key=lambda i: (chunks[i].doc_id, chunks[i].index))
        rows = [_row(chunks[i]) for i in order]
        data = pa.Table.from_pylist(rows)
        flat = pa.array(np.ascontiguousarray(vectors[order], dtype=np.float32).ravel())
        data = data.append_column("vector", pa.FixedSizeListArray.from_arrays(flat, vectors.shape[1]))
        self._db.create_table(self._table, data=data, mode="overwrite")

    def search(self, vector: np.ndarray, limit: int, doc_id: str | None = None) -> list[RankedChunk]:
        """Return up to `limit` chunks by cosine similarity, deterministically;
        only chunks of `doc_id` when it is given."""
        table = self._db.open_table(self._table)

        def fetch(n: int) -> list[RankedChunk]:
            search = table.search(np.asarray(vector, dtype=np.float32)).distance_type("cosine")
            if doc_id is not None:
                search = search.where(_doc_filter(doc_id), prefilter=True)
            rows = search.select([*_CHUNK_COLUMNS, "_distance"]).limit(n).to_arrow().to_pylist()
            return _ranked(rows, [1.0 - float(row["_distance"]) for row in rows])

        return _deterministic_cut(fetch, limit)


def reciprocal_rank_fusion[T: Hashable](rankings: Sequence[Sequence[T]], k: int = 60) -> list[T]:
    """Fuse rankings by reciprocal rank fusion (Cormack et al., 2009): an
    item scores the sum over the rankings that contain it of 1 / (k + rank),
    ranks counted from 1. Ties keep the order of first appearance, ranking
    by ranking. (LanceDB's own RRF reranker counts ranks from 0.)"""
    scores: dict[T, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    first_seen = {item: i for i, item in enumerate(scores)}
    return sorted(scores, key=lambda item: (-scores[item], first_seen[item]))


def rerank_head[T](ranked: Sequence[T], depth: int, scores: Callable[[Sequence[T]], Sequence[float]]) -> list[T]:
    """Reorder the first `depth` items by `scores` (highest first, ties in
    their original order); the rest follows in its original order, the
    unreranked tail. `scores` sees only the first `depth` items."""
    head = list(ranked[:depth])
    head_scores = scores(head)
    order = sorted(range(len(head)), key=lambda i: -head_scores[i])
    return [head[i] for i in order] + list(ranked[depth:])
