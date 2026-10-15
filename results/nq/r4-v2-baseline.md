# R4 - nq v2-baseline, production line and ablations: fixed-k

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

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.4000 | 0.7180 | 0.8210 | 0.1544 | 0.3648 | 0.4756 |
| fixed-128 | 0.4440 | 0.8020 | 0.8770 | 0.2558 | 0.5654 | 0.6748 |
| fixed-256 | 0.5300 | 0.8580 | 0.9330 | 0.4027 | 0.7515 | 0.8538 |
| fixed-512 | 0.6580 | 0.9200 | 0.9710 | 0.6003 | 0.8897 | 0.9505 |
| fixed-1024 | 0.7530 | 0.9530 | 0.9790 | 0.7380 | 0.9455 | 0.9750 |
| section-aware | 0.6000 | 0.8950 | 0.9400 | 0.5995 | 0.8935 | 0.9390 |
| small-to-big | 0.5630 | 0.8560 | 0.9210 | 0.5625 | 0.8550 | 0.9200 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
