# R5 - qasper v2-depth50, production line and ablations: pipeline x embedder x chunking

Config hash: `c56e6f53497ce83caea0c09dd53e62c9c880ca19a18eb645ccce6b7b97c90651`

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
fixed_k:
- 1
- 5
- 10
kind: grid
pipelines:
- hybrid-rerank
rerank_depth: 50
rrf_k: 60
run_name: v2-depth50
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
| hybrid-rerank | nomic | section-aware | 0.0327 | 0.0300 | 0.0327 | 0.0300 | 0.0327 | 0.0300 | 0.0000 | 0.4629 | 0.4629 | 0.4629 |
| hybrid-rerank | nomic | section-aware-titles | 0.0372 | 0.0351 | 0.0372 | 0.0351 | 0.0372 | 0.0351 | 0.0000 | 0.6359 | 0.6359 | 0.6359 |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.0644 | 0.0372 | 0.0644 | 0.0372 | 0.0644 | 0.0372 | 0.0000 | 0.5052 | 0.5052 | 0.5052 |
| hybrid-rerank | nomic | section-aware-titles | 0.0696 | 0.0409 | 0.0696 | 0.0409 | 0.0696 | 0.0409 | 0.0000 | 0.6177 | 0.6181 | 0.6181 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.1597 | 0.0568 | 0.1597 | 0.0568 | 0.1597 | 0.0568 | 0.0000 | 0.4952 | 0.4966 | 0.4966 |
| hybrid-rerank | nomic | section-aware-titles | 0.1772 | 0.0638 | 0.1772 | 0.0638 | 0.1772 | 0.0638 | 0.0000 | 0.6336 | 0.6354 | 0.6354 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.2548 | 0.0476 | 0.2548 | 0.0475 | 0.2548 | 0.0475 | 0.0000 | 0.4333 | 0.4825 | 0.4825 |
| hybrid-rerank | nomic | section-aware-titles | 0.2704 | 0.0516 | 0.2704 | 0.0515 | 0.2704 | 0.0515 | 0.0000 | 0.5885 | 0.6491 | 0.6491 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3150† | 0.0336† | 0.3209 | 0.0312 | 0.3209 | 0.0312 | 0.0000 | 0.0979 | 0.5057 | 0.5066 |
| hybrid-rerank | nomic | section-aware-titles | 0.3400† | 0.0367† | 0.3476 | 0.0343 | 0.3476 | 0.0343 | 0.0000 | 0.1306 | 0.6509 | 0.6591 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3215† | 0.0312† | 0.3636 | 0.0180 | 0.3656 | 0.0179 | 0.0000 | 0.0000 | 0.3714 | 0.5366 |
| hybrid-rerank | nomic | section-aware-titles | 0.3519† | 0.0343† | 0.3907 | 0.0205 | 0.3927 | 0.0203 | 0.0000 | 0.0000 | 0.4816 | 0.6659 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.3215† | 0.0312† | 0.3781† | 0.0148† | 0.3972 | 0.0098 | 0.0000 | 0.0000 | 0.0000 | 0.7064 |
| hybrid-rerank | nomic | section-aware-titles | 0.3519† | 0.0343† | 0.4021† | 0.0161† | 0.4192 | 0.0109 | 0.0000 | 0.0000 | 0.0000 | 0.7852 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 50 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
