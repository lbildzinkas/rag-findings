# rag-findings

**The question:** should a retrieval system index documents cut several ways and route each question to the cut that suits it?

**The answer: yes, build the router in v2.** A perfect per-question router would raise retrieval recall by about +0.13 over the best single chunking, for both embedders, with 95% confidence intervals well above the +0.05 bar fixed before the experiment ran. But the router has to learn from each question's own text: knowing only whether a question is "precise" or "context" gains nothing.

Full write-up, with every table and the method: [RAG chunking v1 results](chunking/2026-10-14-v1-results.md) (2026-10-14).

## v2 so far: routing or better indexing?

**The question:** does the headroom v1 found come from routing each question between chunkings, or from indexing one chunking better?

**The answer so far (provisional): the cheapest indexing change clears the bar.** Indexing section-aware chunks with the dataset's own document and section titles - free, no language model - is the one contender that beats section-aware where v2 judges: +0.0228 pooled retrieval recall with a 95% CI excluding 0 ([R17](results/qasper/r17-v2-titles.md)). The label-free routers, late chunking and contextual chunks all score below section-aware, so none of them reaches the bar fixed before any v2 run ([ADR 0008](docs/adr/0008-pre-register-v2s-success-bar-and-tie-break.md)): at least +0.02 retrieval recall over section-aware. The retrieval results below are final. The answer-accuracy stage ([#26](https://github.com/lbildzinkas/rag-findings/issues/26)) reads section-aware, the oracle router and no retrieval with a local reader ([R14](results/v2/r14-answers.md), checked by a model grader in [R15](results/v2/r15-grader.md)); the formal verdict against the bar with its confidence intervals ([R16](results/v2/r16-verdict.md), [#27](https://github.com/lbildzinkas/rag-findings/issues/27)) confirms section-aware-titles as the only contender that passes; the v2 write-up ([#28](https://github.com/lbildzinkas/rag-findings/issues/28)) has not run yet.

The contenders use no question labels:

- **Search-all routing:** search all seven chunkings' indexes at once, fuse the lists and rerank the merged top 50.
- **Confidence routing:** per question, use the chunking whose top reranked chunk scores highest.
- **Late chunking (late-128, late-256):** fixed-128's and fixed-256's chunks, each embedded from the token embeddings of its whole document instead of on its own.
- **Contextual chunks (contextual-256):** fixed-256's chunks, each with a short context prefix written by a local model; the prefix is used for search only, and the reader gets the chunk text.
- **Section-aware chunks with titles (section-aware-titles):** section-aware's chunks, each indexed with the dataset's own document and section title in front, for search only; no language model is involved.

Budget view (as many reranked whole chunks as fit the budget, at most 20 per question), production line with nomic-embed-text-v1.5, 1024-token budget, QASPER and Natural Questions pooled (3,197 questions):

| setup | retrieval recall | difference from section-aware | table |
|---|---|---|---|
| Section-aware chunks with titles (section-aware-titles) | 0.4497 | +0.0228 | [R17](results/qasper/r17-v2-titles.md) |
| Section-aware (the best single chunking) | 0.4269 | | [R7](results/routing/r7-v2-budget-view.md) |
| Contextual chunks (contextual-256) | 0.4089 | -0.0179 | [R13](results/qasper/r13-v2-contextual.md) |
| Search-all routing | 0.4018 | -0.0250 | [R11](results/pooled/r11-v2-routers.md) |
| Confidence routing | 0.3847 | -0.0422 | [R11](results/pooled/r11-v2-routers.md) |
| Late chunking on fixed-256 (late-256) | 0.3688 | -0.0581 | [R12](results/qasper/r12-v2-late.md) |
| Late chunking on fixed-128 (late-128) | 0.3582 | -0.0686 | [R12](results/qasper/r12-v2-late.md) |
| Oracle router (a ceiling) [95% CI] | 0.5641 | +0.1373 [+0.1263, +0.1485] | [R7](results/routing/r7-v2-budget-view.md) |

*Differences are taken between unrounded means, as R7's headroom is, so a few differ in the last digit from the rounded recalls; every contender's CI is in the formal verdict, [R16](results/v2/r16-verdict.md); section-aware-titles' pre-registered bar verdict is also rendered in R17. R12, R13 and R17 carry the pooled columns in both their QASPER and Natural Questions tables.*

What the results say:

- **The dataset's own titles, used for search only, clear the bar.** Indexing section-aware chunks with their document and section title in front - a QASPER chunk reads `Paper: <paper title>. Section: <section name>.`, and a Natural Questions page's header adds the page title because its chunks already open with their heading - lifts pooled recall by +0.0228 [+0.0128, +0.0331] at 1024 tokens, on both datasets (QASPER +0.0168, Natural Questions +0.0361), and the gain grows with the budget (+0.0251 pooled at 8192 tokens). No language model is involved; the reader and the recall score see the original chunk text, and the budget counts only that text.

- **Context prefixes lift fixed-256 by +0.0403, not past section-aware.** contextual-256 gains on both datasets (QASPER +0.0345, Natural Questions +0.0530) but stays 0.0179 below section-aware. Showing the prefix to the reader as well, counting its tokens against the budget (**contextual-256-prefixed**), gives no retrieval gain: 0.3685, level with plain fixed-256 (0.3686).
- **The label-free routers lose recall rather than capture the oracle's headroom.** Search-all routing trails section-aware by 0.0250 and confidence routing by 0.0422, while the oracle router sits +0.1373 above it. Confidence routing picks fixed-64 most often (0.2856 of questions) and section-aware for 0.2468.
- **Late chunking barely changes small chunks.** Against the same fixed chunks embedded on their own, late-128 moves pooled recall by +0.0064 and late-256 by +0.0002: slightly better on Natural Questions (+0.0290 and +0.0082), slightly worse on QASPER (-0.0039 and -0.0035).

