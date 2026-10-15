"""Late chunking on a fake token-embedding model: character-span-to-token
mapping (multi-byte text, a token straddling a chunk boundary, a shared
multi-byte character), pooling, windows that never exceed the limit and
hold every chunk exactly once, the config option, a grid run whose late
vectors live under their own cache key and a re-run that embeds nothing,
and R12 rendered per dataset and pooled."""

from __future__ import annotations

import json
import re
import zlib
from collections.abc import Sequence
from itertools import pairwise
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.cache import Cache
from rag.config import config_hash, load_any_config, parse_grid_config
from rag.contenders import load_contenders_config, parse_contenders_config, run_contenders
from rag.grid import run_grid
from rag.late import (
    LATE_KEY_SUFFIX,
    TokenEmbeddings,
    Window,
    WindowStats,
    assign_tokens,
    block_spans,
    late_vectors,
    plan_windows,
    pool_window,
)
from rag.models import EMBEDDERS
from rag.paths import Paths
from rag.pipelines import model_key
from rag.tokens import TokenText
from tests.conftest import FakeEncoding
from tests.test_grid import build_env, table_rows
from tests.test_production import PRODUCTION, FakeEmbedder, FakeModels

PREFIX_TOKENS = 3  # the fake model's prefix
SPECIAL_TOKENS = 2  # [CLS] and [SEP]


class FakeTokenModel:
    """Whitespace-separated words are tokens; each token's vector is its own
    hashed direction plus the mean of the window, so a late vector depends
    on its surroundings. Records every text it embeds."""

    def __init__(self, dim: int = 16):
        self.dim = dim
        self.calls: list[str] = []

    def input_tokens(self, texts: Sequence[str]) -> list[int]:
        return [PREFIX_TOKENS + SPECIAL_TOKENS + len(re.findall(r"\S+", t)) for t in texts]

    def _own(self, word: str) -> np.ndarray:
        out = np.zeros(self.dim, dtype=np.float32)
        out[zlib.crc32(word.encode()) % self.dim] = 1.0
        return out

    def token_embeddings(self, text: str) -> TokenEmbeddings:
        self.calls.append(text)
        words = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
        own = np.stack([self._own(text[s:e]) for s, e in words]) if words else np.zeros((0, self.dim))
        context = own.mean(axis=0) if words else np.zeros(self.dim)
        prefix = np.stack([self._own(f"prefix{i}") for i in range(PREFIX_TOKENS)])
        special = np.stack([self._own("cls"), self._own("sep")])
        vectors = np.concatenate([special[:1], prefix, own + 0.5 * context, special[1:]]).astype(np.float32)
        offsets = [None] * (1 + PREFIX_TOKENS) + words + [None]
        return TokenEmbeddings(offsets, vectors)


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


# --- character spans to tokens ---------------------------------------------


def test_tokens_join_the_chunk_their_first_character_starts_in_on_multibyte_text():
    text = "naïve café 東京 über straße"
    chunks = [(0, 11), (11, 19), (19, len(text))]  # "naïve café ", "東京 über ", "straße"
    model = FakeTokenModel()
    embedded = model.token_embeddings(text)
    words = [text[s:e] for s, e in (o for o in embedded.offsets if o is not None)]
    assert words == ["naïve", "café", "東京", "über", "straße"]  # offsets are characters, not bytes
    assignment = assign_tokens(embedded.offsets, chunks)
    assert assignment == [None] * 4 + [0, 0, 1, 1, 2] + [None]  # prefix and special tokens join no chunk


def test_a_token_straddling_a_chunk_boundary_joins_only_the_chunk_it_starts_in():
    text = "alpha bravocharlie delta"
    boundary = text.index("charlie")  # a chunk boundary inside the token "bravocharlie"
    offsets = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    assert assign_tokens(offsets, [(0, boundary), (boundary, len(text))]) == [0, 0, 1]
    assert assign_tokens(offsets, [(0, 5)]) == [0, None, None]  # past every chunk: no chunk
    # the chunk after the boundary holds the straddling token's tail and "delta"
    vectors = np.eye(3, dtype=np.float32)
    pooled = pool_window(TokenEmbeddings(offsets, vectors), [(0, boundary), (boundary, len(text))])
    assert np.allclose(pooled[0], _unit(vectors[0] + vectors[1]))
    assert np.allclose(pooled[1], vectors[2])


