# rag-findings

Research findings on RAG chunking, retrieval strategies and retrieval evaluation.

## Glossary and decisions

The experiment's shared vocabulary is defined in [CONTEXT.md](CONTEXT.md), and its settled design decisions are recorded as ADRs under [docs/adr](docs/adr). [ADR 0004](docs/adr/0004-run-v1-on-the-settled-question-sets-and-chunking-grid-superseding-the-reports-proposal.md) supersedes the chunking grid proposed in the research report below.

## Tracer experiment (v1)

A thin end-to-end retrieval eval: QASPER v0.3 to canonical documents to labelled spans to fixed 256-token chunks to BM25 retrieval to a 1024-token budget (production view), scored as retrieval recall and precision against the labelled spans.

```sh
uv run rag setup && uv run rag run configs/tracer.yaml
```

Then open `results/qasper/r1-tracer.md`. `setup` downloads the QASPER dev and test tarballs (about 15 MB) and the Natural Questions dev config (seven parquet shards, about 1.34 GB; never the default config, whose train split is 57 GB) into the git-ignored `data/` directory and verifies their sha256 checksums; `run` writes per-question results and a run manifest to the git-ignored `runs/` directory (namespaced per dataset label) and regenerates the committed result table under `results/`. Unit tests run offline on small committed fixtures: `uv run pytest`.

## Grid: the production line and its ablations (v1)

