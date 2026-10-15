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
| nq | 1000 | 500 | 500 | 0 | 1000 |

Systems: `search-all` and `confidence` (embedder nomic) from the routers runs; `hybrid-rerank` (the production line) from the baseline runs, collection search.

## Retrieval, budget view (top-N cap 20)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| nq | 128 | section-aware | 0.0580 | 0.0339 | 125.5 | 3.65 |
| nq | 128 | oracle router | 0.4837 | 0.4240 | 127.9 | 1.64 |
| nq | 128 | search-all routing | 0.3217 | 0.2788 | 127.9 | 1.62 |
| nq | 128 | confidence routing | 0.1616 | 0.1338 | 103.9 | 1.84 |
| nq | 256 | section-aware | 0.2403 | 0.0995 | 253.5 | 4.24 |
| nq | 256 | oracle router | 0.7057 | 0.3302 | 255.6 | 2.75 |
| nq | 256 | search-all routing | 0.4771 | 0.2193 | 255.7 | 2.93 |
| nq | 256 | confidence routing | 0.2877 | 0.1280 | 240.1 | 2.82 |
| nq | 512 | section-aware | 0.6600 | 0.1620 | 509.5 | 4.58 |
| nq | 512 | oracle router | 0.8857 | 0.2173 | 511.5 | 4.28 |
| nq | 512 | search-all routing | 0.6600 | 0.1608 | 511.5 | 3.76 |
| nq | 512 | confidence routing | 0.4749 | 0.1136 | 498.1 | 4.14 |
| nq | 1024 | section-aware | 0.8197 | 0.1067 | 1021.6 | 6.51 |
| nq | 1024 | oracle router | 0.9583 | 0.1210 | 1023.4 | 8.30 |
| nq | 1024 | search-all routing | 0.7837 | 0.1009 | 1023.6 | 4.16 |
| nq | 1024 | confidence routing | 0.7686 | 0.0967 | 1022.8 | 6.61 |
| nq | 2048 | section-aware | 0.9087 | 0.0609 | 2045.4 | 9.88 |
| nq | 2048 | oracle router | 0.9845 | 0.0706 | 1822.8 | 13.50 |
| nq | 2048 | search-all routing | 0.8775 | 0.0588 | 2046.8 | 8.54 |
| nq | 2048 | confidence routing | 0.8519 | 0.0590 | 1909.2 | 9.74 |
| nq | 4096 | section-aware | 0.9489 | 0.0323 | 4081.8 | 15.90 |
| nq | 4096 | oracle router | 0.9926 | 0.0524 | 2768.2 | 17.69 |
| nq | 4096 | search-all routing | 0.9136 | 0.0312 | 4075.9 | 14.65 |
| nq | 4096 | confidence routing | 0.8844 | 0.0368 | 3497.4 | 13.54 |
| nq | 8192 | section-aware | 0.9669 | 0.0211 | 6505.6 | 20.00 |
| nq | 8192 | oracle router | 0.9981 | 0.0483 | 3540.9 | 19.53 |
| nq | 8192 | search-all routing | 0.9222 | 0.0187 | 7057.6 | 19.87 |
| nq | 8192 | confidence routing | 0.8985 | 0.0271 | 5794.6 | 16.86 |


## Retrieval, production view (top-N cap 8)

