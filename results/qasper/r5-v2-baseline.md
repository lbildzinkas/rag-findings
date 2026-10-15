# R5 - qasper v2-baseline, production line and ablations: pipeline x embedder x chunking

Config hash: `28fc1dc15c8ac341b982544b402db094b15997c8b808cf9733d9f9d734cb51d7`

## Config

```yaml
budget_top_n: 20
budgets:
- 128
- 256
- 512
- 1024
- 2048
- 4096
- 8192
chunkings:
- chunk_tokens: 64
  method: fixed
  name: fixed-64
- chunk_tokens: 128
  method: fixed
  name: fixed-128
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- chunk_tokens: 512
  method: fixed
  name: fixed-512
- chunk_tokens: 1024
  method: fixed
  name: fixed-1024
- max_tokens: 512
  method: section_aware
  name: section-aware
- child_tokens: 128
  max_tokens: 512
  method: small_to_big
  name: small-to-big
dataset:
  name: qasper
  splits:
  - dev
  - test
embedders:
- nomic
export_packed:
- budget: 1024
  scope: collection
  view: budget
fixed_k:
- 1
- 5
- 10
kind: grid
pipelines:
- hybrid-rerank
rerank_depth: 30
rrf_k: 60
run_name: v2-baseline
scopes:
- collection
search_depth: 1000
seed: 0
side_top_n: 5
top_n: 8
```

## Models

| role | name | model | revision | input limit |
|---|---|---|---|---|
| embedder | nomic | nomic-ai/nomic-embed-text-v1.5 | `e9b6763023c676ca8431644204f50c2b100d9aab` | 8192 tokens |
| reranker | gte-reranker-modernbert-base | Alibaba-NLP/gte-reranker-modernbert-base | `f7481e6055501a30fb19d090657df9ec1f79ab2c` | n/a |

## Dataset

