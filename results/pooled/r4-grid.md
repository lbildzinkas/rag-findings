# R4 - pooled grid, bm25: fixed-k

Config hash: `f694a2158845007eb97e12458bd026cf20f009ae800d81a5bac1c7896c2d70b2`

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
  name: pooled
  sources:
  - name: qasper
    splits:
    - dev
    - test
  - name: nq
    splits:
    - dev
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
| nq/dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |
| qasper/dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| qasper/test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| dataset | query type | n |
|---|---|---|
| nq | precise | 500 |
| nq | context | 500 |
| nq | mixed | 0 |
| qasper | precise | 1317 |
| qasper | context | 404 |
| qasper | mixed | 476 |
| total | | 3197 |

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.1020 | 0.2721 | 0.3503 | 0.0345 | 0.1102 | 0.1586 |
| fixed-128 | 0.1332 | 0.3200 | 0.4041 | 0.0727 | 0.1904 | 0.2605 |
| fixed-256 | 0.1648 | 0.3682 | 0.4410 | 0.1174 | 0.2917 | 0.3640 |
| fixed-512 | 0.2077 | 0.4257 | 0.4911 | 0.1733 | 0.3835 | 0.4532 |
| fixed-1024 | 0.2562 | 0.4670 | 0.5327 | 0.2371 | 0.4473 | 0.5135 |
| section-aware | 0.1476 | 0.3575 | 0.4288 | 0.1418 | 0.3468 | 0.4171 |
| small-to-big | 0.1414 | 0.3441 | 0.4229 | 0.1354 | 0.3321 | 0.4112 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
