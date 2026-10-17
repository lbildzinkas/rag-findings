# R5 - qasper v2-titles, production line and ablations: pipeline x embedder x chunking

Config hash: `0b60e4811932349583d9714f63881085d1a05ccf6f3a85633dc11623bbb3d908`

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
- max_tokens: 512
  method: section_aware
  name: section-aware
- max_tokens: 512
  method: section_aware
  name: section-aware-titles
  titles: true
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
run_name: v2-titles
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
| hybrid-rerank | nomic | section-aware | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0000 | 0.5403 | 0.5403 | 0.5403 |
| hybrid-rerank | nomic | section-aware-titles | 0.0370 | 0.0349 | 0.0370 | 0.0349 | 0.0370 | 0.0349 | 0.0000 | 0.6982 | 0.6982 | 0.6982 |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0000 | 0.5844 | 0.5844 | 0.5844 |
| hybrid-rerank | nomic | section-aware-titles | 0.0693 | 0.0411 | 0.0693 | 0.0411 | 0.0693 | 0.0411 | 0.0000 | 0.6750 | 0.6755 | 0.6755 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.0000 | 0.5576 | 0.5626 | 0.5626 |
| hybrid-rerank | nomic | section-aware-titles | 0.1801 | 0.0650 | 0.1801 | 0.0650 | 0.1801 | 0.0650 | 0.0000 | 0.7082 | 0.7137 | 0.7137 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.2471 | 0.0467 | 0.2480 | 0.0467 | 0.2480 | 0.0467 | 0.0000 | 0.5039 | 0.5831 | 0.5831 |
| hybrid-rerank | nomic | section-aware-titles | 0.2648 | 0.0508 | 0.2648 | 0.0506 | 0.2648 | 0.0506 | 0.0000 | 0.6395 | 0.7246 | 0.7251 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3033† | 0.0320† | 0.3076 | 0.0297 | 0.3076 | 0.0297 | 0.0000 | 0.1202 | 0.5963 | 0.5976 |
| hybrid-rerank | nomic | section-aware-titles | 0.3241† | 0.0352† | 0.3305 | 0.0326 | 0.3305 | 0.0326 | 0.0000 | 0.1607 | 0.7287 | 0.7328 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3429 | 0.0171 | 0.3443 | 0.0170 | 0.0000 | 0.0000 | 0.4693 | 0.7237 |
| hybrid-rerank | nomic | section-aware-titles | 0.3371† | 0.0330† | 0.3678 | 0.0193 | 0.3689 | 0.0191 | 0.0000 | 0.0000 | 0.5589 | 0.7975 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3101† | 0.0300† | 0.3512† | 0.0136† | 0.3695 | 0.0091 | 0.0000 | 0.0000 | 0.0000 | 0.9672 |
| hybrid-rerank | nomic | section-aware-titles | 0.3371† | 0.0330† | 0.3776† | 0.0152† | 0.3951 | 0.0104 | 0.0000 | 0.0000 | 0.0000 | 0.9731 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
