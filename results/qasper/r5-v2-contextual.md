# R5 - qasper v2-contextual, production line and ablations: pipeline x embedder x chunking

Config hash: `01d4edda6b8a81e5cf45e9c645d840b44d539c024c91adadd154c8159ab1865d`

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
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- max_tokens: 512
  method: section_aware
  name: section-aware
- chunk_tokens: 256
  method: fixed
  name: contextual-256
  prefixes:
    model: mlx-community/Qwen3-8B-4bit
    prompt_sha256: 1f90604cbe2d345af3d3eb34108a12fb47626e6416e5dbdf9c39786f77bfef44
    revision: 545dc4251c05440727734bcd94334791f6ab0192
- chunk_tokens: 256
  method: fixed
  name: contextual-256-prefixed
  prefix_in_budget: true
  prefixes:
    model: mlx-community/Qwen3-8B-4bit
    prompt_sha256: 1f90604cbe2d345af3d3eb34108a12fb47626e6416e5dbdf9c39786f77bfef44
    revision: 545dc4251c05440727734bcd94334791f6ab0192
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
run_name: v2-contextual
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
| hybrid-rerank | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0000 | 0.5403 | 0.5403 | 0.5403 |
| hybrid-rerank | nomic | contextual-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | contextual-256-prefixed | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.0620 | 0.0425 | 0.0620 | 0.0425 | 0.0620 | 0.0425 | 0.0000 | 0.0232 | 0.0232 | 0.0232 |
| hybrid-rerank | nomic | section-aware | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0000 | 0.5844 | 0.5844 | 0.5844 |
| hybrid-rerank | nomic | contextual-256 | 0.1056 | 0.0733 | 0.1056 | 0.0733 | 0.1056 | 0.0733 | 0.0000 | 0.0350 | 0.0350 | 0.0350 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.0049 | 0.0025 | 0.0049 | 0.0025 | 0.0049 | 0.0025 | 0.0000 | 0.8339 | 0.8339 | 0.8339 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.1249 | 0.0443 | 0.1249 | 0.0443 | 0.1249 | 0.0443 | 0.0000 | 0.0510 | 0.0510 | 0.0510 |
| hybrid-rerank | nomic | section-aware | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.0000 | 0.5576 | 0.5626 | 0.5626 |
| hybrid-rerank | nomic | contextual-256 | 0.1657 | 0.0593 | 0.1657 | 0.0593 | 0.1657 | 0.0593 | 0.0000 | 0.0724 | 0.0728 | 0.0728 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.1091 | 0.0387 | 0.1091 | 0.0387 | 0.1091 | 0.0387 | 0.0000 | 0.8079 | 0.8084 | 0.8084 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.2019 | 0.0352 | 0.2019 | 0.0352 | 0.2019 | 0.0352 | 0.0000 | 0.1070 | 0.1070 | 0.1070 |
| hybrid-rerank | nomic | section-aware | 0.2471 | 0.0467 | 0.2480 | 0.0467 | 0.2480 | 0.0467 | 0.0000 | 0.5039 | 0.5831 | 0.5831 |
| hybrid-rerank | nomic | contextual-256 | 0.2364 | 0.0424 | 0.2364 | 0.0424 | 0.2364 | 0.0424 | 0.0000 | 0.1315 | 0.1329 | 0.1329 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.2071 | 0.0374 | 0.2071 | 0.0374 | 0.2071 | 0.0374 | 0.0000 | 0.8398 | 0.8398 | 0.8398 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.2599 | 0.0243 | 0.2599 | 0.0240 | 0.2599 | 0.0240 | 0.0000 | 0.0000 | 0.2089 | 0.2089 |
| hybrid-rerank | nomic | section-aware | 0.3033† | 0.0320† | 0.3076 | 0.0297 | 0.3076 | 0.0297 | 0.0000 | 0.1202 | 0.5963 | 0.5976 |
| hybrid-rerank | nomic | contextual-256 | 0.2998 | 0.0291 | 0.2998 | 0.0287 | 0.2998 | 0.0287 | 0.0000 | 0.0000 | 0.2476 | 0.2481 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.2806 | 0.0267 | 0.2806 | 0.0265 | 0.2806 | 0.0265 | 0.0000 | 0.6791 | 0.7487 | 0.7487 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3000 | 0.0143 | 0.3000 | 0.0143 | 0.0000 | 0.0000 | 0.3855 | 0.3901 |
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3429 | 0.0171 | 0.3443 | 0.0170 | 0.0000 | 0.0000 | 0.4693 | 0.7237 |
| hybrid-rerank | nomic | contextual-256 | 0.2998† | 0.0291† | 0.3374 | 0.0167 | 0.3374 | 0.0167 | 0.0000 | 0.0000 | 0.4497 | 0.4561 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.2998† | 0.0249† | 0.3319 | 0.0164 | 0.3319 | 0.0164 | 0.0000 | 0.0000 | 0.8038 | 0.8061 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3072† | 0.0120† | 0.3283 | 0.0080 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3512† | 0.0136† | 0.3695 | 0.0091 | 0.0000 | 0.0000 | 0.0000 | 0.9672 |
| hybrid-rerank | nomic | contextual-256 | 0.2998† | 0.0291† | 0.3459† | 0.0142† | 0.3576 | 0.0091 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.2998† | 0.0249† | 0.3459† | 0.0121† | 0.3511 | 0.0089 | 0.0000 | 0.0000 | 0.0000 | 0.8694 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
