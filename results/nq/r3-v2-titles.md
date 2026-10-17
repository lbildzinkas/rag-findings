# R3 - nq v2-titles, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0620 | 0.0540 | -0.0080 | 0.0620 | 0.0540 | -0.0080 |
| section-aware | 256 | 0.2580 | 0.2226 | -0.0354 | 0.2580 | 0.2226 | -0.0354 |
| section-aware | 512 | 0.6940 | 0.6260 | -0.0680 | 0.6940 | 0.6260 | -0.0680 |
| section-aware | 1024 | 0.8415 | 0.7979 | -0.0436 | 0.8415 | 0.7979 | -0.0436 |
| section-aware | 2048 | 0.9275 | 0.8879 | -0.0396 | 0.9275 | 0.8899 | -0.0376 |
| section-aware | 4096 | 0.9460 | 0.9139 | -0.0321 | 0.9560 | 0.9419 | -0.0141 |
| section-aware | 8192 | 0.9460 | 0.9139 | -0.0321 | 0.9800 | 0.9659 | -0.0141 |
| section-aware-titles | 128 | 0.0740 | 0.0663 | -0.0077 | 0.0740 | 0.0663 | -0.0077 |
| section-aware-titles | 256 | 0.2760 | 0.2481 | -0.0279 | 0.2760 | 0.2481 | -0.0279 |
| section-aware-titles | 512 | 0.7100 | 0.6257 | -0.0843 | 0.7100 | 0.6257 | -0.0843 |
| section-aware-titles | 1024 | 0.8680 | 0.8436 | -0.0244 | 0.8680 | 0.8436 | -0.0244 |
| section-aware-titles | 2048 | 0.9500 | 0.9302 | -0.0198 | 0.9500 | 0.9302 | -0.0198 |
| section-aware-titles | 4096 | 0.9740 | 0.9542 | -0.0198 | 0.9800 | 0.9642 | -0.0158 |
| section-aware-titles | 8192 | 0.9740 | 0.9542 | -0.0198 | 0.9940 | 0.9862 | -0.0078 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
