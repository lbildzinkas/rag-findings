"""Context prefixes on a synthetic corpus with a fake writer: the prompt
and its pinned hash, document windows, the store's resume after an
interruption, the --estimate projection and the manifest."""

from __future__ import annotations

import json
import sqlite3
from itertools import pairwise
from pathlib import Path

import pytest
import yaml

from rag.chunking import Chunk
from rag.cli import main
from rag.paths import Paths
from rag.prefixes import (
    Prefix,
    PromptTemplate,
    context_windows,
    load_prefix_config,
    load_prompt,
    parse_prefix_config,
    run_prefixes,
)
from tests.conftest import FakeEncoding, make_paper, write_split

REPO = Path(__file__).resolve().parents[1]
MODEL = "fake/prefix-model"
REVISION = "0" * 40
PROMPT = "<document>\n{document}\n</document>\n<chunk>\n{chunk}\n</chunk>\nSituate the chunk.\n"
WORDS = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "pi",
    "rho",
    "sigma",
    "tau",
]


class FakeWriter:
    """A deterministic prefix per chunk; records every call; can fail on
    the n-th call to stand in for an interrupted run."""

    model_key = f"{MODEL}@{REVISION}"

    def __init__(self, fail_on_call: int | None = None, tokens: int = 7, max_new_tokens: int = 120):
        self.calls: list[tuple[str, list[str]]] = []
        self.fail_on_call = fail_on_call
        self.tokens = tokens
        self.max_new_tokens = max_new_tokens

    def write(self, context, chunks):
        self.calls.append((context, list(chunks)))
        if self.fail_on_call is not None and len(self.calls) == self.fail_on_call:
            raise KeyboardInterrupt
        n = min(self.tokens, self.max_new_tokens)
        return [Prefix(f"context {len(context)}: {chunk[:5]}", n, n == self.max_new_tokens) for chunk in chunks]


def _paragraph(seed: int, n_words: int) -> str:
    return " ".join(WORDS[(seed + i) % len(WORDS)] for i in range(n_words))