def test_a_shared_multibyte_character_sends_the_token_starting_there_to_the_later_chunk():
    # adjacent chunks share one character when a token boundary splits it
    chunks = [(0, 3), (2, 5)]  # "ab€" and "€cd" both hold "€"
    assert assign_tokens([(0, 2), (2, 5)], chunks) == [0, 1]


def test_a_chunk_in_which_no_token_starts_is_pooled_from_the_tokens_overlapping_it():
    offsets = [(0, 8), (9, 13)]  # "longword next"
    vectors = np.eye(2, dtype=np.float32)
    stats = WindowStats()
    pooled = pool_window(TokenEmbeddings(offsets, vectors), [(0, 4), (4, 9), (9, 13)], stats)
    assert np.allclose(pooled[1], vectors[0])  # only the tail of "longword"
    assert stats.chunks_pooled_from_overlapping_tokens == 1
    with pytest.raises(ValueError, match="no token covers"):
        pool_window(TokenEmbeddings([(0, 8)], vectors[:1]), [(0, 8), (8, 9)])


# --- windows ----------------------------------------------------------------


def _blocks(text: str, words_per_block: int) -> list[tuple[int, int]]:
    starts = [m.start() for m in re.finditer(r"\S+", text)][::words_per_block]
    return [(s, e) for s, e in zip(starts, [*starts[1:], len(text)], strict=True)]


def test_windows_hold_whole_blocks_in_order_and_never_exceed_the_limit():
    text = " ".join(f"w{i}" for i in range(100)) + " "
    blocks = _blocks(text, 4)
    model = FakeTokenModel()
    windows = plan_windows(text, blocks, model.input_tokens, limit=30)
    assert windows[0].start == 0 and windows[-1].end == len(text)
    assert all(a.end == b.start for a, b in pairwise(windows))
    assert {w.start for w in windows} <= {s for s, _ in blocks}
    for i, window in enumerate(windows):
        assert window.tokens == model.input_tokens([text[window.start : window.end]])[0] <= 30
        if i + 1 < len(windows):  # as many blocks as fit: one more would exceed the limit
            nxt = next(e for s, e in blocks if s == window.end)
            assert model.input_tokens([text[window.start : nxt]])[0] > 30
    assert len(windows) == 5  # 5 overhead + 24 words per window: 6 blocks of 4 words


def test_windows_are_counted_exactly_when_tokens_merge_at_block_edges():
    # a block edge inside a word: the blocks count two tokens, the window one
    text = "aaaa bbbbcccc dddd eeee ffff gggg"
    edge = text.index("cccc")
    blocks = [(0, edge), (edge, text.index("eeee")), (text.index("eeee"), len(text))]
    model = FakeTokenModel()
    assert sum(model.input_tokens([text[s:e]])[0] - 5 for s, e in blocks) == 7
    windows = plan_windows(text, blocks, model.input_tokens, limit=5 + 6)
    assert [(w.start, w.end, w.tokens) for w in windows] == [(0, len(text), 11)]


def test_a_block_that_cannot_fit_one_window_is_an_error():
    with pytest.raises(ValueError, match="single"):
        plan_windows("a b c d e f", [(0, 11)], FakeTokenModel().input_tokens, limit=8)


def test_block_spans_cut_the_text_every_size_tokens(fake_encoding):
    tokens = TokenText("abcdefghij", fake_encoding)
    assert block_spans(tokens, 4) == [(0, 4), (4, 8), (8, 10)]


# --- late vectors -------------------------------------------------------------


def test_every_chunk_is_pooled_from_exactly_one_window_with_one_pass_per_window():
    text = " ".join(f"w{i}" for i in range(40)) + " "
    small, large = _blocks(text, 2), _blocks(text, 4)
    windows = plan_windows(text, large, FakeTokenModel().input_tokens, limit=17)  # 12 words per window
    assert len(windows) == 4
    model = FakeTokenModel()
    vectors = late_vectors(text, [small, large], windows, model)
    assert len(model.calls) == len(windows)  # one pass serves both chunkings
    assert [len(v) for v in vectors] == [len(small), len(large)]
    # pooled within its own window only: the same as embedding that window alone
    for spans, chunk_vectors in zip((small, large), vectors, strict=True):
        for (s, e), vector in zip(spans, chunk_vectors, strict=True):
            window = next(w for w in windows if w.start <= s and e <= w.end)
            alone = model.token_embeddings(text[window.start : window.end])
            expected = pool_window(alone, [(s - window.start, e - window.start)])[0]
            assert np.allclose(vector, expected)


