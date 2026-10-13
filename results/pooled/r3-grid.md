# R3 - pooled grid, bm25: chunk size x query type

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

## Retrieval recall by query type, collection search (production view: top-N cap 8)

| chunking | budget | production precise | production context | production context - precise | fair precise | fair context | fair context - precise |
|---|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.0655 | 0.0813 | +0.0158 | 0.0655 | 0.0813 | +0.0158 |
| fixed-64 | 256 | 0.1004 | 0.1321 | +0.0318 | 0.1004 | 0.1321 | +0.0318 |
| fixed-64 | 512 | 0.1471 | 0.1952 | +0.0481 | 0.1471 | 0.1952 | +0.0481 |
| fixed-64 | 1024 | 0.1471 | 0.1952 | +0.0481 | 0.1970 | 0.2598 | +0.0628 |
| fixed-64 | 2048 | 0.1471 | 0.1952 | +0.0481 | 0.2507 | 0.3224 | +0.0718 |
| fixed-64 | 4096 | 0.1471 | 0.1952 | +0.0481 | 0.3065 | 0.3824 | +0.0759 |
| fixed-64 | 8192 | 0.1471 | 0.1952 | +0.0481 | 0.3608 | 0.4424 | +0.0816 |
| fixed-128 | 128 | 0.0811 | 0.1022 | +0.0211 | 0.0811 | 0.1022 | +0.0211 |
| fixed-128 | 256 | 0.1283 | 0.1524 | +0.0242 | 0.1283 | 0.1524 | +0.0242 |
| fixed-128 | 512 | 0.1894 | 0.2332 | +0.0437 | 0.1894 | 0.2332 | +0.0437 |
| fixed-128 | 1024 | 0.2484 | 0.3221 | +0.0737 | 0.2484 | 0.3221 | +0.0737 |
| fixed-128 | 2048 | 0.2484 | 0.3221 | +0.0737 | 0.3112 | 0.4009 | +0.0897 |
| fixed-128 | 4096 | 0.2484 | 0.3221 | +0.0737 | 0.3623 | 0.4712 | +0.1089 |
| fixed-128 | 8192 | 0.2484 | 0.3221 | +0.0737 | 0.4270 | 0.5286 | +0.1016 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.1172 | 0.1615 | +0.0442 | 0.1172 | 0.1615 | +0.0442 |
| fixed-256 | 512 | 0.1817 | 0.2395 | +0.0579 | 0.1817 | 0.2395 | +0.0579 |
| fixed-256 | 1024 | 0.2580 | 0.3434 | +0.0854 | 0.2580 | 0.3434 | +0.0854 |
| fixed-256 | 2048 | 0.3377 | 0.4417 | +0.1040 | 0.3377 | 0.4420 | +0.1043 |
| fixed-256 | 4096 | 0.3377 | 0.4417 | +0.1040 | 0.4037 | 0.5298 | +0.1260 |
| fixed-256 | 8192 | 0.3377 | 0.4417 | +0.1040 | 0.4616 | 0.5907 | +0.1291 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1795 | 0.2165 | +0.0370 | 0.1795 | 0.2165 | +0.0370 |
| fixed-512 | 1024 | 0.2621 | 0.3446 | +0.0825 | 0.2621 | 0.3446 | +0.0825 |
| fixed-512 | 2048 | 0.3454 | 0.4514 | +0.1060 | 0.3454 | 0.4514 | +0.1060 |
| fixed-512 | 4096 | 0.4270 | 0.5445 | +0.1175 | 0.4276 | 0.5447 | +0.1171 |
| fixed-512 | 8192 | 0.4270 | 0.5445 | +0.1175 | 0.4752 | 0.6073 | +0.1322 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.2267 | 0.3061 | +0.0794 | 0.2267 | 0.3061 | +0.0794 |
| fixed-1024 | 2048 | 0.3305 | 0.4335 | +0.1029 | 0.3305 | 0.4335 | +0.1029 |
| fixed-1024 | 4096 | 0.4102 | 0.5374 | +0.1273 | 0.4102 | 0.5374 | +0.1273 |
| fixed-1024 | 8192 | 0.4810 | 0.6095 | +0.1285 | 0.4828 | 0.6116 | +0.1289 |
| section-aware | 128 | 0.0237 | 0.0257 | +0.0020 | 0.0237 | 0.0257 | +0.0020 |
| section-aware | 256 | 0.0793 | 0.0913 | +0.0120 | 0.0793 | 0.0913 | +0.0120 |
| section-aware | 512 | 0.1789 | 0.2381 | +0.0592 | 0.1789 | 0.2381 | +0.0592 |
| section-aware | 1024 | 0.2713 | 0.3792 | +0.1079 | 0.2713 | 0.3792 | +0.1079 |
| section-aware | 2048 | 0.3594 | 0.4748 | +0.1154 | 0.3627 | 0.4787 | +0.1160 |
| section-aware | 4096 | 0.3891 | 0.5056 | +0.1165 | 0.4309 | 0.5563 | +0.1254 |
| section-aware | 8192 | 0.3891 | 0.5056 | +0.1165 | 0.4843 | 0.6137 | +0.1293 |
| small-to-big | 128 | 0.0853 | 0.0994 | +0.0142 | 0.0853 | 0.0994 | +0.0142 |
| small-to-big | 256 | 0.1272 | 0.1613 | +0.0341 | 0.1272 | 0.1613 | +0.0341 |
| small-to-big | 512 | 0.1945 | 0.2397 | +0.0452 | 0.1945 | 0.2397 | +0.0452 |
| small-to-big | 1024 | 0.2671 | 0.3536 | +0.0865 | 0.2671 | 0.3536 | +0.0865 |
| small-to-big | 2048 | 0.3537 | 0.4521 | +0.0983 | 0.3586 | 0.4545 | +0.0959 |
| small-to-big | 4096 | 0.3792 | 0.4901 | +0.1109 | 0.4237 | 0.5370 | +0.1133 |
| small-to-big | 8192 | 0.3792 | 0.4901 | +0.1109 | 0.4823 | 0.5948 | +0.1125 |

Precise: every usable annotation cites one passage; context: every one cites several; mixed: otherwise. Mixed questions count in the means of R2 but not in this contrast.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
