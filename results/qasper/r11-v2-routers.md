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
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Systems: `search-all` and `confidence` (embedder nomic) from the routers runs; `hybrid-rerank` (the production line) from the baseline runs, collection search.

## Retrieval, budget view (top-N cap 20)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| qasper | 128 | section-aware | 0.0315 | 0.0292 | 122.8 | 2.15 |
| qasper | 128 | oracle router | 0.1221 | 0.1433 | 127.7 | 1.92 |
| qasper | 128 | search-all routing | 0.0640 | 0.0726 | 127.5 | 2.18 |
| qasper | 128 | confidence routing | 0.0541 | 0.0625 | 125.8 | 1.84 |
| qasper | 256 | section-aware | 0.0634 | 0.0365 | 250.9 | 2.98 |
| qasper | 256 | oracle router | 0.1977 | 0.1222 | 255.5 | 3.61 |
| qasper | 256 | search-all routing | 0.1033 | 0.0631 | 255.0 | 3.89 |
| qasper | 256 | confidence routing | 0.0911 | 0.0546 | 253.8 | 3.30 |
| qasper | 512 | section-aware | 0.1570 | 0.0555 | 506.8 | 4.06 |
| qasper | 512 | oracle router | 0.2915 | 0.0979 | 511.1 | 6.54 |
| qasper | 512 | search-all routing | 0.1693 | 0.0577 | 510.7 | 5.88 |
| qasper | 512 | confidence routing | 0.1502 | 0.0514 | 509.6 | 5.35 |
| qasper | 1024 | section-aware | 0.2480 | 0.0467 | 1018.9 | 6.43 |
| qasper | 1024 | oracle router | 0.3847 | 0.0674 | 1022.6 | 11.92 |
| qasper | 1024 | search-all routing | 0.2280 | 0.0409 | 1022.8 | 9.02 |
| qasper | 1024 | confidence routing | 0.2099 | 0.0377 | 1022.0 | 9.48 |
| qasper | 2048 | section-aware | 0.3076 | 0.0297 | 2041.6 | 10.86 |
| qasper | 2048 | oracle router | 0.4281 | 0.0399 | 1605.2 | 15.54 |
| qasper | 2048 | search-all routing | 0.2927 | 0.0275 | 2031.7 | 14.27 |
| qasper | 2048 | confidence routing | 0.2500 | 0.0254 | 1786.2 | 13.66 |
| qasper | 4096 | section-aware | 0.3429 | 0.0171 | 3900.1 | 17.97 |
| qasper | 4096 | oracle router | 0.4630 | 0.0257 | 2403.2 | 17.86 |
| qasper | 4096 | search-all routing | 0.3385 | 0.0178 | 3602.2 | 19.18 |
| qasper | 4096 | confidence routing | 0.2775 | 0.0184 | 2981.0 | 17.85 |
| qasper | 8192 | section-aware | 0.3512 | 0.0136 | 4776.7 | 20.00 |
| qasper | 8192 | oracle router | 0.4852 | 0.0207 | 3342.2 | 19.35 |
| qasper | 8192 | search-all routing | 0.3461 | 0.0155 | 4197.1 | 20.00 |
| qasper | 8192 | confidence routing | 0.2862 | 0.0158 | 3923.5 | 19.48 |


## Retrieval, production view (top-N cap 8)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| qasper | 128 | section-aware | 0.0315 | 0.0292 | 122.8 | 2.15 |
| qasper | 128 | oracle router | 0.1221 | 0.1433 | 127.7 | 1.92 |
| qasper | 128 | search-all routing | 0.0640 | 0.0726 | 127.5 | 2.18 |
| qasper | 128 | confidence routing | 0.0541 | 0.0625 | 125.8 | 1.84 |
| qasper | 256 | section-aware | 0.0634 | 0.0365 | 250.9 | 2.98 |
| qasper | 256 | oracle router | 0.1977 | 0.1222 | 255.5 | 3.61 |
| qasper | 256 | search-all routing | 0.1033 | 0.0631 | 255.0 | 3.89 |
| qasper | 256 | confidence routing | 0.0911 | 0.0546 | 253.8 | 3.30 |
| qasper | 512 | section-aware | 0.1570 | 0.0555 | 506.7 | 4.05 |
| qasper | 512 | oracle router | 0.2915 | 0.0980 | 510.1 | 6.48 |
| qasper | 512 | search-all routing | 0.1689 | 0.0577 | 509.1 | 5.71 |
| qasper | 512 | confidence routing | 0.1502 | 0.0515 | 509.0 | 5.32 |
| qasper | 1024 | section-aware | 0.2471 | 0.0467 | 1006.4 | 6.15 |
| qasper | 1024 | oracle router | 0.3766 | 0.0684 | 713.8 | 6.83 |
| qasper | 1024 | search-all routing | 0.2249 | 0.0421 | 942.9 | 7.06 |
| qasper | 1024 | confidence routing | 0.1983 | 0.0422 | 845.9 | 6.61 |
| qasper | 2048 | section-aware | 0.3033 | 0.0320 | 1717.7 | 7.91 |
| qasper | 2048 | oracle router | 0.4172 | 0.0460 | 1079.4 | 7.54 |
| qasper | 2048 | search-all routing | 0.2742 | 0.0333 | 1437.0 | 7.88 |
| qasper | 2048 | confidence routing | 0.2299 | 0.0332 | 1333.1 | 7.63 |
| qasper | 4096 | section-aware | 0.3101 | 0.0300 | 1870.1 | 8.00 |
| qasper | 4096 | oracle router | 0.4420 | 0.0397 | 1456.0 | 7.88 |
| qasper | 4096 | search-all routing | 0.2899 | 0.0315 | 1620.9 | 8.00 |
| qasper | 4096 | confidence routing | 0.2397 | 0.0318 | 1579.4 | 7.86 |
| qasper | 8192 | section-aware | 0.3101 | 0.0300 | 1870.1 | 8.00 |
| qasper | 8192 | oracle router | 0.4560 | 0.0386 | 1731.0 | 8.00 |
| qasper | 8192 | search-all routing | 0.2902 | 0.0314 | 1624.4 | 8.00 |
| qasper | 8192 | confidence routing | 0.2429 | 0.0314 | 1766.5 | 8.00 |


## Confidence routing's chunking picks

The pick is the chunking whose reranked top result scores highest (the top-1 reranker score of each chunking's reranked top 30), ties to the smaller chunk; it does not depend on the budget or the view.

| dataset | fixed-64 | fixed-128 | fixed-256 | fixed-512 | section-aware | small-to-big | fixed-1024 | all |
|---|---|---|---|---|---|---|---|---|
| qasper | 0.3350 (736) | 0.0719 (158) | 0.0250 (55) | 0.0086 (19) | 0.2435 (535) | 0.2613 (574) | 0.0546 (120) | 2197 |

## Notes

- Reranker pairs per question: 30 for one chunking's production line, 50 for search-all routing (the fused top 50) and 210 for confidence routing (seven chunkings x reranked top 30).
- Search-all routing fuses the seven chunkings' hybrid lists by reciprocal rank fusion (k = 60) keyed by document and character span, so identical text from two chunkings is one item; it reranks the fused top 50 and packs by budget counting overlapping text once. Small-to-big children return their parents under v1's rule.
- For search-all the reader text is the packed spans merged per document, in order of first appearance, so no text is repeated.
- Both routers are scored at every budget even when the confidence pick's chunks exceed it: a fixed-1024 pick at a 128-token budget retrieves nothing there.
- These tables regenerate byte-identically from the same runs: means are summed with math.fsum and nothing run-specific enters a table.
