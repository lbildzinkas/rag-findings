# R13 - qasper v2-contextual: contextual chunks next to fixed-256 and section-aware

Config hash: `1e0a7d13d53a704f52862c6500f2bca6e6fa7bd0dbc880a8dca5f0e65e8c4665`

## Config

```yaml
chunkings:
- section-aware
- fixed-256
- contextual-256
- contextual-256-prefixed
embedder: nomic
kind: contenders
notes:
- contextual-256 packs, scores and hands the reader the chunk text only, so the budget
  counts only its chunk tokens. contextual-256-prefixed ranks the same way, but packing
  counts its prefix, blank line and chunk tokens against the budget and those tokens
  are its retrieved text, precision's denominator; recall is still scored on the chunk's
  span.
pairs:
- - contextual-256
  - fixed-256
- - contextual-256-prefixed
  - contextual-256
pipeline: hybrid-rerank
run_name: v2-contextual
runs:
- qasper/v2-contextual
- nq/v2-contextual
scope: collection
table: r13
title: contextual chunks next to fixed-256 and section-aware
```

## Runs

| run | dataset | questions | config hash |
|---|---|---|---|
| qasper/v2-contextual | qasper | 2197 | `01d4edda6b8a81e5cf45e9c645d840b44d539c024c91adadd154c8159ab1865d` |
| nq/v2-contextual | nq | 1000 | `c2b3f7a5067ebfe8fd56be5157f08019a7f985aa9c57fe528db93ecf9397a053` |

## Dataset

| dataset | split | sha256 |
|---|---|---|
| qasper | dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| qasper | test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |
| nq | dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

Retrieval recall and precision, hybrid-rerank with nomic, collection search: qasper (n = 2197) and pooled (qasper + nq) (n = 3197), means over questions.

## Budget view (top-N cap 20)

| chunking | budget | qasper recall | qasper precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0315 | 0.0292 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.0634 | 0.0365 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.1570 | 0.0555 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.2480 | 0.0467 | 0.4269 | 0.0655 |
| section-aware | 2048 | 0.3076 | 0.0297 | 0.4956 | 0.0394 |
| section-aware | 4096 | 0.3429 | 0.0171 | 0.5325 | 0.0218 |
| section-aware | 8192 | 0.3512 | 0.0136 | 0.5438 | 0.0159 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620 | 0.0425 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.1249 | 0.0443 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.2019 | 0.0352 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.2599 | 0.0240 | 0.4426 | 0.0336 |
| fixed-256 | 4096 | 0.3000 | 0.0143 | 0.4923 | 0.0192 |
| fixed-256 | 8192 | 0.3072 | 0.0120 | 0.5003 | 0.0159 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1056 | 0.0733 | 0.2201 | 0.1206 |
| contextual-256 | 512 | 0.1657 | 0.0593 | 0.3159 | 0.0898 |
| contextual-256 | 1024 | 0.2364 | 0.0424 | 0.4089 | 0.0601 |
| contextual-256 | 2048 | 0.2998 | 0.0287 | 0.4838 | 0.0379 |
| contextual-256 | 4096 | 0.3374 | 0.0167 | 0.5281 | 0.0215 |
| contextual-256 | 8192 | 0.3459 | 0.0142 | 0.5367 | 0.0178 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0049 | 0.0025 | 0.0034 | 0.0017 |
| contextual-256-prefixed | 512 | 0.1091 | 0.0387 | 0.2228 | 0.0657 |
| contextual-256-prefixed | 1024 | 0.2071 | 0.0374 | 0.3685 | 0.0552 |
| contextual-256-prefixed | 2048 | 0.2806 | 0.0265 | 0.4598 | 0.0357 |
| contextual-256-prefixed | 4096 | 0.3319 | 0.0164 | 0.5209 | 0.0211 |
| contextual-256-prefixed | 8192 | 0.3459 | 0.0121 | 0.5367 | 0.0153 |

## Production view (top-N cap 8)

