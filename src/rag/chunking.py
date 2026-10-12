"""Chunking: fixed token windows over the canonical text.

Each chunk records its document and its character span, plus its token
index range so metrics can work on token positions. Windows are adjacent
and non-overlapping, so the chunks of a document tile its text exactly.
"""

from __future__ import annotations

from dataclasses import dataclass

from .documents import Document
from .tokens import TokenText


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    index: int
    start: int  # character offset into the canonical text
    end: int  # character offset into the canonical text
    token_start: int  # token index of the first token
    token_end: int  # token index one past the last token
    n_tokens: int

    @property
    def token_span(self) -> tuple[int, int]:
        return (self.token_start, self.token_end)


def fixed_windows(doc: Document, tokens: TokenText, size: int) -> list[Chunk]:
    """Split `tokens` (the tokenization of `doc.text`) into windows of
    `size` tokens, no overlap. The last window may be shorter. A non-positive
    size is rejected."""
    if size <= 0:
        raise ValueError(f"chunk size must be positive, got {size}")
    if len(tokens) == 0:
        return []
    chunks: list[Chunk] = []
    for index, token_start in enumerate(range(0, len(tokens), size)):
        token_end = min(token_start + size, len(tokens))
        start = tokens.offsets[token_start][0]
        end = tokens.offsets[token_end - 1][1]
        chunks.append(
            Chunk(
                doc_id=doc.doc_id,
                index=index,
                start=start,
                end=end,
                token_start=token_start,
                token_end=token_end,
                n_tokens=token_end - token_start,
            )
        )
    return chunks


def chunk_text(doc: Document, chunk: Chunk) -> str:
    """The canonical text covered by a chunk."""
    return doc.text[chunk.start : chunk.end]
