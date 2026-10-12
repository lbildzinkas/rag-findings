"""Fixed token windows: tiling, spans, sizes."""

from __future__ import annotations

from itertools import pairwise

import pytest

from rag.chunking import chunk_text, fixed_windows
from rag.documents import build_document
from rag.tokens import TokenText


def make_doc(text: str):
    abstract, _, rest = text.partition("|")
    paragraphs = rest.split("||") if rest else []
    return build_document("d1", abstract, [("Body", paragraphs)])


def test_windows_tile_the_document_exactly(fake_encoding):
    doc = make_doc("alpha bravo charlie|delta echo foxtrot||golf hotel india")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 10)
    assert chunks[0].start == 0
    assert chunks[-1].end == len(doc.text)
    for a, b in pairwise(chunks):
        assert a.end == b.start  # no gaps, no overlap
    for chunk in chunks:
        assert chunk.doc_id == "d1"
        assert chunk.n_tokens == chunk.token_end - chunk.token_start
        assert chunk.n_tokens <= 10


def test_last_window_is_shorter(fake_encoding):
    doc = make_doc("abcdefghij|klmnop")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 4)
    assert [c.n_tokens for c in chunks] == [4, 4, 4, 4, 2]
    assert [c.index for c in chunks] == [0, 1, 2, 3, 4]


def test_chunk_text_matches_span(fake_encoding):
    doc = make_doc("alpha|beta gamma")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 5)
    for chunk in chunks:
        assert chunk_text(doc, chunk) == doc.text[chunk.start : chunk.end]


def test_token_spans_are_contiguous_indices(fake_encoding):
    doc = make_doc("one two three|four five six")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 7)
    assert chunks[0].token_start == 0
    assert chunks[0].token_end == 7
    assert chunks[1].token_start == 7
    total = sum(c.n_tokens for c in chunks)
    assert total == len(tokens)


def test_empty_document_has_no_chunks(fake_encoding):
    doc = build_document("d0", "", [])
    assert fixed_windows(doc, TokenText(doc.text, fake_encoding), 8) == []


def test_invalid_size_rejected(fake_encoding):
    doc = make_doc("alpha|beta")
    tokens = TokenText(doc.text, fake_encoding)
    with pytest.raises(ValueError):
        fixed_windows(doc, tokens, 0)
    with pytest.raises(ValueError):
        fixed_windows(doc, tokens, -3)