| chunking | budget | qasper recall | qasper precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0315 | 0.0292 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.0634 | 0.0365 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.1570 | 0.0555 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.2471 | 0.0467 | 0.4262 | 0.0656 |
| section-aware | 2048 | 0.3033 | 0.0320 | 0.4923 | 0.0424 |
| section-aware | 4096 | 0.3101 | 0.0300 | 0.5040 | 0.0375 |
| section-aware | 8192 | 0.3101 | 0.0300 | 0.5040 | 0.0375 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620 | 0.0425 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.1249 | 0.0443 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.2019 | 0.0352 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| fixed-256 | 4096 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| fixed-256 | 8192 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.1056 | 0.0733 | 0.2201 | 0.1206 |
| contextual-256 | 512 | 0.1657 | 0.0593 | 0.3159 | 0.0898 |
| contextual-256 | 1024 | 0.2364 | 0.0424 | 0.4089 | 0.0601 |
| contextual-256 | 2048 | 0.2998 | 0.0291 | 0.4838 | 0.0382 |
| contextual-256 | 4096 | 0.2998 | 0.0291 | 0.4838 | 0.0382 |
| contextual-256 | 8192 | 0.2998 | 0.0291 | 0.4838 | 0.0382 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0049 | 0.0025 | 0.0034 | 0.0017 |
| contextual-256-prefixed | 512 | 0.1091 | 0.0387 | 0.2228 | 0.0657 |
| contextual-256-prefixed | 1024 | 0.2071 | 0.0374 | 0.3685 | 0.0552 |
| contextual-256-prefixed | 2048 | 0.2806 | 0.0267 | 0.4598 | 0.0359 |
| contextual-256-prefixed | 4096 | 0.2998 | 0.0249 | 0.4838 | 0.0328 |
| contextual-256-prefixed | 8192 | 0.2998 | 0.0249 | 0.4838 | 0.0328 |

## Contender minus reference

| contender - reference | view | budget | qasper recall | qasper precision | pooled recall | pooled precision |
|---|---|---|---|---|---|---|
| contextual-256 - fixed-256 | budget | 128 | n/a | n/a | n/a | n/a |
| contextual-256 - fixed-256 | budget | 256 | +0.0436 | +0.0307 | +0.0437 | +0.0289 |
| contextual-256 - fixed-256 | budget | 512 | +0.0408 | +0.0149 | +0.0432 | +0.0142 |
| contextual-256 - fixed-256 | budget | 1024 | +0.0345 | +0.0072 | +0.0403 | +0.0070 |
| contextual-256 - fixed-256 | budget | 2048 | +0.0399 | +0.0047 | +0.0412 | +0.0043 |
| contextual-256 - fixed-256 | budget | 4096 | +0.0374 | +0.0025 | +0.0359 | +0.0023 |
| contextual-256 - fixed-256 | budget | 8192 | +0.0387 | +0.0021 | +0.0364 | +0.0019 |
| contextual-256 - fixed-256 | production | 128 | n/a | n/a | n/a | n/a |
| contextual-256 - fixed-256 | production | 256 | +0.0436 | +0.0307 | +0.0437 | +0.0289 |
| contextual-256 - fixed-256 | production | 512 | +0.0408 | +0.0149 | +0.0432 | +0.0142 |
| contextual-256 - fixed-256 | production | 1024 | +0.0345 | +0.0072 | +0.0403 | +0.0070 |
| contextual-256 - fixed-256 | production | 2048 | +0.0399 | +0.0048 | +0.0412 | +0.0044 |
| contextual-256 - fixed-256 | production | 4096 | +0.0399 | +0.0048 | +0.0412 | +0.0044 |
| contextual-256 - fixed-256 | production | 8192 | +0.0399 | +0.0048 | +0.0412 | +0.0044 |
| contextual-256-prefixed - contextual-256 | budget | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed - contextual-256 | budget | 256 | -0.1007 | -0.0708 | -0.2168 | -0.1188 |
| contextual-256-prefixed - contextual-256 | budget | 512 | -0.0566 | -0.0206 | -0.0931 | -0.0241 |
| contextual-256-prefixed - contextual-256 | budget | 1024 | -0.0293 | -0.0049 | -0.0404 | -0.0048 |
| contextual-256-prefixed - contextual-256 | budget | 2048 | -0.0192 | -0.0022 | -0.0240 | -0.0022 |
| contextual-256-prefixed - contextual-256 | budget | 4096 | -0.0054 | -0.0003 | -0.0072 | -0.0003 |
| contextual-256-prefixed - contextual-256 | budget | 8192 | +0.0000 | -0.0020 | +0.0000 | -0.0025 |
| contextual-256-prefixed - contextual-256 | production | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed - contextual-256 | production | 256 | -0.1007 | -0.0708 | -0.2168 | -0.1188 |
| contextual-256-prefixed - contextual-256 | production | 512 | -0.0566 | -0.0206 | -0.0931 | -0.0241 |
| contextual-256-prefixed - contextual-256 | production | 1024 | -0.0293 | -0.0049 | -0.0404 | -0.0048 |
| contextual-256-prefixed - contextual-256 | production | 2048 | -0.0191 | -0.0024 | -0.0240 | -0.0024 |
| contextual-256-prefixed - contextual-256 | production | 4096 | +0.0000 | -0.0042 | +0.0000 | -0.0055 |
| contextual-256-prefixed - contextual-256 | production | 8192 | +0.0000 | -0.0042 | +0.0000 | -0.0055 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.

contextual-256 packs, scores and hands the reader the chunk text only, so the budget counts only its chunk tokens. contextual-256-prefixed ranks the same way, but packing counts its prefix, blank line and chunk tokens against the budget and those tokens are its retrieved text, precision's denominator; recall is still scored on the chunk's span.
