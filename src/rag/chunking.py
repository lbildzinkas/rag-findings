"""Chunkings: fixed token windows, section-aware chunks and small-to-big
children, all over the canonical text.

Each chunk records its document and its character span, plus its token
index range so metrics can work on token positions. Every chunking is cut
at token boundaries, so the chunks of a document tile its tokens exactly.
In characters they tile exactly for single-byte text, which is what the
tiling tests assert; when a token boundary splits a multi-byte character,
that character belongs to both adjacent tokens' character spans (see
rag.tokens.TokenText), so adjacent chunks can share that one character.

- **fixed** windows come from Chonkie's token chunker (no overlap). Chonkie
  derives character offsets from decoded text lengths, which drift when a
  window splits a multi-byte character, so only its token windows are used
  and the character spans come from the token offsets.
- **section-aware** chunks are one per section, a section longer than the
  cap split at paragraph boundaries; a single paragraph longer than the cap
  is split into cap-sized windows.
- **small-to-big** children are fixed windows inside each section-aware
  chunk (their parent), so every child has exactly one parent.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

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
    parent_index: int = -1  # small-to-big children: index of the parent chunk

    @property
    def token_span(self) -> tuple[int, int]:
        return (self.token_start, self.token_end)


def chunks_from_bounds(doc: Document, tokens: TokenText, bounds: Sequence[tuple[int, int, int]]) -> list[Chunk]:
    """Build chunks from (token_start, token_end, parent_index) triples, in order."""
    chunks: list[Chunk] = []
    for index, (token_start, token_end, parent_index) in enumerate(bounds):
        chunks.append(
            Chunk(
                doc_id=doc.doc_id,
                index=index,
                start=tokens.offsets[token_start][0],
                end=tokens.offsets[token_end - 1][1],
                token_start=token_start,
                token_end=token_end,
                n_tokens=token_end - token_start,
                parent_index=parent_index,
            )
        )
    return chunks


def _windows(token_start: int, token_end: int, size: int) -> list[tuple[int, int]]:
    return [(s, min(s + size, token_end)) for s in range(token_start, token_end, size)]


def _chonkie_token_counts(text: str, encoding, size: int) -> list[int]:
    from chonkie import TokenChunker
    from chonkie.tokenizer import Tokenizer

    class _Encoding(Tokenizer):
        """The experiment's encoding behind Chonkie's tokenizer interface;
        `encode_ordinary` so special-token text never raises."""

        def __repr__(self) -> str:
            return f"_Encoding({getattr(encoding, 'name', 'encoding')})"

        def encode(self, text: str) -> list[int]:
            return encoding.encode_ordinary(text)

        def decode(self, tokens: Sequence[int]) -> str:
            return encoding.decode_bytes(list(tokens)).decode("utf-8", errors="replace")

        def tokenize(self, text: str) -> list[int]:
            return self.encode(text)

    chunker = TokenChunker(tokenizer=_Encoding(), chunk_size=size, chunk_overlap=0)
    return [c.token_count for c in chunker.chunk(text)]


def fixed_windows(doc: Document, tokens: TokenText, size: int) -> list[Chunk]:
    """Split `tokens` (the tokenization of `doc.text`) into windows of
    `size` tokens, no overlap, as Chonkie's token chunker cuts them. The
    last window may be shorter. A non-positive size is rejected."""
    if size <= 0:
        raise ValueError(f"chunk size must be positive, got {size}")
    if len(tokens) == 0:
        return []
    counts = _chonkie_token_counts(doc.text, tokens.encoding, size)
    if sum(counts) != len(tokens) or any(n != size for n in counts[:-1]):
        raise ValueError(f"{doc.doc_id}: Chonkie windows do not tile the document's {len(tokens)} tokens")
    bounds: list[tuple[int, int, int]] = []
    token_start = 0
    for n in counts:
        bounds.append((token_start, token_start + n, -1))
        token_start += n
    return chunks_from_bounds(doc, tokens, bounds)


def _section_cuts(boundaries: list[int], max_tokens: int) -> list[int]:
    """Cut points inside one section, given its paragraph start tokens and
    its end token: greedy whole paragraphs up to `max_tokens`, and a single
    paragraph longer than the cap cut into cap-sized windows."""
    cuts = [boundaries[0]]
    current = boundaries[0]
    last_fit = current
    for boundary in boundaries[1:]:
        if boundary - current <= max_tokens:
            last_fit = boundary
            continue
        if last_fit > current:
            cuts.append(last_fit)
            current = last_fit
        if boundary - current > max_tokens:
            cuts.extend(s for s, _ in _windows(current, boundary, max_tokens)[1:])
            cuts.append(boundary)
            current = boundary
        last_fit = boundary
    return cuts


def section_aware(doc: Document, tokens: TokenText, max_tokens: int) -> list[Chunk]:
    """One chunk per section, a section longer than `max_tokens` split at
    paragraph boundaries. The separators between paragraphs belong to the
    chunk before them, so the chunks tile the document."""
    if max_tokens <= 0:
        raise ValueError(f"max_tokens must be positive, got {max_tokens}")
    if len(tokens) == 0:
        return []
    paragraph_tokens = [tokens.token_at_char(p.start) for p in doc.paragraphs]
    paragraph_tokens[0] = 0
    sections: list[list[int]] = []
    for i, paragraph in enumerate(doc.paragraphs):
        if i and paragraph.section_index == doc.paragraphs[i - 1].section_index:
            sections[-1].append(i)
        else:
            sections.append([i])
    cuts: list[int] = []
    for section in sections:
        after = section[-1] + 1
        section_end = paragraph_tokens[after] if after < len(paragraph_tokens) else len(tokens)
        cuts.extend(_section_cuts([paragraph_tokens[i] for i in section] + [section_end], max_tokens))
    edges = sorted(set(cuts) | {len(tokens)})
    return chunks_from_bounds(doc, tokens, [(s, e, -1) for s, e in pairwise(edges) if e > s])


def small_to_big_children(doc: Document, tokens: TokenText, parents: Sequence[Chunk], child_tokens: int) -> list[Chunk]:
    """Fixed windows of `child_tokens` inside each parent chunk; every child
    records its parent's index."""
    if child_tokens <= 0:
        raise ValueError(f"child_tokens must be positive, got {child_tokens}")
    bounds = [
        (s, e, parent.index)
        for parent in parents
        for s, e in _windows(parent.token_start, parent.token_end, child_tokens)
    ]
    return chunks_from_bounds(doc, tokens, bounds)


