# R2 - pooled grid, bm25: chunking x budget, collection search

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

## Production view (top-N cap 8) and fair view (no cap)

| chunking | budget | production recall | production precision | fair recall | fair precision | cap binds |
|---|---|---|---|---|---|---|
| fixed-64 | 128 | 0.0664 | 0.0646 | 0.0664 | 0.0646 | 0.0000 |
| fixed-64 | 256 | 0.1043 | 0.0518 | 0.1043 | 0.0518 | 0.0000 |
| fixed-64 | 512 | 0.1534 | 0.0392 | 0.1535 | 0.0391 | 0.0582 |
| fixed-64 | 1024 | 0.1534† | 0.0392† | 0.2065 | 0.0268 | 1.0000 |
| fixed-64 | 2048 | 0.1534† | 0.0392† | 0.2611 | 0.0172 | 1.0000 |
| fixed-64 | 4096 | 0.1534† | 0.0392† | 0.3167 | 0.0109 | 1.0000 |
| fixed-64 | 8192 | 0.1534† | 0.0392† | 0.3700 | 0.0065 | 1.0000 |
| fixed-128 | 128 | 0.0814 | 0.0796 | 0.0814 | 0.0796 | 0.0000 |
| fixed-128 | 256 | 0.1258 | 0.0642 | 0.1258 | 0.0642 | 0.0000 |
| fixed-128 | 512 | 0.1897 | 0.0499 | 0.1897 | 0.0499 | 0.0006 |
| fixed-128 | 1024 | 0.2558 | 0.0350 | 0.2558 | 0.0349 | 0.0813 |
| fixed-128 | 2048 | 0.2558† | 0.0350† | 0.3231 | 0.0228 | 1.0000 |
| fixed-128 | 4096 | 0.2558† | 0.0350† | 0.3786 | 0.0136 | 1.0000 |
| fixed-128 | 8192 | 0.2558† | 0.0350† | 0.4391 | 0.0081 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.1215 | 0.0637 | 0.1215 | 0.0637 | 0.0000 |
| fixed-256 | 512 | 0.1868 | 0.0502 | 0.1868 | 0.0502 | 0.0000 |
| fixed-256 | 1024 | 0.2699 | 0.0382 | 0.2699 | 0.0382 | 0.0003 |
| fixed-256 | 2048 | 0.3517 | 0.0261 | 0.3518 | 0.0259 | 0.1476 |
| fixed-256 | 4096 | 0.3517† | 0.0261† | 0.4200 | 0.0160 | 0.9994 |
| fixed-256 | 8192 | 0.3517† | 0.0261† | 0.4785 | 0.0094 | 0.9994 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1766 | 0.0509 | 0.1766 | 0.0509 | 0.0000 |
| fixed-512 | 1024 | 0.2696 | 0.0401 | 0.2696 | 0.0401 | 0.0000 |
| fixed-512 | 2048 | 0.3584 | 0.0277 | 0.3584 | 0.0277 | 0.0013 |
| fixed-512 | 4096 | 0.4398 | 0.0177 | 0.4402 | 0.0175 | 0.3000 |
| fixed-512 | 8192 | 0.4398† | 0.0177† | 0.4917 | 0.0101 | 0.9994 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.2382 | 0.0371 | 0.2382 | 0.0371 | 0.0000 |
| fixed-1024 | 2048 | 0.3418 | 0.0274 | 0.3418 | 0.0274 | 0.0006 |
| fixed-1024 | 4096 | 0.4266 | 0.0179 | 0.4266 | 0.0179 | 0.0063 |
| fixed-1024 | 8192 | 0.4976† | 0.0111† | 0.4995 | 0.0107 | 0.5499 |
| section-aware | 128 | 0.0244 | 0.0187 | 0.0244 | 0.0187 | 0.0016 |
| section-aware | 256 | 0.0773 | 0.0353 | 0.0773 | 0.0353 | 0.0041 |
| section-aware | 512 | 0.1855 | 0.0530 | 0.1855 | 0.0530 | 0.0100 |
| section-aware | 1024 | 0.2880 | 0.0429 | 0.2882 | 0.0428 | 0.1073 |
| section-aware | 2048 | 0.3749† | 0.0305† | 0.3784 | 0.0291 | 0.6941 |
| section-aware | 4096 | 0.4012† | 0.0275† | 0.4468 | 0.0179 | 0.9997 |
| section-aware | 8192 | 0.4012† | 0.0275† | 0.5034 | 0.0103 | 0.9997 |
| small-to-big | 128 | 0.0831 | 0.0837 | 0.0831 | 0.0837 | 0.0009 |
| small-to-big | 256 | 0.1283 | 0.0647 | 0.1283 | 0.0647 | 0.0066 |
| small-to-big | 512 | 0.1942 | 0.0552 | 0.1942 | 0.0552 | 0.0394 |
| small-to-big | 1024 | 0.2774 | 0.0416 | 0.2774 | 0.0414 | 0.1611 |
| small-to-big | 2048 | 0.3629† | 0.0294† | 0.3667 | 0.0284 | 0.7576 |
| small-to-big | 4096 | 0.3903† | 0.0256† | 0.4350 | 0.0173 | 0.9997 |
| small-to-big | 8192 | 0.3903† | 0.0256† | 0.4939 | 0.0101 | 0.9997 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.0664 | 0.0646 | 0.0003 |
| fixed-64 | 256 | 0.1043 | 0.0518 | 0.0138 |
| fixed-64 | 512 | 0.1201† | 0.0478† | 1.0000 |
| fixed-64 | 1024 | 0.1201† | 0.0478† | 1.0000 |
| fixed-64 | 2048 | 0.1201† | 0.0478† | 1.0000 |
| fixed-64 | 4096 | 0.1201† | 0.0478† | 1.0000 |
| fixed-64 | 8192 | 0.1201† | 0.0478† | 1.0000 |
| fixed-128 | 128 | 0.0814 | 0.0796 | 0.0003 |
| fixed-128 | 256 | 0.1258 | 0.0642 | 0.0019 |
| fixed-128 | 512 | 0.1897 | 0.0500 | 0.0144 |
| fixed-128 | 1024 | 0.2084† | 0.0447† | 1.0000 |
| fixed-128 | 2048 | 0.2084† | 0.0447† | 1.0000 |
| fixed-128 | 4096 | 0.2084† | 0.0447† | 1.0000 |
| fixed-128 | 8192 | 0.2084† | 0.0447† | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.1215 | 0.0637 | 0.0000 |
| fixed-256 | 512 | 0.1868 | 0.0502 | 0.0016 |
| fixed-256 | 1024 | 0.2699 | 0.0383 | 0.0341 |
| fixed-256 | 2048 | 0.3015† | 0.0346† | 1.0000 |
| fixed-256 | 4096 | 0.3015† | 0.0346† | 1.0000 |
| fixed-256 | 8192 | 0.3015† | 0.0346† | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.1766 | 0.0509 | 0.0003 |
| fixed-512 | 1024 | 0.2696 | 0.0401 | 0.0047 |
| fixed-512 | 2048 | 0.3584 | 0.0278 | 0.0976 |
| fixed-512 | 4096 | 0.3874† | 0.0244† | 1.0000 |
| fixed-512 | 8192 | 0.3874† | 0.0244† | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.2382 | 0.0371 | 0.0009 |
| fixed-1024 | 2048 | 0.3418 | 0.0275 | 0.0084 |
| fixed-1024 | 4096 | 0.4266 | 0.0181 | 0.1992 |
| fixed-1024 | 8192 | 0.4505† | 0.0159† | 0.9994 |
| section-aware | 128 | 0.0244 | 0.0187 | 0.0394 |
| section-aware | 256 | 0.0773 | 0.0356 | 0.0879 |
| section-aware | 512 | 0.1851 | 0.0535 | 0.1880 |
| section-aware | 1024 | 0.2864† | 0.0447† | 0.6143 |
| section-aware | 2048 | 0.3478† | 0.0384† | 0.9962 |
| section-aware | 4096 | 0.3478† | 0.0381† | 1.0000 |
| section-aware | 8192 | 0.3478† | 0.0381† | 1.0000 |
| small-to-big | 128 | 0.0831 | 0.0838 | 0.0535 |
| small-to-big | 256 | 0.1283 | 0.0649 | 0.1386 |
| small-to-big | 512 | 0.1942 | 0.0559 | 0.3244 |
| small-to-big | 1024 | 0.2747† | 0.0436† | 0.7226 |
| small-to-big | 2048 | 0.3301† | 0.0360† | 0.9962 |
| small-to-big | 4096 | 0.3327† | 0.0358† | 1.0000 |
| small-to-big | 8192 | 0.3327† | 0.0358† | 1.0000 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
