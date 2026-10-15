# R5 - nq v2-late, production line and ablations: pipeline x embedder x chunking

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

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap; budget view: top-N cap 20. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.2968 | 0.2642 | 0.2968 | 0.2642 | 0.2968 | 0.2642 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0000 | 0.8370 | 0.8370 | 0.8370 |
| hybrid-rerank | nomic | late-128 | 0.3023 | 0.2700 | 0.3023 | 0.2700 | 0.3023 | 0.2700 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | late-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.4335 | 0.1970 | 0.4335 | 0.1970 | 0.4335 | 0.1970 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | section-aware | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.0000 | 0.8450 | 0.8450 | 0.8450 |
| hybrid-rerank | nomic | late-128 | 0.4422 | 0.2015 | 0.4422 | 0.2015 | 0.4422 | 0.2015 | 0.0000 | 0.0030 | 0.0030 | 0.0030 |
| hybrid-rerank | nomic | late-256 | 0.4298 | 0.2002 | 0.4298 | 0.2002 | 0.4298 | 0.2002 | 0.0000 | 0.0010 | 0.0010 | 0.0010 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.5667 | 0.1321 | 0.5667 | 0.1321 | 0.5667 | 0.1321 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.5975 | 0.1444 | 0.5975 | 0.1444 | 0.5975 | 0.1444 | 0.0000 | 0.0020 | 0.0020 | 0.0020 |
| hybrid-rerank | nomic | section-aware | 0.6600 | 0.1621 | 0.6600 | 0.1620 | 0.6600 | 0.1620 | 0.0000 | 0.8150 | 0.8160 | 0.8160 |
| hybrid-rerank | nomic | late-128 | 0.5897 | 0.1379 | 0.5897 | 0.1379 | 0.5897 | 0.1379 | 0.0000 | 0.0040 | 0.0040 | 0.0040 |
| hybrid-rerank | nomic | late-256 | 0.6066 | 0.1466 | 0.6066 | 0.1466 | 0.6066 | 0.1466 | 0.0000 | 0.0090 | 0.0090 | 0.0090 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.6887 | 0.0836 | 0.6887 | 0.0836 | 0.6887 | 0.0836 | 0.0000 | 0.0000 | 0.0010 | 0.0010 |
| hybrid-rerank | nomic | fixed-256 | 0.7350 | 0.0924 | 0.7350 | 0.0924 | 0.7350 | 0.0924 | 0.0000 | 0.0040 | 0.0040 | 0.0040 |
| hybrid-rerank | nomic | section-aware | 0.8197 | 0.1072 | 0.8197 | 0.1067 | 0.8197 | 0.1067 | 0.0000 | 0.8150 | 0.8540 | 0.8540 |
| hybrid-rerank | nomic | late-128 | 0.7177 | 0.0881 | 0.7177 | 0.0881 | 0.7177 | 0.0881 | 0.0000 | 0.0000 | 0.0090 | 0.0090 |
| hybrid-rerank | nomic | late-256 | 0.7432 | 0.0932 | 0.7432 | 0.0932 | 0.7432 | 0.0932 | 0.0000 | 0.0310 | 0.0310 | 0.0310 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.7833 | 0.0491 | 0.7833 | 0.0491 | 0.0000 | 0.0000 | 0.0020 | 0.0020 |
| hybrid-rerank | nomic | fixed-256 | 0.8439 | 0.0546 | 0.8439 | 0.0546 | 0.8439 | 0.0546 | 0.0000 | 0.0000 | 0.0080 | 0.0080 |
| hybrid-rerank | nomic | section-aware | 0.9077† | 0.0650† | 0.9087 | 0.0609 | 0.9087 | 0.0609 | 0.0000 | 0.4330 | 0.8770 | 0.8770 |
| hybrid-rerank | nomic | late-128 | 0.7177† | 0.0881† | 0.8290 | 0.0525 | 0.8290 | 0.0525 | 0.0000 | 0.0000 | 0.0350 | 0.0350 |
| hybrid-rerank | nomic | late-256 | 0.8591 | 0.0560 | 0.8591 | 0.0559 | 0.8591 | 0.0559 | 0.0000 | 0.0000 | 0.0690 | 0.0690 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.8038† | 0.0408† | 0.8357 | 0.0267 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9147 | 0.0300 | 0.9147 | 0.0300 | 0.0000 | 0.0000 | 0.0160 | 0.0160 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9489 | 0.0323 | 0.9489 | 0.0322 | 0.0000 | 0.0000 | 0.8600 | 0.8970 |
| hybrid-rerank | nomic | late-128 | 0.7177† | 0.0881† | 0.8570† | 0.0439† | 0.9028 | 0.0295 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | late-256 | 0.8591† | 0.0560† | 0.9320 | 0.0309 | 0.9320 | 0.0309 | 0.0000 | 0.0000 | 0.1120 | 0.1130 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.8038† | 0.0408† | 0.8963 | 0.0145 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9247† | 0.0245† | 0.9488 | 0.0159 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9669† | 0.0211† | 0.9729 | 0.0166 | 0.0000 | 0.0000 | 0.0330 | 0.9590 |
| hybrid-rerank | nomic | late-128 | 0.7177† | 0.0881† | 0.8570† | 0.0439† | 0.9620 | 0.0162 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | late-256 | 0.8591† | 0.0560† | 0.9408† | 0.0252† | 0.9680 | 0.0164 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
