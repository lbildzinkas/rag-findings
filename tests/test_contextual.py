"""Contextual chunks on a synthetic corpus with fake models and a fake
prefix store: the config keys, search texts (BM25, vectors, reranker),
cache keys apart from the plain chunks', packing and scoring on the
chunk's own span, the side variant's prefix in the budget, the run's
failure on a missing prefix, a cached re-run, the side variant's reader
text and R13."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest
import yaml

from rag.answers import (
    Sample,
    SampledQuestion,
    load_packed,
    parse_answers_config,
    reader_prefixes,
    render_setup_prompts,
)
from rag.cache import Cache
from rag.chunking import Chunk, fixed_windows
from rag.config import config_hash, load_any_config, parse_grid_config
from rag.contenders import load_contenders_config, parse_contenders_config, run_contenders
from rag.contextual import SEPARATOR, key_suffix, search_text
from rag.grid import run_grid
from rag.metrics import score_question
from rag.models import EMBEDDERS, RERANKER
from rag.packing import pack
from rag.paths import Paths
from rag.pipelines import model_key
from rag.prefixes import Prefix, PrefixStore
from rag.run import gold_token_sets, load_datasets
from rag.tokens import TokenText
from tests.conftest import FakeEncoding
from tests.test_grid import build_env, table_rows
from tests.test_late import _write_run
from tests.test_production import PRODUCTION, FakeModels

PREFIX_SET = {"model": "fake/prefix-model", "revision": "0" * 40, "prompt_sha256": "1" * 64}
CONTEXTUAL_GRID = {
    **PRODUCTION,
    "pipelines": ["hybrid-rerank", "bm25"],
    "embedders": ["nomic"],
    "chunkings": [
        {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        {"name": "contextual-16", "method": "fixed", "chunk_tokens": 16, "prefixes": PREFIX_SET},
        {
            "name": "contextual-16-prefixed",
            "method": "fixed",
            "chunk_tokens": 16,
            "prefixes": PREFIX_SET,
            "prefix_in_budget": True,
        },
    ],
    "budget_top_n": 3,
    "run_name": "v2-contextual",
    "export_packed": [{"view": "budget", "budget": 64, "scope": "collection"}],
}
MODEL_KEY = f"{PREFIX_SET['model']}@{PREFIX_SET['revision']}"


def _prefix(doc_id: str, index: int) -> str:
    """A short prefix whose words the questions share, so it moves search."""
    return f"kerberos context {doc_id} {index}"


def write_store(root: Path, skip: tuple[str, int] | None = None, blank: tuple[str, int] | None = None) -> None:
    """A fake prefix for every 16-token chunk of the synthetic corpus,
    except the `skip` chunk; the `blank` chunk's prefix is empty."""
    paths = Paths(root=root)
    _, documents, _ = load_datasets(paths, parse_grid_config(CONTEXTUAL_GRID).sources)
    store = PrefixStore(paths.prefixes)
    for doc_id in sorted(documents):
        doc = documents[doc_id]
        records = []
        for chunk in fixed_windows(doc, TokenText(doc.text, FakeEncoding()), 16):
            if (doc_id, chunk.index) == skip:
                continue
            text = "  " if (doc_id, chunk.index) == blank else _prefix(doc_id, chunk.index)
            records.append((chunk, (0, len(doc.text)), Prefix(text, 5, False)))
        store.put_document(MODEL_KEY, PREFIX_SET["prompt_sha256"], doc.source_hash, records, 0.0)
    store.close()


