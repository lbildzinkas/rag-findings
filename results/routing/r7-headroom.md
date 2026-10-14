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
| qasper/grid | `97bc8de66def0c97a34aaefe87bc535bd43e7b8f2f2320a696721ee5ab74df62` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `bm25` (embedder -), `hybrid` (embedder bge-small), `hybrid` (embedder nomic), `hybrid-rerank` (embedder bge-small), `hybrid-rerank` (embedder nomic), `vector` (embedder bge-small), `vector` (embedder nomic).

## Router gate (pre-registered)

Rule: build the router in v2 if, on the production line, in the production view, at the primary budget of 1024 tokens, pooled over qasper + nq, either embedder's routing headroom is at least +0.0500 retrieval recall with a 95% CI that excludes 0.

Judged on the production line (`hybrid-rerank`), production view (top-N cap 8), 1024-token budget, 95% CI.
**Provisional:** the gate is pre-registered on qasper + nq pooled, and these results lack nq.
- bge-small, pooled over qasper: routing headroom +0.1273 [+0.1150, +0.1393] over the best single chunking (section-aware), which clears the gate.
- nomic, pooled over qasper: routing headroom +0.1294 [+0.1167, +0.1421] over the best single chunking (section-aware), which clears the gate.
**Verdict: build the router in v2** (bge-small, nomic clear the gate).

### The same test on the other pipelines (for reference, not the gate)

| pipeline | embedder | best single chunking | routing headroom | 95% CI | meets the bar |
|---|---|---|---|---|---|
| bm25 | - | section-aware | +0.1132 | [+0.1001, +0.1230] | yes |
| hybrid | bge-small | section-aware | +0.1192 | [+0.1050, +0.1284] | yes |
| hybrid | nomic | small-to-big | +0.1205 | [+0.1076, +0.1313] | yes |
| vector | bge-small | small-to-big | +0.1081 | [+0.0963, +0.1196] | yes |
| vector | nomic | small-to-big | +0.1075 | [+0.0960, +0.1194] | yes |

## Routing headroom

Best single chunking: highest mean retrieval recall at the budget. Oracle router: per question, the chunking with the highest recall (ties to the smaller chunk). Routing headroom: oracle router minus best single chunking; the best single chunking is re-selected inside every resample.

| dataset | pipeline | embedder | view | budget | best single chunking | best single recall | oracle router recall | routing headroom | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.0708 | 0.1216 | +0.0509 | [+0.0418, +0.0605] | 99.17% | yes |
| qasper | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.1080 | 0.1971 | +0.0892 | [+0.0764, +0.1025] | 99.00% | yes |
| qasper | hybrid-rerank | bge-small | production | 512 | small-to-big | 0.1664 | 0.2958 | +0.1293 | [+0.1138, +0.1448] | 98.75% | yes |
| qasper | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.2458 | 0.3731 | +0.1273 | [+0.1150, +0.1393] | 95.00% | yes |
| qasper | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.3031 | 0.4148 | +0.1117 | [+0.0968, +0.1267] | 98.33% | yes |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-512 | 0.3211 | 0.4392 | +0.1180 | [+0.1038, +0.1305] | 97.50% | yes |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.3591 | 0.4495 | +0.0904 | [+0.0794, +0.1015] | 95.00% | yes |
| qasper | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.0708 | 0.1216 | +0.0509 | [+0.0418, +0.0605] | 99.17% | yes |
| qasper | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.1080 | 0.1971 | +0.0892 | [+0.0764, +0.1025] | 99.00% | yes |
| qasper | hybrid-rerank | bge-small | fair | 512 | small-to-big | 0.1664 | 0.2958 | +0.1293 | [+0.1138, +0.1448] | 98.75% | yes |
| qasper | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.2460 | 0.3787 | +0.1327 | [+0.1202, +0.1450] | 95.00% | yes |
| qasper | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.3074 | 0.4286 | +0.1211 | [+0.1061, +0.1364] | 98.33% | yes |
| qasper | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.3445 | 0.4706 | +0.1261 | [+0.1114, +0.1405] | 97.50% | yes |
| qasper | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.3694 | 0.5128 | +0.1433 | [+0.1294, +0.1540] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | production | 128 | small-to-big | 0.0690 | 0.1221 | +0.0531 | [+0.0437, +0.0632] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | production | 256 | small-to-big | 0.1066 | 0.1977 | +0.0911 | [+0.0787, +0.1040] | 99.00% | yes |
| qasper | hybrid-rerank | nomic | production | 512 | small-to-big | 0.1640 | 0.2915 | +0.1275 | [+0.1121, +0.1424] | 98.75% | yes |
| qasper | hybrid-rerank | nomic | production | 1024 | section-aware | 0.2471 | 0.3766 | +0.1294 | [+0.1167, +0.1421] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | production | 2048 | section-aware | 0.3033 | 0.4172 | +0.1140 | [+0.0992, +0.1290] | 98.33% | yes |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.3202 | 0.4420 | +0.1218 | [+0.1066, +0.1346] | 97.50% | yes |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.3692 | 0.4560 | +0.0868 | [+0.0762, +0.0976] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.0690 | 0.1221 | +0.0531 | [+0.0437, +0.0632] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.1066 | 0.1977 | +0.0911 | [+0.0787, +0.1040] | 99.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.1640 | 0.2915 | +0.1275 | [+0.1121, +0.1424] | 98.75% | yes |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.2480 | 0.3847 | +0.1367 | [+0.1238, +0.1496] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.3076 | 0.4312 | +0.1237 | [+0.1084, +0.1388] | 98.33% | yes |
| qasper | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.3443 | 0.4754 | +0.1311 | [+0.1159, +0.1444] | 97.50% | yes |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.3708 | 0.5211 | +0.1503 | [+0.1345, +0.1584] | 95.00% | yes |
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
| qasper | hybrid | bge-small | production | 128 | small-to-big | 0.0465 | 0.0954 | +0.0490 | [+0.0388, +0.0568] | 99.17% | yes |
| qasper | hybrid | bge-small | production | 256 | fixed-128 | 0.0713 | 0.1512 | +0.0799 | [+0.0664, +0.0904] | 99.00% | yes |
| qasper | hybrid | bge-small | production | 512 | small-to-big | 0.1156 | 0.2274 | +0.1118 | [+0.0966, +0.1244] | 98.75% | yes |
| qasper | hybrid | bge-small | production | 1024 | section-aware | 0.1754 | 0.2946 | +0.1192 | [+0.1050, +0.1284] | 95.00% | yes |
| qasper | hybrid | bge-small | production | 2048 | small-to-big | 0.2322 | 0.3351 | +0.1029 | [+0.0880, +0.1147] | 98.33% | yes |
| qasper | hybrid | bge-small | production | 4096 | fixed-512 | 0.2505 | 0.3672 | +0.1167 | [+0.1024, +0.1295] | 97.50% | yes |
| qasper | hybrid | bge-small | production | 8192 | fixed-1024 | 0.2696 | 0.3892 | +0.1196 | [+0.1062, +0.1333] | 95.00% | yes |
| qasper | hybrid | bge-small | fair | 128 | small-to-big | 0.0465 | 0.0954 | +0.0490 | [+0.0388, +0.0568] | 99.17% | yes |
| qasper | hybrid | bge-small | fair | 256 | fixed-128 | 0.0713 | 0.1512 | +0.0799 | [+0.0664, +0.0904] | 99.00% | yes |
| qasper | hybrid | bge-small | fair | 512 | small-to-big | 0.1156 | 0.2274 | +0.1118 | [+0.0966, +0.1244] | 98.75% | yes |
| qasper | hybrid | bge-small | fair | 1024 | section-aware | 0.1759 | 0.3026 | +0.1268 | [+0.1127, +0.1365] | 95.00% | yes |
| qasper | hybrid | bge-small | fair | 2048 | section-aware | 0.2413 | 0.3634 | +0.1222 | [+0.1066, +0.1354] | 98.33% | yes |
| qasper | hybrid | bge-small | fair | 4096 | section-aware | 0.2973 | 0.4301 | +0.1328 | [+0.1175, +0.1459] | 97.50% | yes |
| qasper | hybrid | bge-small | fair | 8192 | section-aware | 0.3636 | 0.5001 | +0.1366 | [+0.1229, +0.1478] | 95.00% | yes |
| qasper | hybrid | nomic | production | 128 | small-to-big | 0.0530 | 0.0967 | +0.0437 | [+0.0352, +0.0529] | 99.17% | yes |
| qasper | hybrid | nomic | production | 256 | small-to-big | 0.0804 | 0.1573 | +0.0769 | [+0.0648, +0.0879] | 99.00% | yes |
| qasper | hybrid | nomic | production | 512 | fixed-128 | 0.1248 | 0.2429 | +0.1181 | [+0.1014, +0.1309] | 98.75% | yes |
| qasper | hybrid | nomic | production | 1024 | small-to-big | 0.1820 | 0.3025 | +0.1205 | [+0.1076, +0.1313] | 95.00% | yes |
| qasper | hybrid | nomic | production | 2048 | small-to-big | 0.2394 | 0.3471 | +0.1077 | [+0.0921, +0.1206] | 98.33% | yes |
| qasper | hybrid | nomic | production | 4096 | small-to-big | 0.2576 | 0.3729 | +0.1152 | [+0.1007, +0.1271] | 97.50% | yes |
| qasper | hybrid | nomic | production | 8192 | fixed-1024 | 0.2818 | 0.3928 | +0.1110 | [+0.0983, +0.1240] | 95.00% | yes |
| qasper | hybrid | nomic | fair | 128 | small-to-big | 0.0530 | 0.0967 | +0.0437 | [+0.0352, +0.0529] | 99.17% | yes |
| qasper | hybrid | nomic | fair | 256 | small-to-big | 0.0804 | 0.1573 | +0.0769 | [+0.0648, +0.0879] | 99.00% | yes |
| qasper | hybrid | nomic | fair | 512 | fixed-128 | 0.1248 | 0.2429 | +0.1181 | [+0.1014, +0.1309] | 98.75% | yes |
| qasper | hybrid | nomic | fair | 1024 | small-to-big | 0.1820 | 0.3107 | +0.1287 | [+0.1156, +0.1393] | 95.00% | yes |
| qasper | hybrid | nomic | fair | 2048 | section-aware | 0.2436 | 0.3719 | +0.1283 | [+0.1119, +0.1409] | 98.33% | yes |
| qasper | hybrid | nomic | fair | 4096 | section-aware | 0.3076 | 0.4391 | +0.1315 | [+0.1165, +0.1445] | 97.50% | yes |
| qasper | hybrid | nomic | fair | 8192 | small-to-big | 0.3662 | 0.5046 | +0.1384 | [+0.1242, +0.1483] | 95.00% | yes |
| qasper | vector | bge-small | production | 128 | small-to-big | 0.0394 | 0.0843 | +0.0449 | [+0.0348, +0.0532] | 99.17% | yes |
| qasper | vector | bge-small | production | 256 | fixed-64 | 0.0611 | 0.1272 | +0.0660 | [+0.0536, +0.0769] | 99.00% | yes |
| qasper | vector | bge-small | production | 512 | section-aware | 0.0885 | 0.1969 | +0.1084 | [+0.0921, +0.1205] | 98.75% | yes |
| qasper | vector | bge-small | production | 1024 | small-to-big | 0.1388 | 0.2468 | +0.1081 | [+0.0963, +0.1196] | 95.00% | yes |
| qasper | vector | bge-small | production | 2048 | small-to-big | 0.1768 | 0.2772 | +0.1003 | [+0.0862, +0.1125] | 98.33% | yes |
| qasper | vector | bge-small | production | 4096 | small-to-big | 0.1873 | 0.2954 | +0.1081 | [+0.0943, +0.1208] | 97.50% | yes |
| qasper | vector | bge-small | production | 8192 | small-to-big | 0.1873 | 0.3085 | +0.1212 | [+0.1083, +0.1334] | 95.00% | yes |
| qasper | vector | bge-small | fair | 128 | small-to-big | 0.0394 | 0.0843 | +0.0449 | [+0.0348, +0.0532] | 99.17% | yes |
| qasper | vector | bge-small | fair | 256 | fixed-64 | 0.0611 | 0.1272 | +0.0660 | [+0.0536, +0.0769] | 99.00% | yes |
| qasper | vector | bge-small | fair | 512 | section-aware | 0.0885 | 0.1969 | +0.1084 | [+0.0921, +0.1203] | 98.75% | yes |
| qasper | vector | bge-small | fair | 1024 | small-to-big | 0.1395 | 0.2572 | +0.1177 | [+0.1055, +0.1289] | 95.00% | yes |
| qasper | vector | bge-small | fair | 2048 | section-aware | 0.1854 | 0.3080 | +0.1226 | [+0.1071, +0.1349] | 98.33% | yes |
| qasper | vector | bge-small | fair | 4096 | section-aware | 0.2399 | 0.3633 | +0.1233 | [+0.1087, +0.1373] | 97.50% | yes |
| qasper | vector | bge-small | fair | 8192 | section-aware | 0.2887 | 0.4212 | +0.1325 | [+0.1191, +0.1425] | 95.00% | yes |
| qasper | vector | nomic | production | 128 | small-to-big | 0.0531 | 0.1008 | +0.0476 | [+0.0386, +0.0577] | 99.17% | yes |
| qasper | vector | nomic | production | 256 | small-to-big | 0.0756 | 0.1484 | +0.0729 | [+0.0611, +0.0850] | 99.00% | yes |
| qasper | vector | nomic | production | 512 | small-to-big | 0.1140 | 0.2165 | +0.1024 | [+0.0889, +0.1167] | 98.75% | yes |
| qasper | vector | nomic | production | 1024 | small-to-big | 0.1625 | 0.2700 | +0.1075 | [+0.0960, +0.1194] | 95.00% | yes |
| qasper | vector | nomic | production | 2048 | small-to-big | 0.2121 | 0.3094 | +0.0973 | [+0.0837, +0.1114] | 98.33% | yes |
| qasper | vector | nomic | production | 4096 | small-to-big | 0.2249 | 0.3351 | +0.1102 | [+0.0965, +0.1242] | 97.50% | yes |
| qasper | vector | nomic | production | 8192 | small-to-big | 0.2249 | 0.3430 | +0.1181 | [+0.1057, +0.1308] | 95.00% | yes |
| qasper | vector | nomic | fair | 128 | small-to-big | 0.0531 | 0.1008 | +0.0476 | [+0.0386, +0.0577] | 99.17% | yes |
| qasper | vector | nomic | fair | 256 | small-to-big | 0.0756 | 0.1484 | +0.0729 | [+0.0611, +0.0850] | 99.00% | yes |
| qasper | vector | nomic | fair | 512 | small-to-big | 0.1140 | 0.2165 | +0.1024 | [+0.0889, +0.1167] | 98.75% | yes |
| qasper | vector | nomic | fair | 1024 | small-to-big | 0.1626 | 0.2789 | +0.1163 | [+0.1045, +0.1283] | 95.00% | yes |
| qasper | vector | nomic | fair | 2048 | small-to-big | 0.2136 | 0.3384 | +0.1248 | [+0.1095, +0.1395] | 98.33% | yes |
| qasper | vector | nomic | fair | 4096 | small-to-big | 0.2596 | 0.3969 | +0.1373 | [+0.1222, +0.1504] | 97.50% | yes |
| qasper | vector | nomic | fair | 8192 | small-to-big | 0.3157 | 0.4546 | +0.1389 | [+0.1260, +0.1513] | 95.00% | yes |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Query-type oracle (secondary; does not change the gate)

