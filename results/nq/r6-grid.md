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

## Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.1853 | 0.1853 | 0.0000 |
| fixed-64 | 256 | 0.2731 | 0.2731 | 0.0000 |
| fixed-64 | 512 | 0.3868 | 0.3868 | 0.0000 |
| fixed-64 | 1024 | 0.3868† | 0.4866 | 1.0000 |
| fixed-64 | 2048 | 0.3868† | 0.5805 | 1.0000 |
| fixed-64 | 4096 | 0.3868† | 0.6311 | 1.0000 |
| fixed-64 | 8192 | 0.3868† | 0.7031 | 1.0000 |
| fixed-128 | 128 | 0.2355 | 0.2355 | 0.0000 |
| fixed-128 | 256 | 0.3472 | 0.3472 | 0.0000 |
| fixed-128 | 512 | 0.4795 | 0.4795 | 0.0000 |
| fixed-128 | 1024 | 0.5615 | 0.5615 | 0.0041 |
| fixed-128 | 2048 | 0.5615† | 0.6617 | 1.0000 |
| fixed-128 | 4096 | 0.5615† | 0.7258 | 1.0000 |
| fixed-128 | 8192 | 0.5615† | 0.8115 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.3106 | 0.3106 | 0.0000 |
| fixed-256 | 512 | 0.4890 | 0.4890 | 0.0000 |
| fixed-256 | 1024 | 0.5922 | 0.5922 | 0.0000 |
| fixed-256 | 2048 | 0.7053 | 0.7053 | 0.0083 |
| fixed-256 | 4096 | 0.7053† | 0.8042 | 0.9979 |
| fixed-256 | 8192 | 0.7053† | 0.8597 | 0.9979 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.4137 | 0.4137 | 0.0000 |
| fixed-512 | 1024 | 0.6083 | 0.6083 | 0.0000 |
| fixed-512 | 2048 | 0.7470 | 0.7470 | 0.0021 |
| fixed-512 | 4096 | 0.8385 | 0.8385 | 0.0704 |
| fixed-512 | 8192 | 0.8385† | 0.8820 | 0.9979 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4696 | 0.4696 | 0.0000 |
| fixed-1024 | 2048 | 0.6766 | 0.6766 | 0.0041 |
| fixed-1024 | 4096 | 0.8071 | 0.8071 | 0.0062 |
| fixed-1024 | 8192 | 0.9000 | 0.9000 | 0.2754 |
| section-aware | 128 | 0.0352 | 0.0352 | 0.0041 |
| section-aware | 256 | 0.1698 | 0.1698 | 0.0083 |
| section-aware | 512 | 0.4099 | 0.4099 | 0.0166 |
| section-aware | 1024 | 0.5859 | 0.5859 | 0.1491 |
| section-aware | 2048 | 0.7246† | 0.7246 | 0.6480 |
| section-aware | 4096 | 0.7764† | 0.8116 | 0.9979 |
| section-aware | 8192 | 0.7764† | 0.8675 | 0.9979 |
| small-to-big | 128 | 0.2402 | 0.2402 | 0.0000 |
| small-to-big | 256 | 0.3349 | 0.3349 | 0.0041 |
| small-to-big | 512 | 0.4080 | 0.4080 | 0.0311 |
| small-to-big | 1024 | 0.5507 | 0.5507 | 0.1698 |
| small-to-big | 2048 | 0.6923† | 0.6943 | 0.6749 |
| small-to-big | 4096 | 0.7557† | 0.8029 | 0.9979 |
| small-to-big | 8192 | 0.7557† | 0.8592 | 0.9979 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