def test_a_chunk_crossing_a_window_edge_is_an_error():
    text = "a b c d"
    windows = [Window(0, 4, 7), Window(4, 7, 7)]
    with pytest.raises(ValueError, match="exactly one"):
        late_vectors(text, [[(0, 6)]], windows, FakeTokenModel())


def test_a_window_holding_a_single_chunk_pooled_over_all_its_tokens_is_the_independent_vector():
    # the mechanism the real-model check relies on: the mean of every token
    # the model read is the independent vector; the pooling rule leaves the
    # prefix and special tokens out
    text = "kerberos tickets carry session keys"
    model = FakeTokenModel()
    embedded = model.token_embeddings(text)
    independent = _unit(embedded.vectors.mean(axis=0))
    rule = pool_window(embedded, [(0, len(text))])[0]
    own = [i for i, o in enumerate(embedded.offsets) if o is not None]
    assert np.allclose(rule, _unit(embedded.vectors[own].mean(axis=0)))
    assert not np.allclose(rule, independent)


# --- config ---------------------------------------------------------------------

LATE_GRID = {
    **PRODUCTION,
    "pipelines": ["hybrid-rerank", "bm25"],
    "embedders": ["nomic"],
    "chunkings": [
        {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        {"name": "fixed-32", "method": "fixed", "chunk_tokens": 32},
        {"name": "late-16", "method": "fixed", "chunk_tokens": 16, "embedding": "late"},
        {"name": "late-32", "method": "fixed", "chunk_tokens": 32, "embedding": "late"},
    ],
    "budget_top_n": 3,
}


def test_the_embedding_option_enters_only_a_late_chunkings_canonical_json():
    cfg = parse_grid_config(LATE_GRID)
    assert [c.late for c in cfg.chunkings] == [False, False, True, True]
    rendered = [c.as_dict() for c in cfg.chunkings]
    assert "embedding" not in rendered[0] and rendered[2]["embedding"] == "late"
    explicit = {**LATE_GRID, "chunkings": [{**LATE_GRID["chunkings"][0], "embedding": "chunk"}]}
    implicit = {**LATE_GRID, "chunkings": LATE_GRID["chunkings"][:1]}
    assert config_hash(parse_grid_config(explicit)) == config_hash(parse_grid_config(implicit))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"chunkings": [{"name": "s", "method": "section_aware", "max_tokens": 64, "embedding": "late"}]}, "fixed"),
        ({"chunkings": [{"name": "x", "method": "fixed", "chunk_tokens": 16, "embedding": "both"}]}, "embedding"),
        ({"embedders": ["bge-small"]}, "8192"),
        ({"chunkings": [{"name": "late-512", "method": "fixed", "chunk_tokens": 512, "embedding": "late"}]}, "divide"),
        ({"pipelines": ["bm25"], "embedders": []}, "embedder"),
    ],
)
def test_late_chunking_config_errors(change, message):
    raw = {**LATE_GRID, **change}
    if raw["pipelines"] == ["bm25"]:
        raw = {k: v for k, v in raw.items() if k not in ("pipelines", "embedders", "rrf_k", "rerank_depth")}
        raw["pipeline"] = "bm25"
    with pytest.raises(ValueError, match=message):
        parse_grid_config(raw)


def test_the_v2_late_configs_parse_and_the_baselines_keep_their_hashes():
    for dataset in ("qasper", "nq"):
        cfg = load_any_config(Path(f"configs/v2/{dataset}-late.yaml"))
        assert [c.name for c in cfg.chunkings if c.late] == ["late-128", "late-256"]
        assert cfg.embedders == ("nomic",) and cfg.budget_top_n == 20 and cfg.run_name == "v2-late"
        baseline = load_any_config(Path(f"configs/v2/{dataset}-baseline.yaml"))
        table = Path(f"results/{dataset}/r2-v2-baseline.md").read_text(encoding="utf-8")
        assert f"Config hash: `{config_hash(baseline)}`" in table
    r12 = load_contenders_config(Path("configs/v2/late.yaml"))
    assert r12.runs == ("qasper/v2-late", "nq/v2-late") and r12.table == "r12"


