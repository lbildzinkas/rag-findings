# rag-findings

Research findings on RAG chunking, retrieval strategies and retrieval evaluation.

## Glossary and decisions

The experiment's shared vocabulary is defined in [CONTEXT.md](CONTEXT.md), and its settled design decisions are recorded as ADRs under [docs/adr](docs/adr). [ADR 0004](docs/adr/0004-run-v1-on-the-settled-question-sets-and-chunking-grid-superseding-the-reports-proposal.md) supersedes the chunking grid proposed in the research report below.

## Reports

- [Chunk size versus query type, and how to test it fairly](chunking/2026-10-10-chunk-size-vs-query-type.md) (2026-10-10): what the literature shows about larger chunks for context-heavy queries and smaller chunks for precise ones, strategies that combine precision and context, chunking-agnostic evaluation (span gold, token recall at a fixed budget), a budget-matched QASPER pilot, a proposed local experiment, and open design questions.

## Short answer from the first report

- Most published support for "bigger chunks for context-heavy queries" compares chunk sizes at a fixed top-k, which hands bigger chunks more text.
- With the reader's token budget held fixed, a local BM25 pilot on QASPER found 64-128-word chunks best for both single-paragraph and multi-paragraph questions; the hypothesised interaction pointed the right way but was small and not significant.
- Precise questions do favour small chunks: answer-span recall peaked at the smallest sizes.
- Evaluate chunkings with span-level gold and token recall at a fixed budget; chunk-id labels break when the chunking changes, and LLM context-relevancy scores favour small chunks by construction.
