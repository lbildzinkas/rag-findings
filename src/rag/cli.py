"""Command line entry point: `rag setup` and `rag run <config>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .paths import Paths


def _paths(args: argparse.Namespace) -> Paths:
    return Paths(root=Path(args.root).expanduser().resolve() if args.root else Path.cwd())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rag", description="RAG chunking retrieval experiments")
    sub = parser.add_subparsers(dest="command", required=True)

    setup_parser = sub.add_parser(
        "setup", help="download and verify QASPER v0.3 dev and test, and the pinned embedders and reranker"
    )
    setup_parser.add_argument(
        "--root",
        default=None,
        help="project root holding data/ (default: current directory)",
    )
    setup_parser.add_argument(
        "--no-models", action="store_true", help="skip the model downloads (enough for BM25-only runs)"
    )

    run_parser = sub.add_parser("run", help="run a retrieval eval (one cell, or a grid with `kind: grid`)")
    run_parser.add_argument("config", type=Path, help="path to the run config YAML")
    run_parser.add_argument(
        "--root",
        default=None,
        help="project root holding data/, runs/ and results/ (default: current directory)",
    )
    run_parser.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="grid runs only: a seeded sample of N papers, with outputs and tables under runs/<run_name>-sampleN/",
    )

    args = parser.parse_args(argv)
    paths = _paths(args)

    if args.command == "setup":
        from .setup_cmd import setup
        from .tokens import get_encoding

        for line in setup(paths.data):
            print(line)
        if not args.no_models:
            from .models import setup_models

            for line in setup_models(paths.data):
                print(line)
        get_encoding()  # warm the tokenizer cache so runs need no network
        print("setup complete")
        return 0

    if args.command == "run":
        from .config import GridConfig, load_any_config

        cfg = load_any_config(args.config)
        if isinstance(cfg, GridConfig):
            from .grid import run_grid

            run_grid(cfg, paths, sample=args.sample)
            return 0
        if args.sample is not None:
            parser.error("--sample applies to grid runs only")
        from .run import run

        run(args.config, paths)
        return 0

    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