Recall and precision count every retrieved token once (the union of the packed chunks' token ranges); the single chunkings' chunks never overlap, so their scores are unchanged. The oracle router picks per question the chunking with the highest recall, ties to the smaller chunk. Retrieved tokens and chunks are means per question.

| dataset | budget | system | recall | precision | retrieved tokens | chunks |
|---|---|---|---|---|---|---|
| nq | 128 | section-aware | 0.0580 | 0.0339 | 125.5 | 3.65 |
| nq | 128 | oracle router | 0.4837 | 0.4240 | 127.9 | 1.64 |
| nq | 128 | search-all routing | 0.3217 | 0.2788 | 127.9 | 1.62 |
| nq | 128 | confidence routing | 0.1616 | 0.1338 | 103.9 | 1.83 |
| nq | 256 | section-aware | 0.2403 | 0.0995 | 253.4 | 4.24 |
| nq | 256 | oracle router | 0.7057 | 0.3302 | 255.6 | 2.75 |
| nq | 256 | search-all routing | 0.4771 | 0.2193 | 255.7 | 2.92 |
| nq | 256 | confidence routing | 0.2877 | 0.1280 | 240.1 | 2.82 |
| nq | 512 | section-aware | 0.6600 | 0.1621 | 509.3 | 4.54 |
| nq | 512 | oracle router | 0.8857 | 0.2173 | 511.5 | 4.28 |
| nq | 512 | search-all routing | 0.6600 | 0.1610 | 510.9 | 3.70 |
| nq | 512 | confidence routing | 0.4749 | 0.1137 | 498.1 | 4.13 |
| nq | 1024 | section-aware | 0.8197 | 0.1072 | 1017.6 | 6.27 |
| nq | 1024 | oracle router | 0.9551 | 0.1349 | 918.3 | 5.87 |
| nq | 1024 | search-all routing | 0.7836 | 0.1020 | 1013.7 | 3.81 |
| nq | 1024 | confidence routing | 0.7545 | 0.1045 | 930.7 | 5.08 |
| nq | 2048 | section-aware | 0.9077 | 0.0650 | 1929.8 | 7.80 |
| nq | 2048 | oracle router | 0.9803 | 0.0996 | 1478.2 | 7.37 |
| nq | 2048 | search-all routing | 0.8735 | 0.0628 | 1925.5 | 6.57 |
| nq | 2048 | confidence routing | 0.8239 | 0.0720 | 1666.1 | 6.27 |
| nq | 4096 | section-aware | 0.9299 | 0.0541 | 2481.1 | 8.00 |
| nq | 4096 | oracle router | 0.9889 | 0.0914 | 1916.1 | 7.96 |
| nq | 4096 | search-all routing | 0.8971 | 0.0459 | 2930.8 | 7.90 |
| nq | 4096 | confidence routing | 0.8439 | 0.0586 | 2520.4 | 7.04 |
| nq | 8192 | section-aware | 0.9299 | 0.0541 | 2481.1 | 8.00 |
| nq | 8192 | oracle router | 0.9928 | 0.0912 | 1992.9 | 8.00 |
| nq | 8192 | search-all routing | 0.8982 | 0.0449 | 3090.9 | 8.00 |
| nq | 8192 | confidence routing | 0.8522 | 0.0544 | 3568.5 | 8.00 |


## Confidence routing's chunking picks

The pick is the chunking whose reranked top result scores highest (the top-1 reranker score of each chunking's reranked top 30), ties to the smaller chunk; it does not depend on the budget or the view.

| dataset | fixed-64 | fixed-128 | fixed-256 | fixed-512 | section-aware | small-to-big | fixed-1024 | all |
|---|---|---|---|---|---|---|---|---|
| nq | 0.1770 (177) | 0.0570 (57) | 0.0480 (48) | 0.0270 (27) | 0.2540 (254) | 0.1670 (167) | 0.2700 (270) | 1000 |

## Notes

- Reranker pairs per question: 30 for one chunking's production line, 50 for search-all routing (the fused top 50) and 210 for confidence routing (seven chunkings x reranked top 30).
- Search-all routing fuses the seven chunkings' hybrid lists by reciprocal rank fusion (k = 60) keyed by document and character span, so identical text from two chunkings is one item; it reranks the fused top 50 and packs by budget counting overlapping text once. Small-to-big children return their parents under v1's rule.
- For search-all the reader text is the packed spans merged per document, in order of first appearance, so no text is repeated.
- Both routers are scored at every budget even when the confidence pick's chunks exceed it: a fixed-1024 pick at a 128-token budget retrieves nothing there.
- These tables regenerate byte-identically from the same runs: means are summed with math.fsum and nothing run-specific enters a table.
