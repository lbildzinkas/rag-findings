# R4 - qasper v2-contextual, production line and ablations: fixed-k

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

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-256 | 0.0942 | 0.2895 | 0.3364 | 0.0575 | 0.2088 | 0.2566 |
| section-aware | 0.1111 | 0.2936 | 0.3464 | 0.1012 | 0.2765 | 0.3268 |
| contextual-256 | 0.1561 | 0.3277 | 0.3805 | 0.0973 | 0.2458 | 0.3027 |
| contextual-256-prefixed | 0.1561 | 0.3277 | 0.3805 | 0.0973 | 0.2458 | 0.3027 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