def build_env(root: Path, context_tokens: int = 160) -> Path:
    """Three papers (one longer than the context) and a prefix config."""
    dev = {
        "paperA": make_paper("paperA", _paragraph(0, 6), [("Intro", [_paragraph(1, 10)])]),
        "paperB": make_paper(
            "paperB", _paragraph(2, 8), [("Intro", [_paragraph(3, 30)]), ("More", [_paragraph(4, 20)])]
        ),
    }
    test = {"paperC": make_paper("paperC", _paragraph(5, 5), [("Intro", [_paragraph(6, 12)])])}
    write_split(root / "data" / "qasper" / "qasper-dev-v0.3.json", dev)
    write_split(root / "data" / "qasper" / "qasper-test-v0.3.json", test)
    prompt = PromptTemplate(PROMPT)
    (root / "configs").mkdir(parents=True, exist_ok=True)
    (root / "configs" / "prompt.txt").write_text(PROMPT, encoding="utf-8")
    config = {
        "kind": "prefixes",
        "dataset": {"name": "qasper", "splits": ["dev", "test"]},
        "chunking": {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        "model": {"id": MODEL, "revision": REVISION},
        "prompt": "configs/prompt.txt",
        "prompt_sha256": prompt.sha256,
        "context_tokens": context_tokens,
        "max_new_tokens": 120,
        "batch_size": 6,
        "seed": 0,
        "manifest": "results/prefixes/manifest.json",
    }
    path = root / "configs" / "prefixes.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return path


def _rows(root: Path) -> list[tuple]:
    with sqlite3.connect(Paths(root).prefixes) as db:
        return db.execute("SELECT * FROM prefixes ORDER BY doc_hash, start").fetchall()


def _run(config_path: Path, root: Path, writer, estimate=None, logs=None):
    return run_prefixes(
        load_prefix_config(config_path),
        Paths(root=root),
        writer=writer,
        estimate=estimate,
        encoding=FakeEncoding(),
        log=(logs.append if logs is not None else lambda _line: None),
    )


def test_committed_prompt_matches_its_pinned_hash():
    cfg = load_prefix_config(REPO / "configs" / "prefixes.yaml")
    prompt = load_prompt(cfg, REPO)
    assert prompt.sha256 == cfg.prompt_sha256
    head, tail = prompt.split("THE DOCUMENT")
    assert head.startswith("<document>\nTHE DOCUMENT\n</document>\n")
    assert tail.startswith("\n</chunk>\nPlease give a short succinct context to situate this chunk")
    assert tail.endswith("Answer only with the succinct context and nothing else.")
    assert (cfg.chunking.chunk_tokens, cfg.context_tokens, cfg.max_new_tokens, cfg.batch_size) == (256, 8192, 120, 6)


def test_prompt_needs_both_slots_in_order():
    with pytest.raises(ValueError, match="exactly once"):
        PromptTemplate("{document} only")
    with pytest.raises(ValueError, match="before"):
        PromptTemplate("{chunk} then {document}")


def test_edited_prompt_fails_against_the_pinned_hash(tmp_path):
    config_path = build_env(tmp_path)
    (tmp_path / "configs" / "prompt.txt").write_text(PROMPT.replace("Situate", "Place"), encoding="utf-8")
    with pytest.raises(ValueError, match="not the pinned"):
        _run(config_path, tmp_path, FakeWriter())


def test_config_rejects_short_revision_and_variable_chunkings(tmp_path):
    raw = yaml.safe_load(build_env(tmp_path).read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="40-character"):
        parse_prefix_config({**raw, "model": {"id": MODEL, "revision": "abc123"}})
    with pytest.raises(ValueError, match="fixed chunkings"):
        parse_prefix_config({**raw, "chunking": {"name": "s", "method": "section_aware", "max_tokens": 64}})


def _chunks(sizes: list[int]) -> list[Chunk]:
    out, start = [], 0
    for i, n in enumerate(sizes):
        out.append(Chunk("d", i, start, start + n, start, start + n, n))
        start += n
    return out


def test_context_windows_whole_document_when_it_fits():
    assert context_windows(_chunks([256] * 32), 8192) == [(0, 32)]
    assert context_windows(_chunks([256] * 3 + [10]), 8192) == [(0, 4)]
    assert context_windows([], 8192) == []


def test_context_windows_cut_long_documents_into_near_equal_windows():
    windows = context_windows(_chunks([256] * 33 + [40]), 8192)
    assert windows == [(0, 17), (17, 34)]
    chunks = _chunks([256] * 100 + [7])
    windows = context_windows(chunks, 8192)
    assert len(windows) == 4 and windows[0][0] == 0 and windows[-1][1] == len(chunks)
    assert all(a == b for (_, a), (b, _) in pairwise(windows))
    assert all(sum(c.n_tokens for c in chunks[a:b]) <= 8192 for a, b in windows)
    with pytest.raises(ValueError, match="longer than"):
        context_windows(_chunks([300]), 256)


def test_every_chunk_gets_a_prefix_and_the_manifest_has_no_text(tmp_path):
    config_path = build_env(tmp_path)
    writer = FakeWriter()
    manifest = _run(config_path, tmp_path, writer)

    rows = _rows(tmp_path)
    assert manifest["chunks"] == manifest["chunks_with_prefix"] == len(rows) > 0
    assert manifest["missing"] == [] and manifest["truncated"] == []
    cfg = load_prefix_config(config_path)
    assert {(r[0], r[1]) for r in rows} == {(f"{MODEL}@{REVISION}", cfg.prompt_sha256)}
    assert manifest["prompt_sha256"] == cfg.prompt_sha256
    assert manifest["datasets"]["qasper"]["documents"] == 3
    assert manifest["datasets"]["qasper"]["documents_in_windows"] == 1  # paperB is longer than 160 tokens
    assert manifest["prefix_tokens"]["min"] == manifest["prefix_tokens"]["max"] == 7
    written = (tmp_path / "results" / "prefixes" / "manifest.json").read_text(encoding="utf-8")
    assert json.loads(written) == manifest
    assert not any(row[5] in written for row in rows)  # no prefix text in the committed manifest
    # a window of whole chunks is each chunk's context; every chunk lies inside its window
    assert all(r[8] <= r[3] and r[4] <= r[9] for r in rows)
    assert all(len(context) <= 160 for context, _ in writer.calls)


def test_interrupted_run_resumes_without_rewriting_stored_prefixes(tmp_path):
    config_path = build_env(tmp_path)
    with pytest.raises(KeyboardInterrupt):
        _run(config_path, tmp_path, FakeWriter(fail_on_call=2))
    first = _rows(tmp_path)
    assert first  # the first document committed before the interruption

    class Different(FakeWriter):
        def write(self, context, chunks):
            self.calls.append((context, list(chunks)))
            return [Prefix("rewritten", 3, False) for _ in chunks]

    resumed = Different()
    manifest = _run(config_path, tmp_path, resumed)
    rows = _rows(tmp_path)
    assert manifest["chunks_with_prefix"] == manifest["chunks"] == len(rows)
    stored_first = {r[2:5]: r[5] for r in first}
    assert all(r[5] == stored_first[r[2:5]] for r in rows if r[2:5] in stored_first)
    assert {r[5] for r in rows if r[2:5] not in stored_first} == {"rewritten"}

    again = FakeWriter()
    _run(config_path, tmp_path, again)
    assert again.calls == []  # nothing left to write
    assert _rows(tmp_path) == rows


def test_estimate_writes_a_seeded_sample_and_projects_hours(tmp_path):
    config_path = build_env(tmp_path)
    logs: list[str] = []
    projection = _run(config_path, tmp_path, FakeWriter(), estimate=2, logs=logs)
    assert projection["qasper"]["documents"] == 2
    assert projection["qasper"]["hours"] >= projection["qasper"]["hours_left"] >= 0
    assert logs[-1].startswith("projected full run: ")
    assert not (tmp_path / "results" / "prefixes" / "manifest.json").exists()
    sampled = {r[2] for r in _rows(tmp_path)}
    assert len(sampled) == 2

    again = FakeWriter()
    assert _run(config_path, tmp_path, again, estimate=2)["qasper"]["documents"] == 2
    assert again.calls == []  # the same seeded sample, already stored

    rest = FakeWriter()
    _run(config_path, tmp_path, rest)
    assert {r[2] for r in _rows(tmp_path)} > sampled
    assert all(sampled.isdisjoint({context}) for context, _ in rest.calls)


def test_manifest_flags_prefixes_cut_at_the_token_limit_and_empty_ones(tmp_path):
    config_path = build_env(tmp_path)

    class Cut(FakeWriter):
        def write(self, context, chunks):
            return [
                Prefix("", 0, False) if i == 0 else Prefix("long", self.max_new_tokens, True)
                for i, _ in enumerate(chunks)
            ]

    manifest = _run(config_path, tmp_path, Cut())
    assert manifest["missing"] and manifest["truncated"]
    assert manifest["chunks_with_prefix"] == manifest["chunks"] - len(manifest["missing"])
    assert {k for k in manifest["truncated"][0]} == {"dataset", "doc_id", "chunk"}


def test_a_different_prompt_is_a_different_prefix_set(tmp_path):
    config_path = build_env(tmp_path)
    _run(config_path, tmp_path, FakeWriter())
    edited = PROMPT.replace("Situate", "Place")
    (tmp_path / "configs" / "prompt.txt").write_text(edited, encoding="utf-8")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw["prompt_sha256"] = PromptTemplate(edited).sha256
    config_path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    writer = FakeWriter()
    _run(config_path, tmp_path, writer)
    assert writer.calls  # nothing stored under the new prompt's hash yet
    assert len({r[1] for r in _rows(tmp_path)}) == 2


def test_cli_prefixes_command(tmp_path, monkeypatch, capsys):
    config_path = build_env(tmp_path)
    monkeypatch.setattr("rag.prefix_model.load_writer", lambda cfg, data_dir, prompt: FakeWriter())
    monkeypatch.setattr("rag.prefixes.TokenText", _fake_token_text)
    assert main(["prefixes", str(config_path), "--root", str(tmp_path), "--estimate", "1"]) == 0
    assert "projected full run" in capsys.readouterr().out
    assert main(["prefixes", str(config_path), "--root", str(tmp_path)]) == 0
    assert "chunks have a prefix" in capsys.readouterr().out


def _fake_token_text(text, _encoding=None):
    from rag.tokens import TokenText

    return TokenText(text, FakeEncoding())
