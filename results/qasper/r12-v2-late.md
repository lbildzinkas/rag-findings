# R12 - qasper v2-late: late chunking next to fixed-128, fixed-256 and section-aware

Config hash: `51b80efc3541ab1c57365e69e6d5f0d892c0731e6f2c6b585965b27513a369bc`

## Config

```yaml
chunkings:
- section-aware
- fixed-128
- late-128
- fixed-256
- late-256
embedder: nomic
kind: contenders
pairs:
- - late-128
  - fixed-128
- - late-256
  - fixed-256
pipeline: hybrid-rerank
run_name: v2-late
runs:
- qasper/v2-late
- nq/v2-late
scope: collection
table: r12
title: late chunking next to fixed-128, fixed-256 and section-aware
```

## Runs

| run | dataset | questions | config hash |
|---|---|---|---|
| qasper/v2-late | qasper | 2197 | `4681531b4fc2cba80eacfd6d6d987877685b745fa621c2cfb91bede19c7a8be7` |
| nq/v2-late | nq | 1000 | `9ef43d53b9923e4098976e4539a9426dd274124f3e2e85c2e00d7827fc568dbd` |

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
| fixed-128 | 128 | 0.0439 | 0.0569 | 0.1230 | 0.1218 |
| fixed-128 | 256 | 0.0936 | 0.0603 | 0.1999 | 0.1031 |
| fixed-128 | 512 | 0.1411 | 0.0467 | 0.2742 | 0.0734 |
| fixed-128 | 1024 | 0.1985 | 0.0336 | 0.3519 | 0.0492 |
| fixed-128 | 2048 | 0.2434 | 0.0209 | 0.4123 | 0.0297 |
| fixed-128 | 4096 | 0.2534 | 0.0174 | 0.4256 | 0.0247 |
| fixed-128 | 8192 | 0.2534 | 0.0174 | 0.4256 | 0.0247 |
| late-128 | 128 | 0.0438 | 0.0563 | 0.1246 | 0.1231 |
| late-128 | 256 | 0.0890 | 0.0578 | 0.1995 | 0.1028 |
| late-128 | 512 | 0.1384 | 0.0459 | 0.2796 | 0.0747 |
| late-128 | 1024 | 0.1946 | 0.0330 | 0.3582 | 0.0502 |
| late-128 | 2048 | 0.2412 | 0.0209 | 0.4250 | 0.0307 |
| late-128 | 4096 | 0.2519 | 0.0177 | 0.4412 | 0.0259 |
| late-128 | 8192 | 0.2519 | 0.0177 | 0.4412 | 0.0259 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620 | 0.0425 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.1249 | 0.0443 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.2019 | 0.0352 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.2599 | 0.0240 | 0.4426 | 0.0336 |
| fixed-256 | 4096 | 0.3000 | 0.0143 | 0.4923 | 0.0192 |
| fixed-256 | 8192 | 0.3072 | 0.0120 | 0.5003 | 0.0159 |
| late-256 | 128 | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.0614 | 0.0417 | 0.1766 | 0.0913 |
| late-256 | 512 | 0.1199 | 0.0418 | 0.2721 | 0.0745 |
| late-256 | 1024 | 0.1984 | 0.0349 | 0.3688 | 0.0531 |
| late-256 | 2048 | 0.2593 | 0.0242 | 0.4469 | 0.0341 |
| late-256 | 4096 | 0.2993 | 0.0147 | 0.4972 | 0.0198 |
| late-256 | 8192 | 0.3091 | 0.0125 | 0.5067 | 0.0165 |

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
| fixed-128 | 128 | 0.0439 | 0.0569 | 0.1230 | 0.1218 |
| fixed-128 | 256 | 0.0936 | 0.0603 | 0.1999 | 0.1031 |
| fixed-128 | 512 | 0.1411 | 0.0467 | 0.2742 | 0.0734 |
| fixed-128 | 1024 | 0.1985 | 0.0338 | 0.3519 | 0.0494 |
| fixed-128 | 2048 | 0.1985 | 0.0338 | 0.3519 | 0.0494 |
| fixed-128 | 4096 | 0.1985 | 0.0338 | 0.3519 | 0.0494 |
| fixed-128 | 8192 | 0.1985 | 0.0338 | 0.3519 | 0.0494 |
| late-128 | 128 | 0.0438 | 0.0563 | 0.1246 | 0.1231 |
| late-128 | 256 | 0.0890 | 0.0578 | 0.1995 | 0.1028 |
| late-128 | 512 | 0.1384 | 0.0459 | 0.2796 | 0.0747 |
| late-128 | 1024 | 0.1946 | 0.0333 | 0.3582 | 0.0504 |
| late-128 | 2048 | 0.1946 | 0.0333 | 0.3582 | 0.0504 |
| late-128 | 4096 | 0.1946 | 0.0333 | 0.3582 | 0.0504 |
| late-128 | 8192 | 0.1946 | 0.0333 | 0.3582 | 0.0504 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.0620 | 0.0425 | 0.1764 | 0.0916 |
| fixed-256 | 512 | 0.1249 | 0.0443 | 0.2727 | 0.0756 |
| fixed-256 | 1024 | 0.2019 | 0.0352 | 0.3686 | 0.0531 |
| fixed-256 | 2048 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| fixed-256 | 4096 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| fixed-256 | 8192 | 0.2599 | 0.0243 | 0.4426 | 0.0338 |
| late-256 | 128 | n/a | n/a | n/a | n/a |
| late-256 | 256 | 0.0614 | 0.0417 | 0.1766 | 0.0913 |
| late-256 | 512 | 0.1199 | 0.0418 | 0.2721 | 0.0745 |
| late-256 | 1024 | 0.1984 | 0.0349 | 0.3688 | 0.0531 |
| late-256 | 2048 | 0.2590 | 0.0244 | 0.4467 | 0.0343 |
| late-256 | 4096 | 0.2590 | 0.0244 | 0.4467 | 0.0343 |
| late-256 | 8192 | 0.2590 | 0.0244 | 0.4467 | 0.0343 |

