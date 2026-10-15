# R6 - nq v2-baseline, production line and ablations: short-answer span recall

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

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.4212 | 0.4212 | 0.0000 |
| fixed-64 | 256 | 0.5349 | 0.5349 | 0.0000 |
| fixed-64 | 512 | 0.6159 | 0.6159 | 0.0000 |
| fixed-64 | 1024 | 0.6159† | 0.6825 | 1.0000 |
| fixed-64 | 2048 | 0.6159† | 0.7279§ | 1.0000 |
| fixed-64 | 4096 | 0.6159† | 0.8079§ | 1.0000 |
| fixed-64 | 8192 | 0.6159† | 0.8699§ | 1.0000 |
| fixed-128 | 128 | 0.4098 | 0.4098 | 0.0000 |
| fixed-128 | 256 | 0.5697 | 0.5697 | 0.0000 |
| fixed-128 | 512 | 0.7012 | 0.7012 | 0.0000 |
| fixed-128 | 1024 | 0.7790 | 0.7790§ | 0.0021 |
| fixed-128 | 2048 | 0.7790† | 0.8369§ | 1.0000 |
| fixed-128 | 4096 | 0.7790† | 0.8760§ | 1.0000 |
| fixed-128 | 8192 | 0.7790† | 0.9194§ | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.5267 | 0.5267 | 0.0000 |
| fixed-256 | 512 | 0.6867§ | 0.6867§ | 0.0000 |
| fixed-256 | 1024 | 0.7990§ | 0.7990§ | 0.0000 |
| fixed-256 | 2048 | 0.8860 | 0.8860§ | 0.0104 |
| fixed-256 | 4096 | 0.8860† | 0.9429§ | 1.0000 |
| fixed-256 | 8192 | 0.8860† | 0.9719§ | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6710§ | 0.6710§ | 0.0000 |
| fixed-512 | 1024 | 0.8165§ | 0.8165§ | 0.0000 |
| fixed-512 | 2048 | 0.9041§ | 0.9041§ | 0.0000 |
| fixed-512 | 4096 | 0.9503 | 0.9503§ | 0.1470 |
| fixed-512 | 8192 | 0.9503† | 0.9731§ | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7802§ | 0.7802§ | 0.0021 |
| fixed-1024 | 2048 | 0.8814§ | 0.8814§ | 0.0021 |
| fixed-1024 | 4096 | 0.9352§ | 0.9352§ | 0.0041 |
| fixed-1024 | 8192 | 0.9731 | 0.9731§ | 0.4079 |
| section-aware | 128 | 0.0600§ | 0.0600§ | 0.0021 |
| section-aware | 256 | 0.2402§ | 0.2402§ | 0.0041 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.0269 |
| section-aware | 1024 | 0.8613§ | 0.8613§ | 0.1366 |
| section-aware | 2048 | 0.9275†§ | 0.9275§ | 0.6936 |
| section-aware | 4096 | 0.9400† | 0.9482§ | 1.0000 |
| section-aware | 8192 | 0.9400† | 0.9731§ | 1.0000 |
| small-to-big | 128 | 0.4633§ | 0.4633§ | 0.0021 |
| small-to-big | 256 | 0.6044§ | 0.6044§ | 0.0021 |
| small-to-big | 512 | 0.6952§ | 0.6952§ | 0.0207 |
| small-to-big | 1024 | 0.8199§ | 0.8199§ | 0.1429 |
| small-to-big | 2048 | 0.8965†§ | 0.8965§ | 0.6708 |
| small-to-big | 4096 | 0.9255† | 0.9400§ | 1.0000 |
| small-to-big | 8192 | 0.9255† | 0.9565§ | 1.0000 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
Re-run regression: fixed-1024@1024 deviates from v1's grid run by one question; see `v2-baseline-regression.md`.
