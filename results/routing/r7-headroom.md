# R7 - routing headroom and the router gate

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

## Router gate (pre-registered)

Rule: build the router in v2 if, on the production line, in the production view, at the primary budget of 1024 tokens, pooled over qasper + nq, either embedder's routing headroom is at least +0.0500 retrieval recall with a 95% CI that excludes 0.

**Gate not judged:** these results hold no production-line pipeline (`hybrid-rerank`) at 1024 tokens in the production view; pipelines present: `bm25`. The verdict comes from the re-run on the full results.

### The same test on the other pipelines (for reference, not the gate)

| pipeline | embedder | best single chunking | routing headroom | 95% CI | meets the bar |
|---|---|---|---|---|---|
| bm25 | - | section-aware | +0.1132 | [+0.1001, +0.1230] | yes |

## Routing headroom

Best single chunking: highest mean retrieval recall at the budget. Oracle router: per question, the chunking with the highest recall (ties to the smaller chunk). Routing headroom: oracle router minus best single chunking; the best single chunking is re-selected inside every resample.

| dataset | pipeline | embedder | view | budget | best single chunking | best single recall | oracle router recall | routing headroom | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 128 | small-to-big | 0.0411 | 0.0773 | +0.0362 | [+0.0278, +0.0439] | 99.17% | yes |
| qasper | bm25 | - | production | 256 | fixed-128 | 0.0645 | 0.1308 | +0.0664 | [+0.0553, +0.0772] | 99.00% | yes |
| qasper | bm25 | - | production | 512 | fixed-128 | 0.1060 | 0.2067 | +0.1007 | [+0.0862, +0.1131] | 98.75% | yes |
| qasper | bm25 | - | production | 1024 | section-aware | 0.1601 | 0.2733 | +0.1132 | [+0.1001, +0.1230] | 95.00% | yes |
| qasper | bm25 | - | production | 2048 | small-to-big | 0.2247 | 0.3229 | +0.0982 | [+0.0833, +0.1099] | 98.33% | yes |
| qasper | bm25 | - | production | 4096 | fixed-512 | 0.2691 | 0.3528 | +0.0837 | [+0.0718, +0.0945] | 97.50% | yes |
| qasper | bm25 | - | production | 8192 | fixed-1024 | 0.3162 | 0.3693 | +0.0531 | [+0.0445, +0.0620] | 95.00% | yes |
| qasper | bm25 | - | fair | 128 | small-to-big | 0.0411 | 0.0773 | +0.0362 | [+0.0278, +0.0439] | 99.17% | yes |
| qasper | bm25 | - | fair | 256 | fixed-128 | 0.0645 | 0.1308 | +0.0664 | [+0.0553, +0.0772] | 99.00% | yes |
| qasper | bm25 | - | fair | 512 | fixed-128 | 0.1060 | 0.2067 | +0.1007 | [+0.0862, +0.1131] | 98.75% | yes |
| qasper | bm25 | - | fair | 1024 | section-aware | 0.1601 | 0.2826 | +0.1225 | [+0.1091, +0.1327] | 95.00% | yes |
| qasper | bm25 | - | fair | 2048 | section-aware | 0.2297 | 0.3453 | +0.1155 | [+0.1002, +0.1279] | 98.33% | yes |
| qasper | bm25 | - | fair | 4096 | section-aware | 0.2862 | 0.4065 | +0.1203 | [+0.1059, +0.1321] | 97.50% | yes |
| qasper | bm25 | - | fair | 8192 | section-aware | 0.3445 | 0.4745 | +0.1300 | [+0.1169, +0.1419] | 95.00% | yes |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Query-type oracle (secondary; does not change the gate)

The best chunking per labelled query type, applied to every question of that type. Query types come from the labels in hindsight, so no real router has them.