**How section-aware chunking works.** It cuts each document at its own sections: a QASPER paper's named sections (the abstract is one), a Natural Questions page at its H1-H6 headings. Each section becomes one chunk of up to 512 tokens; a longer section is split at paragraph boundaries into runs of whole paragraphs, and a single paragraph longer than 512 tokens is cut into 512-token windows. Chunks therefore follow the document's units of meaning instead of a fixed window. QASPER chunks do not include the section title text; on Natural Questions pages the heading text is part of the page text and opens its section's first chunk. The code is `section_aware` in [`src/rag/chunking.py`](src/rag/chunking.py); the vocabulary is in [`CONTEXT.md`](CONTEXT.md).

Limitations of v2 so far:

- Every v2 number above is retrieval recall. Answers are measured for three setups only (section-aware, the oracle router and no retrieval) with a local Qwen3-8B as the reader on a 1,000-question sample ([R14](results/v2/r14-answers.md); [ADR 0009](docs/adr/0009-measure-answer-accuracy-with-glm-5-3-flash-as-the-reader.md) and its 2026-10-17 amendment), not with GLM 5.3 Flash as first planned.
- Some Natural Questions pages hold byte-identical chunks at the same character span, which the reranker scores exactly equally, so tie order decides which page's copy is packed. Against v1 this moved three v2-baseline cells by one question each, within ±0.001 ([note](results/nq/v2-baseline-regression.md)).
- Late chunking pools each chunk from the token embeddings that start inside it, leaving the document prefix and special tokens out, so a window holding a single chunk reproduces that chunk's own vector to a cosine of 0.999798 at worst for late-128 (just under the 0.9999 check) and 0.999946 for late-256 ([check](results/late-single-chunk-cosine.md)). A document longer than 8192 tokens is read in several windows, so each chunk sees only its own window.
- The reranker orders only the top 30 of each chunking's list (search-all routing: the fused top 50). At 1024 tokens section-aware packs chunks from past rank 30, in fused order, for 0.5831 of QASPER questions and 0.8540 of Natural Questions ones (R5, [QASPER](results/qasper/r5-v2-baseline.md), [Natural Questions](results/nq/r5-v2-baseline.md)), so a deeper rerank could shift the margins either way; reranked to depth 50, section-aware gains +0.0051 and section-aware-titles' margin narrows from +0.0228 to +0.0209 [+0.0108, +0.0311], still clearing the bar's retrieval checks ([R16](results/v2/r16-verdict.md)).
- nomic-embed-text-v1.5 only, one run per setup, two English sources.

## What was measured

A **chunking** is one way of cutting documents into retrievable pieces. Every chunking gets the same **token budget**: the amount of retrieved text, counted in tokens, that a language model may read for one question, filled with whole chunks. The score is **retrieval recall**: the share of the text that answers the question (its labelled spans) that ends up inside that budget. A recall of 0.4256 means 42.56% of the answer text was retrieved.

- **Data:** 2,197 QASPER questions about 684 NLP research papers, and a 1,000-question subset of Natural Questions (questions from search logs, answered from Wikipedia pages).
- **Seven chunkings:** fixed windows of 64, 128, 256, 512 and 1024 tokens (**fixed-64** ... **fixed-1024**); **section-aware** (one chunk per document section, split at paragraph boundaries above 512 tokens); **small-to-big** (match small 128-token pieces, then return the whole section around a match when it still fits the budget).
- **Seven budgets** from 128 to 8192 tokens.
- **Search:** the **production line**, keyword (BM25) and vector search fused into one ranking, then a reranker reorders the top 30. It runs once per embedder (bge-small-en-v1.5 and nomic-embed-text-v1.5), with at most 8 chunks per question (the **production view**) and search over the whole collection.

## The decision in four numbers

Production line, production view, 1024-token budget, QASPER and Natural Questions pooled:

| | bge-small | nomic |
|---|---|---|
| Best single chunking (section-aware), retrieval recall | 0.4256 | 0.4262 |
| Perfect per-question router (an upper bound), retrieval recall | 0.5552 | 0.5575 |
| **Routing headroom** (router minus best single chunking) [95% CI] | **+0.1295 [+0.1187, +0.1402]** | **+0.1313 [+0.1204, +0.1425]** |
| Bar fixed in advance ([ADR 0002](docs/adr/0002-build-a-query-router-only-if-the-routing-headroom-threshold-is-met.md)): headroom of at least this, CI excluding 0 | +0.05, cleared | +0.05, cleared |

The perfect router picks the best chunking for each question in hindsight, so it is a ceiling, not what a real router will reach.

## Finding 1: the best single chunking depends on the budget

![Retrieval recall by token budget for each chunking: QASPER and NQ, production and fair view](chunking/figures/v1-recall-vs-budget.svg)

*Recall per budget for each chunking (production line, bge-small); in the capped view the small fixed windows flatten once 8 chunks fill less than the budget.*

- **512 tokens or less:** small-to-big wins (on Natural Questions alone, section-aware already edges ahead at 512 tokens).
- **1024 and 2048 tokens:** section-aware wins on both datasets and with both embedders. At 1024 tokens it retrieves 0.4256 pooled (bge-small) and is the best chunking in 0.9997 of the bootstrap resamples; small-to-big trails it by -0.0174 [-0.0277, -0.0070].
- **4096 and 8192 tokens:** with the 8-chunk cap the big fixed windows win (fixed-512, then fixed-1024), only because the cap stops smaller chunks from filling the room. Without the cap (the **fair view**) section-aware stays best from 1024 tokens up with bge-small; with nomic, fixed-1024 edges ahead at 8192.

