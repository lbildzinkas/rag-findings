# R3 - nq grid, bm25: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.1411 | 0.1301 | -0.0110 | 0.1411 | 0.1301 | -0.0110 |
| fixed-64 | 256 | 0.2142 | 0.2080 | -0.0063 | 0.2142 | 0.2080 | -0.0063 |
| fixed-64 | 512 | 0.3068 | 0.3042 | -0.0026 | 0.3068 | 0.3042 | -0.0026 |
| fixed-64 | 1024 | 0.3068 | 0.3042 | -0.0026 | 0.4114 | 0.3989 | -0.0126 |
| fixed-64 | 2048 | 0.3068 | 0.3042 | -0.0026 | 0.5009 | 0.4843 | -0.0166 |
| fixed-64 | 4096 | 0.3068 | 0.3042 | -0.0026 | 0.5796 | 0.5753 | -0.0043 |
| fixed-64 | 8192 | 0.3068 | 0.3042 | -0.0026 | 0.6488 | 0.6577 | +0.0089 |
| fixed-128 | 128 | 0.1814 | 0.1723 | -0.0091 | 0.1814 | 0.1723 | -0.0091 |
| fixed-128 | 256 | 0.2833 | 0.2506 | -0.0327 | 0.2833 | 0.2506 | -0.0327 |
| fixed-128 | 512 | 0.3905 | 0.3592 | -0.0313 | 0.3905 | 0.3592 | -0.0313 |
| fixed-128 | 1024 | 0.5015 | 0.4897 | -0.0117 | 0.5015 | 0.4897 | -0.0117 |
| fixed-128 | 2048 | 0.5015 | 0.4897 | -0.0117 | 0.5990 | 0.5993 | +0.0003 |
| fixed-128 | 4096 | 0.5015 | 0.4897 | -0.0117 | 0.6867 | 0.7022 | +0.0156 |
| fixed-128 | 8192 | 0.5015 | 0.4897 | -0.0117 | 0.7708 | 0.7778 | +0.0070 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2692 | 0.2491 | -0.0201 | 0.2692 | 0.2491 | -0.0201 |
| fixed-256 | 512 | 0.4255 | 0.3748 | -0.0506 | 0.4255 | 0.3748 | -0.0506 |
| fixed-256 | 1024 | 0.5410 | 0.5345 | -0.0064 | 0.5410 | 0.5345 | -0.0064 |
| fixed-256 | 2048 | 0.6740 | 0.6620 | -0.0119 | 0.6740 | 0.6620 | -0.0119 |
| fixed-256 | 4096 | 0.6740 | 0.6620 | -0.0119 | 0.7681 | 0.7781 | +0.0100 |
| fixed-256 | 8192 | 0.6740 | 0.6620 | -0.0119 | 0.8339 | 0.8565 | +0.0226 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.4060 | 0.3362 | -0.0698 | 0.4060 | 0.3362 | -0.0698 |
| fixed-512 | 1024 | 0.5720 | 0.5256 | -0.0464 | 0.5720 | 0.5256 | -0.0464 |
| fixed-512 | 2048 | 0.7173 | 0.6875 | -0.0297 | 0.7173 | 0.6875 | -0.0297 |
| fixed-512 | 4096 | 0.8246 | 0.7991 | -0.0255 | 0.8246 | 0.7991 | -0.0255 |
| fixed-512 | 8192 | 0.8246 | 0.7991 | -0.0255 | 0.8775 | 0.8691 | -0.0084 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4608 | 0.4680 | +0.0072 | 0.4608 | 0.4680 | +0.0072 |
| fixed-1024 | 2048 | 0.6686 | 0.6437 | -0.0249 | 0.6686 | 0.6437 | -0.0249 |
| fixed-1024 | 4096 | 0.8031 | 0.7784 | -0.0247 | 0.8031 | 0.7784 | -0.0247 |
| fixed-1024 | 8192 | 0.8993 | 0.8780 | -0.0213 | 0.8993 | 0.8800 | -0.0193 |
| section-aware | 128 | 0.0420 | 0.0360 | -0.0060 | 0.0420 | 0.0360 | -0.0060 |
| section-aware | 256 | 0.1820 | 0.1460 | -0.0360 | 0.1820 | 0.1460 | -0.0360 |
| section-aware | 512 | 0.4080 | 0.3720 | -0.0360 | 0.4080 | 0.3720 | -0.0360 |
| section-aware | 1024 | 0.5700 | 0.5779 | +0.0079 | 0.5700 | 0.5779 | +0.0079 |
| section-aware | 2048 | 0.7120 | 0.7179 | +0.0059 | 0.7120 | 0.7219 | +0.0099 |
| section-aware | 4096 | 0.7740 | 0.7619 | -0.0121 | 0.8080 | 0.8119 | +0.0039 |
| section-aware | 8192 | 0.7740 | 0.7619 | -0.0121 | 0.8660 | 0.8839 | +0.0179 |
| small-to-big | 128 | 0.1948 | 0.1601 | -0.0347 | 0.1948 | 0.1601 | -0.0347 |
| small-to-big | 256 | 0.2906 | 0.2645 | -0.0261 | 0.2906 | 0.2645 | -0.0261 |
| small-to-big | 512 | 0.4051 | 0.3832 | -0.0220 | 0.4051 | 0.3832 | -0.0220 |
| small-to-big | 1024 | 0.5368 | 0.5464 | +0.0096 | 0.5368 | 0.5464 | +0.0096 |
| small-to-big | 2048 | 0.6809 | 0.6771 | -0.0038 | 0.6849 | 0.6771 | -0.0078 |
| small-to-big | 4096 | 0.7380 | 0.7440 | +0.0060 | 0.7888 | 0.7752 | -0.0136 |
| small-to-big | 8192 | 0.7380 | 0.7440 | +0.0060 | 0.8525 | 0.8558 | +0.0033 |

Query types are assigned from the labels: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several and mixed otherwise (only that rule produces mixed questions, which count in the means of R2 but not in this contrast).
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