| dataset | pipeline | embedder | view | budget | precise pick | context pick | mixed pick | query-type oracle recall | gain over best single | CI | CI level | oracle router minus query-type oracle | CI | CI level |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 128 | fixed-128 | small-to-big | small-to-big | 0.0412 | +0.0001 | [+0.0000, +0.0052] | 99.17% | +0.0361 | [+0.0269, +0.0425] | 99.17% |
| qasper | bm25 | - | production | 256 | fixed-128 | fixed-64 | small-to-big | 0.0669 | +0.0024 | [+0.0000, +0.0071] | 99.17% | +0.0639 | [+0.0525, +0.0744] | 99.00% |
| qasper | bm25 | - | production | 512 | small-to-big | fixed-128 | fixed-128 | 0.1060 | +0.0000 | [+0.0000, +0.0091] | 99.17% | +0.1007 | [+0.0843, +0.1102] | 98.75% |
| qasper | bm25 | - | production | 1024 | small-to-big | section-aware | section-aware | 0.1629 | +0.0028 | [+0.0000, +0.0092] | 95.00% | +0.1104 | [+0.0965, +0.1193] | 95.00% |
| qasper | bm25 | - | production | 2048 | small-to-big | section-aware | section-aware | 0.2318 | +0.0070 | [+0.0000, +0.0142] | 99.17% | +0.0911 | [+0.0772, +0.1037] | 98.33% |
| qasper | bm25 | - | production | 4096 | fixed-512 | fixed-1024 | fixed-512 | 0.2705 | +0.0014 | [+0.0000, +0.0087] | 99.17% | +0.0823 | [+0.0699, +0.0921] | 97.50% |
| qasper | bm25 | - | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.3162 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0531 | [+0.0445, +0.0620] | 95.00% |
| qasper | bm25 | - | fair | 128 | fixed-128 | small-to-big | small-to-big | 0.0412 | +0.0001 | [+0.0000, +0.0052] | 99.17% | +0.0361 | [+0.0269, +0.0425] | 99.17% |
| qasper | bm25 | - | fair | 256 | fixed-128 | fixed-64 | small-to-big | 0.0669 | +0.0024 | [+0.0000, +0.0071] | 99.17% | +0.0639 | [+0.0525, +0.0744] | 99.00% |
| qasper | bm25 | - | fair | 512 | small-to-big | fixed-128 | fixed-128 | 0.1060 | +0.0000 | [+0.0000, +0.0091] | 99.17% | +0.1007 | [+0.0843, +0.1102] | 98.75% |
| qasper | bm25 | - | fair | 1024 | small-to-big | section-aware | section-aware | 0.1629 | +0.0028 | [+0.0000, +0.0092] | 95.00% | +0.1197 | [+0.1056, +0.1290] | 95.00% |
| qasper | bm25 | - | fair | 2048 | small-to-big | section-aware | section-aware | 0.2367 | +0.0070 | [+0.0000, +0.0142] | 99.17% | +0.1085 | [+0.0946, +0.1220] | 98.33% |
| qasper | bm25 | - | fair | 4096 | small-to-big | section-aware | section-aware | 0.2868 | +0.0006 | [+0.0000, +0.0105] | 99.17% | +0.1197 | [+0.1034, +0.1282] | 97.50% |
| qasper | bm25 | - | fair | 8192 | small-to-big | fixed-1024 | section-aware | 0.3473 | +0.0028 | [+0.0000, +0.0138] | 99.17% | +0.1272 | [+0.1131, +0.1372] | 95.00% |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Each chunking against the best single chunking