def test_nomic_loads_with_rotary_scaling_for_late_windows():
    assert dict(EMBEDDERS["nomic"].model_kwargs) == {"rotary_scaling_factor": 2}
    assert EMBEDDERS["bge-small"].model_kwargs == ()


# --- a grid run -------------------------------------------------------------------


class FakeLateEmbedder(FakeEmbedder):
    """The production tests' fake embedder, plus token embeddings."""

    def __init__(self, spec):
        super().__init__(spec, tokens_per_byte=1)
        self.token_model = FakeTokenModel(dim=32)

    def token_embeddings(self, text: str) -> TokenEmbeddings:
        return self.token_model.token_embeddings(text)


class FakeLateModels(FakeModels):
    def __init__(self):
        super().__init__()
        self.embedders["nomic"] = FakeLateEmbedder(EMBEDDERS["nomic"])


def _late_run(root: Path, monkeypatch, window: int = 300):
    # small windows, so the synthetic papers need several: 256-byte blocks
    monkeypatch.setattr("rag.pipelines.LATE_WINDOW", window)
    models = FakeLateModels()
    outcome = run_grid(parse_grid_config(LATE_GRID), Paths(root=root), encoding=FakeEncoding(), models=models)
    return outcome, models, json.loads((outcome.run_dir / "manifest.json").read_text(encoding="utf-8"))


def test_a_late_run_caches_its_vectors_apart_and_a_rerun_embeds_nothing(tmp_path, monkeypatch):
    build_env(tmp_path)
    outcome, models, manifest = _late_run(tmp_path, monkeypatch)
    windows = manifest["late_windows"]["nomic"]
    calls = models.embedders["nomic"].token_model.calls
    assert windows["windows"] == manifest["embeddings"]["late_windows_embedded"] == len(calls)
    assert windows["documents"] == 2 and windows["documents_over_one_window"] >= 1
    assert 0 < windows["longest_window_tokens"] <= 300
    assert manifest["truncated_share"]["late-16"] == {"nomic": 0.0}

    key = model_key(EMBEDDERS["nomic"])
    cache = Cache(tmp_path / "data" / "cache" / "rag-cache.sqlite")
    keys = {row[0] for row in cache._db.execute("SELECT DISTINCT model FROM embeddings")}
    late_rows = cache._db.execute("SELECT COUNT(*) FROM embeddings WHERE model = ?", (key + LATE_KEY_SUFFIX,))
    chunk_rows = cache._db.execute("SELECT COUNT(*) FROM embeddings WHERE model = ?", (key,)).fetchone()[0]
    assert keys == {key, key + LATE_KEY_SUFFIX}
    # late-16 and late-32 have fixed-16's and fixed-32's spans: the same number of rows under each key
    assert late_rows.fetchone()[0] == chunk_rows > 0
    cache.close()

    again, models, manifest = _late_run(tmp_path, monkeypatch)
    assert models.embedders["nomic"].token_model.calls == []
    assert manifest["embeddings"]["chunk_vectors_embedded"] == 0
    assert "late_windows_embedded" not in manifest["embeddings"]
    assert manifest["late_windows"]["nomic"] == windows  # planned the same, from the document alone
    assert {p.name: p.read_bytes() for p in again.tables} == {p.name: p.read_bytes() for p in outcome.tables}


def test_late_and_fixed_chunkings_share_bm25_scoring_and_differ_in_vectors(tmp_path, monkeypatch):
    build_env(tmp_path)
    outcome, _, _ = _late_run(tmp_path, monkeypatch)
    rows = pq.read_table(outcome.run_dir / "results.parquet").to_pylist()

    def cells(pipeline: str, chunking: str) -> list:
        return [
            (r["question_id"], r["view"], r["top_n"], r["budget"], r["recall"], r["precision"])
            for r in rows
            if r["pipeline"] == pipeline and r["chunking"] == chunking
        ]

    assert cells("bm25", "late-16") == cells("bm25", "fixed-16")  # same spans, same BM25 index
    assert cells("hybrid-rerank", "late-16") and cells("hybrid-rerank", "late-32")


# --- R12 --------------------------------------------------------------------------

RESULT_COLUMNS = ["pipeline", "embedder", "scope", "chunking", "view", "top_n", "budget", "scored", "recall"]


