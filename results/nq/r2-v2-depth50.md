# R2 - nq v2-depth50, production line and ablations: chunking x budget, collection search

Config hash: `c890dcea23c364405b79cd1aae2e9603ade83b11641b29c30a7397200f3beeb6`

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
  name: nq
  splits:
  - dev
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
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| section-aware | 128 | 0.0570§ | 0.0333§ | 0.0570§ | 0.0333§ | 0.0000 |
| section-aware | 256 | 0.2443§ | 0.0998§ | 0.2443§ | 0.0997§ | 0.0060 |
| section-aware | 512 | 0.6570§ | 0.1610§ | 0.6570§ | 0.1609§ | 0.0270 |
| section-aware | 1024 | 0.8210§ | 0.1077§ | 0.8210§ | 0.1073§ | 0.1440 |
| section-aware | 2048 | 0.9039†§ | 0.0648†§ | 0.9049§ | 0.0606§ | 0.7200 |
| section-aware | 4096 | 0.9269† | 0.0540† | 0.9549§ | 0.0325§ | 1.0000 |
| section-aware | 8192 | 0.9269† | 0.0540† | 0.9779§ | 0.0169§ | 1.0000 |
| section-aware-titles | 128 | 0.0691§ | 0.0400§ | 0.0691§ | 0.0396§ | 0.2790 |
| section-aware-titles | 256 | 0.2621§ | 0.1083§ | 0.2621§ | 0.1062§ | 0.3290 |
| section-aware-titles | 512 | 0.6638§ | 0.1702§ | 0.6638§ | 0.1670§ | 0.3730 |
| section-aware-titles | 1024 | 0.8538†§ | 0.1170†§ | 0.8538§ | 0.1131§ | 0.5850 |
| section-aware-titles | 2048 | 0.9321†§ | 0.0721†§ | 0.9321§ | 0.0630§ | 0.8770 |
| section-aware-titles | 4096 | 0.9600† | 0.0600† | 0.9751§ | 0.0334§ | 1.0000 |
| section-aware-titles | 8192 | 0.9600† | 0.0600† | 0.9941§ | 0.0172§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0570§ | 0.0333§ | 0.0000 |
| section-aware | 256 | 0.2443§ | 0.0997§ | 0.0000 |
| section-aware | 512 | 0.6570§ | 0.1609§ | 0.0000 |
| section-aware | 1024 | 0.8210§ | 0.1073§ | 0.0000 |
| section-aware | 2048 | 0.9049§ | 0.0606§ | 0.0000 |
| section-aware | 4096 | 0.9549§ | 0.0326§ | 0.0910 |
| section-aware | 8192 | 0.9689†§ | 0.0216†§ | 0.9910 |
| section-aware-titles | 128 | 0.0691§ | 0.0396§ | 0.0020 |
| section-aware-titles | 256 | 0.2621§ | 0.1062§ | 0.0000 |
| section-aware-titles | 512 | 0.6638§ | 0.1670§ | 0.0020 |
| section-aware-titles | 1024 | 0.8538§ | 0.1131§ | 0.0030 |
| section-aware-titles | 2048 | 0.9321§ | 0.0630§ | 0.0570 |
| section-aware-titles | 4096 | 0.9751§ | 0.0345§ | 0.4820 |
| section-aware-titles | 8192 | 0.9921†§ | 0.0254†§ | 0.9950 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0570§ | 0.0336§ | 0.0870 |
| section-aware | 256 | 0.2443§ | 0.1007§ | 0.2130 |
| section-aware | 512 | 0.6560§ | 0.1636§ | 0.3000 |
| section-aware | 1024 | 0.8180†§ | 0.1141†§ | 0.7080 |
| section-aware | 2048 | 0.8857†§ | 0.0859†§ | 0.9910 |
| section-aware | 4096 | 0.8927† | 0.0853† | 1.0000 |
| section-aware | 8192 | 0.8927† | 0.0853† | 1.0000 |
| section-aware-titles | 128 | 0.0691†§ | 0.0421†§ | 0.5960 |
| section-aware-titles | 256 | 0.2621†§ | 0.1144†§ | 0.6390 |
| section-aware-titles | 512 | 0.6638†§ | 0.1775†§ | 0.6730 |
| section-aware-titles | 1024 | 0.8538†§ | 0.1241†§ | 0.8680 |
| section-aware-titles | 2048 | 0.9161†§ | 0.0896†§ | 0.9950 |
| section-aware-titles | 4096 | 0.9160† | 0.0883† | 1.0000 |
| section-aware-titles | 8192 | 0.9160† | 0.0883† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 50 into the unreranked tail, which continues in fused (hybrid) order.