Every chunking at every token budget on QASPER (and, with `configs/nq-grid.yaml`, on the Natural Questions subset below): fixed windows of 64, 128, 256, 512 and 1024 tokens (Chonkie's token chunker, cl100k_base, no overlap), section-aware chunks (one per section, split at paragraph boundaries above 512 tokens) and small-to-big (128-token children returning their section-aware parent when it fits the remaining budget); budgets of 128 to 8192 tokens; the production view (top-N cap 8, with a cap-5 side table) and the fair view (no cap); search across the whole collection and within the question's own document.

Each cell runs under four retrieval pipelines, two of them per embedder (bge-small-en-v1.5, 512-token input; nomic-embed-text-v1.5, 8192-token input with its `search_document:` / `search_query:` prefixes, which never count toward a budget):

- the production line (`hybrid-rerank`): BM25 and vector search fused by reciprocal rank fusion (k = 60), then gte-reranker-modernbert-base reorders the fused top 30; after them the list continues in fused order (the unreranked tail), deep enough to fill the fair view at 8192 tokens;
- the ablations: hybrid without the reranker, vector search only, and BM25 only.

Small-to-big matches, and the reranker scores, the 128-token children. Vector search is exact (cosine) over a LanceDB table per chunking and embedder, next to the full-text index. Chunk embeddings (keyed by model and chunk span) and reranker scores (keyed by question and chunk) are cached under `data/cache/`, so both scopes and both embedders share them and a re-run does no reranker passes.

```sh
uv run rag setup && uv run rag run configs/grid.yaml --sample 50   # a seeded 50-paper sample, minutes
uv run rag run configs/grid.yaml                                   # the full run, several hours on an M4 Max
```

`setup` also downloads the pinned model revisions (safetensors weights, tokenizers and configs only, about 1.2 GB) into the git-ignored `data/hf-cache/`; runs then load them offline (`--no-models` skips them). A `--sample` run writes everything, its tables included, under `runs/qasper/grid-sample<N>/` and leaves `results/` untouched. The full run writes per-question results as Parquet under `runs/<dataset>/<run_name>/` (git-ignored; one row per question, pipeline, embedder, chunking, search scope, view, cap and budget, plus fixed-k rows and each question's query type), a manifest with the wall time, the truncation shares and the reranker's pass counts, and regenerates the committed tables, each with one block per pipeline and embedder, the production line first:

- `results/qasper/r2-grid.md` (R2): retrieval recall and precision per chunking and budget, production and fair view side by side, plus the cap-5 side table;
- `results/qasper/r3-grid.md` (R3): retrieval recall per query type (precise, context; mixed counted but left out of the contrast) and the difference between types;
- `results/qasper/r4-grid.md` (R4): fixed-k hit@k and recall@k at k = 1, 5 and 10, for comparison with the literature only;
- `results/qasper/r2w-grid.md` (R2w): R2 with search within the question's own document;
- `results/qasper/r5-grid.md` (R5): pipeline x embedder x chunking at each budget, with each chunking's share of chunks longer than the embedder's input limit (‡, embedded truncated) and how often packing reached the unreranked tail.

"n/a" marks a fixed chunking whose chunk is bigger than the budget (R5 gives every n/a its reason); "†" marks production-view cells where the top-N cap, not the budget, limits the retrieved text for at least half of the questions; "§" marks production-line cells where packing used the unreranked tail. A BM25-only grid (`pipeline: bm25`) still runs in a few minutes without any model.

## Natural Questions subset (v1)

A second dataset, so the chunk size × query type interaction and the routing headroom are not QASPER-only. `sample` picks 1,000 questions from the NQ dev config - 500 with a short answer (precise) and 500 long-answer-only (context) - from the questions where at least 2 of 5 annotators gave a long answer and at least one of those long answers is a paragraph (`<P>`); tables and lists are excluded. The selection ranks question ids by seeded sha256, and the resulting id list is committed as `configs/nq-subset.txt` (ids only, never dataset text, so the CC BY-SA 3.0 ShareAlike term never attaches to the repository) and reproduces the same subset.

```sh
uv run rag sample && uv run rag run configs/nq-tracer.yaml && uv run rag run configs/nq-grid.yaml
```

The canonical page text is the page's non-HTML tokens (tokens joined with spaces inside a paragraph, paragraphs joined with blank lines), with a map from token offsets to character offsets; the labelled span of every annotator whose long answer is a `<P>` paragraph is that paragraph, and short-answer spans are kept per annotator. Sections come from the page's heading tags, so section-aware chunks and small-to-big parents follow the page's own structure. The collection is the subset's 1,000 pages; whole-collection search runs over all of them and within-document search over the question's own page.

The NQ tracer and grid write the same R1-R5 and R2w tables under `results/nq/`, plus `results/nq/r6-grid.md` (R6): short-answer span recall by chunking and budget on the NQ precise questions that have a short-answer span, the same packing as R2 scored against the short-answer spans instead of the long-answer paragraph.

## Pooled runs (v1)

`configs/pooled-tracer.yaml` and `configs/pooled-grid.yaml` load QASPER (dev and test) and the NQ subset together: one collection, one retrieval run over both, and the same tables under `results/pooled/` (BM25 only: the production line and its ablations run per dataset), with each dataset's n kept visible (the Questions section of every pooled table breaks the query-type counts down per dataset).

```sh
uv run rag run configs/pooled-tracer.yaml && uv run rag run configs/pooled-grid.yaml
```

## Routing headroom (v1)

The analysis that decides whether v2 builds a query router, read from the grid runs' per-question results (no retrieval runs). Per dataset (and pooled when there are several), pipeline, embedder, budget and view: the best single chunking (highest mean retrieval recall), the oracle router (per question, the chunking with the highest recall; ties to the smaller chunk) and the routing headroom between them. A paired bootstrap over documents (10,000 resamples, fixed seed) re-selects the best single chunking inside every resample and gives 95% CIs at the pre-registered 1024-token budget, Holm-adjusted at the other budgets.

```sh
uv run rag run configs/grid.yaml && uv run rag run configs/nq-grid.yaml && uv run rag headroom configs/headroom.yaml
```

It takes seconds and regenerates the committed tables under `results/routing/`, byte-identically for the same seed and inputs:

- `r7-headroom.md` (R7): the router gate verdict per embedder (production line, production view, 1024 tokens, pooled QASPER + NQ: build the router if either embedder's headroom is at least +0.05 recall with a CI excluding 0), the routing headroom, a query-type oracle row (the best chunking per labelled query type; secondary, not part of the gate) and every chunking's difference from the best single chunking;
- `r8-headroom.md` (R8): the chunk size x query type interaction [Δ(chunking − fixed-128) | context] − [Δ(chunking − fixed-128) | precise];
- `r9-headroom.md` (R9): which chunking the oracle router picks, by query type, at 1024 tokens.

The committed tables read the QASPER and Natural Questions grid runs (`runs: [qasper/grid, nq/grid]`), pooled per question across the two runs, each dataset's documents resampled as its own clusters.

## v1 results write-up

[RAG chunking v1: which chunking retrieves best, whether query type matters, and whether to build a router](chunking/2026-10-14-v1-results.md) (2026-10-14) answers the three v1 questions from the committed tables: the best single chunking per budget and view, the chunk size x query type interaction against the research pilot's prior, and the router gate's verdict (build the router in v2: the routing headroom clears the pre-registered +0.05 bar for both embedders), with the ablations, the limitations, and what v2 should do. Its tables and figures (`chunking/figures/`) are regenerated from `results/` without running any retrieval:

```sh
uv run rag writeup          # re-render the write-up's tables and figures
uv run rag writeup --check  # change nothing; fail if the write-up or a figure differs from results/
```

## Reports

- [RAG chunking v1 results](chunking/2026-10-14-v1-results.md) (2026-10-14): the v1 write-up above.
- [Chunk size versus query type, and how to test it fairly](chunking/2026-10-10-chunk-size-vs-query-type.md) (2026-10-10): what the literature shows about larger chunks for context-heavy queries and smaller chunks for precise ones, strategies that combine precision and context, chunking-agnostic evaluation (span gold, token recall at a fixed budget), a budget-matched QASPER pilot, a proposed local experiment, and open design questions.

## Short answer from the first report

- Most published support for "bigger chunks for context-heavy queries" compares chunk sizes at a fixed top-k, which hands bigger chunks more text.
- With the reader's token budget held fixed, a local BM25 pilot on QASPER found 64-128-word chunks best for both single-paragraph and multi-paragraph questions; the hypothesised interaction pointed the right way but was small and not significant.
- Precise questions do favour small chunks: answer-span recall peaked at the smallest sizes.
- Evaluate chunkings with span-level gold and token recall at a fixed budget; chunk-id labels break when the chunking changes, and LLM context-relevancy scores favour small chunks by construction.
