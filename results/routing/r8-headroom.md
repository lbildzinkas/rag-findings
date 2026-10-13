# R8 - chunk size x query type interaction

Config hash: `bb042947b42466d59622bb462f1d501a3cbffe130b01f8c78d29c7a7335ba80d`

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
- grid
scope: collection
seed: 0
top_n: 8
```

## Inputs

| run | run config hash |
|---|---|
| grid | `b1a07e4a65f57e48f777369cd0a5dbbd26a4152deeeb6a73e148dd813e97aa9f` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `bm25` (embedder -).

## Chunk size x query type interaction against fixed-128

For each chunking: Δ context = mean recall (chunking − fixed-128) on context questions, Δ precise = the same on precise questions, and interaction = Δ context − Δ precise. A positive interaction means the chunking does relatively better than fixed-128 on context questions than on precise ones. Mixed questions are left out.

| dataset | pipeline | embedder | view | budget | chunking | precise n | context n | Δ context | Δ precise | interaction | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 128 | fixed-64 | 1317 | 404 | +0.0038 | -0.0070 | +0.0108 | [-0.0041, +0.0255] | 99.17% | no |
| qasper | bm25 | - | production | 128 | section-aware | 1317 | 404 | -0.0079 | -0.0291 | +0.0211 | [-0.0002, +0.0428] | 99.17% | no |
| qasper | bm25 | - | production | 128 | small-to-big | 1317 | 404 | +0.0102 | -0.0001 | +0.0103 | [-0.0081, +0.0297] | 99.17% | no |
| qasper | bm25 | - | production | 256 | fixed-64 | 1317 | 404 | +0.0083 | -0.0085 | +0.0169 | [-0.0027, +0.0368] | 99.17% | no |
| qasper | bm25 | - | production | 256 | fixed-256 | 1317 | 404 | +0.0050 | -0.0120 | +0.0170 | [-0.0044, +0.0385] | 99.00% | no |
| qasper | bm25 | - | production | 256 | section-aware | 1317 | 404 | -0.0123 | -0.0311 | +0.0188 | [-0.0049, +0.0426] | 99.17% | no |
| qasper | bm25 | - | production | 256 | small-to-big | 1317 | 404 | +0.0031 | -0.0077 | +0.0109 | [-0.0083, +0.0302] | 99.17% | no |
| qasper | bm25 | - | production | 512 | fixed-64 | 1317 | 404 | -0.0026 | -0.0208 | +0.0182 | [-0.0055, +0.0437] | 99.17% | no |
| qasper | bm25 | - | production | 512 | fixed-256 | 1317 | 404 | -0.0051 | -0.0153 | +0.0102 | [-0.0160, +0.0352] | 99.00% | no |
| qasper | bm25 | - | production | 512 | fixed-512 | 1317 | 404 | -0.0131 | -0.0208 | +0.0077 | [-0.0239, +0.0393] | 98.75% | no |
| qasper | bm25 | - | production | 512 | section-aware | 1317 | 404 | -0.0015 | -0.0211 | +0.0196 | [-0.0133, +0.0529] | 99.17% | no |
| qasper | bm25 | - | production | 512 | small-to-big | 1317 | 404 | -0.0037 | +0.0000 | -0.0037 | [-0.0332, +0.0255] | 99.17% | no |
| qasper | bm25 | - | production | 1024 | fixed-64 | 1317 | 404 | -0.0475 | -0.0704 | +0.0229 | [+0.0029, +0.0428] | 95.00% | yes |
| qasper | bm25 | - | production | 1024 | fixed-256 | 1317 | 404 | -0.0073 | -0.0122 | +0.0049 | [-0.0175, +0.0273] | 95.00% | no |
| qasper | bm25 | - | production | 1024 | fixed-512 | 1317 | 404 | -0.0113 | -0.0189 | +0.0076 | [-0.0216, +0.0359] | 95.00% | no |
| qasper | bm25 | - | production | 1024 | section-aware | 1317 | 404 | +0.0189 | -0.0015 | +0.0204 | [-0.0047, +0.0457] | 95.00% | no |
| qasper | bm25 | - | production | 1024 | small-to-big | 1317 | 404 | +0.0019 | +0.0031 | -0.0012 | [-0.0258, +0.0233] | 95.00% | no |
| qasper | bm25 | - | production | 1024 | fixed-1024 | 1317 | 404 | -0.0187 | -0.0284 | +0.0097 | [-0.0214, +0.0404] | 95.00% | no |
| qasper | bm25 | - | production | 2048 | fixed-64 | 1317 | 404 | -0.0475 | -0.0704 | +0.0229 | [-0.0038, +0.0492] | 99.17% | no |
| qasper | bm25 | - | production | 2048 | fixed-256 | 1317 | 404 | +0.0563 | +0.0532 | +0.0031 | [-0.0252, +0.0334] | 99.00% | no |
| qasper | bm25 | - | production | 2048 | fixed-512 | 1317 | 404 | +0.0450 | +0.0443 | +0.0006 | [-0.0369, +0.0388] | 98.75% | no |
| qasper | bm25 | - | production | 2048 | section-aware | 1317 | 404 | +0.0696 | +0.0638 | +0.0059 | [-0.0299, +0.0438] | 99.17% | no |
| qasper | bm25 | - | production | 2048 | small-to-big | 1317 | 404 | +0.0508 | +0.0782 | -0.0274 | [-0.0616, +0.0070] | 99.17% | no |
| qasper | bm25 | - | production | 2048 | fixed-1024 | 1317 | 404 | +0.0487 | +0.0351 | +0.0136 | [-0.0268, +0.0534] | 98.33% | no |
| qasper | bm25 | - | production | 4096 | fixed-64 | 1317 | 404 | -0.0475 | -0.0704 | +0.0229 | [-0.0038, +0.0492] | 99.17% | no |
| qasper | bm25 | - | production | 4096 | fixed-256 | 1317 | 404 | +0.0563 | +0.0532 | +0.0031 | [-0.0252, +0.0334] | 99.00% | no |
| qasper | bm25 | - | production | 4096 | fixed-512 | 1317 | 404 | +0.1158 | +0.1075 | +0.0083 | [-0.0304, +0.0479] | 98.75% | no |
| qasper | bm25 | - | production | 4096 | section-aware | 1317 | 404 | +0.0788 | +0.0843 | -0.0055 | [-0.0403, +0.0316] | 99.17% | no |
| qasper | bm25 | - | production | 4096 | small-to-big | 1317 | 404 | +0.0653 | +0.0956 | -0.0304 | [-0.0646, +0.0054] | 99.17% | no |
| qasper | bm25 | - | production | 4096 | fixed-1024 | 1317 | 404 | +0.1234 | +0.1035 | +0.0199 | [-0.0238, +0.0631] | 98.33% | no |
| qasper | bm25 | - | production | 8192 | fixed-64 | 1317 | 404 | -0.0475 | -0.0704 | +0.0229 | [-0.0038, +0.0492] | 99.17% | no |
| qasper | bm25 | - | production | 8192 | fixed-256 | 1317 | 404 | +0.0563 | +0.0532 | +0.0031 | [-0.0252, +0.0334] | 99.00% | no |
| qasper | bm25 | - | production | 8192 | fixed-512 | 1317 | 404 | +0.1158 | +0.1075 | +0.0083 | [-0.0304, +0.0479] | 98.75% | no |
| qasper | bm25 | - | production | 8192 | section-aware | 1317 | 404 | +0.0788 | +0.0843 | -0.0055 | [-0.0403, +0.0316] | 99.17% | no |
| qasper | bm25 | - | production | 8192 | small-to-big | 1317 | 404 | +0.0653 | +0.0956 | -0.0304 | [-0.0646, +0.0054] | 99.17% | no |
| qasper | bm25 | - | production | 8192 | fixed-1024 | 1317 | 404 | +0.1788 | +0.1533 | +0.0255 | [-0.0222, +0.0739] | 98.33% | no |
| qasper | bm25 | - | fair | 128 | fixed-64 | 1317 | 404 | +0.0038 | -0.0070 | +0.0108 | [-0.0041, +0.0255] | 99.17% | no |
| qasper | bm25 | - | fair | 128 | section-aware | 1317 | 404 | -0.0079 | -0.0291 | +0.0211 | [-0.0002, +0.0428] | 99.17% | no |
| qasper | bm25 | - | fair | 128 | small-to-big | 1317 | 404 | +0.0102 | -0.0001 | +0.0103 | [-0.0081, +0.0297] | 99.17% | no |
| qasper | bm25 | - | fair | 256 | fixed-64 | 1317 | 404 | +0.0083 | -0.0085 | +0.0169 | [-0.0027, +0.0368] | 99.17% | no |
| qasper | bm25 | - | fair | 256 | fixed-256 | 1317 | 404 | +0.0050 | -0.0120 | +0.0170 | [-0.0044, +0.0385] | 99.00% | no |
| qasper | bm25 | - | fair | 256 | section-aware | 1317 | 404 | -0.0123 | -0.0311 | +0.0188 | [-0.0049, +0.0426] | 99.17% | no |
| qasper | bm25 | - | fair | 256 | small-to-big | 1317 | 404 | +0.0031 | -0.0077 | +0.0109 | [-0.0083, +0.0302] | 99.17% | no |
| qasper | bm25 | - | fair | 512 | fixed-64 | 1317 | 404 | -0.0026 | -0.0208 | +0.0182 | [-0.0055, +0.0437] | 99.17% | no |
| qasper | bm25 | - | fair | 512 | fixed-256 | 1317 | 404 | -0.0051 | -0.0153 | +0.0102 | [-0.0160, +0.0352] | 99.00% | no |
| qasper | bm25 | - | fair | 512 | fixed-512 | 1317 | 404 | -0.0131 | -0.0208 | +0.0077 | [-0.0239, +0.0393] | 98.75% | no |
| qasper | bm25 | - | fair | 512 | section-aware | 1317 | 404 | -0.0015 | -0.0211 | +0.0196 | [-0.0133, +0.0529] | 99.17% | no |
| qasper | bm25 | - | fair | 512 | small-to-big | 1317 | 404 | -0.0037 | +0.0000 | -0.0037 | [-0.0332, +0.0255] | 99.17% | no |
| qasper | bm25 | - | fair | 1024 | fixed-64 | 1317 | 404 | -0.0211 | -0.0343 | +0.0132 | [-0.0058, +0.0321] | 95.00% | no |
| qasper | bm25 | - | fair | 1024 | fixed-256 | 1317 | 404 | -0.0074 | -0.0122 | +0.0049 | [-0.0175, +0.0273] | 95.00% | no |
| qasper | bm25 | - | fair | 1024 | fixed-512 | 1317 | 404 | -0.0114 | -0.0189 | +0.0075 | [-0.0217, +0.0358] | 95.00% | no |
| qasper | bm25 | - | fair | 1024 | section-aware | 1317 | 404 | +0.0188 | -0.0015 | +0.0204 | [-0.0048, +0.0456] | 95.00% | no |
| qasper | bm25 | - | fair | 1024 | small-to-big | 1317 | 404 | +0.0018 | +0.0031 | -0.0013 | [-0.0259, +0.0233] | 95.00% | no |
| qasper | bm25 | - | fair | 1024 | fixed-1024 | 1317 | 404 | -0.0188 | -0.0284 | +0.0096 | [-0.0215, +0.0404] | 95.00% | no |
| qasper | bm25 | - | fair | 2048 | fixed-64 | 1317 | 404 | -0.0341 | -0.0452 | +0.0112 | [-0.0160, +0.0375] | 99.17% | no |
| qasper | bm25 | - | fair | 2048 | fixed-256 | 1317 | 404 | +0.0160 | +0.0032 | +0.0128 | [-0.0151, +0.0420] | 99.00% | no |
| qasper | bm25 | - | fair | 2048 | fixed-512 | 1317 | 404 | +0.0047 | -0.0057 | +0.0104 | [-0.0280, +0.0475] | 98.75% | no |
| qasper | bm25 | - | fair | 2048 | section-aware | 1317 | 404 | +0.0370 | +0.0198 | +0.0172 | [-0.0196, +0.0547] | 99.17% | no |
| qasper | bm25 | - | fair | 2048 | small-to-big | 1317 | 404 | +0.0137 | +0.0315 | -0.0178 | [-0.0520, +0.0174] | 99.17% | no |
| qasper | bm25 | - | fair | 2048 | fixed-1024 | 1317 | 404 | +0.0084 | -0.0150 | +0.0234 | [-0.0175, +0.0646] | 98.33% | no |
| qasper | bm25 | - | fair | 4096 | fixed-64 | 1317 | 404 | -0.0407 | -0.0384 | -0.0024 | [-0.0286, +0.0239] | 99.17% | no |
| qasper | bm25 | - | fair | 4096 | fixed-256 | 1317 | 404 | +0.0221 | +0.0172 | +0.0049 | [-0.0259, +0.0373] | 99.00% | no |
| qasper | bm25 | - | fair | 4096 | fixed-512 | 1317 | 404 | +0.0366 | +0.0212 | +0.0153 | [-0.0222, +0.0533] | 98.75% | no |
| qasper | bm25 | - | fair | 4096 | section-aware | 1317 | 404 | +0.0453 | +0.0450 | +0.0003 | [-0.0383, +0.0405] | 99.17% | no |
| qasper | bm25 | - | fair | 4096 | small-to-big | 1317 | 404 | +0.0325 | +0.0459 | -0.0134 | [-0.0471, +0.0205] | 99.17% | no |
| qasper | bm25 | - | fair | 4096 | fixed-1024 | 1317 | 404 | +0.0442 | +0.0157 | +0.0285 | [-0.0151, +0.0740] | 98.33% | no |
| qasper | bm25 | - | fair | 8192 | fixed-64 | 1317 | 404 | -0.0460 | -0.0365 | -0.0094 | [-0.0354, +0.0153] | 99.17% | no |
| qasper | bm25 | - | fair | 8192 | fixed-256 | 1317 | 404 | +0.0322 | +0.0263 | +0.0058 | [-0.0255, +0.0382] | 99.00% | no |
| qasper | bm25 | - | fair | 8192 | fixed-512 | 1317 | 404 | +0.0460 | +0.0364 | +0.0096 | [-0.0264, +0.0489] | 98.75% | no |
| qasper | bm25 | - | fair | 8192 | section-aware | 1317 | 404 | +0.0531 | +0.0483 | +0.0047 | [-0.0373, +0.0470] | 99.17% | no |
| qasper | bm25 | - | fair | 8192 | small-to-big | 1317 | 404 | +0.0374 | +0.0510 | -0.0136 | [-0.0519, +0.0267] | 99.17% | no |
| qasper | bm25 | - | fair | 8192 | fixed-1024 | 1317 | 404 | +0.0594 | +0.0166 | +0.0428 | [-0.0017, +0.0883] | 98.33% | no |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).
Budgets where fixed-128 is not scored (its chunk is bigger than the budget) have no interaction rows.
