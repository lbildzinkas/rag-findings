"""Budget packing (decision 17): whole chunks in ranked order fill the
token budget, never cut, capped at the top-N cap in the production view
and uncapped in the fair view.

A chunk that does not fit the remaining budget is skipped and packing
keeps filling with the next ranked chunks that fit (the approved rule for
variable-size chunkings). Because the cap only stops packing early, the
production view's packing is always the first N chunks of the fair
view's packing at the same budget.

Small-to-big matches on children and returns each matched child's
parent when the parent fits the remaining budget, else the child itself;
it never returns the same text twice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .chunking import Chunk


def _check(budget: int, top_n: int | None) -> None:
    if budget <= 0:
        raise ValueError(f"budget must be positive, got {budget}")
    if top_n is not None and top_n <= 0:
        raise ValueError(f"top_n must be positive, got {top_n}")


def pack(ranked: Sequence[Chunk], budget: int, top_n: int | None) -> list[Chunk]:
    """Return the packed chunks, in ranked order.

    Invariants: whole chunks only (never cut), the sum of n_tokens never
    exceeds `budget`, and at most `top_n` chunks are returned (no cap when
    `top_n` is None, the fair view). A chunk larger than the whole budget
    is never packed.
    """
    _check(budget, top_n)
    packed: list[Chunk] = []
    used = 0
    for chunk in ranked:
        if top_n is not None and len(packed) >= top_n:
            break
        if used == budget:
            break
        if chunk.n_tokens > budget - used:
            continue
        packed.append(chunk)
        used += chunk.n_tokens
    return packed


def pack_small_to_big(
    ranked_children: Sequence[Chunk],
    parents: Mapping[tuple[str, int], Chunk],
    budget: int,
    top_n: int | None,
) -> list[Chunk]:
    """Pack small-to-big: for each ranked child, its parent when the parent
    fits the remaining budget, else the child; skip anything whose text is
    already returned. `parents` maps (doc_id, parent index) to the parent.

    A parent is never returned after one of its children was (and a child
    never after its parent), so no returned text overlaps.
    """
    _check(budget, top_n)
    packed: list[Chunk] = []
    used = 0
    parents_packed: set[tuple[str, int]] = set()
    parents_with_child_packed: set[tuple[str, int]] = set()
    for child in ranked_children:
        if top_n is not None and len(packed) >= top_n:
            break
        if used == budget:
            break
        key = (child.doc_id, child.parent_index)
        if key in parents_packed:
            continue
        parent = parents[key]
        if key not in parents_with_child_packed and parent.n_tokens <= budget - used:
            packed.append(parent)
            parents_packed.add(key)
            used += parent.n_tokens
            continue
        if child.n_tokens > budget - used:
            continue
        packed.append(child)
        parents_with_child_packed.add(key)
        used += child.n_tokens
    return packed