The best chunking per labelled query type, applied to every question of that type. Query types come from the labels in hindsight, so no real router has them.

| dataset | pipeline | embedder | view | budget | precise pick | context pick | mixed pick | query-type oracle recall | gain over best single | CI | CI level | oracle router minus query-type oracle | CI | CI level |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | hybrid-rerank | bge-small | production | 128 | small-to-big | fixed-64 | small-to-big | 0.0710 | +0.0002 | [+0.0000, +0.0036] | 99.17% | +0.0507 | [+0.0415, +0.0600] | 99.17% |
| qasper | hybrid-rerank | bge-small | production | 256 | small-to-big | fixed-128 | small-to-big | 0.1088 | +0.0008 | [+0.0000, +0.0054] | 99.17% | +0.0884 | [+0.0753, +0.1013] | 99.00% |
| qasper | hybrid-rerank | bge-small | production | 512 | small-to-big | section-aware | small-to-big | 0.1702 | +0.0038 | [+0.0000, +0.0088] | 99.17% | +0.1256 | [+0.1105, +0.1406] | 98.75% |
| qasper | hybrid-rerank | bge-small | production | 1024 | section-aware | section-aware | section-aware | 0.2458 | +0.0000 | [+0.0000, +0.0066] | 95.00% | +0.1273 | [+0.1143, +0.1381] | 95.00% |
| qasper | hybrid-rerank | bge-small | production | 2048 | section-aware | section-aware | section-aware | 0.3031 | +0.0000 | [+0.0000, +0.0084] | 99.17% | +0.1117 | [+0.0965, +0.1257] | 98.33% |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-512 | fixed-512 | section-aware | 0.3225 | +0.0014 | [+0.0000, +0.0130] | 99.17% | +0.1167 | [+0.1009, +0.1264] | 97.50% |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.3591 | +0.0000 | [+0.0000, +0.0009] | 99.17% | +0.0904 | [+0.0794, +0.1015] | 95.00% |
| qasper | hybrid-rerank | bge-small | fair | 128 | small-to-big | fixed-64 | small-to-big | 0.0710 | +0.0002 | [+0.0000, +0.0036] | 99.17% | +0.0507 | [+0.0415, +0.0600] | 99.17% |
| qasper | hybrid-rerank | bge-small | fair | 256 | small-to-big | fixed-128 | small-to-big | 0.1088 | +0.0008 | [+0.0000, +0.0054] | 99.17% | +0.0884 | [+0.0753, +0.1013] | 99.00% |
| qasper | hybrid-rerank | bge-small | fair | 512 | small-to-big | section-aware | small-to-big | 0.1702 | +0.0038 | [+0.0000, +0.0088] | 99.17% | +0.1256 | [+0.1105, +0.1406] | 98.75% |
| qasper | hybrid-rerank | bge-small | fair | 1024 | section-aware | section-aware | section-aware | 0.2460 | +0.0000 | [+0.0000, +0.0066] | 95.00% | +0.1327 | [+0.1194, +0.1437] | 95.00% |
| qasper | hybrid-rerank | bge-small | fair | 2048 | section-aware | section-aware | section-aware | 0.3074 | +0.0000 | [+0.0000, +0.0081] | 99.17% | +0.1211 | [+0.1057, +0.1357] | 98.33% |
| qasper | hybrid-rerank | bge-small | fair | 4096 | section-aware | fixed-512 | section-aware | 0.3467 | +0.0022 | [+0.0000, +0.0133] | 99.17% | +0.1239 | [+0.1079, +0.1367] | 97.50% |
| qasper | hybrid-rerank | bge-small | fair | 8192 | small-to-big | fixed-1024 | section-aware | 0.3757 | +0.0063 | [+0.0000, +0.0178] | 99.17% | +0.1371 | [+0.1218, +0.1471] | 95.00% |
| qasper | hybrid-rerank | nomic | production | 128 | small-to-big | fixed-64 | small-to-big | 0.0694 | +0.0005 | [+0.0000, +0.0037] | 99.17% | +0.0527 | [+0.0427, +0.0625] | 99.17% |
| qasper | hybrid-rerank | nomic | production | 256 | small-to-big | small-to-big | small-to-big | 0.1066 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0911 | [+0.0780, +0.1031] | 99.00% |
| qasper | hybrid-rerank | nomic | production | 512 | small-to-big | section-aware | small-to-big | 0.1683 | +0.0043 | [+0.0000, +0.0101] | 99.17% | +0.1232 | [+0.1078, +0.1376] | 98.75% |
| qasper | hybrid-rerank | nomic | production | 1024 | section-aware | section-aware | section-aware | 0.2471 | +0.0000 | [+0.0000, +0.0082] | 95.00% | +0.1294 | [+0.1151, +0.1399] | 95.00% |
| qasper | hybrid-rerank | nomic | production | 2048 | section-aware | section-aware | section-aware | 0.3033 | +0.0000 | [+0.0000, +0.0083] | 99.17% | +0.1140 | [+0.0984, +0.1272] | 98.33% |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-512 | fixed-512 | fixed-1024 | 0.3205 | +0.0003 | [+0.0000, +0.0131] | 99.17% | +0.1215 | [+0.1045, +0.1305] | 97.50% |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.3692 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0868 | [+0.0762, +0.0976] | 95.00% |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | fixed-64 | small-to-big | 0.0694 | +0.0005 | [+0.0000, +0.0037] | 99.17% | +0.0527 | [+0.0427, +0.0625] | 99.17% |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.1066 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0911 | [+0.0780, +0.1031] | 99.00% |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | section-aware | small-to-big | 0.1683 | +0.0043 | [+0.0000, +0.0101] | 99.17% | +0.1232 | [+0.1078, +0.1376] | 98.75% |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | section-aware | 0.2480 | +0.0000 | [+0.0000, +0.0080] | 95.00% | +0.1367 | [+0.1223, +0.1477] | 95.00% |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | section-aware | 0.3076 | +0.0000 | [+0.0000, +0.0087] | 99.17% | +0.1237 | [+0.1077, +0.1372] | 98.33% |
| qasper | hybrid-rerank | nomic | fair | 4096 | small-to-big | fixed-512 | section-aware | 0.3472 | +0.0029 | [+0.0000, +0.0138] | 99.17% | +0.1282 | [+0.1116, +0.1401] | 97.50% |
| qasper | hybrid-rerank | nomic | fair | 8192 | small-to-big | fixed-1024 | section-aware | 0.3761 | +0.0053 | [+0.0000, +0.0157] | 99.17% | +0.1451 | [+0.1284, +0.1533] | 95.00% |
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
| qasper | hybrid | bge-small | production | 128 | small-to-big | small-to-big | fixed-64 | 0.0496 | +0.0031 | [+0.0000, +0.0075] | 99.17% | +0.0459 | [+0.0357, +0.0540] | 99.17% |
| qasper | hybrid | bge-small | production | 256 | small-to-big | fixed-128 | fixed-64 | 0.0753 | +0.0040 | [+0.0000, +0.0098] | 99.17% | +0.0759 | [+0.0628, +0.0870] | 99.00% |
| qasper | hybrid | bge-small | production | 512 | small-to-big | fixed-128 | section-aware | 0.1188 | +0.0032 | [+0.0000, +0.0103] | 99.17% | +0.1086 | [+0.0928, +0.1206] | 98.75% |
| qasper | hybrid | bge-small | production | 1024 | small-to-big | section-aware | section-aware | 0.1784 | +0.0030 | [+0.0000, +0.0074] | 95.00% | +0.1162 | [+0.1023, +0.1257] | 95.00% |
| qasper | hybrid | bge-small | production | 2048 | small-to-big | section-aware | small-to-big | 0.2323 | +0.0001 | [+0.0000, +0.0072] | 99.17% | +0.1028 | [+0.0866, +0.1129] | 98.33% |
| qasper | hybrid | bge-small | production | 4096 | small-to-big | fixed-512 | fixed-512 | 0.2545 | +0.0040 | [+0.0000, +0.0156] | 99.17% | +0.1127 | [+0.0974, +0.1241] | 97.50% |
| qasper | hybrid | bge-small | production | 8192 | fixed-1024 | fixed-1024 | fixed-512 | 0.2708 | +0.0012 | [+0.0000, +0.0134] | 99.17% | +0.1184 | [+0.1048, +0.1290] | 95.00% |
| qasper | hybrid | bge-small | fair | 128 | small-to-big | small-to-big | fixed-64 | 0.0496 | +0.0031 | [+0.0000, +0.0075] | 99.17% | +0.0459 | [+0.0357, +0.0540] | 99.17% |
| qasper | hybrid | bge-small | fair | 256 | small-to-big | fixed-128 | fixed-64 | 0.0753 | +0.0040 | [+0.0000, +0.0098] | 99.17% | +0.0759 | [+0.0628, +0.0870] | 99.00% |
| qasper | hybrid | bge-small | fair | 512 | small-to-big | fixed-128 | section-aware | 0.1188 | +0.0032 | [+0.0000, +0.0103] | 99.17% | +0.1086 | [+0.0928, +0.1206] | 98.75% |
| qasper | hybrid | bge-small | fair | 1024 | small-to-big | section-aware | section-aware | 0.1784 | +0.0025 | [+0.0000, +0.0073] | 95.00% | +0.1242 | [+0.1098, +0.1338] | 95.00% |
| qasper | hybrid | bge-small | fair | 2048 | section-aware | section-aware | small-to-big | 0.2415 | +0.0003 | [+0.0000, +0.0072] | 99.17% | +0.1219 | [+0.1050, +0.1336] | 98.33% |
| qasper | hybrid | bge-small | fair | 4096 | section-aware | section-aware | section-aware | 0.2973 | +0.0000 | [+0.0000, +0.0090] | 99.17% | +0.1328 | [+0.1157, +0.1433] | 97.50% |
| qasper | hybrid | bge-small | fair | 8192 | small-to-big | section-aware | section-aware | 0.3663 | +0.0027 | [+0.0000, +0.0102] | 99.17% | +0.1338 | [+0.1200, +0.1452] | 95.00% |
| qasper | hybrid | nomic | production | 128 | small-to-big | small-to-big | small-to-big | 0.0530 | +0.0000 | [+0.0000, +0.0043] | 99.00% | +0.0437 | [+0.0346, +0.0521] | 99.17% |
| qasper | hybrid | nomic | production | 256 | fixed-128 | fixed-64 | small-to-big | 0.0805 | +0.0001 | [+0.0000, +0.0071] | 99.00% | +0.0768 | [+0.0631, +0.0858] | 99.00% |
| qasper | hybrid | nomic | production | 512 | small-to-big | section-aware | fixed-128 | 0.1254 | +0.0006 | [+0.0000, +0.0092] | 99.00% | +0.1176 | [+0.0986, +0.1273] | 98.75% |
| qasper | hybrid | nomic | production | 1024 | small-to-big | section-aware | section-aware | 0.1876 | +0.0055 | [+0.0001, +0.0113] | 95.00% | +0.1150 | [+0.1020, +0.1264] | 95.00% |
| qasper | hybrid | nomic | production | 2048 | small-to-big | fixed-256 | section-aware | 0.2401 | +0.0007 | [+0.0000, +0.0087] | 99.00% | +0.1070 | [+0.0898, +0.1182] | 98.33% |
| qasper | hybrid | nomic | production | 4096 | small-to-big | fixed-512 | small-to-big | 0.2652 | +0.0076 | [+0.0003, +0.0138] | 99.17% | +0.1076 | [+0.0933, +0.1200] | 97.50% |
| qasper | hybrid | nomic | production | 8192 | fixed-1024 | fixed-1024 | small-to-big | 0.2827 | +0.0009 | [+0.0000, +0.0130] | 99.00% | +0.1101 | [+0.0968, +0.1199] | 95.00% |
| qasper | hybrid | nomic | fair | 128 | small-to-big | small-to-big | small-to-big | 0.0530 | +0.0000 | [+0.0000, +0.0043] | 99.17% | +0.0437 | [+0.0346, +0.0521] | 99.17% |
| qasper | hybrid | nomic | fair | 256 | fixed-128 | fixed-64 | small-to-big | 0.0805 | +0.0001 | [+0.0000, +0.0072] | 99.17% | +0.0768 | [+0.0631, +0.0858] | 99.00% |
| qasper | hybrid | nomic | fair | 512 | small-to-big | section-aware | fixed-128 | 0.1254 | +0.0006 | [+0.0000, +0.0094] | 99.17% | +0.1176 | [+0.0986, +0.1273] | 98.75% |
| qasper | hybrid | nomic | fair | 1024 | small-to-big | section-aware | section-aware | 0.1880 | +0.0060 | [+0.0001, +0.0117] | 95.00% | +0.1227 | [+0.1097, +0.1340] | 95.00% |
| qasper | hybrid | nomic | fair | 2048 | section-aware | small-to-big | section-aware | 0.2447 | +0.0011 | [+0.0000, +0.0080] | 99.17% | +0.1271 | [+0.1099, +0.1386] | 98.33% |
| qasper | hybrid | nomic | fair | 4096 | section-aware | section-aware | small-to-big | 0.3086 | +0.0010 | [+0.0000, +0.0080] | 99.17% | +0.1305 | [+0.1147, +0.1420] | 97.50% |
| qasper | hybrid | nomic | fair | 8192 | small-to-big | section-aware | section-aware | 0.3686 | +0.0024 | [+0.0000, +0.0085] | 99.17% | +0.1360 | [+0.1222, +0.1462] | 95.00% |
| qasper | vector | bge-small | production | 128 | small-to-big | small-to-big | fixed-64 | 0.0405 | +0.0010 | [+0.0000, +0.0052] | 99.17% | +0.0439 | [+0.0336, +0.0519] | 99.17% |
| qasper | vector | bge-small | production | 256 | fixed-64 | small-to-big | fixed-64 | 0.0619 | +0.0008 | [+0.0000, +0.0067] | 99.17% | +0.0652 | [+0.0521, +0.0749] | 99.00% |
| qasper | vector | bge-small | production | 512 | fixed-64 | section-aware | section-aware | 0.0925 | +0.0040 | [+0.0000, +0.0111] | 99.17% | +0.1043 | [+0.0879, +0.1168] | 98.75% |
| qasper | vector | bge-small | production | 1024 | small-to-big | small-to-big | section-aware | 0.1441 | +0.0053 | [+0.0005, +0.0116] | 95.00% | +0.1027 | [+0.0905, +0.1134] | 95.00% |
| qasper | vector | bge-small | production | 2048 | small-to-big | section-aware | section-aware | 0.1814 | +0.0046 | [+0.0000, +0.0124] | 99.17% | +0.0957 | [+0.0818, +0.1081] | 98.33% |
| qasper | vector | bge-small | production | 4096 | small-to-big | fixed-512 | section-aware | 0.1935 | +0.0062 | [+0.0000, +0.0161] | 99.17% | +0.1019 | [+0.0884, +0.1148] | 97.50% |
| qasper | vector | bge-small | production | 8192 | small-to-big | fixed-1024 | section-aware | 0.1949 | +0.0076 | [+0.0000, +0.0191] | 99.17% | +0.1136 | [+0.1004, +0.1255] | 95.00% |
| qasper | vector | bge-small | fair | 128 | small-to-big | small-to-big | fixed-64 | 0.0405 | +0.0010 | [+0.0000, +0.0052] | 99.17% | +0.0439 | [+0.0336, +0.0519] | 99.17% |
| qasper | vector | bge-small | fair | 256 | fixed-64 | small-to-big | fixed-64 | 0.0619 | +0.0008 | [+0.0000, +0.0067] | 99.17% | +0.0652 | [+0.0521, +0.0749] | 99.00% |
| qasper | vector | bge-small | fair | 512 | fixed-64 | section-aware | section-aware | 0.0927 | +0.0042 | [+0.0000, +0.0111] | 99.17% | +0.1041 | [+0.0878, +0.1167] | 98.75% |
| qasper | vector | bge-small | fair | 1024 | small-to-big | small-to-big | section-aware | 0.1458 | +0.0063 | [+0.0008, +0.0123] | 95.00% | +0.1114 | [+0.0988, +0.1224] | 95.00% |
| qasper | vector | bge-small | fair | 2048 | small-to-big | section-aware | section-aware | 0.1903 | +0.0049 | [+0.0000, +0.0133] | 99.17% | +0.1177 | [+0.1026, +0.1310] | 98.33% |
| qasper | vector | bge-small | fair | 4096 | section-aware | section-aware | section-aware | 0.2399 | +0.0000 | [+0.0000, +0.0094] | 99.17% | +0.1233 | [+0.1084, +0.1356] | 97.50% |
| qasper | vector | bge-small | fair | 8192 | small-to-big | section-aware | small-to-big | 0.2896 | +0.0009 | [+0.0000, +0.0099] | 99.17% | +0.1316 | [+0.1169, +0.1401] | 95.00% |
| qasper | vector | nomic | production | 128 | small-to-big | fixed-64 | small-to-big | 0.0533 | +0.0001 | [+0.0000, +0.0045] | 99.17% | +0.0475 | [+0.0378, +0.0567] | 99.17% |
| qasper | vector | nomic | production | 256 | small-to-big | small-to-big | small-to-big | 0.0756 | +0.0000 | [+0.0000, +0.0050] | 99.17% | +0.0729 | [+0.0606, +0.0837] | 99.00% |
| qasper | vector | nomic | production | 512 | small-to-big | small-to-big | section-aware | 0.1169 | +0.0028 | [+0.0000, +0.0110] | 99.17% | +0.0996 | [+0.0856, +0.1125] | 98.75% |
| qasper | vector | nomic | production | 1024 | small-to-big | section-aware | small-to-big | 0.1633 | +0.0007 | [+0.0000, +0.0064] | 95.00% | +0.1067 | [+0.0943, +0.1168] | 95.00% |
| qasper | vector | nomic | production | 2048 | small-to-big | small-to-big | small-to-big | 0.2121 | +0.0000 | [+0.0000, +0.0057] | 99.17% | +0.0973 | [+0.0829, +0.1102] | 98.33% |
| qasper | vector | nomic | production | 4096 | small-to-big | fixed-512 | small-to-big | 0.2258 | +0.0009 | [+0.0000, +0.0086] | 99.17% | +0.1093 | [+0.0949, +0.1221] | 97.50% |
| qasper | vector | nomic | production | 8192 | small-to-big | fixed-1024 | small-to-big | 0.2296 | +0.0047 | [+0.0000, +0.0130] | 99.17% | +0.1134 | [+0.1012, +0.1257] | 95.00% |
| qasper | vector | nomic | fair | 128 | small-to-big | fixed-64 | small-to-big | 0.0533 | +0.0001 | [+0.0000, +0.0045] | 99.17% | +0.0475 | [+0.0378, +0.0567] | 99.17% |
| qasper | vector | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.0756 | +0.0000 | [+0.0000, +0.0050] | 99.17% | +0.0729 | [+0.0606, +0.0837] | 99.00% |
| qasper | vector | nomic | fair | 512 | small-to-big | small-to-big | section-aware | 0.1169 | +0.0028 | [+0.0000, +0.0110] | 99.17% | +0.0996 | [+0.0856, +0.1125] | 98.75% |
| qasper | vector | nomic | fair | 1024 | small-to-big | section-aware | small-to-big | 0.1633 | +0.0007 | [+0.0000, +0.0064] | 95.00% | +0.1156 | [+0.1027, +0.1257] | 95.00% |
| qasper | vector | nomic | fair | 2048 | small-to-big | section-aware | small-to-big | 0.2145 | +0.0009 | [+0.0000, +0.0075] | 99.17% | +0.1240 | [+0.1083, +0.1373] | 98.33% |
| qasper | vector | nomic | fair | 4096 | small-to-big | small-to-big | section-aware | 0.2625 | +0.0029 | [+0.0000, +0.0107] | 99.17% | +0.1344 | [+0.1188, +0.1471] | 97.50% |
| qasper | vector | nomic | fair | 8192 | small-to-big | section-aware | small-to-big | 0.3163 | +0.0006 | [+0.0000, +0.0096] | 99.17% | +0.1383 | [+0.1241, +0.1492] | 95.00% |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Each chunking against the best single chunking

