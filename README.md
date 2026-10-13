# rag-findings

Research findings on RAG chunking, retrieval strategies and retrieval evaluation.

## Glossary and decisions

The experiment's shared vocabulary is defined in [CONTEXT.md](CONTEXT.md), and its settled design decisions are recorded as ADRs under [docs/adr](docs/adr). [ADR 0004](docs/adr/0004-run-v1-on-the-settled-question-sets-and-chunking-grid-superseding-the-reports-proposal.md) supersedes the chunking grid proposed in the research report below.

## Tracer experiment (v1)

A thin end-to-end retrieval eval: QASPER v0.3 to canonical documents to labelled spans to fixed 256-token chunks to BM25 retrieval to a 1024-token budget (production view), scored as retrieval recall and precision against the labelled spans.

```sh
uv run rag setup && uv run rag run configs/tracer.yaml
```

Then open `results/qasper/r1-tracer.md`. `setup` downloads the QASPER dev and test tarballs (about 15 MB) into the git-ignored `data/` directory and verifies their sha256 checksums; `run` writes per-question results and a run manifest to the git-ignored `runs/` directory and regenerates the committed result table under `results/`. Unit tests run offline on small committed fixtures: `uv run pytest`.

## Grid: the production line and its ablations (v1)

Every chunking at every token budget on QASPER: fixed windows of 64, 128, 256, 512 and 1024 tokens (Chonkie's token chunker, cl100k_base, no overlap), section-aware chunks (one per section, split at paragraph boundaries above 512 tokens) and small-to-big (128-token children returning their section-aware parent when it fits the remaining budget); budgets of 128 to 8192 tokens; the production view (top-N cap 8, with a cap-5 side table) and the fair view (no cap); search across the whole collection and within the question's own document.

Each cell runs under four retrieval pipelines, two of them per embedder (bge-small-en-v1.5, 512-token input; nomic-embed-text-v1.5, 8192-token input with its `search_document:` / `search_query:` prefixes, which never count toward a budget):

- the production line: BM25 and vector search fused by reciprocal rank fusion (k = 60), then gte-reranker-modernbert-base reorders the fused top 30; after them the list continues in fused order (the unreranked tail), deep enough to fill the fair view at 8192 tokens;
- the ablations: hybrid without the reranker, vector search only, and BM25 only.

Small-to-big matches, and the reranker scores, the 128-token children. Vector search is exact (cosine) over a LanceDB table per chunking and embedder, next to the full-text index. Chunk embeddings (keyed by model and chunk span) and reranker scores (keyed by question and chunk) are cached under `data/cache/`, so both scopes and both embedders share them and a re-run does no reranker passes.

```sh
uv run rag setup && uv run rag run configs/grid.yaml --sample 50   # a seeded 50-paper sample, minutes
uv run rag run configs/grid.yaml                                   # the full run, several hours on an M4 Max
```

`setup` also downloads the pinned model revisions (safetensors weights, tokenizers and configs only, about 1.2 GB) into the git-ignored `data/hf-cache/`; runs then load them offline (`--no-models` skips them). A `--sample` run writes everything, its tables included, under `runs/grid-sample<N>/` and leaves `results/` untouched. The full run writes per-question results as Parquet under `runs/grid/` (git-ignored; one row per question, pipeline, embedder, chunking, search scope, view, cap and budget, plus fixed-k rows and each question's query type), a manifest with the wall time, the truncation shares and the reranker's pass counts, and regenerates the committed tables, each with one block per pipeline and embedder, the production line first:

- `results/qasper/r2-grid.md` (R2): retrieval recall and precision per chunking and budget, production and fair view side by side, plus the cap-5 side table;
- `results/qasper/r3-grid.md` (R3): retrieval recall per query type (precise, context; mixed counted but left out of the contrast) and the difference between types;
- `results/qasper/r4-grid.md` (R4): fixed-k hit@k and recall@k at k = 1, 5 and 10, for comparison with the literature only;
- `results/qasper/r2w-grid.md` (R2w): R2 with search within the question's own document;
- `results/qasper/r5-grid.md` (R5): pipeline x embedder x chunking at each budget, with each chunking's share of chunks longer than the embedder's input limit (‡, embedded truncated) and how often packing reached the unreranked tail.

"n/a" marks a fixed chunking whose chunk is bigger than the budget (R5 gives every n/a its reason); "†" marks production-view cells where the top-N cap, not the budget, limits the retrieved text for at least half of the questions; "§" marks production-line cells where packing used the unreranked tail. A BM25-only grid (`pipeline: bm25`) still runs in a few minutes without any model.

## Reports

- [Chunk size versus query type, and how to test it fairly](chunking/2026-10-10-chunk-size-vs-query-type.md) (2026-10-10): what the literature shows about larger chunks for context-heavy queries and smaller chunks for precise ones, strategies that combine precision and context, chunking-agnostic evaluation (span gold, token recall at a fixed budget), a budget-matched QASPER pilot, a proposed local experiment, and open design questions.

## Short answer from the first report

- Most published support for "bigger chunks for context-heavy queries" compares chunk sizes at a fixed top-k, which hands bigger chunks more text.
- With the reader's token budget held fixed, a local BM25 pilot on QASPER found 64-128-word chunks best for both single-paragraph and multi-paragraph questions; the hypothesised interaction pointed the right way but was small and not significant.
- Precise questions do favour small chunks: answer-span recall peaked at the smallest sizes.
- Evaluate chunkings with span-level gold and token recall at a fixed budget; chunk-id labels break when the chunking changes, and LLM context-relevancy scores favour small chunks by construction.
