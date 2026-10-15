# R4 - nq v2-late, production line and ablations: fixed-k

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

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-128 | 0.4440 | 0.8020 | 0.8770 | 0.2558 | 0.5654 | 0.6748 |
| fixed-256 | 0.5300 | 0.8580 | 0.9330 | 0.4027 | 0.7515 | 0.8538 |
| section-aware | 0.6000 | 0.8950 | 0.9400 | 0.5995 | 0.8935 | 0.9390 |
| late-128 | 0.4520 | 0.8210 | 0.8990 | 0.2606 | 0.5850 | 0.7167 |
| late-256 | 0.5300 | 0.8700 | 0.9360 | 0.4027 | 0.7618 | 0.8657 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
