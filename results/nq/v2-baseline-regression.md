# NQ v2-baseline re-run regression against the v1 grid

The v2 baseline re-runs v1's production line (hybrid-rerank, nomic, collection search) from the same embedding and reranker-score cache. Against the v1 grid's nomic production-line cells, every committed v2-baseline cell matches byte-for-byte except three: fixed-512@512, fixed-1024@1024 and section-aware@512, which stay within ±0.001. The three cells carry through R2 (production, side, budget and fair columns), R5 (the same), R3 (the context cells of the two 512-budget rows, the precise cell of the 1024 row), R4 (hit@1 and recall@1 only) and R6 (fixed-1024@1024 only).

What the committed aggregates show:

- each deviating recall, precision or hit cell moves against the v2 re-run by exactly one question (0.0010 over the 1000 questions; 0.0020 over the 500-question query-type means and the 483-question short-answer mean);
- R4's hit@5, recall@5, hit@10 and recall@10 are unchanged for all three chunkings, so each flip is a swap of ranks 1 and 2 of the reranked head, and only the top-ranked chunk - the single chunk those budgets pack - changed;
- the two 512-budget losses fall in R3's context column and the 1024 loss in its precise column, so at least two distinct questions are involved; whether the two context losses are the same question the aggregates cannot show;
- the QASPER re-run matched v1 byte-for-byte, and no retrieval code path differs between the two runs.

What the committed data cannot show: the flipped question ids (the per-question results live in the git-ignored runs/nq/grid and runs/nq/v2-baseline) and the v2 run manifest's recomputation counts (chunk vectors embedded, queries embedded, reranker pairs scored, in runs/nq/v2-baseline/manifest.json). The cause is therefore undetermined from the repository: the remaining candidates are a near-tied embedding or reranker score recomputed on a cache miss - which those counts would reveal - and tie order at a fused cutoff.
