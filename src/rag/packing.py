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

`pack_union` (v2) is the overlap-aware packing of search-all routing,
whose ranked list mixes the chunkings: chunks from different chunkings
overlap, so packing counts only the tokens not already packed.
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


def _covered(ranges: Sequence[tuple[int, int]], start: int, end: int) -> int:
    """How much of the token range [start, end) the sorted, disjoint ranges
    already cover."""
    covered = 0
    for s, e in ranges:
        if e <= start:
            continue
        if s >= end:
            break
        covered += min(e, end) - max(s, start)
    return covered


def _add_range(ranges: list[tuple[int, int]], start: int, end: int) -> None:
    """Add [start, end) to the sorted, disjoint ranges, merging overlaps."""
    out: list[tuple[int, int]] = []
    low, high = start, end
    placed = False
    for s, e in ranges:
        if e < low:
            out.append((s, e))
        elif s > high:
            if not placed:
                out.append((low, high))
                placed = True
            out.append((s, e))
        else:
            low, high = min(low, s), max(high, e)
    if not placed:
        out.append((low, high))
    ranges[:] = out


def pack_union(
    ranked: Sequence[Chunk],
    budget: int,
    top_n: int | None,
    parents: Mapping[tuple[str, int], Chunk] | None = None,
) -> list[Chunk]:
    """Overlap-aware packing for a ranked list that mixes chunkings
    (search-all routing): a chunk adds only the tokens not already packed
    in its document, so no text is returned twice.

    - a chunk wholly inside packed text adds nothing and is skipped;
    - a chunk whose new tokens do not fit the remaining budget is skipped,
      and packing keeps filling with the next ranked chunks that fit;
    - the top-N cap counts chunks that added text;
    - the used budget is the union of the packed token ranges, never more
      than `budget`.

    Small-to-big children keep v1's rule: a child returns its parent when
    the parent's new tokens fit (`parents` maps (doc_id, parent index) to
    the parent, one small-to-big chunking), else the child itself; a
    parent is never returned after one of its children was packed. A
    chunk with no parent (`parent_index` < 0) is packed as itself.
    """
    _check(budget, top_n)
    packed: list[Chunk] = []
    used = 0
    ranges: dict[str, list[tuple[int, int]]] = {}  # doc_id -> packed token ranges
    parents_packed: set[tuple[str, int]] = set()
    parents_with_child_packed: set[tuple[str, int]] = set()
    for chunk in ranked:
        if top_n is not None and len(packed) >= top_n:
            break
        if used == budget:
            break
        if parents is not None and chunk.parent_index >= 0:
            key = (chunk.doc_id, chunk.parent_index)
            if key not in parents_packed and key not in parents_with_child_packed:
                parent = parents[key]
                doc_ranges = ranges.setdefault(parent.doc_id, [])
                new = parent.n_tokens - _covered(doc_ranges, parent.token_start, parent.token_end)
                if new > 0 and new <= budget - used:
                    _add_range(doc_ranges, parent.token_start, parent.token_end)
                    packed.append(parent)
                    parents_packed.add(key)
                    used += new
                    continue
                # the parent's new tokens do not fit: the child itself (v1's rule)
        doc_ranges = ranges.setdefault(chunk.doc_id, [])
        new = chunk.n_tokens - _covered(doc_ranges, chunk.token_start, chunk.token_end)
        if new == 0 or new > budget - used:
            continue
        _add_range(doc_ranges, chunk.token_start, chunk.token_end)
        packed.append(chunk)
        used += new
        if chunk.parent_index >= 0:
            parents_with_child_packed.add((chunk.doc_id, chunk.parent_index))
    return packed
