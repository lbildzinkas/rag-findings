# R2 - nq v2-late, production line and ablations: chunking x budget, collection search

Config hash: `9ef43d53b9923e4098976e4539a9426dd274124f3e2e85c2e00d7827fc568dbd`

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
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0580§ | 0.0339§ | 0.0010 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.2403§ | 0.0995§ | 0.0050 |
| section-aware | 512 | 0.6600§ | 0.1621§ | 0.6600§ | 0.1620§ | 0.0250 |
| section-aware | 1024 | 0.8197§ | 0.1072§ | 0.8197§ | 0.1067§ | 0.1390 |
| section-aware | 2048 | 0.9077†§ | 0.0650†§ | 0.9087§ | 0.0609§ | 0.7190 |
| section-aware | 4096 | 0.9299† | 0.0541† | 0.9489§ | 0.0322§ | 1.0000 |
| section-aware | 8192 | 0.9299† | 0.0541† | 0.9729§ | 0.0166§ | 1.0000 |
| late-128 | 128 | 0.3023 | 0.2700 | 0.3023 | 0.2700 | 0.0000 |
| late-128 | 256 | 0.4422§ | 0.2015§ | 0.4422§ | 0.2015§ | 0.0000 |
| late-128 | 512 | 0.5897§ | 0.1379§ | 0.5897§ | 0.1379§ | 0.0000 |
| late-128 | 1024 | 0.7177 | 0.0881 | 0.7177§ | 0.0881§ | 0.0090 |
| late-128 | 2048 | 0.7177† | 0.0881† | 0.8290§ | 0.0525§ | 1.0000 |
| late-128 | 4096 | 0.7177† | 0.0881† | 0.9028§ | 0.0295§ | 1.0000 |
| late-128 | 8192 | 0.7177† | 0.0881† | 0.9620§ | 0.0162§ | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.4298§ | 0.2002§ | 0.4298§ | 0.2002§ | 0.0000 |
| late-256 | 512 | 0.6066§ | 0.1466§ | 0.6066§ | 0.1466§ | 0.0000 |
| late-256 | 1024 | 0.7432§ | 0.0932§ | 0.7432§ | 0.0932§ | 0.0000 |
| late-256 | 2048 | 0.8591 | 0.0560 | 0.8591§ | 0.0559§ | 0.0700 |
| late-256 | 4096 | 0.8591† | 0.0560† | 0.9320§ | 0.0309§ | 1.0000 |
| late-256 | 8192 | 0.8591† | 0.0560† | 0.9680§ | 0.0164§ | 1.0000 |

## Budget view (top-N cap 20)

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
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
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0000 |
| section-aware | 256 | 0.2403§ | 0.0995§ | 0.0000 |
| section-aware | 512 | 0.6600§ | 0.1620§ | 0.0000 |
| section-aware | 1024 | 0.8197§ | 0.1067§ | 0.0000 |
| section-aware | 2048 | 0.9087§ | 0.0609§ | 0.0000 |
| section-aware | 4096 | 0.9489§ | 0.0323§ | 0.0730 |
| section-aware | 8192 | 0.9669†§ | 0.0211†§ | 0.9930 |
| late-128 | 128 | 0.3023 | 0.2700 | 0.0000 |
| late-128 | 256 | 0.4422§ | 0.2015§ | 0.0000 |
| late-128 | 512 | 0.5897§ | 0.1379§ | 0.0000 |
| late-128 | 1024 | 0.7177§ | 0.0881§ | 0.0000 |
| late-128 | 2048 | 0.8290§ | 0.0525§ | 0.0010 |
| late-128 | 4096 | 0.8570† | 0.0439† | 1.0000 |
| late-128 | 8192 | 0.8570† | 0.0439† | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a |
| late-256 | 256 | 0.4298§ | 0.2002§ | 0.0000 |
| late-256 | 512 | 0.6066§ | 0.1466§ | 0.0000 |
| late-256 | 1024 | 0.7432§ | 0.0932§ | 0.0000 |
| late-256 | 2048 | 0.8591§ | 0.0559§ | 0.0000 |
| late-256 | 4096 | 0.9320§ | 0.0309§ | 0.0040 |
| late-256 | 8192 | 0.9408† | 0.0252† | 1.0000 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
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
| section-aware | 128 | 0.0580§ | 0.0339§ | 0.0840 |
| section-aware | 256 | 0.2403§ | 0.1003§ | 0.1960 |
| section-aware | 512 | 0.6600§ | 0.1645§ | 0.2710 |
| section-aware | 1024 | 0.8167†§ | 0.1136†§ | 0.6980 |
| section-aware | 2048 | 0.8887†§ | 0.0861†§ | 0.9920 |
| section-aware | 4096 | 0.8947† | 0.0856† | 1.0000 |
| section-aware | 8192 | 0.8947† | 0.0856† | 1.0000 |
| late-128 | 128 | 0.3023 | 0.2700 | 0.0000 |
| late-128 | 256 | 0.4422§ | 0.2015§ | 0.0000 |
| late-128 | 512 | 0.5897§ | 0.1379§ | 0.0040 |
| late-128 | 1024 | 0.6324† | 0.1205† | 1.0000 |
| late-128 | 2048 | 0.6324† | 0.1205† | 1.0000 |
| late-128 | 4096 | 0.6324† | 0.1205† | 1.0000 |
| late-128 | 8192 | 0.6324† | 0.1205† | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a |
| late-256 | 256 | 0.4298§ | 0.2002§ | 0.0000 |
| late-256 | 512 | 0.6066§ | 0.1466§ | 0.0020 |
| late-256 | 1024 | 0.7432§ | 0.0933§ | 0.0190 |
| late-256 | 2048 | 0.7846† | 0.0801† | 1.0000 |
| late-256 | 4096 | 0.7846† | 0.0801† | 1.0000 |
| late-256 | 8192 | 0.7846† | 0.0801† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
