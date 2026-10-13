# R2w - pooled grid, bm25: chunking x budget, within the document

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
| fixed-64 | 128 | 0.1538 | 0.1624 | 0.1538 | 0.1624 | 0.0000 |
| fixed-64 | 256 | 0.2605 | 0.1428 | 0.2605 | 0.1428 | 0.0000 |
| fixed-64 | 512 | 0.3929 | 0.1161 | 0.3929 | 0.1161 | 0.0000 |
| fixed-64 | 1024 | 0.3929† | 0.1161† | 0.5436 | 0.0938 | 0.9212 |
| fixed-64 | 2048 | 0.3929† | 0.1161† | 0.6759 | 0.0808 | 0.9212 |
| fixed-64 | 4096 | 0.3929† | 0.1161† | 0.7519 | 0.0758 | 0.9212 |
| fixed-64 | 8192 | 0.3929† | 0.1161† | 0.7784 | 0.0749 | 0.9212 |
| fixed-128 | 128 | 0.1646 | 0.1744 | 0.1646 | 0.1744 | 0.0000 |
| fixed-128 | 256 | 0.2694 | 0.1508 | 0.2694 | 0.1508 | 0.0000 |
| fixed-128 | 512 | 0.4183 | 0.1223 | 0.4183 | 0.1223 | 0.0000 |
| fixed-128 | 1024 | 0.5901 | 0.0958 | 0.5901 | 0.0958 | 0.0000 |
| fixed-128 | 2048 | 0.5901† | 0.0958† | 0.7545 | 0.0770 | 0.8821 |
| fixed-128 | 4096 | 0.5901† | 0.0958† | 0.8491 | 0.0679 | 0.8821 |
| fixed-128 | 8192 | 0.5901† | 0.0958† | 0.8821 | 0.0663 | 0.8821 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2454 | 0.1408 | 0.2454 | 0.1408 | 0.0000 |
| fixed-256 | 512 | 0.3946 | 0.1185 | 0.3946 | 0.1185 | 0.0000 |
| fixed-256 | 1024 | 0.5916 | 0.0960 | 0.5916 | 0.0960 | 0.0000 |
| fixed-256 | 2048 | 0.7832 | 0.0746 | 0.7832 | 0.0746 | 0.0000 |
| fixed-256 | 4096 | 0.7832† | 0.0746† | 0.9032 | 0.0617 | 0.7948 |
| fixed-256 | 8192 | 0.7832† | 0.0746† | 0.9376 | 0.0588 | 0.7948 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.3539 | 0.1111 | 0.3539 | 0.1111 | 0.0000 |
| fixed-512 | 1024 | 0.5547 | 0.0922 | 0.5547 | 0.0922 | 0.0000 |
| fixed-512 | 2048 | 0.7713 | 0.0725 | 0.7713 | 0.0725 | 0.0000 |
| fixed-512 | 4096 | 0.9200 | 0.0576 | 0.9200 | 0.0576 | 0.0000 |
| fixed-512 | 8192 | 0.9200† | 0.0576† | 0.9597 | 0.0535 | 0.5017 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4754 | 0.0832 | 0.4754 | 0.0832 | 0.0000 |
| fixed-1024 | 2048 | 0.7178 | 0.0695 | 0.7178 | 0.0695 | 0.0000 |
| fixed-1024 | 4096 | 0.9121 | 0.0561 | 0.9121 | 0.0561 | 0.0000 |
| fixed-1024 | 8192 | 0.9712 | 0.0512 | 0.9712 | 0.0512 | 0.0000 |
| section-aware | 128 | 0.0642 | 0.0667 | 0.0642 | 0.0667 | 0.0000 |
| section-aware | 256 | 0.1656 | 0.1005 | 0.1656 | 0.1005 | 0.0000 |
| section-aware | 512 | 0.3925 | 0.1332 | 0.3925 | 0.1332 | 0.0003 |
| section-aware | 1024 | 0.6194 | 0.1111 | 0.6194 | 0.1111 | 0.0084 |
| section-aware | 2048 | 0.8113 | 0.0861 | 0.8164 | 0.0847 | 0.2243 |
| section-aware | 4096 | 0.8551† | 0.0797† | 0.9167 | 0.0663 | 0.7739 |
| section-aware | 8192 | 0.8551† | 0.0797† | 0.9478 | 0.0624 | 0.7742 |
| small-to-big | 128 | 0.1767 | 0.1967 | 0.1767 | 0.1967 | 0.0000 |
| small-to-big | 256 | 0.2768 | 0.1604 | 0.2768 | 0.1604 | 0.0000 |
| small-to-big | 512 | 0.4386 | 0.1424 | 0.4386 | 0.1424 | 0.0003 |
| small-to-big | 1024 | 0.6254 | 0.1097 | 0.6254 | 0.1096 | 0.0144 |
| small-to-big | 2048 | 0.8036 | 0.0840 | 0.8121 | 0.0823 | 0.3500 |
| small-to-big | 4096 | 0.8422† | 0.0784† | 0.9131 | 0.0660 | 0.7742 |
| small-to-big | 8192 | 0.8422† | 0.0784† | 0.9460 | 0.0623 | 0.7742 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.1538 | 0.1624 | 0.0000 |
| fixed-64 | 256 | 0.2605 | 0.1428 | 0.0000 |
| fixed-64 | 512 | 0.2978† | 0.1338† | 0.9596 |
| fixed-64 | 1024 | 0.2978† | 0.1338† | 0.9596 |
| fixed-64 | 2048 | 0.2978† | 0.1338† | 0.9596 |
| fixed-64 | 4096 | 0.2978† | 0.1338† | 0.9596 |
| fixed-64 | 8192 | 0.2978† | 0.1338† | 0.9596 |
| fixed-128 | 128 | 0.1646 | 0.1744 | 0.0000 |
| fixed-128 | 256 | 0.2694 | 0.1508 | 0.0000 |
| fixed-128 | 512 | 0.4183 | 0.1223 | 0.0000 |
| fixed-128 | 1024 | 0.4706† | 0.1135† | 0.9468 |
| fixed-128 | 2048 | 0.4706† | 0.1135† | 0.9468 |
| fixed-128 | 4096 | 0.4706† | 0.1135† | 0.9468 |
| fixed-128 | 8192 | 0.4706† | 0.1135† | 0.9468 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2454 | 0.1408 | 0.0000 |
| fixed-256 | 512 | 0.3946 | 0.1185 | 0.0000 |
| fixed-256 | 1024 | 0.5916 | 0.0960 | 0.0000 |
| fixed-256 | 2048 | 0.6596† | 0.0886† | 0.9037 |
| fixed-256 | 4096 | 0.6596† | 0.0886† | 0.9037 |
| fixed-256 | 8192 | 0.6596† | 0.0886† | 0.9037 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.3539 | 0.1111 | 0.0000 |
| fixed-512 | 1024 | 0.5547 | 0.0922 | 0.0000 |
| fixed-512 | 2048 | 0.7713 | 0.0725 | 0.0000 |
| fixed-512 | 4096 | 0.8300† | 0.0664† | 0.7804 |
| fixed-512 | 8192 | 0.8300† | 0.0664† | 0.7804 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4754 | 0.0832 | 0.0000 |
| fixed-1024 | 2048 | 0.7178 | 0.0695 | 0.0000 |
| fixed-1024 | 4096 | 0.9121 | 0.0561 | 0.0000 |
| fixed-1024 | 8192 | 0.9441 | 0.0533 | 0.3891 |
| section-aware | 128 | 0.0642 | 0.0667 | 0.0003 |
| section-aware | 256 | 0.1656 | 0.1005 | 0.0038 |
| section-aware | 512 | 0.3922 | 0.1331 | 0.0122 |
| section-aware | 1024 | 0.6128 | 0.1127 | 0.1749 |
| section-aware | 2048 | 0.7388† | 0.0994† | 0.8721 |
| section-aware | 4096 | 0.7397† | 0.0990† | 0.9134 |
| section-aware | 8192 | 0.7397† | 0.0990† | 0.9134 |
| small-to-big | 128 | 0.1767 | 0.1967 | 0.0013 |
| small-to-big | 256 | 0.2768 | 0.1604 | 0.0050 |
| small-to-big | 512 | 0.4381 | 0.1426 | 0.0504 |
| small-to-big | 1024 | 0.6160 | 0.1120 | 0.3266 |
| small-to-big | 2048 | 0.7208† | 0.0969† | 0.8937 |
| small-to-big | 4096 | 0.7224† | 0.0965† | 0.9134 |
| small-to-big | 8192 | 0.7224† | 0.0965† | 0.9134 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
