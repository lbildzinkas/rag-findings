# R13 - nq v2-contextual: contextual chunks next to fixed-256 and section-aware

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

Retrieval recall and precision, hybrid-rerank with nomic, collection search: nq (n = 1000) and pooled (qasper + nq) (n = 3197), means over questions.

## Budget view (top-N cap 20)

| chunking | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0580 | 0.0339 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.2403 | 0.0995 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.6600 | 0.1620 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.8197 | 0.1067 | 0.4269 | 0.0655 |
| section-aware | 2048 | 0.9087 | 0.0609 | 0.4956 | 0.0394 |
| section-aware | 4096 | 0.9489 | 0.0323 | 0.5325 | 0.0218 |
| section-aware | 8192 | 0.9669 | 0.0211 | 0.5438 | 0.0159 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.5975 | 0.1444 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.7350 | 0.0924 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.8439 | 0.0546 | 0.4426 | 0.0336 |
| fixed-256 | 4096 | 0.9147 | 0.0300 | 0.4923 | 0.0192 |
| fixed-256 | 8192 | 0.9247 | 0.0245 | 0.5003 | 0.0159 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4717 | 0.2245 | 0.2201 | 0.1206 |
| contextual-256 | 512 | 0.6459 | 0.1569 | 0.3159 | 0.0898 |
| contextual-256 | 1024 | 0.7880 | 0.0990 | 0.4089 | 0.0601 |
| contextual-256 | 2048 | 0.8881 | 0.0579 | 0.4838 | 0.0379 |
| contextual-256 | 4096 | 0.9472 | 0.0318 | 0.5281 | 0.0215 |
| contextual-256 | 8192 | 0.9559 | 0.0259 | 0.5367 | 0.0178 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000 | 0.0000 | 0.0034 | 0.0017 |
| contextual-256-prefixed | 512 | 0.4727 | 0.1249 | 0.2228 | 0.0657 |
| contextual-256-prefixed | 1024 | 0.7231 | 0.0944 | 0.3685 | 0.0552 |
| contextual-256-prefixed | 2048 | 0.8534 | 0.0558 | 0.4598 | 0.0357 |
| contextual-256-prefixed | 4096 | 0.9361 | 0.0316 | 0.5209 | 0.0211 |
| contextual-256-prefixed | 8192 | 0.9559 | 0.0223 | 0.5367 | 0.0153 |

## Production view (top-N cap 8)

| chunking | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0580 | 0.0339 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.2403 | 0.0995 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.6600 | 0.1621 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.8197 | 0.1072 | 0.4262 | 0.0656 |
| section-aware | 2048 | 0.9077 | 0.0650 | 0.4923 | 0.0424 |
| section-aware | 4096 | 0.9299 | 0.0541 | 0.5040 | 0.0375 |
| section-aware | 8192 | 0.9299 | 0.0541 | 0.5040 | 0.0375 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4278 | 0.1996 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.5975 | 0.1444 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.7350 | 0.0924 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.8439 | 0.0546 | 0.4426 | 0.0338 |
| fixed-256 | 4096 | 0.8439 | 0.0546 | 0.4426 | 0.0338 |
| fixed-256 | 8192 | 0.8439 | 0.0546 | 0.4426 | 0.0338 |
| contextual-256 | 128 | n/a | n/a | n/a | n/a |
| contextual-256 | 256 | 0.4717 | 0.2245 | 0.2201 | 0.1206 |
| contextual-256 | 512 | 0.6459 | 0.1569 | 0.3159 | 0.0898 |
| contextual-256 | 1024 | 0.7880 | 0.0990 | 0.4089 | 0.0601 |
| contextual-256 | 2048 | 0.8881 | 0.0582 | 0.4838 | 0.0382 |
| contextual-256 | 4096 | 0.8881 | 0.0582 | 0.4838 | 0.0382 |
| contextual-256 | 8192 | 0.8881 | 0.0582 | 0.4838 | 0.0382 |
| contextual-256-prefixed | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed | 256 | 0.0000 | 0.0000 | 0.0034 | 0.0017 |
| contextual-256-prefixed | 512 | 0.4727 | 0.1249 | 0.2228 | 0.0657 |
| contextual-256-prefixed | 1024 | 0.7231 | 0.0944 | 0.3685 | 0.0552 |
| contextual-256-prefixed | 2048 | 0.8534 | 0.0559 | 0.4598 | 0.0359 |
| contextual-256-prefixed | 4096 | 0.8881 | 0.0500 | 0.4838 | 0.0328 |
| contextual-256-prefixed | 8192 | 0.8881 | 0.0500 | 0.4838 | 0.0328 |

