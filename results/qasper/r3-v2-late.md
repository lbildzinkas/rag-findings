# R3 - qasper v2-late, production line and ablations: chunk size x query type

Config hash: `4681531b4fc2cba80eacfd6d6d987877685b745fa621c2cfb91bede19c7a8be7`

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
| fixed-128 | 128 | 0.0476 | 0.0278 | -0.0197 | 0.0476 | 0.0278 | -0.0197 |
| fixed-128 | 256 | 0.1011 | 0.0593 | -0.0418 | 0.1011 | 0.0593 | -0.0418 |
| fixed-128 | 512 | 0.1520 | 0.0914 | -0.0606 | 0.1520 | 0.0914 | -0.0606 |
| fixed-128 | 1024 | 0.2103 | 0.1417 | -0.0686 | 0.2103 | 0.1417 | -0.0686 |
| fixed-128 | 2048 | 0.2103 | 0.1417 | -0.0686 | 0.2535 | 0.1857 | -0.0678 |
| fixed-128 | 4096 | 0.2103 | 0.1417 | -0.0686 | 0.2808 | 0.2101 | -0.0706 |
| fixed-128 | 8192 | 0.2103 | 0.1417 | -0.0686 | 0.3379 | 0.2660 | -0.0718 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0646 | 0.0433 | -0.0213 | 0.0646 | 0.0433 | -0.0213 |
| fixed-256 | 512 | 0.1332 | 0.0861 | -0.0471 | 0.1332 | 0.0861 | -0.0471 |
| fixed-256 | 1024 | 0.2048 | 0.1481 | -0.0567 | 0.2048 | 0.1481 | -0.0567 |
| fixed-256 | 2048 | 0.2603 | 0.2208 | -0.0396 | 0.2603 | 0.2208 | -0.0396 |
| fixed-256 | 4096 | 0.2603 | 0.2208 | -0.0396 | 0.3022 | 0.2611 | -0.0411 |
| fixed-256 | 8192 | 0.2603 | 0.2208 | -0.0396 | 0.3318 | 0.2896 | -0.0422 |
| section-aware | 128 | 0.0357 | 0.0172 | -0.0184 | 0.0357 | 0.0172 | -0.0184 |
| section-aware | 256 | 0.0737 | 0.0324 | -0.0413 | 0.0737 | 0.0324 | -0.0413 |
| section-aware | 512 | 0.1678 | 0.1148 | -0.0530 | 0.1678 | 0.1148 | -0.0530 |
| section-aware | 1024 | 0.2536 | 0.2003 | -0.0533 | 0.2544 | 0.2003 | -0.0540 |
| section-aware | 2048 | 0.3098 | 0.2405 | -0.0693 | 0.3144 | 0.2451 | -0.0693 |
| section-aware | 4096 | 0.3166 | 0.2521 | -0.0646 | 0.3493 | 0.2828 | -0.0664 |
| section-aware | 8192 | 0.3166 | 0.2521 | -0.0646 | 0.3768 | 0.3164 | -0.0604 |
| late-128 | 128 | 0.0463 | 0.0299 | -0.0164 | 0.0463 | 0.0299 | -0.0164 |
| late-128 | 256 | 0.0966 | 0.0613 | -0.0352 | 0.0966 | 0.0613 | -0.0352 |
| late-128 | 512 | 0.1484 | 0.0962 | -0.0522 | 0.1484 | 0.0962 | -0.0522 |
| late-128 | 1024 | 0.2030 | 0.1492 | -0.0538 | 0.2030 | 0.1492 | -0.0538 |
| late-128 | 2048 | 0.2030 | 0.1492 | -0.0538 | 0.2462 | 0.1922 | -0.0540 |
| late-128 | 4096 | 0.2030 | 0.1492 | -0.0538 | 0.2734 | 0.2212 | -0.0522 |
| late-128 | 8192 | 0.2030 | 0.1492 | -0.0538 | 0.3241 | 0.2747 | -0.0495 |
| late-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.0623 | 0.0456 | -0.0168 | 0.0623 | 0.0456 | -0.0168 |
| late-256 | 512 | 0.1277 | 0.0761 | -0.0516 | 0.1277 | 0.0761 | -0.0516 |
| late-256 | 1024 | 0.1975 | 0.1522 | -0.0453 | 0.1975 | 0.1522 | -0.0453 |
| late-256 | 2048 | 0.2584 | 0.2297 | -0.0288 | 0.2586 | 0.2297 | -0.0290 |
| late-256 | 4096 | 0.2584 | 0.2297 | -0.0288 | 0.2990 | 0.2696 | -0.0294 |
| late-256 | 8192 | 0.2584 | 0.2297 | -0.0288 | 0.3262 | 0.2853 | -0.0408 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
