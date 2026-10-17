# R3 - qasper v2-titles, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0357 | 0.0172 | -0.0184 | 0.0357 | 0.0172 | -0.0184 |
| section-aware | 256 | 0.0737 | 0.0324 | -0.0413 | 0.0737 | 0.0324 | -0.0413 |
| section-aware | 512 | 0.1678 | 0.1148 | -0.0530 | 0.1678 | 0.1148 | -0.0530 |
| section-aware | 1024 | 0.2536 | 0.2003 | -0.0533 | 0.2544 | 0.2003 | -0.0540 |
| section-aware | 2048 | 0.3098 | 0.2405 | -0.0693 | 0.3144 | 0.2451 | -0.0693 |
| section-aware | 4096 | 0.3166 | 0.2521 | -0.0646 | 0.3493 | 0.2828 | -0.0664 |
| section-aware | 8192 | 0.3166 | 0.2521 | -0.0646 | 0.3768 | 0.3164 | -0.0604 |
| section-aware-titles | 128 | 0.0418 | 0.0250 | -0.0168 | 0.0418 | 0.0250 | -0.0168 |
| section-aware-titles | 256 | 0.0767 | 0.0417 | -0.0350 | 0.0767 | 0.0417 | -0.0350 |
| section-aware-titles | 512 | 0.1853 | 0.1552 | -0.0301 | 0.1853 | 0.1552 | -0.0301 |
| section-aware-titles | 1024 | 0.2703 | 0.2188 | -0.0515 | 0.2703 | 0.2190 | -0.0513 |
| section-aware-titles | 2048 | 0.3242 | 0.2880 | -0.0363 | 0.3295 | 0.2949 | -0.0346 |
| section-aware-titles | 4096 | 0.3364 | 0.3007 | -0.0356 | 0.3667 | 0.3384 | -0.0284 |
| section-aware-titles | 8192 | 0.3364 | 0.3007 | -0.0356 | 0.3948 | 0.3670 | -0.0278 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
