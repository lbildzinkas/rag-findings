# R2 - nq v2-baseline, production line and ablations: chunking x budget, collection search

Config hash: `b88ce9188b6e18537719b8dc5850675abc3f472d121b8683b761ac304b576f9f`

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
| fixed-64 | 128 | 0.2764 | 0.2335 | 0.2764 | 0.2335 | 0.0000 |
| fixed-64 | 256 | 0.3750 | 0.1613 | 0.3750 | 0.1613 | 0.0000 |
| fixed-64 | 512 | 0.4789 | 0.1077 | 0.4789 | 0.1077 | 0.0000 |
| fixed-64 | 1024 | 0.4789† | 0.1077† | 0.5779 | 0.0664 | 1.0000 |
| fixed-64 | 2048 | 0.4789† | 0.1077† | 0.6504§ | 0.0384§ | 1.0000 |
| fixed-64 | 4096 | 0.4789† | 0.1077† | 0.7466§ | 0.0227§ | 1.0000 |
| fixed-64 | 8192 | 0.4789† | 0.1077† | 0.8190§ | 0.0129§ | 1.0000 |
| fixed-128 | 128 | 0.2968 | 0.2642 | 0.2968 | 0.2642 | 0.0000 |
| fixed-128 | 256 | 0.4335 | 0.1970 | 0.4335 | 0.1970 | 0.0000 |
| fixed-128 | 512 | 0.5667 | 0.1321 | 0.5667 | 0.1321 | 0.0000 |
| fixed-128 | 1024 | 0.6887 | 0.0836 | 0.6887§ | 0.0836§ | 0.0010 |
| fixed-128 | 2048 | 0.6887† | 0.0836† | 0.7833§ | 0.0491§ | 1.0000 |
| fixed-128 | 4096 | 0.6887† | 0.0836† | 0.8357§ | 0.0267§ | 1.0000 |
| fixed-128 | 8192 | 0.6887† | 0.0836† | 0.8963§ | 0.0145§ | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.8439 | 0.0546 | 0.8439§ | 0.0546§ | 0.0080 |
| fixed-256 | 4096 | 0.8439† | 0.0546† | 0.9147§ | 0.0300§ | 1.0000 |
| fixed-256 | 8192 | 0.8439† | 0.0546† | 0.9488§ | 0.0159§ | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6104§ | 0.1477§ | 0.6104§ | 0.1477§ | 0.0000 |
| fixed-512 | 1024 | 0.7683§ | 0.0967§ | 0.7683§ | 0.0967§ | 0.0000 |
| fixed-512 | 2048 | 0.8720§ | 0.0576§ | 0.8720§ | 0.0576§ | 0.0000 |
| fixed-512 | 4096 | 0.9318 | 0.0318 | 0.9318§ | 0.0316§ | 0.1490 |
| fixed-512 | 8192 | 0.9318† | 0.0318† | 0.9722§ | 0.0167§ | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7406§ | 0.0947§ | 0.7406§ | 0.0947§ | 0.0010 |
| fixed-1024 | 2048 | 0.8577§ | 0.0571§ | 0.8577§ | 0.0571§ | 0.0010 |
| fixed-1024 | 4096 | 0.9255§ | 0.0315§ | 0.9255§ | 0.0315§ | 0.0030 |
| fixed-1024 | 8192 | 0.9705 | 0.0171 | 0.9705§ | 0.0167§ | 0.4060 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0580§ | 0.0339§ | 0.0010 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.2403§ | 0.0995§ | 0.0050 |
| section-aware | 512 | 0.6600§ | 0.1621§ | 0.6600§ | 0.1620§ | 0.0250 |
| section-aware | 1024 | 0.8197§ | 0.1072§ | 0.8197§ | 0.1067§ | 0.1390 |
| section-aware | 2048 | 0.9077†§ | 0.0650†§ | 0.9087§ | 0.0609§ | 0.7190 |
| section-aware | 4096 | 0.9299† | 0.0541† | 0.9489§ | 0.0322§ | 1.0000 |
| section-aware | 8192 | 0.9299† | 0.0541† | 0.9729§ | 0.0166§ | 1.0000 |
| small-to-big | 128 | 0.3320§ | 0.2940§ | 0.3320§ | 0.2940§ | 0.0010 |
| small-to-big | 256 | 0.4997§ | 0.2295§ | 0.4997§ | 0.2294§ | 0.0010 |
| small-to-big | 512 | 0.6541§ | 0.1628§ | 0.6541§ | 0.1627§ | 0.0150 |
| small-to-big | 1024 | 0.7871§ | 0.1022§ | 0.7871§ | 0.1020§ | 0.1570 |
| small-to-big | 2048 | 0.8774†§ | 0.0607†§ | 0.8774§ | 0.0581§ | 0.6830 |
| small-to-big | 4096 | 0.9089† | 0.0482† | 0.9304§ | 0.0313§ | 1.0000 |
| small-to-big | 8192 | 0.9089† | 0.0482† | 0.9559§ | 0.0162§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.2764 | 0.2335 | 0.0000 |
| fixed-64 | 256 | 0.3750 | 0.1613 | 0.0000 |
| fixed-64 | 512 | 0.4789 | 0.1077 | 0.0000 |
| fixed-64 | 1024 | 0.5779 | 0.0664 | 0.0000 |
| fixed-64 | 2048 | 0.6076† | 0.0562† | 1.0000 |
| fixed-64 | 4096 | 0.6076† | 0.0562† | 1.0000 |
| fixed-64 | 8192 | 0.6076† | 0.0562† | 1.0000 |
| fixed-128 | 128 | 0.2968 | 0.2642 | 0.0000 |
| fixed-128 | 256 | 0.4335 | 0.1970 | 0.0000 |
| fixed-128 | 512 | 0.5667 | 0.1321 | 0.0000 |
| fixed-128 | 1024 | 0.6887§ | 0.0836§ | 0.0000 |
| fixed-128 | 2048 | 0.7833§ | 0.0491§ | 0.0000 |
| fixed-128 | 4096 | 0.8038† | 0.0408† | 1.0000 |
| fixed-128 | 8192 | 0.8038† | 0.0408† | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.8439§ | 0.0546§ | 0.0000 |
| fixed-256 | 4096 | 0.9147§ | 0.0300§ | 0.0000 |
| fixed-256 | 8192 | 0.9247† | 0.0245† | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6104§ | 0.1477§ | 0.0000 |
| fixed-512 | 1024 | 0.7683§ | 0.0967§ | 0.0000 |
| fixed-512 | 2048 | 0.8720§ | 0.0576§ | 0.0000 |
| fixed-512 | 4096 | 0.9318§ | 0.0316§ | 0.0000 |
| fixed-512 | 8192 | 0.9722§ | 0.0167§ | 0.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7406§ | 0.0947§ | 0.0000 |
| fixed-1024 | 2048 | 0.8577§ | 0.0571§ | 0.0000 |
| fixed-1024 | 4096 | 0.9255§ | 0.0315§ | 0.0000 |
| fixed-1024 | 8192 | 0.9705§ | 0.0167§ | 0.0000 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0000 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.0000 |
| section-aware | 512 | 0.6600§ | 0.1620§ | 0.0000 |
| section-aware | 1024 | 0.8197§ | 0.1067§ | 0.0000 |
| section-aware | 2048 | 0.9087§ | 0.0609§ | 0.0000 |
| section-aware | 4096 | 0.9489§ | 0.0323§ | 0.0730 |
| section-aware | 8192 | 0.9669†§ | 0.0211†§ | 0.9930 |
| small-to-big | 128 | 0.3320§ | 0.2940§ | 0.0000 |
| small-to-big | 256 | 0.4997§ | 0.2294§ | 0.0000 |
| small-to-big | 512 | 0.6541§ | 0.1627§ | 0.0000 |
| small-to-big | 1024 | 0.7871§ | 0.1020§ | 0.0000 |
| small-to-big | 2048 | 0.8774§ | 0.0581§ | 0.0000 |
| small-to-big | 4096 | 0.9304§ | 0.0313§ | 0.0500 |
| small-to-big | 8192 | 0.9509†§ | 0.0196†§ | 0.9860 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.2764 | 0.2335 | 0.0000 |
| fixed-64 | 256 | 0.3750 | 0.1613 | 0.0000 |
| fixed-64 | 512 | 0.4046† | 0.1416† | 1.0000 |
| fixed-64 | 1024 | 0.4046† | 0.1416† | 1.0000 |
| fixed-64 | 2048 | 0.4046† | 0.1416† | 1.0000 |
| fixed-64 | 4096 | 0.4046† | 0.1416† | 1.0000 |
| fixed-64 | 8192 | 0.4046† | 0.1416† | 1.0000 |
| fixed-128 | 128 | 0.2968 | 0.2642 | 0.0000 |
| fixed-128 | 256 | 0.4335 | 0.1970 | 0.0000 |
| fixed-128 | 512 | 0.5667 | 0.1321 | 0.0000 |
| fixed-128 | 1024 | 0.6140† | 0.1169† | 1.0000 |
| fixed-128 | 2048 | 0.6140† | 0.1169† | 1.0000 |
| fixed-128 | 4096 | 0.6140† | 0.1169† | 1.0000 |
| fixed-128 | 8192 | 0.6140† | 0.1169† | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.7771† | 0.0786† | 1.0000 |
| fixed-256 | 4096 | 0.7771† | 0.0786† | 1.0000 |
| fixed-256 | 8192 | 0.7771† | 0.0786† | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6104§ | 0.1477§ | 0.0000 |
| fixed-512 | 1024 | 0.7683§ | 0.0967§ | 0.0010 |
| fixed-512 | 2048 | 0.8720§ | 0.0576§ | 0.0180 |
| fixed-512 | 4096 | 0.8940† | 0.0480† | 1.0000 |
| fixed-512 | 8192 | 0.8940† | 0.0480† | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7406§ | 0.0947§ | 0.0010 |
| fixed-1024 | 2048 | 0.8577§ | 0.0571§ | 0.0040 |
| fixed-1024 | 4096 | 0.9255§ | 0.0317§ | 0.1210 |
| fixed-1024 | 8192 | 0.9460† | 0.0266† | 1.0000 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0840 |
| section-aware | 256 | 0.2403§ | 0.1003§ | 0.1960 |
| section-aware | 512 | 0.6600§ | 0.1645§ | 0.2710 |
| section-aware | 1024 | 0.8167†§ | 0.1136†§ | 0.6980 |
| section-aware | 2048 | 0.8887†§ | 0.0861†§ | 0.9920 |
| section-aware | 4096 | 0.8947† | 0.0856† | 1.0000 |
| section-aware | 8192 | 0.8947† | 0.0856† | 1.0000 |
| small-to-big | 128 | 0.3320§ | 0.2941§ | 0.0140 |
| small-to-big | 256 | 0.4997§ | 0.2302§ | 0.0970 |
| small-to-big | 512 | 0.6541§ | 0.1646§ | 0.3030 |
| small-to-big | 1024 | 0.7839†§ | 0.1074†§ | 0.6940 |
| small-to-big | 2048 | 0.8511†§ | 0.0765†§ | 0.9970 |
| small-to-big | 4096 | 0.8559† | 0.0749† | 1.0000 |
| small-to-big | 8192 | 0.8559† | 0.0749† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
Re-run regression: fixed-512@512, fixed-1024@1024 and section-aware@512 deviate from v1's grid run by one question each; see `v2-baseline-regression.md`.
