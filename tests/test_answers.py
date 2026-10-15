"""The answers stage: config validation, setup assembly from packed.parquet
(the oracle's tie-break included), prompt rendering with the budget check,
the dry run's availability report, and the R14 scaffold's clustered
analysis - all on synthetic parquet fixtures, offline."""

from __future__ import annotations

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.answers import (
    ANSWERS_SCHEMA,
    SetupSpec,
    analyse_answers,
    answers_config_hash,
    clustered_mean,
    dry_run,
    load_packed,
    oracle_picks,
    parse_answers_config,
    read_answers,
    render_r14,
    render_setup_prompts,
    setup_missing,
    write_answers,
)
from rag.bootstrap import resample_counts
from rag.documents import build_document
from rag.grid import PACKED_SCHEMA, RESULTS_SCHEMA
from rag.labels import Question
from rag.paths import Paths
from rag.query_type import CONTEXT, PRECISE
from rag.reader_sample import write_sample

QASPER_DOC = build_document(
    "paperA",
    "Alpha abstract with tickets.",
    [("Intro", ["First body paragraph about tickets.", "Second body paragraph about renewals."])],
)
NQ_DOC = build_document("page1", "The Senate page abstract.", [("Section", ["The Senate consists of 100 members."])])

QASPER_QUESTION = Question(
    question_id="q1", doc_id="paperA", split="dev", text="How do tickets work?", annotators=()
)
NQ_PRECISE = Question(
    question_id="nq1", doc_id="page1", split="dev", text="how many members", annotators=(), query_type=PRECISE
)
NQ_CONTEXT = Question(
    question_id="nq2", doc_id="page1", split="dev", text="describe the senate", annotators=(), query_type=CONTEXT
)

# two disjoint spans of the QASPER document: the abstract and the first body paragraph
SPAN_A = (0, len("Alpha abstract with tickets."))
SPAN_B = (SPAN_A[1] + 2, SPAN_A[1] + 2 + len("First body paragraph about tickets."))

RUN = "fake-run"
CHUNKINGS = ("fixed-64", "fixed-128", "section-aware")


def write_packed(path, rows):
    table = pa.Table.from_pylist(rows, schema=PACKED_SCHEMA)
    pq.write_table(table, path)


def packed_row(question_id, chunking, rank, span, tokens, doc_id, dataset):
    return {
        "dataset": dataset,
        "split": "dev",
        "question_id": question_id,
        "doc_id": doc_id,
        "query_type": "mixed",
        "pipeline": "hybrid-rerank",
        "embedder": "nomic",
        "chunking": chunking,
        "scope": "collection",
        "view": "budget",
        "budget": 1024,
        "rank": rank,
        "start": span[0],
        "end": span[1],
        "tokens": tokens,
    }


def result_row(question_id, chunking, recall, dataset):
    row = {name: None for name in RESULTS_SCHEMA.names}
    row |= {
        "dataset": dataset,
        "split": "dev",
        "question_id": question_id,
        "doc_id": "paperA" if dataset == "qasper" else "page1",
        "query_type": "mixed",
        "pipeline": "hybrid-rerank",
        "embedder": "nomic",
        "chunking": chunking,
        "scope": "collection",
        "view": "budget",
        "top_n": 20,
        "budget": 1024,
        "scored": True,
        "recall": recall,
    }
    return row


@pytest.fixture
def env(tmp_path, fake_encoding):
    """A runs/ tree with one baseline run per dataset and a committed sample."""
    paths = Paths(root=tmp_path)
    for dataset, questions in (("qasper", (QASPER_QUESTION,)), ("nq", (NQ_PRECISE, NQ_CONTEXT))):
        run_dir = paths.run_dir(RUN, dataset)
        run_dir.mkdir(parents=True)
        rows = []
        for question in questions:
            for chunking, (span, tokens) in zip(
                CHUNKINGS, ((SPAN_A, 5), (SPAN_B, 6), (SPAN_A, 7)), strict=False
            ):
                if chunking == "section-aware":
                    continue
                rows.append(packed_row(question.question_id, chunking, 1, span, tokens, QASPER_DOC.doc_id, dataset))
                rows.append(
                    packed_row(question.question_id, chunking, 2, SPAN_B if span == SPAN_A else SPAN_A, 4,
                               QASPER_DOC.doc_id, dataset)
                )
        write_packed(run_dir / "packed.parquet", rows)
        results = [
            result_row(question.question_id, chunking, recall, dataset)
            for question in questions
            for chunking, recall in (("fixed-64", 0.25), ("fixed-128", 0.5), ("section-aware", 0.5))
        ]
        pq.write_table(pa.Table.from_pylist(results, schema=RESULTS_SCHEMA), run_dir / "results.parquet")
    write_sample(
        tmp_path / "configs" / "v2" / "reader-sample.txt",
        seed=0,
        qasper_ids=["q1"],
        nq_ids=["nq1", "nq2"],
    )
    return paths


