# R6 - nq v2-contextual, production line and ablations: short-answer span recall

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

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
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
| contextual-256 | 128 | n/a | n/a | n/a |
| contextual-256 | 256 | 0.5442§ | 0.5442§ | 0.0000 |
| contextual-256 | 512 | 0.7407§ | 0.7407§ | 0.0000 |
| contextual-256 | 1024 | 0.8532§ | 0.8532§ | 0.0021 |
| contextual-256 | 2048 | 0.9402 | 0.9402§ | 0.0952 |
| contextual-256 | 4096 | 0.9402† | 0.9760§ | 1.0000 |
| contextual-256 | 8192 | 0.9402† | 0.9823§ | 1.0000 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000§ | 0.0000§ | 0.0000 |
| contextual-256-prefixed | 512 | 0.5442§ | 0.5442§ | 0.0000 |
| contextual-256-prefixed | 1024 | 0.8032§ | 0.8032§ | 0.0000 |
| contextual-256-prefixed | 2048 | 0.9070§ | 0.9070§ | 0.0725 |
| contextual-256-prefixed | 4096 | 0.9402† | 0.9615§ | 1.0000 |
| contextual-256-prefixed | 8192 | 0.9402† | 0.9802§ | 1.0000 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
