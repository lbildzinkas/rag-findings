"""Natural Questions dev subset: download, canonical pages, labelled spans.

`setup` downloads only the dev config of
`google-research-datasets/natural_questions` from Hugging Face: seven
parquet shards of about 1.34 GB in total, each pinned by size and sha256
and streamed to disk one shard at a time. The default config, whose train
split is 57 GB, is never touched: no `datasets` loading goes through the
repo's default branch, only the pinned `dev/` file URLs.

The subset sampler picks 1,000 dev questions - 500 with a short answer
(precise) and 500 long-answer-only (context) - from the questions where
at least 2 of 5 annotators gave a long answer and at least one of those
long answers is a paragraph (`<P>`); tables and lists are excluded. The
selection is seeded by ranking question ids by sha256(f"{seed}:{id}"),
which is reproducible on any machine, and the resulting id list is
committed (ids only, never dataset text, so the ShareAlike term of the
CC BY-SA 3.0 licence never attaches to the repository).

The canonical page text is the page's non-HTML tokens: tokens joined
with single spaces inside a paragraph, paragraphs joined with blank
lines. A map from token offsets to character offsets records each
token's span in that text; the labelled span of every annotator whose
long answer is a `<P>` paragraph is that paragraph, and short-answer
spans are kept per annotator for R6. Sections come from the page's
heading tags (`<H1>`-`<H6>`), so section-aware chunking and the
small-to-big parents follow the page's own structure.
"""

from __future__ import annotations

import hashlib
import re
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq

from .documents import Document, Paragraph
from .labels import LabelledSpan, Question
from .query_type import CONTEXT, PRECISE

NQ_REPO = "google-research-datasets/natural_questions"
NQ_BASE_URL = f"https://huggingface.co/datasets/{NQ_REPO}/resolve/main"
NQ_CONFIG = "dev"

LONG_ANSWER_MIN_ANNOTATORS = 2  # a question is kept when >= 2 of 5 annotators gave a long answer
SHORT_ANSWER_MIN_ANNOTATORS = 2  # ...and counts as having a short answer when >= 2 gave one (span or yes/no)
SUBSET_PER_TYPE = 500
SUBSET_SEED = 0
SUBSET_RELATIVE_PATH = Path("configs") / "nq-subset.txt"


@dataclass(frozen=True)
class NqShard:
    filename: str
    sha256: str
    size: int

    @property
    def url(self) -> str:
        return f"{NQ_BASE_URL}/{NQ_CONFIG}/{self.filename}"


# The dev config's seven parquet shards, pinned by size and sha256.
NQ_DEV_SHARDS: tuple[NqShard, ...] = (
    NqShard(
        "validation-00000-of-00007.parquet",
        "348fb27f787e68e1c6389d0fdc3453a41fc66321ec30a2f3c451f1ef82d07c20",
        185_560_593,
    ),
    NqShard(
        "validation-00001-of-00007.parquet",
        "5be65bc20b859c5ca6041043507fbc8f34224192a70e5e767dcb2876f04468a4",
        197_099_510,
    ),
    NqShard(
        "validation-00002-of-00007.parquet",
        "d639409b817ceceacf3b2538fed27065ff296793c158707e9e07f3ab2f737a9d",
        190_921_063,
    ),
    NqShard(
        "validation-00003-of-00007.parquet",
        "4d1df3bea63e9bb567bdf3b87e8955b947f8c6f998bded0840c01bb9a13968bc",
        191_104_999,
    ),
    NqShard(
        "validation-00004-of-00007.parquet",
        "40781760176ff93afc84fb5dba1239f46a082aa2edc0e7dd4fad1a34f38435e0",
        192_525_840,
    ),
    NqShard(
        "validation-00005-of-00007.parquet",
        "3988c0d16f6b014348be130ef20ce324cf2b9bbafbddee96ad78a37e52e8903f",
        190_204_549,
    ),
    NqShard(
        "validation-00006-of-00007.parquet",
        "b3153de2b44df02e0f0a5eac8d82499ef175f99026e8e4dc30e55f4e3b22e725",
        189_709_804,
    ),
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nq_shard_dir(data_dir: Path) -> Path:
    return data_dir / "natural_questions" / NQ_CONFIG


def download_shard(shard: NqShard, dest: Path) -> None:
    """Stream the shard to dest, then verify size and sha256."""
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(shard.url) as response, tmp.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)
    size = tmp.stat().st_size
    if size != shard.size:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"{shard.filename}: expected {shard.size} bytes, downloaded {size}")
    digest = _sha256_file(tmp)
    if digest != shard.sha256:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"{shard.filename}: sha256 mismatch (got {digest})")
    tmp.replace(dest)


