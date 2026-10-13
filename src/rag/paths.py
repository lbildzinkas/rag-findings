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
    def runs(self) -> Path:
        return self.root / "runs"

    @property
    def results(self) -> Path:
        return self.root / "results"

    def run_dir(self, run_name: str) -> Path:
        return self.runs / run_name


def default_paths(cwd: Path | None = None) -> Paths:
    return Paths(root=cwd if cwd is not None else Path.cwd())
