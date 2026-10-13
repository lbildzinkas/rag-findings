# R3 - qasper grid, bm25: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.0373 | 0.0221 | -0.0152 | 0.0373 | 0.0221 | -0.0152 |
| fixed-64 | 256 | 0.0644 | 0.0441 | -0.0202 | 0.0644 | 0.0441 | -0.0202 |
| fixed-64 | 512 | 0.0937 | 0.0687 | -0.0250 | 0.0937 | 0.0687 | -0.0250 |
| fixed-64 | 1024 | 0.0937 | 0.0687 | -0.0250 | 0.1297 | 0.0952 | -0.0346 |
| fixed-64 | 2048 | 0.0937 | 0.0687 | -0.0250 | 0.1688 | 0.1224 | -0.0465 |
| fixed-64 | 4096 | 0.0937 | 0.0687 | -0.0250 | 0.2135 | 0.1547 | -0.0588 |
| fixed-64 | 8192 | 0.0937 | 0.0687 | -0.0250 | 0.2667 | 0.1929 | -0.0738 |
| fixed-128 | 128 | 0.0442 | 0.0183 | -0.0260 | 0.0442 | 0.0183 | -0.0260 |
| fixed-128 | 256 | 0.0729 | 0.0358 | -0.0371 | 0.0729 | 0.0358 | -0.0371 |
| fixed-128 | 512 | 0.1145 | 0.0713 | -0.0432 | 0.1145 | 0.0713 | -0.0432 |
| fixed-128 | 1024 | 0.1640 | 0.1162 | -0.0478 | 0.1640 | 0.1162 | -0.0478 |
| fixed-128 | 2048 | 0.1640 | 0.1162 | -0.0478 | 0.2141 | 0.1564 | -0.0576 |
| fixed-128 | 4096 | 0.1640 | 0.1162 | -0.0478 | 0.2519 | 0.1954 | -0.0564 |
| fixed-128 | 8192 | 0.1640 | 0.1162 | -0.0478 | 0.3032 | 0.2389 | -0.0644 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0609 | 0.0408 | -0.0201 | 0.0609 | 0.0408 | -0.0201 |
| fixed-256 | 512 | 0.0992 | 0.0662 | -0.0330 | 0.0992 | 0.0662 | -0.0330 |
| fixed-256 | 1024 | 0.1518 | 0.1088 | -0.0429 | 0.1518 | 0.1088 | -0.0429 |
| fixed-256 | 2048 | 0.2173 | 0.1725 | -0.0448 | 0.2173 | 0.1725 | -0.0448 |
| fixed-256 | 4096 | 0.2173 | 0.1725 | -0.0448 | 0.2691 | 0.2175 | -0.0515 |
| fixed-256 | 8192 | 0.2173 | 0.1725 | -0.0448 | 0.3295 | 0.2710 | -0.0585 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.0937 | 0.0582 | -0.0355 | 0.0937 | 0.0582 | -0.0355 |
| fixed-512 | 1024 | 0.1451 | 0.1049 | -0.0403 | 0.1451 | 0.1049 | -0.0403 |
| fixed-512 | 2048 | 0.2084 | 0.1612 | -0.0472 | 0.2084 | 0.1612 | -0.0472 |
| fixed-512 | 4096 | 0.2715 | 0.2320 | -0.0395 | 0.2731 | 0.2320 | -0.0411 |
| fixed-512 | 8192 | 0.2715 | 0.2320 | -0.0395 | 0.3396 | 0.2848 | -0.0547 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1356 | 0.0974 | -0.0382 | 0.1356 | 0.0974 | -0.0382 |
| fixed-1024 | 2048 | 0.1991 | 0.1649 | -0.0343 | 0.1991 | 0.1649 | -0.0343 |
| fixed-1024 | 4096 | 0.2675 | 0.2396 | -0.0279 | 0.2675 | 0.2396 | -0.0279 |
| fixed-1024 | 8192 | 0.3174 | 0.2950 | -0.0224 | 0.3198 | 0.2983 | -0.0216 |
| section-aware | 128 | 0.0152 | 0.0103 | -0.0048 | 0.0152 | 0.0103 | -0.0048 |
| section-aware | 256 | 0.0418 | 0.0235 | -0.0183 | 0.0418 | 0.0235 | -0.0183 |
| section-aware | 512 | 0.0934 | 0.0698 | -0.0236 | 0.0934 | 0.0698 | -0.0236 |
| section-aware | 1024 | 0.1625 | 0.1351 | -0.0274 | 0.1625 | 0.1351 | -0.0274 |
| section-aware | 2048 | 0.2278 | 0.1858 | -0.0419 | 0.2339 | 0.1935 | -0.0404 |
| section-aware | 4096 | 0.2483 | 0.1950 | -0.0533 | 0.2969 | 0.2407 | -0.0561 |
| section-aware | 8192 | 0.2483 | 0.1950 | -0.0533 | 0.3516 | 0.2919 | -0.0596 |
| small-to-big | 128 | 0.0441 | 0.0284 | -0.0157 | 0.0441 | 0.0284 | -0.0157 |
| small-to-big | 256 | 0.0651 | 0.0389 | -0.0262 | 0.0651 | 0.0389 | -0.0262 |
| small-to-big | 512 | 0.1145 | 0.0676 | -0.0469 | 0.1145 | 0.0676 | -0.0469 |
| small-to-big | 1024 | 0.1671 | 0.1181 | -0.0491 | 0.1671 | 0.1181 | -0.0491 |
| small-to-big | 2048 | 0.2423 | 0.1670 | -0.0752 | 0.2456 | 0.1701 | -0.0755 |
| small-to-big | 4096 | 0.2597 | 0.1815 | -0.0782 | 0.2978 | 0.2279 | -0.0699 |
| small-to-big | 8192 | 0.2597 | 0.1815 | -0.0782 | 0.3542 | 0.2763 | -0.0780 |

Precise: every usable annotation cites one passage; context: every one cites several; mixed: otherwise. Mixed questions count in the means of R2 but not in this contrast.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