def verify_shard(shard: NqShard, dest: Path) -> bool:
    """True when dest exists with the pinned size and sha256."""
    if not dest.is_file():
        return False
    if dest.stat().st_size != shard.size:
        raise ValueError(
            f"{dest.name}: size {dest.stat().st_size} != pinned {shard.size}; delete the file and re-run setup"
        )
    digest = _sha256_file(dest)
    if digest != shard.sha256:
        raise ValueError(f"{dest.name}: sha256 mismatch (got {digest}); delete the file and re-run setup")
    return True


def setup_nq(data_dir: Path, shards: tuple[NqShard, ...] = NQ_DEV_SHARDS) -> list[str]:
    """Make the dev config's shards present and verified. Returns report lines."""
    shard_dir = nq_shard_dir(data_dir)
    shard_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for shard in shards:
        dest = shard_dir / shard.filename
        if verify_shard(shard, dest):
            lines.append(f"verified {shard.filename} (sha256 ok)")
        else:
            download_shard(shard, dest)
            lines.append(f"downloaded {shard.filename} ({shard.size:,} bytes, sha256 ok)")
    return lines


def ensure_nq_shards(data_dir: Path, shards: tuple[NqShard, ...] = NQ_DEV_SHARDS) -> list[Path]:
    """Return the shard paths; raise with a hint when any shard is missing."""
    paths = [nq_shard_dir(data_dir) / shard.filename for shard in shards]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            f"missing Natural Questions dev shard(s) {missing} under {nq_shard_dir(data_dir)}; "
            "run `uv run rag setup` first"
        )
    return paths


def nq_dataset_hash(shard_paths: list[Path]) -> str:
    """Content hash of the dev config: sha256 over its pinned shards."""
    lines = [f"{p.name} {_sha256_file(p)}" for p in shard_paths]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


# --- canonical page text -------------------------------------------------

_HEADING_OPEN = frozenset(f"<H{n}>" for n in range(1, 7))
_HEADING_CLOSE = frozenset(f"</H{n}>" for n in range(1, 7))
_HEADING_OPEN_ATTR = tuple(f"<H{n} " for n in range(1, 7))
_BLOCK_OPENS = frozenset({"<P>", "<Li>", "<Tr>", "<Table>", "<Ul>", "<Ol>", "<Dl>", "<Dt>", "<Dd>"})
_BLOCK_CLOSES = frozenset(f"</{tag[1:]}" for tag in _BLOCK_OPENS)
_CELL_OPEN_RE = re.compile(r"^<T[dh]\b[^>]*>$", re.IGNORECASE)
_CELL_CLOSE_RE = re.compile(r"^</T[dh]>$", re.IGNORECASE)


def _is_heading_open(tag: str) -> bool:
    return tag in _HEADING_OPEN or tag.startswith(_HEADING_OPEN_ATTR)


def _is_heading_close(tag: str) -> bool:
    return tag in _HEADING_CLOSE


def _is_paragraph_boundary(tag: str) -> bool:
    """An HTML tag that ends the current paragraph: the open or close of a
    block element (paragraphs, headings, list items, table structure)."""
    return (
        tag in _BLOCK_OPENS
        or tag in _BLOCK_CLOSES
        or _is_heading_open(tag)
        or _is_heading_close(tag)
        or bool(_CELL_OPEN_RE.match(tag))
        or bool(_CELL_CLOSE_RE.match(tag))
    )


@dataclass(frozen=True)
class CanonicalPage:
    """The page's canonical text and the token-to-character-offset map.

    `token_spans` has one entry per document token: the [start, end)
    character span of a non-HTML token in the canonical text, or None for
    an HTML token. `paragraphs` tile the text exactly.
    """

    text: str
    token_spans: tuple[tuple[int, int] | None, ...]
    paragraphs: tuple[Paragraph, ...]


