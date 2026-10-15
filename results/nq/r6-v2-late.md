# R6 - nq v2-late, production line and ablations: short-answer span recall

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

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
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
| section-aware | 128 | 0.0600§ | 0.0600§ | 0.0021 |
| section-aware | 256 | 0.2402§ | 0.2402§ | 0.0041 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.0269 |
| section-aware | 1024 | 0.8613§ | 0.8613§ | 0.1366 |
| section-aware | 2048 | 0.9275†§ | 0.9275§ | 0.6936 |
| section-aware | 4096 | 0.9400† | 0.9482§ | 1.0000 |
| section-aware | 8192 | 0.9400† | 0.9731§ | 1.0000 |
| late-128 | 128 | 0.4230 | 0.4230 | 0.0000 |
| late-128 | 256 | 0.5867§ | 0.5867§ | 0.0000 |
| late-128 | 512 | 0.7178§ | 0.7178§ | 0.0000 |
| late-128 | 1024 | 0.7977 | 0.7977§ | 0.0104 |
| late-128 | 2048 | 0.7977† | 0.8747§ | 1.0000 |
| late-128 | 4096 | 0.7977† | 0.9156§ | 1.0000 |
| late-128 | 8192 | 0.7977† | 0.9768§ | 1.0000 |
| late-256 | 128 | n/a | n/a | n/a |
| late-256 | 256 | 0.5294§ | 0.5294§ | 0.0000 |
| late-256 | 512 | 0.6929§ | 0.6929§ | 0.0000 |
| late-256 | 1024 | 0.8197§ | 0.8197§ | 0.0000 |
| late-256 | 2048 | 0.9084 | 0.9084§ | 0.0704 |
| late-256 | 4096 | 0.9084† | 0.9602§ | 1.0000 |
| late-256 | 8192 | 0.9084† | 0.9851§ | 1.0000 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
