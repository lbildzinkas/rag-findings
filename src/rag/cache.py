"""On-disk cache of embeddings and reranker scores (SQLite, git-ignored).

Chunk embeddings are keyed by model and chunk span: the model id and
revision, the document's source hash and the chunk's character span.
Question embeddings are keyed by model and the hash of the question text.
Reranker scores are keyed by model, question and chunk: the question hash
plus the chunk span. A span names the same text in every chunking, so a
chunk that two chunkings share (or that both search scopes and both
embedders retrieve) is embedded or reranked once. Writes commit as they
go, so an interrupted run resumes from what it already computed.
"""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterable
from pathlib import Path

import numpy as np

SpanKey = tuple[str, int, int]  # (document source hash, start, end) in characters

_SCHEMA = """
CREATE TABLE IF NOT EXISTS embeddings (
    model TEXT NOT NULL, doc_hash TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL,
    vector BLOB NOT NULL, PRIMARY KEY (model, doc_hash, start, end)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS query_vectors (
    model TEXT NOT NULL, question_hash TEXT NOT NULL, vector BLOB NOT NULL, PRIMARY KEY (model, question_hash)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS rerank_scores (
    model TEXT NOT NULL, question_hash TEXT NOT NULL, doc_hash TEXT NOT NULL, start INTEGER NOT NULL,
    end INTEGER NOT NULL, score REAL NOT NULL, PRIMARY KEY (model, question_hash, doc_hash, start, end)
) WITHOUT ROWID;
"""


def question_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Cache:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path))
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def vectors(self, model: str, doc_hash: str) -> dict[tuple[int, int], np.ndarray]:
        """Every cached vector of one document under `model`, by (start, end)."""
        rows = self._db.execute(
            "SELECT start, end, vector FROM embeddings WHERE model = ? AND doc_hash = ?", (model, doc_hash)
        )
        return {(start, end): np.frombuffer(blob, dtype=np.float32) for start, end, blob in rows}

    def put_vectors(self, model: str, items: Iterable[tuple[SpanKey, np.ndarray]]) -> None:
        self._db.executemany(
            "INSERT OR REPLACE INTO embeddings VALUES (?, ?, ?, ?, ?)",
            [(model, h, s, e, np.asarray(v, dtype=np.float32).tobytes()) for (h, s, e), v in items],
        )
        self._db.commit()

    def query_vectors(self, model: str, questions: Iterable[str]) -> dict[str, np.ndarray]:
        """Cached question vectors under `model`, by question text."""
        out: dict[str, np.ndarray] = {}
        for question in questions:
            row = self._db.execute(
                "SELECT vector FROM query_vectors WHERE model = ? AND question_hash = ?",
                (model, question_hash(question)),
            ).fetchone()
            if row is not None:
                out[question] = np.frombuffer(row[0], dtype=np.float32)
        return out

    def put_query_vectors(self, model: str, items: Iterable[tuple[str, np.ndarray]]) -> None:
        self._db.executemany(
            "INSERT OR REPLACE INTO query_vectors VALUES (?, ?, ?)",
            [(model, question_hash(q), np.asarray(v, dtype=np.float32).tobytes()) for q, v in items],
        )
        self._db.commit()

    def scores(self, model: str, question: str) -> dict[SpanKey, float]:
        """Every cached reranker score of one question under `model`."""
        rows = self._db.execute(
            "SELECT doc_hash, start, end, score FROM rerank_scores WHERE model = ? AND question_hash = ?",
            (model, question_hash(question)),
        )
        return {(h, s, e): score for h, s, e, score in rows}

    def put_scores(self, model: str, question: str, items: Iterable[tuple[SpanKey, float]]) -> None:
        qhash = question_hash(question)
        self._db.executemany(
            "INSERT OR REPLACE INTO rerank_scores VALUES (?, ?, ?, ?, ?, ?)",
            [(model, qhash, h, s, e, float(score)) for (h, s, e), score in items],
        )
        self._db.commit()
