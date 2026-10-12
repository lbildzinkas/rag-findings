# Run v1 on the settled question sets and chunking grid, superseding the report's proposal

The research report under chunking/ drafted its chunkers before the design session settled v1: fixed windows of 64 to 512 tokens with 1024 only for the long-context embedder, heading-aware recursive splitting with the heading path as a prefix, natural units, sentence windows and an overlap cell, plus contextual prefixes on a subset and late chunking as an option. Later tickets implementing data ingestion or chunking would follow that superseded grid, because no record here names the settled question sets or chunkings.

So v1 runs on QASPER plus a Natural Questions subset with labelled spans; the owner's own set over interview-coach study material comes later, at adoption. The chunkings are fixed 64/128/256/512/1024-token windows, section-aware and small-to-big, counted with the one tokenizer (tiktoken `cl100k_base`), and the embedders are bge-small-en-v1.5 and nomic-embed-text-v1.5. Budgets run from 128 to 8192 tokens, reported in both the production and the fair view, and v1 also measures the chunk size x query type interaction. This supersedes the chunker grid proposed in the research report under chunking/.

LLM context prefixes, late chunking and answer accuracy are deferred to v2.
