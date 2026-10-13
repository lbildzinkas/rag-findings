"""Budget packing: whole chunks, never cut, never over budget or cap."""

from __future__ import annotations

import pytest

from rag.chunking import Chunk
from rag.packing import pack


def chunk(n_tokens: int, doc_id: str = "d1", index: int = 0) -> Chunk:
    return Chunk(
        doc_id=doc_id,
        index=index,
        start=0,
        end=n_tokens,
        token_start=0,
        token_end=n_tokens,
        n_tokens=n_tokens,
    )


def test_fills_budget_with_whole_chunks_in_ranked_order():
    ranked = [chunk(40, index=0), chunk(40, index=1), chunk(40, index=2), chunk(40, index=3)]
    packed = pack(ranked, budget=1024, top_n=8)
    assert [c.index for c in packed] == [0, 1, 2, 3]
    assert sum(c.n_tokens for c in packed) == 160


def test_never_exceeds_budget():
    ranked = [chunk(600), chunk(500), chunk(300)]
    packed = pack(ranked, budget=1024, top_n=8)
    assert [c.n_tokens for c in packed] == [600, 300]
    assert sum(c.n_tokens for c in packed) <= 1024


def test_chunk_larger_than_budget_is_never_packed():
    ranked = [chunk(2000), chunk(700), chunk(700)]
    packed = pack(ranked, budget=1024, top_n=8)
    assert [c.n_tokens for c in packed] == [700]
    assert sum(c.n_tokens for c in packed) <= 1024


def test_chunk_exactly_the_budget_fits_alone():
    ranked = [chunk(1024), chunk(1)]
    packed = pack(ranked, budget=1024, top_n=8)
    assert [c.n_tokens for c in packed] == [1024]


def test_respects_top_n_cap():
    ranked = [chunk(100, index=i) for i in range(20)]
    packed = pack(ranked, budget=10_000, top_n=8)
    assert len(packed) == 8
    assert [c.index for c in packed] == list(range(8))


def test_cap_and_budget_bind_together():
    ranked = [chunk(300, index=i) for i in range(10)]
    packed = pack(ranked, budget=1024, top_n=3)
    assert len(packed) == 3
    assert sum(c.n_tokens for c in packed) == 900


def test_skips_and_keeps_filling():
    ranked = [chunk(900), chunk(800), chunk(200), chunk(100)]
    packed = pack(ranked, budget=1024, top_n=8)
    # 900 fits; neither 800 nor 200 fit the remaining 124; 100 does
    assert [c.n_tokens for c in packed] == [900, 100]


def test_never_cuts_a_chunk():
    ranked = [chunk(300), chunk(300), chunk(300), chunk(300)]
    packed = pack(ranked, budget=1000, top_n=8)
    # three whole chunks (900) fit; the fourth is not sliced to 100 tokens
    assert [c.n_tokens for c in packed] == [300, 300, 300]


def test_empty_ranking_and_invalid_arguments():
    assert pack([], budget=100, top_n=8) == []
    with pytest.raises(ValueError):
        pack([chunk(1)], budget=0, top_n=8)
    with pytest.raises(ValueError):
        pack([chunk(1)], budget=100, top_n=0)
