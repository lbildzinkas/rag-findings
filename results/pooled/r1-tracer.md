# R1 - pooled tracer: fixed-256, bm25, budget 1024, production view

Config hash: `3acca43f6ccc26ed855366f6d9d71de56c5bf8e245174be1b9690c6b84c94681`

## Config

```yaml
budget: 1024
chunking:
  chunk_tokens: 256
  method: fixed
  overlap: 0
dataset:
  name: pooled
  sources:
  - name: qasper
    splits:
    - dev
    - test
  - name: nq
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
| qasper/dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| qasper/test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |
| nq/dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| | n |
|---|---|
| included | 3197 |
| excluded: unanswerable | 177 |
| excluded: figure_or_table_only | 78 |
| excluded: evidence_unanchored | 4 |
| total | 3456 |

## Query types

| dataset | query type | n |
|---|---|---|
| nq | precise | 500 |
| nq | context | 500 |
| nq | mixed | 0 |
| nq | total | 1000 |
| qasper | precise | 1317 |
| qasper | context | 404 |
| qasper | mixed | 476 |
| qasper | total | 2197 |

## Retrieval

| metric | value |
|---|---|
| mean retrieval recall | 0.2699 |
| mean retrieval precision | 0.0383 |
