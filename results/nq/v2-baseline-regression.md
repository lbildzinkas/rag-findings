# NQ v2-baseline re-run regression against the v1 grid

The v2 baseline re-runs v1's production line (hybrid-rerank, nomic, collection search) from the same embedding and reranker-score cache. Against the v1 grid's nomic production-line cells, every committed v2-baseline cell matches byte-for-byte except three, which stay within ±0.001: fixed-512@512, fixed-1024@1024 and section-aware@512. The three cells carry through R2 (production, side, budget and fair columns), R5 (the same), R3 (the context cells of the two 512-budget rows, the precise cell of the 1024 row), R4 (hit@1 and recall@1 only) and R6 (fixed-1024@1024 only).

The flipped questions, exactly one per affected cell, diagnosed from the git-ignored run artifacts (runs/nq/grid, runs/nq/v2-baseline, data/cache/rag-cache.sqlite) on the machine that ran the grids:

| cell | question |
|---|---|
| fixed-512@512 | -4523406960144718852 |
| fixed-1024@1024 | -8209058272420680202 |
| section-aware@512 | 3583320863223516578 |

The v2 run manifest (runs/nq/v2-baseline/manifest.json) records chunk_vectors_embedded 0, queries_embedded 0 and reranker pairs_scored 0, with 202,777 pairs cached: nothing was recomputed, so a recomputed embedding or reranker score is ruled out.

Cause: for each flipped question another NQ page holds a byte-identical chunk at the same character span, and the reranker scores both duplicates exactly equally. fixed-1024: doc -8209058272420680202 span 0-4267 vs doc -6382343808953358712 span 0-4267, both scored 0.9190916419029236. fixed-512: doc -4523406960144718852 span 0-2437 vs doc -2525700398664435471 span 0-2437, both 0.920451283454895. section-aware: doc 3583320863223516578 span 1452-3091 vs doc 2607341085762662184 span 1452-3091, both 0.9183371067047119. The tied duplicates occupy the top of the reranked head: in the v2 run's packed list (runs/nq/v2-baseline/packed.parquet) the other page's duplicate is rank 1 and the gold page's duplicate rank 2, so at the affected budget only the other page's duplicate fits and the gold text goes unpacked; for fixed-1024 the 2048-token row packs both duplicates and its recall is 1.0. The v1 NQ run ordered the gold page's duplicate first; it was made after the deterministic tie handling had merged (commit a322d74 landed 2026-10-14 10:44 UTC and the run began about an hour later, on the branch that became #15, whose single commit changed no source file), so pre-determinism does not explain its order. The flip is tie order between byte-identical duplicate chunks under equal reranker scores - no code change on this branch and no recomputed score is involved; QASPER, whose v1 run is the deterministic re-run, matches byte-for-byte.

Consistent with the committed aggregates: each deviating cell moves by one question's worth and only downward; R4's hit@5 and recall@5 (and beyond) are unchanged, because both duplicates sit at the top of the reranked head; the two 512-budget losses fall in R3's context column and the 1024 loss in its precise column.