def canonical_page(tokens: list[str], is_html: list[bool]) -> CanonicalPage:
    """Build the canonical page text from the non-HTML tokens.

    Non-HTML tokens are joined with single spaces inside a paragraph and
    paragraphs with blank lines, so paragraphs tile the text exactly. A
    paragraph boundary falls at the open or close of any block-level tag;
    a heading tag also starts a new section, named by the heading's text.
    """
    finished: list[tuple[str, int, list[int]]] = []  # (section name, section index, token indices)
    current: list[int] = []
    section_name = ""  # name of the section paragraphs are collected in
    section_index = 0
    pending_heading: list[str] | None = None  # heading text tokens while inside a heading

    def close_paragraph() -> None:
        nonlocal current
        if current:
            name = " ".join(pending_heading) if pending_heading is not None else section_name
            finished.append((name, section_index, current))
            current = []

    for i, (token, html) in enumerate(zip(tokens, is_html, strict=True)):
        if html:
            if _is_heading_open(token):
                close_paragraph()
                section_index += 1
                section_name = ""
                pending_heading = []
            elif _is_heading_close(token):
                close_paragraph()
                if pending_heading is not None:
                    section_name = " ".join(pending_heading)
                pending_heading = None
            elif _is_paragraph_boundary(token):
                close_paragraph()
            continue
        current.append(i)
        if pending_heading is not None:
            pending_heading.append(token)
    close_paragraph()

    pieces: list[str] = []
    spans: list[tuple[int, int] | None] = [None] * len(tokens)
    paragraphs: list[Paragraph] = []
    pos = 0
    for name, index, token_indices in finished:
        if pieces:
            pieces.append("\n\n")
            pos += 2
        start = pos
        for j, token_index in enumerate(token_indices):
            if j:
                pieces.append(" ")
                pos += 1
            token = tokens[token_index]
            pieces.append(token)
            spans[token_index] = (pos, pos + len(token))
            pos += len(token)
        paragraphs.append(
            Paragraph(
                start=start,
                end=pos,
                text=" ".join(tokens[t] for t in token_indices),
                section=name,
                section_index=index,
            )
        )
    return CanonicalPage(text="".join(pieces), token_spans=tuple(spans), paragraphs=tuple(paragraphs))


def page_document(
    doc_id: str, tokens: list[str], is_html: list[bool], title: str = ""
) -> tuple[Document, CanonicalPage]:
    """The page as a Document over its canonical text, plus the page. The
    Document carries the page's own title and marks its headings as part
    of the text (both for rag.titles)."""
    page = canonical_page(tokens, is_html)
    doc = Document(doc_id=doc_id, text=page.text, paragraphs=page.paragraphs, title=title, headings_in_text=True)
    return doc, page


def span_over_tokens(page: CanonicalPage, start_token: int, end_token: int) -> tuple[int, int] | None:
    """The character span covering a token range's non-HTML tokens, or None
    when the range holds none (an empty block)."""
    kept = [page.token_spans[i] for i in range(start_token, end_token) if page.token_spans[i] is not None]
    if not kept:
        return None
    return kept[0][0], kept[-1][1]


# --- annotations ----------------------------------------------------------


@dataclass(frozen=True)
class NqExample:
    """One dev example's classification and raw annotation spans."""

    question_id: str
    question_text: str
    tokens: list[str]
    is_html: list[bool]
    long_answers: tuple[tuple[int, int], ...]  # per annotator, (-1, -1) when none
    short_answers: tuple[tuple[tuple[int, int], ...], ...]  # per annotator
    yes_no: tuple[int, ...]  # per annotator: -1 none, 0 no, 1 yes
    title: str = ""  # the page's own title from the dataset

    @property
    def n_long(self) -> int:
        return sum(1 for s, _ in self.long_answers if s >= 0)

    @property
    def n_short(self) -> int:
        return sum(1 for shorts, yes_no in zip(self.short_answers, self.yes_no, strict=True) if shorts or yes_no >= 0)

    @property
    def n_paragraph(self) -> int:
        return sum(1 for s, _ in self.long_answers if s >= 0 and self.tokens[s] == "<P>")

    @property
    def eligible(self) -> bool:
        """Kept when >= 2 of 5 annotators gave a long answer and at least
        one of them is a paragraph (<P>): tables and lists are excluded."""
        return self.n_long >= LONG_ANSWER_MIN_ANNOTATORS and self.n_paragraph >= 1

    @property
    def query_type(self) -> str:
        """Short answer means precise, long-answer-only means context."""
        return PRECISE if self.n_short >= SHORT_ANSWER_MIN_ANNOTATORS else CONTEXT


