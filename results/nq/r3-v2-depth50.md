# R3 - nq v2-depth50, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0640 | 0.0500 | -0.0140 | 0.0640 | 0.0500 | -0.0140 |
| section-aware | 256 | 0.2600 | 0.2286 | -0.0314 | 0.2600 | 0.2286 | -0.0314 |
| section-aware | 512 | 0.6900 | 0.6240 | -0.0660 | 0.6900 | 0.6240 | -0.0660 |
| section-aware | 1024 | 0.8402 | 0.8019 | -0.0383 | 0.8402 | 0.8019 | -0.0383 |
| section-aware | 2048 | 0.9160 | 0.8919 | -0.0241 | 0.9160 | 0.8939 | -0.0221 |
| section-aware | 4096 | 0.9420 | 0.9119 | -0.0301 | 0.9580 | 0.9519 | -0.0061 |
| section-aware | 8192 | 0.9420 | 0.9119 | -0.0301 | 0.9780 | 0.9779 | -0.0001 |
| section-aware-titles | 128 | 0.0740 | 0.0643 | -0.0097 | 0.0740 | 0.0643 | -0.0097 |
| section-aware-titles | 256 | 0.2760 | 0.2481 | -0.0279 | 0.2760 | 0.2481 | -0.0279 |
| section-aware-titles | 512 | 0.7040 | 0.6237 | -0.0803 | 0.7040 | 0.6237 | -0.0803 |
| section-aware-titles | 1024 | 0.8680 | 0.8396 | -0.0284 | 0.8680 | 0.8396 | -0.0284 |
| section-aware-titles | 2048 | 0.9440 | 0.9202 | -0.0238 | 0.9440 | 0.9202 | -0.0238 |
| section-aware-titles | 4096 | 0.9680 | 0.9520 | -0.0160 | 0.9800 | 0.9702 | -0.0098 |
| section-aware-titles | 8192 | 0.9680 | 0.9520 | -0.0160 | 0.9960 | 0.9922 | -0.0038 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
