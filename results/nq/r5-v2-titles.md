# R5 - nq v2-titles, production line and ablations: pipeline x embedder x chunking

Config hash: `3bd1a0559ea19a538444eb855a7d0b93a494388536e92193c588ae8363f66b03`

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
  name: nq
  splits:
  - dev
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
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap; budget view: top-N cap 20. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0000 | 0.8370 | 0.8370 | 0.8370 |
| hybrid-rerank | nomic | section-aware-titles | 0.0701 | 0.0405 | 0.0701 | 0.0400 | 0.0701 | 0.0400 | 0.0000 | 0.7510 | 0.7970 | 0.7970 |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.0000 | 0.8450 | 0.8450 | 0.8450 |
| hybrid-rerank | nomic | section-aware-titles | 0.2621 | 0.1083 | 0.2621 | 0.1062 | 0.2621 | 0.1062 | 0.0000 | 0.7080 | 0.8030 | 0.8030 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.6600 | 0.1621 | 0.6600 | 0.1620 | 0.6600 | 0.1620 | 0.0000 | 0.8150 | 0.8160 | 0.8160 |
| hybrid-rerank | nomic | section-aware-titles | 0.6678 | 0.1723 | 0.6678 | 0.1689 | 0.6678 | 0.1689 | 0.0000 | 0.6480 | 0.7920 | 0.7920 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.8197 | 0.1072 | 0.8197 | 0.1067 | 0.8197 | 0.1067 | 0.0000 | 0.8150 | 0.8540 | 0.8540 |
| hybrid-rerank | nomic | section-aware-titles | 0.8558† | 0.1171† | 0.8558 | 0.1132 | 0.8558 | 0.1132 | 0.0000 | 0.5220 | 0.8290 | 0.8290 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9077† | 0.0650† | 0.9087 | 0.0609 | 0.9087 | 0.0609 | 0.0000 | 0.4330 | 0.8770 | 0.8770 |
| hybrid-rerank | nomic | section-aware-titles | 0.9401† | 0.0729† | 0.9401 | 0.0637 | 0.9401 | 0.0636 | 0.0000 | 0.3140 | 0.8660 | 0.8770 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9489 | 0.0323 | 0.9489 | 0.0322 | 0.0000 | 0.0000 | 0.8600 | 0.8970 |
| hybrid-rerank | nomic | section-aware-titles | 0.9641† | 0.0605† | 0.9721 | 0.0344 | 0.9721 | 0.0334 | 0.0000 | 0.0000 | 0.6640 | 0.9220 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9669† | 0.0211† | 0.9729 | 0.0166 | 0.0000 | 0.0000 | 0.0330 | 0.9590 |
| hybrid-rerank | nomic | section-aware-titles | 0.9641† | 0.0605† | 0.9891† | 0.0251† | 0.9901 | 0.0170 | 0.0000 | 0.0000 | 0.0230 | 0.9790 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
