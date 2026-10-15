# R3 - nq v2-baseline, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.3024 | 0.2503 | -0.0521 | 0.3024 | 0.2503 | -0.0521 |
| fixed-64 | 256 | 0.3993 | 0.3506 | -0.0487 | 0.3993 | 0.3506 | -0.0487 |
| fixed-64 | 512 | 0.4977 | 0.4601 | -0.0377 | 0.4977 | 0.4601 | -0.0377 |
| fixed-64 | 1024 | 0.4977 | 0.4601 | -0.0377 | 0.5844 | 0.5714 | -0.0131 |
| fixed-64 | 2048 | 0.4977 | 0.4601 | -0.0377 | 0.6516 | 0.6492 | -0.0023 |
| fixed-64 | 4096 | 0.4977 | 0.4601 | -0.0377 | 0.7462 | 0.7470 | +0.0008 |
| fixed-64 | 8192 | 0.4977 | 0.4601 | -0.0377 | 0.8207 | 0.8172 | -0.0034 |
| fixed-128 | 128 | 0.3109 | 0.2826 | -0.0282 | 0.3109 | 0.2826 | -0.0282 |
| fixed-128 | 256 | 0.4560 | 0.4111 | -0.0449 | 0.4560 | 0.4111 | -0.0449 |
| fixed-128 | 512 | 0.5894 | 0.5440 | -0.0454 | 0.5894 | 0.5440 | -0.0454 |
| fixed-128 | 1024 | 0.6923 | 0.6852 | -0.0071 | 0.6923 | 0.6852 | -0.0071 |
| fixed-128 | 2048 | 0.6923 | 0.6852 | -0.0071 | 0.7893 | 0.7773 | -0.0120 |
| fixed-128 | 4096 | 0.6923 | 0.6852 | -0.0071 | 0.8420 | 0.8294 | -0.0126 |
| fixed-128 | 8192 | 0.6923 | 0.6852 | -0.0071 | 0.9064 | 0.8863 | -0.0201 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4441 | 0.4114 | -0.0328 | 0.4441 | 0.4114 | -0.0328 |
| fixed-256 | 512 | 0.6062 | 0.5887 | -0.0175 | 0.6062 | 0.5887 | -0.0175 |
| fixed-256 | 1024 | 0.7556 | 0.7145 | -0.0411 | 0.7556 | 0.7145 | -0.0411 |
| fixed-256 | 2048 | 0.8535 | 0.8342 | -0.0194 | 0.8535 | 0.8342 | -0.0194 |
| fixed-256 | 4096 | 0.8535 | 0.8342 | -0.0194 | 0.9202 | 0.9092 | -0.0110 |
| fixed-256 | 8192 | 0.8535 | 0.8342 | -0.0194 | 0.9577 | 0.9400 | -0.0177 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6409 | 0.5798 | -0.0612 | 0.6409 | 0.5798 | -0.0612 |
| fixed-512 | 1024 | 0.8021 | 0.7344 | -0.0677 | 0.8021 | 0.7344 | -0.0677 |
| fixed-512 | 2048 | 0.8953 | 0.8487 | -0.0466 | 0.8953 | 0.8487 | -0.0466 |
| fixed-512 | 4096 | 0.9468 | 0.9168 | -0.0300 | 0.9468 | 0.9168 | -0.0300 |
| fixed-512 | 8192 | 0.9468 | 0.9168 | -0.0300 | 0.9802 | 0.9643 | -0.0159 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7680 | 0.7132 | -0.0547 | 0.7680 | 0.7132 | -0.0547 |
| fixed-1024 | 2048 | 0.8811 | 0.8343 | -0.0467 | 0.8811 | 0.8343 | -0.0467 |
| fixed-1024 | 4096 | 0.9359 | 0.9151 | -0.0208 | 0.9359 | 0.9151 | -0.0208 |
| fixed-1024 | 8192 | 0.9760 | 0.9650 | -0.0111 | 0.9760 | 0.9650 | -0.0111 |
| section-aware | 128 | 0.0620 | 0.0540 | -0.0080 | 0.0620 | 0.0540 | -0.0080 |
| section-aware | 256 | 0.2580 | 0.2226 | -0.0354 | 0.2580 | 0.2226 | -0.0354 |
| section-aware | 512 | 0.6940 | 0.6260 | -0.0680 | 0.6940 | 0.6260 | -0.0680 |
| section-aware | 1024 | 0.8415 | 0.7979 | -0.0436 | 0.8415 | 0.7979 | -0.0436 |
| section-aware | 2048 | 0.9275 | 0.8879 | -0.0396 | 0.9275 | 0.8899 | -0.0376 |
| section-aware | 4096 | 0.9460 | 0.9139 | -0.0321 | 0.9560 | 0.9419 | -0.0141 |
| section-aware | 8192 | 0.9460 | 0.9139 | -0.0321 | 0.9800 | 0.9659 | -0.0141 |
| small-to-big | 128 | 0.3516 | 0.3124 | -0.0392 | 0.3516 | 0.3124 | -0.0392 |
| small-to-big | 256 | 0.5199 | 0.4795 | -0.0404 | 0.5199 | 0.4795 | -0.0404 |
| small-to-big | 512 | 0.6929 | 0.6153 | -0.0776 | 0.6929 | 0.6153 | -0.0776 |
| small-to-big | 1024 | 0.8134 | 0.7607 | -0.0527 | 0.8134 | 0.7607 | -0.0527 |
| small-to-big | 2048 | 0.8946 | 0.8602 | -0.0345 | 0.8946 | 0.8602 | -0.0345 |
| small-to-big | 4096 | 0.9280 | 0.8899 | -0.0381 | 0.9437 | 0.9170 | -0.0266 |
| small-to-big | 8192 | 0.9280 | 0.8899 | -0.0381 | 0.9620 | 0.9499 | -0.0121 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
