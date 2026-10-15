# R3 - qasper v2-baseline, production line and ablations: chunk size x query type

Config hash: `28fc1dc15c8ac341b982544b402db094b15997c8b808cf9733d9f9d734cb51d7`

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
- chunk_tokens: 64
  method: fixed
  name: fixed-64
- chunk_tokens: 128
  method: fixed
  name: fixed-128
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- chunk_tokens: 512
  method: fixed
  name: fixed-512
- chunk_tokens: 1024
  method: fixed
  name: fixed-1024
- max_tokens: 512
  method: section_aware
  name: section-aware
- child_tokens: 128
  max_tokens: 512
  method: small_to_big
  name: small-to-big
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
run_name: v2-baseline
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
| fixed-64 | 128 | 0.0586 | 0.0341 | -0.0245 | 0.0586 | 0.0341 | -0.0245 |
| fixed-64 | 256 | 0.0972 | 0.0531 | -0.0442 | 0.0972 | 0.0531 | -0.0442 |
| fixed-64 | 512 | 0.1327 | 0.0783 | -0.0544 | 0.1327 | 0.0783 | -0.0544 |
| fixed-64 | 1024 | 0.1327 | 0.0783 | -0.0544 | 0.1716 | 0.1104 | -0.0612 |
| fixed-64 | 2048 | 0.1327 | 0.0783 | -0.0544 | 0.2000 | 0.1370 | -0.0629 |
| fixed-64 | 4096 | 0.1327 | 0.0783 | -0.0544 | 0.2504 | 0.1818 | -0.0686 |
| fixed-64 | 8192 | 0.1327 | 0.0783 | -0.0544 | 0.2991 | 0.2193 | -0.0798 |
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
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1062 | 0.0689 | -0.0373 | 0.1062 | 0.0689 | -0.0373 |
| fixed-512 | 1024 | 0.1944 | 0.1543 | -0.0401 | 0.1944 | 0.1543 | -0.0401 |
| fixed-512 | 2048 | 0.2638 | 0.2277 | -0.0361 | 0.2638 | 0.2277 | -0.0361 |
| fixed-512 | 4096 | 0.3216 | 0.2913 | -0.0304 | 0.3225 | 0.2914 | -0.0311 |
| fixed-512 | 8192 | 0.3216 | 0.2913 | -0.0304 | 0.3629 | 0.3312 | -0.0316 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1556 | 0.1146 | -0.0410 | 0.1556 | 0.1146 | -0.0410 |
| fixed-1024 | 2048 | 0.2441 | 0.1959 | -0.0482 | 0.2441 | 0.1959 | -0.0482 |
| fixed-1024 | 4096 | 0.3152 | 0.2786 | -0.0366 | 0.3152 | 0.2786 | -0.0366 |
| fixed-1024 | 8192 | 0.3683 | 0.3456 | -0.0226 | 0.3698 | 0.3473 | -0.0225 |
| section-aware | 128 | 0.0357 | 0.0172 | -0.0184 | 0.0357 | 0.0172 | -0.0184 |
| section-aware | 256 | 0.0737 | 0.0324 | -0.0413 | 0.0737 | 0.0324 | -0.0413 |
| section-aware | 512 | 0.1678 | 0.1148 | -0.0530 | 0.1678 | 0.1148 | -0.0530 |
| section-aware | 1024 | 0.2536 | 0.2003 | -0.0533 | 0.2544 | 0.2003 | -0.0540 |
| section-aware | 2048 | 0.3098 | 0.2405 | -0.0693 | 0.3144 | 0.2451 | -0.0693 |
| section-aware | 4096 | 0.3166 | 0.2521 | -0.0646 | 0.3493 | 0.2828 | -0.0664 |
| section-aware | 8192 | 0.3166 | 0.2521 | -0.0646 | 0.3768 | 0.3164 | -0.0604 |
| small-to-big | 128 | 0.0782 | 0.0316 | -0.0466 | 0.0782 | 0.0316 | -0.0466 |
| small-to-big | 256 | 0.1175 | 0.0596 | -0.0579 | 0.1175 | 0.0596 | -0.0579 |
| small-to-big | 512 | 0.1836 | 0.0914 | -0.0922 | 0.1836 | 0.0914 | -0.0922 |
| small-to-big | 1024 | 0.2528 | 0.1699 | -0.0830 | 0.2528 | 0.1699 | -0.0830 |
| small-to-big | 2048 | 0.3042 | 0.2360 | -0.0682 | 0.3098 | 0.2360 | -0.0738 |
| small-to-big | 4096 | 0.3144 | 0.2503 | -0.0640 | 0.3516 | 0.2826 | -0.0690 |
| small-to-big | 8192 | 0.3144 | 0.2503 | -0.0640 | 0.3783 | 0.3147 | -0.0636 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
