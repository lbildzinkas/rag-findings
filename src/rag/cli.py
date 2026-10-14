"""Command line entry point: `rag setup`, `rag sample`, `rag run <config>`, `rag headroom <config>` and `rag writeup`."""

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
        "setup",
        help="download and verify QASPER v0.3 dev and test, the Natural Questions dev config, and the pinned "
        "embedders and reranker",
    )
    setup_parser.add_argument(
        "--root",
        default=None,
        help="project root holding data/ (default: current directory)",
    )
    setup_parser.add_argument(
        "--no-models", action="store_true", help="skip the model downloads (enough for BM25-only runs)"
    )

    sample_parser = sub.add_parser(
        "sample", help="sample the committed Natural Questions subset id list from the dev config"
    )
    sample_parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="sampling seed recorded in the id list header (default: 0)",
    )
    sample_parser.add_argument(
        "--per-type",
        type=int,
        default=500,
        help="questions per query type: short answer and long-answer-only (default: 500)",
    )
    sample_parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="id list path (default: configs/nq-subset.txt under the root)",
    )
    sample_parser.add_argument(
        "--root",
        default=None,
        help="project root holding data/ (default: current directory)",
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
        help="grid runs only: a seeded sample of N papers, with outputs and tables under runs/<dataset>/<run_name>-sampleN/",
    )

    headroom_parser = sub.add_parser(
        "headroom", help="routing headroom, the router gate and the interaction, from grid run results"
    )
    headroom_parser.add_argument("config", type=Path, help="path to the headroom config YAML")
    headroom_parser.add_argument(
        "--root",
        default=None,
        help="project root holding runs/ and results/ (default: current directory)",
    )

    writeup_parser = sub.add_parser(
        "writeup", help="regenerate the v1 write-up's tables and figures from the committed result tables"
    )
    writeup_parser.add_argument(
        "--check",
        action="store_true",
        help="change nothing; fail when the write-up or a figure differs from the result tables",
    )
    writeup_parser.add_argument(
        "--root",
        default=None,
        help="project root holding results/ and chunking/ (default: current directory)",
    )

    args = parser.parse_args(argv)
    paths = _paths(args)

    if args.command == "setup":
        from .nq import setup_nq
        from .setup_cmd import setup
        from .tokens import get_encoding

        for line in setup(paths.data):
            print(line)
        for line in setup_nq(paths.data):
            print(line)
        if not args.no_models:
            from .models import setup_models

            for line in setup_models(paths.data):
                print(line)
        get_encoding()  # warm the tokenizer cache so runs need no network
        print("setup complete")
        return 0

    if args.command == "sample":
        from .nq import ensure_nq_shards, sample_subset, subset_ids_path

        shard_paths = ensure_nq_shards(paths.data)
        out_path = args.out if args.out is not None else subset_ids_path(paths.root)
        funnel = sample_subset(shard_paths, seed=args.seed, per_type=args.per_type, out_path=out_path)
        print(
            f"sampled {funnel['sampled_short']} short-answer and {funnel['sampled_long_only']} long-answer-only questions"
        )
        print(f"  dev examples scanned: {funnel['examples']}")
        print(f"  long-answer agreement (>= 2 of 5 annotators): {funnel['long_answer_agreement']}")
        print(f"  paragraph long answers: {funnel['paragraph_eligible']}")
        print(f"  eligible: {funnel['eligible_short']} short answer, {funnel['eligible_long_only']} long-answer-only")
        print(f"  id list: {out_path}")
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

    if args.command == "headroom":
        from .routing import load_headroom_config, run_headroom

        run_headroom(load_headroom_config(args.config), paths)
        return 0

    if args.command == "writeup":
        from .writeup import check, write

        if args.check:
            problems = check(paths.root)
            for problem in problems:
                print(problem)
            return 1 if problems else 0
        for relative in write(paths.root):
            print(f"wrote {relative}")
        return 0

    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
