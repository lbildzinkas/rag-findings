"""Deterministic retrieval: a cutoff inside a group of tied scores must
keep the same tied rows, in the same order, on every run.

The engine (LanceDB's full-text and vector searches) cuts its top-n by
score in an arbitrary tie order, so which tied rows survive the cut can
flip between identical runs. `_deterministic_cut` over-fetches past the
cutoff and extends the fetch while a tie could still straddle it; the
tests pin that logic against a deliberately arbitrary engine, and the
real indexes against corpora whose chunks all tie.
"""

from __future__ import annotations

import random

import numpy as np

from rag.chunking import Chunk
from rag.retrieval import _OVERFETCH, BM25Index, RankedChunk, VectorIndex, _deterministic_cut

TIED_TEXT = "alpha beta gamma delta"


def _chunk(doc_id: str, index: int) -> Chunk:
    return Chunk(doc_id=doc_id, index=index, start=0, end=len(TIED_TEXT), token_start=0, token_end=4, n_tokens=4)


def _tied_corpus(n_docs: int, chunks_per_doc: int) -> tuple[list[Chunk], dict[str, str]]:
    chunks = [_chunk(f"doc{d:02d}", c) for d in range(n_docs) for c in range(chunks_per_doc)]
    texts = {f"{c.doc_id}:{c.index}": TIED_TEXT for c in chunks}
    return chunks, texts


def _keys(ranked: list[RankedChunk]) -> list[tuple[str, int]]:
    return [(r.doc_id, r.index) for r in ranked]


def test_the_cut_extends_the_fetch_until_no_tie_can_straddle_the_cutoff():
    """200 chunks all tie, more than the first over-fetch; the engine
    returns an arbitrary tied subset of whatever size it is asked for,
    re-sorted here as `_ranked` would. The cut must keep extending the
    fetch until it has the whole tie group, so the kept rows are the
    smallest (doc_id, chunk index) keys."""
    chunks = [_chunk(f"doc{d:03d}", c) for d in range(40) for c in range(5)]
    fetches: list[int] = []

    def fetch(n: int) -> list[RankedChunk]:
        fetches.append(n)
        subset = random.Random(n).sample(chunks, min(n, len(chunks)))  # arbitrary tied subset
        return sorted((RankedChunk(chunk=c, score=1.0) for c in subset), key=lambda r: (r.doc_id, r.index))

    top = _deterministic_cut(fetch, 5)
    assert _keys(top) == _keys(sorted(chunks, key=lambda c: (c.doc_id, c.index))[:5])
    # the fetch had to grow past the whole tie group, doubling as it went
    assert fetches[0] == 5 + _OVERFETCH and fetches[-1] >= len(chunks) and fetches == sorted(set(fetches))


def test_the_cut_fetches_once_when_scores_are_distinct():
    calls: list[int] = []

    def fetch(n: int) -> list[RankedChunk]:
        calls.append(n)
        return [RankedChunk(chunk=_chunk(f"doc{i:02d}", 0), score=1.0 / (i + 1)) for i in range(min(n, 100))]

    top = _deterministic_cut(fetch, 5)
    assert calls == [5 + _OVERFETCH]  # no tie at the cutoff: one fetch is enough
    assert [r.doc_id for r in top] == [f"doc{i:02d}" for i in range(5)]


def test_bm25_ties_at_the_cutoff_come_back_in_the_same_order_every_time(tmp_path):
    chunks, texts = _tied_corpus(n_docs=6, chunks_per_doc=5)  # 30 identical chunks: one BM25 tie group
    index = BM25Index(tmp_path)
    index.build(chunks, texts)
    whole = index.search("alpha", 10**6)  # every match, so the cutoff cannot drop anything
    assert len(whole) == len(chunks)
    expected = _keys(whole[:7])
    assert expected == sorted(expected)  # the stable key orders the tie group
    for _ in range(10):
        assert _keys(index.search("alpha", 7)) == expected


def test_vector_ties_at_the_cutoff_come_back_in_the_same_order_every_time(tmp_path):
    chunks, _ = _tied_corpus(n_docs=6, chunks_per_doc=5)
    vectors = np.zeros((len(chunks), 4), dtype=np.float32)
    vectors[:, 0] = 1.0  # every chunk the same direction: cosine ties everywhere
    index = VectorIndex(tmp_path, table="vectors")
    index.build(chunks, vectors)
    whole = index.search(vectors[0], 10**6)
    assert len(whole) == len(chunks)
    expected = _keys(whole[:7])
    assert expected == sorted(expected)
    for _ in range(10):
        assert _keys(index.search(vectors[0], 7)) == expected
