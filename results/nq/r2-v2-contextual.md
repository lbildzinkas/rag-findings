# R2 - nq v2-contextual, production line and ablations: chunking x budget, collection search

Config hash: `c2b3f7a5067ebfe8fd56be5157f08019a7f985aa9c57fe528db93ecf9397a053`

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
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.8439 | 0.0546 | 0.8439§ | 0.0546§ | 0.0080 |
| fixed-256 | 4096 | 0.8439† | 0.0546† | 0.9147§ | 0.0300§ | 1.0000 |
| fixed-256 | 8192 | 0.8439† | 0.0546† | 0.9488§ | 0.0159§ | 1.0000 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0580§ | 0.0339§ | 0.0010 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.2403§ | 0.0995§ | 0.0050 |
| section-aware | 512 | 0.6600§ | 0.1621§ | 0.6600§ | 0.1620§ | 0.0250 |
| section-aware | 1024 | 0.8197§ | 0.1072§ | 0.8197§ | 0.1067§ | 0.1390 |
| section-aware | 2048 | 0.9077†§ | 0.0650†§ | 0.9087§ | 0.0609§ | 0.7190 |
| section-aware | 4096 | 0.9299† | 0.0541† | 0.9489§ | 0.0322§ | 1.0000 |
| section-aware | 8192 | 0.9299† | 0.0541† | 0.9729§ | 0.0166§ | 1.0000 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4717§ | 0.2245§ | 0.4717§ | 0.2245§ | 0.0000 |
| contextual-256 | 512 | 0.6459§ | 0.1569§ | 0.6459§ | 0.1569§ | 0.0000 |
| contextual-256 | 1024 | 0.7880§ | 0.0990§ | 0.7880§ | 0.0990§ | 0.0010 |
| contextual-256 | 2048 | 0.8881 | 0.0582 | 0.8881§ | 0.0579§ | 0.0970 |
| contextual-256 | 4096 | 0.8881† | 0.0582† | 0.9472§ | 0.0318§ | 1.0000 |
| contextual-256 | 8192 | 0.8881† | 0.0582† | 0.9649§ | 0.0164§ | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000§ | 0.0000§ | 0.0000§ | 0.0000§ | 0.0000 |
| contextual-256-prefixed | 512 | 0.4727§ | 0.1249§ | 0.4727§ | 0.1249§ | 0.0000 |
| contextual-256-prefixed | 1024 | 0.7231§ | 0.0944§ | 0.7231§ | 0.0944§ | 0.0000 |
| contextual-256-prefixed | 2048 | 0.8534§ | 0.0559§ | 0.8534§ | 0.0558§ | 0.0760 |
| contextual-256-prefixed | 4096 | 0.8881† | 0.0500† | 0.9361§ | 0.0316§ | 1.0000 |
| contextual-256-prefixed | 8192 | 0.8881† | 0.0500† | 0.9612§ | 0.0164§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.8439§ | 0.0546§ | 0.0000 |
| fixed-256 | 4096 | 0.9147§ | 0.0300§ | 0.0000 |
| fixed-256 | 8192 | 0.9247† | 0.0245† | 1.0000 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0000 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.0000 |
| section-aware | 512 | 0.6600§ | 0.1620§ | 0.0000 |
| section-aware | 1024 | 0.8197§ | 0.1067§ | 0.0000 |
| section-aware | 2048 | 0.9087§ | 0.0609§ | 0.0000 |
| section-aware | 4096 | 0.9489§ | 0.0323§ | 0.0730 |
| section-aware | 8192 | 0.9669†§ | 0.0211†§ | 0.9930 |
| contextual-256 | 128 | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4717§ | 0.2245§ | 0.0000 |
| contextual-256 | 512 | 0.6459§ | 0.1569§ | 0.0000 |
| contextual-256 | 1024 | 0.7880§ | 0.0990§ | 0.0000 |
| contextual-256 | 2048 | 0.8881§ | 0.0579§ | 0.0020 |
| contextual-256 | 4096 | 0.9472§ | 0.0318§ | 0.0150 |
| contextual-256 | 8192 | 0.9559† | 0.0259† | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000§ | 0.0000§ | 0.0000 |
| contextual-256-prefixed | 512 | 0.4727§ | 0.1249§ | 0.0000 |
| contextual-256-prefixed | 1024 | 0.7231§ | 0.0944§ | 0.0000 |
| contextual-256-prefixed | 2048 | 0.8534§ | 0.0558§ | 0.0000 |
| contextual-256-prefixed | 4096 | 0.9361§ | 0.0316§ | 0.0000 |
| contextual-256-prefixed | 8192 | 0.9559† | 0.0223† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.0000 |
| fixed-256 | 512 | 0.5975§ | 0.1444§ | 0.0000 |
| fixed-256 | 1024 | 0.7350§ | 0.0924§ | 0.0000 |
| fixed-256 | 2048 | 0.7771† | 0.0786† | 1.0000 |
| fixed-256 | 4096 | 0.7771† | 0.0786† | 1.0000 |
| fixed-256 | 8192 | 0.7771† | 0.0786† | 1.0000 |
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0840 |
| section-aware | 256 | 0.2403§ | 0.1003§ | 0.1960 |
| section-aware | 512 | 0.6600§ | 0.1645§ | 0.2710 |
| section-aware | 1024 | 0.8167†§ | 0.1136†§ | 0.6980 |
| section-aware | 2048 | 0.8887†§ | 0.0861†§ | 0.9920 |
| section-aware | 4096 | 0.8947† | 0.0856† | 1.0000 |
| section-aware | 8192 | 0.8947† | 0.0856† | 1.0000 |
| contextual-256 | 128 | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4717§ | 0.2245§ | 0.0000 |
| contextual-256 | 512 | 0.6459§ | 0.1569§ | 0.0010 |
| contextual-256 | 1024 | 0.7880§ | 0.0991§ | 0.0220 |
| contextual-256 | 2048 | 0.8246† | 0.0845† | 1.0000 |
| contextual-256 | 4096 | 0.8246† | 0.0845† | 1.0000 |
| contextual-256 | 8192 | 0.8246† | 0.0845† | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000§ | 0.0000§ | 0.0020 |
| contextual-256-prefixed | 512 | 0.4727§ | 0.1250§ | 0.0080 |
| contextual-256-prefixed | 1024 | 0.7231§ | 0.0946§ | 0.0570 |
| contextual-256-prefixed | 2048 | 0.8246† | 0.0725† | 1.0000 |
| contextual-256-prefixed | 4096 | 0.8246† | 0.0725† | 1.0000 |
| contextual-256-prefixed | 8192 | 0.8246† | 0.0725† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
