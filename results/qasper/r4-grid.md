# R4 - qasper grid, bm25: fixed-k

Config hash: `b1a07e4a65f57e48f777369cd0a5dbbd26a4152deeeb6a73e148dd813e97aa9f`

## Config

```yaml
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
  name: qasper
  splits:
  - dev
  - test
fixed_k:
- 1
- 5
- 10
kind: grid
pipeline: bm25
run_name: grid
scopes:
- collection
- document
search_depth: 1000
seed: 0
side_top_n: 5
top_n: 8
```

## Dataset

| split | sha256 |
|---|---|
| dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| query type | n |
|---|---|
| precise | 1317 |
| context | 404 |
| mixed | 476 |
| total | 2197 |

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0596 | 0.1780 | 0.2353 | 0.0170 | 0.0608 | 0.0894 |
| fixed-128 | 0.0746 | 0.2066 | 0.2745 | 0.0332 | 0.1071 | 0.1573 |
| fixed-256 | 0.0869 | 0.2271 | 0.2845 | 0.0526 | 0.1624 | 0.2168 |
| fixed-512 | 0.1161 | 0.2645 | 0.3286 | 0.0826 | 0.2198 | 0.2841 |
| fixed-1024 | 0.1507 | 0.3027 | 0.3600 | 0.1277 | 0.2784 | 0.3358 |
| section-aware | 0.0683 | 0.2053 | 0.2722 | 0.0602 | 0.1900 | 0.2558 |
| small-to-big | 0.0715 | 0.2117 | 0.2763 | 0.0619 | 0.1953 | 0.2581 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