def _normalise(raw: dict) -> NqExample:
    """One parquet row (struct-of-lists) to an NqExample."""
    ann = raw["annotations"]
    n = len(ann["id"])
    short_answers: list[tuple[tuple[int, int], ...]] = []
    for j in range(n):
        sa = ann["short_answers"][j] or {}
        short_answers.append(tuple(zip(sa.get("start_token", []), sa.get("end_token", []), strict=True)))
    return NqExample(
        question_id=raw["id"],
        question_text=raw["question"]["text"],
        tokens=raw["document"]["tokens"]["token"],
        is_html=raw["document"]["tokens"]["is_html"],
        long_answers=tuple((la["start_token"], la["end_token"]) for la in ann["long_answer"]),
        short_answers=tuple(short_answers),
        yes_no=tuple(ann["yes_no_answer"]),
        title=raw["document"].get("title") or "",
    )


NQ_COLUMNS = [
    "id",
    "question.text",
    "document.title",
    "document.tokens.token",
    "document.tokens.is_html",
    "annotations",
]


def iter_examples(shard_paths: list[Path], batch_size: int = 64) -> Iterator[NqExample]:
    """Stream the dev config's examples shard by shard, batch by batch."""
    for shard_path in shard_paths:
        parquet = pq.ParquetFile(shard_path)
        for batch in parquet.iter_batches(batch_size=batch_size, columns=NQ_COLUMNS):
            rows = batch.to_pydict()
            for i in range(len(rows["id"])):
                yield _normalise(
                    {
                        "id": rows["id"][i],
                        "question": rows["question"][i],
                        "document": rows["document"][i],
                        "annotations": rows["annotations"][i],
                    }
                )


# --- the subset -----------------------------------------------------------


@dataclass(frozen=True)
class NqSplit:
    split: str
    documents: tuple[Document, ...]
    questions: tuple[Question, ...]
    dataset_hash: str
    evidence_counts: dict[str, int]
    excluded: tuple = ()
    dataset: str = "nq"
    subset_size: int = 0
    subset_hash: str = ""


def subset_ids_path(root: Path) -> Path:
    return root / SUBSET_RELATIVE_PATH


def selection_key(seed: int, question_id: str) -> str:
    return hashlib.sha256(f"{seed}:{question_id}".encode()).hexdigest()


def select_subset(short_ids: list[str], long_only_ids: list[str], seed: int, per_type: int) -> dict[str, list[str]]:
    """Pick `per_type` ids of each query type by seeded sha256 ranking.

    Ranking question ids by sha256(f"{seed}:{id}") makes the subset a pure
    function of the data, the seed and the per-type count, whatever the
    shard order or the Python version.
    """
    out: dict[str, list[str]] = {}
    for name, ids in (("short", short_ids), ("long_only", long_only_ids)):
        if len(ids) < per_type:
            raise ValueError(
                f"only {len(ids)} eligible {name} questions in the dev config; the planned subset needs {per_type}"
            )
        ranked = sorted(ids, key=lambda qid: (selection_key(seed, qid), qid))
        out[name] = sorted(ranked[:per_type])
    return out


