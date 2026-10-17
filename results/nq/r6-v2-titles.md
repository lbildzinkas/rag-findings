# R6 - nq v2-titles, production line and ablations: short-answer span recall

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

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0600§ | 0.0600§ | 0.0021 |
| section-aware | 256 | 0.2402§ | 0.2402§ | 0.0041 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.0269 |
| section-aware | 1024 | 0.8613§ | 0.8613§ | 0.1366 |
| section-aware | 2048 | 0.9275†§ | 0.9275§ | 0.6936 |
| section-aware | 4096 | 0.9400† | 0.9482§ | 1.0000 |
| section-aware | 8192 | 0.9400† | 0.9731§ | 1.0000 |
| section-aware-titles | 128 | 0.0807§ | 0.0807§ | 0.2609 |
| section-aware-titles | 256 | 0.2733§ | 0.2733§ | 0.3168 |
| section-aware-titles | 512 | 0.7288§ | 0.7288§ | 0.3602 |
| section-aware-titles | 1024 | 0.8716†§ | 0.8716§ | 0.5342 |
| section-aware-titles | 2048 | 0.9503†§ | 0.9503§ | 0.8778 |
| section-aware-titles | 4096 | 0.9710† | 0.9752§ | 1.0000 |
| section-aware-titles | 8192 | 0.9710† | 0.9896§ | 1.0000 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
