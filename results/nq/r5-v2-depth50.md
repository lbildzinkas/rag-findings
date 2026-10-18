# R5 - nq v2-depth50, production line and ablations: pipeline x embedder x chunking

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

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap; budget view: top-N cap 20. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.0570 | 0.0333 | 0.0570 | 0.0333 | 0.0570 | 0.0333 | 0.0000 | 0.7650 | 0.7650 | 0.7650 |
| hybrid-rerank | nomic | section-aware-titles | 0.0691 | 0.0400 | 0.0691 | 0.0396 | 0.0691 | 0.0396 | 0.0000 | 0.6530 | 0.7260 | 0.7260 |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.2443 | 0.0998 | 0.2443 | 0.0997 | 0.2443 | 0.0997 | 0.0000 | 0.7900 | 0.7900 | 0.7900 |
| hybrid-rerank | nomic | section-aware-titles | 0.2621 | 0.1083 | 0.2621 | 0.1062 | 0.2621 | 0.1062 | 0.0000 | 0.5770 | 0.7100 | 0.7100 |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.6570 | 0.1610 | 0.6570 | 0.1609 | 0.6570 | 0.1609 | 0.0000 | 0.7740 | 0.7770 | 0.7770 |
| hybrid-rerank | nomic | section-aware-titles | 0.6638 | 0.1702 | 0.6638 | 0.1670 | 0.6638 | 0.1670 | 0.0000 | 0.5230 | 0.7070 | 0.7080 |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.8210 | 0.1077 | 0.8210 | 0.1073 | 0.8210 | 0.1073 | 0.0000 | 0.7530 | 0.8020 | 0.8020 |
| hybrid-rerank | nomic | section-aware-titles | 0.8538† | 0.1170† | 0.8538 | 0.1131 | 0.8538 | 0.1131 | 0.0000 | 0.3830 | 0.7440 | 0.7460 |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9039† | 0.0648† | 0.9049 | 0.0606 | 0.9049 | 0.0606 | 0.0000 | 0.3250 | 0.8240 | 0.8240 |
| hybrid-rerank | nomic | section-aware-titles | 0.9321† | 0.0721† | 0.9321 | 0.0630 | 0.9321 | 0.0630 | 0.0000 | 0.1890 | 0.7680 | 0.7810 |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9269† | 0.0540† | 0.9549 | 0.0326 | 0.9549 | 0.0325 | 0.0000 | 0.0000 | 0.8200 | 0.8610 |
| hybrid-rerank | nomic | section-aware-titles | 0.9600† | 0.0600† | 0.9751 | 0.0345 | 0.9751 | 0.0334 | 0.0000 | 0.0000 | 0.5460 | 0.8330 |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | budget recall | budget precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, budget view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | nomic | section-aware | 0.9269† | 0.0540† | 0.9689† | 0.0216† | 0.9779 | 0.0169 | 0.0000 | 0.0000 | 0.0140 | 0.8650 |
| hybrid-rerank | nomic | section-aware-titles | 0.9600† | 0.0600† | 0.9921† | 0.0254† | 0.9941 | 0.0172 | 0.0000 | 0.0000 | 0.0110 | 0.9260 |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 50 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
