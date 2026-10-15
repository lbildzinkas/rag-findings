# R11 - v2 routers: search-all and confidence routing

Config hash: `78fb4fdf560d092211f6d71af05e3ed9f325638d26fb68a088ee4680ee5db6ae`

## Config

```yaml
baseline_chunking: section-aware
baselines:
- qasper/v2-baseline
- nq/v2-baseline
budget_top_n: 20
chunkings:
- fixed-64
- fixed-128
- fixed-256
- fixed-512
- section-aware
- small-to-big
- fixed-1024
embedder: nomic
kind: routers-table
pipeline: hybrid-rerank
run_name: v2-routers
runs:
- qasper/v2-routers
- nq/v2-routers
scope: collection
top_n: 8
```

## Inputs

| run | kind | run config hash |
|---|---|---|
| nq/v2-routers | routers | `f15eabd39780d5ba429c7f3fd8cc8e6b61a5155900ad83094f366ff3b1505c0b` |
| nq/v2-baseline | grid | `b88ce9188b6e18537719b8dc5850675abc3f472d121b8683b761ac304b576f9f` |
| qasper/v2-routers | routers | `bde74c2df035145fcc0e87b372eb7209b582e35b8fd3f5f3d60730e4deb96b1b` |
| qasper/v2-baseline | grid | `28fc1dc15c8ac341b982544b402db094b15997c8b808cf9733d9f9d734cb51d7` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| pooled | 1684 | 1817 | 904 | 476 | 3197 |

Systems: `search-all` and `confidence` (embedder nomic) from the routers runs; `hybrid-rerank` (the production line) from the baseline runs, collection search.

## Retrieval, budget view (top-N cap 20)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| pooled | 128 | section-aware | 0.0398 | 0.0307 | 123.7 | 2.62 |
| pooled | 128 | oracle router | 0.2352 | 0.2311 | 127.8 | 1.83 |
| pooled | 128 | search-all routing | 0.1446 | 0.1371 | 127.6 | 2.01 |
| pooled | 128 | confidence routing | 0.0877 | 0.0848 | 119.0 | 1.84 |
| pooled | 256 | section-aware | 0.1188 | 0.0562 | 251.7 | 3.37 |
| pooled | 256 | oracle router | 0.3566 | 0.1873 | 255.5 | 3.34 |
| pooled | 256 | search-all routing | 0.2203 | 0.1120 | 255.2 | 3.59 |
| pooled | 256 | confidence routing | 0.1526 | 0.0775 | 249.5 | 3.15 |
| pooled | 512 | section-aware | 0.3143 | 0.0888 | 507.7 | 4.22 |
| pooled | 512 | oracle router | 0.4774 | 0.1353 | 511.2 | 5.83 |
| pooled | 512 | search-all routing | 0.3228 | 0.0900 | 511.0 | 5.22 |
| pooled | 512 | confidence routing | 0.2517 | 0.0709 | 506.0 | 4.97 |
| pooled | 1024 | section-aware | 0.4269 | 0.0655 | 1019.7 | 6.46 |
| pooled | 1024 | oracle router | 0.5641 | 0.0842 | 1022.8 | 10.79 |
| pooled | 1024 | search-all routing | 0.4018 | 0.0597 | 1023.0 | 7.50 |
| pooled | 1024 | confidence routing | 0.3847 | 0.0562 | 1022.2 | 8.58 |
| pooled | 2048 | section-aware | 0.4956 | 0.0394 | 2042.8 | 10.56 |
| pooled | 2048 | oracle router | 0.6021 | 0.0495 | 1673.2 | 14.91 |
| pooled | 2048 | search-all routing | 0.4756 | 0.0373 | 2036.4 | 12.48 |
| pooled | 2048 | confidence routing | 0.4383 | 0.0359 | 1824.6 | 12.43 |
| pooled | 4096 | section-aware | 0.5325 | 0.0218 | 3956.9 | 17.32 |
| pooled | 4096 | oracle router | 0.6286 | 0.0340 | 2517.3 | 17.81 |
| pooled | 4096 | search-all routing | 0.5184 | 0.0220 | 3750.4 | 17.77 |
| pooled | 4096 | confidence routing | 0.4673 | 0.0241 | 3142.5 | 16.50 |
| pooled | 8192 | section-aware | 0.5438 | 0.0159 | 5317.5 | 20.00 |
| pooled | 8192 | oracle router | 0.6456 | 0.0293 | 3404.3 | 19.41 |
| pooled | 8192 | search-all routing | 0.5263 | 0.0165 | 5091.9 | 19.96 |
| pooled | 8192 | confidence routing | 0.4777 | 0.0194 | 4508.7 | 18.66 |