def make_config(paths, setups=None):
    return parse_answers_config(
        {
            "kind": "answers",
            "run_name": "test-answers",
            "dataset": {
                "name": "pooled",
                "sources": [
                    {"name": "qasper", "splits": ["dev"]},
                    {"name": "nq", "splits": ["dev"]},
                ],
            },
            "sample": "configs/v2/reader-sample.txt",
            "view": "budget",
            "budget": 1024,
            "top_n": 20,
            "pipeline": "hybrid-rerank",
            "embedder": "nomic",
            "oracle_chunkings": ["fixed-64", "fixed-128", "section-aware"],
            "setups": setups
            or [
                {"name": "section-aware", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "fixed-128"},
                {"name": "oracle", "kind": "oracle", "runs": {"qasper": RUN, "nq": RUN}},
                {"name": "none", "kind": "none"},
            ],
            "resamples": 200,
            "seed": 0,
            "confidence": 0.95,
        }
    )


# --- config ----------------------------------------------------------------


def test_config_parses_and_hashes_stably(env):
    cfg = make_config(env)
    assert [s.name for s in cfg.setups] == ["section-aware", "oracle", "none"]
    assert answers_config_hash(cfg) == answers_config_hash(make_config(env))
    raw = cfg.as_dict()
    assert raw["kind"] == "answers" and raw["view"] == "budget"


def make_config_with(env, **overrides):
    base = {
        "kind": "answers",
        "run_name": "test-answers",
        "dataset": {
            "name": "pooled",
            "sources": [
                {"name": "qasper", "splits": ["dev"]},
                {"name": "nq", "splits": ["dev"]},
            ],
        },
        "sample": "configs/v2/reader-sample.txt",
        "view": "budget",
        "budget": 1024,
        "top_n": 20,
        "pipeline": "hybrid-rerank",
        "embedder": "nomic",
        "oracle_chunkings": ["fixed-64", "fixed-128", "section-aware"],
        "setups": [
            {"name": "section-aware", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "fixed-128"},
            {"name": "none", "kind": "none"},
        ],
        "resamples": 200,
        "seed": 0,
        "confidence": 0.95,
    }
    base.update(overrides)
    return parse_answers_config(base)


def test_config_validation_rejects_bad_shapes(env):
    with pytest.raises(ValueError, match="pooled"):
        parse_answers_config(
            {"kind": "answers", "run_name": "x", "dataset": {"name": "qasper", "splits": ["dev"]}}
        )
    with pytest.raises(ValueError, match="budget view"):
        make_config_with(env, view="production")
    with pytest.raises(ValueError, match="needs a section-aware"):
        make_config_with(
            env,
            setups=[
                {"name": "a", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "c"},
                {"name": "none", "kind": "none"},
            ],
        )
    with pytest.raises(ValueError, match="chunking or pipeline"):
        make_config_with(
            env,
            setups=[
                {"name": "section-aware", "runs": {"qasper": RUN, "nq": RUN}},
                {"name": "none", "kind": "none"},
            ],
        )
    with pytest.raises(ValueError, match="reads no runs"):
        make_config_with(
            env,
            setups=[
                {"name": "section-aware", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "c"},
                {"name": "none", "kind": "none", "runs": {"qasper": RUN}},
            ],
        )
    with pytest.raises(ValueError, match="picks its chunkings"):
        make_config_with(
            env,
            setups=[
                {"name": "section-aware", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "c"},
                {"name": "o", "kind": "oracle", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "c"},
            ],
        )
    with pytest.raises(ValueError, match="name each dataset"):
        make_config_with(
            env,
            setups=[
                {"name": "section-aware", "runs": {"qasper": RUN}, "chunking": "c"},
                {"name": "none", "kind": "none"},
            ],
        )
    with pytest.raises(ValueError, match="unique names"):
        make_config_with(
            env,
            setups=[
                {"name": "a", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "c"},
                {"name": "a", "runs": {"qasper": RUN, "nq": RUN}, "chunking": "d"},
                {"name": "none", "kind": "none"},
            ],
        )


# --- setup assembly ----------------------------------------------------------


def test_load_packed_filters_the_cell_and_keeps_rank_order(env):
    packed = load_packed(env.run_dir(RUN, "qasper"), "hybrid-rerank", "nomic", "fixed-64", "budget", 1024, "collection")
    spans = packed["q1"]
    assert [s.rank for s in spans] == [1, 2]
    assert spans[0].start == SPAN_A[0]
    assert sum(s.tokens for s in spans) == 9
    with pytest.raises(ValueError, match="no packed spans"):
        load_packed(env.run_dir(RUN, "qasper"), "hybrid-rerank", "nomic", "absent", "budget", 1024, "collection")
    # a merged read (chunking None) rejects colliding ranks across chunkings
    with pytest.raises(ValueError, match="not distinct"):
        load_packed(env.run_dir(RUN, "qasper"), "hybrid-rerank", "nomic", None, "budget", 1024, "collection")


