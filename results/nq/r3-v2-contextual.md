# R3 - nq v2-contextual, production line and ablations: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4441 | 0.4114 | -0.0328 | 0.4441 | 0.4114 | -0.0328 |
| fixed-256 | 512 | 0.6062 | 0.5887 | -0.0175 | 0.6062 | 0.5887 | -0.0175 |
| fixed-256 | 1024 | 0.7556 | 0.7145 | -0.0411 | 0.7556 | 0.7145 | -0.0411 |
| fixed-256 | 2048 | 0.8535 | 0.8342 | -0.0194 | 0.8535 | 0.8342 | -0.0194 |
| fixed-256 | 4096 | 0.8535 | 0.8342 | -0.0194 | 0.9202 | 0.9092 | -0.0110 |
| fixed-256 | 8192 | 0.8535 | 0.8342 | -0.0194 | 0.9577 | 0.9400 | -0.0177 |
| section-aware | 128 | 0.0620 | 0.0540 | -0.0080 | 0.0620 | 0.0540 | -0.0080 |
| section-aware | 256 | 0.2580 | 0.2226 | -0.0354 | 0.2580 | 0.2226 | -0.0354 |
| section-aware | 512 | 0.6940 | 0.6260 | -0.0680 | 0.6940 | 0.6260 | -0.0680 |
| section-aware | 1024 | 0.8415 | 0.7979 | -0.0436 | 0.8415 | 0.7979 | -0.0436 |
| section-aware | 2048 | 0.9275 | 0.8879 | -0.0396 | 0.9275 | 0.8899 | -0.0376 |
| section-aware | 4096 | 0.9460 | 0.9139 | -0.0321 | 0.9560 | 0.9419 | -0.0141 |
| section-aware | 8192 | 0.9460 | 0.9139 | -0.0321 | 0.9800 | 0.9659 | -0.0141 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4734 | 0.4700 | -0.0034 | 0.4734 | 0.4700 | -0.0034 |
| contextual-256 | 512 | 0.6640 | 0.6277 | -0.0363 | 0.6640 | 0.6277 | -0.0363 |
| contextual-256 | 1024 | 0.8067 | 0.7693 | -0.0375 | 0.8067 | 0.7693 | -0.0375 |
| contextual-256 | 2048 | 0.9055 | 0.8706 | -0.0349 | 0.9055 | 0.8706 | -0.0349 |
| contextual-256 | 4096 | 0.9055 | 0.8706 | -0.0349 | 0.9578 | 0.9366 | -0.0212 |
| contextual-256 | 8192 | 0.9055 | 0.8706 | -0.0349 | 0.9712 | 0.9586 | -0.0126 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000 | 0.0000 | +0.0000 | 0.0000 | 0.0000 | +0.0000 |
| contextual-256-prefixed | 512 | 0.4734 | 0.4720 | -0.0014 | 0.4734 | 0.4720 | -0.0014 |
| contextual-256-prefixed | 1024 | 0.7417 | 0.7044 | -0.0373 | 0.7417 | 0.7044 | -0.0373 |
| contextual-256-prefixed | 2048 | 0.8678 | 0.8391 | -0.0288 | 0.8678 | 0.8391 | -0.0288 |
| contextual-256-prefixed | 4096 | 0.9055 | 0.8706 | -0.0349 | 0.9437 | 0.9285 | -0.0152 |
| contextual-256-prefixed | 8192 | 0.9055 | 0.8706 | -0.0349 | 0.9683 | 0.9541 | -0.0142 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
