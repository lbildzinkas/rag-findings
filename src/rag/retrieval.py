"""BM25 retrieval over the whole collection with a LanceDB full-text index.

All papers' chunks go into one FTS table. Search results are re-sorted by
(-score, doc_id, chunk index) so packing is deterministic regardless of
the engine's tie order.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chunking import Chunk


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


class BM25Index:
    """A LanceDB full-text index over every chunk of the collection."""

    def __init__(self, path: Path, table: str = "chunks"):
        import lancedb

        self._db = lancedb.connect(str(path))
        self._table = table

    def build(self, chunks: list[Chunk], texts: dict[str, str]) -> None:
        """Index chunks in a deterministic order (doc_id, chunk index)."""
        from lancedb.index import FTS

        rows = []
        for chunk in sorted(chunks, key=lambda c: (c.doc_id, c.index)):
            rows.append(
                {
                    "doc_id": chunk.doc_id,
                    "chunk_index": chunk.index,
                    "start": chunk.start,
                    "end": chunk.end,
                    "token_start": chunk.token_start,
                    "token_end": chunk.token_end,
                    "n_tokens": chunk.n_tokens,
                    "text": texts[f"{chunk.doc_id}:{chunk.index}"],
                }
            )
        table = self._db.create_table(self._table, data=rows, mode="overwrite")
        table.create_index("text", config=FTS())

    def search(self, query: str, limit: int) -> list[RankedChunk]:
        """Return up to `limit` chunks ranked by BM25, deterministically."""
        table = self._db.open_table(self._table)
        rows = table.search(query, query_type="fts").limit(limit).to_list()
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
                ),
                score=float(row["_score"]),
            )
            for row in rows
        ]
        ranked.sort(key=lambda r: (-r.score, r.doc_id, r.index))
        return ranked