## Finding 2: the kind of question does not pick the chunk size

![Interaction of each chunking against fixed-128 at 1024 tokens, QASPER and NQ, with 95% CIs](chunking/figures/v1-interaction.svg)

*How much more each chunking gains over fixed-128 on context questions than on precise ones, at 1024 tokens; most CIs cross 0.*

A **precise** question is answered by one passage, a **context** question by several. The test: do bigger chunks help context questions more than precise ones?

- QASPER repeats an earlier pilot: fixed-512 against fixed-128 gives +0.0237 [-0.0096, +0.0568], a small effect whose CI spans 0. Natural Questions points the other way: -0.0647 [-0.1178, -0.0122]. Pooled, it disappears: +0.0106 [-0.0190, +0.0410].
- Section-aware is the best chunking for precise and for context questions alike, so a router that knew each question's type in hindsight would gain +0.0000 over section-aware, on every dataset and with both embedders.

## Finding 3: a router is worth building

![Routing headroom per budget with CIs for both embedders, above the +0.05 gate threshold](chunking/figures/v1-routing-headroom.svg)

*Routing headroom per budget, pooled, production line, production view; every CI sits above the +0.05 bar.*

- The headroom holds on each dataset alone at 1024 tokens (QASPER +0.1273, Natural Questions +0.1345 with bge-small), at every budget (largest at 512 tokens, +0.1601), and for every search variant, keyword-only included.
- It comes from question-by-question differences, not from the query type: on many QASPER questions no chunking finds the paper at all, and on the rest the best chunking varies per question in the same way for precise and context questions.

## What each part of the search adds

At 1024 tokens, production view, comparing each pipeline's best single chunking (differences between means; no CI is computed for them):

- **The reranker adds the most:** +0.0849 retrieval recall pooled with bge-small (+0.0764 with nomic) over hybrid search without it, on both datasets.
- **Hybrid fusion helps QASPER and hurts Natural Questions before the reranker:** fusing BM25 with vector search beats vector search alone on QASPER (+0.0366, bge-small) but costs -0.0532 (bge-small) and -0.0858 (nomic) on Natural Questions, where BM25 is much weaker.
- **The winner barely moves:** section-aware or small-to-big is the best chunking for every pipeline, embedder and dataset.

## What to use today, and what v2 does

**Use today:** section-aware chunks with a token budget around 1024 tokens, hybrid search plus the reranker over the top 30. Either embedder works; their recalls are within a few thousandths.

