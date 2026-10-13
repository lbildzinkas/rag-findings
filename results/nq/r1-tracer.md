# R1 - nq tracer: fixed-256, bm25, budget 1024, production view

Config hash: `4c25f5e98514852169e2938da9d5fecce3a555189e73b51f57ae4e2233a6acb1`

## Config

```yaml
budget: 1024
chunking:
  chunk_tokens: 256
  method: fixed
  overlap: 0
dataset:
  name: nq
  splits:
  - dev
pipeline: bm25
run_name: tracer
search_depth: 100
seed: 0
top_n: 8
view: production
```

## Dataset

| split | sha256 |
|---|---|
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| | n |
|---|---|
| included | 1000 |
| excluded: unanswerable | 0 |
| excluded: figure_or_table_only | 0 |
| excluded: evidence_unanchored | 0 |
| total | 1000 |

## Query types

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Retrieval

| metric | value |
|---|---|
| mean retrieval recall | 0.5377 |
| mean retrieval precision | 0.0656 |
