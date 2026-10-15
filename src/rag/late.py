"""Late chunking (ADR 0005, ADR 0007): chunk vectors pooled from the token
embeddings of the whole document, so each chunk's vector carries its
surroundings.

- **Windows.** A document longer than the embedder's input is read in
  consecutive windows of whole blocks: blocks are the document's
  consecutive `WINDOW_BLOCK_TOKENS`-token (cl100k) pieces, the same cuts
  as fixed-256, so a window holds whole fixed-128 and fixed-256 chunks and
  one model pass per window serves every late chunking. Each window is
  read with the document prefix (`search_document: `) and the special
  tokens, and holds as many blocks as fit `LATE_WINDOW` tokens of the
  embedder's own, prefix and special tokens included. The rule depends
  on the document alone, never on which chunkings a run has, so a late
  vector's cache key (the model key plus `LATE_KEY_SUFFIX`) always means
  the same windows.
- **Pooling.** A chunk's vector is the normalized mean of the token
  embeddings whose character offsets start inside the chunk's span; the
  prefix and special tokens join no chunk. Adjacent chunks can share one
  multi-byte character, so a token starting there joins the later chunk,
  the one whose span starts at it. A chunk in which no token starts (it
  holds only the tail of a token that started before it) is pooled from
  the tokens overlapping its span instead, and counted.

Everything here works on character spans and an injected model, so the
tests run on a fake token-embedding model.
"""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .tokens import TokenText

LATE_WINDOW = 8192  # the most tokens one window may hold, prefix and special tokens included
WINDOW_BLOCK_TOKENS = 256  # windows are cut only between blocks of this many cl100k tokens
LATE_KEY_SUFFIX = f"#late-{LATE_WINDOW}"  # appended to the model key: late vectors never mix with v1's

Span = tuple[int, int]  # [start, end) in characters


@dataclass(frozen=True)
class TokenEmbeddings:
    """One window's token embeddings, one row per token the model read.
    `offsets` gives each token's character span in the window's text, or
    None for the prefix and special tokens."""

    offsets: list[Span | None]
    vectors: np.ndarray


class TokenEmbedder(Protocol):
    def input_tokens(self, texts: Sequence[str]) -> list[int]:
        """Tokens the model reads for each document text, prefix and special tokens included."""
        ...

    def token_embeddings(self, text: str) -> TokenEmbeddings:
        """The token embeddings of one document text, read with the document prefix."""
        ...


@dataclass(frozen=True)
class Window:
    start: int  # character span of the window's text in the document
    end: int
    tokens: int  # tokens the model reads, prefix and special tokens included


@dataclass
class WindowStats:
    documents: int = 0
    windows: int = 0
    documents_over_one_window: int = 0
    longest_window_tokens: int = 0
    chunks_pooled_from_overlapping_tokens: int = 0

    def add(self, windows: Sequence[Window]) -> None:
        self.documents += 1
        self.windows += len(windows)
        self.documents_over_one_window += len(windows) > 1
        self.longest_window_tokens = max([self.longest_window_tokens, *(w.tokens for w in windows)])

    def as_dict(self) -> dict[str, int]:
        return {
            "window_tokens": LATE_WINDOW,
            "block_tokens": WINDOW_BLOCK_TOKENS,
            "documents": self.documents,
            "windows": self.windows,
            "documents_over_one_window": self.documents_over_one_window,
            "longest_window_tokens": self.longest_window_tokens,
            "chunks_pooled_from_overlapping_tokens": self.chunks_pooled_from_overlapping_tokens,
        }


def block_spans(tokens: TokenText, size: int = WINDOW_BLOCK_TOKENS) -> list[Span]:
    """Character spans of the text's consecutive `size`-token blocks (the
    last may be shorter): the only places a window may be cut."""
    return [
        (tokens.offsets[s][0], tokens.offsets[min(s + size, len(tokens)) - 1][1]) for s in range(0, len(tokens), size)
    ]