**v2:** asks whether the headroom v1 found comes from routing between chunkings or from indexing one chunking better, measured end to end through a reader's answers. Label-free contenders - search-all routing, confidence routing, late chunking, contextual chunks and section-aware chunks indexed with their titles - run against section-aware with the oracle router as the ceiling, on nomic-embed-text-v1.5 and judged in the budget view. The success bar and the tie-break between contenders were fixed before any run, and section-aware stays if nothing clears them. On retrieval one contender beats section-aware - the same chunks indexed with the dataset's own document and section titles, which clears the pre-registered bar ([v2 so far](#v2-so-far-routing-or-better-indexing)) - so the advice above stands with that header in front of the chunks; answer accuracy is measured with a local Qwen3-8B as the reader on section-aware, the oracle router and no retrieval ([R14](results/v2/r14-answers.md), [R15](results/v2/r15-grader.md)), and the formal verdict is [R16](results/v2/r16-verdict.md). The settled decisions are recorded in [ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md) through [ADR 0009](docs/adr/0009-measure-answer-accuracy-with-glm-5-3-flash-as-the-reader.md).

## Limitations

- v1 measured retrieval only; v2 measures answers for three setups (section-aware, the oracle router, no retrieval) with one local reader ([R14](results/v2/r14-answers.md)), never per contender.
- The perfect router picks in hindsight from seven chunkings, so part of the headroom is noise.
- Two English sources (NLP papers and Wikipedia), one run per setup, one reranker depth (30), one fusion constant (k = 60).
- The reranker orders only the top 30; section-aware often packs chunks from past rank 30, so a deeper rerank could shift its margin either way.
- bge-small reads only 512 tokens and embeds longer chunks truncated; nomic reads 8192 and gives recalls within a few thousandths, so truncation moves no conclusion.
- The tables over one combined index of both datasets are BM25-only; the router decision pools the two per-dataset runs instead.

The write-up's [limitations section](chunking/2026-10-14-v1-results.md#5-limitations) has the details.

## Repository map

- [`chunking/2026-10-14-v1-results.md`](chunking/2026-10-14-v1-results.md): the v1 results write-up; its figures are in [`chunking/figures/`](chunking/figures).
- [`chunking/2026-10-10-chunk-size-vs-query-type.md`](chunking/2026-10-10-chunk-size-vs-query-type.md): the research report that motivated v1, covering the literature on chunk size versus query type, budget-matched evaluation, and a QASPER pilot.
- [`results/`](results): the committed result tables (`qasper/`, `nq/`, `pooled/`, `routing/`, `v2/`) and the context-prefix manifest (`prefixes/`); every number above comes from the tables.
- [`configs/`](configs): the run configurations, the committed context-prefix and grader prompts, and the committed id lists (the Natural Questions subset, the v2 reader sample).
- [`CONTEXT.md`](CONTEXT.md): the experiment's vocabulary.
- [`docs/adr`](docs/adr): the settled design decisions. [ADR 0004](docs/adr/0004-run-v1-on-the-settled-question-sets-and-chunking-grid-superseding-the-reports-proposal.md) supersedes the chunking grid proposed in the research report.
- [`src/rag`](src/rag) and [`tests`](tests): the experiment code and its unit tests.

## Setup

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```sh
uv run rag setup
```

`setup` downloads the QASPER dev and test tarballs (about 15 MB) and the Natural Questions dev config (seven parquet shards, about 1.34 GB; never the default config, whose train split is 57 GB) into the git-ignored `data/` directory and verifies their sha256 checksums. It also downloads the v1 models' pinned revisions (safetensors weights, tokenizers and configs only, about 1.2 GB) into the git-ignored `data/hf-cache/`; runs then load them offline (`--no-models` skips them).

Unit tests run offline on small committed fixtures: `uv run pytest`.

## Reproduce the results

### Re-render the write-up from the committed tables

The write-up's tables and figures are regenerated from `results/` without running any retrieval:

```sh
uv run rag writeup          # re-render the write-up's tables and figures
uv run rag writeup --check  # change nothing; fail if the write-up or a figure differs from results/
```

### Tracer experiment

A thin end-to-end retrieval eval: QASPER v0.3 to canonical documents to labelled spans to fixed 256-token chunks to BM25 retrieval to a 1024-token budget (production view), scored as retrieval recall and precision against the labelled spans.

```sh
uv run rag setup && uv run rag run configs/tracer.yaml
```

Then open `results/qasper/r1-tracer.md`. `run` writes per-question results and a run manifest to the git-ignored `runs/` directory (namespaced per dataset label) and regenerates the committed result table under `results/`.

### Grid: the production line and its ablations

Every chunking at every token budget on QASPER (and, with `configs/nq-grid.yaml`, on the Natural Questions subset below): fixed windows of 64, 128, 256, 512 and 1024 tokens (Chonkie's token chunker, cl100k_base, no overlap), section-aware chunks (one per section, split at paragraph boundaries above 512 tokens) and small-to-big (128-token children returning their section-aware parent when it fits the remaining budget); budgets of 128 to 8192 tokens; the production view (top-N cap 8, with a cap-5 side table) and the fair view (no cap); search across the whole collection and within the question's own document.

Each cell runs under four retrieval pipelines, two of them per embedder (bge-small-en-v1.5, 512-token input; nomic-embed-text-v1.5, 8192-token input with its `search_document:` / `search_query:` prefixes, which never count toward a budget):

- the production line (`hybrid-rerank`): BM25 and vector search fused by reciprocal rank fusion (k = 60), then gte-reranker-modernbert-base reorders the fused top 30; after them the list continues in fused order (the unreranked tail), deep enough to fill the fair view at 8192 tokens;
- the ablations: hybrid without the reranker, vector search only, and BM25 only.

Small-to-big matches, and the reranker scores, the 128-token children. Vector search is exact (cosine) over a LanceDB table per chunking and embedder, next to the full-text index. Chunk embeddings (keyed by model and chunk span) and reranker scores (keyed by question and chunk) are cached under `data/cache/`, so both scopes and both embedders share them and a re-run does no reranker passes.

```sh
uv run rag setup && uv run rag run configs/grid.yaml --sample 50   # a seeded 50-paper sample, minutes
uv run rag run configs/grid.yaml                                   # the full run, several hours on an M4 Max
```

A `--sample` run writes everything, its tables included, under `runs/qasper/grid-sample<N>/` and leaves `results/` untouched. The full run writes per-question results as Parquet under `runs/<dataset>/<run_name>/` (git-ignored; one row per question, pipeline, embedder, chunking, search scope, view, cap and budget, plus fixed-k rows and each question's query type), a manifest with the wall time, the truncation shares, the reranker's pass counts and the embedding cache counts, and regenerates the committed tables, each with one block per pipeline and embedder, the production line first:

- `results/qasper/r2-grid.md` (R2): retrieval recall and precision per chunking and budget, production and fair view side by side, plus the cap-5 side table;
- `results/qasper/r3-grid.md` (R3): retrieval recall per query type (precise, context; mixed counted but left out of the contrast) and the difference between types;
- `results/qasper/r4-grid.md` (R4): fixed-k hit@k and recall@k at k = 1, 5 and 10, for comparison with the literature only;
- `results/qasper/r2w-grid.md` (R2w): R2 with search within the question's own document;
- `results/qasper/r5-grid.md` (R5): pipeline x embedder x chunking at each budget, with each chunking's share of chunks longer than the embedder's input limit (‡, embedded truncated) and how often packing reached the unreranked tail.

"n/a" marks a fixed chunking whose chunk is bigger than the budget (R5 gives every n/a its reason); "†" marks production-view cells where the top-N cap, not the budget, limits the retrieved text for at least half of the questions; "§" marks production-line cells where packing used the unreranked tail. A BM25-only grid (`pipeline: bm25`) still runs in a few minutes without any model.

### Natural Questions subset

A second dataset, so the chunk size × query type interaction and the routing headroom are not QASPER-only. `sample` picks 1,000 questions from the NQ dev config - 500 with a short answer (precise) and 500 long-answer-only (context) - from the questions where at least 2 of 5 annotators gave a long answer and at least one of those long answers is a paragraph (`<P>`); tables and lists are excluded. The selection ranks question ids by seeded sha256, and the resulting id list is committed as `configs/nq-subset.txt` (ids only, never dataset text, so the CC BY-SA 3.0 ShareAlike term never attaches to the repository) and reproduces the same subset.

```sh
uv run rag sample && uv run rag run configs/nq-tracer.yaml && uv run rag run configs/nq-grid.yaml
```

The canonical page text is the page's non-HTML tokens (tokens joined with spaces inside a paragraph, paragraphs joined with blank lines), with a map from token offsets to character offsets; the labelled span of every annotator whose long answer is a `<P>` paragraph is that paragraph, and short-answer spans are kept per annotator. Sections come from the page's heading tags, so section-aware chunks and small-to-big parents follow the page's own structure. The collection is the subset's 1,000 pages; whole-collection search runs over all of them and within-document search over the question's own page.

The NQ tracer and grid write the same R1-R5 and R2w tables under `results/nq/`, plus `results/nq/r6-grid.md` (R6): short-answer span recall by chunking and budget on the NQ precise questions that have a short-answer span, the same packing as R2 scored against the short-answer spans instead of the long-answer paragraph.

### Pooled runs

`configs/pooled-tracer.yaml` and `configs/pooled-grid.yaml` load QASPER (dev and test) and the NQ subset together: one collection, one retrieval run over both, and the same tables under `results/pooled/` (BM25 only: the production line and its ablations run per dataset), with each dataset's n kept visible (the Questions section of every pooled table breaks the query-type counts down per dataset).

```sh
uv run rag run configs/pooled-tracer.yaml && uv run rag run configs/pooled-grid.yaml
```

### Routing headroom

The analysis that decides whether v2 builds a query router, read from the grid runs' per-question results (no retrieval runs). Per dataset (and pooled when there are several), pipeline, embedder, budget and view: the best single chunking (highest mean retrieval recall), the oracle router (per question, the chunking with the highest recall; ties to the smaller chunk) and the routing headroom between them. A paired bootstrap over documents (10,000 resamples, fixed seed) re-selects the best single chunking inside every resample and gives 95% CIs at the pre-registered 1024-token budget, Holm-adjusted at the other budgets.

```sh
uv run rag run configs/grid.yaml && uv run rag run configs/nq-grid.yaml && uv run rag headroom configs/headroom.yaml
```

It takes seconds and regenerates the committed tables under `results/routing/`, byte-identically for the same seed and inputs:

- `r7-headroom.md` (R7): the router gate verdict per embedder (production line, production view, 1024 tokens, pooled QASPER + NQ: build the router if either embedder's headroom is at least +0.05 recall with a CI excluding 0), the routing headroom, a query-type oracle row (the best chunking per labelled query type; secondary, not part of the gate) and every chunking's difference from the best single chunking;
- `r8-headroom.md` (R8): the chunk size x query type interaction [Δ(chunking − fixed-128) | context] − [Δ(chunking − fixed-128) | precise];
- `r9-headroom.md` (R9): which chunking the oracle router picks, by query type, at 1024 tokens.

The committed tables read the QASPER and Natural Questions grid runs (`runs: [qasper/grid, nq/grid]`), pooled per question across the two runs, each dataset's documents resampled as its own clusters.

### The v2 runs, in order

Each stage reads the runs before it. The retrieval runs use the production line with nomic only and collection search, after `rag setup` and `rag sample`:

```sh
uv run rag run configs/v2/qasper-baseline.yaml && uv run rag run configs/v2/nq-baseline.yaml
uv run rag headroom configs/v2/budget-view.yaml
uv run rag run configs/v2/qasper-routers.yaml && uv run rag run configs/v2/nq-routers.yaml
uv run rag routers configs/v2/routers.yaml
uv run rag run configs/v2/qasper-late.yaml && uv run rag run configs/v2/nq-late.yaml
uv run rag contenders configs/v2/late.yaml
uv run --group prefixes rag prefixes configs/prefixes.yaml
uv run rag run configs/v2/qasper-contextual.yaml && uv run rag run configs/v2/nq-contextual.yaml
uv run rag contenders configs/v2/contextual.yaml
uv run rag run configs/v2/qasper-titles.yaml && uv run rag run configs/v2/nq-titles.yaml
uv run rag contenders configs/v2/titles.yaml
uv run rag reader-sample --check
uv run rag answers configs/v2/answers.yaml --dry-run
uv run --group prefixes rag answers configs/v2/answers.yaml   # the reader run (macOS, Apple silicon)
uv run rag grade configs/v2/answers.yaml                      # the model-graded check
uv run rag run configs/v2/qasper-depth50.yaml && uv run rag run configs/v2/nq-depth50.yaml
uv run rag latency configs/v2/latency.yaml                    # the uncached query-path probe
uv run rag verdict configs/v2/verdict.yaml
```

The subsections below describe each stage.

### The v2 baseline and the budget view

v1's seven chunkings re-scored in the budget view ([ADR 0006](docs/adr/0006-make-the-budget-view-v2s-primary-view.md)) with nomic-embed-text-v1.5 ([ADR 0007](docs/adr/0007-use-nomic-embed-text-v1-5-as-v2s-primary-embedder.md)), and the oracle router ceiling recomputed under it before any contender ran. The baseline runs (`configs/v2/qasper-baseline.yaml`, `configs/v2/nq-baseline.yaml`, run name `v2-baseline`) write the R2-R6 tables under `results/qasper/` and `results/nq/` (`*-v2-baseline.md`, R6 on Natural Questions only) and export the packed spans of the budget view's 1024-token cell, which the reader stage's section-aware and oracle setups read. `headroom configs/v2/budget-view.yaml` reads both runs (no retrieval runs) and regenerates `results/routing/r7-v2-budget-view.md`, `r8-v2-budget-view.md` and `r9-v2-budget-view.md`: the best single chunking, the oracle router and the routing headroom with no gate verdict (the gate was v1's question), the chunk size x query type interaction, and the oracle router's picks by query type. The Natural Questions re-run matches the v1 grid's nomic production-line cells byte-for-byte except three cells, one question each; [`results/nq/v2-baseline-regression.md`](results/nq/v2-baseline-regression.md) traces them to tie order between byte-identical chunks on different pages.

### The v2 routers

The two label-free routers of [ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md), computed per question from the seven chunkings' rankings with no labels, over the v2 baseline's settings (production line, nomic, collection search). **Search-all routing** fuses the seven chunkings' hybrid lists by reciprocal rank fusion (k = 60) keyed by document and character span - identical text from two chunkings is one item - reranks the fused top 50 and packs by budget counting overlapping text once, small-to-big children keeping v1's parent rule. **Confidence routing** uses, per question, the chunking whose reranked top result scores highest (the top-1 reranker score of each chunking's reranked top 30), ties going to the smaller chunk, and records the pick per question. Both are scored over merged text: recall and precision count every retrieved token once, the union of the packed token ranges, so the single chunkings' scores are unchanged.

```sh
uv run rag run configs/v2/qasper-routers.yaml && uv run rag run configs/v2/nq-routers.yaml
uv run rag routers configs/v2/routers.yaml
```

The runs (`kind: routers`) write `routed.parquet` (one row per question x router x view x budget, the results' columns plus `picked_chunking`) and, for the exported budget-view 1024-token cell, `packed.parquet` under pipelines `search-all` and `confidence`, which the reader stage's search-all and confidence setups can still read (its config, since the ADR 0009 amendment, reads three setups). `rag routers` reads the routers runs next to the v2 baseline runs (no retrieval runs) and regenerates the committed `results/{qasper,nq,pooled}/r11-v2-routers.md` (R11) byte-identically for the same runs: recall and precision of both routers at every budget in the budget and production views, next to section-aware and the oracle router, and confidence routing's picks per chunking.

### Late chunking

The indexing contender of [ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md) (with [ADR 0007](docs/adr/0007-use-nomic-embed-text-v1-5-as-v2s-primary-embedder.md)): **late-128** and **late-256** keep fixed-128's and fixed-256's exact spans - BM25, packing, scoring and reranker scores are shared, only the vectors differ - but each chunk's vector is pooled from the token embeddings of the whole document instead of embedding the chunk alone. Each document, prefixed once with `search_document: `, is read in consecutive windows of whole 256-token blocks (the fixed-256 cuts, so every window holds whole chunks of both sizes) of at most 8192 nomic tokens, prefix and special tokens included, one forward pass per window serving both late chunkings; a chunk's vector is the normalized mean of the token embeddings that start inside it (the prefix and special tokens join no chunk) and is cached under the model key plus `#late-8192`, never mixing with the chunk-embedded vectors of the same spans. nomic is loaded with `rotary_scaling_factor=2`, the model card's setting for inputs past its 2048 trained positions; inputs up to 2048 tokens stay bit-identical, so the cached v1 vectors remain valid.

```sh
uv run rag run configs/v2/qasper-late.yaml && uv run rag run configs/v2/nq-late.yaml
uv run rag contenders configs/v2/late.yaml
```

The runs (production line, nomic, collection search, fixed-128, fixed-256, section-aware and the two late chunkings, all budgets, budget, production and fair views) write the R2-R6 tables under run name `v2-late` (R6 on Natural Questions only) and export the packed spans of the budget view's 1024-token cell, which the reader stage's late-128 and late-256 setups can still read (dropped from its config by the ADR 0009 amendment). `contenders` reads the two runs' per-question results (no retrieval runs) and regenerates the committed `results/{qasper,nq}/r12-v2-late.md` (R12) byte-identically: recall and precision of both late chunkings at every budget in the budget and production views, next to fixed-128, fixed-256 and section-aware, per dataset and pooled, plus each contender's difference from the fixed chunking with the same spans. A window holding a single chunk reproduces that chunk's independent vector to cosine >= 0.9999; the check runs once against the real model and is recorded in [`results/late-single-chunk-cosine.md`](results/late-single-chunk-cosine.md).

### Context prefixes (v2)

The index-time half of contextual chunks ([ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md)): a local model writes one short context prefix for every fixed-256 chunk of QASPER dev + test and the Natural Questions subset. It runs on Apple silicon only, through mlx-lm in the optional `prefixes` dependency group (tests use a fake writer).

```sh
uv run --group prefixes rag prefixes configs/prefixes.yaml --estimate 20   # 20 seeded documents per dataset, then the projected hours
uv run --group prefixes rag prefixes configs/prefixes.yaml                 # every chunk; about a day on an M4 Max
```

- **Model and prompt.** Qwen3-8B (4-bit MLX weights at a pinned revision) decodes greedily with thinking off, at most 120 new tokens per prefix. The prompt is the committed contextual-retrieval prompt [`configs/prefix-prompt.txt`](configs/prefix-prompt.txt), whose sha256 the config pins.
- **Document context.** A document of at most 8192 cl100k tokens is given whole. A longer one is cut into the fewest near-equal windows of whole chunks that fit, and each chunk gets the window that holds it. Each document or window is prefilled once, and its chunks are generated in batches of 6.
- **Store.** Prefixes go to the git-ignored `data/prefixes/prefixes.sqlite`, keyed by prefix model and revision, prompt hash, document source hash and chunk span. Each document commits as one transaction, so an interrupted run resumes at the next document and never rewrites a stored prefix.
- **Manifest.** The committed manifest [`results/prefixes/fixed-256-qwen3-8b.json`](results/prefixes) records the counts, the prefix-length distribution, the prefixes cut at 120 tokens, the wall time and a sha256 digest of the stored prefixes, never their text.

### Contextual chunks

The search-time half of contextual chunks ([ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md), [ADR 0009](docs/adr/0009-measure-answer-accuracy-with-glm-5-3-flash-as-the-reader.md)): **contextual-256** keeps fixed-256's exact spans, and each chunk's search text is its stored prefix, a blank line and the chunk text. The BM25 index reads the search text, nomic embeds `search_document: ` plus the search text, and the reranker scores (question, search text) pairs, because the reranker is part of search. Packing, scoring and the reader use the chunk text only, so the token budget counts only the chunk's tokens. The side variant **contextual-256-prefixed** ranks the same way, but its packing counts the cl100k tokens of the whole search text against the budget (those are also its retrieved tokens, precision's denominator), and its reader receives the search text; recall is still scored on the chunk's span.

A contextual chunking names its prefix set in the grid config (`prefixes: {model, revision, prompt_sha256}`, the set `configs/prefixes.yaml` wrote; `prefix_in_budget: true` for the side variant). Its vectors and reranker scores are cached under the model key plus `#ctx:<prefix model>@<revision>:<prompt sha256>`, never mixing with fixed-256's entries for the same spans, and the run fails before any search when a chunk has no prefix in that set.

```sh
uv run rag run configs/v2/qasper-contextual.yaml && uv run rag run configs/v2/nq-contextual.yaml
uv run rag contenders configs/v2/contextual.yaml
```

The runs (production line, nomic, collection search, fixed-256, section-aware and both contextual chunkings, all budgets, budget, production and fair views) write the R2-R6 tables under run name `v2-contextual` (R6 on Natural Questions only) and export the packed spans of the budget view's 1024-token cell for both variants, which the reader stage's contextual setups can still read (dropped from its config by the ADR 0009 amendment). `contenders` regenerates the committed `results/{qasper,nq}/r13-v2-contextual.md` (R13) byte-identically: recall and precision of both contextual chunkings at every budget in the budget and production views, next to fixed-256 and section-aware, per dataset and pooled, plus contextual-256's difference from fixed-256 and the side variant's from contextual-256.

### Section-aware chunks with titles

The cheapest form of context enrichment on the best single chunking ([ADR 0005](docs/adr/0005-compare-routing-against-indexing-with-label-free-contenders-only.md)): **section-aware-titles** keeps section-aware's exact spans, and each chunk's search text is its title header, a blank line and the chunk text - exactly a contextual chunk's prefix, written by no model. The header comes only from the dataset's own title and section fields: a QASPER chunk reads `Paper: <paper title>. Section: <section name>.` (the abstract is the section named `Abstract`; the section names are otherwise not part of a paper's canonical text), and a Natural Questions page's canonical text already opens every section with its heading, so its header adds only the page title, `Page: <page title>.`. The BM25 index, the vectors and the reranker pairs read the search text; packing, scoring and the reader use the chunk text only, so the budget counts only its tokens.

A section-aware chunking sets `titles: true` in the grid config. Its vectors and reranker scores are cached under the model key plus `#titles`, never mixing with the plain section-aware chunking's entries for the same spans, so the plain chunking's recall is reproduced exactly from the cache.

```sh
uv run rag run configs/v2/qasper-titles.yaml && uv run rag run configs/v2/nq-titles.yaml
uv run rag contenders configs/v2/titles.yaml
```

The runs (production line, nomic, collection search, section-aware and section-aware-titles, all budgets, budget, production and fair views) write the R2-R6 tables under run name `v2-titles` (R6 on Natural Questions only) and export the packed spans of the budget view's 1024-token cell. `contenders` regenerates the committed `results/{qasper,nq}/r17-v2-titles.md` (R17) byte-identically: recall and precision of the titled chunking at every budget in the budget and production views, next to section-aware, per dataset and pooled, its difference from section-aware, and the pre-registered bar verdict of [ADR 0008](docs/adr/0008-pre-register-v2s-success-bar-and-tie-break.md) - at least +0.02 pooled recall with a 95% CI from the paired, document-clustered bootstrap excluding 0 in the budget view at 1024 tokens, and no dataset alone below -0.01.

### Reader sample and the answers stage

The v2 reader stage (ADR 0009). `reader-sample` draws the 1,000-question reader sample - 500 QASPER questions filled by whole papers in seeded order (a paper that would overshoot is skipped), 250 precise and 250 context Natural Questions pages - and commits it as ids only (`configs/v2/reader-sample.txt`, reproducible from its seed; `--check` verifies the committed list against a fresh draw). The loaders also carry each question's reference answers (QASPER: each answering annotator's extractive spans joined with ", ", free-form answer, or "Yes"/"No"; NQ precise: the short-answer texts and yes/no answers; NQ context: the long-answer paragraph) - a field the retrieval path never reads.

```sh
uv run rag reader-sample --check   # verify the committed sample against a fresh draw
uv run rag answers configs/v2/answers.yaml --dry-run
uv run --group prefixes rag answers configs/v2/answers.yaml   # the reader run (macOS, Apple silicon)
uv run rag grade configs/v2/answers.yaml                      # the model-graded check
```

`answers --dry-run` assembles every reader setup from the runs' `packed.parquet` at the budget view's primary cell (1024 tokens, collection search, nomic). Since the 2026-10-17 amendment to ADR 0009 the config reads three setups: section-aware, the oracle router (per question, the chunking with the highest recall, ties to the smaller chunk) and the no-retrieval floor, which uses the closed-book variant of the prompt. The code still assembles the other setups (the routers, late and contextual chunks, whose prefix-in-budget variant is rendered as prefix, blank line and chunk text). The dry run renders the fixed reader prompt (whose template hash is recorded before any answer exists), reports prompt token counts per setup and dataset without calling a model, and fails when any prompt exceeds the budget plus the template. Setups whose packed spans are not on disk are reported as pending.

`answers` without `--dry-run` is the reader run: every prompt is answered by the local Qwen3-8B (4-bit MLX weights at the revision the context prefixes used, from the `prefixes` dependency group; thinking off in the chat template, greedy decoding, at most 256 new tokens, one prompt at a time) through a SQLite response cache, `data/cache/answers.sqlite`, which also keeps each call's latency and token counts. An interrupted run resumes free, and a warm re-run neither loads nor calls the model; setups that hand the reader the same chunks share one answer. Answers are scored with the datasets' standard metrics (answer F1 for QASPER, short-answer match with contains-a-reference as a secondary column for NQ precise, token F1 for NQ context, all after SQuAD-style normalisation). The run writes `runs/v2-answers/answers.parquet` (ids, hashes, scores and call records, never answer text), the committed manifest `results/v2/answers-manifest.json` (model id and revision, settings, prompt hashes, call counts, token usage, latencies and wall time) and [R14](results/v2/r14-answers.md): answer score per setup and dataset with document-clustered CIs and the difference from section-aware, Natural Questions by query type, and latency per answer.

`grade` is the model-graded check: 50 seeded questions per dataset (Natural Questions half precise, half context) times the three setups, 300 answers, each graded pass or fail through the `claude` command-line tool in headless mode (no tools, no settings files, no saved session, on its subscription login; the child process gets no Anthropic API key variable, so it never uses a paid API). The grader prompt, `configs/v2/grader-prompt.txt`, was committed before any answer existed and its sha256 is checked against the config. Calls are paced 5 s apart, retried with backoff and cached beside the answers. It writes `results/v2/grader-manifest.json` and [R15](results/v2/r15-grader.md): per dataset, the mean answer score of passes against fails, the AUC of the answer score for predicting a pass and how often the score (a pass at 0.5 or above) and the grader agree; per setup, the grader pass rate next to the mean answer score; and whether the setup ranking holds under the grader.

### The verdict

The verdict of [ADR 0008](docs/adr/0008-pre-register-v2s-success-bar-and-tie-break.md), computed mechanically from the runs above (issue 27). The depth-50 side run reranks section-aware and section-aware-titles to depth 50 instead of 30 (run name `v2-depth50`, otherwise the section-titles runs' settings), and the latency probe times each system's query path uncached.

```sh
uv run rag run configs/v2/qasper-depth50.yaml && uv run rag run configs/v2/nq-depth50.yaml
uv run rag latency configs/v2/latency.yaml
uv run rag verdict configs/v2/verdict.yaml
```

`latency` draws 50 seeded questions per dataset and times, per question and system, the query embedding, the searches (BM25 and vector search of each chunking in the runs' own indexes, then fusion) and the reranker (30 pairs for one chunking, the fused top 50 for search-all routing, every chunking's top 30 for confidence routing), with every query vector and reranker score computed by the model and one untimed pass per system first. It writes `results/v2/latency-profile.json` with the hardware and the library versions; the numbers are measurements, so a re-run differs. The depth-50 runs write the R2-R6 tables under run name `v2-depth50` (R6 on Natural Questions only).

`verdict` reads the per-question results (no retrieval runs) and joins every contender with its section-aware reference by dataset and question id, the reference being the section-aware rows of the run behind the contender's own table (R11 reads the baseline runs), so each contender's numbers agree with that table. It writes [R16](results/v2/r16-verdict.md): per contender at the bar's cell (budget view, 1024 tokens), the pooled and per-dataset recall differences with intervals from the paired, document-clustered bootstrap (10000 resamples, seed 0), the bar's three checks, the share of the oracle ceiling captured, the tie-break and a verdict sentence; R7's numbers reproduced at that cell; the reader stage's answer scores; the secondary results (512 and 2048 tokens Holm-adjusted, the production view, contextual-256-prefixed, the depth-50 side run); and the adoption profile (the latency probe, index-time costs from the late-chunking and prefix manifests, reader cost per answer). The same runs and seed regenerate R16 byte-identically.

## Data, models and licences

No dataset text is committed; the repository holds only identifiers, character offsets, hashes, scores and result tables.

**Datasets**

- **QASPER** v0.3, dev and test splits: Dasigi et al., *A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers*, NAACL 2021 ([arXiv 2105.03011](https://arxiv.org/abs/2105.03011)). Allen Institute for AI, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Natural Questions**, dev config (the 1,000-question subset is listed by id in `configs/nq-subset.txt`): Kwiatkowski et al., *Natural Questions: a Benchmark for Question Answering Research*, TACL 2019 ([ACL Anthology Q19-1026](https://aclanthology.org/Q19-1026/)). Google, licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

**Models**, each pinned to a Hugging Face revision:

| role | model | input limit | licence |
|---|---|---|---|
| embedder | [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) (Beijing Academy of Artificial Intelligence) | 512 tokens | MIT |
| embedder | [nomic-ai/nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) (Nomic AI) | 8192 tokens | Apache-2.0 |
| reranker | [Alibaba-NLP/gte-reranker-modernbert-base](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base) (Alibaba-NLP) | n/a | Apache-2.0 |
| context prefixes and reader (v2) | [mlx-community/Qwen3-8B-4bit](https://huggingface.co/mlx-community/Qwen3-8B-4bit) (Qwen3-8B by the Qwen team, Alibaba Cloud; 4-bit MLX conversion) | n/a | Apache-2.0 |

The v1 models' pinned revisions are listed in the write-up's [data, models and licences section](chunking/2026-10-14-v1-results.md#data-models-and-licences); the prefix model's is in [`configs/prefixes.yaml`](configs/prefixes.yaml), and the reader's (the same revision) in [`configs/v2/answers.yaml`](configs/v2/answers.yaml). The model-graded check uses Claude Sonnet through the `claude` command-line tool; the model that served each verdict is recorded in `results/v2/grader-manifest.json`.
