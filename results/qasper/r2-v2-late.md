# R2 - qasper v2-late, production line and ablations: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| fixed-128 | 128 | 0.0439§ | 0.0569§ | 0.0439§ | 0.0569§ | 0.0000 |
| fixed-128 | 256 | 0.0936§ | 0.0603§ | 0.0936§ | 0.0603§ | 0.0000 |
| fixed-128 | 512 | 0.1411§ | 0.0467§ | 0.1411§ | 0.0467§ | 0.0005 |
| fixed-128 | 1024 | 0.1985 | 0.0338 | 0.1985§ | 0.0336§ | 0.1065 |
| fixed-128 | 2048 | 0.1985† | 0.0338† | 0.2434§ | 0.0209§ | 1.0000 |
| fixed-128 | 4096 | 0.1985† | 0.0338† | 0.2703§ | 0.0116§ | 1.0000 |
| fixed-128 | 8192 | 0.1985† | 0.0338† | 0.3286§ | 0.0072§ | 1.0000 |
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
| late-128 | 128 | 0.0438§ | 0.0563§ | 0.0438§ | 0.0563§ | 0.0000 |
| late-128 | 256 | 0.0890§ | 0.0578§ | 0.0890§ | 0.0578§ | 0.0000 |
| late-128 | 512 | 0.1384§ | 0.0459§ | 0.1384§ | 0.0459§ | 0.0005 |
| late-128 | 1024 | 0.1946 | 0.0333 | 0.1946§ | 0.0330§ | 0.1707 |
| late-128 | 2048 | 0.1946† | 0.0333† | 0.2412§ | 0.0209§ | 1.0000 |
| late-128 | 4096 | 0.1946† | 0.0333† | 0.2673§ | 0.0120§ | 1.0000 |
| late-128 | 8192 | 0.1946† | 0.0333† | 0.3200§ | 0.0076§ | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.0614§ | 0.0417§ | 0.0614§ | 0.0417§ | 0.0000 |
| late-256 | 512 | 0.1199§ | 0.0418§ | 0.1199§ | 0.0418§ | 0.0000 |
| late-256 | 1024 | 0.1984§ | 0.0349§ | 0.1984§ | 0.0349§ | 0.0050 |
| late-256 | 2048 | 0.2590 | 0.0244 | 0.2593§ | 0.0242§ | 0.2417 |
| late-256 | 4096 | 0.2590† | 0.0244† | 0.2993§ | 0.0147§ | 1.0000 |
| late-256 | 8192 | 0.2590† | 0.0244† | 0.3230§ | 0.0081§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-128 | 128 | 0.0439§ | 0.0569§ | 0.0000 |
| fixed-128 | 256 | 0.0936§ | 0.0603§ | 0.0000 |
| fixed-128 | 512 | 0.1411§ | 0.0467§ | 0.0000 |
| fixed-128 | 1024 | 0.1985§ | 0.0336§ | 0.0000 |
| fixed-128 | 2048 | 0.2434§ | 0.0209§ | 0.0027 |
| fixed-128 | 4096 | 0.2534† | 0.0174† | 1.0000 |
| fixed-128 | 8192 | 0.2534† | 0.0174† | 1.0000 |
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
| late-128 | 128 | 0.0438§ | 0.0563§ | 0.0000 |
| late-128 | 256 | 0.0890§ | 0.0578§ | 0.0000 |
| late-128 | 512 | 0.1384§ | 0.0459§ | 0.0000 |
| late-128 | 1024 | 0.1946§ | 0.0330§ | 0.0000 |
| late-128 | 2048 | 0.2412§ | 0.0209§ | 0.0055 |
| late-128 | 4096 | 0.2519† | 0.0177† | 1.0000 |
| late-128 | 8192 | 0.2519† | 0.0177† | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a |
| late-256 | 256 | 0.0614§ | 0.0417§ | 0.0000 |
| late-256 | 512 | 0.1199§ | 0.0418§ | 0.0000 |
| late-256 | 1024 | 0.1984§ | 0.0349§ | 0.0000 |
| late-256 | 2048 | 0.2593§ | 0.0242§ | 0.0000 |
| late-256 | 4096 | 0.2993§ | 0.0147§ | 0.0209 |
| late-256 | 8192 | 0.3091† | 0.0125† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-128 | 128 | 0.0439§ | 0.0569§ | 0.0000 |
| fixed-128 | 256 | 0.0936§ | 0.0603§ | 0.0018 |
| fixed-128 | 512 | 0.1411§ | 0.0468§ | 0.0291 |
| fixed-128 | 1024 | 0.1578† | 0.0425† | 1.0000 |
| fixed-128 | 2048 | 0.1578† | 0.0425† | 1.0000 |
| fixed-128 | 4096 | 0.1578† | 0.0425† | 1.0000 |
| fixed-128 | 8192 | 0.1578† | 0.0425† | 1.0000 |
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
| late-128 | 128 | 0.0438§ | 0.0563§ | 0.0000 |
| late-128 | 256 | 0.0890§ | 0.0578§ | 0.0014 |
| late-128 | 512 | 0.1384§ | 0.0460§ | 0.0519 |
| late-128 | 1024 | 0.1560† | 0.0422† | 1.0000 |
| late-128 | 2048 | 0.1560† | 0.0422† | 1.0000 |
| late-128 | 4096 | 0.1560† | 0.0422† | 1.0000 |
| late-128 | 8192 | 0.1560† | 0.0422† | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a |
| late-256 | 256 | 0.0614§ | 0.0417§ | 0.0005 |
| late-256 | 512 | 0.1199§ | 0.0418§ | 0.0046 |
| late-256 | 1024 | 0.1984§ | 0.0350§ | 0.0674 |
| late-256 | 2048 | 0.2179† | 0.0315† | 1.0000 |
| late-256 | 4096 | 0.2179† | 0.0315† | 1.0000 |
| late-256 | 8192 | 0.2179† | 0.0315† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