| split | sha256 |
|---|---|
| dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| query type | n |
|---|---|
| precise | 1317 |
| context | 404 |
| mixed | 476 |
| total | 2197 |

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap; budget view: top-N cap 20. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.0524 | 0.0630 | 0.0524 | 0.0630 | 0.0524 | 0.0630 | 0.0000 | 0.0091 | 0.0091 | 0.0091 |
| hybrid-rerank | nomic | fixed-128 | 0.0439 | 0.0569 | 0.0439 | 0.0569 | 0.0439 | 0.0569 | 0.0000 | 0.0141 | 0.0141 | 0.0141 |
| hybrid-rerank | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0000 | 0.5403 | 0.5403 | 0.5403 |
| hybrid-rerank | nomic | small-to-big | 0.0690 | 0.0839 | 0.0690 | 0.0839 | 0.0690 | 0.0839 | 0.0000 | 0.2358 | 0.2362 | 0.2362 |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.0879 | 0.0536 | 0.0879 | 0.0536 | 0.0879 | 0.0536 | 0.0000 | 0.0209 | 0.0209 | 0.0209 |
| hybrid-rerank | nomic | fixed-128 | 0.0936 | 0.0603 | 0.0936 | 0.0603 | 0.0936 | 0.0603 | 0.0000 | 0.0296 | 0.0296 | 0.0296 |
| hybrid-rerank | nomic | fixed-256 | 0.0620 | 0.0425 | 0.0620 | 0.0425 | 0.0620 | 0.0425 | 0.0000 | 0.0232 | 0.0232 | 0.0232 |
| hybrid-rerank | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0000 | 0.5844 | 0.5844 | 0.5844 |
| hybrid-rerank | nomic | small-to-big | 0.1066 | 0.0643 | 0.1066 | 0.0643 | 0.1066 | 0.0643 | 0.0000 | 0.4984 | 0.4989 | 0.4989 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.1241 | 0.0379 | 0.1241 | 0.0379 | 0.1241 | 0.0379 | 0.0000 | 0.0000 | 0.0460 | 0.0460 |
| hybrid-rerank | nomic | fixed-128 | 0.1411 | 0.0467 | 0.1411 | 0.0467 | 0.1411 | 0.0467 | 0.0000 | 0.0528 | 0.0528 | 0.0528 |
| hybrid-rerank | nomic | fixed-256 | 0.1249 | 0.0443 | 0.1249 | 0.0443 | 0.1249 | 0.0443 | 0.0000 | 0.0510 | 0.0510 | 0.0510 |
| hybrid-rerank | nomic | fixed-512 | 0.1006 | 0.0361 | 0.1006 | 0.0361 | 0.1006 | 0.0361 | 0.0000 | 0.0624 | 0.0624 | 0.0624 |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.0000 | 0.5576 | 0.5626 | 0.5626 |
| hybrid-rerank | nomic | small-to-big | 0.1640 | 0.0568 | 0.1640 | 0.0568 | 0.1640 | 0.0568 | 0.0000 | 0.6891 | 0.6946 | 0.6946 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1634 | 0.0255 | 0.1634 | 0.0255 | 0.0000 | 0.0000 | 0.1020 | 0.1020 |
| hybrid-rerank | nomic | fixed-128 | 0.1985 | 0.0338 | 0.1985 | 0.0336 | 0.1985 | 0.0336 | 0.0000 | 0.0000 | 0.0979 | 0.0979 |
| hybrid-rerank | nomic | fixed-256 | 0.2019 | 0.0352 | 0.2019 | 0.0352 | 0.2019 | 0.0352 | 0.0000 | 0.1070 | 0.1070 | 0.1070 |
| hybrid-rerank | nomic | fixed-512 | 0.1890 | 0.0356 | 0.1890 | 0.0356 | 0.1890 | 0.0356 | 0.0000 | 0.1302 | 0.1311 | 0.1311 |
| hybrid-rerank | nomic | fixed-1024 | 0.1509 | 0.0284 | 0.1509 | 0.0284 | 0.1509 | 0.0284 | 0.0000 | 0.0833 | 0.0833 | 0.0833 |
| hybrid-rerank | nomic | section-aware | 0.2471 | 0.0467 | 0.2480 | 0.0467 | 0.2480 | 0.0467 | 0.0000 | 0.5039 | 0.5831 | 0.5831 |
| hybrid-rerank | nomic | small-to-big | 0.2377 | 0.0444 | 0.2377 | 0.0444 | 0.2377 | 0.0444 | 0.0000 | 0.6545 | 0.7183 | 0.7183 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1732† | 0.0218† | 0.1910 | 0.0151 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.1985† | 0.0338† | 0.2434 | 0.0209 | 0.2434 | 0.0209 | 0.0000 | 0.0000 | 0.1893 | 0.1903 |
| hybrid-rerank | nomic | fixed-256 | 0.2599 | 0.0243 | 0.2599 | 0.0240 | 0.2599 | 0.0240 | 0.0000 | 0.0000 | 0.2089 | 0.2089 |
| hybrid-rerank | nomic | fixed-512 | 0.2596 | 0.0256 | 0.2596 | 0.0256 | 0.2596 | 0.0256 | 0.0000 | 0.2472 | 0.2576 | 0.2576 |
| hybrid-rerank | nomic | fixed-1024 | 0.2430 | 0.0241 | 0.2430 | 0.0241 | 0.2430 | 0.0241 | 0.0000 | 0.2012 | 0.2021 | 0.2021 |
| hybrid-rerank | nomic | section-aware | 0.3033† | 0.0320† | 0.3076 | 0.0297 | 0.3076 | 0.0297 | 0.0000 | 0.1202 | 0.5963 | 0.5976 |
| hybrid-rerank | nomic | small-to-big | 0.2933† | 0.0304† | 0.2975 | 0.0289 | 0.2975 | 0.0289 | 0.0000 | 0.1620 | 0.7137 | 0.7142 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1732† | 0.0218† | 0.2387 | 0.0096 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.1985† | 0.0338† | 0.2534† | 0.0174† | 0.2703 | 0.0116 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3000 | 0.0143 | 0.3000 | 0.0143 | 0.0000 | 0.0000 | 0.3855 | 0.3901 |
| hybrid-rerank | nomic | fixed-512 | 0.3202† | 0.0171† | 0.3209 | 0.0165 | 0.3209 | 0.0165 | 0.0000 | 0.0000 | 0.4779 | 0.4779 |
| hybrid-rerank | nomic | fixed-1024 | 0.3143 | 0.0166 | 0.3143 | 0.0166 | 0.3143 | 0.0166 | 0.0000 | 0.3842 | 0.4110 | 0.4110 |
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3429 | 0.0171 | 0.3443 | 0.0170 | 0.0000 | 0.0000 | 0.4693 | 0.7237 |
| hybrid-rerank | nomic | small-to-big | 0.3057† | 0.0273† | 0.3404 | 0.0166 | 0.3404 | 0.0166 | 0.0000 | 0.0000 | 0.7128 | 0.7806 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1732† | 0.0218† | 0.2862 | 0.0058 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.1985† | 0.0338† | 0.2534† | 0.0174† | 0.3286 | 0.0072 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3072† | 0.0120† | 0.3283 | 0.0080 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-512 | 0.3202† | 0.0171† | 0.3596 | 0.0094 | 0.3598 | 0.0094 | 0.0000 | 0.0000 | 0.6486 | 0.6850 |
| hybrid-rerank | nomic | fixed-1024 | 0.3692† | 0.0108† | 0.3708 | 0.0101 | 0.3708 | 0.0101 | 0.0000 | 0.0000 | 0.6618 | 0.6618 |
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3512† | 0.0136† | 0.3695 | 0.0091 | 0.0000 | 0.0000 | 0.0000 | 0.9672 |
| hybrid-rerank | nomic | small-to-big | 0.3057† | 0.0273† | 0.3584† | 0.0121† | 0.3696 | 0.0091 | 0.0000 | 0.0000 | 0.0132 | 0.9577 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