def verify_tiling(doc: Document, tokens: TokenText, chunks: Sequence[Chunk]) -> int:
    """Check that chunks tile the document: token ranges exactly, character
    spans exactly except for a shared multi-byte character at a token
    boundary. Returns the number of such shared characters."""
    if len(tokens) == 0:
        if chunks:
            raise ValueError(f"{doc.doc_id}: chunks over an empty document")
        return 0
    if not chunks or chunks[0].token_start != 0 or chunks[-1].token_end != len(tokens):
        raise ValueError(f"{doc.doc_id}: chunks do not cover the document's tokens")
    if chunks[0].start != 0 or chunks[-1].end != len(doc.text):
        raise ValueError(f"{doc.doc_id}: chunks do not cover the document's text")
    shared = 0
    for a, b in pairwise(chunks):
        if a.token_end != b.token_start:
            raise ValueError(f"{doc.doc_id}: token gap or overlap between chunks {a.index} and {b.index}")
        if a.end == b.start + 1 and len(doc.text[b.start].encode("utf-8")) > 1:
            shared += 1
        elif a.end != b.start:
            raise ValueError(f"{doc.doc_id}: character gap or overlap between chunks {a.index} and {b.index}")
    return shared


def chunk_text(doc: Document, chunk: Chunk) -> str:
    """The canonical text covered by a chunk."""
    return doc.text[chunk.start : chunk.end]
