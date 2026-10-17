# R2 - qasper v2-contextual, production line and ablations: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620§ | 0.0425§ | 0.0620§ | 0.0425§ | 0.0000 |
| fixed-256 | 512 | 0.1249§ | 0.0443§ | 0.1249§ | 0.0443§ | 0.0000 |
| fixed-256 | 1024 | 0.2019§ | 0.0352§ | 0.2019§ | 0.0352§ | 0.0023 |
| fixed-256 | 2048 | 0.2599 | 0.0243 | 0.2599§ | 0.0240§ | 0.2294 |
| fixed-256 | 4096 | 0.2599† | 0.0243† | 0.3000§ | 0.0143§ | 1.0000 |
| fixed-256 | 8192 | 0.2599† | 0.0243† | 0.3283§ | 0.0080§ | 1.0000 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.1570§ | 0.0555§ | 0.0073 |
| section-aware | 1024 | 0.2471§ | 0.0467§ | 0.2480§ | 0.0467§ | 0.1447 |
| section-aware | 2048 | 0.3033†§ | 0.0320†§ | 0.3076§ | 0.0297§ | 0.7975 |
| section-aware | 4096 | 0.3101† | 0.0300† | 0.3443§ | 0.0170§ | 1.0000 |
| section-aware | 8192 | 0.3101† | 0.0300† | 0.3695§ | 0.0091§ | 1.0000 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1056§ | 0.0733§ | 0.1056§ | 0.0733§ | 0.0000 |
| contextual-256 | 512 | 0.1657§ | 0.0593§ | 0.1657§ | 0.0593§ | 0.0014 |
| contextual-256 | 1024 | 0.2364§ | 0.0424§ | 0.2364§ | 0.0424§ | 0.0155 |
| contextual-256 | 2048 | 0.2998 | 0.0291 | 0.2998§ | 0.0287§ | 0.2594 |
| contextual-256 | 4096 | 0.2998† | 0.0291† | 0.3374§ | 0.0167§ | 1.0000 |
| contextual-256 | 8192 | 0.2998† | 0.0291† | 0.3576§ | 0.0091§ | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0049§ | 0.0025§ | 0.0049§ | 0.0025§ | 0.0000 |
| contextual-256-prefixed | 512 | 0.1091§ | 0.0387§ | 0.1091§ | 0.0387§ | 0.0005 |
| contextual-256-prefixed | 1024 | 0.2071§ | 0.0374§ | 0.2071§ | 0.0374§ | 0.0005 |
| contextual-256-prefixed | 2048 | 0.2806§ | 0.0267§ | 0.2806§ | 0.0265§ | 0.2581 |
| contextual-256-prefixed | 4096 | 0.2998† | 0.0249† | 0.3319§ | 0.0164§ | 1.0000 |
| contextual-256-prefixed | 8192 | 0.2998† | 0.0249† | 0.3511§ | 0.0089§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620§ | 0.0425§ | 0.0000 |
| fixed-256 | 512 | 0.1249§ | 0.0443§ | 0.0000 |
| fixed-256 | 1024 | 0.2019§ | 0.0352§ | 0.0000 |
| fixed-256 | 2048 | 0.2599§ | 0.0240§ | 0.0000 |
| fixed-256 | 4096 | 0.3000§ | 0.0143§ | 0.0127 |
| fixed-256 | 8192 | 0.3072† | 0.0120† | 1.0000 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.0000 |
| section-aware | 1024 | 0.2480§ | 0.0467§ | 0.0000 |
| section-aware | 2048 | 0.3076§ | 0.0297§ | 0.0032 |
| section-aware | 4096 | 0.3429§ | 0.0171§ | 0.3482 |
| section-aware | 8192 | 0.3512† | 0.0136† | 1.0000 |
| contextual-256 | 128 | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1056§ | 0.0733§ | 0.0000 |
| contextual-256 | 512 | 0.1657§ | 0.0593§ | 0.0000 |
| contextual-256 | 1024 | 0.2364§ | 0.0424§ | 0.0000 |
| contextual-256 | 2048 | 0.2998§ | 0.0287§ | 0.0014 |
| contextual-256 | 4096 | 0.3374§ | 0.0167§ | 0.0719 |
| contextual-256 | 8192 | 0.3459† | 0.0142† | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0049§ | 0.0025§ | 0.0000 |
| contextual-256-prefixed | 512 | 0.1091§ | 0.0387§ | 0.0000 |
| contextual-256-prefixed | 1024 | 0.2071§ | 0.0374§ | 0.0000 |
| contextual-256-prefixed | 2048 | 0.2806§ | 0.0265§ | 0.0000 |
| contextual-256-prefixed | 4096 | 0.3319§ | 0.0164§ | 0.0032 |
| contextual-256-prefixed | 8192 | 0.3459† | 0.0121† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620§ | 0.0425§ | 0.0000 |
| fixed-256 | 512 | 0.1249§ | 0.0443§ | 0.0036 |
| fixed-256 | 1024 | 0.2019§ | 0.0353§ | 0.0701 |
| fixed-256 | 2048 | 0.2242† | 0.0325† | 1.0000 |
| fixed-256 | 4096 | 0.2242† | 0.0325† | 1.0000 |
| fixed-256 | 8192 | 0.2242† | 0.0325† | 1.0000 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0187 |
| section-aware | 512 | 0.1570§ | 0.0557§ | 0.1452 |
| section-aware | 1024 | 0.2440†§ | 0.0488†§ | 0.6436 |
| section-aware | 2048 | 0.2774† | 0.0428† | 0.9977 |
| section-aware | 4096 | 0.2774† | 0.0428† | 1.0000 |
| section-aware | 8192 | 0.2774† | 0.0428† | 1.0000 |
| contextual-256 | 128 | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1056§ | 0.0733§ | 0.0050 |
| contextual-256 | 512 | 0.1657§ | 0.0593§ | 0.0259 |
| contextual-256 | 1024 | 0.2364§ | 0.0425§ | 0.1224 |
| contextual-256 | 2048 | 0.2606† | 0.0389† | 1.0000 |
| contextual-256 | 4096 | 0.2606† | 0.0389† | 1.0000 |
| contextual-256 | 8192 | 0.2606† | 0.0389† | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0049§ | 0.0025§ | 0.0009 |
| contextual-256-prefixed | 512 | 0.1091§ | 0.0387§ | 0.0014 |
| contextual-256-prefixed | 1024 | 0.2071§ | 0.0375§ | 0.0633 |
| contextual-256-prefixed | 2048 | 0.2606† | 0.0333† | 1.0000 |
| contextual-256-prefixed | 4096 | 0.2606† | 0.0333† | 1.0000 |
| contextual-256-prefixed | 8192 | 0.2606† | 0.0333† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
