"""Project layout: data (git-ignored downloads), runs (git-ignored outputs)
and results (committed tables) live under the working directory, so the
ticket's `uv run rag setup && uv run rag run configs/tracer.yaml` works from
the repository root.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def cache(self) -> Path:
        """Embeddings and reranker scores reused across runs (git-ignored)."""
        return self.data / "cache"

    @property
    def prefixes(self) -> Path:
        """Context prefixes written for contextual chunks (git-ignored)."""
        return self.data / "prefixes" / "prefixes.sqlite"

    @property
    def runs(self) -> Path:
        return self.root / "runs"

    @property
    def results(self) -> Path:
        return self.root / "results"

    def run_dir(self, run_name: str, dataset: str | None = None) -> Path:
        """Runs are namespaced per dataset label (qasper, nq, pooled), so
        runs of different datasets never share lance tables."""
        return self.runs / dataset / run_name if dataset else self.runs / run_name


def default_paths(cwd: Path | None = None) -> Paths:
    return Paths(root=cwd if cwd is not None else Path.cwd())