## Contender minus reference

| contender - reference | view | budget | qasper recall | qasper precision | pooled recall | pooled precision |
|---|---|---|---|---|---|---|
| late-128 - fixed-128 | budget | 128 | -0.0002 | -0.0007 | +0.0016 | +0.0014 |
| late-128 - fixed-128 | budget | 256 | -0.0046 | -0.0025 | -0.0005 | -0.0003 |
| late-128 - fixed-128 | budget | 512 | -0.0027 | -0.0008 | +0.0053 | +0.0013 |
| late-128 - fixed-128 | budget | 1024 | -0.0039 | -0.0006 | +0.0064 | +0.0010 |
| late-128 - fixed-128 | budget | 2048 | -0.0023 | -0.0000 | +0.0127 | +0.0010 |
| late-128 - fixed-128 | budget | 4096 | -0.0015 | +0.0003 | +0.0156 | +0.0012 |
| late-128 - fixed-128 | budget | 8192 | -0.0015 | +0.0003 | +0.0156 | +0.0012 |
| late-128 - fixed-128 | production | 128 | -0.0002 | -0.0007 | +0.0016 | +0.0014 |
| late-128 - fixed-128 | production | 256 | -0.0046 | -0.0025 | -0.0005 | -0.0003 |
| late-128 - fixed-128 | production | 512 | -0.0027 | -0.0008 | +0.0053 | +0.0013 |
| late-128 - fixed-128 | production | 1024 | -0.0039 | -0.0006 | +0.0064 | +0.0010 |
| late-128 - fixed-128 | production | 2048 | -0.0039 | -0.0006 | +0.0064 | +0.0010 |
| late-128 - fixed-128 | production | 4096 | -0.0039 | -0.0006 | +0.0064 | +0.0010 |
| late-128 - fixed-128 | production | 8192 | -0.0039 | -0.0006 | +0.0064 | +0.0010 |
| late-256 - fixed-256 | budget | 128 | n/a | n/a | n/a | n/a |
| late-256 - fixed-256 | budget | 256 | -0.0006 | -0.0008 | +0.0002 | -0.0004 |
| late-256 - fixed-256 | budget | 512 | -0.0050 | -0.0026 | -0.0006 | -0.0011 |
| late-256 - fixed-256 | budget | 1024 | -0.0035 | -0.0003 | +0.0002 | +0.0000 |
| late-256 - fixed-256 | budget | 2048 | -0.0006 | +0.0002 | +0.0044 | +0.0005 |
| late-256 - fixed-256 | budget | 4096 | -0.0007 | +0.0005 | +0.0049 | +0.0006 |
| late-256 - fixed-256 | budget | 8192 | +0.0019 | +0.0005 | +0.0064 | +0.0006 |
| late-256 - fixed-256 | production | 128 | n/a | n/a | n/a | n/a |
| late-256 - fixed-256 | production | 256 | -0.0006 | -0.0008 | +0.0002 | -0.0004 |
| late-256 - fixed-256 | production | 512 | -0.0050 | -0.0026 | -0.0006 | -0.0011 |
| late-256 - fixed-256 | production | 1024 | -0.0035 | -0.0003 | +0.0002 | +0.0000 |
| late-256 - fixed-256 | production | 2048 | -0.0009 | +0.0001 | +0.0041 | +0.0005 |
| late-256 - fixed-256 | production | 4096 | -0.0009 | +0.0001 | +0.0041 | +0.0005 |
| late-256 - fixed-256 | production | 8192 | -0.0009 | +0.0001 | +0.0041 | +0.0005 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
