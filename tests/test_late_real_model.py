"""The one real-model check of the late-chunking ticket: a window holding
a single chunk reproduces that chunk's independent vector (cosine
>= 0.9999), checked once against the real model.

The unit suite stays offline on the fake token-embedding model
(tests/test_late.py); this module runs only where `uv run rag setup` has
downloaded the pinned nomic model into the git-ignored data/hf-cache/
(where a run's `use_project_cache` points every Hugging Face import), so
CI's download-free suite just skips it. It embeds deterministic synthetic
text, so no dataset text enters git.

What it checks, under the settled pooling design (ADR 0005, ADR 0007):
the late-embedding mechanism. Reading one window that holds a single
chunk and pooling every token the model read - prefix and special tokens
included, exactly the tokens the model's own independent embedding
averages - reproduces that independent vector, which is what the unit
suite's `..._pooled_over_all_its_tokens_is_the_independent_vector`
states on the fake model; the 0.9999 bar leaves float slop. The shipped
pooling rule additionally leaves the prefix and special tokens out of
every chunk, so it necessarily sits just under the independent vector
(about 2e-4 of cosine on a ~130-token chunk): the check reports that
deviation instead of failing on it, and the run's numbers are recorded
in results/late-single-chunk-cosine.md.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

import numpy as np
import pytest

from rag import tokens as _tokens
from rag.models import EMBEDDERS, Models, hf_cache_dir
from rag.paths import default_paths
from rag.tokens import TokenText

# The Hugging Face libraries resolve their cache at import time; point them
# where `rag setup` writes before any test imports them (a run's
# use_project_cache does the same).
_DATA = default_paths().data
os.environ["HF_HOME"] = str(hf_cache_dir(_DATA))

# captured at collection, before the conftest guard patches the name away
_REAL_ENCODING = _tokens.get_encoding

_NOMIC = EMBEDDERS["nomic"]


def _snapshot_dir(repo: str, revision: str) -> Path:
    return hf_cache_dir(_DATA) / "hub" / f"models--{repo.replace('/', '--')}" / "snapshots" / revision


def _model_downloaded() -> bool:
    weights = (_snapshot_dir(_NOMIC.model_id, _NOMIC.revision) / "model.safetensors").is_file()
    code_ref = (
        hf_cache_dir(_DATA) / "hub" / f"models--{_NOMIC.code_repo.replace('/', '--')}" / "refs" / "main"
    ).is_file()
    return weights and code_ref


pytestmark = pytest.mark.skipif(
    not _model_downloaded(), reason="the pinned nomic model is not downloaded; run `uv run rag setup`"
)

VOCAB = [
    "retrieval",
    "recall",
    "precision",
    "chunking",
    "embedding",
    "transformer",
    "attention",
    "token",
    "document",
    "corpus",
    "query",
    "router",
    "headroom",
    "baseline",
    "section",
    "paragraph",
    "window",
    "pooling",
    "cosine",
    "similarity",
    "hybrid",
    "fusion",
    "reranker",
    "budget",
    "packing",
    "span",
    "offset",
    "context",
    "surroundings",
    "passage",
    "wikipedia",
    "paper",
    "experiment",
    "measure",
    "estimate",
    "kerberos",
    "tickets",
    "session",
    "keys",
    "protocol",
    "network",
    "latency",
    "throughput",
    "memory",
    "gradient",
    "descent",
    "optimizer",
]


def _paragraph(seed: int, sentences: int) -> str:
    """Deterministic synthetic text: no dataset text enters git."""
    rng = random.Random(seed)
    out = []
    for _ in range(sentences):
        words = [rng.choice(VOCAB) for _ in range(rng.randint(8, 14))]
        out.append(" ".join(words) + ".")
    return " ".join(out)


def _unit(rows: np.ndarray) -> np.ndarray:
    mean = rows.astype(np.float64).mean(axis=0)
    return (mean / np.linalg.norm(mean)).astype(np.float32)


CHUNKS_PER_SIZE = 8
BAR = 0.9999


def test_a_window_holding_a_single_chunk_reproduces_the_independent_vector():
    from rag.chunking import fixed_windows
    from rag.documents import build_document
    from rag.late import block_spans, late_vectors, plan_windows

    embedder = Models(_DATA).embedder("nomic")
    encoding = _REAL_ENCODING()
    doc = build_document("single-chunk-check", "", [("Body", [_paragraph(seed, 90) for seed in range(4)])])
    tokens = TokenText(doc.text, encoding)
    report = [
        (
            f"real model: {embedder.spec.model_id} @ {embedder.spec.revision[:12]} "
            f"| model_kwargs {dict(embedder.spec.model_kwargs)}"
        )
    ]
    for size in (128, 256):
        chunks = fixed_windows(doc, tokens, size)[:CHUNKS_PER_SIZE]
        assert len(chunks) == CHUNKS_PER_SIZE, "the synthetic document must yield enough chunks"
        rule, mechanism, independent = [], [], []
        for chunk in chunks:
            text = doc.text[chunk.start : chunk.end]
            independent.append(embedder.embed_documents([text])[0])
            windows = plan_windows(text, block_spans(TokenText(text, encoding)), embedder.input_tokens)
            assert [(w.start, w.end) for w in windows] == [(0, len(text))]  # a window holding a single chunk
            rule.append(late_vectors(text, [[(0, len(text))]], windows, embedder)[0][0])  # the shipped pooling rule
            mechanism.append(_unit(embedder.token_embeddings(text).vectors))  # every token the model read

        def cosines(vectors: list[np.ndarray], independent: list[np.ndarray] = independent) -> list[float]:
            return sorted(float(np.dot(v, i)) for v, i in zip(vectors, independent, strict=True))

        for name, values in (
            ("every token read (the mechanism; the bar)", cosines(mechanism)),
            ("shipped rule (prefix and specials out, by design)", cosines(rule)),
        ):
            report.append(f"fixed-{size}: {name}: min {values[0]:.6f}  median {values[len(values) // 2]:.6f}")
        assert cosines(mechanism)[0] >= BAR  # the acceptance criterion
        # the settled design leaves the prefix and special tokens out, which costs
        # ~2e-4 of cosine on a ~130-token chunk: bounded, expected, recorded
        assert cosines(rule)[0] >= 0.999
    print("\n".join(report))
