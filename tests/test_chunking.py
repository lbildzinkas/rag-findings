"""Chunkings: fixed token windows, section-aware chunks and small-to-big
children; tiling, spans, sizes."""

from __future__ import annotations

from itertools import pairwise

import pytest

from rag.chunking import chunk_text, fixed_windows, section_aware, small_to_big_children, verify_tiling
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


def sectioned_doc(sections: list[tuple[str, list[str]]], abstract: str = "abstract text"):
    return build_document("d1", abstract, sections)


def test_fixed_windows_match_plain_token_windows(fake_encoding):
    doc = make_doc("x" * 50 + "|" + "y" * 37)
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 16)
    assert [c.token_span for c in chunks] == [(s, min(s + 16, len(tokens))) for s in range(0, len(tokens), 16)]
    assert verify_tiling(doc, tokens, chunks) == 0


def test_fixed_windows_split_multibyte_character_is_shared(fake_encoding):
    doc = make_doc("abé|cd")  # é is two bytes: tokens 2 and 3
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 3)  # the window boundary splits é
    assert chunks[0].end == chunks[1].start + 1
    assert verify_tiling(doc, tokens, chunks) == 1


def test_section_aware_one_chunk_per_section_tiles_document(fake_encoding):
    doc = sectioned_doc([("Intro", ["intro one", "intro two"]), ("Method", ["method one"])])
    tokens = TokenText(doc.text, fake_encoding)
    chunks = section_aware(doc, tokens, 512)
    texts = [chunk_text(doc, c) for c in chunks]
    assert texts == ["abstract text\n\n", "intro one\n\nintro two\n\n", "method one"]
    assert verify_tiling(doc, tokens, chunks) == 0


def test_section_aware_splits_long_sections_at_paragraph_boundaries(fake_encoding):
    paragraphs = ["a" * 10, "b" * 10, "c" * 10, "d" * 10]
    doc = sectioned_doc([("Body", paragraphs)], abstract="")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = section_aware(doc, tokens, 25)  # two 10-byte paragraphs plus separator fit, three do not
    texts = [chunk_text(doc, c) for c in chunks]
    assert texts == ["a" * 10 + "\n\n" + "b" * 10 + "\n\n", "c" * 10 + "\n\n" + "d" * 10]
    assert all(c.n_tokens <= 25 for c in chunks)
    assert verify_tiling(doc, tokens, chunks) == 0


def test_section_aware_splits_an_oversize_paragraph_into_capped_windows(fake_encoding):
    doc = sectioned_doc([("Body", ["short", "z" * 50, "tail"])], abstract="")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = section_aware(doc, tokens, 20)
    assert all(c.n_tokens <= 20 for c in chunks)
    assert chunk_text(doc, chunks[0]) == "short\n\n"
    assert chunk_text(doc, chunks[-1]) == "tail"
    assert "".join(chunk_text(doc, c) for c in chunks) == doc.text
    assert verify_tiling(doc, tokens, chunks) == 0


def test_section_aware_keeps_same_named_sections_apart(fake_encoding):
    doc = sectioned_doc([("Notes", ["first"]), ("Notes", ["second"])], abstract="")
    tokens = TokenText(doc.text, fake_encoding)
    assert [chunk_text(doc, c) for c in section_aware(doc, tokens, 512)] == ["first\n\n", "second"]


def test_small_to_big_children_tile_their_parents(fake_encoding):
    doc = sectioned_doc([("Intro", ["i" * 30]), ("Body", ["b" * 12, "c" * 12])])
    tokens = TokenText(doc.text, fake_encoding)
    parents = section_aware(doc, tokens, 64)
    children = small_to_big_children(doc, tokens, parents, 8)
    assert verify_tiling(doc, tokens, children) == 0
    for parent in parents:
        own = [c for c in children if c.parent_index == parent.index]
        assert own[0].token_start == parent.token_start
        assert own[-1].token_end == parent.token_end
        assert all(c.n_tokens <= 8 for c in own)
    assert [c.index for c in children] == list(range(len(children)))


def test_verify_tiling_rejects_gaps(fake_encoding):
    doc = make_doc("alpha bravo|charlie")
    tokens = TokenText(doc.text, fake_encoding)
    chunks = fixed_windows(doc, tokens, 4)
    with pytest.raises(ValueError):
        verify_tiling(doc, tokens, [chunks[0], *chunks[2:]])
    with pytest.raises(ValueError):
        verify_tiling(doc, tokens, chunks[:-1])


def test_invalid_section_and_child_sizes_rejected(fake_encoding):
    doc = make_doc("alpha|beta")
    tokens = TokenText(doc.text, fake_encoding)
    with pytest.raises(ValueError):
        section_aware(doc, tokens, 0)
    with pytest.raises(ValueError):
        small_to_big_children(doc, tokens, section_aware(doc, tokens, 8), 0)
