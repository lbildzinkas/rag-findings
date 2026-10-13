# R1 - qasper tracer: fixed-256, bm25, budget 1024, production view

Config hash: `90a2ec4c41511bbf65bc26dace554a345166d9bbfc741ac37099197015c61e8b`

## Config

```yaml
budget: 1024
chunking:
  chunk_tokens: 256
  method: fixed
  overlap: 0
dataset:
  name: qasper
  splits:
  - dev
  - test
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
| dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| | n |
|---|---|
| included | 2197 |
| excluded: unanswerable | 177 |
| excluded: figure_or_table_only | 78 |
| excluded: evidence_unanchored | 4 |
| total | 2456 |

## Retrieval

| metric | value |
|---|---|
| mean retrieval recall | 0.1476 |
| mean retrieval precision | 0.0260 |
