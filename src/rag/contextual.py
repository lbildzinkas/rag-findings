"""Contextual chunks, the search-time half (ADR 0005, ADR 0009).

A contextual chunking has the spans of the fixed chunking its prefixes
were written for (v2: fixed-256), and each chunk's search text is its
context prefix, a blank line and the chunk text:

- the BM25 index reads the search text;
- the embedder embeds the search text (nomic adds `search_document: `);
- the reranker scores (question, search text) pairs, because the reranker
  is part of search.

Packing, scoring and the reader use the chunk text only, and the token
budget counts only the chunk's tokens. The side variant
(`prefix_in_budget`) ranks the same way, but its packing counts the
tokens of the whole search text against the budget (in the experiment's
tokenizer, cl100k) and the reader receives the search text; recall is
still scored on the chunk's own span.

Vectors and reranker scores of contextual chunks are cached under the
model key plus the prefix set's id (`key_suffix`), so they never collide
with the plain chunk's entries for the same span. The prefixes come from
the store `rag prefixes` writes; a run fails before any search when a
chunk has no prefix in the configured set, and so does the reader stage
for a packed span of the side variant.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path

from .cache import SpanKey
from .config import PrefixSet
from .documents import Document
from .prefixes import PrefixStore

SEPARATOR = "\n\n"  # a blank line between the prefix and the chunk text
MISSING_SHOWN = 5  # chunks named in the error when prefixes are missing


def key_suffix(prefix_set: PrefixSet) -> str:
    """The suffix of the embedder's and reranker's cache keys."""
    return f"#ctx:{prefix_set.id}"


def search_text(prefix: str, chunk_text: str) -> str:
    """What search reads for a contextual chunk (and the side variant's reader)."""
    return prefix + SEPARATOR + chunk_text


def load_prefixes(
    store_path: Path,
    prefix_set: PrefixSet,
    documents: Mapping[str, Document],
    spans: Iterable[tuple[str, int, int]],
    chunking: str,
) -> dict[SpanKey, str]:
    """The stored prefix of every (doc_id, start, end) chunk span, by
    (document source hash, start, end). Raises when the store is absent or
    any span has no non-empty prefix in the prefix set, naming how many
    and the first few."""
    if not store_path.is_file():
        raise ValueError(f"chunking {chunking}: no prefix store at {store_path}; run `rag prefixes` first")
    store = PrefixStore(store_path)
    try:
        stored: dict[str, dict[tuple[int, int], tuple[str, int, bool]]] = {}
        out: dict[SpanKey, str] = {}
        missing: list[tuple[str, int, int]] = []
        total = 0
        for doc_id, start, end in spans:
            total += 1
            doc_hash = documents[doc_id].source_hash
            if doc_hash not in stored:
                stored[doc_hash] = store.prefixes(prefix_set.model_key, prefix_set.prompt_sha256, doc_hash)
            record = stored[doc_hash].get((start, end))
            if record is None or not record[0].strip():
                missing.append((doc_id, start, end))
                continue
            out[(doc_hash, start, end)] = record[0]
    finally:
        store.close()
    if missing:
        shown = ", ".join(f"{doc_id} characters {start}-{end}" for doc_id, start, end in missing[:MISSING_SHOWN])
        raise ValueError(
            f"chunking {chunking}: {len(missing)} of {total} chunks have no prefix in the prefix set "
            f"{prefix_set.id} (first: {shown}); write them with `rag prefixes` before this run"
        )
    return out
