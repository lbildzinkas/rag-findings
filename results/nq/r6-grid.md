# R6 - nq grid, bm25: short-answer span recall

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

## Short-answer span recall, collection search, n = 742 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.1586 | 0.1586 | 0.0000 |
| fixed-64 | 256 | 0.2382 | 0.2382 | 0.0000 |
| fixed-64 | 512 | 0.3460 | 0.3460 | 0.0000 |
| fixed-64 | 1024 | 0.3460† | 0.4463 | 1.0000 |
| fixed-64 | 2048 | 0.3460† | 0.5371 | 1.0000 |
| fixed-64 | 4096 | 0.3460† | 0.5908 | 1.0000 |
| fixed-64 | 8192 | 0.3460† | 0.6641 | 1.0000 |
| fixed-128 | 128 | 0.2108 | 0.2108 | 0.0000 |
| fixed-128 | 256 | 0.3063 | 0.3063 | 0.0000 |
| fixed-128 | 512 | 0.4216 | 0.4216 | 0.0000 |
| fixed-128 | 1024 | 0.5210 | 0.5210 | 0.0020 |
| fixed-128 | 2048 | 0.5210† | 0.6193 | 1.0000 |
| fixed-128 | 4096 | 0.5210† | 0.6969 | 1.0000 |
| fixed-128 | 8192 | 0.5210† | 0.7843 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2712 | 0.2712 | 0.0000 |
| fixed-256 | 512 | 0.4332 | 0.4332 | 0.0000 |
| fixed-256 | 1024 | 0.5513 | 0.5513 | 0.0000 |
| fixed-256 | 2048 | 0.6739 | 0.6739 | 0.0070 |
| fixed-256 | 4096 | 0.6739† | 0.7868 | 0.9990 |
| fixed-256 | 8192 | 0.6739† | 0.8523 | 0.9990 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.3661 | 0.3661 | 0.0000 |
| fixed-512 | 1024 | 0.5632 | 0.5632 | 0.0000 |
| fixed-512 | 2048 | 0.7047 | 0.7047 | 0.0010 |
| fixed-512 | 4096 | 0.8081 | 0.8081 | 0.0840 |
| fixed-512 | 8192 | 0.8081† | 0.8670 | 0.9990 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4506 | 0.4506 | 0.0000 |
| fixed-1024 | 2048 | 0.6541 | 0.6541 | 0.0020 |
| fixed-1024 | 4096 | 0.7915 | 0.7915 | 0.0030 |
| fixed-1024 | 8192 | 0.8871 | 0.8884 | 0.2740 |
| section-aware | 128 | 0.0337 | 0.0337 | 0.0020 |
| section-aware | 256 | 0.1482 | 0.1482 | 0.0110 |
| section-aware | 512 | 0.3733 | 0.3733 | 0.0240 |
| section-aware | 1024 | 0.5566 | 0.5566 | 0.1540 |
| section-aware | 2048 | 0.6954† | 0.6968 | 0.6770 |
| section-aware | 4096 | 0.7439† | 0.7938 | 0.9990 |
| section-aware | 8192 | 0.7439† | 0.8558 | 0.9990 |
| small-to-big | 128 | 0.2029 | 0.2029 | 0.0000 |
| small-to-big | 256 | 0.2933 | 0.2933 | 0.0080 |
| small-to-big | 512 | 0.3762 | 0.3762 | 0.0360 |
| small-to-big | 1024 | 0.5206 | 0.5206 | 0.1790 |
| small-to-big | 2048 | 0.6649† | 0.6663 | 0.7010 |
| small-to-big | 4096 | 0.7332† | 0.7801 | 0.9990 |
| small-to-big | 8192 | 0.7332† | 0.8410 | 0.9990 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