## Contender minus reference

| contender - reference | view | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|---|
| contextual-256 - fixed-256 | budget | 128 | n/a | n/a | n/a | n/a |
| contextual-256 - fixed-256 | budget | 256 | +0.0439 | +0.0249 | +0.0437 | +0.0289 |
| contextual-256 - fixed-256 | budget | 512 | +0.0484 | +0.0124 | +0.0432 | +0.0142 |
| contextual-256 - fixed-256 | budget | 1024 | +0.0530 | +0.0066 | +0.0403 | +0.0070 |
| contextual-256 - fixed-256 | budget | 2048 | +0.0442 | +0.0033 | +0.0412 | +0.0043 |
| contextual-256 - fixed-256 | budget | 4096 | +0.0325 | +0.0019 | +0.0359 | +0.0023 |
| contextual-256 - fixed-256 | budget | 8192 | +0.0312 | +0.0014 | +0.0364 | +0.0019 |
| contextual-256 - fixed-256 | production | 128 | n/a | n/a | n/a | n/a |
| contextual-256 - fixed-256 | production | 256 | +0.0439 | +0.0249 | +0.0437 | +0.0289 |
| contextual-256 - fixed-256 | production | 512 | +0.0484 | +0.0124 | +0.0432 | +0.0142 |
| contextual-256 - fixed-256 | production | 1024 | +0.0530 | +0.0066 | +0.0403 | +0.0070 |
| contextual-256 - fixed-256 | production | 2048 | +0.0442 | +0.0036 | +0.0412 | +0.0044 |
| contextual-256 - fixed-256 | production | 4096 | +0.0442 | +0.0036 | +0.0412 | +0.0044 |
| contextual-256 - fixed-256 | production | 8192 | +0.0442 | +0.0036 | +0.0412 | +0.0044 |
| contextual-256-prefixed - contextual-256 | budget | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed - contextual-256 | budget | 256 | -0.4717 | -0.2245 | -0.2168 | -0.1188 |
| contextual-256-prefixed - contextual-256 | budget | 512 | -0.1732 | -0.0320 | -0.0931 | -0.0241 |
| contextual-256-prefixed - contextual-256 | budget | 1024 | -0.0649 | -0.0046 | -0.0404 | -0.0048 |
| contextual-256-prefixed - contextual-256 | budget | 2048 | -0.0346 | -0.0021 | -0.0240 | -0.0022 |
| contextual-256-prefixed - contextual-256 | budget | 4096 | -0.0111 | -0.0002 | -0.0072 | -0.0003 |
| contextual-256-prefixed - contextual-256 | budget | 8192 | +0.0000 | -0.0036 | +0.0000 | -0.0025 |
| contextual-256-prefixed - contextual-256 | production | 128 | n/a | n/a | n/a | n/a |
| contextual-256-prefixed - contextual-256 | production | 256 | -0.4717 | -0.2245 | -0.2168 | -0.1188 |
| contextual-256-prefixed - contextual-256 | production | 512 | -0.1732 | -0.0320 | -0.0931 | -0.0241 |
| contextual-256-prefixed - contextual-256 | production | 1024 | -0.0649 | -0.0046 | -0.0404 | -0.0048 |
| contextual-256-prefixed - contextual-256 | production | 2048 | -0.0346 | -0.0023 | -0.0240 | -0.0024 |
| contextual-256-prefixed - contextual-256 | production | 4096 | +0.0000 | -0.0082 | +0.0000 | -0.0055 |
| contextual-256-prefixed - contextual-256 | production | 8192 | +0.0000 | -0.0082 | +0.0000 | -0.0055 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.

contextual-256 packs, scores and hands the reader the chunk text only, so the budget counts only its chunk tokens. contextual-256-prefixed ranks the same way, but packing counts its prefix, blank line and chunk tokens against the budget and those tokens are its retrieved text, precision's denominator; recall is still scored on the chunk's span.
