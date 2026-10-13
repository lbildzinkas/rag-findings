# R4 - nq grid, bm25: fixed-k

Config hash: `d7dd7e084b9247e3b81b87274351dc6c243892605fe631984f1cfe3dcd7cd969`

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
  name: nq
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
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.2010 | 0.4910 | 0.6220 | 0.0743 | 0.2246 | 0.3212 |
| fixed-128 | 0.2660 | 0.5770 | 0.7130 | 0.1613 | 0.3794 | 0.5058 |
| fixed-256 | 0.3270 | 0.6850 | 0.7870 | 0.2533 | 0.5833 | 0.6910 |
| fixed-512 | 0.4070 | 0.7810 | 0.8570 | 0.3673 | 0.7433 | 0.8333 |
| fixed-1024 | 0.4750 | 0.8350 | 0.9090 | 0.4640 | 0.8270 | 0.9055 |
| section-aware | 0.3250 | 0.6880 | 0.7850 | 0.3245 | 0.6870 | 0.7840 |
| small-to-big | 0.2990 | 0.6390 | 0.7700 | 0.2985 | 0.6385 | 0.7695 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