def _run(root: Path):
    models = FakeModels()
    outcome = run_grid(parse_grid_config(CONTEXTUAL_GRID), Paths(root=root), encoding=FakeEncoding(), models=models)
    return outcome, models, json.loads((outcome.run_dir / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def contextual_run(tmp_path):
    build_env(tmp_path)
    write_store(tmp_path)
    outcome, models, manifest = _run(tmp_path)
    return tmp_path, outcome, models, manifest


def _rows(outcome, name: str) -> list[dict]:
    return pq.read_table(outcome.run_dir / name).to_pylist()


# --- config ---------------------------------------------------------------------


def test_the_prefix_keys_enter_only_a_contextual_chunkings_canonical_json():
    cfg = parse_grid_config(CONTEXTUAL_GRID)
    assert [(c.contextual, c.prefix_in_budget) for c in cfg.chunkings] == [(False, False), (True, False), (True, True)]
    rendered = [c.as_dict() for c in cfg.chunkings]
    assert "prefixes" not in rendered[0] and "prefix_in_budget" not in rendered[0]
    assert rendered[1]["prefixes"] == PREFIX_SET and "prefix_in_budget" not in rendered[1]
    assert rendered[2]["prefix_in_budget"] is True
    explicit = {**CONTEXTUAL_GRID, "chunkings": [{**CONTEXTUAL_GRID["chunkings"][1], "prefix_in_budget": False}]}
    implicit = {**CONTEXTUAL_GRID, "chunkings": CONTEXTUAL_GRID["chunkings"][1:2]}
    assert config_hash(parse_grid_config(explicit)) == config_hash(parse_grid_config(implicit))
    assert key_suffix(cfg.chunkings[1].prefixes) == f"#ctx:{MODEL_KEY}:{'1' * 64}"


@pytest.mark.parametrize(
    ("chunking", "message"),
    [
        ({"name": "s", "method": "section_aware", "max_tokens": 64, "prefixes": PREFIX_SET}, "fixed windows"),
        ({"name": "x", "method": "fixed", "chunk_tokens": 16, "embedding": "late", "prefixes": PREFIX_SET}, "fixed"),
        ({"name": "x", "method": "fixed", "chunk_tokens": 16, "prefix_in_budget": True}, "needs a prefix set"),
        (
            {"name": "x", "method": "fixed", "chunk_tokens": 16, "prefixes": PREFIX_SET, "prefix_in_budget": "yes"},
            "true or false",
        ),
        (
            {"name": "x", "method": "fixed", "chunk_tokens": 16, "prefixes": {**PREFIX_SET, "revision": "abc"}},
            "40-character",
        ),
        (
            {"name": "x", "method": "fixed", "chunk_tokens": 16, "prefixes": {**PREFIX_SET, "prompt_sha256": "ab"}},
            "sha256",
        ),
        ({"name": "x", "method": "fixed", "chunk_tokens": 16, "prefixes": {"model": "m"}}, "invalid grid config"),
    ],
)
def test_contextual_chunking_config_errors(chunking, message):
    with pytest.raises(ValueError, match=message):
        parse_grid_config({**CONTEXTUAL_GRID, "chunkings": [chunking]})


def test_the_v2_contextual_configs_name_the_committed_prefix_set_and_r13():
    prefixes = yaml.safe_load(Path("configs/prefixes.yaml").read_text(encoding="utf-8"))
    for dataset in ("qasper", "nq"):
        cfg = load_any_config(Path(f"configs/v2/{dataset}-contextual.yaml"))
        assert [c.name for c in cfg.chunkings] == [
            "fixed-256",
            "section-aware",
            "contextual-256",
            "contextual-256-prefixed",
        ]
        assert cfg.embedders == ("nomic",) and cfg.budget_top_n == 20 and cfg.run_name == "v2-contextual"
        for spec in cfg.chunkings[2:]:
            assert spec.chunk_tokens == prefixes["chunking"]["chunk_tokens"] == 256
            assert spec.prefixes.as_dict() == {
                "model": prefixes["model"]["id"],
                "revision": prefixes["model"]["revision"],
                "prompt_sha256": prefixes["prompt_sha256"],
            }
        assert [c.prefix_in_budget for c in cfg.chunkings] == [False, False, False, True]
    r13 = load_contenders_config(Path("configs/v2/contextual.yaml"))
    assert r13.runs == ("qasper/v2-contextual", "nq/v2-contextual") and r13.table == "r13"
    assert r13.run_name == "v2-contextual"


# --- packing --------------------------------------------------------------------


def _chunk(index: int, n_tokens: int) -> Chunk:
    start = index * n_tokens
    return Chunk("d", index, start, start + n_tokens, start, start + n_tokens, n_tokens)


def test_the_side_variants_prefix_pushes_a_chunk_out_of_the_budget():
    ranked = [_chunk(i, 10) for i in range(3)]
    assert pack(ranked, 25, None) == ranked[:2]  # 10 + 10 chunk tokens fit 25
    with_prefix = pack(ranked, 25, None, cost=lambda c: c.n_tokens + 4)
    assert with_prefix == ranked[:1]  # 14 + 14 = 28 > 25: the prefix pushes the second chunk out
    assert pack(ranked, 28, None, cost=lambda c: c.n_tokens + 4) == ranked[:2]
    # a chunk whose prefix makes it cost more than the whole budget never packs
    assert pack(ranked, 12, None, cost=lambda c: c.n_tokens + 4) == []


# --- a grid run -------------------------------------------------------------------


def test_packed_contextual_chunks_carry_chunk_tokens_and_are_scored_on_their_spans(contextual_run):
    root, outcome, _, _ = contextual_run
    paths = Paths(root=root)
    splits, documents, _ = load_datasets(paths, parse_grid_config(CONTEXTUAL_GRID).sources)
    tokenized = {d: TokenText(documents[d].text, FakeEncoding()) for d in documents}
    fixed = {
        (c.doc_id, c.start, c.end): c for d in sorted(documents) for c in fixed_windows(documents[d], tokenized[d], 16)
    }
    packed = [r for r in _rows(outcome, "packed.parquet") if r["chunking"] == "contextual-16"]
    assert packed
    for row in packed:  # fixed-16's span and its chunk tokens, no prefix
        assert row["tokens"] == fixed[(row["doc_id"], row["start"], row["end"])].n_tokens
    questions = {q.question_id: q for split in splits for q in split.questions}
    results = {
        (r["question_id"], r["pipeline"]): r
        for r in _rows(outcome, "results.parquet")
        if r["chunking"] == "contextual-16"
        and r["view"] == "budget"
        and r["budget"] == 64
        and r["scope"] == "collection"
    }
    for (question_id, pipeline), result in results.items():
        chunks = [
            fixed[(r["doc_id"], r["start"], r["end"])]
            for r in sorted(packed, key=lambda r: r["rank"])
            if r["question_id"] == question_id and r["pipeline"] == pipeline
        ]
        question = questions[question_id]
        score = score_question(gold_token_sets(question, tokenized), chunks, question.doc_id)
        assert (result["recall"], result["precision"]) == (score.recall, score.precision)
        assert result["retrieved_tokens"] == sum(c.n_tokens for c in chunks) <= 64


def test_search_reads_the_prefix_and_ranks_differently_from_the_plain_chunks(contextual_run):
    _root, outcome, models, _ = contextual_run
    texts = [p for _, p in models.reranker_model.pairs]
    assert any(t.startswith("kerberos context ") and SEPARATOR in t for t in texts)  # (question, search text)
    assert any(not t.startswith("kerberos context ") for t in texts)  # fixed-16's plain pairs

    def cells(pipeline: str, chunking: str) -> list:
        return [
            (r["question_id"], r["k"], r["hit"], r["recall"])
            for r in _rows(outcome, "fixed_k.parquet")
            if r["pipeline"] == pipeline and r["chunking"] == chunking
        ]

    # the same ranking for the contextual chunking and its side variant, under every pipeline
    for pipeline in ("bm25", "hybrid-rerank"):
        assert cells(pipeline, "contextual-16") == cells(pipeline, "contextual-16-prefixed")
    bm25 = BM25Texts(outcome.run_dir / "lance")
    assert bm25.text("contextual-16").startswith("kerberos context ")
    assert not bm25.text("fixed-16").startswith("kerberos context ")


class BM25Texts:
    """The texts a run's BM25 tables index."""

    def __init__(self, lance_dir: Path):
        import lancedb

        self._db = lancedb.connect(str(lance_dir))

    def text(self, table: str) -> str:
        rows = self._db.open_table(table).to_arrow().to_pylist()
        return min(rows, key=lambda r: (r["doc_id"], r["chunk_index"]))["text"]


def test_contextual_vectors_and_scores_live_under_their_own_cache_key(contextual_run):
    root, _, _, manifest = contextual_run
    suffix = key_suffix(parse_grid_config(CONTEXTUAL_GRID).chunkings[1].prefixes)
    assert manifest["contextual"]["contextual-16"]["key_suffix"] == suffix
    cache = Cache(root / "data" / "cache" / "rag-cache.sqlite")
    nomic, reranker = model_key(EMBEDDERS["nomic"]), model_key(RERANKER)
    keys = {row[0] for row in cache._db.execute("SELECT DISTINCT model FROM embeddings")}
    assert keys == {nomic, nomic + suffix}
    # the same span returns a different vector under each key
    doc_hash, start, end = cache._db.execute(
        "SELECT doc_hash, start, end FROM embeddings WHERE model = ? ORDER BY doc_hash, start LIMIT 1", (nomic,)
    ).fetchone()
    plain = cache.vectors(nomic, doc_hash)[(start, end)]
    contextual = cache.vectors(nomic + suffix, doc_hash)[(start, end)]
    assert not np.allclose(plain, contextual)
    # and a different reranker score for the same question and span
    shared = cache._db.execute(
        "SELECT a.question_hash, a.doc_hash, a.start, a.end, a.score, b.score FROM rerank_scores a "
        "JOIN rerank_scores b USING (question_hash, doc_hash, start, end) WHERE a.model = ? AND b.model = ?",
        (reranker, reranker + suffix),
    ).fetchall()
    assert shared and all(a != b for *_, a, b in shared)
    cache.close()


def test_the_side_variant_packs_and_exports_prefix_and_chunk_tokens(contextual_run):
    root, outcome, _, manifest = contextual_run
    paths = Paths(root=root)
    _, documents, _ = load_datasets(paths, parse_grid_config(CONTEXTUAL_GRID).sources)
    packed = [r for r in _rows(outcome, "packed.parquet") if r["chunking"] == "contextual-16-prefixed"]
    assert packed
    by_doc_span = {}
    for d in sorted(documents):
        for c in fixed_windows(documents[d], TokenText(documents[d].text, FakeEncoding()), 16):
            by_doc_span[(d, c.start, c.end)] = c
    for row in packed:
        chunk = by_doc_span[(row["doc_id"], row["start"], row["end"])]
        text = search_text(_prefix(row["doc_id"], chunk.index), documents[row["doc_id"]].text[chunk.start : chunk.end])
        assert row["tokens"] == len(TokenText(text, FakeEncoding())) > chunk.n_tokens
    for row in _rows(outcome, "results.parquet"):
        if row["chunking"] == "contextual-16-prefixed" and row["scored"]:
            assert row["retrieved_tokens"] <= row["budget"]
    added = manifest["contextual"]["contextual-16-prefixed"]["budget_tokens_added"]
    assert added["min"] > 0 and "budget_tokens_added" not in manifest["contextual"]["contextual-16"]
    # at a budget that holds fewer prefixed chunks, the side variant packs fewer chunks
    counts = {
        name: sum(
            r["n_chunks"]
            for r in _rows(outcome, "results.parquet")
            if r["chunking"] == name and r["view"] == "fair" and r["budget"] == 64 and r["pipeline"] == "bm25"
        )
        for name in ("contextual-16", "contextual-16-prefixed")
    }
    assert counts["contextual-16-prefixed"] < counts["contextual-16"]


def test_a_cached_rerun_embeds_and_reranks_nothing_and_rewrites_identical_tables(contextual_run):
    root, outcome, _, _ = contextual_run
    again, models, manifest = _run(root)
    assert manifest["embeddings"]["chunk_vectors_embedded"] == 0
    assert manifest["reranker"]["pairs_scored"] == 0 and models.reranker_model.pairs == []
    assert {p.name: p.read_bytes() for p in again.tables} == {p.name: p.read_bytes() for p in outcome.tables}


@pytest.mark.parametrize(("hole", "message"), [("skip", "1 of"), ("blank", "1 of")])
def test_the_run_fails_when_a_chunk_has_no_prefix(tmp_path, hole, message):
    build_env(tmp_path)
    write_store(tmp_path, **{hole: ("paperA", 1)})
    with pytest.raises(ValueError, match=rf"contextual-16: {message} .* no prefix .*paperA characters"):
        _run(tmp_path)


def test_the_run_fails_without_a_prefix_store_or_with_another_prefix_set(tmp_path):
    build_env(tmp_path)
    with pytest.raises(ValueError, match="no prefix store"):
        _run(tmp_path)
    write_store(tmp_path)
    other = {
        **CONTEXTUAL_GRID,
        "chunkings": [{**CONTEXTUAL_GRID["chunkings"][1], "prefixes": {**PREFIX_SET, "prompt_sha256": "2" * 64}}],
    }
    with pytest.raises(ValueError, match="have no prefix in the prefix set"):
        run_grid(parse_grid_config(other), Paths(root=tmp_path), encoding=FakeEncoding(), models=FakeModels())


# --- the reader text --------------------------------------------------------------


def test_the_side_variants_reader_receives_prefix_and_chunk(contextual_run, fake_encoding):
    root, outcome, _, _ = contextual_run
    paths = Paths(root=root)
    splits, documents, _ = load_datasets(paths, parse_grid_config(CONTEXTUAL_GRID).sources)
    # the answers stage reads a run per dataset: stand the QASPER run in for NQ too
    shutil.copytree(outcome.run_dir, paths.run_dir("v2-contextual", "nq"))
    setups = [
        {"name": name, "runs": {"qasper": "v2-contextual", "nq": "v2-contextual"}, "chunking": chunking}
        for name, chunking in (
            ("section-aware", "fixed-16"),
            ("contextual-256", "contextual-16"),
            ("contextual-256-prefixed", "contextual-16-prefixed"),
        )
    ]
    cfg = parse_answers_config(
        {
            "kind": "answers",
            "run_name": "test-answers",
            "dataset": {
                "name": "pooled",
                "sources": [{"name": "qasper", "splits": ["dev"]}, {"name": "nq", "splits": ["dev"]}],
            },
            "sample": "configs/v2/reader-sample.txt",
            "budget": 64,
            "top_n": 3,
            "embedder": "nomic",
            "oracle_chunkings": ["fixed-16", "section-aware"],
            "setups": setups,
            "resamples": 10,
            "seed": 0,
            "confidence": 0.95,
        }
    )
    questions = [q for split in splits for q in split.questions]
    sample = Sample(seed=0, per_dataset={"qasper": tuple(SampledQuestion(q, "qasper") for q in questions)})
    plain, prefixed = (render_setup_prompts(cfg, s, sample, documents, paths, fake_encoding) for s in cfg.setups[1:])
    assert not any("kerberos context " in p.prompt for p in plain)
    assert any("kerberos context " in p.prompt for p in prefixed)
    assert all(p.within_budget and p.context_tokens <= 64 for p in prefixed)
    run_dir = outcome.run_dir
    spans = load_packed(run_dir, "hybrid-rerank", "nomic", "contextual-16", "budget", 64, "collection")
    assert reader_prefixes(run_dir, "contextual-16", spans, documents, paths) is None
    assert reader_prefixes(run_dir, "fixed-16", spans, documents, paths) is None


# --- R13 --------------------------------------------------------------------------

R13_CONFIG = {
    "kind": "contenders",
    "table": "r13",
    "title": "contextual chunks",
    "runs": ["qasper/v2-contextual", "nq/v2-contextual"],
    "chunkings": ["fixed-256", "contextual-256", "contextual-256-prefixed"],
    "pairs": [["contextual-256", "fixed-256"], ["contextual-256-prefixed", "contextual-256"]],
    "run_name": "v2-contextual",
    "notes": ["The side variant counts its prefix."],
}


def test_r13_reports_each_dataset_and_the_pooled_questions_byte_identically(tmp_path):
    recalls = {"fixed-256": [0.2, 0.4], "contextual-256": [0.3, 0.5], "contextual-256-prefixed": [0.1, 0.3]}
    _write_run(tmp_path, "qasper", recalls, run_name="v2-contextual")
    _write_run(tmp_path, "nq", {name: [0.6] for name in recalls}, run_name="v2-contextual")
    cfg = parse_contenders_config(R13_CONFIG)
    paths = run_contenders(cfg, Paths(root=tmp_path))
    assert [p.relative_to(tmp_path).as_posix() for p in paths] == [
        "results/qasper/r13-v2-contextual.md",
        "results/nq/r13-v2-contextual.md",
    ]
    qasper = paths[0].read_text(encoding="utf-8")
    assert qasper.startswith("# R13 - qasper v2-contextual: contextual chunks")
    differences = table_rows(qasper, "## Contender minus reference")
    assert ["contextual-256 - fixed-256", "budget", "256", "+0.1000", "+0.0500", "+0.0667", "+0.0333"] in differences
    assert [
        "contextual-256-prefixed - contextual-256",
        "production",
        "256",
        "-0.2000",
        "-0.1000",
        "-0.1333",
        "-0.0667",
    ] in differences
    assert qasper.endswith("at that budget.\n\nThe side variant counts its prefix.\n")
    first = {p: p.read_bytes() for p in paths}
    run_contenders(cfg, Paths(root=tmp_path))
    assert {p: p.read_bytes() for p in paths} == first
    # a config without notes keeps its canonical JSON
    plain = {k: v for k, v in R13_CONFIG.items() if k != "notes"}
    assert "notes" not in parse_contenders_config(plain).as_dict()
