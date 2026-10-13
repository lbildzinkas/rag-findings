"""Budget packing (decision 17): whole chunks in ranked order fill the
token budget, never cut, capped at the top-N cap.

A chunk that does not fit the remaining budget is skipped and packing
keeps filling with the next ranked chunks that fit (the approved rule for
variable-size chunkings); with fixed-256 windows and a 1024-token budget
every chunk fits, but the rule is the same one later tickets widen.
"""

from __future__ import annotations

from .chunking import Chunk


def pack(ranked: list[Chunk], budget: int, top_n: int) -> list[Chunk]:
    """Return the packed chunks, in ranked order.

    Invariants: whole chunks only (never cut), the sum of n_tokens never
    exceeds `budget`, and at most `top_n` chunks are returned. A chunk
    larger than the whole budget is never packed.
    """
    if budget <= 0:
        raise ValueError(f"budget must be positive, got {budget}")
    if top_n <= 0:
        raise ValueError(f"top_n must be positive, got {top_n}")
    packed: list[Chunk] = []
    used = 0
    for chunk in ranked:
        if len(packed) >= top_n:
            break
        if chunk.n_tokens > budget - used:
            continue
        packed.append(chunk)
        used += chunk.n_tokens
    return packed
