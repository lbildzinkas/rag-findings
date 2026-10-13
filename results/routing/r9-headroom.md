# R9 - the oracle router's chunking by query type

Config hash: `1ed161605655c1535133d7529febf4a25c2e7cedba03b2ce6f8ff7671ee9edbc`

## Config

```yaml
chunkings:
- fixed-64
- fixed-128
- fixed-256
- fixed-512
- section-aware
- small-to-big
- fixed-1024
gate:
  budget: 1024
  confidence: 0.95
  datasets:
  - qasper
  - nq
  min_headroom: 0.05
  pipeline: hybrid-rerank
interaction_reference: fixed-128
kind: headroom
resamples: 10000
run_name: headroom
runs:
- qasper/grid
scope: collection
seed: 0
top_n: 8
```

## Inputs

| run | run config hash |
|---|---|
| qasper/grid | `b1a07e4a65f57e48f777369cd0a5dbbd26a4152deeeb6a73e148dd813e97aa9f` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `bm25` (embedder -).

## The oracle router's chunking per query type, at 1024 tokens

Each cell: the share of the query type's questions for which the oracle router picks the chunking, and their count. Ties go to the smaller chunk, so a question on which every chunking scores the same goes to the smallest candidate; the last row of each block counts those questions.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 1024 | fixed-64 | 0.7046 (928) | 0.6881 (278) | 0.6765 (322) | 0.6955 (1528) |
| qasper | bm25 | - | production | 1024 | fixed-128 | 0.0850 (112) | 0.0668 (27) | 0.0924 (44) | 0.0833 (183) |
| qasper | bm25 | - | production | 1024 | fixed-256 | 0.0569 (75) | 0.0668 (27) | 0.0651 (31) | 0.0605 (133) |
| qasper | bm25 | - | production | 1024 | fixed-512 | 0.0486 (64) | 0.0520 (21) | 0.0588 (28) | 0.0514 (113) |
| qasper | bm25 | - | production | 1024 | section-aware | 0.0547 (72) | 0.0594 (24) | 0.0546 (26) | 0.0555 (122) |
| qasper | bm25 | - | production | 1024 | small-to-big | 0.0258 (34) | 0.0248 (10) | 0.0252 (12) | 0.0255 (56) |
| qasper | bm25 | - | production | 1024 | fixed-1024 | 0.0243 (32) | 0.0421 (17) | 0.0273 (13) | 0.0282 (62) |
| qasper | bm25 | - | production | 1024 | every chunking tied | 0.6872 (905) | 0.6510 (263) | 0.6429 (306) | 0.6709 (1474) |
| qasper | bm25 | - | fair | 1024 | fixed-64 | 0.7175 (945) | 0.6955 (281) | 0.6954 (331) | 0.7087 (1557) |
| qasper | bm25 | - | fair | 1024 | fixed-128 | 0.0774 (102) | 0.0644 (26) | 0.0819 (39) | 0.0760 (167) |
| qasper | bm25 | - | fair | 1024 | fixed-256 | 0.0532 (70) | 0.0619 (25) | 0.0609 (29) | 0.0564 (124) |
| qasper | bm25 | - | fair | 1024 | fixed-512 | 0.0478 (63) | 0.0520 (21) | 0.0588 (28) | 0.0510 (112) |
| qasper | bm25 | - | fair | 1024 | section-aware | 0.0547 (72) | 0.0594 (24) | 0.0546 (26) | 0.0555 (122) |
| qasper | bm25 | - | fair | 1024 | small-to-big | 0.0258 (34) | 0.0248 (10) | 0.0231 (11) | 0.0250 (55) |
| qasper | bm25 | - | fair | 1024 | fixed-1024 | 0.0235 (31) | 0.0421 (17) | 0.0252 (12) | 0.0273 (60) |
| qasper | bm25 | - | fair | 1024 | every chunking tied | 0.6651 (876) | 0.6312 (255) | 0.6218 (296) | 0.6495 (1427) |

## The same, among the questions where the chunkings differ

Leaves out the questions on which every chunking scores the same, so the tie-break does not decide the picks.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 1024 | fixed-64 | 0.0558 (23) | 0.1064 (15) | 0.0941 (16) | 0.0747 (54) |
| qasper | bm25 | - | production | 1024 | fixed-128 | 0.2718 (112) | 0.1915 (27) | 0.2588 (44) | 0.2531 (183) |
| qasper | bm25 | - | production | 1024 | fixed-256 | 0.1820 (75) | 0.1915 (27) | 0.1824 (31) | 0.1840 (133) |
| qasper | bm25 | - | production | 1024 | fixed-512 | 0.1553 (64) | 0.1489 (21) | 0.1647 (28) | 0.1563 (113) |
| qasper | bm25 | - | production | 1024 | section-aware | 0.1748 (72) | 0.1702 (24) | 0.1529 (26) | 0.1687 (122) |
| qasper | bm25 | - | production | 1024 | small-to-big | 0.0825 (34) | 0.0709 (10) | 0.0706 (12) | 0.0775 (56) |
| qasper | bm25 | - | production | 1024 | fixed-1024 | 0.0777 (32) | 0.1206 (17) | 0.0765 (13) | 0.0858 (62) |
| qasper | bm25 | - | fair | 1024 | fixed-64 | 0.1565 (69) | 0.1745 (26) | 0.1944 (35) | 0.1688 (130) |
| qasper | bm25 | - | fair | 1024 | fixed-128 | 0.2313 (102) | 0.1745 (26) | 0.2167 (39) | 0.2169 (167) |
| qasper | bm25 | - | fair | 1024 | fixed-256 | 0.1587 (70) | 0.1678 (25) | 0.1611 (29) | 0.1610 (124) |
| qasper | bm25 | - | fair | 1024 | fixed-512 | 0.1429 (63) | 0.1409 (21) | 0.1556 (28) | 0.1455 (112) |
| qasper | bm25 | - | fair | 1024 | section-aware | 0.1633 (72) | 0.1611 (24) | 0.1444 (26) | 0.1584 (122) |
| qasper | bm25 | - | fair | 1024 | small-to-big | 0.0771 (34) | 0.0671 (10) | 0.0611 (11) | 0.0714 (55) |
| qasper | bm25 | - | fair | 1024 | fixed-1024 | 0.0703 (31) | 0.1141 (17) | 0.0667 (12) | 0.0779 (60) |
