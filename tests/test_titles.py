"""Section-aware chunks indexed with their document and section titles on
a synthetic corpus with fake models: the config keys, the headers built
from the dataset's own title and section fields only, the search texts
(BM25, vectors, reranker), cache keys apart from the plain chunks',
packing and scoring on the chunk's own span, the plain chunking
reproduced exactly from the cache, a cached re-run, and R17 with its
pre-registered bar verdict."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.cache import Cache
from rag.config import config_hash, load_any_config, parse_grid_config
from rag.contenders import load_contenders_config, parse_contenders_config, run_contenders
from rag.contextual import SEPARATOR
from rag.documents import Document, build_document
from rag.grid import run_grid
from rag.metrics import score_question
from rag.models import EMBEDDERS, RERANKER
from rag.paths import Paths
from rag.pipelines import model_key
from rag.run import gold_token_sets, load_datasets
from rag.titles import KEY_SUFFIX, chunk_headers, chunk_section, header, key_suffix
from rag.tokens import TokenText
from tests.conftest import FakeEncoding
from tests.test_grid import build_env, table_rows
from tests.test_production import PRODUCTION, FakeModels

TITLES_GRID = {
    **PRODUCTION,
    "pipelines": ["hybrid-rerank", "bm25"],
    "embedders": ["nomic"],
    "chunkings": [
        {"name": "section-aware", "method": "section_aware", "max_tokens": 128},
        {"name": "section-aware-titles", "method": "section_aware", "max_tokens": 128, "titles": True},
    ],
    "budget_top_n": 3,
    "run_name": "v2-titles",
    "export_packed": [{"view": "budget", "budget": 64, "scope": "collection"}],
}
PLAIN_GRID = {**TITLES_GRID, "chunkings": TITLES_GRID["chunkings"][:1], "run_name": "v2-plain"}


def _run(root: Path, grid=TITLES_GRID):
    models = FakeModels()
    outcome = run_grid(parse_grid_config(grid), Paths(root=root), encoding=FakeEncoding(), models=models)
    return outcome, models, json.loads((outcome.run_dir / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def titles_run(tmp_path):
    build_env(tmp_path)
    outcome, models, manifest = _run(tmp_path)
    return tmp_path, outcome, models, manifest


def _rows(outcome, name: str) -> list[dict]:
    return pq.read_table(outcome.run_dir / name).to_pylist()


# --- config ---------------------------------------------------------------------


def test_the_titles_key_enters_only_a_titled_chunkings_canonical_json():
    cfg = parse_grid_config(TITLES_GRID)
    assert [c.titled for c in cfg.chunkings] == [False, True]
    rendered = [c.as_dict() for c in cfg.chunkings]
    assert "titles" not in rendered[0]
    assert rendered[1]["titles"] is True
    explicit = {**TITLES_GRID, "chunkings": [{**TITLES_GRID["chunkings"][1], "titles": False}]}
    implicit = {
        **TITLES_GRID,
        "chunkings": [{k: v for k, v in TITLES_GRID["chunkings"][1].items() if k != "titles"}],
    }
    assert config_hash(parse_grid_config(explicit)) == config_hash(parse_grid_config(implicit))
    assert key_suffix() == KEY_SUFFIX == "#titles"


@pytest.mark.parametrize(
    ("chunking", "message"),
    [
        ({"name": "x", "method": "fixed", "chunk_tokens": 16, "titles": True}, "titled chunks need section-aware"),
        ({"name": "x", "method": "section_aware", "max_tokens": 64, "titles": "yes"}, "true or false"),
    ],
)
def test_titled_chunking_config_errors(chunking, message):
    with pytest.raises(ValueError, match=message):
        parse_grid_config({**TITLES_GRID, "chunkings": [chunking]})


def test_titles_needs_section_aware_chunking():
    with pytest.raises(ValueError, match="titled chunks need section-aware"):
        parse_grid_config(
            {**TITLES_GRID, "chunkings": [{"name": "x", "method": "fixed", "chunk_tokens": 16, "titles": True}]}
        )



def test_titled_chunks_take_no_prefixes_late_embedding_or_prefix_in_budget():
    prefix_set = {"model": "m", "revision": "0" * 40, "prompt_sha256": "1" * 64}
    for extra in ({"prefixes": prefix_set}, {"embedding": "late"}, {"prefix_in_budget": True}):
        chunking = {"name": "x", "method": "section_aware", "max_tokens": 64, "titles": True, **extra}
        with pytest.raises(ValueError, match="titled chunks have no prefixes"):
            parse_grid_config({**TITLES_GRID, "chunkings": [chunking]})


def test_the_v2_titles_configs_name_both_chunkings_and_r17():
    for dataset in ("qasper", "nq"):
        cfg = load_any_config(Path(f"configs/v2/{dataset}-titles.yaml"))
        assert [c.name for c in cfg.chunkings] == ["section-aware", "section-aware-titles"]
        assert [c.titled for c in cfg.chunkings] == [False, True]
        assert all(c.method == "section_aware" and c.max_tokens == 512 for c in cfg.chunkings)
        assert cfg.embedders == ("nomic",) and cfg.budget_top_n == 20 and cfg.run_name == "v2-titles"
        assert cfg.pipelines == ("hybrid-rerank",) and cfg.scopes == ("collection",)
        assert cfg.budgets == (128, 256, 512, 1024, 2048, 4096, 8192)
    r17 = load_contenders_config(Path("configs/v2/titles.yaml"))
    assert r17.runs == ("qasper/v2-titles", "nq/v2-titles") and r17.table == "r17"
    assert r17.pairs == (("section-aware-titles", "section-aware"),)
    assert (r17.gate.view, r17.gate.budget, r17.gate.min_gain, r17.gate.max_loss) == ("budget", 1024, 0.02, 0.01)


# --- the header -----------------------------------------------------------------


def _paper() -> Document:
    return build_document(
        "p",
        "Abstract sentence about tickets.",
        [("Intro", ["First paragraph.", "Second paragraph."]), ("Results", ["Numbers here."])],
        title="A Study of Tickets",
    )


def test_a_qasper_chunk_headers_with_the_paper_title_and_the_section_name():
    doc = _paper()
    from rag.chunking import section_aware

    tokens = TokenText(doc.text, FakeEncoding())
    chunks = section_aware(doc, tokens, 8)
    by_section = {chunk_section(doc, c): c for c in chunks}
    assert header(doc, by_section["Abstract"]).startswith("Paper: A Study of Tickets. Section: Abstract.")
    assert header(doc, by_section["Intro"]) == "Paper: A Study of Tickets. Section: Intro."
    assert header(doc, by_section["Results"]) == "Paper: A Study of Tickets. Section: Results."


def test_a_section_split_across_chunks_keeps_one_section_name():
    doc = _paper()  # two Intro paragraphs, capped at 8 tokens a chunk
    from rag.chunking import section_aware

    chunks = section_aware(doc, TokenText(doc.text, FakeEncoding()), 8)
    intro = [c for c in chunks if chunk_section(doc, c) == "Intro"]
    assert len(intro) > 1  # the section is split across chunks
    assert {chunk_section(doc, c) for c in chunks} <= {"Abstract", "Intro", "Results"}


def test_a_page_chunk_headers_with_the_page_title_only_because_its_heading_is_in_the_text():
    page = build_document(
        "n",
        "",
        [("Senate membership", ["Senate membership", "The Senate has members."])],
        title="United States Senate",
        headings_in_text=True,
    )
    from rag.chunking import section_aware

    chunks = section_aware(page, TokenText(page.text, FakeEncoding()), 8)
    assert page.text.startswith("Senate membership")  # the heading the chunks open with
    assert all(header(page, c) == "Page: United States Senate." for c in chunks)


def test_empty_title_and_section_parts_are_skipped():
    untitled = build_document("u", "One abstract sentence.", [("Intro", ["Body."])], title="")
    unnamed = build_document("v", "", [("", ["Body."])], title="Titled")
    from rag.chunking import section_aware

    for doc, expected in ((untitled, "Section: Abstract."), (unnamed, "Paper: Titled.")):
        chunk = section_aware(doc, TokenText(doc.text, FakeEncoding()), 8)[0]
        assert header(doc, chunk) == expected
    neither = build_document("w", "", [("", ["Body."])])
    chunk = section_aware(neither, TokenText(neither.text, FakeEncoding()), 8)[0]
    assert header(neither, chunk) == ""


def test_chunk_headers_keys_every_chunk_by_document_hash_and_span():
    doc = _paper()
    from rag.chunking import section_aware

    chunks = section_aware(doc, TokenText(doc.text, FakeEncoding()), 8)
    headers = chunk_headers({"p": doc}, chunks)
    assert set(headers) == {(doc.source_hash, c.start, c.end) for c in chunks}
    assert headers[(doc.source_hash, chunks[0].start, chunks[0].end)] == header(doc, chunks[0])


# --- a grid run -------------------------------------------------------------------


def test_the_manifest_records_the_titled_chunking_and_its_headers(titles_run):
    _root, _outcome, _models, manifest = titles_run
    entry = manifest["contextual"]["section-aware-titles"]
    assert set(entry) == {"titles", "key_suffix", "headers", "headers_empty"}
    assert entry["titles"] is True and entry["key_suffix"] == "#titles" and entry["headers_empty"] == 0
    assert entry["headers"] == manifest["counts"]["chunks"]["section-aware"]


def test_search_reads_the_header_and_the_plain_chunks_their_own_text(titles_run):
    _root, outcome, models, _ = titles_run
    texts = [p for _, p in models.reranker_model.pairs]
    assert any(t.startswith("Paper: Paper paperA. Section: ") and SEPARATOR in t for t in texts)  # (question, search text)
    assert any(not t.startswith("Paper: ") for t in texts)  # the plain chunking's pairs

    class BM25Texts:
        def __init__(self, lance_dir: Path):
            import lancedb

            self._db = lancedb.connect(str(lance_dir))

        def text(self, table: str) -> str:
            rows = self._db.open_table(table).to_arrow().to_pylist()
            return min(rows, key=lambda r: (r["doc_id"], r["chunk_index"]))["text"]

    bm25 = BM25Texts(outcome.run_dir / "lance")
    headed = bm25.text("section-aware-titles")
    plain = bm25.text("section-aware")
    assert headed.startswith("Paper: Paper paperA.")
    assert headed.endswith(plain)  # the header in front of the same chunk text


def test_titled_vectors_and_scores_live_under_their_own_cache_key(titles_run):
    root, _outcome, _models, manifest = titles_run
    assert manifest["contextual"]["section-aware-titles"]["key_suffix"] == "#titles"
    cache = Cache(root / "data" / "cache" / "rag-cache.sqlite")
    nomic, reranker = model_key(EMBEDDERS["nomic"]), model_key(RERANKER)
    keys = {row[0] for row in cache._db.execute("SELECT DISTINCT model FROM embeddings")}
    assert keys == {nomic, nomic + "#titles"}
    # the same span returns a different vector under each key
    doc_hash, start, end = cache._db.execute(
        "SELECT doc_hash, start, end FROM embeddings WHERE model = ? ORDER BY doc_hash, start LIMIT 1", (nomic,)
    ).fetchone()
    plain = cache.vectors(nomic, doc_hash)[(start, end)]
    headed = cache.vectors(nomic + "#titles", doc_hash)[(start, end)]
    assert not np.allclose(plain, headed)
    # and a different reranker score for the same question and span
    shared = cache._db.execute(
        "SELECT a.question_hash, a.doc_hash, a.start, a.end, a.score, b.score FROM rerank_scores a "
        "JOIN rerank_scores b USING (question_hash, doc_hash, start, end) WHERE a.model = ? AND b.model = ?",
        (reranker, reranker + "#titles"),
    ).fetchall()
    assert shared and all(a != b for *_, a, b in shared)
    cache.close()


def test_packed_titled_chunks_carry_chunk_tokens_and_are_scored_on_their_spans(titles_run):
    root, outcome, _, _ = titles_run
    paths = Paths(root=root)
    splits, documents, _ = load_datasets(paths, parse_grid_config(TITLES_GRID).sources)
    tokenized = {d: TokenText(documents[d].text, FakeEncoding()) for d in documents}
    from rag.chunking import section_aware

    section_chunks = {
        (c.doc_id, c.start, c.end): c
        for d in sorted(documents)
        for c in section_aware(documents[d], tokenized[d], TITLES_GRID["chunkings"][0]["max_tokens"])
    }
    packed = [r for r in _rows(outcome, "packed.parquet") if r["chunking"] == "section-aware-titles"]
    assert packed
    for row in packed:  # the plain chunking's span and its chunk tokens, no header
        chunk = section_chunks[(row["doc_id"], row["start"], row["end"])]
        assert row["tokens"] == chunk.n_tokens
    questions = {q.question_id: q for split in splits for q in split.questions}
    results = {
        (r["question_id"], r["pipeline"]): r
        for r in _rows(outcome, "results.parquet")
        if r["chunking"] == "section-aware-titles"
        and r["view"] == "budget"
        and r["budget"] == 64
        and r["scope"] == "collection"
    }
    for (question_id, pipeline), result in results.items():
        chunks = [
            section_chunks[(r["doc_id"], r["start"], r["end"])]
            for r in sorted(packed, key=lambda r: r["rank"])
            if r["question_id"] == question_id and r["pipeline"] == pipeline
        ]
        question = questions[question_id]
        score = score_question(gold_token_sets(question, tokenized), chunks, question.doc_id)
        assert (result["recall"], result["precision"]) == (score.recall, score.precision)
        assert result["retrieved_tokens"] == sum(c.n_tokens for c in chunks) <= 64


def test_the_plain_section_aware_rows_are_reproduced_exactly_from_the_cache(tmp_path):
    build_env(tmp_path)
    plain, _plain_models, _plain_manifest = _run(tmp_path, PLAIN_GRID)
    titles, _models, manifest = _run(tmp_path)
    assert manifest["embeddings"]["chunk_vectors_embedded"] == manifest["counts"]["chunks"][
        "section-aware-titles"
    ]  # only the headed chunks were embedded; the plain ones came from the cache
    plain_rows = [r for r in _rows(plain, "results.parquet") if r["chunking"] == "section-aware"]
    titled_rows = [r for r in _rows(titles, "results.parquet") if r["chunking"] == "section-aware"]
    assert plain_rows and len(plain_rows) == len(titled_rows)
    assert plain_rows == titled_rows


def test_a_cached_rerun_embeds_and_reranks_nothing_and_rewrites_identical_tables(titles_run):
    root, outcome, _, _ = titles_run
    again, models, manifest = _run(root)
    assert manifest["embeddings"]["chunk_vectors_embedded"] == 0
    assert manifest["reranker"]["pairs_scored"] == 0 and models.reranker_model.pairs == []
    assert {p.name: p.read_bytes() for p in again.tables} == {p.name: p.read_bytes() for p in outcome.tables}


# --- R17 -------------------------------------------------------------------------


RESULT_COLUMNS = [
    "pipeline",
    "embedder",
    "scope",
    "chunking",
    "view",
    "top_n",
    "budget",
    "scored",
    "recall",
]


def _write_run(root: Path, dataset: str, questions: list[tuple[str, str, float, float]], run_name="v2-titles"):
    """One gate-cell run: per (question, doc), the plain and the titled
    recall; the same values sit at both budgets and in both views."""
    run_dir = root / "runs" / dataset / run_name
    run_dir.mkdir(parents=True)
    rows: dict[str, list] = {name: [] for name in [*RESULT_COLUMNS, "precision", "question_id", "doc_id"]}
    for qid, doc_id, plain, titled in questions:
        for view, top_n in (("budget", 20), ("production", 8)):
            for budget in (1024, 2048):
                for chunking, value in (("section-aware", plain), ("section-aware-titles", titled)):
                    row = ["hybrid-rerank", "nomic", "collection", chunking, view, top_n, budget, True]
                    row += [value, value / 2, qid, doc_id]
                    for name, cell in zip(rows, row, strict=True):
                        rows[name].append(cell)
    pq.write_table(pa.table(rows), run_dir / "results.parquet")
    manifest = {
        "config": {"dataset": {"name": dataset}, "budgets": [1024, 2048], "budget_top_n": 20, "top_n": 8},
        "config_hash": f"hash-{dataset}",
        "datasets": {"dev": f"sha-{dataset}"},
        "counts": {"questions": len(questions)},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


R17_CONFIG = {
    "kind": "contenders",
    "table": "r17",
    "title": "section-aware chunks with their titles",
    "runs": ["qasper/v2-titles", "nq/v2-titles"],
    "chunkings": ["section-aware", "section-aware-titles"],
    "pairs": [["section-aware-titles", "section-aware"]],
    "run_name": "v2-titles",
    "gate": {"view": "budget", "budget": 1024, "resamples": 100},
    "notes": ["No language model is involved."],
}


def test_r17_reports_each_dataset_the_pooled_questions_and_the_bar_verdict(tmp_path):
    _write_run(tmp_path, "qasper", [("qa1", "paperA", 0.2, 0.3), ("qa2", "paperA", 0.4, 0.5)])
    _write_run(tmp_path, "nq", [("qn1", "page1", 0.6, 0.7)])
    cfg = parse_contenders_config(R17_CONFIG)
    paths = run_contenders(cfg, Paths(root=tmp_path))
    assert [p.relative_to(tmp_path).as_posix() for p in paths] == [
        "results/qasper/r17-v2-titles.md",
        "results/nq/r17-v2-titles.md",
    ]
    qasper = paths[0].read_text(encoding="utf-8")
    assert qasper.startswith("# R17 - qasper v2-titles: section-aware chunks with their titles")
    differences = table_rows(qasper, "## Contender minus reference")
    assert ["section-aware-titles - section-aware", "budget", "1024", "+0.1000", "+0.0500", "+0.1000", "+0.0500"] in (
        differences
    )
    verdict = [line for line in qasper.splitlines() if "Verdict" in line]
    assert any(
        "section-aware-titles clears the bar" in line and "CI excluding 0" in line for line in verdict
    ), verdict
    pooled = [line for line in qasper.splitlines() if line.startswith("- section-aware-titles - section-aware, pooled")]
    assert any("+0.1000 [" in line and "nq +0.1000, qasper +0.1000" in line for line in pooled), pooled
    first = {p: p.read_bytes() for p in paths}
    run_contenders(cfg, Paths(root=tmp_path))
    assert {p: p.read_bytes() for p in paths} == first
    # a config without a gate or notes keeps its canonical JSON
    plain = {k: v for k, v in R17_CONFIG.items() if k not in ("gate", "notes")}
    parsed = parse_contenders_config(plain)
    assert "gate" not in parsed.as_dict() and "notes" not in parsed.as_dict()


def test_the_verdict_names_every_reason_a_contender_misses_the_bar(tmp_path):
    _write_run(tmp_path, "qasper", [("qa1", "paperA", 0.2, 0.21)])
    _write_run(tmp_path, "nq", [("qn1", "page1", 0.6, 0.55)])
    cfg = parse_contenders_config(R17_CONFIG)
    paths = run_contenders(cfg, Paths(root=tmp_path))
    text = paths[0].read_text(encoding="utf-8")
    verdict = [line for line in text.splitlines() if "Verdict" in line]
    assert any(
        "does not clear the bar" in line and "pooled gain is below +0.0200" in line and "nq alone is below -0.0100" in line
        for line in verdict
    ), verdict


def test_the_gate_needs_its_budget_scored_for_every_question(tmp_path):
    _write_run(tmp_path, "qasper", [("qa1", "paperA", 0.2, 0.3)])
    _write_run(tmp_path, "nq", [("qn1", "page1", 0.6, 0.7)])
    wrong_budget = {**R17_CONFIG, "gate": {"view": "budget", "budget": 4096, "resamples": 100}}
    with pytest.raises(ValueError, match="rows at 4096 tokens"):
        run_contenders(parse_contenders_config(wrong_budget), Paths(root=tmp_path))