Difference: the chunking's mean recall minus the best single chunking's, with the best re-selected inside every resample (so the best chunking's own difference is 0 with a CI at or below 0). Best in resamples: the share of resamples in which the chunking was the best single chunking.

| dataset | pipeline | embedder | view | budget | chunking | mean recall | difference from best | CI | CI level | CI excludes 0 | best in resamples |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qasper | hybrid-rerank | bge-small | production | 128 | fixed-64 | 0.0526 | -0.0182 | [-0.0298, -0.0070] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 128 | fixed-128 | 0.0416 | -0.0291 | [-0.0408, -0.0179] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 128 | section-aware | 0.0313 | -0.0395 | [-0.0534, -0.0262] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.0708 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 1.0000 |
| qasper | hybrid-rerank | bge-small | production | 256 | fixed-64 | 0.0863 | -0.0217 | [-0.0360, -0.0085] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 256 | fixed-128 | 0.0935 | -0.0144 | [-0.0255, -0.0039] | 95.00% | yes | 0.0034 |
| qasper | hybrid-rerank | bge-small | production | 256 | fixed-256 | 0.0632 | -0.0448 | [-0.0619, -0.0279] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 256 | section-aware | 0.0619 | -0.0461 | [-0.0604, -0.0323] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.1080 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9966 |
| qasper | hybrid-rerank | bge-small | production | 512 | fixed-64 | 0.1245 | -0.0419 | [-0.0582, -0.0262] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 512 | fixed-128 | 0.1410 | -0.0254 | [-0.0422, -0.0094] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 512 | fixed-256 | 0.1271 | -0.0393 | [-0.0573, -0.0215] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 512 | fixed-512 | 0.0970 | -0.0694 | [-0.0912, -0.0488] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 512 | section-aware | 0.1559 | -0.0105 | [-0.0248, +0.0000] | 98.33% | no | 0.0351 |
| qasper | hybrid-rerank | bge-small | production | 512 | small-to-big | 0.1664 | +0.0000 | [-0.0042, +0.0000] | 98.75% | no | 0.9649 |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.1245 | -0.1213 | [-0.1365, -0.1066] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.1958 | -0.0501 | [-0.0642, -0.0364] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.2058 | -0.0400 | [-0.0532, -0.0270] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.1858 | -0.0600 | [-0.0757, -0.0453] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.2458 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9864 |
| qasper | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.2333 | -0.0125 | [-0.0240, -0.0015] | 95.00% | yes | 0.0136 |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.1521 | -0.0938 | [-0.1130, -0.0755] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 2048 | fixed-64 | 0.1245 | -0.1785 | [-0.1984, -0.1586] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 2048 | fixed-128 | 0.1958 | -0.1073 | [-0.1256, -0.0890] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 2048 | fixed-256 | 0.2617 | -0.0414 | [-0.0572, -0.0258] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 2048 | fixed-512 | 0.2555 | -0.0476 | [-0.0660, -0.0298] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.3031 | +0.0000 | [-0.0001, +0.0000] | 98.33% | no | 0.9911 |
| qasper | hybrid-rerank | bge-small | production | 2048 | small-to-big | 0.2893 | -0.0138 | [-0.0285, +0.0000] | 98.75% | no | 0.0089 |
| qasper | hybrid-rerank | bge-small | production | 2048 | fixed-1024 | 0.2411 | -0.0620 | [-0.0827, -0.0418] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-64 | 0.1245 | -0.1966 | [-0.2163, -0.1788] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-128 | 0.1958 | -0.1254 | [-0.1442, -0.1093] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-256 | 0.2617 | -0.0594 | [-0.0732, -0.0475] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-512 | 0.3211 | +0.0000 | [-0.0072, +0.0000] | 95.00% | no | 0.8092 |
| qasper | hybrid-rerank | bge-small | production | 4096 | section-aware | 0.3119 | -0.0093 | [-0.0265, +0.0000] | 98.33% | no | 0.0783 |
| qasper | hybrid-rerank | bge-small | production | 4096 | small-to-big | 0.3010 | -0.0201 | [-0.0404, -0.0032] | 99.00% | yes | 0.0018 |
| qasper | hybrid-rerank | bge-small | production | 4096 | fixed-1024 | 0.3132 | -0.0079 | [-0.0232, +0.0000] | 97.50% | no | 0.1107 |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-64 | 0.1245 | -0.2345 | [-0.2535, -0.2154] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-128 | 0.1958 | -0.1633 | [-0.1837, -0.1436] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-256 | 0.2617 | -0.0973 | [-0.1122, -0.0826] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-512 | 0.3211 | -0.0379 | [-0.0524, -0.0238] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | section-aware | 0.3119 | -0.0472 | [-0.0670, -0.0269] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | small-to-big | 0.3010 | -0.0580 | [-0.0813, -0.0345] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.3591 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| qasper | hybrid-rerank | bge-small | fair | 128 | fixed-64 | 0.0526 | -0.0182 | [-0.0298, -0.0070] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 128 | fixed-128 | 0.0416 | -0.0291 | [-0.0408, -0.0179] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 128 | section-aware | 0.0313 | -0.0395 | [-0.0534, -0.0262] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.0708 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| qasper | hybrid-rerank | bge-small | fair | 256 | fixed-64 | 0.0863 | -0.0217 | [-0.0360, -0.0085] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 256 | fixed-128 | 0.0935 | -0.0144 | [-0.0255, -0.0039] | 95.00% | yes | 0.0034 |
| qasper | hybrid-rerank | bge-small | fair | 256 | fixed-256 | 0.0632 | -0.0448 | [-0.0619, -0.0279] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 256 | section-aware | 0.0619 | -0.0461 | [-0.0604, -0.0323] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.1080 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9966 |
| qasper | hybrid-rerank | bge-small | fair | 512 | fixed-64 | 0.1245 | -0.0419 | [-0.0582, -0.0262] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 512 | fixed-128 | 0.1410 | -0.0254 | [-0.0422, -0.0094] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 512 | fixed-256 | 0.1271 | -0.0393 | [-0.0573, -0.0215] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 512 | fixed-512 | 0.0970 | -0.0694 | [-0.0912, -0.0488] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 512 | section-aware | 0.1559 | -0.0105 | [-0.0254, +0.0000] | 98.75% | no | 0.0351 |
| qasper | hybrid-rerank | bge-small | fair | 512 | small-to-big | 0.1664 | +0.0000 | [-0.0052, +0.0000] | 99.17% | no | 0.9649 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.1617 | -0.0843 | [-0.0984, -0.0705] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.1958 | -0.0502 | [-0.0643, -0.0365] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.2058 | -0.0402 | [-0.0534, -0.0272] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.1858 | -0.0602 | [-0.0758, -0.0454] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.2460 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9869 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.2333 | -0.0126 | [-0.0241, -0.0016] | 95.00% | yes | 0.0131 |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.1521 | -0.0939 | [-0.1130, -0.0755] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | fixed-64 | 0.1886 | -0.1189 | [-0.1367, -0.1006] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | fixed-128 | 0.2373 | -0.0702 | [-0.0875, -0.0521] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | fixed-256 | 0.2618 | -0.0456 | [-0.0612, -0.0297] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | fixed-512 | 0.2558 | -0.0516 | [-0.0700, -0.0337] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.3074 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9945 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | small-to-big | 0.2925 | -0.0149 | [-0.0306, +0.0000] | 99.17% | no | 0.0055 |
| qasper | hybrid-rerank | bge-small | fair | 2048 | fixed-1024 | 0.2411 | -0.0663 | [-0.0870, -0.0461] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | fixed-64 | 0.2314 | -0.1132 | [-0.1296, -0.0962] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | fixed-128 | 0.2656 | -0.0790 | [-0.0962, -0.0623] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | fixed-256 | 0.3009 | -0.0436 | [-0.0577, -0.0296] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | fixed-512 | 0.3220 | -0.0225 | [-0.0386, -0.0070] | 97.50% | yes | 0.0003 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.3445 | +0.0000 | [-0.0018, +0.0000] | 98.75% | no | 0.9832 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | small-to-big | 0.3324 | -0.0121 | [-0.0275, +0.0000] | 99.17% | no | 0.0164 |
| qasper | hybrid-rerank | bge-small | fair | 4096 | fixed-1024 | 0.3132 | -0.0313 | [-0.0499, -0.0128] | 97.50% | yes | 0.0001 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | fixed-64 | 0.2765 | -0.0930 | [-0.1086, -0.0802] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | fixed-128 | 0.3168 | -0.0527 | [-0.0685, -0.0399] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | fixed-256 | 0.3266 | -0.0429 | [-0.0557, -0.0329] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | fixed-512 | 0.3520 | -0.0175 | [-0.0325, -0.0058] | 95.00% | yes | 0.0013 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.3694 | +0.0000 | [-0.0128, +0.0000] | 98.75% | no | 0.7019 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | small-to-big | 0.3639 | -0.0055 | [-0.0225, +0.0000] | 99.17% | no | 0.1488 |
| qasper | hybrid-rerank | bge-small | fair | 8192 | fixed-1024 | 0.3614 | -0.0080 | [-0.0247, +0.0000] | 95.00% | no | 0.1480 |
| qasper | hybrid-rerank | nomic | production | 128 | fixed-64 | 0.0524 | -0.0165 | [-0.0282, -0.0052] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 128 | fixed-128 | 0.0439 | -0.0250 | [-0.0371, -0.0136] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 128 | section-aware | 0.0315 | -0.0375 | [-0.0515, -0.0243] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 128 | small-to-big | 0.0690 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 1.0000 |
| qasper | hybrid-rerank | nomic | production | 256 | fixed-64 | 0.0879 | -0.0187 | [-0.0330, -0.0056] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 256 | fixed-128 | 0.0936 | -0.0130 | [-0.0246, -0.0020] | 95.00% | yes | 0.0106 |
| qasper | hybrid-rerank | nomic | production | 256 | fixed-256 | 0.0620 | -0.0446 | [-0.0623, -0.0274] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 256 | section-aware | 0.0634 | -0.0431 | [-0.0576, -0.0287] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 256 | small-to-big | 0.1066 | +0.0000 | [-0.0016, +0.0000] | 99.00% | no | 0.9894 |
| qasper | hybrid-rerank | nomic | production | 512 | fixed-64 | 0.1241 | -0.0400 | [-0.0561, -0.0255] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 512 | fixed-128 | 0.1411 | -0.0229 | [-0.0400, -0.0069] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 512 | fixed-256 | 0.1249 | -0.0391 | [-0.0565, -0.0228] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 512 | fixed-512 | 0.1006 | -0.0634 | [-0.0847, -0.0442] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 512 | section-aware | 0.1570 | -0.0070 | [-0.0214, +0.0000] | 98.33% | no | 0.1197 |
| qasper | hybrid-rerank | nomic | production | 512 | small-to-big | 0.1640 | +0.0000 | [-0.0079, +0.0000] | 99.00% | no | 0.8803 |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.1241 | -0.1231 | [-0.1389, -0.1087] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.1985 | -0.0486 | [-0.0631, -0.0350] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.2019 | -0.0453 | [-0.0595, -0.0316] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.1890 | -0.0582 | [-0.0743, -0.0428] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 1024 | section-aware | 0.2471 | +0.0000 | [-0.0027, +0.0000] | 95.00% | no | 0.9378 |
| qasper | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.2377 | -0.0094 | [-0.0215, +0.0000] | 95.00% | no | 0.0622 |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.1509 | -0.0963 | [-0.1158, -0.0773] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 2048 | fixed-64 | 0.1241 | -0.1792 | [-0.1997, -0.1594] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 2048 | fixed-128 | 0.1985 | -0.1047 | [-0.1238, -0.0867] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 2048 | fixed-256 | 0.2599 | -0.0434 | [-0.0594, -0.0269] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 2048 | fixed-512 | 0.2596 | -0.0436 | [-0.0620, -0.0250] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 2048 | section-aware | 0.3033 | +0.0000 | [-0.0036, +0.0000] | 98.33% | no | 0.9599 |
| qasper | hybrid-rerank | nomic | production | 2048 | small-to-big | 0.2933 | -0.0100 | [-0.0245, +0.0000] | 99.00% | no | 0.0401 |
| qasper | hybrid-rerank | nomic | production | 2048 | fixed-1024 | 0.2430 | -0.0603 | [-0.0815, -0.0397] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-64 | 0.1241 | -0.1962 | [-0.2161, -0.1790] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-128 | 0.1985 | -0.1217 | [-0.1401, -0.1063] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-256 | 0.2599 | -0.0603 | [-0.0744, -0.0487] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.3202 | +0.0000 | [-0.0081, +0.0000] | 95.00% | no | 0.7464 |
| qasper | hybrid-rerank | nomic | production | 4096 | section-aware | 0.3101 | -0.0101 | [-0.0284, +0.0000] | 98.33% | no | 0.0655 |
| qasper | hybrid-rerank | nomic | production | 4096 | small-to-big | 0.3057 | -0.0146 | [-0.0345, +0.0000] | 99.00% | no | 0.0124 |
| qasper | hybrid-rerank | nomic | production | 4096 | fixed-1024 | 0.3143 | -0.0059 | [-0.0209, +0.0000] | 97.50% | no | 0.1757 |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-64 | 0.1241 | -0.2451 | [-0.2648, -0.2260] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-128 | 0.1985 | -0.1707 | [-0.1912, -0.1507] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-256 | 0.2599 | -0.1093 | [-0.1248, -0.0943] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-512 | 0.3202 | -0.0490 | [-0.0639, -0.0349] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | section-aware | 0.3101 | -0.0591 | [-0.0795, -0.0390] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | small-to-big | 0.3057 | -0.0635 | [-0.0859, -0.0415] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.3692 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| qasper | hybrid-rerank | nomic | fair | 128 | fixed-64 | 0.0524 | -0.0165 | [-0.0282, -0.0052] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 128 | fixed-128 | 0.0439 | -0.0250 | [-0.0371, -0.0136] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 128 | section-aware | 0.0315 | -0.0375 | [-0.0515, -0.0243] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.0690 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| qasper | hybrid-rerank | nomic | fair | 256 | fixed-64 | 0.0879 | -0.0187 | [-0.0330, -0.0056] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 256 | fixed-128 | 0.0936 | -0.0130 | [-0.0246, -0.0020] | 95.00% | yes | 0.0106 |
| qasper | hybrid-rerank | nomic | fair | 256 | fixed-256 | 0.0620 | -0.0446 | [-0.0623, -0.0274] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 256 | section-aware | 0.0634 | -0.0431 | [-0.0576, -0.0287] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.1066 | +0.0000 | [-0.0019, +0.0000] | 99.17% | no | 0.9894 |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-64 | 0.1241 | -0.0400 | [-0.0561, -0.0255] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-128 | 0.1411 | -0.0229 | [-0.0400, -0.0069] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-256 | 0.1249 | -0.0391 | [-0.0565, -0.0228] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-512 | 0.1006 | -0.0634 | [-0.0847, -0.0442] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 512 | section-aware | 0.1570 | -0.0070 | [-0.0220, +0.0000] | 98.75% | no | 0.1197 |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.1640 | +0.0000 | [-0.0082, +0.0000] | 99.17% | no | 0.8803 |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1634 | -0.0846 | [-0.0996, -0.0705] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.1985 | -0.0495 | [-0.0639, -0.0358] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2019 | -0.0462 | [-0.0605, -0.0324] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1890 | -0.0591 | [-0.0752, -0.0436] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.2480 | +0.0000 | [-0.0019, +0.0000] | 95.00% | no | 0.9513 |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.2377 | -0.0103 | [-0.0223, +0.0000] | 95.00% | no | 0.0487 |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.1509 | -0.0972 | [-0.1167, -0.0781] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 0.1910 | -0.1166 | [-0.1346, -0.0987] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-128 | 0.2434 | -0.0642 | [-0.0823, -0.0467] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 0.2599 | -0.0477 | [-0.0639, -0.0312] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 0.2596 | -0.0479 | [-0.0664, -0.0299] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.3076 | +0.0000 | [-0.0045, +0.0000] | 98.75% | no | 0.9544 |
| qasper | hybrid-rerank | nomic | fair | 2048 | small-to-big | 0.2975 | -0.0101 | [-0.0251, +0.0000] | 99.17% | no | 0.0456 |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 0.2430 | -0.0646 | [-0.0861, -0.0439] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 0.2387 | -0.1055 | [-0.1228, -0.0905] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-128 | 0.2703 | -0.0739 | [-0.0914, -0.0593] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 0.3000 | -0.0443 | [-0.0599, -0.0307] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 0.3209 | -0.0234 | [-0.0405, -0.0082] | 97.50% | yes | 0.0003 |
| qasper | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.3443 | +0.0000 | [-0.0113, +0.0000] | 98.75% | no | 0.7336 |
| qasper | hybrid-rerank | nomic | fair | 4096 | small-to-big | 0.3404 | -0.0039 | [-0.0191, +0.0000] | 99.17% | no | 0.2661 |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 0.3143 | -0.0299 | [-0.0492, -0.0126] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 0.2862 | -0.0845 | [-0.1029, -0.0742] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-128 | 0.3286 | -0.0422 | [-0.0611, -0.0316] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 0.3283 | -0.0424 | [-0.0576, -0.0353] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 0.3598 | -0.0110 | [-0.0266, -0.0033] | 95.00% | yes | 0.0058 |
| qasper | hybrid-rerank | nomic | fair | 8192 | section-aware | 0.3695 | -0.0013 | [-0.0223, +0.0000] | 98.75% | no | 0.2947 |
| qasper | hybrid-rerank | nomic | fair | 8192 | small-to-big | 0.3696 | -0.0012 | [-0.0215, +0.0000] | 99.17% | no | 0.2654 |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.3708 | +0.0000 | [-0.0164, +0.0000] | 95.00% | no | 0.4341 |
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
| qasper | hybrid | bge-small | production | 128 | fixed-64 | 0.0453 | -0.0012 | [-0.0097, +0.0000] | 97.50% | no | 0.2956 |
| qasper | hybrid | bge-small | production | 128 | fixed-128 | 0.0442 | -0.0023 | [-0.0117, +0.0000] | 98.33% | no | 0.1655 |
| qasper | hybrid | bge-small | production | 128 | section-aware | 0.0207 | -0.0258 | [-0.0373, -0.0167] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 128 | small-to-big | 0.0465 | +0.0000 | [-0.0085, +0.0000] | 99.00% | no | 0.5389 |
| qasper | hybrid | bge-small | production | 256 | fixed-64 | 0.0708 | -0.0004 | [-0.0101, +0.0000] | 97.50% | no | 0.3390 |
| qasper | hybrid | bge-small | production | 256 | fixed-128 | 0.0713 | +0.0000 | [-0.0101, +0.0000] | 98.33% | no | 0.4149 |
| qasper | hybrid | bge-small | production | 256 | fixed-256 | 0.0585 | -0.0127 | [-0.0228, -0.0068] | 95.00% | yes | 0.0002 |
| qasper | hybrid | bge-small | production | 256 | section-aware | 0.0421 | -0.0291 | [-0.0431, -0.0197] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 256 | small-to-big | 0.0697 | -0.0016 | [-0.0140, +0.0000] | 99.00% | no | 0.2459 |
| qasper | hybrid | bge-small | production | 512 | fixed-64 | 0.1028 | -0.0127 | [-0.0259, -0.0045] | 98.33% | yes | 0.0001 |
| qasper | hybrid | bge-small | production | 512 | fixed-128 | 0.1136 | -0.0020 | [-0.0149, +0.0000] | 98.33% | no | 0.3265 |
| qasper | hybrid | bge-small | production | 512 | fixed-256 | 0.0989 | -0.0166 | [-0.0319, -0.0060] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 512 | fixed-512 | 0.0815 | -0.0341 | [-0.0498, -0.0224] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 512 | section-aware | 0.1093 | -0.0063 | [-0.0211, +0.0000] | 98.33% | no | 0.0848 |
| qasper | hybrid | bge-small | production | 512 | small-to-big | 0.1156 | +0.0000 | [-0.0124, +0.0000] | 99.00% | no | 0.5886 |
| qasper | hybrid | bge-small | production | 1024 | fixed-64 | 0.1028 | -0.0726 | [-0.0874, -0.0635] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 1024 | fixed-128 | 0.1598 | -0.0156 | [-0.0295, -0.0069] | 95.00% | yes | 0.0003 |
| qasper | hybrid | bge-small | production | 1024 | fixed-256 | 0.1497 | -0.0257 | [-0.0399, -0.0169] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 1024 | fixed-512 | 0.1299 | -0.0456 | [-0.0610, -0.0356] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 1024 | section-aware | 0.1754 | +0.0000 | [-0.0125, +0.0000] | 95.00% | no | 0.5199 |
| qasper | hybrid | bge-small | production | 1024 | small-to-big | 0.1752 | -0.0002 | [-0.0127, +0.0000] | 95.00% | no | 0.4798 |
| qasper | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0994 | -0.0760 | [-0.0931, -0.0641] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 2048 | fixed-64 | 0.1028 | -0.1294 | [-0.1503, -0.1129] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 2048 | fixed-128 | 0.1598 | -0.0724 | [-0.0904, -0.0582] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 2048 | fixed-256 | 0.2101 | -0.0221 | [-0.0362, -0.0109] | 97.50% | yes | 0.0001 |
| qasper | hybrid | bge-small | production | 2048 | fixed-512 | 0.1875 | -0.0448 | [-0.0624, -0.0307] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 2048 | section-aware | 0.2300 | -0.0022 | [-0.0162, +0.0000] | 98.33% | no | 0.3569 |
| qasper | hybrid | bge-small | production | 2048 | small-to-big | 0.2322 | +0.0000 | [-0.0127, +0.0000] | 99.00% | no | 0.6430 |
| qasper | hybrid | bge-small | production | 2048 | fixed-1024 | 0.1447 | -0.0875 | [-0.1082, -0.0702] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 4096 | fixed-64 | 0.1028 | -0.1477 | [-0.1696, -0.1289] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 4096 | fixed-128 | 0.1598 | -0.0907 | [-0.1107, -0.0746] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 4096 | fixed-256 | 0.2101 | -0.0404 | [-0.0560, -0.0275] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 4096 | fixed-512 | 0.2505 | +0.0000 | [-0.0068, +0.0000] | 95.00% | no | 0.8326 |
| qasper | hybrid | bge-small | production | 4096 | section-aware | 0.2405 | -0.0100 | [-0.0267, +0.0000] | 98.33% | no | 0.0487 |
| qasper | hybrid | bge-small | production | 4096 | small-to-big | 0.2425 | -0.0080 | [-0.0260, +0.0000] | 99.00% | no | 0.1187 |
| qasper | hybrid | bge-small | production | 4096 | fixed-1024 | 0.2044 | -0.0461 | [-0.0622, -0.0320] | 97.50% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 8192 | fixed-64 | 0.1028 | -0.1668 | [-0.1900, -0.1438] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 8192 | fixed-128 | 0.1598 | -0.1098 | [-0.1327, -0.0881] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 8192 | fixed-256 | 0.2101 | -0.0595 | [-0.0790, -0.0399] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | production | 8192 | fixed-512 | 0.2505 | -0.0191 | [-0.0343, -0.0036] | 97.50% | yes | 0.0030 |
| qasper | hybrid | bge-small | production | 8192 | section-aware | 0.2405 | -0.0291 | [-0.0510, -0.0072] | 98.75% | yes | 0.0002 |
| qasper | hybrid | bge-small | production | 8192 | small-to-big | 0.2425 | -0.0271 | [-0.0512, -0.0035] | 99.17% | yes | 0.0012 |
| qasper | hybrid | bge-small | production | 8192 | fixed-1024 | 0.2696 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9956 |
| qasper | hybrid | bge-small | fair | 128 | fixed-64 | 0.0453 | -0.0012 | [-0.0097, +0.0000] | 97.50% | no | 0.2956 |
| qasper | hybrid | bge-small | fair | 128 | fixed-128 | 0.0442 | -0.0023 | [-0.0117, +0.0000] | 98.33% | no | 0.1655 |
| qasper | hybrid | bge-small | fair | 128 | section-aware | 0.0207 | -0.0258 | [-0.0373, -0.0167] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 128 | small-to-big | 0.0465 | +0.0000 | [-0.0087, +0.0000] | 99.17% | no | 0.5389 |
| qasper | hybrid | bge-small | fair | 256 | fixed-64 | 0.0708 | -0.0004 | [-0.0101, +0.0000] | 97.50% | no | 0.3390 |
| qasper | hybrid | bge-small | fair | 256 | fixed-128 | 0.0713 | +0.0000 | [-0.0101, +0.0000] | 98.33% | no | 0.4149 |
| qasper | hybrid | bge-small | fair | 256 | fixed-256 | 0.0585 | -0.0127 | [-0.0228, -0.0068] | 95.00% | yes | 0.0002 |
| qasper | hybrid | bge-small | fair | 256 | section-aware | 0.0421 | -0.0291 | [-0.0431, -0.0197] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 256 | small-to-big | 0.0697 | -0.0016 | [-0.0144, +0.0000] | 99.17% | no | 0.2459 |
| qasper | hybrid | bge-small | fair | 512 | fixed-64 | 0.1029 | -0.0126 | [-0.0259, -0.0043] | 98.33% | yes | 0.0001 |
| qasper | hybrid | bge-small | fair | 512 | fixed-128 | 0.1136 | -0.0020 | [-0.0149, +0.0000] | 98.33% | no | 0.3265 |
| qasper | hybrid | bge-small | fair | 512 | fixed-256 | 0.0989 | -0.0166 | [-0.0319, -0.0060] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 512 | fixed-512 | 0.0815 | -0.0341 | [-0.0498, -0.0224] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 512 | section-aware | 0.1093 | -0.0063 | [-0.0218, +0.0000] | 98.75% | no | 0.0848 |
| qasper | hybrid | bge-small | fair | 512 | small-to-big | 0.1156 | +0.0000 | [-0.0129, +0.0000] | 99.17% | no | 0.5886 |
| qasper | hybrid | bge-small | fair | 1024 | fixed-64 | 0.1438 | -0.0321 | [-0.0461, -0.0231] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 1024 | fixed-128 | 0.1600 | -0.0159 | [-0.0297, -0.0068] | 95.00% | yes | 0.0003 |
| qasper | hybrid | bge-small | fair | 1024 | fixed-256 | 0.1497 | -0.0262 | [-0.0401, -0.0171] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 1024 | fixed-512 | 0.1299 | -0.0460 | [-0.0613, -0.0358] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 1024 | section-aware | 0.1759 | +0.0000 | [-0.0121, +0.0000] | 95.00% | no | 0.5470 |
| qasper | hybrid | bge-small | fair | 1024 | small-to-big | 0.1752 | -0.0007 | [-0.0131, +0.0000] | 95.00% | no | 0.4527 |
| qasper | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0994 | -0.0765 | [-0.0933, -0.0643] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 2048 | fixed-64 | 0.1886 | -0.0527 | [-0.0711, -0.0379] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 2048 | fixed-128 | 0.2105 | -0.0308 | [-0.0490, -0.0164] | 99.17% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 2048 | fixed-256 | 0.2107 | -0.0305 | [-0.0473, -0.0172] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 2048 | fixed-512 | 0.1875 | -0.0538 | [-0.0720, -0.0393] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 2048 | section-aware | 0.2413 | +0.0000 | [-0.0122, +0.0000] | 98.75% | no | 0.6833 |
| qasper | hybrid | bge-small | fair | 2048 | small-to-big | 0.2384 | -0.0028 | [-0.0182, +0.0000] | 99.17% | no | 0.3167 |
| qasper | hybrid | bge-small | fair | 2048 | fixed-1024 | 0.1447 | -0.0965 | [-0.1177, -0.0786] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 4096 | fixed-64 | 0.2314 | -0.0659 | [-0.0850, -0.0494] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 4096 | fixed-128 | 0.2656 | -0.0317 | [-0.0491, -0.0170] | 99.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 4096 | fixed-256 | 0.2685 | -0.0287 | [-0.0443, -0.0159] | 98.33% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 4096 | fixed-512 | 0.2528 | -0.0445 | [-0.0619, -0.0298] | 97.50% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 4096 | section-aware | 0.2973 | +0.0000 | [-0.0120, +0.0000] | 98.75% | no | 0.6903 |
| qasper | hybrid | bge-small | fair | 4096 | small-to-big | 0.2943 | -0.0030 | [-0.0184, +0.0000] | 99.17% | no | 0.3097 |
| qasper | hybrid | bge-small | fair | 4096 | fixed-1024 | 0.2044 | -0.0929 | [-0.1133, -0.0750] | 97.50% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 8192 | fixed-64 | 0.2765 | -0.0871 | [-0.1070, -0.0701] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 8192 | fixed-128 | 0.3168 | -0.0468 | [-0.0640, -0.0321] | 98.75% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 8192 | fixed-256 | 0.3266 | -0.0370 | [-0.0518, -0.0247] | 97.50% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 8192 | fixed-512 | 0.3084 | -0.0552 | [-0.0711, -0.0421] | 95.00% | yes | 0.0000 |
| qasper | hybrid | bge-small | fair | 8192 | section-aware | 0.3636 | +0.0000 | [-0.0120, +0.0000] | 98.75% | no | 0.6772 |
| qasper | hybrid | bge-small | fair | 8192 | small-to-big | 0.3607 | -0.0028 | [-0.0187, +0.0000] | 99.17% | no | 0.3228 |
| qasper | hybrid | bge-small | fair | 8192 | fixed-1024 | 0.2737 | -0.0899 | [-0.1092, -0.0733] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 128 | fixed-64 | 0.0451 | -0.0079 | [-0.0153, -0.0009] | 95.00% | yes | 0.0116 |
| qasper | hybrid | nomic | production | 128 | fixed-128 | 0.0457 | -0.0072 | [-0.0158, +0.0000] | 98.33% | no | 0.0177 |
| qasper | hybrid | nomic | production | 128 | section-aware | 0.0199 | -0.0331 | [-0.0449, -0.0222] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 128 | small-to-big | 0.0530 | +0.0000 | [-0.0025, +0.0000] | 99.00% | no | 0.9707 |
| qasper | hybrid | nomic | production | 256 | fixed-64 | 0.0720 | -0.0083 | [-0.0182, -0.0005] | 97.50% | yes | 0.0090 |
| qasper | hybrid | nomic | production | 256 | fixed-128 | 0.0772 | -0.0032 | [-0.0137, +0.0000] | 98.33% | no | 0.2333 |
| qasper | hybrid | nomic | production | 256 | fixed-256 | 0.0630 | -0.0173 | [-0.0304, -0.0066] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 256 | section-aware | 0.0416 | -0.0388 | [-0.0525, -0.0266] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 256 | small-to-big | 0.0804 | +0.0000 | [-0.0084, +0.0000] | 99.00% | no | 0.7577 |
| qasper | hybrid | nomic | production | 512 | fixed-64 | 0.1075 | -0.0173 | [-0.0327, -0.0076] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 512 | fixed-128 | 0.1248 | +0.0000 | [-0.0133, +0.0000] | 98.33% | no | 0.5522 |
| qasper | hybrid | nomic | production | 512 | fixed-256 | 0.1043 | -0.0205 | [-0.0354, -0.0106] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 512 | fixed-512 | 0.0864 | -0.0384 | [-0.0564, -0.0255] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 512 | section-aware | 0.1104 | -0.0145 | [-0.0309, -0.0017] | 98.33% | yes | 0.0037 |
| qasper | hybrid | nomic | production | 512 | small-to-big | 0.1241 | -0.0007 | [-0.0156, +0.0000] | 99.00% | no | 0.4441 |
| qasper | hybrid | nomic | production | 1024 | fixed-64 | 0.1075 | -0.0745 | [-0.0879, -0.0634] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 1024 | fixed-128 | 0.1729 | -0.0091 | [-0.0207, +0.0000] | 95.00% | no | 0.0351 |
| qasper | hybrid | nomic | production | 1024 | fixed-256 | 0.1549 | -0.0271 | [-0.0399, -0.0168] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 1024 | fixed-512 | 0.1347 | -0.0473 | [-0.0619, -0.0348] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 1024 | section-aware | 0.1768 | -0.0052 | [-0.0182, +0.0000] | 95.00% | no | 0.2081 |
| qasper | hybrid | nomic | production | 1024 | small-to-big | 0.1820 | +0.0000 | [-0.0083, +0.0000] | 95.00% | no | 0.7568 |
| qasper | hybrid | nomic | production | 1024 | fixed-1024 | 0.1036 | -0.0784 | [-0.0945, -0.0652] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 2048 | fixed-64 | 0.1075 | -0.1318 | [-0.1526, -0.1152] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 2048 | fixed-128 | 0.1729 | -0.0665 | [-0.0839, -0.0524] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 2048 | fixed-256 | 0.2126 | -0.0268 | [-0.0427, -0.0142] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 2048 | fixed-512 | 0.1918 | -0.0476 | [-0.0658, -0.0324] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 2048 | section-aware | 0.2369 | -0.0025 | [-0.0165, +0.0000] | 97.50% | no | 0.3457 |
| qasper | hybrid | nomic | production | 2048 | small-to-big | 0.2394 | +0.0000 | [-0.0131, +0.0000] | 99.00% | no | 0.6543 |
| qasper | hybrid | nomic | production | 2048 | fixed-1024 | 0.1584 | -0.0810 | [-0.1016, -0.0634] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 4096 | fixed-64 | 0.1075 | -0.1501 | [-0.1707, -0.1334] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 4096 | fixed-128 | 0.1729 | -0.0847 | [-0.1017, -0.0712] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 4096 | fixed-256 | 0.2126 | -0.0450 | [-0.0594, -0.0340] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 4096 | fixed-512 | 0.2527 | -0.0049 | [-0.0189, +0.0000] | 95.00% | no | 0.2294 |
| qasper | hybrid | nomic | production | 4096 | section-aware | 0.2479 | -0.0097 | [-0.0238, +0.0000] | 97.50% | no | 0.0273 |
| qasper | hybrid | nomic | production | 4096 | small-to-big | 0.2576 | +0.0000 | [-0.0130, +0.0000] | 99.00% | no | 0.7433 |
| qasper | hybrid | nomic | production | 4096 | fixed-1024 | 0.2213 | -0.0363 | [-0.0556, -0.0209] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | fixed-64 | 0.1075 | -0.1743 | [-0.1959, -0.1531] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | fixed-128 | 0.1729 | -0.1089 | [-0.1301, -0.0888] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | fixed-256 | 0.2126 | -0.0692 | [-0.0849, -0.0536] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | fixed-512 | 0.2527 | -0.0291 | [-0.0432, -0.0146] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | section-aware | 0.2479 | -0.0339 | [-0.0545, -0.0122] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | production | 8192 | small-to-big | 0.2576 | -0.0242 | [-0.0472, -0.0017] | 99.17% | yes | 0.0024 |
| qasper | hybrid | nomic | production | 8192 | fixed-1024 | 0.2818 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9976 |
| qasper | hybrid | nomic | fair | 128 | fixed-64 | 0.0451 | -0.0079 | [-0.0153, -0.0009] | 95.00% | yes | 0.0116 |
| qasper | hybrid | nomic | fair | 128 | fixed-128 | 0.0457 | -0.0072 | [-0.0158, +0.0000] | 98.33% | no | 0.0177 |
| qasper | hybrid | nomic | fair | 128 | section-aware | 0.0199 | -0.0331 | [-0.0449, -0.0222] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 128 | small-to-big | 0.0530 | +0.0000 | [-0.0026, +0.0000] | 99.17% | no | 0.9707 |
| qasper | hybrid | nomic | fair | 256 | fixed-64 | 0.0720 | -0.0083 | [-0.0182, -0.0005] | 97.50% | yes | 0.0090 |
| qasper | hybrid | nomic | fair | 256 | fixed-128 | 0.0772 | -0.0032 | [-0.0137, +0.0000] | 98.33% | no | 0.2333 |
| qasper | hybrid | nomic | fair | 256 | fixed-256 | 0.0630 | -0.0173 | [-0.0304, -0.0066] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 256 | section-aware | 0.0416 | -0.0388 | [-0.0525, -0.0266] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 256 | small-to-big | 0.0804 | +0.0000 | [-0.0085, +0.0000] | 99.17% | no | 0.7577 |
| qasper | hybrid | nomic | fair | 512 | fixed-64 | 0.1075 | -0.0173 | [-0.0327, -0.0076] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 512 | fixed-128 | 0.1248 | +0.0000 | [-0.0133, +0.0000] | 98.33% | no | 0.5522 |
| qasper | hybrid | nomic | fair | 512 | fixed-256 | 0.1043 | -0.0205 | [-0.0354, -0.0106] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 512 | fixed-512 | 0.0864 | -0.0384 | [-0.0564, -0.0255] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 512 | section-aware | 0.1104 | -0.0145 | [-0.0315, -0.0010] | 98.75% | yes | 0.0037 |
| qasper | hybrid | nomic | fair | 512 | small-to-big | 0.1241 | -0.0007 | [-0.0159, +0.0000] | 99.17% | no | 0.4441 |
| qasper | hybrid | nomic | fair | 1024 | fixed-64 | 0.1473 | -0.0347 | [-0.0476, -0.0248] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 1024 | fixed-128 | 0.1731 | -0.0089 | [-0.0207, +0.0000] | 95.00% | no | 0.0342 |
| qasper | hybrid | nomic | fair | 1024 | fixed-256 | 0.1549 | -0.0271 | [-0.0401, -0.0170] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 1024 | fixed-512 | 0.1347 | -0.0473 | [-0.0620, -0.0350] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 1024 | section-aware | 0.1777 | -0.0043 | [-0.0173, +0.0000] | 95.00% | no | 0.2521 |
| qasper | hybrid | nomic | fair | 1024 | small-to-big | 0.1820 | +0.0000 | [-0.0092, +0.0000] | 95.00% | no | 0.7137 |
| qasper | hybrid | nomic | fair | 1024 | fixed-1024 | 0.1036 | -0.0784 | [-0.0946, -0.0656] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 2048 | fixed-64 | 0.1910 | -0.0526 | [-0.0718, -0.0383] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 2048 | fixed-128 | 0.2205 | -0.0231 | [-0.0406, -0.0107] | 99.17% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 2048 | fixed-256 | 0.2129 | -0.0307 | [-0.0475, -0.0183] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 2048 | fixed-512 | 0.1918 | -0.0518 | [-0.0708, -0.0371] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 2048 | section-aware | 0.2436 | +0.0000 | [-0.0137, +0.0000] | 98.33% | no | 0.5671 |
| qasper | hybrid | nomic | fair | 2048 | small-to-big | 0.2425 | -0.0011 | [-0.0174, +0.0000] | 99.17% | no | 0.4329 |
| qasper | hybrid | nomic | fair | 2048 | fixed-1024 | 0.1584 | -0.0852 | [-0.1063, -0.0681] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 4096 | fixed-64 | 0.2387 | -0.0688 | [-0.0871, -0.0526] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 4096 | fixed-128 | 0.2703 | -0.0372 | [-0.0553, -0.0221] | 99.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 4096 | fixed-256 | 0.2739 | -0.0336 | [-0.0488, -0.0212] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 4096 | fixed-512 | 0.2551 | -0.0525 | [-0.0695, -0.0377] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 4096 | section-aware | 0.3076 | +0.0000 | [-0.0112, +0.0000] | 98.33% | no | 0.7325 |
| qasper | hybrid | nomic | fair | 4096 | small-to-big | 0.3036 | -0.0040 | [-0.0206, +0.0000] | 99.17% | no | 0.2675 |
| qasper | hybrid | nomic | fair | 4096 | fixed-1024 | 0.2213 | -0.0862 | [-0.1067, -0.0686] | 97.50% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 8192 | fixed-64 | 0.2862 | -0.0799 | [-0.0995, -0.0650] | 98.33% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 8192 | fixed-128 | 0.3286 | -0.0376 | [-0.0556, -0.0246] | 98.75% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 8192 | fixed-256 | 0.3283 | -0.0378 | [-0.0516, -0.0288] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 8192 | fixed-512 | 0.3131 | -0.0531 | [-0.0702, -0.0407] | 95.00% | yes | 0.0000 |
| qasper | hybrid | nomic | fair | 8192 | section-aware | 0.3660 | -0.0002 | [-0.0148, +0.0000] | 98.33% | no | 0.4991 |
| qasper | hybrid | nomic | fair | 8192 | small-to-big | 0.3662 | +0.0000 | [-0.0154, +0.0000] | 99.17% | no | 0.5009 |
| qasper | hybrid | nomic | fair | 8192 | fixed-1024 | 0.2922 | -0.0739 | [-0.0928, -0.0599] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 128 | fixed-64 | 0.0389 | -0.0005 | [-0.0092, +0.0000] | 98.33% | no | 0.4345 |
| qasper | vector | bge-small | production | 128 | fixed-128 | 0.0349 | -0.0046 | [-0.0135, +0.0000] | 98.33% | no | 0.0282 |
| qasper | vector | bge-small | production | 128 | section-aware | 0.0193 | -0.0202 | [-0.0315, -0.0116] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | production | 128 | small-to-big | 0.0394 | +0.0000 | [-0.0088, +0.0000] | 99.17% | no | 0.5373 |
| qasper | vector | bge-small | production | 256 | fixed-64 | 0.0611 | +0.0000 | [-0.0078, +0.0000] | 98.33% | no | 0.5934 |
| qasper | vector | bge-small | production | 256 | fixed-128 | 0.0586 | -0.0026 | [-0.0115, +0.0000] | 98.33% | no | 0.1715 |
| qasper | vector | bge-small | production | 256 | fixed-256 | 0.0498 | -0.0113 | [-0.0199, -0.0049] | 95.00% | yes | 0.0006 |
| qasper | vector | bge-small | production | 256 | section-aware | 0.0347 | -0.0265 | [-0.0387, -0.0170] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 256 | small-to-big | 0.0588 | -0.0023 | [-0.0134, +0.0000] | 99.17% | no | 0.2345 |
| qasper | vector | bge-small | production | 512 | fixed-64 | 0.0864 | -0.0021 | [-0.0158, +0.0000] | 98.33% | no | 0.1893 |
| qasper | vector | bge-small | production | 512 | fixed-128 | 0.0853 | -0.0032 | [-0.0172, +0.0000] | 98.33% | no | 0.1296 |
| qasper | vector | bge-small | production | 512 | fixed-256 | 0.0741 | -0.0144 | [-0.0292, -0.0053] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 512 | fixed-512 | 0.0613 | -0.0272 | [-0.0435, -0.0166] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | production | 512 | section-aware | 0.0885 | +0.0000 | [-0.0134, +0.0000] | 98.75% | no | 0.4594 |
| qasper | vector | bge-small | production | 512 | small-to-big | 0.0864 | -0.0021 | [-0.0171, +0.0000] | 99.17% | no | 0.2217 |
| qasper | vector | bge-small | production | 1024 | fixed-64 | 0.0864 | -0.0523 | [-0.0646, -0.0412] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 1024 | fixed-128 | 0.1217 | -0.0171 | [-0.0290, -0.0065] | 95.00% | yes | 0.0016 |
| qasper | vector | bge-small | production | 1024 | fixed-256 | 0.1082 | -0.0306 | [-0.0429, -0.0191] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 1024 | fixed-512 | 0.0931 | -0.0457 | [-0.0591, -0.0338] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 1024 | section-aware | 0.1315 | -0.0072 | [-0.0192, +0.0000] | 95.00% | no | 0.1106 |
| qasper | vector | bge-small | production | 1024 | small-to-big | 0.1388 | +0.0000 | [-0.0047, +0.0000] | 95.00% | no | 0.8878 |
| qasper | vector | bge-small | production | 1024 | fixed-1024 | 0.0673 | -0.0714 | [-0.0858, -0.0583] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 2048 | fixed-64 | 0.0864 | -0.0904 | [-0.1098, -0.0743] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | production | 2048 | fixed-128 | 0.1217 | -0.0552 | [-0.0722, -0.0405] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | production | 2048 | fixed-256 | 0.1499 | -0.0269 | [-0.0429, -0.0129] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | production | 2048 | fixed-512 | 0.1365 | -0.0403 | [-0.0577, -0.0265] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | production | 2048 | section-aware | 0.1729 | -0.0039 | [-0.0189, +0.0000] | 98.75% | no | 0.2560 |
| qasper | vector | bge-small | production | 2048 | small-to-big | 0.1768 | +0.0000 | [-0.0121, +0.0000] | 99.17% | no | 0.7440 |
| qasper | vector | bge-small | production | 2048 | fixed-1024 | 0.0969 | -0.0799 | [-0.0986, -0.0641] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | production | 4096 | fixed-64 | 0.0864 | -0.1009 | [-0.1200, -0.0837] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 4096 | fixed-128 | 0.1217 | -0.0656 | [-0.0830, -0.0505] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | production | 4096 | fixed-256 | 0.1499 | -0.0374 | [-0.0535, -0.0230] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | production | 4096 | fixed-512 | 0.1749 | -0.0124 | [-0.0293, +0.0000] | 97.50% | no | 0.0393 |
| qasper | vector | bge-small | production | 4096 | section-aware | 0.1779 | -0.0094 | [-0.0246, +0.0000] | 98.75% | no | 0.0583 |
| qasper | vector | bge-small | production | 4096 | small-to-big | 0.1873 | +0.0000 | [-0.0084, +0.0000] | 99.17% | no | 0.9024 |
| qasper | vector | bge-small | production | 4096 | fixed-1024 | 0.1364 | -0.0509 | [-0.0687, -0.0349] | 97.50% | yes | 0.0000 |
| qasper | vector | bge-small | production | 8192 | fixed-64 | 0.0864 | -0.1009 | [-0.1193, -0.0844] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | production | 8192 | fixed-128 | 0.1217 | -0.0656 | [-0.0827, -0.0509] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | production | 8192 | fixed-256 | 0.1499 | -0.0374 | [-0.0526, -0.0239] | 97.50% | yes | 0.0000 |
| qasper | vector | bge-small | production | 8192 | fixed-512 | 0.1749 | -0.0124 | [-0.0293, +0.0000] | 97.50% | no | 0.0369 |
| qasper | vector | bge-small | production | 8192 | section-aware | 0.1779 | -0.0094 | [-0.0246, +0.0000] | 98.75% | no | 0.0574 |
| qasper | vector | bge-small | production | 8192 | small-to-big | 0.1873 | +0.0000 | [-0.0084, +0.0000] | 99.17% | no | 0.8963 |
| qasper | vector | bge-small | production | 8192 | fixed-1024 | 0.1690 | -0.0183 | [-0.0349, -0.0030] | 95.00% | yes | 0.0094 |
| qasper | vector | bge-small | fair | 128 | fixed-64 | 0.0389 | -0.0005 | [-0.0092, +0.0000] | 98.33% | no | 0.4345 |
| qasper | vector | bge-small | fair | 128 | fixed-128 | 0.0349 | -0.0046 | [-0.0135, +0.0000] | 98.33% | no | 0.0282 |
| qasper | vector | bge-small | fair | 128 | section-aware | 0.0193 | -0.0202 | [-0.0315, -0.0116] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 128 | small-to-big | 0.0394 | +0.0000 | [-0.0088, +0.0000] | 99.17% | no | 0.5373 |
| qasper | vector | bge-small | fair | 256 | fixed-64 | 0.0611 | +0.0000 | [-0.0078, +0.0000] | 98.33% | no | 0.5934 |
| qasper | vector | bge-small | fair | 256 | fixed-128 | 0.0586 | -0.0026 | [-0.0115, +0.0000] | 98.33% | no | 0.1715 |
| qasper | vector | bge-small | fair | 256 | fixed-256 | 0.0498 | -0.0113 | [-0.0199, -0.0049] | 95.00% | yes | 0.0006 |
| qasper | vector | bge-small | fair | 256 | section-aware | 0.0347 | -0.0265 | [-0.0387, -0.0170] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 256 | small-to-big | 0.0588 | -0.0023 | [-0.0134, +0.0000] | 99.17% | no | 0.2345 |
| qasper | vector | bge-small | fair | 512 | fixed-64 | 0.0866 | -0.0019 | [-0.0156, +0.0000] | 98.33% | no | 0.1956 |
| qasper | vector | bge-small | fair | 512 | fixed-128 | 0.0856 | -0.0029 | [-0.0170, +0.0000] | 98.33% | no | 0.1400 |
| qasper | vector | bge-small | fair | 512 | fixed-256 | 0.0741 | -0.0144 | [-0.0292, -0.0055] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 512 | fixed-512 | 0.0613 | -0.0272 | [-0.0436, -0.0169] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 512 | section-aware | 0.0885 | +0.0000 | [-0.0136, +0.0000] | 98.75% | no | 0.4511 |
| qasper | vector | bge-small | fair | 512 | small-to-big | 0.0864 | -0.0021 | [-0.0172, +0.0000] | 99.17% | no | 0.2133 |
| qasper | vector | bge-small | fair | 1024 | fixed-64 | 0.1167 | -0.0228 | [-0.0344, -0.0125] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 1024 | fixed-128 | 0.1226 | -0.0169 | [-0.0291, -0.0065] | 95.00% | yes | 0.0012 |
| qasper | vector | bge-small | fair | 1024 | fixed-256 | 0.1082 | -0.0314 | [-0.0438, -0.0203] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 1024 | fixed-512 | 0.0931 | -0.0465 | [-0.0599, -0.0350] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 1024 | section-aware | 0.1343 | -0.0052 | [-0.0170, +0.0000] | 95.00% | no | 0.1912 |
| qasper | vector | bge-small | fair | 1024 | small-to-big | 0.1395 | +0.0000 | [-0.0067, +0.0000] | 95.00% | no | 0.8076 |
| qasper | vector | bge-small | fair | 1024 | fixed-1024 | 0.0673 | -0.0722 | [-0.0867, -0.0596] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 2048 | fixed-64 | 0.1511 | -0.0343 | [-0.0526, -0.0202] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 2048 | fixed-128 | 0.1625 | -0.0229 | [-0.0414, -0.0086] | 99.17% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 2048 | fixed-256 | 0.1518 | -0.0337 | [-0.0506, -0.0207] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 2048 | fixed-512 | 0.1365 | -0.0489 | [-0.0661, -0.0355] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 2048 | section-aware | 0.1854 | +0.0000 | [-0.0136, +0.0000] | 98.75% | no | 0.6265 |
| qasper | vector | bge-small | fair | 2048 | small-to-big | 0.1831 | -0.0023 | [-0.0193, +0.0000] | 99.17% | no | 0.3735 |
| qasper | vector | bge-small | fair | 2048 | fixed-1024 | 0.0969 | -0.0885 | [-0.1079, -0.0731] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 4096 | fixed-64 | 0.1859 | -0.0541 | [-0.0726, -0.0366] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 4096 | fixed-128 | 0.2042 | -0.0357 | [-0.0544, -0.0178] | 99.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 4096 | fixed-256 | 0.1974 | -0.0425 | [-0.0591, -0.0273] | 98.33% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 4096 | fixed-512 | 0.1766 | -0.0634 | [-0.0793, -0.0480] | 97.50% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 4096 | section-aware | 0.2399 | +0.0000 | [-0.0071, +0.0000] | 98.75% | no | 0.9303 |
| qasper | vector | bge-small | fair | 4096 | small-to-big | 0.2300 | -0.0100 | [-0.0276, +0.0000] | 99.17% | no | 0.0697 |
| qasper | vector | bge-small | fair | 4096 | fixed-1024 | 0.1364 | -0.1036 | [-0.1219, -0.0859] | 97.50% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 8192 | fixed-64 | 0.2263 | -0.0624 | [-0.0811, -0.0473] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 8192 | fixed-128 | 0.2485 | -0.0402 | [-0.0586, -0.0260] | 98.75% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 8192 | fixed-256 | 0.2478 | -0.0408 | [-0.0566, -0.0286] | 97.50% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 8192 | fixed-512 | 0.2183 | -0.0703 | [-0.0859, -0.0584] | 95.00% | yes | 0.0000 |
| qasper | vector | bge-small | fair | 8192 | section-aware | 0.2887 | +0.0000 | [-0.0140, +0.0000] | 98.75% | no | 0.6569 |
| qasper | vector | bge-small | fair | 8192 | small-to-big | 0.2859 | -0.0028 | [-0.0206, +0.0000] | 99.17% | no | 0.3431 |
| qasper | vector | bge-small | fair | 8192 | fixed-1024 | 0.1721 | -0.1166 | [-0.1347, -0.1021] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 128 | fixed-64 | 0.0454 | -0.0077 | [-0.0165, +0.0000] | 97.50% | no | 0.0192 |
| qasper | vector | nomic | production | 128 | fixed-128 | 0.0452 | -0.0080 | [-0.0173, +0.0000] | 98.33% | no | 0.0169 |
| qasper | vector | nomic | production | 128 | section-aware | 0.0215 | -0.0316 | [-0.0446, -0.0194] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | production | 128 | small-to-big | 0.0531 | +0.0000 | [-0.0031, +0.0000] | 99.17% | no | 0.9639 |
| qasper | vector | nomic | production | 256 | fixed-64 | 0.0670 | -0.0085 | [-0.0185, +0.0000] | 97.50% | no | 0.0181 |
| qasper | vector | nomic | production | 256 | fixed-128 | 0.0689 | -0.0067 | [-0.0173, +0.0000] | 98.33% | no | 0.0584 |
| qasper | vector | nomic | production | 256 | fixed-256 | 0.0553 | -0.0203 | [-0.0332, -0.0087] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 256 | section-aware | 0.0407 | -0.0348 | [-0.0491, -0.0221] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 256 | small-to-big | 0.0756 | +0.0000 | [-0.0052, +0.0000] | 99.17% | no | 0.9235 |
| qasper | vector | nomic | production | 512 | fixed-64 | 0.0967 | -0.0173 | [-0.0321, -0.0036] | 98.33% | yes | 0.0009 |
| qasper | vector | nomic | production | 512 | fixed-128 | 0.1013 | -0.0128 | [-0.0267, +0.0000] | 98.33% | no | 0.0104 |
| qasper | vector | nomic | production | 512 | fixed-256 | 0.0829 | -0.0311 | [-0.0466, -0.0168] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | production | 512 | fixed-512 | 0.0591 | -0.0549 | [-0.0731, -0.0384] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | production | 512 | section-aware | 0.0996 | -0.0144 | [-0.0271, -0.0018] | 95.00% | yes | 0.0130 |
| qasper | vector | nomic | production | 512 | small-to-big | 0.1140 | +0.0000 | [-0.0033, +0.0000] | 99.17% | no | 0.9757 |
| qasper | vector | nomic | production | 1024 | fixed-64 | 0.0967 | -0.0658 | [-0.0795, -0.0529] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 1024 | fixed-128 | 0.1450 | -0.0175 | [-0.0294, -0.0058] | 95.00% | yes | 0.0008 |
| qasper | vector | nomic | production | 1024 | fixed-256 | 0.1208 | -0.0417 | [-0.0545, -0.0292] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 1024 | fixed-512 | 0.1059 | -0.0566 | [-0.0718, -0.0420] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 1024 | section-aware | 0.1467 | -0.0158 | [-0.0286, -0.0032] | 95.00% | yes | 0.0074 |
| qasper | vector | nomic | production | 1024 | small-to-big | 0.1625 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9918 |
| qasper | vector | nomic | production | 1024 | fixed-1024 | 0.0653 | -0.0972 | [-0.1139, -0.0814] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 2048 | fixed-64 | 0.0967 | -0.1154 | [-0.1359, -0.0964] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | production | 2048 | fixed-128 | 0.1450 | -0.0671 | [-0.0839, -0.0509] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | production | 2048 | fixed-256 | 0.1669 | -0.0452 | [-0.0612, -0.0299] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | production | 2048 | fixed-512 | 0.1374 | -0.0747 | [-0.0933, -0.0569] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | production | 2048 | section-aware | 0.1913 | -0.0208 | [-0.0351, -0.0067] | 97.50% | yes | 0.0006 |
| qasper | vector | nomic | production | 2048 | small-to-big | 0.2121 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9994 |
| qasper | vector | nomic | production | 2048 | fixed-1024 | 0.1104 | -0.1017 | [-0.1217, -0.0826] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | fixed-64 | 0.0967 | -0.1282 | [-0.1488, -0.1092] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | fixed-128 | 0.1450 | -0.0799 | [-0.0965, -0.0636] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | fixed-256 | 0.1669 | -0.0580 | [-0.0728, -0.0436] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | fixed-512 | 0.1861 | -0.0388 | [-0.0559, -0.0220] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | section-aware | 0.1968 | -0.0282 | [-0.0436, -0.0125] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | production | 4096 | small-to-big | 0.2249 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| qasper | vector | nomic | production | 4096 | fixed-1024 | 0.1597 | -0.0653 | [-0.0846, -0.0466] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | fixed-64 | 0.0967 | -0.1282 | [-0.1480, -0.1097] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | fixed-128 | 0.1450 | -0.0799 | [-0.0960, -0.0641] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | fixed-256 | 0.1669 | -0.0580 | [-0.0710, -0.0454] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | fixed-512 | 0.1861 | -0.0388 | [-0.0535, -0.0241] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | section-aware | 0.1968 | -0.0282 | [-0.0429, -0.0130] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | production | 8192 | small-to-big | 0.2249 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| qasper | vector | nomic | production | 8192 | fixed-1024 | 0.1896 | -0.0353 | [-0.0520, -0.0188] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 128 | fixed-64 | 0.0454 | -0.0077 | [-0.0165, +0.0000] | 97.50% | no | 0.0192 |
| qasper | vector | nomic | fair | 128 | fixed-128 | 0.0452 | -0.0080 | [-0.0173, +0.0000] | 98.33% | no | 0.0169 |
| qasper | vector | nomic | fair | 128 | section-aware | 0.0215 | -0.0316 | [-0.0446, -0.0194] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | fair | 128 | small-to-big | 0.0531 | +0.0000 | [-0.0031, +0.0000] | 99.17% | no | 0.9639 |
| qasper | vector | nomic | fair | 256 | fixed-64 | 0.0670 | -0.0085 | [-0.0185, +0.0000] | 97.50% | no | 0.0181 |
| qasper | vector | nomic | fair | 256 | fixed-128 | 0.0689 | -0.0067 | [-0.0173, +0.0000] | 98.33% | no | 0.0584 |
| qasper | vector | nomic | fair | 256 | fixed-256 | 0.0553 | -0.0203 | [-0.0332, -0.0087] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 256 | section-aware | 0.0407 | -0.0348 | [-0.0491, -0.0221] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 256 | small-to-big | 0.0756 | +0.0000 | [-0.0052, +0.0000] | 99.17% | no | 0.9235 |
| qasper | vector | nomic | fair | 512 | fixed-64 | 0.0967 | -0.0173 | [-0.0321, -0.0036] | 98.33% | yes | 0.0009 |
| qasper | vector | nomic | fair | 512 | fixed-128 | 0.1013 | -0.0128 | [-0.0267, +0.0000] | 98.33% | no | 0.0104 |
| qasper | vector | nomic | fair | 512 | fixed-256 | 0.0829 | -0.0311 | [-0.0466, -0.0168] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | fair | 512 | fixed-512 | 0.0591 | -0.0549 | [-0.0731, -0.0384] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | fair | 512 | section-aware | 0.0996 | -0.0144 | [-0.0307, +0.0000] | 98.75% | no | 0.0130 |
| qasper | vector | nomic | fair | 512 | small-to-big | 0.1140 | +0.0000 | [-0.0033, +0.0000] | 99.17% | no | 0.9757 |
| qasper | vector | nomic | fair | 1024 | fixed-64 | 0.1308 | -0.0318 | [-0.0445, -0.0195] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 1024 | fixed-128 | 0.1450 | -0.0176 | [-0.0294, -0.0058] | 95.00% | yes | 0.0006 |
| qasper | vector | nomic | fair | 1024 | fixed-256 | 0.1208 | -0.0417 | [-0.0546, -0.0292] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 1024 | fixed-512 | 0.1059 | -0.0567 | [-0.0719, -0.0420] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 1024 | section-aware | 0.1472 | -0.0154 | [-0.0279, -0.0028] | 95.00% | yes | 0.0082 |
| qasper | vector | nomic | fair | 1024 | small-to-big | 0.1626 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9912 |
| qasper | vector | nomic | fair | 1024 | fixed-1024 | 0.0653 | -0.0973 | [-0.1139, -0.0814] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 2048 | fixed-64 | 0.1699 | -0.0437 | [-0.0617, -0.0275] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | fair | 2048 | fixed-128 | 0.1928 | -0.0209 | [-0.0372, -0.0056] | 99.17% | yes | 0.0000 |
| qasper | vector | nomic | fair | 2048 | fixed-256 | 0.1670 | -0.0466 | [-0.0627, -0.0323] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | fair | 2048 | fixed-512 | 0.1374 | -0.0762 | [-0.0947, -0.0595] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | fair | 2048 | section-aware | 0.2045 | -0.0091 | [-0.0250, +0.0000] | 98.75% | no | 0.0753 |
| qasper | vector | nomic | fair | 2048 | small-to-big | 0.2136 | +0.0000 | [-0.0078, +0.0000] | 99.17% | no | 0.9247 |
| qasper | vector | nomic | fair | 2048 | fixed-1024 | 0.1104 | -0.1032 | [-0.1231, -0.0849] | 98.33% | yes | 0.0000 |
| qasper | vector | nomic | fair | 4096 | fixed-64 | 0.2065 | -0.0530 | [-0.0711, -0.0375] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 4096 | fixed-128 | 0.2328 | -0.0267 | [-0.0440, -0.0120] | 99.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 4096 | fixed-256 | 0.2183 | -0.0412 | [-0.0568, -0.0284] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | fair | 4096 | fixed-512 | 0.1890 | -0.0705 | [-0.0881, -0.0558] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | fair | 4096 | section-aware | 0.2553 | -0.0042 | [-0.0202, +0.0000] | 98.75% | no | 0.2605 |
| qasper | vector | nomic | fair | 4096 | small-to-big | 0.2596 | +0.0000 | [-0.0126, +0.0000] | 99.17% | no | 0.7395 |
| qasper | vector | nomic | fair | 4096 | fixed-1024 | 0.1601 | -0.0994 | [-0.1195, -0.0821] | 97.50% | yes | 0.0000 |
| qasper | vector | nomic | fair | 8192 | fixed-64 | 0.2475 | -0.0682 | [-0.0862, -0.0508] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | fair | 8192 | fixed-128 | 0.2841 | -0.0316 | [-0.0478, -0.0156] | 98.75% | yes | 0.0000 |
| qasper | vector | nomic | fair | 8192 | fixed-256 | 0.2616 | -0.0541 | [-0.0679, -0.0408] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 8192 | fixed-512 | 0.2382 | -0.0775 | [-0.0933, -0.0619] | 95.00% | yes | 0.0000 |
| qasper | vector | nomic | fair | 8192 | section-aware | 0.3037 | -0.0119 | [-0.0290, +0.0000] | 98.75% | no | 0.0409 |
| qasper | vector | nomic | fair | 8192 | small-to-big | 0.3157 | +0.0000 | [-0.0056, +0.0000] | 99.17% | no | 0.9591 |
| qasper | vector | nomic | fair | 8192 | fixed-1024 | 0.2057 | -0.1100 | [-0.1280, -0.0927] | 95.00% | yes | 0.0000 |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).
