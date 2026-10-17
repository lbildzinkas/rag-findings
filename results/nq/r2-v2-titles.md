# R2 - nq v2-titles, production line and ablations: chunking x budget, collection search

Config hash: `3bd1a0559ea19a538444eb855a7d0b93a494388536e92193c588ae8363f66b03`

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
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0580§ | 0.0339§ | 0.0010 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.2403§ | 0.0995§ | 0.0050 |
| section-aware | 512 | 0.6600§ | 0.1621§ | 0.6600§ | 0.1620§ | 0.0250 |
| section-aware | 1024 | 0.8197§ | 0.1072§ | 0.8197§ | 0.1067§ | 0.1390 |
| section-aware | 2048 | 0.9077†§ | 0.0650†§ | 0.9087§ | 0.0609§ | 0.7190 |
| section-aware | 4096 | 0.9299† | 0.0541† | 0.9489§ | 0.0322§ | 1.0000 |
| section-aware | 8192 | 0.9299† | 0.0541† | 0.9729§ | 0.0166§ | 1.0000 |
| section-aware-titles | 128 | 0.0701§ | 0.0405§ | 0.0701§ | 0.0400§ | 0.2650 |
| section-aware-titles | 256 | 0.2621§ | 0.1083§ | 0.2621§ | 0.1062§ | 0.3180 |
| section-aware-titles | 512 | 0.6678§ | 0.1723§ | 0.6678§ | 0.1689§ | 0.3640 |
| section-aware-titles | 1024 | 0.8558†§ | 0.1171†§ | 0.8558§ | 0.1132§ | 0.5690 |
| section-aware-titles | 2048 | 0.9401†§ | 0.0729†§ | 0.9401§ | 0.0636§ | 0.8700 |
| section-aware-titles | 4096 | 0.9641† | 0.0605† | 0.9721§ | 0.0334§ | 1.0000 |
| section-aware-titles | 8192 | 0.9641† | 0.0605† | 0.9901§ | 0.0170§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0000 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.0000 |
| section-aware | 512 | 0.6600§ | 0.1620§ | 0.0000 |
| section-aware | 1024 | 0.8197§ | 0.1067§ | 0.0000 |
| section-aware | 2048 | 0.9087§ | 0.0609§ | 0.0000 |
| section-aware | 4096 | 0.9489§ | 0.0323§ | 0.0730 |
| section-aware | 8192 | 0.9669†§ | 0.0211†§ | 0.9930 |
| section-aware-titles | 128 | 0.0701§ | 0.0400§ | 0.0020 |
| section-aware-titles | 256 | 0.2621§ | 0.1062§ | 0.0000 |
| section-aware-titles | 512 | 0.6678§ | 0.1689§ | 0.0020 |
| section-aware-titles | 1024 | 0.8558§ | 0.1132§ | 0.0020 |
| section-aware-titles | 2048 | 0.9401§ | 0.0637§ | 0.0600 |
| section-aware-titles | 4096 | 0.9721§ | 0.0344§ | 0.4800 |
| section-aware-titles | 8192 | 0.9891†§ | 0.0251†§ | 0.9980 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0840 |
| section-aware | 256 | 0.2403§ | 0.1003§ | 0.1960 |
| section-aware | 512 | 0.6600§ | 0.1645§ | 0.2710 |
| section-aware | 1024 | 0.8167†§ | 0.1136†§ | 0.6980 |
| section-aware | 2048 | 0.8887†§ | 0.0861†§ | 0.9920 |
| section-aware | 4096 | 0.8947† | 0.0856† | 1.0000 |
| section-aware | 8192 | 0.8947† | 0.0856† | 1.0000 |
| section-aware-titles | 128 | 0.0701†§ | 0.0425†§ | 0.5850 |
| section-aware-titles | 256 | 0.2621†§ | 0.1142†§ | 0.6360 |
| section-aware-titles | 512 | 0.6678†§ | 0.1795†§ | 0.6620 |
| section-aware-titles | 1024 | 0.8558†§ | 0.1242†§ | 0.8680 |
| section-aware-titles | 2048 | 0.9211†§ | 0.0902†§ | 0.9940 |
| section-aware-titles | 4096 | 0.9220† | 0.0889† | 1.0000 |
| section-aware-titles | 8192 | 0.9220† | 0.0889† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
