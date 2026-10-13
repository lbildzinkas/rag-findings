# R2 - qasper grid, bm25: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.0351 | 0.0431 | 0.0351 | 0.0431 | 0.0000 |
| fixed-64 | 256 | 0.0610 | 0.0372 | 0.0610 | 0.0372 | 0.0000 |
| fixed-64 | 512 | 0.0910 | 0.0280 | 0.0910 | 0.0279 | 0.0801 |
| fixed-64 | 1024 | 0.0910† | 0.0280† | 0.1265 | 0.0198 | 0.9995 |
| fixed-64 | 2048 | 0.0910† | 0.0280† | 0.1649 | 0.0132 | 0.9995 |
| fixed-64 | 4096 | 0.0910† | 0.0280† | 0.2072 | 0.0083 | 0.9995 |
| fixed-64 | 8192 | 0.0910† | 0.0280† | 0.2555 | 0.0053 | 0.9995 |
| fixed-128 | 128 | 0.0388 | 0.0467 | 0.0388 | 0.0467 | 0.0000 |
| fixed-128 | 256 | 0.0645 | 0.0402 | 0.0645 | 0.0402 | 0.0005 |
| fixed-128 | 512 | 0.1060 | 0.0344 | 0.1060 | 0.0344 | 0.0009 |
| fixed-128 | 1024 | 0.1560 | 0.0261 | 0.1560 | 0.0260 | 0.1193 |
| fixed-128 | 2048 | 0.1560† | 0.0261† | 0.2040 | 0.0174 | 0.9995 |
| fixed-128 | 4096 | 0.1560† | 0.0261† | 0.2449 | 0.0106 | 0.9995 |
| fixed-128 | 8192 | 0.1560† | 0.0261† | 0.2950 | 0.0065 | 0.9995 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0552 | 0.0363 | 0.0552 | 0.0363 | 0.0000 |
| fixed-256 | 512 | 0.0934 | 0.0320 | 0.0934 | 0.0320 | 0.0000 |
| fixed-256 | 1024 | 0.1476 | 0.0259 | 0.1476 | 0.0259 | 0.0000 |
| fixed-256 | 2048 | 0.2120 | 0.0195 | 0.2120 | 0.0193 | 0.2089 |
| fixed-256 | 4096 | 0.2120† | 0.0195† | 0.2620 | 0.0122 | 0.9995 |
| fixed-256 | 8192 | 0.2120† | 0.0195† | 0.3202 | 0.0077 | 0.9995 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.0862 | 0.0319 | 0.0862 | 0.0319 | 0.0000 |
| fixed-512 | 1024 | 0.1384 | 0.0264 | 0.1384 | 0.0264 | 0.0000 |
| fixed-512 | 2048 | 0.2053 | 0.0201 | 0.2053 | 0.0201 | 0.0046 |
| fixed-512 | 4096 | 0.2691 | 0.0135 | 0.2700 | 0.0132 | 0.4083 |
| fixed-512 | 8192 | 0.2691† | 0.0135† | 0.3260 | 0.0082 | 0.9995 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1286 | 0.0253 | 0.1286 | 0.0253 | 0.0000 |
| fixed-1024 | 2048 | 0.1955 | 0.0198 | 0.1955 | 0.0198 | 0.0005 |
| fixed-1024 | 4096 | 0.2640 | 0.0138 | 0.2640 | 0.0138 | 0.0073 |
| fixed-1024 | 8192 | 0.3162† | 0.0090† | 0.3187 | 0.0086 | 0.6787 |
| section-aware | 128 | 0.0167 | 0.0164 | 0.0167 | 0.0164 | 0.0000 |
| section-aware | 256 | 0.0389 | 0.0214 | 0.0389 | 0.0214 | 0.0000 |
| section-aware | 512 | 0.0922 | 0.0331 | 0.0922 | 0.0331 | 0.0009 |
| section-aware | 1024 | 0.1601 | 0.0300 | 0.1601 | 0.0300 | 0.1061 |
| section-aware | 2048 | 0.2231† | 0.0225† | 0.2297 | 0.0219 | 0.6846 |
| section-aware | 4096 | 0.2396† | 0.0217† | 0.2862 | 0.0140 | 0.9995 |
| section-aware | 8192 | 0.2396† | 0.0217† | 0.3445 | 0.0085 | 0.9995 |
| small-to-big | 128 | 0.0411 | 0.0531 | 0.0411 | 0.0531 | 0.0014 |
| small-to-big | 256 | 0.0613 | 0.0402 | 0.0613 | 0.0402 | 0.0036 |
| small-to-big | 512 | 0.1034 | 0.0373 | 0.1034 | 0.0373 | 0.0364 |
| small-to-big | 1024 | 0.1568 | 0.0296 | 0.1568 | 0.0295 | 0.1293 |
| small-to-big | 2048 | 0.2247† | 0.0227† | 0.2279 | 0.0219 | 0.7720 |
| small-to-big | 4096 | 0.2406† | 0.0203† | 0.2842 | 0.0139 | 0.9995 |
| small-to-big | 8192 | 0.2406† | 0.0203† | 0.3392 | 0.0085 | 0.9995 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.0351 | 0.0431 | 0.0032 |
| fixed-64 | 256 | 0.0610 | 0.0372 | 0.0205 |
| fixed-64 | 512 | 0.0688† | 0.0337† | 1.0000 |
| fixed-64 | 1024 | 0.0688† | 0.0337† | 1.0000 |
| fixed-64 | 2048 | 0.0688† | 0.0337† | 1.0000 |
| fixed-64 | 4096 | 0.0688† | 0.0337† | 1.0000 |
| fixed-64 | 8192 | 0.0688† | 0.0337† | 1.0000 |
| fixed-128 | 128 | 0.0388 | 0.0467 | 0.0005 |
| fixed-128 | 256 | 0.0645 | 0.0402 | 0.0023 |
| fixed-128 | 512 | 0.1060 | 0.0345 | 0.0228 |
| fixed-128 | 1024 | 0.1220† | 0.0320† | 1.0000 |
| fixed-128 | 2048 | 0.1220† | 0.0320† | 1.0000 |
| fixed-128 | 4096 | 0.1220† | 0.0320† | 1.0000 |
| fixed-128 | 8192 | 0.1220† | 0.0320† | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0552 | 0.0363 | 0.0000 |
| fixed-256 | 512 | 0.0934 | 0.0320 | 0.0018 |
| fixed-256 | 1024 | 0.1476 | 0.0260 | 0.0514 |
| fixed-256 | 2048 | 0.1700† | 0.0242† | 0.9995 |
| fixed-256 | 4096 | 0.1700† | 0.0242† | 0.9995 |
| fixed-256 | 8192 | 0.1700† | 0.0242† | 0.9995 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.0862 | 0.0319 | 0.0005 |
| fixed-512 | 1024 | 0.1384 | 0.0264 | 0.0086 |
| fixed-512 | 2048 | 0.2052 | 0.0202 | 0.1411 |
| fixed-512 | 4096 | 0.2253† | 0.0182† | 0.9995 |
| fixed-512 | 8192 | 0.2253† | 0.0182† | 0.9995 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.1286 | 0.0253 | 0.0014 |
| fixed-1024 | 2048 | 0.1955 | 0.0198 | 0.0146 |
| fixed-1024 | 4096 | 0.2640 | 0.0140 | 0.2890 |
| fixed-1024 | 8192 | 0.2813† | 0.0125† | 0.9995 |
| section-aware | 128 | 0.0167 | 0.0164 | 0.0000 |
| section-aware | 256 | 0.0389 | 0.0214 | 0.0050 |
| section-aware | 512 | 0.0918 | 0.0331 | 0.1179 |
| section-aware | 1024 | 0.1585† | 0.0311† | 0.5521 |
| section-aware | 2048 | 0.1910† | 0.0277† | 0.9991 |
| section-aware | 4096 | 0.1910† | 0.0276† | 1.0000 |
| section-aware | 8192 | 0.1910† | 0.0276† | 1.0000 |
| small-to-big | 128 | 0.0411 | 0.0532 | 0.0614 |
| small-to-big | 256 | 0.0613 | 0.0403 | 0.1284 |
| small-to-big | 512 | 0.1033 | 0.0375 | 0.3118 |
| small-to-big | 1024 | 0.1547† | 0.0307† | 0.7151 |
| small-to-big | 2048 | 0.1951† | 0.0268† | 0.9982 |
| small-to-big | 4096 | 0.1956† | 0.0268† | 1.0000 |
| small-to-big | 8192 | 0.1956† | 0.0268† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
