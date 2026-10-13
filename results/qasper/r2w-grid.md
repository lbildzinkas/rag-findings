# R2w - qasper grid, bm25: chunking x budget, within the document

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
| fixed-64 | 128 | 0.1526 | 0.1763 | 0.1526 | 0.1763 | 0.0000 |
| fixed-64 | 256 | 0.2569 | 0.1547 | 0.2569 | 0.1547 | 0.0000 |
| fixed-64 | 512 | 0.3971 | 0.1290 | 0.3971 | 0.1290 | 0.0000 |
| fixed-64 | 1024 | 0.3971† | 0.1290† | 0.5491 | 0.1048 | 0.9058 |
| fixed-64 | 2048 | 0.3971† | 0.1290† | 0.6823 | 0.0915 | 0.9058 |
| fixed-64 | 4096 | 0.3971† | 0.1290† | 0.7430 | 0.0868 | 0.9058 |
| fixed-64 | 8192 | 0.3971† | 0.1290† | 0.7494 | 0.0863 | 0.9058 |
| fixed-128 | 128 | 0.1482 | 0.1739 | 0.1482 | 0.1739 | 0.0000 |
| fixed-128 | 256 | 0.2545 | 0.1562 | 0.2545 | 0.1562 | 0.0000 |
| fixed-128 | 512 | 0.4053 | 0.1310 | 0.4053 | 0.1310 | 0.0000 |
| fixed-128 | 1024 | 0.5908 | 0.1059 | 0.5908 | 0.1059 | 0.0000 |
| fixed-128 | 2048 | 0.5908† | 0.1059† | 0.7649 | 0.0864 | 0.8726 |
| fixed-128 | 4096 | 0.5908† | 0.1059† | 0.8534 | 0.0774 | 0.8726 |
| fixed-128 | 8192 | 0.5908† | 0.1059† | 0.8669 | 0.0766 | 0.8726 |
| fixed-256 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2197 | 0.1411 | 0.2197 | 0.1411 | 0.0000 |
| fixed-256 | 512 | 0.3704 | 0.1245 | 0.3704 | 0.1245 | 0.0000 |
| fixed-256 | 1024 | 0.5709 | 0.1027 | 0.5709 | 0.1027 | 0.0000 |
| fixed-256 | 2048 | 0.7880 | 0.0828 | 0.7880 | 0.0828 | 0.0000 |
| fixed-256 | 4096 | 0.7880† | 0.0828† | 0.9106 | 0.0695 | 0.7902 |
| fixed-256 | 8192 | 0.7880† | 0.0828† | 0.9324 | 0.0675 | 0.7902 |
| fixed-512 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-512 | 512 | 0.3154 | 0.1110 | 0.3154 | 0.1110 | 0.0000 |
| fixed-512 | 1024 | 0.5227 | 0.0976 | 0.5227 | 0.0976 | 0.0000 |
| fixed-512 | 2048 | 0.7614 | 0.0788 | 0.7614 | 0.0788 | 0.0000 |
| fixed-512 | 4096 | 0.9271 | 0.0643 | 0.9271 | 0.0643 | 0.0000 |
| fixed-512 | 8192 | 0.9271 | 0.0643 | 0.9602 | 0.0611 | 0.4483 |
| fixed-1024 | 128 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4426 | 0.0872 | 0.4426 | 0.0872 | 0.0000 |
| fixed-1024 | 2048 | 0.7002 | 0.0751 | 0.7002 | 0.0751 | 0.0000 |
| fixed-1024 | 4096 | 0.9247 | 0.0625 | 0.9247 | 0.0625 | 0.0000 |
| fixed-1024 | 8192 | 0.9762 | 0.0581 | 0.9762 | 0.0581 | 0.0000 |
| section-aware | 128 | 0.0698 | 0.0798 | 0.0698 | 0.0798 | 0.0000 |
| section-aware | 256 | 0.1506 | 0.1027 | 0.1506 | 0.1027 | 0.0000 |
| section-aware | 512 | 0.3639 | 0.1374 | 0.3639 | 0.1374 | 0.0000 |
| section-aware | 1024 | 0.6015 | 0.1206 | 0.6015 | 0.1205 | 0.0036 |
| section-aware | 2048 | 0.8139 | 0.0954 | 0.8219 | 0.0940 | 0.2044 |
| section-aware | 4096 | 0.8505† | 0.0895† | 0.9203 | 0.0744 | 0.7542 |
| section-aware | 8192 | 0.8505† | 0.0895† | 0.9407 | 0.0717 | 0.7542 |
| small-to-big | 128 | 0.1622 | 0.1993 | 0.1622 | 0.1993 | 0.0000 |
| small-to-big | 256 | 0.2554 | 0.1657 | 0.2554 | 0.1657 | 0.0000 |
| small-to-big | 512 | 0.4177 | 0.1510 | 0.4177 | 0.1510 | 0.0000 |
| small-to-big | 1024 | 0.6246 | 0.1212 | 0.6246 | 0.1212 | 0.0082 |
| small-to-big | 2048 | 0.8162 | 0.0940 | 0.8271 | 0.0924 | 0.3409 |
| small-to-big | 4096 | 0.8454† | 0.0883† | 0.9221 | 0.0744 | 0.7542 |
| small-to-big | 8192 | 0.8454† | 0.0883† | 0.9411 | 0.0717 | 0.7542 |

