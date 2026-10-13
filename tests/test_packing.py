"""Budget packing: whole chunks, never cut, never over budget or cap;
the fair view; small-to-big parents, child fallback and no repeated text."""

from __future__ import annotations

import random
from itertools import pairwise

import pytest

from rag.chunking import Chunk
from rag.packing import pack, pack_small_to_big


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


def test_fair_view_has_no_cap():
    ranked = [chunk(100, index=i) for i in range(20)]
    assert len(pack(ranked, budget=10_000, top_n=None)) == 20


def test_production_view_is_a_prefix_of_the_fair_view():
    rng = random.Random(0)
    ranked = [chunk(rng.randint(1, 300), index=i) for i in range(40)]
    for budget in (128, 512, 2048):
        fair = pack(ranked, budget=budget, top_n=None)
        for top_n in (1, 5, 8):
            assert pack(ranked, budget=budget, top_n=top_n) == fair[:top_n]


# small-to-big: parents are section-aware chunks, children 4-token windows inside them


def family(doc_id: str, parent_index: int, token_start: int, n_children: int, child_tokens: int = 4):
    parent = Chunk(
        doc_id=doc_id,
        index=parent_index,
        start=token_start,
        end=token_start + n_children * child_tokens,
        token_start=token_start,
        token_end=token_start + n_children * child_tokens,
        n_tokens=n_children * child_tokens,
    )
    children = [
        Chunk(
            doc_id=doc_id,
            index=parent_index * 100 + i,
            start=token_start + i * child_tokens,
            end=token_start + (i + 1) * child_tokens,
            token_start=token_start + i * child_tokens,
            token_end=token_start + (i + 1) * child_tokens,
            n_tokens=child_tokens,
            parent_index=parent_index,
        )
        for i in range(n_children)
    ]
    return parent, children


def parents_map(*parents: Chunk) -> dict[tuple[str, int], Chunk]:
    return {(p.doc_id, p.index): p for p in parents}


def test_small_to_big_returns_the_parent_when_it_fits():
    parent, children = family("d1", 0, 0, 4)  # parent 16 tokens
    packed = pack_small_to_big([children[2]], parents_map(parent), budget=16, top_n=8)
    assert packed == [parent]


def test_small_to_big_falls_back_to_the_child_when_the_parent_does_not_fit():
    parent, children = family("d1", 0, 0, 4)  # parent 16 tokens
    packed = pack_small_to_big([children[2]], parents_map(parent), budget=12, top_n=8)
    assert packed == [children[2]]


def test_small_to_big_never_returns_the_same_text_twice():
    big, big_children = family("d1", 0, 0, 4)  # 16 tokens
    small, small_children = family("d1", 1, 16, 2)  # 8 tokens
    ranked = [small_children[0], big_children[1], small_children[1], big_children[3]]
    packed = pack_small_to_big(ranked, parents_map(big, small), budget=20, top_n=8)
    # small parent fits (8); big parent no longer fits (16 > 12), so its
    # child does; the small parent's second child is already returned;
    # the big parent's other child still fits beside its sibling
    assert packed == [small, big_children[1], big_children[3]]
    assert sum(c.n_tokens for c in packed) <= 20


def test_small_to_big_respects_the_top_n_cap():
    a, a_children = family("d1", 0, 0, 2)
    b, b_children = family("d1", 1, 8, 2)
    c, c_children = family("d2", 0, 0, 2)
    ranked = [a_children[0], b_children[0], c_children[0]]
    packed = pack_small_to_big(ranked, parents_map(a, b, c), budget=1000, top_n=2)
    assert packed == [a, b]
    assert pack_small_to_big(ranked, parents_map(a, b, c), budget=1000, top_n=None) == [a, b, c]


def test_small_to_big_property_no_overlap_and_within_budget():
    rng = random.Random(7)
    for _ in range(200):
        parents, children = [], []
        token_start = 0
        for parent_index in range(rng.randint(1, 6)):
            parent, kids = family("d1", parent_index, token_start, rng.randint(1, 5))
            parents.append(parent)
            children.extend(kids)
            token_start = parent.token_end
        ranked = rng.sample(children, rng.randint(1, len(children)))
        budget = rng.randint(4, 40)
        top_n = rng.choice([None, 1, 3, 8])
        packed = pack_small_to_big(ranked, parents_map(*parents), budget=budget, top_n=top_n)
        assert sum(c.n_tokens for c in packed) <= budget
        assert top_n is None or len(packed) <= top_n
        spans = sorted(c.token_span for c in packed)
        assert all(a[1] <= b[0] for a, b in pairwise(spans))
        fair = pack_small_to_big(ranked, parents_map(*parents), budget=budget, top_n=None)
        assert packed == (fair if top_n is None else fair[:top_n])


def test_small_to_big_rejects_invalid_arguments():
    parent, children = family("d1", 0, 0, 1)
    with pytest.raises(ValueError):
        pack_small_to_big(children, parents_map(parent), budget=0, top_n=8)
    with pytest.raises(ValueError):
        pack_small_to_big(children, parents_map(parent), budget=8, top_n=0)