Difference: the chunking's mean recall minus the best single chunking's, with the best re-selected inside every resample (so the best chunking's own difference is 0 with a CI at or below 0). Best in resamples: the share of resamples in which the chunking was the best single chunking.

| dataset | pipeline | embedder | view | budget | chunking | mean recall | difference from best | CI | CI level | CI excludes 0 | best in resamples |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | bm25 | - | production | 128 | fixed-64 | 0.0351 | -0.0060 | [-0.0132, -0.0005] | 97.50% | yes | 0.0086 |
| qasper | bm25 | - | production | 128 | fixed-128 | 0.0388 | -0.0023 | [-0.0107, +0.0000] | 98.33% | no | 0.2506 |
| qasper | bm25 | - | production | 128 | section-aware | 0.0167 | -0.0245 | [-0.0347, -0.0158] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | production | 128 | small-to-big | 0.0411 | +0.0000 | [-0.0066, +0.0000] | 98.75% | no | 0.7408 |
| qasper | bm25 | - | production | 256 | fixed-64 | 0.0610 | -0.0035 | [-0.0106, +0.0000] | 95.00% | no | 0.1190 |
| qasper | bm25 | - | production | 256 | fixed-128 | 0.0645 | +0.0000 | [-0.0061, +0.0000] | 98.33% | no | 0.7082 |
| qasper | bm25 | - | production | 256 | fixed-256 | 0.0552 | -0.0092 | [-0.0182, -0.0016] | 98.33% | yes | 0.0019 |
| qasper | bm25 | - | production | 256 | section-aware | 0.0389 | -0.0256 | [-0.0388, -0.0149] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 256 | small-to-big | 0.0613 | -0.0032 | [-0.0129, +0.0000] | 98.75% | no | 0.1709 |
| qasper | bm25 | - | production | 512 | fixed-64 | 0.0910 | -0.0150 | [-0.0265, -0.0056] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | production | 512 | fixed-128 | 0.1060 | +0.0000 | [-0.0089, +0.0000] | 98.33% | no | 0.6968 |
| qasper | bm25 | - | production | 512 | fixed-256 | 0.0934 | -0.0126 | [-0.0233, -0.0035] | 97.50% | yes | 0.0021 |
| qasper | bm25 | - | production | 512 | fixed-512 | 0.0862 | -0.0198 | [-0.0345, -0.0074] | 98.33% | yes | 0.0001 |
| qasper | bm25 | - | production | 512 | section-aware | 0.0922 | -0.0138 | [-0.0266, -0.0028] | 97.50% | yes | 0.0028 |
| qasper | bm25 | - | production | 512 | small-to-big | 0.1034 | -0.0026 | [-0.0144, +0.0000] | 98.75% | no | 0.2982 |
| qasper | bm25 | - | production | 1024 | fixed-64 | 0.0910 | -0.0692 | [-0.0823, -0.0602] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 1024 | fixed-128 | 0.1560 | -0.0041 | [-0.0157, +0.0000] | 95.00% | no | 0.1599 |
| qasper | bm25 | - | production | 1024 | fixed-256 | 0.1476 | -0.0125 | [-0.0246, -0.0040] | 95.00% | yes | 0.0030 |
| qasper | bm25 | - | production | 1024 | fixed-512 | 0.1384 | -0.0217 | [-0.0350, -0.0120] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 1024 | section-aware | 0.1601 | +0.0000 | [-0.0091, +0.0000] | 95.00% | no | 0.6159 |
| qasper | bm25 | - | production | 1024 | small-to-big | 0.1568 | -0.0033 | [-0.0149, +0.0000] | 95.00% | no | 0.2212 |
| qasper | bm25 | - | production | 1024 | fixed-1024 | 0.1286 | -0.0315 | [-0.0469, -0.0192] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 2048 | fixed-64 | 0.0910 | -0.1338 | [-0.1544, -0.1172] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 2048 | fixed-128 | 0.1560 | -0.0688 | [-0.0858, -0.0554] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | production | 2048 | fixed-256 | 0.2120 | -0.0128 | [-0.0246, -0.0045] | 95.00% | yes | 0.0021 |
| qasper | bm25 | - | production | 2048 | fixed-512 | 0.2053 | -0.0194 | [-0.0340, -0.0079] | 97.50% | yes | 0.0001 |
| qasper | bm25 | - | production | 2048 | section-aware | 0.2231 | -0.0017 | [-0.0125, +0.0000] | 95.00% | no | 0.3853 |
| qasper | bm25 | - | production | 2048 | small-to-big | 0.2247 | +0.0000 | [-0.0120, +0.0000] | 98.75% | no | 0.6125 |
| qasper | bm25 | - | production | 2048 | fixed-1024 | 0.1955 | -0.0292 | [-0.0475, -0.0140] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | fixed-64 | 0.0910 | -0.1781 | [-0.1980, -0.1586] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | fixed-128 | 0.1560 | -0.1131 | [-0.1312, -0.0960] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | fixed-256 | 0.2120 | -0.0571 | [-0.0720, -0.0437] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | fixed-512 | 0.2691 | +0.0000 | [-0.0051, +0.0000] | 95.00% | no | 0.8381 |
| qasper | bm25 | - | production | 4096 | section-aware | 0.2396 | -0.0295 | [-0.0453, -0.0143] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | small-to-big | 0.2406 | -0.0285 | [-0.0452, -0.0127] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | production | 4096 | fixed-1024 | 0.2640 | -0.0051 | [-0.0167, +0.0000] | 97.50% | no | 0.1619 |
| qasper | bm25 | - | production | 8192 | fixed-64 | 0.0910 | -0.2253 | [-0.2472, -0.2037] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | fixed-128 | 0.1560 | -0.1602 | [-0.1811, -0.1397] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | fixed-256 | 0.2120 | -0.1042 | [-0.1229, -0.0868] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | fixed-512 | 0.2691 | -0.0471 | [-0.0609, -0.0344] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | section-aware | 0.2396 | -0.0766 | [-0.0945, -0.0589] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | small-to-big | 0.2406 | -0.0756 | [-0.0951, -0.0571] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | production | 8192 | fixed-1024 | 0.3162 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| qasper | bm25 | - | fair | 128 | fixed-64 | 0.0351 | -0.0060 | [-0.0132, -0.0005] | 97.50% | yes | 0.0086 |
| qasper | bm25 | - | fair | 128 | fixed-128 | 0.0388 | -0.0023 | [-0.0107, +0.0000] | 98.33% | no | 0.2506 |
| qasper | bm25 | - | fair | 128 | section-aware | 0.0167 | -0.0245 | [-0.0347, -0.0158] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | fair | 128 | small-to-big | 0.0411 | +0.0000 | [-0.0073, +0.0000] | 99.17% | no | 0.7408 |
| qasper | bm25 | - | fair | 256 | fixed-64 | 0.0610 | -0.0035 | [-0.0106, +0.0000] | 95.00% | no | 0.1190 |
| qasper | bm25 | - | fair | 256 | fixed-128 | 0.0645 | +0.0000 | [-0.0061, +0.0000] | 98.33% | no | 0.7082 |
| qasper | bm25 | - | fair | 256 | fixed-256 | 0.0552 | -0.0092 | [-0.0177, -0.0022] | 97.50% | yes | 0.0019 |
| qasper | bm25 | - | fair | 256 | section-aware | 0.0389 | -0.0256 | [-0.0388, -0.0149] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 256 | small-to-big | 0.0613 | -0.0032 | [-0.0134, +0.0000] | 99.17% | no | 0.1709 |
| qasper | bm25 | - | fair | 512 | fixed-64 | 0.0910 | -0.0150 | [-0.0265, -0.0056] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | fair | 512 | fixed-128 | 0.1060 | +0.0000 | [-0.0089, +0.0000] | 98.33% | no | 0.6968 |
| qasper | bm25 | - | fair | 512 | fixed-256 | 0.0934 | -0.0126 | [-0.0220, -0.0048] | 95.00% | yes | 0.0021 |
| qasper | bm25 | - | fair | 512 | fixed-512 | 0.0862 | -0.0198 | [-0.0345, -0.0074] | 98.33% | yes | 0.0001 |
| qasper | bm25 | - | fair | 512 | section-aware | 0.0922 | -0.0138 | [-0.0282, -0.0014] | 98.75% | yes | 0.0028 |
| qasper | bm25 | - | fair | 512 | small-to-big | 0.1034 | -0.0026 | [-0.0151, +0.0000] | 99.17% | no | 0.2982 |
| qasper | bm25 | - | fair | 1024 | fixed-64 | 0.1265 | -0.0337 | [-0.0464, -0.0249] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 1024 | fixed-128 | 0.1560 | -0.0041 | [-0.0157, +0.0000] | 95.00% | no | 0.1605 |
| qasper | bm25 | - | fair | 1024 | fixed-256 | 0.1476 | -0.0125 | [-0.0246, -0.0040] | 95.00% | yes | 0.0030 |
| qasper | bm25 | - | fair | 1024 | fixed-512 | 0.1384 | -0.0217 | [-0.0350, -0.0120] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 1024 | section-aware | 0.1601 | +0.0000 | [-0.0091, +0.0000] | 95.00% | no | 0.6156 |
| qasper | bm25 | - | fair | 1024 | small-to-big | 0.1568 | -0.0033 | [-0.0150, +0.0000] | 95.00% | no | 0.2209 |
| qasper | bm25 | - | fair | 1024 | fixed-1024 | 0.1286 | -0.0315 | [-0.0469, -0.0192] | 95.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 2048 | fixed-64 | 0.1649 | -0.0648 | [-0.0823, -0.0509] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 2048 | fixed-128 | 0.2040 | -0.0257 | [-0.0419, -0.0139] | 99.17% | yes | 0.0000 |
| qasper | bm25 | - | fair | 2048 | fixed-256 | 0.2120 | -0.0178 | [-0.0328, -0.0065] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 2048 | fixed-512 | 0.2053 | -0.0244 | [-0.0406, -0.0111] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | fair | 2048 | section-aware | 0.2297 | +0.0000 | [-0.0119, +0.0000] | 98.33% | no | 0.6306 |
| qasper | bm25 | - | fair | 2048 | small-to-big | 0.2279 | -0.0019 | [-0.0171, +0.0000] | 99.17% | no | 0.3694 |
| qasper | bm25 | - | fair | 2048 | fixed-1024 | 0.1955 | -0.0342 | [-0.0534, -0.0186] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | fair | 4096 | fixed-64 | 0.2072 | -0.0790 | [-0.0970, -0.0635] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | fair | 4096 | fixed-128 | 0.2449 | -0.0414 | [-0.0575, -0.0282] | 99.00% | yes | 0.0000 |
| qasper | bm25 | - | fair | 4096 | fixed-256 | 0.2620 | -0.0242 | [-0.0388, -0.0120] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | fair | 4096 | fixed-512 | 0.2700 | -0.0162 | [-0.0294, -0.0054] | 95.00% | yes | 0.0023 |
| qasper | bm25 | - | fair | 4096 | section-aware | 0.2862 | +0.0000 | [-0.0102, +0.0000] | 98.33% | no | 0.6567 |
| qasper | bm25 | - | fair | 4096 | small-to-big | 0.2842 | -0.0020 | [-0.0154, +0.0000] | 99.17% | no | 0.3404 |
| qasper | bm25 | - | fair | 4096 | fixed-1024 | 0.2640 | -0.0222 | [-0.0381, -0.0092] | 95.00% | yes | 0.0006 |
| qasper | bm25 | - | fair | 8192 | fixed-64 | 0.2555 | -0.0891 | [-0.1058, -0.0731] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | fair | 8192 | fixed-128 | 0.2950 | -0.0495 | [-0.0651, -0.0352] | 98.75% | yes | 0.0000 |
| qasper | bm25 | - | fair | 8192 | fixed-256 | 0.3202 | -0.0244 | [-0.0379, -0.0125] | 98.33% | yes | 0.0000 |
| qasper | bm25 | - | fair | 8192 | fixed-512 | 0.3260 | -0.0186 | [-0.0331, -0.0053] | 97.50% | yes | 0.0014 |
| qasper | bm25 | - | fair | 8192 | section-aware | 0.3445 | +0.0000 | [-0.0077, +0.0000] | 98.33% | no | 0.8283 |
| qasper | bm25 | - | fair | 8192 | small-to-big | 0.3392 | -0.0053 | [-0.0193, +0.0000] | 99.17% | no | 0.1700 |
| qasper | bm25 | - | fair | 8192 | fixed-1024 | 0.3187 | -0.0258 | [-0.0429, -0.0097] | 97.50% | yes | 0.0003 |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).
