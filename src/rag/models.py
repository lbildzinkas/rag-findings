"""The embedders and the reranker, run in-process through sentence-transformers.

Two embedders (decision 13) and one reranker (decision 20), each pinned to
a Hugging Face revision. `rag setup` downloads their safetensors weights,
tokenizers and configs (no ONNX or pickle weights) into the git-ignored
data/hf-cache/; runs load them from there without network.

An embedder's input limit is in its own tokenizer's tokens, counted on the
text it actually reads (task prefix and special tokens included), so a
chunk "exceeds the input limit" exactly when the model truncates it. The
task prefixes are what the model reads, not retrieved text: they never
count toward a token budget, which is always in cl100k tokens.

Tests inject fakes with the same small interface (`Embedder`, `Reranker`),
so they need no downloads.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass(frozen=True)
class EmbedderSpec:
    name: str  # registry key used in configs and result rows
    model_id: str
    revision: str
    max_tokens: int  # input limit, in the model's own tokens
    document_prefix: str = ""
    query_prefix: str = ""
    code_repo: str = ""  # repository of the model's remote code, when it has some
    code_revision: str = ""


@dataclass(frozen=True)
class RerankerSpec:
    name: str
    model_id: str
    revision: str


EMBEDDERS: dict[str, EmbedderSpec] = {
    spec.name: spec
    for spec in (
        EmbedderSpec(
            name="bge-small",
            model_id="BAAI/bge-small-en-v1.5",
            revision="5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
            max_tokens=512,
        ),
        EmbedderSpec(
            name="nomic",
            model_id="nomic-ai/nomic-embed-text-v1.5",
            revision="e9b6763023c676ca8431644204f50c2b100d9aab",
            max_tokens=8192,
            document_prefix="search_document: ",
            query_prefix="search_query: ",
            code_repo="nomic-ai/nomic-bert-2048",
            code_revision="7710840340a098cfb869c4f65e87cf2b1b70caca",
        ),
    )
}

RERANKER = RerankerSpec(
    name="gte-reranker-modernbert-base",
    model_id="Alibaba-NLP/gte-reranker-modernbert-base",
    revision="f7481e6055501a30fb19d090657df9ec1f79ab2c",
)

_WEIGHT_FILES = ["*.json", "*.txt", "model.safetensors"]


class Embedder(Protocol):
    spec: EmbedderSpec

    def input_tokens(self, texts: Sequence[str]) -> list[int]:
        """Tokens the model reads for each document text, prefix and special tokens included."""
        ...

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        """Unit-normalised float32 vectors, one row per text."""
        ...

    def embed_queries(self, texts: Sequence[str]) -> np.ndarray: ...


class Reranker(Protocol):
    spec: RerankerSpec

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        """A relevance score per (query, passage) pair; higher is more relevant."""
        ...


def hf_cache_dir(data_dir: Path) -> Path:
    return data_dir / "hf-cache"


def use_project_cache(data_dir: Path, offline: bool = False) -> None:
    """Point the Hugging Face libraries at data/hf-cache/ (unless HF_HOME is
    already set), offline for runs; must run before they are imported."""
    if not os.environ.get("HF_HOME"):
        os.environ["HF_HOME"] = str(hf_cache_dir(data_dir))
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"


def setup_models(data_dir: Path) -> list[str]:
    """Download the pinned weights, tokenizers and configs; idempotent."""
    use_project_cache(data_dir)
    from huggingface_hub import snapshot_download

    lines: list[str] = []
    downloads = [(s.model_id, s.revision, _WEIGHT_FILES) for s in EMBEDDERS.values()]
    downloads.append((RERANKER.model_id, RERANKER.revision, _WEIGHT_FILES))
    for repo_id, revision, patterns in downloads:
        snapshot_download(repo_id, revision=revision, allow_patterns=patterns)
        lines.append(f"present {repo_id}@{revision[:12]}")
    for spec in EMBEDDERS.values():
        if spec.code_repo:
            # transformers fetches a model's remote code from the code repo's
            # main branch (sentence-transformers drops `code_revision`), so
            # main is downloaded and must be the pinned revision
            path = snapshot_download(spec.code_repo, revision="main", allow_patterns=["*.py", "config.json"])
            _check_code_revision(spec, Path(path).name)
            lines.append(f"present {spec.code_repo}@{spec.code_revision[:12]} (remote code)")
    return lines


def _check_code_revision(spec: EmbedderSpec, resolved: str) -> None:
    if resolved != spec.code_revision:
        raise ValueError(
            f"{spec.code_repo} main is at {resolved[:12]}, not the pinned {spec.code_revision[:12]}; "
            "review the new remote code and update the pin"
        )


def _local_path(repo_id: str, revision: str) -> str:
    from huggingface_hub import snapshot_download

    try:
        return snapshot_download(repo_id, revision=revision, local_files_only=True)
    except Exception as exc:  # any cache miss means setup has not run
        raise FileNotFoundError(f"model {repo_id}@{revision[:12]} is not downloaded; run `uv run rag setup`") from exc


def _device() -> str:
    import torch

    if torch.backends.mps.is_available():
        return "mps"
    return "cuda" if torch.cuda.is_available() else "cpu"


class SentenceTransformerEmbedder:
    def __init__(self, spec: EmbedderSpec, batch_size: int = 32):
        from sentence_transformers import SentenceTransformer

        self.spec = spec
        self.batch_size = batch_size
        if spec.code_repo:
            _check_code_revision(spec, Path(_local_path(spec.code_repo, "main")).name)
        self._model = SentenceTransformer(
            _local_path(spec.model_id, spec.revision), device=_device(), trust_remote_code=bool(spec.code_repo)
        )
        self._model.max_seq_length = spec.max_tokens

    def input_tokens(self, texts: Sequence[str]) -> list[int]:
        tokenizer = self._model.tokenizer
        prefixed = [self.spec.document_prefix + t for t in texts]
        encoded = tokenizer(prefixed, add_special_tokens=True, truncation=False, verbose=False)["input_ids"]
        return [len(ids) for ids in encoded]

    def _encode(self, texts: Sequence[str], prefix: str) -> np.ndarray:
        vectors = self._model.encode(
            [prefix + t for t in texts],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, self.spec.document_prefix)

    def embed_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, self.spec.query_prefix)


class CrossEncoderReranker:
    def __init__(self, spec: RerankerSpec = RERANKER, batch_size: int = 16):
        from sentence_transformers import CrossEncoder

        self.spec = spec
        self.batch_size = batch_size
        self._model = CrossEncoder(_local_path(spec.model_id, spec.revision), device=_device())

    def score(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        # longest first, so each batch pads to similar lengths
        order = sorted(range(len(pairs)), key=lambda i: -len(pairs[i][1]))
        scores = self._model.predict(
            [pairs[i] for i in order], batch_size=self.batch_size, convert_to_numpy=True, show_progress_bar=False
        )
        out = [0.0] * len(pairs)
        for i, score in zip(order, scores, strict=True):
            out[i] = float(score)
        return out


class ModelSource(Protocol):
    """What a run needs from the models: embedders by name and the reranker."""

    def embedder(self, name: str) -> Embedder: ...

    def reranker(self) -> Reranker: ...


@dataclass
class Models:
    """The real models, loaded on first use; tests pass fakes instead."""

    data_dir: Path

    def embedder(self, name: str) -> Embedder:
        return _load_embedder(self.data_dir, name)

    def reranker(self) -> Reranker:
        return _load_reranker(self.data_dir)


@cache
def _load_embedder(data_dir: Path, name: str) -> Embedder:
    use_project_cache(data_dir, offline=True)
    return SentenceTransformerEmbedder(EMBEDDERS[name])


@lru_cache(maxsize=1)
def _load_reranker(data_dir: Path) -> Reranker:
    use_project_cache(data_dir, offline=True)
    return CrossEncoderReranker()