def sample_subset(shard_paths: list[Path], seed: int, per_type: int, out_path: Path) -> dict[str, int]:
    """Stream the dev config, classify every question and write the subset
    id list. Returns the sampling funnel counts."""
    funnel = {
        "examples": 0,
        "long_answer_agreement": 0,
        "paragraph_eligible": 0,
        "eligible_short": 0,
        "eligible_long_only": 0,
        "sampled_short": 0,
        "sampled_long_only": 0,
    }
    short_ids: list[str] = []
    long_only_ids: list[str] = []
    seen: set[str] = set()
    for example in iter_examples(shard_paths):
        if example.question_id in seen:
            raise ValueError(f"duplicate question id in the dev config: {example.question_id}")
        seen.add(example.question_id)
        funnel["examples"] += 1
        if example.n_long < LONG_ANSWER_MIN_ANNOTATORS:
            continue
        funnel["long_answer_agreement"] += 1
        if not example.eligible:
            continue
        funnel["paragraph_eligible"] += 1
        if example.query_type == PRECISE:
            funnel["eligible_short"] += 1
            short_ids.append(example.question_id)
        else:
            funnel["eligible_long_only"] += 1
            long_only_ids.append(example.question_id)

    subset = select_subset(short_ids, long_only_ids, seed, per_type)
    funnel["sampled_short"] = len(subset["short"])
    funnel["sampled_long_only"] = len(subset["long_only"])
    ids = sorted(subset["short"] + subset["long_only"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join([f"# seed={seed} per_type={per_type}", *ids]) + "\n", encoding="utf-8")
    return funnel


def read_subset_ids(path: Path) -> tuple[str, ...]:
    """Read the committed id list, skipping comment lines."""
    ids = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    ids = [i for i in ids if i and not i.startswith("#")]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate question id in {path}")
    if not ids:
        raise ValueError(f"empty subset id list: {path}")
    return tuple(sorted(ids))


def load_nq(paths, split: str = NQ_CONFIG) -> NqSplit:
    """Load the committed subset: canonical pages, labelled spans, types.

    The collection is the subset's pages. Every annotator whose long
    answer is a `<P>` paragraph contributes that paragraph as its
    labelled span; short-answer spans are kept per annotator for R6.
    Each question also carries reference answers for the reader stage
    (never read by retrieval): precise questions keep every annotator's
    short-answer texts and "Yes"/"No" answers, context questions the
    long-answer paragraph of each annotator that gave one.
    """
    shard_paths = ensure_nq_shards(paths.data)
    ids_path = subset_ids_path(paths.root)
    if not ids_path.is_file():
        raise FileNotFoundError(f"missing subset id list {ids_path}; run `uv run rag sample` first")
    ids = read_subset_ids(ids_path)
    wanted = set(ids)

    documents: dict[str, Document] = {}
    questions: list[Question] = []
    evidence_counts = {
        "long_answer_paragraph": 0,
        "short_answer_span": 0,
        "reference_short_span": 0,
        "reference_yes_no": 0,
        "reference_long_answer": 0,
    }
    for example in iter_examples(shard_paths):
        if example.question_id not in wanted:
            continue
        if example.question_id in documents:
            raise ValueError(f"duplicate question id in the dev config: {example.question_id}")
        doc, page = page_document(example.question_id, example.tokens, example.is_html, title=example.title)
        source_hash = doc.source_hash

        annotators: list[tuple[LabelledSpan, ...]] = []
        short_annotators: list[tuple[LabelledSpan, ...]] = []
        references: list[str] = []
        for (start, end), shorts, yes_no in zip(
            example.long_answers, example.short_answers, example.yes_no, strict=True
        ):
            if start >= 0 and example.tokens[start] == "<P>":
                span = span_over_tokens(page, start, end)
                if span is not None:
                    annotators.append(
                        (
                            LabelledSpan(
                                doc_id=doc.doc_id,
                                start=span[0],
                                end=span[1],
                                quote=doc.text[span[0] : span[1]],
                                source_hash=source_hash,
                            ),
                        )
                    )
                    evidence_counts["long_answer_paragraph"] += 1
                    if example.query_type == CONTEXT:
                        references.append(doc.text[span[0] : span[1]])
                        evidence_counts["reference_long_answer"] += 1
            kept_shorts: list[LabelledSpan] = []
            for s_start, s_end in shorts:
                span = span_over_tokens(page, s_start, s_end)
                if span is not None:
                    kept_shorts.append(
                        LabelledSpan(
                            doc_id=doc.doc_id,
                            start=span[0],
                            end=span[1],
                            quote=doc.text[span[0] : span[1]],
                            source_hash=source_hash,
                        )
                    )
            if kept_shorts:
                deduped = tuple(sorted(set(kept_shorts), key=lambda s: (s.start, s.end)))
                short_annotators.append(deduped)
                evidence_counts["short_answer_span"] += len(deduped)
            else:
                deduped = ()
            if example.query_type == PRECISE:
                references.extend(span.quote for span in deduped)
                evidence_counts["reference_short_span"] += len(deduped)
                if yes_no >= 0:
                    references.append("Yes" if yes_no == 1 else "No")
                    evidence_counts["reference_yes_no"] += 1

        if not annotators:
            raise ValueError(f"subset question {example.question_id} has no paragraph long answer")
        questions.append(
            Question(
                question_id=example.question_id,
                doc_id=doc.doc_id,
                split=split,
                text=example.question_text,
                annotators=tuple(annotators),
                query_type=example.query_type,
                short_annotators=tuple(short_annotators),
                references=tuple(references),
            )
        )
        documents[doc.doc_id] = doc

    missing = wanted - set(documents)
    if missing:
        raise ValueError(f"subset question id(s) not in the dev config: {sorted(missing)[:5]}")

    return NqSplit(
        split=split,
        documents=tuple(documents[qid] for qid in sorted(documents)),
        questions=tuple(questions),
        dataset_hash=nq_dataset_hash(shard_paths),
        evidence_counts=evidence_counts,
        dataset="nq",
        subset_size=len(ids),
        subset_hash=hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
    )