def test_oracle_picks_highest_recall_with_ties_to_the_smaller_chunk(env):
    picks = oracle_picks(env.run_dir(RUN, "qasper"), CHUNKINGS, "hybrid-rerank", "nomic", "budget", 20, 1024, "collection")
    assert picks["q1"] == "fixed-128"  # 0.5 beats 0.25; ties with section-aware go to the smaller chunk


def test_setup_missing_reports_pending_runs(env):
    cfg = make_config(env)
    assert setup_missing(cfg.setups[0], env) == []
    assert setup_missing(cfg.setups[2], env) == []
    absent = SetupSpec(name="late-128", kind="packed", runs=(("qasper", "nope"), ("nq", "nope")), chunking="late-128")
    assert setup_missing(absent, env) == [
        "nq: nope (packed.parquet)",
        "qasper: nope (packed.parquet)",
    ]


# --- prompts -----------------------------------------------------------------


DOCUMENTS = {"paperA": QASPER_DOC, "page1": NQ_DOC}


def make_sample():
    from rag.answers import Sample, SampledQuestion

    return Sample(
        seed=0,
        per_dataset={
            "qasper": (SampledQuestion(question=QASPER_QUESTION, dataset="qasper"),),
            "nq": (
                SampledQuestion(question=NQ_PRECISE, dataset="nq"),
                SampledQuestion(question=NQ_CONTEXT, dataset="nq"),
            ),
        },
    )


def test_render_setup_prompts_packed_chunks_in_packed_order(env, fake_encoding):
    cfg = make_config(env)
    prompts = render_setup_prompts(cfg, cfg.setups[0], make_sample(), DOCUMENTS, env, encoding=fake_encoding)
    assert [p.question_id for p in prompts] == ["q1", "nq1", "nq2"]
    first = prompts[0]
    text_a = QASPER_DOC.text[SPAN_A[0] : SPAN_A[1]]
    text_b = QASPER_DOC.text[SPAN_B[0] : SPAN_B[1]]
    # the setup reads fixed-128, whose rank 1 is SPAN_B: packed order, not document order
    assert first.prompt.index(text_b) < first.prompt.index(text_a)
    assert first.context_tokens == 10
    assert first.prompt.startswith("Answer the question from the context only, briefly.")
    assert first.prompt.endswith("Question: How do tickets work?")
    precise = prompts[1]
    assert "Give a short answer." in precise.prompt  # NQ precise questions ask for a short answer
    assert "Give a short answer." not in prompts[0].prompt
    assert all(p.within_budget for p in prompts)


def test_render_setup_prompts_floor_has_no_context(env, fake_encoding):
    cfg = make_config(env)
    prompts = render_setup_prompts(cfg, cfg.setups[2], make_sample(), DOCUMENTS, env, encoding=fake_encoding)
    assert all(p.context_tokens == 0 and p.chunks == 0 for p in prompts)
    assert "Context:" not in prompts[0].prompt
    assert "from the context only" not in prompts[0].prompt
    assert all(p.within_budget for p in prompts)


def test_render_setup_prompts_oracle_uses_the_picked_chunking(env, fake_encoding):
    cfg = make_config(env)
    prompts = render_setup_prompts(cfg, cfg.setups[1], make_sample(), DOCUMENTS, env, encoding=fake_encoding)
    first = prompts[0]
    assert first.context_tokens == 10  # fixed-128's spans (6 + 4), the oracle pick for q1
    assert first.prompt_hash != prompts[1].prompt_hash


def test_dry_run_reports_available_and_pending_setups(env, fake_encoding):
    cfg = make_config(env)
    cfg = parse_answers_config(cfg.as_dict() | {"setups": cfg.as_dict()["setups"] + [{"name": "late-128", "runs": {"qasper": "nope", "nq": "nope"}, "chunking": "late-128"}]})

    def loader(config, paths):
        return make_sample(), DOCUMENTS

    report = dry_run(cfg, env, encoding=fake_encoding, loader=loader)
    assert report["sample"]["counts"] == {"qasper": 1, "nq": 2}
    assert report["setups"]["section-aware"]["qasper"]["questions"] == 1
    assert report["setups"]["none"]["nq"]["questions"] == 2
    assert report["setups"]["late-128"]["pending"] == [
        "nq: nope (packed.parquet)",
        "qasper: nope (packed.parquet)",
    ]
    assert report["over_budget_prompts"] == 0
    assert (env.run_dir("test-answers") / "dry-run.json").is_file()


