# R6 - nq v2-depth50, production line and ablations: short-answer span recall

Config hash: `c890dcea23c364405b79cd1aae2e9603ade83b11641b29c30a7397200f3beeb6`

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
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0642§ | 0.0642§ | 0.0000 |
| section-aware | 256 | 0.2422§ | 0.2422§ | 0.0083 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.0248 |
| section-aware | 1024 | 0.8634§ | 0.8634§ | 0.1553 |
| section-aware | 2048 | 0.9172†§ | 0.9172§ | 0.6853 |
| section-aware | 4096 | 0.9400† | 0.9524§ | 1.0000 |
| section-aware | 8192 | 0.9400† | 0.9752§ | 1.0000 |
| section-aware-titles | 128 | 0.0807§ | 0.0807§ | 0.2733 |
| section-aware-titles | 256 | 0.2733§ | 0.2733§ | 0.3354 |
| section-aware-titles | 512 | 0.7226§ | 0.7226§ | 0.3727 |
| section-aware-titles | 1024 | 0.8696†§ | 0.8696§ | 0.5631 |
| section-aware-titles | 2048 | 0.9482†§ | 0.9482§ | 0.8634 |
| section-aware-titles | 4096 | 0.9669† | 0.9793§ | 1.0000 |
| section-aware-titles | 8192 | 0.9669† | 0.9959§ | 1.0000 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 50 into the unreranked tail, which continues in fused (hybrid) order.
