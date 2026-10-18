# R2 - qasper v2-depth50, production line and ablations: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0327§ | 0.0300§ | 0.0327§ | 0.0300§ | 0.0000 |
| section-aware | 256 | 0.0644§ | 0.0372§ | 0.0644§ | 0.0372§ | 0.0000 |
| section-aware | 512 | 0.1597§ | 0.0568§ | 0.1597§ | 0.0568§ | 0.0023 |
| section-aware | 1024 | 0.2548§ | 0.0476§ | 0.2548§ | 0.0475§ | 0.1120 |
| section-aware | 2048 | 0.3150†§ | 0.0336†§ | 0.3209§ | 0.0312§ | 0.7915 |
| section-aware | 4096 | 0.3215† | 0.0312† | 0.3656§ | 0.0179§ | 1.0000 |
| section-aware | 8192 | 0.3215† | 0.0312† | 0.3972§ | 0.0098§ | 1.0000 |
| section-aware-titles | 128 | 0.0372§ | 0.0351§ | 0.0372§ | 0.0351§ | 0.0000 |
| section-aware-titles | 256 | 0.0696§ | 0.0409§ | 0.0696§ | 0.0409§ | 0.0005 |
| section-aware-titles | 512 | 0.1772§ | 0.0638§ | 0.1772§ | 0.0638§ | 0.0050 |
| section-aware-titles | 1024 | 0.2704§ | 0.0516§ | 0.2704§ | 0.0515§ | 0.1088 |
| section-aware-titles | 2048 | 0.3400†§ | 0.0367†§ | 0.3476§ | 0.0343§ | 0.7902 |
| section-aware-titles | 4096 | 0.3519† | 0.0343† | 0.3927§ | 0.0203§ | 1.0000 |
| section-aware-titles | 8192 | 0.3519† | 0.0343† | 0.4192§ | 0.0109§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0327§ | 0.0300§ | 0.0000 |
| section-aware | 256 | 0.0644§ | 0.0372§ | 0.0000 |
| section-aware | 512 | 0.1597§ | 0.0568§ | 0.0000 |
| section-aware | 1024 | 0.2548§ | 0.0475§ | 0.0000 |
| section-aware | 2048 | 0.3209§ | 0.0312§ | 0.0018 |
| section-aware | 4096 | 0.3636§ | 0.0180§ | 0.3432 |
| section-aware | 8192 | 0.3781† | 0.0148† | 1.0000 |
| section-aware-titles | 128 | 0.0372§ | 0.0351§ | 0.0000 |
| section-aware-titles | 256 | 0.0696§ | 0.0409§ | 0.0000 |
| section-aware-titles | 512 | 0.1772§ | 0.0638§ | 0.0000 |
| section-aware-titles | 1024 | 0.2704§ | 0.0515§ | 0.0000 |
| section-aware-titles | 2048 | 0.3476§ | 0.0343§ | 0.0091 |
| section-aware-titles | 4096 | 0.3907§ | 0.0205§ | 0.3036 |
| section-aware-titles | 8192 | 0.4021† | 0.0161† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0327§ | 0.0300§ | 0.0000 |
| section-aware | 256 | 0.0644§ | 0.0372§ | 0.0132 |
| section-aware | 512 | 0.1597§ | 0.0569§ | 0.1429 |
| section-aware | 1024 | 0.2504†§ | 0.0493†§ | 0.6213 |
| section-aware | 2048 | 0.2888† | 0.0445† | 0.9982 |
| section-aware | 4096 | 0.2888† | 0.0445† | 1.0000 |
| section-aware | 8192 | 0.2888† | 0.0445† | 1.0000 |
| section-aware-titles | 128 | 0.0372§ | 0.0351§ | 0.0046 |
| section-aware-titles | 256 | 0.0696§ | 0.0410§ | 0.0305 |
| section-aware-titles | 512 | 0.1765§ | 0.0639§ | 0.1661 |
| section-aware-titles | 1024 | 0.2680†§ | 0.0538†§ | 0.6695 |
| section-aware-titles | 2048 | 0.3107† | 0.0475† | 0.9982 |
| section-aware-titles | 4096 | 0.3102† | 0.0473† | 1.0000 |
| section-aware-titles | 8192 | 0.3102† | 0.0473† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 50 into the unreranked tail, which continues in fused (hybrid) order.