def _write_run(root: Path, dataset: str, recalls: dict[str, list[float]], run_name: str = "v2-late") -> None:
    """A two-budget run: `recalls[chunking]` per question, the same at both
    budgets and in both views; fixed-256 is not scored at budget 128."""
    run_dir = root / "runs" / dataset / run_name
    run_dir.mkdir(parents=True)
    rows: dict[str, list] = {name: [] for name in [*RESULT_COLUMNS, "precision"]}
    for chunking, values in recalls.items():
        for view, top_n in (("budget", 20), ("production", 8), ("production", 5), ("fair", None)):
            for budget in (128, 256):
                for value in values:
                    scored = not (chunking.endswith("256") and budget == 128)
                    row = ["hybrid-rerank", "nomic", "collection", chunking, view, top_n, budget, scored]
                    row += [value if scored else None, value / 2 if scored else None]
                    for name, cell in zip(rows, row, strict=True):
                        rows[name].append(cell)
    pq.write_table(pa.table(rows), run_dir / "results.parquet")
    manifest = {
        "config": {"dataset": {"name": dataset}, "budgets": [128, 256], "budget_top_n": 20, "top_n": 8},
        "config_hash": f"hash-{dataset}",
        "datasets": {"dev": f"sha-{dataset}"},
        "counts": {"questions": len(next(iter(recalls.values())))},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


R12_CONFIG = {
    "kind": "contenders",
    "table": "r12",
    "title": "late chunking",
    "runs": ["qasper/v2-late", "nq/v2-late"],
    "chunkings": ["fixed-128", "late-128", "fixed-256", "late-256"],
    "pairs": [["late-128", "fixed-128"], ["late-256", "fixed-256"]],
    "run_name": "v2-late",
}


def test_r12_reports_each_dataset_and_the_pooled_questions_byte_identically(tmp_path):
    _write_run(tmp_path, "qasper", {"fixed-128": [0.2, 0.4], "late-128": [0.3, 0.5], "fixed-256": [0.1, 0.1],
                                    "late-256": [0.2, 0.2]})  # fmt: skip
    _write_run(tmp_path, "nq", {"fixed-128": [0.8], "late-128": [0.5], "fixed-256": [0.6], "late-256": [0.9]})
    cfg = parse_contenders_config(R12_CONFIG)
    paths = run_contenders(cfg, Paths(root=tmp_path))
    assert [p.relative_to(tmp_path).as_posix() for p in paths] == ["results/qasper/r12-v2-late.md",
                                                                   "results/nq/r12-v2-late.md"]  # fmt: skip
    qasper = paths[0].read_text(encoding="utf-8")
    assert qasper.startswith("# R12 - qasper v2-late: late chunking")
    assert table_rows(qasper, "## Budget view (top-N cap 20)")[:2] == [
        ["fixed-128", "128", "0.3000", "0.1500", "0.4667", "0.2333"],  # pooled: (0.2 + 0.4 + 0.8) / 3
        ["fixed-128", "256", "0.3000", "0.1500", "0.4667", "0.2333"],
    ]
    assert ["fixed-256", "128", "n/a", "n/a", "n/a", "n/a"] in table_rows(qasper, "## Production view (top-N cap 8)")
    differences = table_rows(qasper, "## Contender minus reference")
    assert ["late-128 - fixed-128", "budget", "128", "+0.1000", "+0.0500", "-0.0333", "-0.0167"] in differences
    assert ["late-256 - fixed-256", "production", "256", "+0.1000", "+0.0500", "+0.1667", "+0.0833"] in differences
    first = {p: p.read_bytes() for p in paths}
    run_contenders(cfg, Paths(root=tmp_path))
    assert {p: p.read_bytes() for p in paths} == first


def test_r12_needs_known_pairs_and_one_run_per_dataset(tmp_path):
    with pytest.raises(ValueError, match="pair"):
        parse_contenders_config({**R12_CONFIG, "pairs": [["late-512", "fixed-128"]]})
    recalls = {c: [0.1] for c in R12_CONFIG["chunkings"]}
    _write_run(tmp_path, "qasper", recalls)
    _write_run(tmp_path, "qasper", recalls, run_name="v2-late-again")
    cfg = parse_contenders_config({**R12_CONFIG, "runs": ["qasper/v2-late", "qasper/v2-late-again"]})
    with pytest.raises(ValueError, match="different dataset"):
        run_contenders(cfg, Paths(root=tmp_path))
