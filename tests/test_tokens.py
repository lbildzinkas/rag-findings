"""Tokenizer offsets: tiling, straddling characters and overlap sets."""

from __future__ import annotations

from rag.tokens import TokenText, sha256_text


def test_offsets_tile_the_text(fake_encoding):
    text = "hello world, this is a tokenizer test"
    tt = TokenText(text, fake_encoding)
    assert len(tt) == len(text.encode("utf-8"))
    # every character position is covered by at least one token
    covered = set()
    for start, end in tt.offsets:
        covered.update(range(start, end))
    assert covered == set(range(len(text)))
    # offsets are non-decreasing and in order
    assert [s for s, _ in tt.offsets] == sorted(s for s, _ in tt.offsets)


def test_multibyte_char_straddling_two_tokens(fake_encoding):
    # with byte tokens, a 3-byte character is covered by 3 tokens,
    # each reporting the character's span
    text = "a\u4e2db"
    tt = TokenText(text, fake_encoding)
    char_index = text.index("\u4e2d")
    spans = [tt.offsets[i] for i in range(len(tt))]
    covering = [(s, e) for s, e in spans if s <= char_index < e]
    assert len(covering) == 3  # one per utf-8 byte
    assert all(s == char_index and e == char_index + 1 for s, e in covering)


def test_token_indices_overlapping(fake_encoding):
    text = "abcdefgh"
    tt = TokenText(text, fake_encoding)
    assert tt.token_indices_overlapping(0, 3) == frozenset({0, 1, 2})
    assert tt.token_indices_overlapping(2, 3) == frozenset({2})
    assert tt.token_indices_overlapping(5, 8) == frozenset({5, 6, 7})
    assert tt.token_indices_overlapping(4, 4) == frozenset()


def test_tokenization_is_lossless(fake_encoding):
    text = "labels, spans; caf\u00e9 \u4e2d\u6587 and emoji \U0001f600"
    tt = TokenText(text, fake_encoding)
    assert b"".join(fake_encoding.decode_bytes([t]) for t in tt.token_ids) == text.encode("utf-8")


def test_sha256_text_stable():
    assert sha256_text("abc") == ("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
