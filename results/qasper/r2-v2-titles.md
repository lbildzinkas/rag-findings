# R2 - qasper v2-titles, production line and ablations: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.1570§ | 0.0555§ | 0.0073 |
| section-aware | 1024 | 0.2471§ | 0.0467§ | 0.2480§ | 0.0467§ | 0.1447 |
| section-aware | 2048 | 0.3033†§ | 0.0320†§ | 0.3076§ | 0.0297§ | 0.7975 |
| section-aware | 4096 | 0.3101† | 0.0300† | 0.3443§ | 0.0170§ | 1.0000 |
| section-aware | 8192 | 0.3101† | 0.0300† | 0.3695§ | 0.0091§ | 1.0000 |
| section-aware-titles | 128 | 0.0370§ | 0.0349§ | 0.0370§ | 0.0349§ | 0.0000 |
| section-aware-titles | 256 | 0.0693§ | 0.0411§ | 0.0693§ | 0.0411§ | 0.0005 |
| section-aware-titles | 512 | 0.1801§ | 0.0650§ | 0.1801§ | 0.0650§ | 0.0077 |
| section-aware-titles | 1024 | 0.2648§ | 0.0508§ | 0.2648§ | 0.0506§ | 0.1507 |
| section-aware-titles | 2048 | 0.3241†§ | 0.0352†§ | 0.3305§ | 0.0326§ | 0.8011 |
| section-aware-titles | 4096 | 0.3371† | 0.0330† | 0.3689§ | 0.0191§ | 1.0000 |
| section-aware-titles | 8192 | 0.3371† | 0.0330† | 0.3951§ | 0.0104§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.0000 |
| section-aware | 1024 | 0.2480§ | 0.0467§ | 0.0000 |
| section-aware | 2048 | 0.3076§ | 0.0297§ | 0.0032 |
| section-aware | 4096 | 0.3429§ | 0.0171§ | 0.3482 |
| section-aware | 8192 | 0.3512† | 0.0136† | 1.0000 |
| section-aware-titles | 128 | 0.0370§ | 0.0349§ | 0.0000 |
| section-aware-titles | 256 | 0.0693§ | 0.0411§ | 0.0000 |
| section-aware-titles | 512 | 0.1801§ | 0.0650§ | 0.0000 |
| section-aware-titles | 1024 | 0.2648§ | 0.0506§ | 0.0005 |
| section-aware-titles | 2048 | 0.3305§ | 0.0326§ | 0.0055 |
| section-aware-titles | 4096 | 0.3678§ | 0.0193§ | 0.3323 |
| section-aware-titles | 8192 | 0.3776† | 0.0152† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0187 |
| section-aware | 512 | 0.1570§ | 0.0557§ | 0.1452 |
| section-aware | 1024 | 0.2440†§ | 0.0488†§ | 0.6436 |
| section-aware | 2048 | 0.2774† | 0.0428† | 0.9977 |
| section-aware | 4096 | 0.2774† | 0.0428† | 1.0000 |
| section-aware | 8192 | 0.2774† | 0.0428† | 1.0000 |
| section-aware-titles | 128 | 0.0370§ | 0.0350§ | 0.0041 |
| section-aware-titles | 256 | 0.0693§ | 0.0412§ | 0.0282 |
| section-aware-titles | 512 | 0.1794§ | 0.0652§ | 0.1925 |
| section-aware-titles | 1024 | 0.2633†§ | 0.0531†§ | 0.6937 |
| section-aware-titles | 2048 | 0.3020† | 0.0467† | 0.9982 |
| section-aware-titles | 4096 | 0.3028† | 0.0468† | 1.0000 |
| section-aware-titles | 8192 | 0.3028† | 0.0468† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
