# R3 - qasper v2-depth50, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0364 | 0.0197 | -0.0168 | 0.0364 | 0.0197 | -0.0168 |
| section-aware | 256 | 0.0729 | 0.0393 | -0.0336 | 0.0729 | 0.0393 | -0.0336 |
| section-aware | 512 | 0.1701 | 0.1139 | -0.0561 | 0.1701 | 0.1139 | -0.0561 |
| section-aware | 1024 | 0.2642 | 0.2002 | -0.0640 | 0.2642 | 0.2002 | -0.0640 |
| section-aware | 2048 | 0.3166 | 0.2556 | -0.0610 | 0.3242 | 0.2629 | -0.0613 |
| section-aware | 4096 | 0.3257 | 0.2648 | -0.0609 | 0.3736 | 0.3023 | -0.0713 |
| section-aware | 8192 | 0.3257 | 0.2648 | -0.0609 | 0.4077 | 0.3312 | -0.0766 |
| section-aware-titles | 128 | 0.0418 | 0.0253 | -0.0165 | 0.0418 | 0.0253 | -0.0165 |
| section-aware-titles | 256 | 0.0790 | 0.0427 | -0.0362 | 0.0790 | 0.0427 | -0.0362 |
| section-aware-titles | 512 | 0.1838 | 0.1479 | -0.0358 | 0.1838 | 0.1479 | -0.0358 |
| section-aware-titles | 1024 | 0.2787 | 0.2214 | -0.0572 | 0.2787 | 0.2214 | -0.0572 |
| section-aware-titles | 2048 | 0.3409 | 0.3035 | -0.0374 | 0.3470 | 0.3159 | -0.0311 |
| section-aware-titles | 4096 | 0.3531 | 0.3133 | -0.0398 | 0.3872 | 0.3668 | -0.0204 |
| section-aware-titles | 8192 | 0.3531 | 0.3133 | -0.0398 | 0.4178 | 0.3890 | -0.0288 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
