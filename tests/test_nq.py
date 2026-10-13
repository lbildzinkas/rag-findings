"""Natural Questions: canonical page text, labelled spans, subset
sampling, shard download, loading and the NQ grid (R6 included).

The synthetic shards carry the real parquet schema, so the loader is
exercised end to end offline; the real dev config is only touched by the
local `rag setup && rag sample && rag run` on the actual data.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from rag.config import parse_grid_config
from rag.grid import run_grid
from rag.labels import verify_spans
from rag.nq import (
    NqShard,
    canonical_page,
    download_shard,
    ensure_nq_shards,
    iter_examples,
    load_nq,
    page_document,
    read_subset_ids,
    sample_subset,
    select_subset,
    setup_nq,
    span_over_tokens,
    subset_ids_path,
)
from rag.paths import Paths
from rag.query_type import CONTEXT, PRECISE
from tests.conftest import FakeEncoding

SCHEMA = pa.schema(
    [
        ("id", pa.string()),
        (
            "document",
            pa.struct(
                [
                    ("title", pa.string()),
                    ("url", pa.string()),
                    ("html", pa.string()),
                    (
                        "tokens",
                        pa.struct(
                            [
                                ("token", pa.list_(pa.string())),
                                ("is_html", pa.list_(pa.bool_())),
                                ("start_byte", pa.list_(pa.int64())),
                                ("end_byte", pa.list_(pa.int64())),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        ("question", pa.struct([("text", pa.string()), ("tokens", pa.list_(pa.string()))])),
        (
            "long_answer_candidates",
            pa.struct(
                [
                    ("start_token", pa.list_(pa.int64())),
                    ("end_token", pa.list_(pa.int64())),
                    ("start_byte", pa.list_(pa.int64())),
                    ("end_byte", pa.list_(pa.int64())),
                    ("top_level", pa.list_(pa.bool_())),
                ]
            ),
        ),
        (
            "annotations",
            pa.struct(
                [
                    ("id", pa.list_(pa.string())),
                    (
                        "long_answer",
                        pa.list_(
                            pa.struct(
                                [
                                    ("start_token", pa.int64()),
                                    ("end_token", pa.int64()),
                                    ("start_byte", pa.int64()),
                                    ("end_byte", pa.int64()),
                                    ("candidate_index", pa.int64()),
                                ]
                            )
                        ),
                    ),
                    (
                        "short_answers",
                        pa.list_(
                            pa.struct(
                                [
                                    ("start_token", pa.list_(pa.int64())),
                                    ("end_token", pa.list_(pa.int64())),
                                    ("start_byte", pa.list_(pa.int64())),
                                    ("end_byte", pa.list_(pa.int64())),
                                    ("text", pa.list_(pa.string())),
                                ]
                            )
                        ),
                    ),
                    ("yes_no_answer", pa.list_(pa.int64())),
                ]
            ),
        ),
    ]
)

# --- shard fixtures -------------------------------------------------------


def make_example(
    ex_id: str,
    question: str,
    tokens: list[tuple[str, bool]],
    annotations: list[dict],
) -> dict:
    """One dev example: `tokens` are (token, is_html) pairs; annotations
    are {"long": (start, end) | None, "short": [(start, end)], "yes_no": -1|0|1}."""
    flat = [t for t, _ in tokens]
    byte = 0
    start_byte, end_byte = [], []
    for t, _ in tokens:
        start_byte.append(byte)
        byte += len(t) + 1
        end_byte.append(byte)
    rows = {"id": [], "long_answer": [], "short_answers": [], "yes_no_answer": []}
    for i, ann in enumerate(annotations):
        rows["id"].append(f"{ex_id}-ann{i}")
        if ann.get("long"):
            s, e = ann["long"]
            rows["long_answer"].append(
                {"start_token": s, "end_token": e, "start_byte": 0, "end_byte": 0, "candidate_index": 0}
            )
        else:
            rows["long_answer"].append(
                {"start_token": -1, "end_token": -1, "start_byte": -1, "end_byte": -1, "candidate_index": -1}
            )
        shorts = ann.get("short", [])
        rows["short_answers"].append(
            {
                "start_token": [s for s, _ in shorts],
                "end_token": [e for _, e in shorts],
                "start_byte": [0] * len(shorts),
                "end_byte": [0] * len(shorts),
                "text": [" ".join(flat[s:e]) for s, e in shorts],
            }
        )
        rows["yes_no_answer"].append(ann.get("yes_no", -1))
    return {
        "id": ex_id,
        "document": {
            "title": f"Page {ex_id}",
            "url": "https://example.org/page",
            "html": "",
            "tokens": {
                "token": flat,
                "is_html": [h for _, h in tokens],
                "start_byte": start_byte,
                "end_byte": end_byte,
            },
        },
        "question": {"text": question, "tokens": question.split()},
        "long_answer_candidates": {
            "start_token": [],
            "end_token": [],
            "start_byte": [],
            "end_byte": [],
            "top_level": [],
        },
        "annotations": rows,
    }


def write_shard(path: Path, examples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(examples, schema=SCHEMA)
    pq.write_table(table, path)


# a page with a preamble, two heading sections, paragraphs and a table
PAGE: list[tuple[str, bool]] = [
    ("The", False),
    ("Senate", False),
    ("page", False),
    ("preamble", False),
    ("<H1>", True),
    ("Senate", False),
    ("membership", False),
    ("</H1>", True),
    ("<P>", True),
    ("The", False),
    ("United", False),
    ("States", False),
    ("Senate", False),
    ("consists", False),
    ("of", False),
    ("100", False),
    ("members", False),
    (".", False),
    ("</P>", True),
    ("<H2>", True),
    ("Leadership", False),
    ("</H2>", True),
    ("<P>", True),
    ("Parties", False),
    ("elect", False),
    ("their", False),
    ("leaders", False),
    (".", False),
    ("</P>", True),
    ("<Table>", True),
    ("<Tr>", True),
    ("<Th>", True),
    ("Party", False),
    ("</Th>", True),
    ("</Tr>", True),
    ("</Table>", True),
]


def token_index(needle: str) -> int:
    return [t for t, _ in PAGE].index(needle)


MEMBERS_P = (token_index("<P>"), token_index("</P>") + 1)  # the membership paragraph block
HUNDRED = (token_index("100"), token_index("100") + 1)  # the short answer "100"
_P2_START = PAGE.index(("<P>", True), MEMBERS_P[1])
LEADERS_P = (_P2_START, PAGE.index(("</P>", True), _P2_START) + 1)  # the leadership paragraph block
TABLE_BLOCK = (token_index("<Table>"), token_index("</Table>") + 1)
TR_BLOCK = (token_index("<Tr>"), token_index("</Tr>") + 1)  # a table row


def five(longs: list, shorts: list | None = None, yes_no: int = -1) -> list[dict]:
    """Five annotators: `longs` cycles through the given long answers,
    None padding for the rest; shorts/yes_no on the first two annotators
    (a short answer needs 2 of 5 annotators too)."""
    out = []
    for i in range(5):
        ann = {"long": longs[i] if i < len(longs) else None}
        if i < 2:
            if shorts is not None:
                ann["short"] = shorts
            ann["yes_no"] = yes_no
        out.append(ann)
    return out


def corpus() -> list[dict]:
    return [
        # short answer: 3 long answers on the membership <P>, 1 annotator with a short span
        make_example("q-short", "how many senators are there", PAGE, five([MEMBERS_P] * 3, shorts=[HUNDRED])),
        # yes/no precise: 3 long answers, a yes mark, no short span
        make_example("q-yesno", "is the senate large", PAGE, five([LEADERS_P] * 3, yes_no=1)),
        # long-answer-only: 2 long answers on paragraphs, no short answer anywhere
        make_example("q-long", "describe senate leadership", PAGE, five([LEADERS_P, MEMBERS_P])),
        # a second long-answer-only question, so per-type sampling has room
        make_example("q-long2", "explain membership rules", PAGE, five([MEMBERS_P, LEADERS_P])),
        # table long answers only: excluded
        make_example("q-table", "party breakdown", PAGE, five([TABLE_BLOCK] * 2)),
        # only one annotator gave a long answer: excluded
        make_example("q-single", "weak agreement", PAGE, five([MEMBERS_P])),
        # 2 long answers but neither is a paragraph: excluded
        make_example("q-mixedtags", "weak paragraphs", PAGE, five([TABLE_BLOCK, TR_BLOCK])),
    ]


def write_dev_shards(root: Path) -> list[Path]:
    """Spread the corpus over the seven pinned dev shard filenames."""
    examples = corpus()
    paths = []
    for i in range(7):
        shard = examples[i::7]
        path = root / "data" / "natural_questions" / "dev" / f"validation-0000{i}-of-00007.parquet"
        write_shard(path, shard)
        paths.append(path)
    return paths


def build_env(root: Path) -> None:
    paths = write_dev_shards(root)
    sample_subset(
        paths,
        seed=0,
        per_type=2,  # both eligible precise questions and two long-answer-only questions
        out_path=subset_ids_path(root),
    )


# --- canonical page -------------------------------------------------------


def test_canonical_page_text_and_offsets():
    page = canonical_page([t for t, _ in PAGE], [h for _, h in PAGE])
    expected = (
        "The Senate page preamble\n\n"
        "Senate membership\n\n"
        "The United States Senate consists of 100 members .\n\n"
        "Leadership\n\n"
        "Parties elect their leaders .\n\n"
        "Party"
    )
    assert page.text == expected

    # paragraphs tile the text exactly
    pos = 0
    for i, para in enumerate(page.paragraphs):
        assert para.start == pos
        assert para.end == para.start + len(para.text)
        assert page.text[para.start : para.end] == para.text
        pos = para.end + (2 if i + 1 < len(page.paragraphs) else 0)
    assert pos == len(page.text)

    # sections come from the heading tags
    assert [(p.section, p.section_index) for p in page.paragraphs] == [
        ("", 0),  # preamble
        ("Senate membership", 1),  # the heading's own text opens the section
        ("Senate membership", 1),
        ("Leadership", 2),
        ("Leadership", 2),
        ("Leadership", 2),  # the table cell stays in the Leadership section
    ]

    # the token-to-character map: html tokens have no span, text tokens slice back
    assert page.token_spans[token_index("<P>")] is None
    for i, (token, html) in enumerate(PAGE):
        if not html:
            start, end = page.token_spans[i]
            assert page.text[start:end] == token


def test_span_over_tokens_maps_annotation_spans():
    doc, page = page_document("d", [t for t, _ in PAGE], [h for _, h in PAGE])
    span = span_over_tokens(page, *MEMBERS_P)
    assert span is not None
    assert doc.text[span[0] : span[1]] == "The United States Senate consists of 100 members ."
    short = span_over_tokens(page, *HUNDRED)
    assert doc.text[short[0] : short[1]] == "100"
    # a range holding only html tokens has no span
    assert span_over_tokens(page, token_index("<Table>"), token_index("<Tr>")) is None


# --- classification and sampling ------------------------------------------


def test_examples_are_classified_by_annotation_agreement(tmp_path):
    shard = tmp_path / "shard.parquet"
    write_shard(shard, corpus())
    by_id = {ex.question_id: ex for ex in iter_examples([shard])}
    assert by_id["q-short"].query_type == PRECISE
    assert by_id["q-short"].eligible
    assert by_id["q-yesno"].query_type == PRECISE  # a yes/no mark is a short answer
    assert by_id["q-long"].query_type == CONTEXT
    assert by_id["q-long"].eligible
    assert not by_id["q-table"].eligible  # table long answers are excluded
    assert not by_id["q-single"].eligible  # fewer than 2 long-answer annotators
    assert not by_id["q-mixedtags"].eligible  # two long answers, neither a paragraph


def test_select_subset_is_seeded_and_order_independent():
    ids = [f"q{i}" for i in range(40)]
    one = select_subset(ids, [f"l{i}" for i in range(30)], seed=0, per_type=10)
    assert sorted(one["short"]) == one["short"]
    assert len(one["short"]) == 10 and len(one["long_only"]) == 10
    assert select_subset(list(reversed(ids)), list(reversed([f"l{i}" for i in range(30)])), 0, 10) == one
    assert select_subset(ids, [f"l{i}" for i in range(30)], 1, 10) != one
    with pytest.raises(ValueError, match="eligible"):
        select_subset(["a"], ["b"], 0, 2)


def test_sample_subset_writes_the_committed_id_list(tmp_path):
    shard = tmp_path / "shard.parquet"
    write_shard(shard, corpus())
    out = tmp_path / "nq-subset.txt"
    funnel = sample_subset([shard], seed=0, per_type=1, out_path=out)
    assert funnel["examples"] == 7
    assert funnel["long_answer_agreement"] == 6
    assert funnel["paragraph_eligible"] == 4
    assert (funnel["eligible_short"], funnel["eligible_long_only"]) == (2, 2)
    ids = sorted(read_subset_ids(out))
    assert len(ids) == 2  # one per type, whichever the seed picks
    assert len(set(ids) & {"q-long", "q-long2"}) == 1
    assert len(set(ids) & {"q-short", "q-yesno"}) == 1
    assert out.read_text(encoding="utf-8").splitlines()[0] == "# seed=0 per_type=1"
    # the same data and seed reproduce the same list
    again = tmp_path / "again.txt"
    sample_subset([shard], seed=0, per_type=1, out_path=again)
    assert again.read_bytes() == out.read_bytes()


# --- shard download -------------------------------------------------------


class LocalShard(NqShard):
    @property
    def url(self):
        return self._local_uri

    @classmethod
    def from_file(cls, path: Path) -> LocalShard:
        data = path.read_bytes()
        shard = cls(path.name, hashlib.sha256(data).hexdigest(), len(data))
        shard._local_uri = path.as_uri()
        return shard


def test_setup_nq_downloads_and_is_idempotent(tmp_path):
    source = tmp_path / "source.parquet"
    write_shard(source, corpus())
    local = LocalShard.from_file(source)
    data_dir = tmp_path / "data"

    first = setup_nq(data_dir, (local,))
    assert any("downloaded" in line for line in first)
    assert (data_dir / "natural_questions" / "dev" / source.name).is_file()

    second = setup_nq(data_dir, (local,))
    assert any("verified" in line for line in second)

    paths = ensure_nq_shards(data_dir, (local,))
    assert [p.name for p in paths] == [source.name]


def test_download_shard_rejects_bad_checksum(tmp_path):
    source = tmp_path / "source.parquet"
    write_shard(source, corpus())
    local = LocalShard.from_file(source)
    bad = LocalShard(local.filename, "0" * 64, local.size)
    bad._local_uri = source.as_uri()
    with pytest.raises(ValueError, match="sha256 mismatch"):
        download_shard(bad, tmp_path / "bad.parquet")
    assert not (tmp_path / "bad.parquet").exists()


def test_ensure_nq_shards_missing_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match="rag setup"):
        ensure_nq_shards(tmp_path)


# --- loading and the grid --------------------------------------------------


def test_load_nq_builds_documents_questions_and_spans(tmp_path):
    build_env(tmp_path)
    split = load_nq(Paths(root=tmp_path))
    assert split.dataset == "nq"
    assert split.split == "dev"
    assert split.subset_size == 4

    documents = {d.doc_id: d for d in split.documents}
    assert sorted(documents) == ["q-long", "q-long2", "q-short", "q-yesno"]  # the subset's pages

    by_id = {q.question_id: q for q in split.questions}
    short = by_id["q-short"]
    assert short.query_type == PRECISE
    assert short.text == "how many senators are there"
    assert len(short.annotators) == 3  # the paragraph long answers, one per annotator
    for annotator in short.annotators:
        (span,) = annotator
        assert documents["q-short"].text[span.start : span.end] == "The United States Senate consists of 100 members ."
    assert len(short.short_annotators) == 2
    assert short.short_annotators[0][0].quote == "100"

    assert by_id["q-long"].query_type == CONTEXT
    assert by_id["q-long"].short_annotators == ()

    # every labelled span round-trips, long and short:
    # q-short 3 long + 2 short, q-yesno 3, q-long 2, q-long2 2
    assert verify_spans(split, documents) == 12


def test_load_nq_rejects_ids_missing_from_the_dev_config(tmp_path):
    write_dev_shards(tmp_path)
    subset_ids_path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    subset_ids_path(tmp_path).write_text("# seed=0 per_type=1\nq-short\nq-missing\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not in the dev config"):
        load_nq(Paths(root=tmp_path))


def test_load_nq_requires_the_subset_file(tmp_path):
    write_dev_shards(tmp_path)
    with pytest.raises(FileNotFoundError, match="rag sample"):
        load_nq(Paths(root=tmp_path))


GRID = {
    "kind": "grid",
    "dataset": {"name": "nq", "splits": ["dev"]},
    "pipeline": "bm25",
    "chunkings": [
        {"name": "fixed-16", "method": "fixed", "chunk_tokens": 16},
        {"name": "section-aware", "method": "section_aware", "max_tokens": 32},
        {"name": "small-to-big", "method": "small_to_big", "max_tokens": 32, "child_tokens": 8},
    ],
    "budgets": [16, 32, 64],
    "top_n": 2,
    "side_top_n": 1,
    "scopes": ["collection", "document"],
    "fixed_k": [1, 2],
    "search_depth": 100,
    "seed": 0,
    "run_name": "grid",
}


@pytest.fixture
def nq_grid(tmp_path):
    build_env(tmp_path)
    cfg = parse_grid_config(GRID)
    outcome = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding())
    return cfg, outcome, tmp_path


def table_rows(text: str, heading: str) -> list[list[str]]:
    """Data rows of the first markdown table under `heading`."""
    lines = text.split(heading, 1)[1].splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("|"))
    rows = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[2:]  # skip the header and separator rows


def test_nq_grid_stores_types_and_short_flags(nq_grid):
    _, outcome, root = nq_grid
    assert outcome.n_questions == 4
    assert outcome.query_types == {"precise": 2, "context": 2, "mixed": 0}
    questions = pq.read_table(root / "runs" / "nq" / "grid" / "questions.parquet").to_pydict()
    assert dict(zip(questions["question_id"], questions["query_type"], strict=True)) == {
        "q-short": "precise",
        "q-yesno": "precise",
        "q-long": "context",
        "q-long2": "context",
    }
    assert dict(zip(questions["question_id"], questions["short_answer"], strict=True)) == {
        "q-short": True,
        "q-yesno": None,
        "q-long": None,
        "q-long2": None,
    }


def test_nq_grid_scores_short_recall_only_where_spans_exist(nq_grid):
    _, _, root = nq_grid
    results = pq.read_table(root / "runs" / "nq" / "grid" / "results.parquet").to_pylist()
    for row in results:
        if row["question_id"] == "q-short" and row["scored"]:
            assert row["short_recall"] is not None and 0.0 <= row["short_recall"] <= 1.0
        else:
            assert row["short_recall"] is None


def test_nq_tables_cover_query_type_counts_and_r6(nq_grid):
    cfg, outcome, root = nq_grid
    assert sorted(p.name for p in outcome.tables) == [
        "r2-grid.md",
        "r2w-grid.md",
        "r3-grid.md",
        "r4-grid.md",
        "r6-grid.md",
    ]
    r6 = (root / "results" / "nq" / "r6-grid.md").read_text(encoding="utf-8")
    assert "n = 1 precise questions with a short-answer span" in r6
    rows = table_rows(r6, "## Short-answer span recall")
    assert len(rows) == len(cfg.chunkings) * len(cfg.budgets)
    assert [r[0] for r in rows] == [c.name for c in cfg.chunkings for _ in cfg.budgets]
    for row in rows:
        budget = int(row[1])
        size = 16 if row[0] == "fixed-16" else None
        is_na = size is not None and size > budget
        assert all((cell == "n/a") == is_na for cell in row[2:5]), row
        if not is_na:
            assert float(row[2].rstrip("†")) <= 1.0 and float(row[3].rstrip("†")) <= 1.0
    # every NQ table shows the planned count per query type
    for name in ("r2", "r3", "r4", "r6"):
        table = (root / "results" / "nq" / f"{name}-grid.md").read_text(encoding="utf-8")
        assert table_rows(table, "## Questions") == [["precise", "2"], ["context", "2"], ["mixed", "0"], ["total", "4"]]


def test_nq_tables_regenerate_byte_identically(nq_grid):
    cfg, outcome, root = nq_grid
    first = {p.name: p.read_bytes() for p in outcome.tables}
    again = run_grid(cfg, Paths(root=root), encoding=FakeEncoding())
    assert {p.name: p.read_bytes() for p in again.tables} == first


def test_pooled_run_keeps_each_dataset_n_visible(tmp_path):
    from tests.test_grid import GRID as QASPER_GRID
    from tests.test_grid import build_env as build_qasper_env

    build_qasper_env(tmp_path)
    build_env(tmp_path)
    pooled = {
        **{k: v for k, v in QASPER_GRID.items() if k != "dataset"},
        "dataset": {
            "name": "pooled",
            "sources": [
                {"name": "qasper", "splits": ["dev", "test"]},
                {"name": "nq", "splits": ["dev"]},
            ],
        },
    }
    cfg = parse_grid_config(pooled)
    outcome = run_grid(cfg, Paths(root=tmp_path), encoding=FakeEncoding())
    assert outcome.n_questions == 8  # 4 qasper + 4 nq

    questions = pq.read_table(tmp_path / "runs" / "pooled" / "grid" / "questions.parquet").to_pydict()
    assert sorted(set(questions["dataset"])) == ["nq", "qasper"]
    results = pq.read_table(tmp_path / "runs" / "pooled" / "grid" / "results.parquet").to_pylist()
    assert {row["dataset"] for row in results} == {"nq", "qasper"}

    # no r6 for a pooled run
    assert sorted(p.name for p in outcome.tables) == ["r2-grid.md", "r2w-grid.md", "r3-grid.md", "r4-grid.md"]

    for name in ("r2", "r3", "r4"):
        table = (tmp_path / "results" / "pooled" / f"{name}-grid.md").read_text(encoding="utf-8")
        rows = table_rows(table, "## Questions")
        assert rows == [
            ["nq", "precise", "2"],
            ["nq", "context", "2"],
            ["nq", "mixed", "0"],
            ["qasper", "precise", "2"],
            ["qasper", "context", "1"],
            ["qasper", "mixed", "1"],
            ["total", "", "8"],
        ]
        assert "| qasper/dev |" in table and "| qasper/test |" in table and "| nq/dev |" in table

    # pooled runs write under their own label, never over the qasper tables
    assert (tmp_path / "results" / "pooled" / "r2-grid.md").is_file()
    assert not (tmp_path / "results" / "qasper").exists()