## Retrieval, production view (top-N cap 8)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| pooled | 128 | section-aware | 0.0398 | 0.0307 | 123.6 | 2.62 |
| pooled | 128 | oracle router | 0.2352 | 0.2311 | 127.8 | 1.83 |
| pooled | 128 | search-all routing | 0.1446 | 0.1371 | 127.6 | 2.01 |
| pooled | 128 | confidence routing | 0.0877 | 0.0848 | 119.0 | 1.84 |
| pooled | 256 | section-aware | 0.1188 | 0.0562 | 251.7 | 3.37 |
| pooled | 256 | oracle router | 0.3566 | 0.1873 | 255.5 | 3.34 |
| pooled | 256 | search-all routing | 0.2203 | 0.1120 | 255.2 | 3.58 |
| pooled | 256 | confidence routing | 0.1526 | 0.0775 | 249.5 | 3.15 |
| pooled | 512 | section-aware | 0.3143 | 0.0888 | 507.5 | 4.20 |
| pooled | 512 | oracle router | 0.4774 | 0.1353 | 510.5 | 5.79 |
| pooled | 512 | search-all routing | 0.3225 | 0.0900 | 509.7 | 5.08 |
| pooled | 512 | confidence routing | 0.2517 | 0.0709 | 505.6 | 4.95 |
| pooled | 1024 | section-aware | 0.4262 | 0.0656 | 1009.9 | 6.19 |
| pooled | 1024 | oracle router | 0.5575 | 0.0892 | 777.8 | 6.53 |
| pooled | 1024 | search-all routing | 0.3996 | 0.0608 | 965.1 | 6.04 |
| pooled | 1024 | confidence routing | 0.3722 | 0.0617 | 872.4 | 6.13 |
| pooled | 2048 | section-aware | 0.4923 | 0.0424 | 1784.0 | 7.87 |
| pooled | 2048 | oracle router | 0.5933 | 0.0628 | 1204.2 | 7.48 |
| pooled | 2048 | search-all routing | 0.4616 | 0.0425 | 1589.8 | 7.47 |
| pooled | 2048 | confidence routing | 0.4157 | 0.0453 | 1437.2 | 7.20 |
| pooled | 4096 | section-aware | 0.5040 | 0.0375 | 2061.2 | 8.00 |
| pooled | 4096 | oracle router | 0.6131 | 0.0559 | 1599.9 | 7.91 |
| pooled | 4096 | search-all routing | 0.4798 | 0.0360 | 2030.6 | 7.97 |
| pooled | 4096 | confidence routing | 0.4287 | 0.0402 | 1873.7 | 7.60 |
| pooled | 8192 | section-aware | 0.5040 | 0.0375 | 2061.2 | 8.00 |
| pooled | 8192 | oracle router | 0.6239 | 0.0550 | 1812.9 | 8.00 |
| pooled | 8192 | search-all routing | 0.4804 | 0.0357 | 2083.1 | 8.00 |
| pooled | 8192 | confidence routing | 0.4335 | 0.0386 | 2330.2 | 8.00 |


## Confidence routing's chunking picks

The pick is the chunking whose reranked top result scores highest (the top-1 reranker score of each chunking's reranked top 30), ties to the smaller chunk; it does not depend on the budget or the view.

| dataset | fixed-64 | fixed-128 | fixed-256 | fixed-512 | section-aware | small-to-big | fixed-1024 | all |
|---|---|---|---|---|---|---|---|---|
| pooled | 0.2856 (913) | 0.0673 (215) | 0.0322 (103) | 0.0144 (46) | 0.2468 (789) | 0.2318 (741) | 0.1220 (390) | 3197 |

## Notes

- Reranker pairs per question: 30 for one chunking's production line, 50 for search-all routing (the fused top 50) and 210 for confidence routing (seven chunkings x reranked top 30).
- Search-all routing fuses the seven chunkings' hybrid lists by reciprocal rank fusion (k = 60) keyed by document and character span, so identical text from two chunkings is one item; it reranks the fused top 50 and packs by budget counting overlapping text once. Small-to-big children return their parents under v1's rule.
- For search-all the reader text is the packed spans merged per document, in order of first appearance, so no text is repeated.
- Both routers are scored at every budget even when the confidence pick's chunks exceed it: a fixed-1024 pick at a 128-token budget retrieves nothing there.
- These tables regenerate byte-identically from the same runs: means are summed with math.fsum and nothing run-specific enters a table.
