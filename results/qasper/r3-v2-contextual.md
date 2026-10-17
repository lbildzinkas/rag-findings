# R3 - qasper v2-contextual, production line and ablations: chunk size x query type

Config hash: `01d4edda6b8a81e5cf45e9c645d840b44d539c024c91adadd154c8159ab1865d`

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
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- max_tokens: 512
  method: section_aware
  name: section-aware
- chunk_tokens: 256
  method: fixed
  name: contextual-256
  prefixes:
    model: mlx-community/Qwen3-8B-4bit
    prompt_sha256: 1f90604cbe2d345af3d3eb34108a12fb47626e6416e5dbdf9c39786f77bfef44
    revision: 545dc4251c05440727734bcd94334791f6ab0192
- chunk_tokens: 256
  method: fixed
  name: contextual-256-prefixed
  prefix_in_budget: true
  prefixes:
    model: mlx-community/Qwen3-8B-4bit
    prompt_sha256: 1f90604cbe2d345af3d3eb34108a12fb47626e6416e5dbdf9c39786f77bfef44
    revision: 545dc4251c05440727734bcd94334791f6ab0192
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
run_name: v2-contextual
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
| contextual-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1113 | 0.0741 | -0.0371 | 0.1113 | 0.0741 | -0.0371 |
| contextual-256 | 512 | 0.1672 | 0.1371 | -0.0301 | 0.1672 | 0.1371 | -0.0301 |
| contextual-256 | 1024 | 0.2324 | 0.2032 | -0.0292 | 0.2324 | 0.2032 | -0.0292 |
| contextual-256 | 2048 | 0.2957 | 0.2727 | -0.0230 | 0.2957 | 0.2727 | -0.0230 |
| contextual-256 | 4096 | 0.2957 | 0.2727 | -0.0230 | 0.3328 | 0.3205 | -0.0123 |
| contextual-256 | 8192 | 0.2957 | 0.2727 | -0.0230 | 0.3535 | 0.3396 | -0.0139 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0068 | 0.0000 | -0.0068 | 0.0068 | 0.0000 | -0.0068 |
| contextual-256-prefixed | 512 | 0.1157 | 0.0741 | -0.0415 | 0.1157 | 0.0741 | -0.0415 |
| contextual-256-prefixed | 1024 | 0.2053 | 0.1706 | -0.0347 | 0.2053 | 0.1706 | -0.0347 |
| contextual-256-prefixed | 2048 | 0.2774 | 0.2501 | -0.0273 | 0.2774 | 0.2501 | -0.0273 |
| contextual-256-prefixed | 4096 | 0.2957 | 0.2727 | -0.0230 | 0.3286 | 0.3125 | -0.0161 |
| contextual-256-prefixed | 8192 | 0.2957 | 0.2727 | -0.0230 | 0.3478 | 0.3352 | -0.0126 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