## Side table: production view, top-N cap 5

| chunking | budget | recall | precision | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.1526 | 0.1763 | 0.0000 |
| fixed-64 | 256 | 0.2569 | 0.1547 | 0.0000 |
| fixed-64 | 512 | 0.2967† | 0.1461† | 0.9481 |
| fixed-64 | 1024 | 0.2967† | 0.1461† | 0.9481 |
| fixed-64 | 2048 | 0.2967† | 0.1461† | 0.9481 |
| fixed-64 | 4096 | 0.2967† | 0.1461† | 0.9481 |
| fixed-64 | 8192 | 0.2967† | 0.1461† | 0.9481 |
| fixed-128 | 128 | 0.1482 | 0.1739 | 0.0000 |
| fixed-128 | 256 | 0.2545 | 0.1562 | 0.0000 |
| fixed-128 | 512 | 0.4053 | 0.1310 | 0.0000 |
| fixed-128 | 1024 | 0.4697† | 0.1244† | 0.9386 |
| fixed-128 | 2048 | 0.4697† | 0.1244† | 0.9386 |
| fixed-128 | 4096 | 0.4697† | 0.1244† | 0.9386 |
| fixed-128 | 8192 | 0.4697† | 0.1244† | 0.9386 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.2197 | 0.1411 | 0.0000 |
| fixed-256 | 512 | 0.3704 | 0.1245 | 0.0000 |
| fixed-256 | 1024 | 0.5709 | 0.1027 | 0.0000 |
| fixed-256 | 2048 | 0.6533† | 0.0976† | 0.9076 |
| fixed-256 | 4096 | 0.6533† | 0.0976† | 0.9076 |
| fixed-256 | 8192 | 0.6533† | 0.0976† | 0.9076 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.3154 | 0.1110 | 0.0000 |
| fixed-512 | 1024 | 0.5227 | 0.0976 | 0.0000 |
| fixed-512 | 2048 | 0.7614 | 0.0788 | 0.0000 |
| fixed-512 | 4096 | 0.8272† | 0.0728† | 0.7815 |
| fixed-512 | 8192 | 0.8272† | 0.0728† | 0.7815 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4426 | 0.0872 | 0.0000 |
| fixed-1024 | 2048 | 0.7002 | 0.0751 | 0.0000 |
| fixed-1024 | 4096 | 0.9247 | 0.0625 | 0.0000 |
| fixed-1024 | 8192 | 0.9584 | 0.0597 | 0.3132 |
| section-aware | 128 | 0.0698 | 0.0798 | 0.0000 |
| section-aware | 256 | 0.1506 | 0.1027 | 0.0000 |
| section-aware | 512 | 0.3638 | 0.1373 | 0.0046 |
| section-aware | 1024 | 0.5947 | 0.1220 | 0.1284 |
| section-aware | 2048 | 0.7196† | 0.1111† | 0.8712 |
| section-aware | 4096 | 0.7208† | 0.1111† | 0.9076 |
| section-aware | 8192 | 0.7208† | 0.1111† | 0.9076 |
| small-to-big | 128 | 0.1622 | 0.1993 | 0.0005 |
| small-to-big | 256 | 0.2554 | 0.1656 | 0.0014 |
| small-to-big | 512 | 0.4175 | 0.1511 | 0.0259 |
| small-to-big | 1024 | 0.6150 | 0.1235 | 0.2981 |
| small-to-big | 2048 | 0.7208† | 0.1086† | 0.8930 |
| small-to-big | 4096 | 0.7215† | 0.1084† | 0.9076 |
| small-to-big | 8192 | 0.7215† | 0.1084† | 0.9076 |

n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`cap binds`: share of questions where the top-N cap stopped packing while a further ranked chunk would still have fit the budget; †: the cap binds for at least half of the questions.