def plan_windows(
    text: str, blocks: Sequence[Span], count: Callable[[Sequence[str]], list[int]], limit: int = LATE_WINDOW
) -> list[Window]:
    """Consecutive windows of whole blocks, each holding as many blocks as
    fit `limit` tokens. Block costs estimate where a window ends; the
    window's own text is then counted exactly, so no window exceeds the
    limit even when tokens merge or split at block edges."""
    if not blocks:
        return []
    overhead = count([""])[0]
    cost = [n - overhead for n in count([text[s:e] for s, e in blocks])]

    def exact(i: int, j: int) -> int:
        return count([text[blocks[i][0] : blocks[j][1]]])[0]

    windows: list[Window] = []
    i = 0
    while i < len(blocks):
        j, estimate = i, overhead + cost[i]
        while j + 1 < len(blocks) and estimate + cost[j + 1] <= limit:
            j += 1
            estimate += cost[j]
        n = exact(i, j)
        while n > limit and j > i:
            j -= 1
            n = exact(i, j)
        while j + 1 < len(blocks) and (grown := exact(i, j + 1)) <= limit:
            j, n = j + 1, grown
        if n > limit:
            raise ValueError(f"a single {WINDOW_BLOCK_TOKENS}-token block reads as {n} tokens, over {limit}")
        windows.append(Window(blocks[i][0], blocks[j][1], n))
        i = j + 1
    return windows


def assign_tokens(offsets: Sequence[Span | None], chunks: Sequence[Span]) -> list[int | None]:
    """The chunk each token joins: the last chunk starting at or before the
    token's start, when the token starts before that chunk's end (`chunks`
    ascending, in the same coordinates as the offsets); None for the
    prefix and special tokens and for tokens outside every chunk."""
    starts = [start for start, _ in chunks]
    out: list[int | None] = []
    for offset in offsets:
        index = None if offset is None else bisect_right(starts, offset[0]) - 1
        inside = index is not None and index >= 0 and offset[0] < chunks[index][1]  # type: ignore[index]
        out.append(index if inside else None)
    return out


def _normalized_mean(rows: np.ndarray) -> np.ndarray:
    mean = rows.astype(np.float64).mean(axis=0)
    return (mean / np.linalg.norm(mean)).astype(np.float32)


def pool_window(
    embedded: TokenEmbeddings, chunks: Sequence[Span], stats: WindowStats | None = None
) -> list[np.ndarray]:
    """One vector per chunk (spans relative to the window's text, ascending)."""
    members: dict[int, list[int]] = {}
    for row, index in enumerate(assign_tokens(embedded.offsets, chunks)):
        if index is not None:
            members.setdefault(index, []).append(row)
    out: list[np.ndarray] = []
    for index, (start, end) in enumerate(chunks):
        rows = members.get(index, [])
        if not rows:  # only the tail of a token that started in an earlier chunk
            rows = [i for i, o in enumerate(embedded.offsets) if o is not None and o[0] < end and o[1] > start]
            if not rows:
                raise ValueError(f"no token covers the chunk at characters {start}-{end}")
            if stats is not None:
                stats.chunks_pooled_from_overlapping_tokens += 1
        out.append(_normalized_mean(embedded.vectors[rows]))
    return out


def late_vectors(
    text: str,
    chunkings: Sequence[Sequence[Span]],
    windows: Sequence[Window],
    model: TokenEmbedder,
    stats: WindowStats | None = None,
) -> list[list[np.ndarray]]:
    """Late-chunked vectors of one document: one list per chunking, one
    vector per chunk, with one model pass per window serving every
    chunking. Every chunk must lie inside exactly one window."""
    homes = [[_window_of(span, windows) for span in spans] for spans in chunkings]
    out: list[list[np.ndarray | None]] = [[None] * len(spans) for spans in chunkings]
    for w, window in enumerate(windows):
        embedded = model.token_embeddings(text[window.start : window.end])
        for c, spans in enumerate(chunkings):
            members = [i for i, home in enumerate(homes[c]) if home == w]
            local = [(spans[i][0] - window.start, spans[i][1] - window.start) for i in members]
            for i, vector in zip(members, pool_window(embedded, local, stats), strict=True):
                out[c][i] = vector
    assert all(v is not None for vectors in out for v in vectors)
    return out  # type: ignore[return-value]


def _window_of(span: Span, windows: Sequence[Window]) -> int:
    inside = [w for w, window in enumerate(windows) if window.start <= span[0] and span[1] <= window.end]
    if len(inside) != 1:
        raise ValueError(f"chunk at characters {span[0]}-{span[1]} lies in {len(inside)} windows, not exactly one")
    return inside[0]