def test_dry_run_fails_when_packed_chunks_exceed_the_budget(env, fake_encoding):
    cfg = make_config(env)
    rows = [
        packed_row("q1", "fixed-128", 1, SPAN_A, 2000, "paperA", "qasper"),
    ]
    write_packed(env.run_dir(RUN, "qasper") / "packed.parquet", rows + [
        packed_row("nq1", "fixed-128", 1, SPAN_A, 5, "paperA", "nq"),
        packed_row("nq2", "fixed-128", 1, SPAN_A, 5, "paperA", "nq"),
    ])

    def loader(config, paths):
        return make_sample(), DOCUMENTS

    with pytest.raises(ValueError, match="exceed the 1024-token budget"):
        dry_run(cfg, env, encoding=fake_encoding, loader=loader)


# --- analysis and R14 ---------------------------------------------------------


def score_row(dataset, question_id, doc_id, setup, score, query_type="precise", secondary=None):
    return {
        "dataset": dataset,
        "question_id": question_id,
        "doc_id": doc_id,
        "query_type": query_type,
        "setup": setup,
        "metric": "short_match",
        "score": score,
        "secondary": secondary,
        "prompt_hash": "h",
    }


def synthetic_scores():
    rows = []
    for i, (score_a, score_b) in enumerate([(1.0, 0.0), (1.0, 0.5), (0.0, 1.0), (0.5, 0.5)]):
        rows.append(score_row("nq", f"q{i}", f"d{i % 2}", "section-aware", score_a, secondary=score_a))
        rows.append(score_row("nq", f"q{i}", f"d{i % 2}", "other", score_b, secondary=score_b))
    for i, (score_a, score_b) in enumerate([(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 0.0), (1.0, 0.5), (0.0, 0.0)]):
        rows.append(score_row("qasper", f"p{i}", f"paper{i % 3}", "section-aware", score_a, query_type="mixed"))
        rows.append(score_row("qasper", f"p{i}", f"paper{i % 3}", "other", score_b, query_type="mixed"))
    return rows


def test_clustered_mean_point_and_resamples():
    values = np.array([1.0, 0.0, 1.0, 0.0])
    cluster = np.array([0, 0, 1, 1])
    counts = resample_counts(2, 50, seed=0, stratum="nq")
    estimate = clustered_mean(values, cluster, counts)
    assert estimate.point == 0.5
    assert len(estimate.samples) == 50
    assert estimate.samples.min() >= 0.0 and estimate.samples.max() <= 1.0


def test_analyse_answers_means_cis_and_difference():
    analysis = analyse_answers(synthetic_scores(), ["section-aware", "other"], ["qasper", "nq"], resamples=400, seed=0)
    nq = analysis[("nq", "section-aware")]
    assert nq.n == 4 and nq.score.point == 0.625
    assert analysis[("nq", "other")].difference.point == pytest.approx(0.5 - 0.625)
    assert nq.difference is None  # the reference has no difference from itself
    pooled = analysis[("pooled", "other")]
    assert pooled.n == 10
    qasper = analysis[("qasper", "section-aware")]
    assert qasper.score.point == pytest.approx((1 + 1 + 0 + 0.5 + 1 + 0) / 6)
    for estimate in analysis.values():
        assert estimate.score_interval.low <= estimate.score.point <= estimate.score_interval.high


def test_analyse_answers_needs_matching_question_coverage():
    rows = synthetic_scores()
    rows = [row for row in rows if not (row["question_id"] == "q3" and row["setup"] == "other")]
    with pytest.raises(ValueError, match="different questions"):
        analyse_answers(rows, ["section-aware", "other"], ["qasper", "nq"], resamples=10)


def test_answers_parquet_round_trip(tmp_path):
    rows = synthetic_scores()[:4]
    path = tmp_path / "answers.parquet"
    write_answers(path, rows)
    read = read_answers(path)
    assert read[0]["setup"] == "section-aware" and read[1]["secondary"] is not None
    assert set(ANSWERS_SCHEMA.names) == set(read[0])


def test_render_r14_lists_every_setup_and_dataset(env):
    cfg = make_config(env)
    text = render_r14(cfg, "hash" * 16, synthetic_scores())
    assert "# R14 - test-answers" in text
    for setup in ("section-aware", "oracle", "none"):
        assert f"| pooled | {setup} |" in text
        assert f"| nq | {setup} |" in text
    assert "| section-aware | 4 |" in text  # the NQ by-type block
    assert "difference from section-aware" in text
    # a setup without scores renders empty cells, not an error
    assert "| qasper | oracle | - | - | - | - | - |" in text
    empty = render_r14(cfg, "hash" * 16, [])
    assert "| pooled | section-aware | - | - | - | - | - |" in empty
