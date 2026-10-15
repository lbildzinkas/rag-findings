# R2 - qasper v2-baseline, production line and ablations: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.0524§ | 0.0630§ | 0.0524§ | 0.0630§ | 0.0000 |
| fixed-64 | 256 | 0.0879§ | 0.0536§ | 0.0879§ | 0.0536§ | 0.0000 |
| fixed-64 | 512 | 0.1241 | 0.0379 | 0.1241§ | 0.0379§ | 0.0473 |
| fixed-64 | 1024 | 0.1241† | 0.0379† | 0.1634§ | 0.0255§ | 1.0000 |
| fixed-64 | 2048 | 0.1241† | 0.0379† | 0.1910§ | 0.0151§ | 1.0000 |
| fixed-64 | 4096 | 0.1241† | 0.0379† | 0.2387§ | 0.0096§ | 1.0000 |
| fixed-64 | 8192 | 0.1241† | 0.0379† | 0.2862§ | 0.0058§ | 1.0000 |
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
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1006§ | 0.0361§ | 0.1006§ | 0.0361§ | 0.0000 |
| fixed-512 | 1024 | 0.1890§ | 0.0356§ | 0.1890§ | 0.0356§ | 0.0027 |
| fixed-512 | 2048 | 0.2596§ | 0.0256§ | 0.2596§ | 0.0256§ | 0.0382 |
| fixed-512 | 4096 | 0.3202† | 0.0171† | 0.3209§ | 0.0165§ | 0.5448 |
| fixed-512 | 8192 | 0.3202† | 0.0171† | 0.3598§ | 0.0094§ | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1509§ | 0.0284§ | 0.1509§ | 0.0284§ | 0.0009 |
| fixed-1024 | 2048 | 0.2430§ | 0.0241§ | 0.2430§ | 0.0241§ | 0.0055 |
| fixed-1024 | 4096 | 0.3143§ | 0.0166§ | 0.3143§ | 0.0166§ | 0.0765 |
| fixed-1024 | 8192 | 0.3692† | 0.0108† | 0.3708§ | 0.0101§ | 0.7633 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.1570§ | 0.0555§ | 0.0073 |
| section-aware | 1024 | 0.2471§ | 0.0467§ | 0.2480§ | 0.0467§ | 0.1447 |
| section-aware | 2048 | 0.3033†§ | 0.0320†§ | 0.3076§ | 0.0297§ | 0.7975 |
| section-aware | 4096 | 0.3101† | 0.0300† | 0.3443§ | 0.0170§ | 1.0000 |
| section-aware | 8192 | 0.3101† | 0.0300† | 0.3695§ | 0.0091§ | 1.0000 |
| small-to-big | 128 | 0.0690§ | 0.0839§ | 0.0690§ | 0.0839§ | 0.0005 |
| small-to-big | 256 | 0.1066§ | 0.0643§ | 0.1066§ | 0.0643§ | 0.0009 |
| small-to-big | 512 | 0.1640§ | 0.0568§ | 0.1640§ | 0.0568§ | 0.0132 |
| small-to-big | 1024 | 0.2377§ | 0.0444§ | 0.2377§ | 0.0444§ | 0.1270 |
| small-to-big | 2048 | 0.2933†§ | 0.0304†§ | 0.2975§ | 0.0289§ | 0.7993 |
| small-to-big | 4096 | 0.3057† | 0.0273† | 0.3404§ | 0.0166§ | 1.0000 |
| small-to-big | 8192 | 0.3057† | 0.0273† | 0.3696§ | 0.0091§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.0524§ | 0.0630§ | 0.0000 |
| fixed-64 | 256 | 0.0879§ | 0.0536§ | 0.0000 |
| fixed-64 | 512 | 0.1241§ | 0.0379§ | 0.0000 |
| fixed-64 | 1024 | 0.1634§ | 0.0255§ | 0.0005 |
| fixed-64 | 2048 | 0.1732† | 0.0218† | 1.0000 |
| fixed-64 | 4096 | 0.1732† | 0.0218† | 1.0000 |
| fixed-64 | 8192 | 0.1732† | 0.0218† | 1.0000 |
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
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1006§ | 0.0361§ | 0.0000 |
| fixed-512 | 1024 | 0.1890§ | 0.0356§ | 0.0000 |
| fixed-512 | 2048 | 0.2596§ | 0.0256§ | 0.0000 |
| fixed-512 | 4096 | 0.3209§ | 0.0165§ | 0.0000 |
| fixed-512 | 8192 | 0.3596§ | 0.0094§ | 0.1356 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1509§ | 0.0284§ | 0.0000 |
| fixed-1024 | 2048 | 0.2430§ | 0.0241§ | 0.0000 |
| fixed-1024 | 4096 | 0.3143§ | 0.0166§ | 0.0000 |
| fixed-1024 | 8192 | 0.3708§ | 0.0101§ | 0.0005 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0000 |
| section-aware | 512 | 0.1570§ | 0.0555§ | 0.0000 |
| section-aware | 1024 | 0.2480§ | 0.0467§ | 0.0000 |
| section-aware | 2048 | 0.3076§ | 0.0297§ | 0.0032 |
| section-aware | 4096 | 0.3429§ | 0.0171§ | 0.3482 |
| section-aware | 8192 | 0.3512† | 0.0136† | 1.0000 |
| small-to-big | 128 | 0.0690§ | 0.0839§ | 0.0000 |
| small-to-big | 256 | 0.1066§ | 0.0643§ | 0.0000 |
| small-to-big | 512 | 0.1640§ | 0.0568§ | 0.0000 |
| small-to-big | 1024 | 0.2377§ | 0.0444§ | 0.0000 |
| small-to-big | 2048 | 0.2975§ | 0.0289§ | 0.0005 |
| small-to-big | 4096 | 0.3404§ | 0.0166§ | 0.1152 |
| small-to-big | 8192 | 0.3584†§ | 0.0121†§ | 0.9995 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.0524§ | 0.0630§ | 0.0005 |
| fixed-64 | 256 | 0.0879§ | 0.0537§ | 0.0118 |
| fixed-64 | 512 | 0.0964† | 0.0474† | 1.0000 |
| fixed-64 | 1024 | 0.0964† | 0.0474† | 1.0000 |
| fixed-64 | 2048 | 0.0964† | 0.0474† | 1.0000 |
| fixed-64 | 4096 | 0.0964† | 0.0474† | 1.0000 |
| fixed-64 | 8192 | 0.0964† | 0.0474† | 1.0000 |
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
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1006§ | 0.0361§ | 0.0168 |
| fixed-512 | 1024 | 0.1890§ | 0.0357§ | 0.0432 |
| fixed-512 | 2048 | 0.2596§ | 0.0259§ | 0.2499 |
| fixed-512 | 4096 | 0.2819† | 0.0230† | 1.0000 |
| fixed-512 | 8192 | 0.2819† | 0.0230† | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1509§ | 0.0284§ | 0.0141 |
| fixed-1024 | 2048 | 0.2430§ | 0.0242§ | 0.0742 |
| fixed-1024 | 4096 | 0.3139§ | 0.0170§ | 0.4201 |
| fixed-1024 | 8192 | 0.3330† | 0.0152† | 1.0000 |
| section-aware | 128 | 0.0315§ | 0.0292§ | 0.0000 |
| section-aware | 256 | 0.0634§ | 0.0365§ | 0.0187 |
| section-aware | 512 | 0.1570§ | 0.0557§ | 0.1452 |
| section-aware | 1024 | 0.2440†§ | 0.0488†§ | 0.6436 |
| section-aware | 2048 | 0.2774† | 0.0428† | 0.9977 |
| section-aware | 4096 | 0.2774† | 0.0428† | 1.0000 |
| section-aware | 8192 | 0.2774† | 0.0428† | 1.0000 |
| small-to-big | 128 | 0.0690§ | 0.0839§ | 0.0137 |
| small-to-big | 256 | 0.1066§ | 0.0643§ | 0.0633 |
| small-to-big | 512 | 0.1640§ | 0.0573§ | 0.2622 |
| small-to-big | 1024 | 0.2345†§ | 0.0462†§ | 0.7301 |
| small-to-big | 2048 | 0.2600† | 0.0374† | 0.9973 |
| small-to-big | 4096 | 0.2601† | 0.0374† | 1.0000 |
| small-to-big | 8192 | 0.2601† | 0.0374† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
