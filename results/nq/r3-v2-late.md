# R3 - nq v2-late, production line and ablations: chunk size x query type

Config hash: `9ef43d53b9923e4098976e4539a9426dd274124f3e2e85c2e00d7827fc568dbd`

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
- chunk_tokens: 128
  method: fixed
  name: fixed-128
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- max_tokens: 512
  method: section_aware
  name: section-aware
- chunk_tokens: 128
  embedding: late
  method: fixed
  name: late-128
- chunk_tokens: 256
  embedding: late
  method: fixed
  name: late-256
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
run_name: v2-late
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
| fixed-128 | 128 | 0.3109 | 0.2826 | -0.0282 | 0.3109 | 0.2826 | -0.0282 |
| fixed-128 | 256 | 0.4560 | 0.4111 | -0.0449 | 0.4560 | 0.4111 | -0.0449 |
| fixed-128 | 512 | 0.5894 | 0.5440 | -0.0454 | 0.5894 | 0.5440 | -0.0454 |
| fixed-128 | 1024 | 0.6923 | 0.6852 | -0.0071 | 0.6923 | 0.6852 | -0.0071 |
| fixed-128 | 2048 | 0.6923 | 0.6852 | -0.0071 | 0.7893 | 0.7773 | -0.0120 |
| fixed-128 | 4096 | 0.6923 | 0.6852 | -0.0071 | 0.8420 | 0.8294 | -0.0126 |
| fixed-128 | 8192 | 0.6923 | 0.6852 | -0.0071 | 0.9064 | 0.8863 | -0.0201 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4441 | 0.4114 | -0.0328 | 0.4441 | 0.4114 | -0.0328 |
| fixed-256 | 512 | 0.6062 | 0.5887 | -0.0175 | 0.6062 | 0.5887 | -0.0175 |
| fixed-256 | 1024 | 0.7556 | 0.7145 | -0.0411 | 0.7556 | 0.7145 | -0.0411 |
| fixed-256 | 2048 | 0.8535 | 0.8342 | -0.0194 | 0.8535 | 0.8342 | -0.0194 |
| fixed-256 | 4096 | 0.8535 | 0.8342 | -0.0194 | 0.9202 | 0.9092 | -0.0110 |
| fixed-256 | 8192 | 0.8535 | 0.8342 | -0.0194 | 0.9577 | 0.9400 | -0.0177 |
| section-aware | 128 | 0.0620 | 0.0540 | -0.0080 | 0.0620 | 0.0540 | -0.0080 |
| section-aware | 256 | 0.2580 | 0.2226 | -0.0354 | 0.2580 | 0.2226 | -0.0354 |
| section-aware | 512 | 0.6940 | 0.6260 | -0.0680 | 0.6940 | 0.6260 | -0.0680 |
| section-aware | 1024 | 0.8415 | 0.7979 | -0.0436 | 0.8415 | 0.7979 | -0.0436 |
| section-aware | 2048 | 0.9275 | 0.8879 | -0.0396 | 0.9275 | 0.8899 | -0.0376 |
| section-aware | 4096 | 0.9460 | 0.9139 | -0.0321 | 0.9560 | 0.9419 | -0.0141 |
| section-aware | 8192 | 0.9460 | 0.9139 | -0.0321 | 0.9800 | 0.9659 | -0.0141 |
| late-128 | 128 | 0.3185 | 0.2861 | -0.0324 | 0.3185 | 0.2861 | -0.0324 |
| late-128 | 256 | 0.4706 | 0.4138 | -0.0568 | 0.4706 | 0.4138 | -0.0568 |
| late-128 | 512 | 0.6078 | 0.5716 | -0.0362 | 0.6078 | 0.5716 | -0.0362 |
| late-128 | 1024 | 0.7241 | 0.7113 | -0.0129 | 0.7241 | 0.7113 | -0.0129 |
| late-128 | 2048 | 0.7241 | 0.7113 | -0.0129 | 0.8446 | 0.8133 | -0.0314 |
| late-128 | 4096 | 0.7241 | 0.7113 | -0.0129 | 0.9110 | 0.8945 | -0.0165 |
| late-128 | 8192 | 0.7241 | 0.7113 | -0.0129 | 0.9731 | 0.9510 | -0.0220 |
| late-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.4454 | 0.4142 | -0.0312 | 0.4454 | 0.4142 | -0.0312 |
| late-256 | 512 | 0.6146 | 0.5987 | -0.0158 | 0.6146 | 0.5987 | -0.0158 |
| late-256 | 1024 | 0.7675 | 0.7189 | -0.0486 | 0.7675 | 0.7189 | -0.0486 |
| late-256 | 2048 | 0.8688 | 0.8494 | -0.0194 | 0.8688 | 0.8494 | -0.0194 |
| late-256 | 4096 | 0.8688 | 0.8494 | -0.0194 | 0.9416 | 0.9223 | -0.0194 |
| late-256 | 8192 | 0.8688 | 0.8494 | -0.0194 | 0.9775 | 0.9585 | -0.0190 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
