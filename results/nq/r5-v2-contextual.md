# R5 - nq v2-contextual, production line and ablations: pipeline x embedder x chunking

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

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap; budget view: top-N cap 20. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0000 | 0.8370 | 0.8370 | 0.8370 |
| hybrid-rerank | nomic | contextual-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | contextual-256-prefixed | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | section-aware | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.0000 | 0.8450 | 0.8450 | 0.8450 |
| hybrid-rerank | nomic | contextual-256 | 0.4717 | 0.2245 | 0.4717 | 0.2245 | 0.4717 | 0.2245 | 0.0000 | 0.0020 | 0.0020 | 0.0020 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.8560 | 0.8560 | 0.8560 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.5975 | 0.1444 | 0.5975 | 0.1444 | 0.5975 | 0.1444 | 0.0000 | 0.0020 | 0.0020 | 0.0020 |
| hybrid-rerank | nomic | section-aware | 0.6600 | 0.1621 | 0.6600 | 0.1620 | 0.6600 | 0.1620 | 0.0000 | 0.8150 | 0.8160 | 0.8160 |
| hybrid-rerank | nomic | contextual-256 | 0.6459 | 0.1569 | 0.6459 | 0.1569 | 0.6459 | 0.1569 | 0.0000 | 0.0130 | 0.0130 | 0.0130 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.4727 | 0.1249 | 0.4727 | 0.1249 | 0.4727 | 0.1249 | 0.0000 | 0.8460 | 0.8460 | 0.8460 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.7350 | 0.0924 | 0.7350 | 0.0924 | 0.7350 | 0.0924 | 0.0000 | 0.0040 | 0.0040 | 0.0040 |
| hybrid-rerank | nomic | section-aware | 0.8197 | 0.1072 | 0.8197 | 0.1067 | 0.8197 | 0.1067 | 0.0000 | 0.8150 | 0.8540 | 0.8540 |
| hybrid-rerank | nomic | contextual-256 | 0.7880 | 0.0990 | 0.7880 | 0.0990 | 0.7880 | 0.0990 | 0.0000 | 0.0440 | 0.0440 | 0.0440 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.7231 | 0.0944 | 0.7231 | 0.0944 | 0.7231 | 0.0944 | 0.0000 | 0.7110 | 0.7110 | 0.7110 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.8439 | 0.0546 | 0.8439 | 0.0546 | 0.8439 | 0.0546 | 0.0000 | 0.0000 | 0.0080 | 0.0080 |
| hybrid-rerank | nomic | section-aware | 0.9077† | 0.0650† | 0.9087 | 0.0609 | 0.9087 | 0.0609 | 0.0000 | 0.4330 | 0.8770 | 0.8770 |
| hybrid-rerank | nomic | contextual-256 | 0.8881 | 0.0582 | 0.8881 | 0.0579 | 0.8881 | 0.0579 | 0.0000 | 0.0000 | 0.0960 | 0.0960 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.8534 | 0.0559 | 0.8534 | 0.0558 | 0.8534 | 0.0558 | 0.0000 | 0.6320 | 0.6320 | 0.6320 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9147 | 0.0300 | 0.9147 | 0.0300 | 0.0000 | 0.0000 | 0.0160 | 0.0160 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9489 | 0.0323 | 0.9489 | 0.0322 | 0.0000 | 0.0000 | 0.8600 | 0.8970 |
| hybrid-rerank | nomic | contextual-256 | 0.8881† | 0.0582† | 0.9472 | 0.0318 | 0.9472 | 0.0318 | 0.0000 | 0.0000 | 0.1890 | 0.1890 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.8881† | 0.0500† | 0.9361 | 0.0316 | 0.9361 | 0.0316 | 0.0000 | 0.0000 | 0.6820 | 0.6820 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9247† | 0.0245† | 0.9488 | 0.0159 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9669† | 0.0211† | 0.9729 | 0.0166 | 0.0000 | 0.0000 | 0.0330 | 0.9590 |
| hybrid-rerank | nomic | contextual-256 | 0.8881† | 0.0582† | 0.9559† | 0.0259† | 0.9649 | 0.0164 | 0.0000 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | contextual-256-prefixed | 0.8881† | 0.0500† | 0.9559† | 0.0223† | 0.9612 | 0.0164 | 0.0000 | 0.0000 | 0.0000 | 0.6890 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
