# R7 - routing headroom and the router gate

Config hash: `a84d7d256393c9aec6f06c734fa2429ab6913b87bbc0a93e0dd9eeab039728b9`

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
- nq/grid
scope: collection
seed: 0
top_n: 8
```

## Inputs

| run | run config hash |
|---|---|
| qasper/grid | `97bc8de66def0c97a34aaefe87bc535bd43e7b8f2f2320a696721ee5ab74df62` |
| nq/grid | `b9cc99a6120a5b239138af5ab75b41aeb4cbebda4ffa6792299a0066f496cc92` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| nq | 1000 | 500 | 500 | 0 | 1000 |
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `bm25` (embedder -), `hybrid` (embedder bge-small), `hybrid` (embedder nomic), `hybrid-rerank` (embedder bge-small), `hybrid-rerank` (embedder nomic), `vector` (embedder bge-small), `vector` (embedder nomic).

## Router gate (pre-registered)

Rule: build the router in v2 if, on the production line, in the production view, at the primary budget of 1024 tokens, pooled over qasper + nq, either embedder's routing headroom is at least +0.0500 retrieval recall with a 95% CI that excludes 0.

Judged on the production line (`hybrid-rerank`), production view (top-N cap 8), 1024-token budget, 95% CI.
- bge-small, pooled over nq + qasper: routing headroom +0.1295 [+0.1187, +0.1402] over the best single chunking (section-aware), which clears the gate.
- nomic, pooled over nq + qasper: routing headroom +0.1313 [+0.1204, +0.1425] over the best single chunking (section-aware), which clears the gate.
**Verdict: build the router in v2** (bge-small, nomic clear the gate).

### The same test on the other pipelines (for reference, not the gate)

| pipeline | embedder | best single chunking | routing headroom | 95% CI | meets the bar |
|---|---|---|---|---|---|
| bm25 | - | section-aware | +0.1400 | [+0.1288, +0.1515] | yes |
| hybrid | bge-small | section-aware | +0.1420 | [+0.1297, +0.1509] | yes |
| hybrid | nomic | section-aware | +0.1382 | [+0.1267, +0.1474] | yes |
| vector | bge-small | small-to-big | +0.1294 | [+0.1188, +0.1403] | yes |
| vector | nomic | small-to-big | +0.1198 | [+0.1095, +0.1296] | yes |

## Routing headroom

Best single chunking: highest mean retrieval recall at the budget. Oracle router: per question, the chunking with the highest recall (ties to the smaller chunk). Routing headroom: oracle router minus best single chunking; the best single chunking is re-selected inside every resample.

| dataset | pipeline | embedder | view | budget | best single chunking | best single recall | oracle router recall | routing headroom | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.1530 | 0.2348 | +0.0818 | [+0.0722, +0.0919] | 99.17% | yes |
| pooled | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.2308 | 0.3571 | +0.1263 | [+0.1144, +0.1385] | 99.00% | yes |
| pooled | hybrid-rerank | bge-small | production | 512 | small-to-big | 0.3200 | 0.4801 | +0.1601 | [+0.1457, +0.1729] | 98.75% | yes |
| pooled | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.4256 | 0.5552 | +0.1295 | [+0.1187, +0.1402] | 95.00% | yes |
| pooled | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.4923 | 0.5917 | +0.0994 | [+0.0878, +0.1113] | 98.33% | yes |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-512 | 0.5111 | 0.6111 | +0.1000 | [+0.0891, +0.1096] | 97.50% | yes |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.5485 | 0.6186 | +0.0701 | [+0.0620, +0.0781] | 95.00% | yes |
| pooled | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.1530 | 0.2348 | +0.0818 | [+0.0722, +0.0919] | 99.17% | yes |
| pooled | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.2308 | 0.3571 | +0.1263 | [+0.1144, +0.1385] | 99.00% | yes |
| pooled | hybrid-rerank | bge-small | fair | 512 | small-to-big | 0.3200 | 0.4801 | +0.1601 | [+0.1457, +0.1729] | 98.75% | yes |
| pooled | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.4257 | 0.5599 | +0.1341 | [+0.1233, +0.1450] | 95.00% | yes |
| pooled | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.4959 | 0.6026 | +0.1067 | [+0.0949, +0.1188] | 98.33% | yes |
| pooled | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.5339 | 0.6343 | +0.1004 | [+0.0894, +0.1115] | 97.50% | yes |
| pooled | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.5570 | 0.6647 | +0.1077 | [+0.0980, +0.1162] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | production | 128 | small-to-big | 0.1512 | 0.2352 | +0.0840 | [+0.0742, +0.0945] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | production | 256 | small-to-big | 0.2296 | 0.3566 | +0.1271 | [+0.1151, +0.1393] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | production | 512 | small-to-big | 0.3173 | 0.4779 | +0.1606 | [+0.1456, +0.1725] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | production | 1024 | section-aware | 0.4262 | 0.5575 | +0.1313 | [+0.1204, +0.1425] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | production | 2048 | section-aware | 0.4923 | 0.5933 | +0.1010 | [+0.0892, +0.1131] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.5115 | 0.6131 | +0.1015 | [+0.0904, +0.1115] | 97.50% | yes |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.5573 | 0.6239 | +0.0666 | [+0.0587, +0.0744] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.1512 | 0.2352 | +0.0840 | [+0.0742, +0.0945] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.2296 | 0.3566 | +0.1271 | [+0.1151, +0.1393] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.3173 | 0.4779 | +0.1606 | [+0.1456, +0.1725] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.4269 | 0.5641 | +0.1373 | [+0.1263, +0.1485] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.4956 | 0.6044 | +0.1088 | [+0.0968, +0.1212] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.5334 | 0.6372 | +0.1038 | [+0.0927, +0.1146] | 97.50% | yes |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.5584 | 0.6703 | +0.1119 | [+0.1006, +0.1181] | 95.00% | yes |
| pooled | bm25 | - | production | 128 | small-to-big | 0.0838 | 0.1411 | +0.0574 | [+0.0485, +0.0649] | 99.17% | yes |
| pooled | bm25 | - | production | 256 | small-to-big | 0.1289 | 0.2375 | +0.1086 | [+0.0964, +0.1187] | 99.00% | yes |
| pooled | bm25 | - | production | 512 | small-to-big | 0.1943 | 0.3435 | +0.1491 | [+0.1354, +0.1605] | 98.75% | yes |
| pooled | bm25 | - | production | 1024 | section-aware | 0.2896 | 0.4295 | +0.1400 | [+0.1288, +0.1515] | 95.00% | yes |
| pooled | bm25 | - | production | 2048 | section-aware | 0.3769 | 0.4866 | +0.1097 | [+0.0968, +0.1224] | 98.33% | yes |
| pooled | bm25 | - | production | 4096 | fixed-512 | 0.4389 | 0.5219 | +0.0831 | [+0.0731, +0.0928] | 97.50% | yes |
| pooled | bm25 | - | production | 8192 | fixed-1024 | 0.4953 | 0.5407 | +0.0455 | [+0.0387, +0.0523] | 95.00% | yes |
| pooled | bm25 | - | fair | 128 | small-to-big | 0.0838 | 0.1411 | +0.0574 | [+0.0485, +0.0649] | 99.17% | yes |
| pooled | bm25 | - | fair | 256 | small-to-big | 0.1289 | 0.2375 | +0.1086 | [+0.0964, +0.1187] | 99.00% | yes |
| pooled | bm25 | - | fair | 512 | small-to-big | 0.1943 | 0.3435 | +0.1491 | [+0.1354, +0.1605] | 98.75% | yes |
| pooled | bm25 | - | fair | 1024 | section-aware | 0.2896 | 0.4383 | +0.1487 | [+0.1374, +0.1604] | 95.00% | yes |
| pooled | bm25 | - | fair | 2048 | section-aware | 0.3821 | 0.5076 | +0.1255 | [+0.1123, +0.1389] | 98.33% | yes |
| pooled | bm25 | - | fair | 4096 | section-aware | 0.4500 | 0.5671 | +0.1170 | [+0.1052, +0.1285] | 97.50% | yes |
| pooled | bm25 | - | fair | 8192 | section-aware | 0.5104 | 0.6255 | +0.1150 | [+0.1047, +0.1251] | 95.00% | yes |
| pooled | hybrid | bge-small | production | 128 | fixed-128 | 0.1123 | 0.1921 | +0.0797 | [+0.0693, +0.0878] | 99.17% | yes |
| pooled | hybrid | bge-small | production | 256 | small-to-big | 0.1729 | 0.2946 | +0.1216 | [+0.1092, +0.1341] | 99.00% | yes |
| pooled | hybrid | bge-small | production | 512 | small-to-big | 0.2487 | 0.4031 | +0.1545 | [+0.1400, +0.1686] | 98.75% | yes |
| pooled | hybrid | bge-small | production | 1024 | section-aware | 0.3407 | 0.4828 | +0.1420 | [+0.1297, +0.1509] | 95.00% | yes |
| pooled | hybrid | bge-small | production | 2048 | small-to-big | 0.4160 | 0.5276 | +0.1115 | [+0.0993, +0.1230] | 98.33% | yes |
| pooled | hybrid | bge-small | production | 4096 | fixed-512 | 0.4574 | 0.5556 | +0.0982 | [+0.0874, +0.1094] | 97.50% | yes |
| pooled | hybrid | bge-small | production | 8192 | fixed-1024 | 0.4778 | 0.5729 | +0.0951 | [+0.0854, +0.1056] | 95.00% | yes |
| pooled | hybrid | bge-small | fair | 128 | fixed-128 | 0.1123 | 0.1921 | +0.0797 | [+0.0693, +0.0878] | 99.17% | yes |
| pooled | hybrid | bge-small | fair | 256 | small-to-big | 0.1729 | 0.2946 | +0.1216 | [+0.1092, +0.1341] | 99.00% | yes |
| pooled | hybrid | bge-small | fair | 512 | small-to-big | 0.2487 | 0.4031 | +0.1545 | [+0.1400, +0.1686] | 98.75% | yes |
| pooled | hybrid | bge-small | fair | 1024 | section-aware | 0.3411 | 0.4896 | +0.1486 | [+0.1361, +0.1577] | 95.00% | yes |
| pooled | hybrid | bge-small | fair | 2048 | small-to-big | 0.4214 | 0.5501 | +0.1287 | [+0.1150, +0.1390] | 98.33% | yes |
| pooled | hybrid | bge-small | fair | 4096 | section-aware | 0.4898 | 0.6027 | +0.1130 | [+0.1012, +0.1238] | 97.50% | yes |
| pooled | hybrid | bge-small | fair | 8192 | section-aware | 0.5498 | 0.6544 | +0.1046 | [+0.0950, +0.1137] | 95.00% | yes |
| pooled | hybrid | nomic | production | 128 | small-to-big | 0.1188 | 0.1906 | +0.0717 | [+0.0628, +0.0816] | 99.17% | yes |
| pooled | hybrid | nomic | production | 256 | small-to-big | 0.1838 | 0.3015 | +0.1177 | [+0.1060, +0.1299] | 99.00% | yes |
| pooled | hybrid | nomic | production | 512 | small-to-big | 0.2540 | 0.4135 | +0.1594 | [+0.1445, +0.1733] | 98.75% | yes |
| pooled | hybrid | nomic | production | 1024 | section-aware | 0.3498 | 0.4880 | +0.1382 | [+0.1267, +0.1474] | 95.00% | yes |
| pooled | hybrid | nomic | production | 2048 | small-to-big | 0.4258 | 0.5351 | +0.1094 | [+0.0965, +0.1209] | 98.33% | yes |
| pooled | hybrid | nomic | production | 4096 | fixed-512 | 0.4571 | 0.5590 | +0.1020 | [+0.0911, +0.1123] | 97.50% | yes |
| pooled | hybrid | nomic | production | 8192 | fixed-1024 | 0.4897 | 0.5760 | +0.0863 | [+0.0770, +0.0959] | 95.00% | yes |
| pooled | hybrid | nomic | fair | 128 | small-to-big | 0.1188 | 0.1906 | +0.0717 | [+0.0628, +0.0816] | 99.17% | yes |
| pooled | hybrid | nomic | fair | 256 | small-to-big | 0.1838 | 0.3015 | +0.1177 | [+0.1060, +0.1299] | 99.00% | yes |
| pooled | hybrid | nomic | fair | 512 | small-to-big | 0.2540 | 0.4135 | +0.1594 | [+0.1445, +0.1733] | 98.75% | yes |
| pooled | hybrid | nomic | fair | 1024 | section-aware | 0.3504 | 0.4956 | +0.1452 | [+0.1337, +0.1548] | 95.00% | yes |
| pooled | hybrid | nomic | fair | 2048 | small-to-big | 0.4286 | 0.5563 | +0.1277 | [+0.1136, +0.1380] | 98.33% | yes |
| pooled | hybrid | nomic | fair | 4096 | section-aware | 0.4982 | 0.6097 | +0.1115 | [+0.0999, +0.1225] | 97.50% | yes |
| pooled | hybrid | nomic | fair | 8192 | section-aware | 0.5530 | 0.6577 | +0.1047 | [+0.0948, +0.1131] | 95.00% | yes |
| pooled | vector | bge-small | production | 128 | fixed-128 | 0.1182 | 0.2014 | +0.0831 | [+0.0730, +0.0939] | 99.17% | yes |
| pooled | vector | bge-small | production | 256 | fixed-128 | 0.1779 | 0.3019 | +0.1240 | [+0.1120, +0.1359] | 99.00% | yes |
| pooled | vector | bge-small | production | 512 | small-to-big | 0.2400 | 0.4020 | +0.1620 | [+0.1471, +0.1747] | 98.75% | yes |
| pooled | vector | bge-small | production | 1024 | small-to-big | 0.3322 | 0.4615 | +0.1294 | [+0.1188, +0.1403] | 95.00% | yes |
| pooled | vector | bge-small | production | 2048 | small-to-big | 0.3894 | 0.4923 | +0.1029 | [+0.0911, +0.1145] | 98.33% | yes |
| pooled | vector | bge-small | production | 4096 | small-to-big | 0.4039 | 0.5086 | +0.1047 | [+0.0931, +0.1148] | 97.50% | yes |
| pooled | vector | bge-small | production | 8192 | small-to-big | 0.4039 | 0.5195 | +0.1156 | [+0.1048, +0.1240] | 95.00% | yes |
| pooled | vector | bge-small | fair | 128 | fixed-128 | 0.1182 | 0.2014 | +0.0831 | [+0.0730, +0.0939] | 99.17% | yes |
| pooled | vector | bge-small | fair | 256 | fixed-128 | 0.1779 | 0.3019 | +0.1240 | [+0.1120, +0.1359] | 99.00% | yes |
| pooled | vector | bge-small | fair | 512 | small-to-big | 0.2401 | 0.4020 | +0.1620 | [+0.1471, +0.1744] | 98.75% | yes |
| pooled | vector | bge-small | fair | 1024 | small-to-big | 0.3330 | 0.4698 | +0.1369 | [+0.1262, +0.1479] | 95.00% | yes |
| pooled | vector | bge-small | fair | 2048 | small-to-big | 0.3960 | 0.5155 | +0.1195 | [+0.1070, +0.1308] | 98.33% | yes |
| pooled | vector | bge-small | fair | 4096 | small-to-big | 0.4468 | 0.5594 | +0.1126 | [+0.1002, +0.1212] | 97.50% | yes |
| pooled | vector | bge-small | fair | 8192 | small-to-big | 0.4948 | 0.6009 | +0.1061 | [+0.0967, +0.1144] | 95.00% | yes |
| pooled | vector | nomic | production | 128 | small-to-big | 0.1513 | 0.2269 | +0.0755 | [+0.0662, +0.0857] | 99.17% | yes |
| pooled | vector | nomic | production | 256 | small-to-big | 0.2145 | 0.3318 | +0.1173 | [+0.1059, +0.1296] | 99.00% | yes |
| pooled | vector | nomic | production | 512 | small-to-big | 0.2818 | 0.4288 | +0.1470 | [+0.1331, +0.1605] | 98.75% | yes |
| pooled | vector | nomic | production | 1024 | small-to-big | 0.3646 | 0.4843 | +0.1198 | [+0.1095, +0.1296] | 95.00% | yes |
| pooled | vector | nomic | production | 2048 | small-to-big | 0.4236 | 0.5186 | +0.0950 | [+0.0837, +0.1065] | 98.33% | yes |
| pooled | vector | nomic | production | 4096 | small-to-big | 0.4423 | 0.5398 | +0.0975 | [+0.0863, +0.1085] | 97.50% | yes |
| pooled | vector | nomic | production | 8192 | small-to-big | 0.4423 | 0.5458 | +0.1035 | [+0.0937, +0.1134] | 95.00% | yes |
| pooled | vector | nomic | fair | 128 | small-to-big | 0.1513 | 0.2269 | +0.0755 | [+0.0662, +0.0857] | 99.17% | yes |
| pooled | vector | nomic | fair | 256 | small-to-big | 0.2145 | 0.3318 | +0.1173 | [+0.1059, +0.1296] | 99.00% | yes |
| pooled | vector | nomic | fair | 512 | small-to-big | 0.2818 | 0.4288 | +0.1470 | [+0.1331, +0.1605] | 98.75% | yes |
| pooled | vector | nomic | fair | 1024 | small-to-big | 0.3646 | 0.4917 | +0.1271 | [+0.1166, +0.1370] | 95.00% | yes |
| pooled | vector | nomic | fair | 2048 | small-to-big | 0.4251 | 0.5397 | +0.1146 | [+0.1021, +0.1251] | 98.33% | yes |
| pooled | vector | nomic | fair | 4096 | small-to-big | 0.4733 | 0.5836 | +0.1103 | [+0.0989, +0.1204] | 97.50% | yes |
| pooled | vector | nomic | fair | 8192 | small-to-big | 0.5175 | 0.6246 | +0.1071 | [+0.0976, +0.1162] | 95.00% | yes |
| nq | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.3337 | 0.4834 | +0.1497 | [+0.1270, +0.1738] | 99.17% | yes |
| nq | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.5006 | 0.7084 | +0.2078 | [+0.1817, +0.2344] | 99.00% | yes |
| nq | hybrid-rerank | bge-small | production | 512 | section-aware | 0.6610 | 0.8850 | +0.2240 | [+0.1927, +0.2468] | 98.75% | yes |
| nq | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.8207 | 0.9552 | +0.1345 | [+0.1145, +0.1551] | 95.00% | yes |
| nq | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.9079 | 0.9802 | +0.0723 | [+0.0534, +0.0915] | 98.33% | yes |
| nq | hybrid-rerank | bge-small | production | 4096 | section-aware | 0.9289 | 0.9889 | +0.0600 | [+0.0429, +0.0693] | 97.50% | yes |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.9648 | 0.9903 | +0.0254 | [+0.0165, +0.0350] | 95.00% | yes |
| nq | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.3337 | 0.4834 | +0.1497 | [+0.1270, +0.1738] | 99.17% | yes |
| nq | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.5006 | 0.7084 | +0.2078 | [+0.1817, +0.2344] | 99.00% | yes |
| nq | hybrid-rerank | bge-small | fair | 512 | section-aware | 0.6610 | 0.8850 | +0.2240 | [+0.1927, +0.2468] | 98.75% | yes |
| nq | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.8207 | 0.9580 | +0.1373 | [+0.1171, +0.1579] | 95.00% | yes |
| nq | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.9099 | 0.9850 | +0.0751 | [+0.0561, +0.0948] | 98.33% | yes |
| nq | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.9499 | 0.9940 | +0.0441 | [+0.0297, +0.0592] | 97.50% | yes |
| nq | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.9689 | 0.9984 | +0.0294 | [+0.0188, +0.0359] | 95.00% | yes |
| nq | hybrid-rerank | nomic | production | 128 | small-to-big | 0.3320 | 0.4837 | +0.1517 | [+0.1295, +0.1760] | 99.17% | yes |
| nq | hybrid-rerank | nomic | production | 256 | small-to-big | 0.4997 | 0.7057 | +0.2060 | [+0.1797, +0.2324] | 99.00% | yes |
| nq | hybrid-rerank | nomic | production | 512 | section-aware | 0.6610 | 0.8874 | +0.2264 | [+0.1957, +0.2509] | 98.75% | yes |
| nq | hybrid-rerank | nomic | production | 1024 | section-aware | 0.8197 | 0.9551 | +0.1354 | [+0.1154, +0.1559] | 95.00% | yes |
| nq | hybrid-rerank | nomic | production | 2048 | section-aware | 0.9077 | 0.9803 | +0.0726 | [+0.0537, +0.0922] | 98.33% | yes |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.9318 | 0.9889 | +0.0571 | [+0.0416, +0.0673] | 97.50% | yes |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.9705 | 0.9928 | +0.0223 | [+0.0141, +0.0312] | 95.00% | yes |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.3320 | 0.4837 | +0.1517 | [+0.1295, +0.1760] | 99.17% | yes |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.4997 | 0.7057 | +0.2060 | [+0.1797, +0.2324] | 99.00% | yes |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | 0.6610 | 0.8874 | +0.2264 | [+0.1957, +0.2509] | 98.75% | yes |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.8197 | 0.9583 | +0.1386 | [+0.1184, +0.1594] | 95.00% | yes |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.9087 | 0.9847 | +0.0760 | [+0.0569, +0.0955] | 98.33% | yes |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.9489 | 0.9927 | +0.0438 | [+0.0300, +0.0585] | 97.50% | yes |
| nq | hybrid-rerank | nomic | fair | 8192 | section-aware | 0.9729 | 0.9981 | +0.0251 | [+0.0153, +0.0304] | 95.00% | yes |
| nq | bm25 | - | production | 128 | small-to-big | 0.1775 | 0.2814 | +0.1039 | [+0.0820, +0.1195] | 99.17% | yes |
| nq | bm25 | - | production | 256 | small-to-big | 0.2776 | 0.4720 | +0.1944 | [+0.1677, +0.2177] | 99.00% | yes |
| nq | bm25 | - | production | 512 | fixed-256 | 0.4002 | 0.6439 | +0.2437 | [+0.2140, +0.2660] | 98.75% | yes |
| nq | bm25 | - | production | 1024 | section-aware | 0.5739 | 0.7726 | +0.1987 | [+0.1754, +0.2223] | 95.00% | yes |
| nq | bm25 | - | production | 2048 | section-aware | 0.7149 | 0.8462 | +0.1313 | [+0.1064, +0.1538] | 98.33% | yes |
| nq | bm25 | - | production | 4096 | fixed-512 | 0.8119 | 0.8936 | +0.0817 | [+0.0642, +0.0992] | 97.50% | yes |
| nq | bm25 | - | production | 8192 | fixed-1024 | 0.8887 | 0.9172 | +0.0285 | [+0.0192, +0.0387] | 95.00% | yes |
| nq | bm25 | - | fair | 128 | small-to-big | 0.1775 | 0.2814 | +0.1039 | [+0.0820, +0.1195] | 99.17% | yes |
| nq | bm25 | - | fair | 256 | small-to-big | 0.2776 | 0.4720 | +0.1944 | [+0.1677, +0.2177] | 99.00% | yes |
| nq | bm25 | - | fair | 512 | fixed-256 | 0.4002 | 0.6439 | +0.2437 | [+0.2140, +0.2660] | 98.75% | yes |
| nq | bm25 | - | fair | 1024 | section-aware | 0.5739 | 0.7804 | +0.2065 | [+0.1831, +0.2301] | 95.00% | yes |
| nq | bm25 | - | fair | 2048 | section-aware | 0.7169 | 0.8642 | +0.1472 | [+0.1213, +0.1711] | 98.33% | yes |
| nq | bm25 | - | fair | 4096 | fixed-512 | 0.8119 | 0.9198 | +0.1079 | [+0.0868, +0.1233] | 97.50% | yes |
| nq | bm25 | - | fair | 8192 | fixed-1024 | 0.8897 | 0.9571 | +0.0674 | [+0.0527, +0.0816] | 95.00% | yes |
| nq | hybrid | bge-small | production | 128 | fixed-128 | 0.2621 | 0.4044 | +0.1423 | [+0.1199, +0.1624] | 99.17% | yes |
| nq | hybrid | bge-small | production | 256 | small-to-big | 0.3997 | 0.6095 | +0.2098 | [+0.1831, +0.2380] | 99.00% | yes |
| nq | hybrid | bge-small | production | 512 | small-to-big | 0.5411 | 0.7892 | +0.2481 | [+0.2173, +0.2715] | 98.75% | yes |
| nq | hybrid | bge-small | production | 1024 | section-aware | 0.7039 | 0.8962 | +0.1923 | [+0.1675, +0.2096] | 95.00% | yes |
| nq | hybrid | bge-small | production | 2048 | small-to-big | 0.8199 | 0.9504 | +0.1305 | [+0.1058, +0.1501] | 98.33% | yes |
| nq | hybrid | bge-small | production | 4096 | fixed-512 | 0.9119 | 0.9694 | +0.0575 | [+0.0433, +0.0732] | 97.50% | yes |
| nq | hybrid | bge-small | production | 8192 | fixed-1024 | 0.9352 | 0.9766 | +0.0414 | [+0.0298, +0.0540] | 95.00% | yes |
| nq | hybrid | bge-small | fair | 128 | fixed-128 | 0.2621 | 0.4044 | +0.1423 | [+0.1199, +0.1624] | 99.17% | yes |
| nq | hybrid | bge-small | fair | 256 | small-to-big | 0.3997 | 0.6095 | +0.2098 | [+0.1831, +0.2380] | 99.00% | yes |
| nq | hybrid | bge-small | fair | 512 | small-to-big | 0.5411 | 0.7892 | +0.2481 | [+0.2173, +0.2715] | 98.75% | yes |
| nq | hybrid | bge-small | fair | 1024 | section-aware | 0.7039 | 0.9004 | +0.1965 | [+0.1714, +0.2139] | 95.00% | yes |
| nq | hybrid | bge-small | fair | 2048 | small-to-big | 0.8234 | 0.9601 | +0.1367 | [+0.1118, +0.1573] | 98.33% | yes |
| nq | hybrid | bge-small | fair | 4096 | section-aware | 0.9127 | 0.9821 | +0.0694 | [+0.0514, +0.0813] | 97.50% | yes |
| nq | hybrid | bge-small | fair | 8192 | section-aware | 0.9590 | 0.9934 | +0.0344 | [+0.0236, +0.0453] | 95.00% | yes |
| nq | hybrid | nomic | production | 128 | small-to-big | 0.2634 | 0.3968 | +0.1333 | [+0.1120, +0.1550] | 99.17% | yes |
| nq | hybrid | nomic | production | 256 | small-to-big | 0.4111 | 0.6183 | +0.2073 | [+0.1809, +0.2340] | 99.00% | yes |
| nq | hybrid | nomic | production | 512 | small-to-big | 0.5395 | 0.7882 | +0.2487 | [+0.2177, +0.2715] | 98.75% | yes |
| nq | hybrid | nomic | production | 1024 | section-aware | 0.7299 | 0.8954 | +0.1655 | [+0.1435, +0.1868] | 95.00% | yes |
| nq | hybrid | nomic | production | 2048 | small-to-big | 0.8352 | 0.9482 | +0.1129 | [+0.0896, +0.1329] | 98.33% | yes |
| nq | hybrid | nomic | production | 4096 | fixed-512 | 0.9059 | 0.9681 | +0.0621 | [+0.0470, +0.0781] | 97.50% | yes |
| nq | hybrid | nomic | production | 8192 | fixed-1024 | 0.9465 | 0.9784 | +0.0320 | [+0.0219, +0.0427] | 95.00% | yes |
| nq | hybrid | nomic | fair | 128 | small-to-big | 0.2634 | 0.3968 | +0.1333 | [+0.1120, +0.1550] | 99.17% | yes |
| nq | hybrid | nomic | fair | 256 | small-to-big | 0.4111 | 0.6183 | +0.2073 | [+0.1809, +0.2340] | 99.00% | yes |
| nq | hybrid | nomic | fair | 512 | small-to-big | 0.5395 | 0.7882 | +0.2487 | [+0.2177, +0.2715] | 98.75% | yes |
| nq | hybrid | nomic | fair | 1024 | section-aware | 0.7299 | 0.9019 | +0.1719 | [+0.1498, +0.1935] | 95.00% | yes |
| nq | hybrid | nomic | fair | 2048 | small-to-big | 0.8374 | 0.9616 | +0.1242 | [+0.1000, +0.1446] | 98.33% | yes |
| nq | hybrid | nomic | fair | 4096 | section-aware | 0.9169 | 0.9846 | +0.0676 | [+0.0508, +0.0839] | 97.50% | yes |
| nq | hybrid | nomic | fair | 8192 | section-aware | 0.9639 | 0.9941 | +0.0301 | [+0.0200, +0.0398] | 95.00% | yes |
| nq | vector | bge-small | production | 128 | fixed-128 | 0.3013 | 0.4584 | +0.1571 | [+0.1332, +0.1820] | 99.17% | yes |
| nq | vector | bge-small | production | 256 | fixed-128 | 0.4401 | 0.6859 | +0.2458 | [+0.2194, +0.2714] | 99.00% | yes |
| nq | vector | bge-small | production | 512 | small-to-big | 0.5774 | 0.8526 | +0.2752 | [+0.2428, +0.3004] | 98.75% | yes |
| nq | vector | bge-small | production | 1024 | small-to-big | 0.7571 | 0.9333 | +0.1762 | [+0.1542, +0.1982] | 95.00% | yes |
| nq | vector | bge-small | production | 2048 | small-to-big | 0.8565 | 0.9650 | +0.1085 | [+0.0865, +0.1319] | 98.33% | yes |
| nq | vector | bge-small | production | 4096 | fixed-512 | 0.8868 | 0.9770 | +0.0902 | [+0.0708, +0.1059] | 97.50% | yes |
| nq | vector | bge-small | production | 8192 | fixed-1024 | 0.9033 | 0.9830 | +0.0796 | [+0.0635, +0.0952] | 95.00% | yes |
| nq | vector | bge-small | fair | 128 | fixed-128 | 0.3013 | 0.4584 | +0.1571 | [+0.1332, +0.1820] | 99.17% | yes |
| nq | vector | bge-small | fair | 256 | fixed-128 | 0.4401 | 0.6859 | +0.2458 | [+0.2194, +0.2714] | 99.00% | yes |
| nq | vector | bge-small | fair | 512 | small-to-big | 0.5777 | 0.8527 | +0.2750 | [+0.2426, +0.3003] | 98.75% | yes |
| nq | vector | bge-small | fair | 1024 | small-to-big | 0.7579 | 0.9369 | +0.1790 | [+0.1572, +0.2011] | 95.00% | yes |
| nq | vector | bge-small | fair | 2048 | small-to-big | 0.8636 | 0.9712 | +0.1076 | [+0.0859, +0.1306] | 98.33% | yes |
| nq | vector | bge-small | fair | 4096 | small-to-big | 0.9233 | 0.9904 | +0.0672 | [+0.0508, +0.0848] | 97.50% | yes |
| nq | vector | bge-small | fair | 8192 | small-to-big | 0.9539 | 0.9958 | +0.0419 | [+0.0302, +0.0545] | 95.00% | yes |
| nq | vector | nomic | production | 128 | small-to-big | 0.3670 | 0.5038 | +0.1369 | [+0.1153, +0.1595] | 99.17% | yes |
| nq | vector | nomic | production | 256 | small-to-big | 0.5196 | 0.7346 | +0.2150 | [+0.1890, +0.2424] | 99.00% | yes |
| nq | vector | nomic | production | 512 | section-aware | 0.6510 | 0.8954 | +0.2444 | [+0.2104, +0.2647] | 98.75% | yes |
| nq | vector | nomic | production | 1024 | section-aware | 0.8157 | 0.9552 | +0.1395 | [+0.1181, +0.1568] | 95.00% | yes |
| nq | vector | nomic | production | 2048 | section-aware | 0.8979 | 0.9781 | +0.0802 | [+0.0610, +0.0988] | 98.33% | yes |
| nq | vector | nomic | production | 4096 | fixed-512 | 0.9254 | 0.9896 | +0.0642 | [+0.0473, +0.0757] | 97.50% | yes |
| nq | vector | nomic | production | 8192 | fixed-1024 | 0.9393 | 0.9914 | +0.0521 | [+0.0391, +0.0647] | 95.00% | yes |
| nq | vector | nomic | fair | 128 | small-to-big | 0.3670 | 0.5038 | +0.1369 | [+0.1153, +0.1595] | 99.17% | yes |
| nq | vector | nomic | fair | 256 | small-to-big | 0.5196 | 0.7346 | +0.2150 | [+0.1890, +0.2424] | 99.00% | yes |
| nq | vector | nomic | fair | 512 | section-aware | 0.6510 | 0.8954 | +0.2444 | [+0.2104, +0.2647] | 98.75% | yes |
| nq | vector | nomic | fair | 1024 | section-aware | 0.8157 | 0.9593 | +0.1436 | [+0.1222, +0.1611] | 95.00% | yes |
| nq | vector | nomic | fair | 2048 | section-aware | 0.8989 | 0.9818 | +0.0828 | [+0.0635, +0.1017] | 98.33% | yes |
| nq | vector | nomic | fair | 4096 | small-to-big | 0.9430 | 0.9940 | +0.0510 | [+0.0353, +0.0638] | 97.50% | yes |
| nq | vector | nomic | fair | 8192 | section-aware | 0.9649 | 0.9982 | +0.0333 | [+0.0223, +0.0429] | 95.00% | yes |
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
| pooled | hybrid-rerank | bge-small | production | 128 | small-to-big | small-to-big | small-to-big | 0.1530 | +0.0000 | [+0.0000, +0.0002] | 99.17% | +0.0818 | [+0.0722, +0.0919] | 99.17% |
| pooled | hybrid-rerank | bge-small | production | 256 | small-to-big | small-to-big | small-to-big | 0.2308 | +0.0000 | [+0.0000, +0.0005] | 99.17% | +0.1263 | [+0.1144, +0.1385] | 99.00% |
| pooled | hybrid-rerank | bge-small | production | 512 | small-to-big | section-aware | small-to-big | 0.3242 | +0.0042 | [+0.0000, +0.0120] | 99.17% | +0.1558 | [+0.1415, +0.1694] | 98.75% |
| pooled | hybrid-rerank | bge-small | production | 1024 | section-aware | section-aware | section-aware | 0.4256 | +0.0000 | [+0.0000, +0.0031] | 95.00% | +0.1295 | [+0.1186, +0.1395] | 95.00% |
| pooled | hybrid-rerank | bge-small | production | 2048 | section-aware | section-aware | section-aware | 0.4923 | +0.0000 | [+0.0000, +0.0030] | 99.17% | +0.0994 | [+0.0878, +0.1112] | 98.33% |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-512 | fixed-512 | section-aware | 0.5120 | +0.0009 | [+0.0000, +0.0092] | 99.17% | +0.0991 | [+0.0871, +0.1068] | 97.50% |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.5485 | +0.0000 | [+0.0000, +0.0006] | 99.17% | +0.0701 | [+0.0620, +0.0780] | 95.00% |
| pooled | hybrid-rerank | bge-small | fair | 128 | small-to-big | small-to-big | small-to-big | 0.1530 | +0.0000 | [+0.0000, +0.0002] | 99.17% | +0.0818 | [+0.0722, +0.0919] | 99.17% |
| pooled | hybrid-rerank | bge-small | fair | 256 | small-to-big | small-to-big | small-to-big | 0.2308 | +0.0000 | [+0.0000, +0.0005] | 99.17% | +0.1263 | [+0.1144, +0.1385] | 99.00% |
| pooled | hybrid-rerank | bge-small | fair | 512 | small-to-big | section-aware | small-to-big | 0.3242 | +0.0042 | [+0.0000, +0.0120] | 99.17% | +0.1558 | [+0.1415, +0.1694] | 98.75% |
| pooled | hybrid-rerank | bge-small | fair | 1024 | section-aware | section-aware | section-aware | 0.4257 | +0.0000 | [+0.0000, +0.0031] | 95.00% | +0.1341 | [+0.1231, +0.1444] | 95.00% |
| pooled | hybrid-rerank | bge-small | fair | 2048 | section-aware | section-aware | section-aware | 0.4959 | +0.0000 | [+0.0000, +0.0023] | 99.17% | +0.1067 | [+0.0949, +0.1187] | 98.33% |
| pooled | hybrid-rerank | bge-small | fair | 4096 | section-aware | section-aware | section-aware | 0.5339 | +0.0000 | [+0.0000, +0.0052] | 99.17% | +0.1004 | [+0.0893, +0.1109] | 97.50% |
| pooled | hybrid-rerank | bge-small | fair | 8192 | section-aware | fixed-1024 | section-aware | 0.5601 | +0.0031 | [+0.0000, +0.0108] | 99.17% | +0.1046 | [+0.0944, +0.1126] | 95.00% |
| pooled | hybrid-rerank | nomic | production | 128 | small-to-big | small-to-big | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0013] | 99.17% | +0.0840 | [+0.0742, +0.0944] | 99.17% |
| pooled | hybrid-rerank | nomic | production | 256 | small-to-big | small-to-big | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0019] | 99.17% | +0.1271 | [+0.1151, +0.1392] | 99.00% |
| pooled | hybrid-rerank | nomic | production | 512 | small-to-big | section-aware | small-to-big | 0.3223 | +0.0049 | [+0.0000, +0.0119] | 99.17% | +0.1556 | [+0.1414, +0.1688] | 98.75% |
| pooled | hybrid-rerank | nomic | production | 1024 | section-aware | section-aware | section-aware | 0.4262 | +0.0000 | [+0.0000, +0.0038] | 95.00% | +0.1313 | [+0.1203, +0.1416] | 95.00% |
| pooled | hybrid-rerank | nomic | production | 2048 | section-aware | section-aware | section-aware | 0.4923 | +0.0000 | [+0.0000, +0.0026] | 99.17% | +0.1010 | [+0.0892, +0.1129] | 98.33% |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-512 | fixed-512 | fixed-1024 | 0.5117 | +0.0002 | [+0.0000, +0.0095] | 99.17% | +0.1014 | [+0.0885, +0.1087] | 97.50% |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.5573 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0666 | [+0.0587, +0.0744] | 95.00% |
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | small-to-big | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0013] | 99.17% | +0.0840 | [+0.0742, +0.0944] | 99.17% |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0019] | 99.17% | +0.1271 | [+0.1151, +0.1392] | 99.00% |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | section-aware | small-to-big | 0.3223 | +0.0049 | [+0.0000, +0.0119] | 99.17% | +0.1556 | [+0.1414, +0.1688] | 98.75% |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0034] | 95.00% | +0.1373 | [+0.1262, +0.1479] | 95.00% |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | section-aware | 0.4956 | +0.0000 | [+0.0000, +0.0030] | 99.17% | +0.1088 | [+0.0968, +0.1211] | 98.33% |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | section-aware | section-aware | 0.5334 | +0.0000 | [+0.0000, +0.0083] | 99.17% | +0.1038 | [+0.0921, +0.1130] | 97.50% |
| pooled | hybrid-rerank | nomic | fair | 8192 | section-aware | fixed-1024 | section-aware | 0.5620 | +0.0036 | [+0.0000, +0.0112] | 99.17% | +0.1083 | [+0.0967, +0.1147] | 95.00% |
| pooled | bm25 | - | production | 128 | small-to-big | fixed-128 | small-to-big | 0.0844 | +0.0006 | [+0.0000, +0.0053] | 99.17% | +0.0567 | [+0.0474, +0.0636] | 99.17% |
| pooled | bm25 | - | production | 256 | fixed-128 | small-to-big | small-to-big | 0.1310 | +0.0020 | [+0.0000, +0.0075] | 99.17% | +0.1066 | [+0.0944, +0.1163] | 99.00% |
| pooled | bm25 | - | production | 512 | small-to-big | small-to-big | fixed-128 | 0.1957 | +0.0014 | [+0.0000, +0.0091] | 99.17% | +0.1478 | [+0.1328, +0.1572] | 98.75% |
| pooled | bm25 | - | production | 1024 | section-aware | section-aware | section-aware | 0.2896 | +0.0000 | [+0.0000, +0.0064] | 95.00% | +0.1400 | [+0.1279, +0.1495] | 95.00% |
| pooled | bm25 | - | production | 2048 | small-to-big | section-aware | section-aware | 0.3780 | +0.0011 | [+0.0000, +0.0117] | 99.17% | +0.1085 | [+0.0950, +0.1190] | 98.33% |
| pooled | bm25 | - | production | 4096 | fixed-512 | fixed-512 | fixed-512 | 0.4389 | +0.0000 | [+0.0000, +0.0053] | 99.17% | +0.0831 | [+0.0730, +0.0920] | 97.50% |
| pooled | bm25 | - | production | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.4953 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0455 | [+0.0387, +0.0523] | 95.00% |
| pooled | bm25 | - | fair | 128 | small-to-big | fixed-128 | small-to-big | 0.0844 | +0.0006 | [+0.0000, +0.0053] | 99.17% | +0.0567 | [+0.0474, +0.0636] | 99.17% |
| pooled | bm25 | - | fair | 256 | fixed-128 | small-to-big | small-to-big | 0.1310 | +0.0020 | [+0.0000, +0.0075] | 99.17% | +0.1066 | [+0.0944, +0.1163] | 99.00% |
| pooled | bm25 | - | fair | 512 | small-to-big | small-to-big | fixed-128 | 0.1957 | +0.0014 | [+0.0000, +0.0091] | 99.17% | +0.1478 | [+0.1328, +0.1572] | 98.75% |
| pooled | bm25 | - | fair | 1024 | section-aware | section-aware | section-aware | 0.2896 | +0.0000 | [+0.0000, +0.0064] | 95.00% | +0.1487 | [+0.1366, +0.1584] | 95.00% |
| pooled | bm25 | - | fair | 2048 | small-to-big | section-aware | section-aware | 0.3827 | +0.0006 | [+0.0000, +0.0108] | 99.17% | +0.1249 | [+0.1112, +0.1360] | 98.33% |
| pooled | bm25 | - | fair | 4096 | section-aware | section-aware | section-aware | 0.4500 | +0.0000 | [+0.0000, +0.0076] | 99.17% | +0.1170 | [+0.1043, +0.1262] | 97.50% |
| pooled | bm25 | - | fair | 8192 | section-aware | fixed-1024 | section-aware | 0.5106 | +0.0002 | [+0.0000, +0.0110] | 99.17% | +0.1148 | [+0.1031, +0.1217] | 95.00% |
| pooled | hybrid | bge-small | production | 128 | fixed-128 | fixed-128 | fixed-64 | 0.1134 | +0.0011 | [+0.0000, +0.0071] | 99.17% | +0.0787 | [+0.0675, +0.0857] | 99.17% |
| pooled | hybrid | bge-small | production | 256 | small-to-big | small-to-big | fixed-64 | 0.1758 | +0.0029 | [+0.0000, +0.0095] | 99.17% | +0.1187 | [+0.1059, +0.1301] | 99.00% |
| pooled | hybrid | bge-small | production | 512 | small-to-big | small-to-big | section-aware | 0.2502 | +0.0015 | [+0.0000, +0.0115] | 99.17% | +0.1530 | [+0.1378, +0.1645] | 98.75% |
| pooled | hybrid | bge-small | production | 1024 | small-to-big | section-aware | section-aware | 0.3416 | +0.0008 | [+0.0000, +0.0060] | 95.00% | +0.1412 | [+0.1280, +0.1492] | 95.00% |
| pooled | hybrid | bge-small | production | 2048 | small-to-big | section-aware | small-to-big | 0.4180 | +0.0020 | [+0.0000, +0.0093] | 99.17% | +0.1095 | [+0.0967, +0.1199] | 98.33% |
| pooled | hybrid | bge-small | production | 4096 | fixed-512 | fixed-512 | fixed-512 | 0.4574 | +0.0000 | [+0.0000, +0.0089] | 99.17% | +0.0982 | [+0.0872, +0.1076] | 97.50% |
| pooled | hybrid | bge-small | production | 8192 | fixed-1024 | fixed-1024 | fixed-512 | 0.4786 | +0.0008 | [+0.0000, +0.0070] | 99.17% | +0.0943 | [+0.0844, +0.1034] | 95.00% |
| pooled | hybrid | bge-small | fair | 128 | fixed-128 | fixed-128 | fixed-64 | 0.1134 | +0.0011 | [+0.0000, +0.0071] | 99.17% | +0.0787 | [+0.0675, +0.0857] | 99.17% |
| pooled | hybrid | bge-small | fair | 256 | small-to-big | small-to-big | fixed-64 | 0.1758 | +0.0029 | [+0.0000, +0.0095] | 99.17% | +0.1187 | [+0.1059, +0.1301] | 99.00% |
| pooled | hybrid | bge-small | fair | 512 | small-to-big | small-to-big | section-aware | 0.2502 | +0.0015 | [+0.0000, +0.0115] | 99.17% | +0.1530 | [+0.1378, +0.1645] | 98.75% |
| pooled | hybrid | bge-small | fair | 1024 | small-to-big | section-aware | section-aware | 0.3416 | +0.0005 | [+0.0000, +0.0059] | 95.00% | +0.1480 | [+0.1346, +0.1560] | 95.00% |
| pooled | hybrid | bge-small | fair | 2048 | small-to-big | section-aware | small-to-big | 0.4242 | +0.0028 | [+0.0000, +0.0090] | 99.17% | +0.1259 | [+0.1123, +0.1361] | 98.33% |
| pooled | hybrid | bge-small | fair | 4096 | section-aware | section-aware | section-aware | 0.4898 | +0.0000 | [+0.0000, +0.0090] | 99.17% | +0.1130 | [+0.0998, +0.1212] | 97.50% |
| pooled | hybrid | bge-small | fair | 8192 | section-aware | section-aware | section-aware | 0.5498 | +0.0000 | [+0.0000, +0.0076] | 99.17% | +0.1046 | [+0.0939, +0.1122] | 95.00% |
| pooled | hybrid | nomic | production | 128 | small-to-big | small-to-big | small-to-big | 0.1188 | +0.0000 | [+0.0000, +0.0042] | 99.17% | +0.0717 | [+0.0623, +0.0807] | 99.17% |
| pooled | hybrid | nomic | production | 256 | small-to-big | small-to-big | small-to-big | 0.1838 | +0.0000 | [+0.0000, +0.0036] | 99.17% | +0.1177 | [+0.1059, +0.1293] | 99.00% |
| pooled | hybrid | nomic | production | 512 | small-to-big | section-aware | fixed-128 | 0.2552 | +0.0011 | [+0.0000, +0.0113] | 99.17% | +0.1583 | [+0.1418, +0.1694] | 98.75% |
| pooled | hybrid | nomic | production | 1024 | small-to-big | section-aware | section-aware | 0.3562 | +0.0064 | [+0.0000, +0.0126] | 95.00% | +0.1318 | [+0.1207, +0.1423] | 95.00% |
| pooled | hybrid | nomic | production | 2048 | small-to-big | section-aware | section-aware | 0.4276 | +0.0019 | [+0.0000, +0.0088] | 99.17% | +0.1075 | [+0.0941, +0.1186] | 98.33% |
| pooled | hybrid | nomic | production | 4096 | small-to-big | fixed-512 | small-to-big | 0.4614 | +0.0043 | [+0.0000, +0.0146] | 99.17% | +0.0976 | [+0.0860, +0.1066] | 97.50% |
| pooled | hybrid | nomic | production | 8192 | fixed-1024 | fixed-1024 | small-to-big | 0.4903 | +0.0006 | [+0.0000, +0.0078] | 99.17% | +0.0856 | [+0.0758, +0.0940] | 95.00% |
| pooled | hybrid | nomic | fair | 128 | small-to-big | small-to-big | small-to-big | 0.1188 | +0.0000 | [+0.0000, +0.0042] | 99.17% | +0.0717 | [+0.0623, +0.0807] | 99.17% |
| pooled | hybrid | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.1838 | +0.0000 | [+0.0000, +0.0036] | 99.17% | +0.1177 | [+0.1059, +0.1293] | 99.00% |
| pooled | hybrid | nomic | fair | 512 | small-to-big | section-aware | fixed-128 | 0.2552 | +0.0011 | [+0.0000, +0.0113] | 99.17% | +0.1583 | [+0.1418, +0.1694] | 98.75% |
| pooled | hybrid | nomic | fair | 1024 | small-to-big | section-aware | section-aware | 0.3565 | +0.0061 | [+0.0000, +0.0125] | 95.00% | +0.1391 | [+0.1280, +0.1497] | 95.00% |
| pooled | hybrid | nomic | fair | 2048 | small-to-big | section-aware | section-aware | 0.4311 | +0.0025 | [+0.0000, +0.0083] | 99.17% | +0.1252 | [+0.1117, +0.1362] | 98.33% |
| pooled | hybrid | nomic | fair | 4096 | section-aware | section-aware | small-to-big | 0.4989 | +0.0007 | [+0.0000, +0.0077] | 99.17% | +0.1108 | [+0.0985, +0.1199] | 97.50% |
| pooled | hybrid | nomic | fair | 8192 | small-to-big | section-aware | section-aware | 0.5536 | +0.0006 | [+0.0000, +0.0066] | 99.17% | +0.1041 | [+0.0936, +0.1114] | 95.00% |
| pooled | vector | bge-small | production | 128 | fixed-128 | fixed-128 | fixed-64 | 0.1197 | +0.0015 | [+0.0000, +0.0049] | 99.17% | +0.0817 | [+0.0716, +0.0920] | 99.17% |
| pooled | vector | bge-small | production | 256 | fixed-128 | fixed-128 | fixed-64 | 0.1790 | +0.0011 | [+0.0000, +0.0103] | 99.17% | +0.1229 | [+0.1097, +0.1324] | 99.00% |
| pooled | vector | bge-small | production | 512 | fixed-128 | small-to-big | section-aware | 0.2430 | +0.0031 | [+0.0000, +0.0124] | 99.17% | +0.1590 | [+0.1434, +0.1700] | 98.75% |
| pooled | vector | bge-small | production | 1024 | small-to-big | small-to-big | section-aware | 0.3358 | +0.0037 | [+0.0000, +0.0076] | 95.00% | +0.1257 | [+0.1152, +0.1363] | 95.00% |
| pooled | vector | bge-small | production | 2048 | small-to-big | small-to-big | section-aware | 0.3923 | +0.0029 | [+0.0000, +0.0079] | 99.17% | +0.1000 | [+0.0883, +0.1113] | 98.33% |
| pooled | vector | bge-small | production | 4096 | small-to-big | small-to-big | section-aware | 0.4061 | +0.0022 | [+0.0000, +0.0109] | 99.17% | +0.1025 | [+0.0902, +0.1110] | 97.50% |
| pooled | vector | bge-small | production | 8192 | small-to-big | fixed-1024 | section-aware | 0.4093 | +0.0054 | [+0.0000, +0.0145] | 99.17% | +0.1102 | [+0.0991, +0.1181] | 95.00% |
| pooled | vector | bge-small | fair | 128 | fixed-128 | fixed-128 | fixed-64 | 0.1197 | +0.0015 | [+0.0000, +0.0049] | 99.17% | +0.0817 | [+0.0716, +0.0920] | 99.17% |
| pooled | vector | bge-small | fair | 256 | fixed-128 | fixed-128 | fixed-64 | 0.1790 | +0.0011 | [+0.0000, +0.0103] | 99.17% | +0.1229 | [+0.1097, +0.1324] | 99.00% |
| pooled | vector | bge-small | fair | 512 | fixed-128 | small-to-big | section-aware | 0.2433 | +0.0032 | [+0.0000, +0.0125] | 99.17% | +0.1587 | [+0.1433, +0.1698] | 98.75% |
| pooled | vector | bge-small | fair | 1024 | small-to-big | small-to-big | section-aware | 0.3373 | +0.0043 | [+0.0005, +0.0083] | 95.00% | +0.1326 | [+0.1221, +0.1431] | 95.00% |
| pooled | vector | bge-small | fair | 2048 | small-to-big | small-to-big | section-aware | 0.3999 | +0.0039 | [+0.0000, +0.0092] | 99.17% | +0.1156 | [+0.1037, +0.1269] | 98.33% |
| pooled | vector | bge-small | fair | 4096 | section-aware | small-to-big | section-aware | 0.4502 | +0.0034 | [+0.0000, +0.0091] | 99.17% | +0.1092 | [+0.0971, +0.1183] | 97.50% |
| pooled | vector | bge-small | fair | 8192 | small-to-big | small-to-big | small-to-big | 0.4948 | +0.0000 | [+0.0000, +0.0083] | 99.17% | +0.1061 | [+0.0952, +0.1126] | 95.00% |
| pooled | vector | nomic | production | 128 | small-to-big | small-to-big | small-to-big | 0.1513 | +0.0000 | [+0.0000, +0.0036] | 99.17% | +0.0755 | [+0.0662, +0.0852] | 99.17% |
| pooled | vector | nomic | production | 256 | small-to-big | small-to-big | small-to-big | 0.2145 | +0.0000 | [+0.0000, +0.0041] | 99.17% | +0.1173 | [+0.1059, +0.1290] | 99.00% |
| pooled | vector | nomic | production | 512 | small-to-big | section-aware | section-aware | 0.2867 | +0.0049 | [+0.0000, +0.0141] | 99.17% | +0.1421 | [+0.1283, +0.1547] | 98.75% |
| pooled | vector | nomic | production | 1024 | small-to-big | section-aware | small-to-big | 0.3695 | +0.0049 | [+0.0000, +0.0108] | 95.00% | +0.1148 | [+0.1044, +0.1246] | 95.00% |
| pooled | vector | nomic | production | 2048 | small-to-big | section-aware | small-to-big | 0.4257 | +0.0021 | [+0.0000, +0.0091] | 99.17% | +0.0928 | [+0.0813, +0.1035] | 98.33% |
| pooled | vector | nomic | production | 4096 | small-to-big | fixed-512 | small-to-big | 0.4433 | +0.0009 | [+0.0000, +0.0087] | 99.17% | +0.0966 | [+0.0853, +0.1062] | 97.50% |
| pooled | vector | nomic | production | 8192 | small-to-big | fixed-1024 | small-to-big | 0.4464 | +0.0040 | [+0.0000, +0.0126] | 99.17% | +0.0995 | [+0.0898, +0.1088] | 95.00% |
| pooled | vector | nomic | fair | 128 | small-to-big | small-to-big | small-to-big | 0.1513 | +0.0000 | [+0.0000, +0.0036] | 99.17% | +0.0755 | [+0.0662, +0.0852] | 99.17% |
| pooled | vector | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.2145 | +0.0000 | [+0.0000, +0.0041] | 99.17% | +0.1173 | [+0.1059, +0.1290] | 99.00% |
| pooled | vector | nomic | fair | 512 | small-to-big | section-aware | section-aware | 0.2867 | +0.0049 | [+0.0000, +0.0141] | 99.17% | +0.1421 | [+0.1283, +0.1547] | 98.75% |
| pooled | vector | nomic | fair | 1024 | small-to-big | section-aware | small-to-big | 0.3695 | +0.0049 | [+0.0000, +0.0108] | 95.00% | +0.1222 | [+0.1116, +0.1320] | 95.00% |
| pooled | vector | nomic | fair | 2048 | small-to-big | section-aware | small-to-big | 0.4282 | +0.0031 | [+0.0000, +0.0089] | 99.17% | +0.1115 | [+0.0992, +0.1226] | 98.33% |
| pooled | vector | nomic | fair | 4096 | small-to-big | small-to-big | section-aware | 0.4753 | +0.0020 | [+0.0000, +0.0068] | 99.17% | +0.1083 | [+0.0967, +0.1183] | 97.50% |
| pooled | vector | nomic | fair | 8192 | small-to-big | section-aware | small-to-big | 0.5189 | +0.0014 | [+0.0000, +0.0078] | 99.17% | +0.1057 | [+0.0955, +0.1142] | 95.00% |
| nq | hybrid-rerank | bge-small | production | 128 | small-to-big | small-to-big | n/a | 0.3337 | +0.0000 | [+0.0000, +0.0049] | 99.17% | +0.1497 | [+0.1270, +0.1733] | 99.17% |
| nq | hybrid-rerank | bge-small | production | 256 | small-to-big | small-to-big | n/a | 0.5006 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2078 | [+0.1817, +0.2343] | 99.00% |
| nq | hybrid-rerank | bge-small | production | 512 | small-to-big | section-aware | n/a | 0.6626 | +0.0016 | [+0.0000, +0.0182] | 99.17% | +0.2223 | [+0.1900, +0.2443] | 98.75% |
| nq | hybrid-rerank | bge-small | production | 1024 | section-aware | section-aware | n/a | 0.8207 | +0.0000 | [+0.0000, +0.0050] | 95.00% | +0.1345 | [+0.1143, +0.1543] | 95.00% |
| nq | hybrid-rerank | bge-small | production | 2048 | section-aware | section-aware | n/a | 0.9079 | +0.0000 | [+0.0000, +0.0052] | 99.17% | +0.0723 | [+0.0534, +0.0911] | 98.33% |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-512 | section-aware | n/a | 0.9298 | +0.0009 | [+0.0000, +0.0110] | 99.17% | +0.0591 | [+0.0412, +0.0672] | 97.50% |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9648 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0254 | [+0.0165, +0.0350] | 95.00% |
| nq | hybrid-rerank | bge-small | fair | 128 | small-to-big | small-to-big | n/a | 0.3337 | +0.0000 | [+0.0000, +0.0049] | 99.17% | +0.1497 | [+0.1270, +0.1733] | 99.17% |
| nq | hybrid-rerank | bge-small | fair | 256 | small-to-big | small-to-big | n/a | 0.5006 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2078 | [+0.1817, +0.2343] | 99.00% |
| nq | hybrid-rerank | bge-small | fair | 512 | small-to-big | section-aware | n/a | 0.6626 | +0.0016 | [+0.0000, +0.0182] | 99.17% | +0.2223 | [+0.1900, +0.2443] | 98.75% |
| nq | hybrid-rerank | bge-small | fair | 1024 | section-aware | section-aware | n/a | 0.8207 | +0.0000 | [+0.0000, +0.0050] | 95.00% | +0.1373 | [+0.1171, +0.1571] | 95.00% |
| nq | hybrid-rerank | bge-small | fair | 2048 | section-aware | section-aware | n/a | 0.9099 | +0.0000 | [+0.0000, +0.0048] | 99.17% | +0.0751 | [+0.0561, +0.0945] | 98.33% |
| nq | hybrid-rerank | bge-small | fair | 4096 | section-aware | section-aware | n/a | 0.9499 | +0.0000 | [+0.0000, +0.0082] | 99.17% | +0.0441 | [+0.0296, +0.0575] | 97.50% |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-512 | section-aware | n/a | 0.9720 | +0.0031 | [+0.0000, +0.0098] | 99.17% | +0.0264 | [+0.0166, +0.0332] | 95.00% |
| nq | hybrid-rerank | nomic | production | 128 | small-to-big | small-to-big | n/a | 0.3320 | +0.0000 | [+0.0000, +0.0060] | 99.17% | +0.1517 | [+0.1295, +0.1756] | 99.17% |
| nq | hybrid-rerank | nomic | production | 256 | small-to-big | small-to-big | n/a | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2060 | [+0.1797, +0.2324] | 99.00% |
| nq | hybrid-rerank | nomic | production | 512 | section-aware | section-aware | n/a | 0.6610 | +0.0000 | [+0.0000, +0.0183] | 99.17% | +0.2264 | [+0.1931, +0.2490] | 98.75% |
| nq | hybrid-rerank | nomic | production | 1024 | section-aware | section-aware | n/a | 0.8197 | +0.0000 | [+0.0000, +0.0024] | 95.00% | +0.1354 | [+0.1153, +0.1555] | 95.00% |
| nq | hybrid-rerank | nomic | production | 2048 | section-aware | section-aware | n/a | 0.9077 | +0.0000 | [+0.0000, +0.0052] | 99.17% | +0.0726 | [+0.0537, +0.0917] | 98.33% |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-512 | fixed-512 | n/a | 0.9318 | +0.0000 | [+0.0000, +0.0111] | 99.17% | +0.0571 | [+0.0397, +0.0650] | 97.50% |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9705 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0223 | [+0.0141, +0.0312] | 95.00% |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | small-to-big | n/a | 0.3320 | +0.0000 | [+0.0000, +0.0060] | 99.17% | +0.1517 | [+0.1295, +0.1756] | 99.17% |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | n/a | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2060 | [+0.1797, +0.2324] | 99.00% |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | section-aware | n/a | 0.6610 | +0.0000 | [+0.0000, +0.0183] | 99.17% | +0.2264 | [+0.1931, +0.2490] | 98.75% |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | n/a | 0.8197 | +0.0000 | [+0.0000, +0.0024] | 95.00% | +0.1386 | [+0.1184, +0.1590] | 95.00% |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | n/a | 0.9087 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0760 | [+0.0569, +0.0952] | 98.33% |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | section-aware | n/a | 0.9489 | +0.0000 | [+0.0000, +0.0082] | 99.17% | +0.0438 | [+0.0299, +0.0571] | 97.50% |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-512 | section-aware | n/a | 0.9730 | +0.0001 | [+0.0000, +0.0077] | 99.17% | +0.0250 | [+0.0142, +0.0287] | 95.00% |
| nq | bm25 | - | production | 128 | small-to-big | fixed-128 | n/a | 0.1836 | +0.0061 | [+0.0000, +0.0161] | 99.17% | +0.0978 | [+0.0786, +0.1157] | 99.17% |
| nq | bm25 | - | production | 256 | small-to-big | small-to-big | n/a | 0.2776 | +0.0000 | [+0.0000, +0.0138] | 99.17% | +0.1944 | [+0.1665, +0.2156] | 99.00% |
| nq | bm25 | - | production | 512 | fixed-256 | small-to-big | n/a | 0.4043 | +0.0042 | [+0.0000, +0.0224] | 99.17% | +0.2396 | [+0.2091, +0.2611] | 98.75% |
| nq | bm25 | - | production | 1024 | fixed-512 | section-aware | n/a | 0.5749 | +0.0010 | [+0.0000, +0.0174] | 95.00% | +0.1977 | [+0.1729, +0.2166] | 95.00% |
| nq | bm25 | - | production | 2048 | fixed-512 | section-aware | n/a | 0.7176 | +0.0026 | [+0.0000, +0.0201] | 99.17% | +0.1286 | [+0.1033, +0.1493] | 98.33% |
| nq | bm25 | - | production | 4096 | fixed-512 | fixed-512 | n/a | 0.8119 | +0.0000 | [+0.0000, +0.0094] | 99.17% | +0.0817 | [+0.0641, +0.0984] | 97.50% |
| nq | bm25 | - | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.8887 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0285 | [+0.0192, +0.0387] | 95.00% |
| nq | bm25 | - | fair | 128 | small-to-big | fixed-128 | n/a | 0.1836 | +0.0061 | [+0.0000, +0.0161] | 99.17% | +0.0978 | [+0.0786, +0.1157] | 99.17% |
| nq | bm25 | - | fair | 256 | small-to-big | small-to-big | n/a | 0.2776 | +0.0000 | [+0.0000, +0.0138] | 99.17% | +0.1944 | [+0.1665, +0.2156] | 99.00% |
| nq | bm25 | - | fair | 512 | fixed-256 | small-to-big | n/a | 0.4043 | +0.0042 | [+0.0000, +0.0224] | 99.17% | +0.2396 | [+0.2091, +0.2611] | 98.75% |
| nq | bm25 | - | fair | 1024 | fixed-512 | section-aware | n/a | 0.5749 | +0.0010 | [+0.0000, +0.0174] | 95.00% | +0.2054 | [+0.1804, +0.2244] | 95.00% |
| nq | bm25 | - | fair | 2048 | fixed-512 | section-aware | n/a | 0.7196 | +0.0026 | [+0.0000, +0.0210] | 99.17% | +0.1446 | [+0.1190, +0.1658] | 98.33% |
| nq | bm25 | - | fair | 4096 | fixed-512 | section-aware | n/a | 0.8183 | +0.0064 | [+0.0000, +0.0181] | 99.17% | +0.1015 | [+0.0819, +0.1190] | 97.50% |
| nq | bm25 | - | fair | 8192 | fixed-1024 | section-aware | n/a | 0.8916 | +0.0019 | [+0.0000, +0.0192] | 99.17% | +0.0655 | [+0.0500, +0.0770] | 95.00% |
| nq | hybrid | bge-small | production | 128 | fixed-128 | fixed-128 | n/a | 0.2621 | +0.0000 | [+0.0000, +0.0136] | 99.17% | +0.1423 | [+0.1191, +0.1602] | 99.17% |
| nq | hybrid | bge-small | production | 256 | small-to-big | small-to-big | n/a | 0.3997 | +0.0000 | [+0.0000, +0.0158] | 99.17% | +0.2098 | [+0.1828, +0.2349] | 99.00% |
| nq | hybrid | bge-small | production | 512 | small-to-big | fixed-256 | n/a | 0.5419 | +0.0008 | [+0.0000, +0.0228] | 99.17% | +0.2473 | [+0.2144, +0.2661] | 98.75% |
| nq | hybrid | bge-small | production | 1024 | section-aware | small-to-big | n/a | 0.7047 | +0.0008 | [+0.0000, +0.0128] | 95.00% | +0.1915 | [+0.1652, +0.2064] | 95.00% |
| nq | hybrid | bge-small | production | 2048 | small-to-big | section-aware | n/a | 0.8261 | +0.0061 | [+0.0000, +0.0233] | 99.17% | +0.1243 | [+0.0993, +0.1409] | 98.33% |
| nq | hybrid | bge-small | production | 4096 | fixed-512 | fixed-512 | n/a | 0.9119 | +0.0000 | [+0.0000, +0.0037] | 99.17% | +0.0575 | [+0.0433, +0.0729] | 97.50% |
| nq | hybrid | bge-small | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9352 | +0.0000 | [+0.0000, +0.0085] | 99.17% | +0.0414 | [+0.0298, +0.0529] | 95.00% |
| nq | hybrid | bge-small | fair | 128 | fixed-128 | fixed-128 | n/a | 0.2621 | +0.0000 | [+0.0000, +0.0136] | 99.17% | +0.1423 | [+0.1191, +0.1602] | 99.17% |
| nq | hybrid | bge-small | fair | 256 | small-to-big | small-to-big | n/a | 0.3997 | +0.0000 | [+0.0000, +0.0158] | 99.17% | +0.2098 | [+0.1828, +0.2349] | 99.00% |
| nq | hybrid | bge-small | fair | 512 | small-to-big | fixed-256 | n/a | 0.5419 | +0.0008 | [+0.0000, +0.0228] | 99.17% | +0.2473 | [+0.2144, +0.2661] | 98.75% |
| nq | hybrid | bge-small | fair | 1024 | section-aware | small-to-big | n/a | 0.7047 | +0.0008 | [+0.0000, +0.0128] | 95.00% | +0.1957 | [+0.1693, +0.2108] | 95.00% |
| nq | hybrid | bge-small | fair | 2048 | small-to-big | section-aware | n/a | 0.8318 | +0.0084 | [+0.0000, +0.0242] | 99.17% | +0.1283 | [+0.1042, +0.1480] | 98.33% |
| nq | hybrid | bge-small | fair | 4096 | fixed-512 | section-aware | n/a | 0.9137 | +0.0010 | [+0.0000, +0.0117] | 99.17% | +0.0684 | [+0.0501, +0.0790] | 97.50% |
| nq | hybrid | bge-small | fair | 8192 | section-aware | section-aware | n/a | 0.9590 | +0.0000 | [+0.0000, +0.0096] | 99.17% | +0.0344 | [+0.0232, +0.0430] | 95.00% |
| nq | hybrid | nomic | production | 128 | small-to-big | small-to-big | n/a | 0.2634 | +0.0000 | [+0.0000, +0.0127] | 99.17% | +0.1333 | [+0.1113, +0.1532] | 99.17% |
| nq | hybrid | nomic | production | 256 | small-to-big | small-to-big | n/a | 0.4111 | +0.0000 | [+0.0000, +0.0073] | 99.17% | +0.2073 | [+0.1809, +0.2332] | 99.00% |
| nq | hybrid | nomic | production | 512 | small-to-big | section-aware | n/a | 0.5403 | +0.0009 | [+0.0000, +0.0199] | 99.17% | +0.2478 | [+0.2151, +0.2678] | 98.75% |
| nq | hybrid | nomic | production | 1024 | section-aware | section-aware | n/a | 0.7299 | +0.0000 | [+0.0000, +0.0123] | 95.00% | +0.1655 | [+0.1425, +0.1842] | 95.00% |
| nq | hybrid | nomic | production | 2048 | small-to-big | section-aware | n/a | 0.8423 | +0.0071 | [+0.0000, +0.0215] | 99.17% | +0.1059 | [+0.0835, +0.1261] | 98.33% |
| nq | hybrid | nomic | production | 4096 | fixed-512 | fixed-512 | n/a | 0.9059 | +0.0000 | [+0.0000, +0.0079] | 99.17% | +0.0621 | [+0.0470, +0.0772] | 97.50% |
| nq | hybrid | nomic | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9465 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.0320 | [+0.0219, +0.0427] | 95.00% |
| nq | hybrid | nomic | fair | 128 | small-to-big | small-to-big | n/a | 0.2634 | +0.0000 | [+0.0000, +0.0127] | 99.17% | +0.1333 | [+0.1113, +0.1532] | 99.17% |
| nq | hybrid | nomic | fair | 256 | small-to-big | small-to-big | n/a | 0.4111 | +0.0000 | [+0.0000, +0.0073] | 99.17% | +0.2073 | [+0.1809, +0.2332] | 99.00% |
| nq | hybrid | nomic | fair | 512 | small-to-big | section-aware | n/a | 0.5403 | +0.0009 | [+0.0000, +0.0199] | 99.17% | +0.2478 | [+0.2151, +0.2678] | 98.75% |
| nq | hybrid | nomic | fair | 1024 | section-aware | section-aware | n/a | 0.7299 | +0.0000 | [+0.0000, +0.0122] | 95.00% | +0.1719 | [+0.1487, +0.1908] | 95.00% |
| nq | hybrid | nomic | fair | 2048 | small-to-big | section-aware | n/a | 0.8445 | +0.0071 | [+0.0000, +0.0205] | 99.17% | +0.1172 | [+0.0940, +0.1390] | 98.33% |
| nq | hybrid | nomic | fair | 4096 | section-aware | section-aware | n/a | 0.9169 | +0.0000 | [+0.0000, +0.0121] | 99.17% | +0.0676 | [+0.0495, +0.0806] | 97.50% |
| nq | hybrid | nomic | fair | 8192 | section-aware | section-aware | n/a | 0.9639 | +0.0000 | [+0.0000, +0.0080] | 99.17% | +0.0301 | [+0.0196, +0.0381] | 95.00% |
| nq | vector | bge-small | production | 128 | fixed-128 | fixed-128 | n/a | 0.3013 | +0.0000 | [+0.0000, +0.0017] | 99.17% | +0.1571 | [+0.1332, +0.1819] | 99.17% |
| nq | vector | bge-small | production | 256 | fixed-128 | fixed-128 | n/a | 0.4401 | +0.0000 | [+0.0000, +0.0266] | 99.17% | +0.2458 | [+0.2160, +0.2656] | 99.00% |
| nq | vector | bge-small | production | 512 | fixed-128 | small-to-big | n/a | 0.5847 | +0.0072 | [+0.0000, +0.0294] | 99.17% | +0.2680 | [+0.2374, +0.2897] | 98.75% |
| nq | vector | bge-small | production | 1024 | small-to-big | small-to-big | n/a | 0.7571 | +0.0000 | [+0.0000, +0.0148] | 95.00% | +0.1762 | [+0.1524, +0.1943] | 95.00% |
| nq | vector | bge-small | production | 2048 | small-to-big | small-to-big | n/a | 0.8565 | +0.0000 | [+0.0000, +0.0137] | 99.17% | +0.1085 | [+0.0863, +0.1289] | 98.33% |
| nq | vector | bge-small | production | 4096 | fixed-512 | small-to-big | n/a | 0.8936 | +0.0067 | [+0.0000, +0.0220] | 99.17% | +0.0834 | [+0.0649, +0.1002] | 97.50% |
| nq | vector | bge-small | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9033 | +0.0000 | [+0.0000, +0.0227] | 99.17% | +0.0796 | [+0.0617, +0.0905] | 95.00% |
| nq | vector | bge-small | fair | 128 | fixed-128 | fixed-128 | n/a | 0.3013 | +0.0000 | [+0.0000, +0.0017] | 99.17% | +0.1571 | [+0.1332, +0.1819] | 99.17% |
| nq | vector | bge-small | fair | 256 | fixed-128 | fixed-128 | n/a | 0.4401 | +0.0000 | [+0.0000, +0.0266] | 99.17% | +0.2458 | [+0.2160, +0.2656] | 99.00% |
| nq | vector | bge-small | fair | 512 | fixed-128 | small-to-big | n/a | 0.5850 | +0.0072 | [+0.0000, +0.0295] | 99.17% | +0.2677 | [+0.2371, +0.2894] | 98.75% |
| nq | vector | bge-small | fair | 1024 | small-to-big | small-to-big | n/a | 0.7579 | +0.0000 | [+0.0000, +0.0146] | 95.00% | +0.1790 | [+0.1553, +0.1973] | 95.00% |
| nq | vector | bge-small | fair | 2048 | small-to-big | small-to-big | n/a | 0.8636 | +0.0000 | [+0.0000, +0.0125] | 99.17% | +0.1076 | [+0.0857, +0.1284] | 98.33% |
| nq | vector | bge-small | fair | 4096 | small-to-big | small-to-big | n/a | 0.9233 | +0.0000 | [+0.0000, +0.0147] | 99.17% | +0.0672 | [+0.0496, +0.0813] | 97.50% |
| nq | vector | bge-small | fair | 8192 | fixed-512 | small-to-big | n/a | 0.9551 | +0.0012 | [+0.0000, +0.0154] | 99.17% | +0.0407 | [+0.0279, +0.0495] | 95.00% |
| nq | vector | nomic | production | 128 | small-to-big | small-to-big | n/a | 0.3670 | +0.0000 | [+0.0000, +0.0109] | 99.17% | +0.1369 | [+0.1153, +0.1582] | 99.17% |
| nq | vector | nomic | production | 256 | small-to-big | small-to-big | n/a | 0.5196 | +0.0000 | [+0.0000, +0.0133] | 99.17% | +0.2150 | [+0.1890, +0.2414] | 99.00% |
| nq | vector | nomic | production | 512 | small-to-big | section-aware | n/a | 0.6606 | +0.0096 | [+0.0000, +0.0286] | 99.17% | +0.2348 | [+0.2032, +0.2570] | 98.75% |
| nq | vector | nomic | production | 1024 | small-to-big | section-aware | n/a | 0.8225 | +0.0068 | [+0.0000, +0.0181] | 95.00% | +0.1327 | [+0.1121, +0.1515] | 95.00% |
| nq | vector | nomic | production | 2048 | section-aware | section-aware | n/a | 0.8979 | +0.0000 | [+0.0000, +0.0107] | 99.17% | +0.0802 | [+0.0598, +0.0971] | 98.33% |
| nq | vector | nomic | production | 4096 | fixed-512 | fixed-512 | n/a | 0.9254 | +0.0000 | [+0.0000, +0.0122] | 99.17% | +0.0642 | [+0.0456, +0.0731] | 97.50% |
| nq | vector | nomic | production | 8192 | fixed-1024 | fixed-1024 | n/a | 0.9393 | +0.0000 | [+0.0000, +0.0160] | 99.17% | +0.0521 | [+0.0376, +0.0606] | 95.00% |
| nq | vector | nomic | fair | 128 | small-to-big | small-to-big | n/a | 0.3670 | +0.0000 | [+0.0000, +0.0109] | 99.17% | +0.1369 | [+0.1153, +0.1582] | 99.17% |
| nq | vector | nomic | fair | 256 | small-to-big | small-to-big | n/a | 0.5196 | +0.0000 | [+0.0000, +0.0133] | 99.17% | +0.2150 | [+0.1890, +0.2414] | 99.00% |
| nq | vector | nomic | fair | 512 | small-to-big | section-aware | n/a | 0.6606 | +0.0096 | [+0.0000, +0.0286] | 99.17% | +0.2348 | [+0.2032, +0.2570] | 98.75% |
| nq | vector | nomic | fair | 1024 | small-to-big | section-aware | n/a | 0.8225 | +0.0068 | [+0.0000, +0.0181] | 95.00% | +0.1368 | [+0.1160, +0.1556] | 95.00% |
| nq | vector | nomic | fair | 2048 | section-aware | section-aware | n/a | 0.8989 | +0.0000 | [+0.0000, +0.0107] | 99.17% | +0.0828 | [+0.0622, +0.1001] | 98.33% |
| nq | vector | nomic | fair | 4096 | section-aware | small-to-big | n/a | 0.9469 | +0.0039 | [+0.0000, +0.0110] | 99.17% | +0.0471 | [+0.0327, +0.0608] | 97.50% |
| nq | vector | nomic | fair | 8192 | section-aware | section-aware | n/a | 0.9649 | +0.0000 | [+0.0000, +0.0077] | 99.17% | +0.0333 | [+0.0216, +0.0410] | 95.00% |
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
| pooled | hybrid-rerank | bge-small | production | 128 | fixed-64 | 0.1222 | -0.0308 | [-0.0435, -0.0177] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 128 | fixed-128 | 0.1210 | -0.0320 | [-0.0447, -0.0195] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 128 | section-aware | 0.0390 | -0.1140 | [-0.1290, -0.0997] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.1530 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | production | 256 | fixed-64 | 0.1753 | -0.0555 | [-0.0695, -0.0419] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 256 | fixed-128 | 0.1995 | -0.0313 | [-0.0455, -0.0177] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 256 | fixed-256 | 0.1762 | -0.0545 | [-0.0713, -0.0376] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 256 | section-aware | 0.1195 | -0.1113 | [-0.1271, -0.0952] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.2308 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | production | 512 | fixed-64 | 0.2325 | -0.0875 | [-0.1032, -0.0726] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 512 | fixed-128 | 0.2743 | -0.0457 | [-0.0615, -0.0310] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 512 | fixed-256 | 0.2734 | -0.0466 | [-0.0639, -0.0308] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 512 | fixed-512 | 0.2567 | -0.0633 | [-0.0823, -0.0452] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 512 | section-aware | 0.3139 | -0.0061 | [-0.0205, +0.0000] | 98.33% | no | 0.1517 |
| pooled | hybrid-rerank | bge-small | production | 512 | small-to-big | 0.3200 | +0.0000 | [-0.0081, +0.0000] | 98.33% | no | 0.8483 |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.2325 | -0.1931 | [-0.2064, -0.1798] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.3491 | -0.0765 | [-0.0888, -0.0642] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.3712 | -0.0544 | [-0.0662, -0.0428] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.3677 | -0.0579 | [-0.0710, -0.0453] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.4256 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9997 |
| pooled | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.4082 | -0.0174 | [-0.0277, -0.0070] | 95.00% | yes | 0.0003 |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.3358 | -0.0898 | [-0.1055, -0.0744] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | fixed-64 | 0.2325 | -0.2598 | [-0.2763, -0.2429] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | fixed-128 | 0.3491 | -0.1431 | [-0.1577, -0.1283] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | fixed-256 | 0.4446 | -0.0476 | [-0.0607, -0.0346] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | fixed-512 | 0.4459 | -0.0464 | [-0.0610, -0.0318] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.4923 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | small-to-big | 0.4744 | -0.0179 | [-0.0307, -0.0055] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 2048 | fixed-1024 | 0.4330 | -0.0592 | [-0.0756, -0.0427] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-64 | 0.2325 | -0.2786 | [-0.2947, -0.2641] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-128 | 0.3491 | -0.1620 | [-0.1765, -0.1494] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-256 | 0.4446 | -0.0665 | [-0.0781, -0.0565] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-512 | 0.5111 | +0.0000 | [-0.0056, +0.0000] | 95.00% | no | 0.7996 |
| pooled | hybrid-rerank | bge-small | production | 4096 | section-aware | 0.5049 | -0.0062 | [-0.0194, +0.0000] | 98.33% | no | 0.1153 |
| pooled | hybrid-rerank | bge-small | production | 4096 | small-to-big | 0.4905 | -0.0206 | [-0.0367, -0.0072] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 4096 | fixed-1024 | 0.5044 | -0.0067 | [-0.0188, +0.0000] | 97.50% | no | 0.0851 |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-64 | 0.2325 | -0.3160 | [-0.3310, -0.3008] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-128 | 0.3491 | -0.1994 | [-0.2135, -0.1856] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-256 | 0.4446 | -0.1039 | [-0.1156, -0.0920] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-512 | 0.5111 | -0.0374 | [-0.0485, -0.0264] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | section-aware | 0.5049 | -0.0437 | [-0.0590, -0.0286] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | small-to-big | 0.4905 | -0.0580 | [-0.0749, -0.0408] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.5485 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | fair | 128 | fixed-64 | 0.1222 | -0.0308 | [-0.0435, -0.0177] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 128 | fixed-128 | 0.1210 | -0.0320 | [-0.0447, -0.0195] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 128 | section-aware | 0.0390 | -0.1140 | [-0.1290, -0.0997] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.1530 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | fair | 256 | fixed-64 | 0.1753 | -0.0555 | [-0.0695, -0.0419] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 256 | fixed-128 | 0.1995 | -0.0313 | [-0.0455, -0.0177] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 256 | fixed-256 | 0.1762 | -0.0545 | [-0.0713, -0.0376] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 256 | section-aware | 0.1195 | -0.1113 | [-0.1271, -0.0952] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.2308 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | fair | 512 | fixed-64 | 0.2325 | -0.0875 | [-0.1032, -0.0726] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 512 | fixed-128 | 0.2743 | -0.0457 | [-0.0615, -0.0310] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 512 | fixed-256 | 0.2734 | -0.0466 | [-0.0639, -0.0308] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 512 | fixed-512 | 0.2567 | -0.0633 | [-0.0823, -0.0452] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 512 | section-aware | 0.3139 | -0.0061 | [-0.0212, +0.0000] | 98.75% | no | 0.1517 |
| pooled | hybrid-rerank | bge-small | fair | 512 | small-to-big | 0.3200 | +0.0000 | [-0.0081, +0.0000] | 98.33% | no | 0.8483 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.2891 | -0.1366 | [-0.1494, -0.1238] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.3491 | -0.0766 | [-0.0889, -0.0642] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.3712 | -0.0545 | [-0.0664, -0.0429] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.3677 | -0.0580 | [-0.0710, -0.0454] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.4257 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9997 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.4082 | -0.0175 | [-0.0278, -0.0071] | 95.00% | yes | 0.0003 |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.3358 | -0.0899 | [-0.1055, -0.0744] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | fixed-64 | 0.3306 | -0.1653 | [-0.1806, -0.1498] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | fixed-128 | 0.4078 | -0.0881 | [-0.1018, -0.0737] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | fixed-256 | 0.4447 | -0.0512 | [-0.0643, -0.0382] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | fixed-512 | 0.4461 | -0.0498 | [-0.0643, -0.0350] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.4959 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 1.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | small-to-big | 0.4767 | -0.0192 | [-0.0320, -0.0064] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 2048 | fixed-1024 | 0.4330 | -0.0629 | [-0.0793, -0.0462] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | fixed-64 | 0.3891 | -0.1448 | [-0.1584, -0.1312] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | fixed-128 | 0.4440 | -0.0899 | [-0.1024, -0.0777] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | fixed-256 | 0.4925 | -0.0414 | [-0.0524, -0.0304] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | fixed-512 | 0.5117 | -0.0222 | [-0.0346, -0.0101] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.5339 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9998 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | small-to-big | 0.5181 | -0.0158 | [-0.0272, -0.0042] | 99.00% | yes | 0.0002 |
| pooled | hybrid-rerank | bge-small | fair | 4096 | fixed-1024 | 0.5044 | -0.0295 | [-0.0440, -0.0148] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | fixed-64 | 0.4393 | -0.1176 | [-0.1296, -0.1065] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | fixed-128 | 0.4962 | -0.0607 | [-0.0712, -0.0514] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | fixed-256 | 0.5198 | -0.0372 | [-0.0467, -0.0290] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | fixed-512 | 0.5445 | -0.0125 | [-0.0231, -0.0035] | 95.00% | yes | 0.0040 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.5570 | +0.0000 | [-0.0081, +0.0000] | 98.75% | no | 0.8597 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | small-to-big | 0.5460 | -0.0110 | [-0.0226, -0.0006] | 98.75% | yes | 0.0042 |
| pooled | hybrid-rerank | bge-small | fair | 8192 | fixed-1024 | 0.5501 | -0.0068 | [-0.0188, +0.0000] | 95.00% | no | 0.1321 |
| pooled | hybrid-rerank | nomic | production | 128 | fixed-64 | 0.1225 | -0.0288 | [-0.0415, -0.0158] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 128 | fixed-128 | 0.1230 | -0.0282 | [-0.0408, -0.0154] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 128 | section-aware | 0.0398 | -0.1115 | [-0.1264, -0.0970] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 128 | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | production | 256 | fixed-64 | 0.1777 | -0.0519 | [-0.0657, -0.0383] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 256 | fixed-128 | 0.1999 | -0.0296 | [-0.0439, -0.0159] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 256 | fixed-256 | 0.1764 | -0.0531 | [-0.0703, -0.0363] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 256 | section-aware | 0.1188 | -0.1108 | [-0.1268, -0.0944] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 256 | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | production | 512 | fixed-64 | 0.2351 | -0.0823 | [-0.0984, -0.0689] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 512 | fixed-128 | 0.2742 | -0.0431 | [-0.0599, -0.0293] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 512 | fixed-256 | 0.2727 | -0.0446 | [-0.0616, -0.0304] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 512 | fixed-512 | 0.2604 | -0.0569 | [-0.0758, -0.0413] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 512 | section-aware | 0.3147 | -0.0027 | [-0.0171, +0.0000] | 98.33% | no | 0.3278 |
| pooled | hybrid-rerank | nomic | production | 512 | small-to-big | 0.3173 | +0.0000 | [-0.0116, +0.0000] | 98.33% | no | 0.6722 |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.2351 | -0.1912 | [-0.2049, -0.1776] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.3519 | -0.0744 | [-0.0867, -0.0620] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.3686 | -0.0576 | [-0.0701, -0.0451] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.3702 | -0.0561 | [-0.0691, -0.0429] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 1024 | section-aware | 0.4262 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9985 |
| pooled | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.4096 | -0.0167 | [-0.0273, -0.0060] | 95.00% | yes | 0.0015 |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.3356 | -0.0906 | [-0.1065, -0.0747] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 2048 | fixed-64 | 0.2351 | -0.2573 | [-0.2739, -0.2400] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 2048 | fixed-128 | 0.3519 | -0.1405 | [-0.1555, -0.1256] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 2048 | fixed-256 | 0.4426 | -0.0498 | [-0.0631, -0.0362] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 2048 | fixed-512 | 0.4512 | -0.0411 | [-0.0558, -0.0263] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 2048 | section-aware | 0.4923 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9998 |
| pooled | hybrid-rerank | nomic | production | 2048 | small-to-big | 0.4760 | -0.0164 | [-0.0288, -0.0043] | 99.00% | yes | 0.0002 |
| pooled | hybrid-rerank | nomic | production | 2048 | fixed-1024 | 0.4353 | -0.0570 | [-0.0740, -0.0401] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-64 | 0.2351 | -0.2765 | [-0.2927, -0.2614] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-128 | 0.3519 | -0.1597 | [-0.1741, -0.1470] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-256 | 0.4426 | -0.0690 | [-0.0805, -0.0589] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.5115 | +0.0000 | [-0.0052, +0.0000] | 95.00% | no | 0.8115 |
| pooled | hybrid-rerank | nomic | production | 4096 | section-aware | 0.5040 | -0.0075 | [-0.0214, +0.0000] | 98.33% | no | 0.0788 |
| pooled | hybrid-rerank | nomic | production | 4096 | small-to-big | 0.4944 | -0.0172 | [-0.0320, -0.0045] | 98.75% | yes | 0.0004 |
| pooled | hybrid-rerank | nomic | production | 4096 | fixed-1024 | 0.5055 | -0.0060 | [-0.0179, +0.0000] | 97.50% | no | 0.1093 |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-64 | 0.2351 | -0.3222 | [-0.3374, -0.3069] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-128 | 0.3519 | -0.2054 | [-0.2197, -0.1915] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-256 | 0.4426 | -0.1147 | [-0.1269, -0.1029] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-512 | 0.5115 | -0.0458 | [-0.0570, -0.0349] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | section-aware | 0.5040 | -0.0533 | [-0.0687, -0.0380] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | small-to-big | 0.4944 | -0.0629 | [-0.0798, -0.0463] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.5573 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | fixed-64 | 0.1225 | -0.0288 | [-0.0415, -0.0158] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | fixed-128 | 0.1230 | -0.0282 | [-0.0408, -0.0154] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | section-aware | 0.0398 | -0.1115 | [-0.1264, -0.0970] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-64 | 0.1777 | -0.0519 | [-0.0657, -0.0383] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-128 | 0.1999 | -0.0296 | [-0.0439, -0.0159] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-256 | 0.1764 | -0.0531 | [-0.0703, -0.0363] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | section-aware | 0.1188 | -0.1108 | [-0.1268, -0.0944] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-64 | 0.2351 | -0.0823 | [-0.0984, -0.0689] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-128 | 0.2742 | -0.0431 | [-0.0599, -0.0293] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-256 | 0.2727 | -0.0446 | [-0.0616, -0.0304] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-512 | 0.2604 | -0.0569 | [-0.0758, -0.0413] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | section-aware | 0.3147 | -0.0027 | [-0.0176, +0.0000] | 98.75% | no | 0.3278 |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.3173 | +0.0000 | [-0.0129, +0.0000] | 99.00% | no | 0.6722 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.2931 | -0.1338 | [-0.1466, -0.1208] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.3519 | -0.0750 | [-0.0874, -0.0626] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.3686 | -0.0582 | [-0.0706, -0.0459] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.3702 | -0.0567 | [-0.0697, -0.0435] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9990 |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.4096 | -0.0173 | [-0.0280, -0.0065] | 95.00% | yes | 0.0010 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.3356 | -0.0912 | [-0.1070, -0.0753] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 0.3347 | -0.1609 | [-0.1762, -0.1458] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-128 | 0.4123 | -0.0833 | [-0.0977, -0.0691] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 0.4426 | -0.0530 | [-0.0664, -0.0393] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 0.4512 | -0.0444 | [-0.0592, -0.0295] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.4956 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9998 |
| pooled | hybrid-rerank | nomic | fair | 2048 | small-to-big | 0.4789 | -0.0167 | [-0.0296, -0.0042] | 99.17% | yes | 0.0002 |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 0.4353 | -0.0603 | [-0.0772, -0.0433] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 0.3976 | -0.1358 | [-0.1497, -0.1223] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-128 | 0.4472 | -0.0862 | [-0.0990, -0.0740] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 0.4923 | -0.0411 | [-0.0526, -0.0296] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 0.5120 | -0.0214 | [-0.0342, -0.0086] | 97.50% | yes | 0.0001 |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.5334 | +0.0000 | [-0.0030, +0.0000] | 98.75% | no | 0.9673 |
| pooled | hybrid-rerank | nomic | fair | 4096 | small-to-big | 0.5249 | -0.0085 | [-0.0202, +0.0000] | 99.00% | no | 0.0326 |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 0.5055 | -0.0279 | [-0.0423, -0.0134] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 0.4529 | -0.1055 | [-0.1196, -0.0968] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-128 | 0.5062 | -0.0522 | [-0.0653, -0.0448] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 0.5224 | -0.0359 | [-0.0474, -0.0301] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 0.5513 | -0.0070 | [-0.0185, -0.0011] | 95.00% | yes | 0.0135 |
| pooled | hybrid-rerank | nomic | fair | 8192 | section-aware | 0.5582 | -0.0001 | [-0.0154, +0.0000] | 98.75% | no | 0.4692 |
| pooled | hybrid-rerank | nomic | fair | 8192 | small-to-big | 0.5530 | -0.0054 | [-0.0204, +0.0000] | 99.00% | no | 0.0360 |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.5584 | +0.0000 | [-0.0119, +0.0000] | 95.00% | no | 0.4813 |
| pooled | bm25 | - | production | 128 | fixed-64 | 0.0665 | -0.0172 | [-0.0263, -0.0098] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | production | 128 | fixed-128 | 0.0820 | -0.0018 | [-0.0106, +0.0000] | 98.33% | no | 0.3168 |
| pooled | bm25 | - | production | 128 | section-aware | 0.0236 | -0.0601 | [-0.0722, -0.0502] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | production | 128 | small-to-big | 0.0838 | +0.0000 | [-0.0075, +0.0000] | 98.75% | no | 0.6832 |
| pooled | bm25 | - | production | 256 | fixed-64 | 0.1079 | -0.0210 | [-0.0319, -0.0128] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 256 | fixed-128 | 0.1278 | -0.0012 | [-0.0110, +0.0000] | 98.33% | no | 0.3919 |
| pooled | bm25 | - | production | 256 | fixed-256 | 0.1190 | -0.0099 | [-0.0213, -0.0014] | 97.50% | yes | 0.0049 |
| pooled | bm25 | - | production | 256 | section-aware | 0.0780 | -0.0509 | [-0.0650, -0.0390] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 256 | small-to-big | 0.1289 | +0.0000 | [-0.0094, +0.0000] | 98.75% | no | 0.6032 |
| pooled | bm25 | - | production | 512 | fixed-64 | 0.1581 | -0.0362 | [-0.0496, -0.0261] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | production | 512 | fixed-128 | 0.1901 | -0.0042 | [-0.0162, +0.0000] | 98.33% | no | 0.1494 |
| pooled | bm25 | - | production | 512 | fixed-256 | 0.1893 | -0.0050 | [-0.0157, +0.0000] | 95.00% | no | 0.1257 |
| pooled | bm25 | - | production | 512 | fixed-512 | 0.1753 | -0.0190 | [-0.0349, -0.0060] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | production | 512 | section-aware | 0.1854 | -0.0089 | [-0.0214, +0.0000] | 97.50% | no | 0.0269 |
| pooled | bm25 | - | production | 512 | small-to-big | 0.1943 | +0.0000 | [-0.0100, +0.0000] | 98.75% | no | 0.6980 |
| pooled | bm25 | - | production | 1024 | fixed-64 | 0.1581 | -0.1315 | [-0.1440, -0.1192] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 1024 | fixed-128 | 0.2622 | -0.0273 | [-0.0385, -0.0161] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 1024 | fixed-256 | 0.2697 | -0.0199 | [-0.0309, -0.0088] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 1024 | fixed-512 | 0.2668 | -0.0228 | [-0.0344, -0.0112] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 1024 | section-aware | 0.2896 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9873 |
| pooled | bm25 | - | production | 1024 | small-to-big | 0.2772 | -0.0124 | [-0.0233, -0.0013] | 95.00% | yes | 0.0127 |
| pooled | bm25 | - | production | 1024 | fixed-1024 | 0.2337 | -0.0559 | [-0.0704, -0.0412] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 2048 | fixed-64 | 0.1581 | -0.2189 | [-0.2355, -0.2030] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | production | 2048 | fixed-128 | 0.2622 | -0.1147 | [-0.1308, -0.0996] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | production | 2048 | fixed-256 | 0.3546 | -0.0223 | [-0.0361, -0.0093] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 2048 | fixed-512 | 0.3608 | -0.0161 | [-0.0291, -0.0037] | 97.50% | yes | 0.0019 |
| pooled | bm25 | - | production | 2048 | section-aware | 0.3769 | +0.0000 | [-0.0014, +0.0000] | 97.50% | no | 0.9744 |
| pooled | bm25 | - | production | 2048 | small-to-big | 0.3668 | -0.0101 | [-0.0233, +0.0000] | 98.75% | no | 0.0237 |
| pooled | bm25 | - | production | 2048 | fixed-1024 | 0.3396 | -0.0373 | [-0.0539, -0.0212] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | fixed-64 | 0.1581 | -0.2808 | [-0.2964, -0.2653] | 97.50% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | fixed-128 | 0.2622 | -0.1767 | [-0.1926, -0.1605] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | fixed-256 | 0.3546 | -0.0843 | [-0.0970, -0.0719] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | fixed-512 | 0.4389 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9852 |
| pooled | bm25 | - | production | 4096 | section-aware | 0.4049 | -0.0340 | [-0.0471, -0.0206] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | small-to-big | 0.3971 | -0.0417 | [-0.0567, -0.0268] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | production | 4096 | fixed-1024 | 0.4287 | -0.0101 | [-0.0207, +0.0000] | 97.50% | no | 0.0148 |
| pooled | bm25 | - | production | 8192 | fixed-64 | 0.1581 | -0.3372 | [-0.3521, -0.3224] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | fixed-128 | 0.2622 | -0.2331 | [-0.2512, -0.2151] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | fixed-256 | 0.3546 | -0.1407 | [-0.1562, -0.1255] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | fixed-512 | 0.4389 | -0.0564 | [-0.0676, -0.0457] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | section-aware | 0.4049 | -0.0904 | [-0.1059, -0.0753] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | small-to-big | 0.3971 | -0.0981 | [-0.1151, -0.0819] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | production | 8192 | fixed-1024 | 0.4953 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| pooled | bm25 | - | fair | 128 | fixed-64 | 0.0665 | -0.0172 | [-0.0263, -0.0098] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | fair | 128 | fixed-128 | 0.0820 | -0.0018 | [-0.0106, +0.0000] | 98.33% | no | 0.3168 |
| pooled | bm25 | - | fair | 128 | section-aware | 0.0236 | -0.0601 | [-0.0722, -0.0502] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | fair | 128 | small-to-big | 0.0838 | +0.0000 | [-0.0080, +0.0000] | 99.17% | no | 0.6832 |
| pooled | bm25 | - | fair | 256 | fixed-64 | 0.1079 | -0.0210 | [-0.0319, -0.0128] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 256 | fixed-128 | 0.1278 | -0.0012 | [-0.0110, +0.0000] | 98.33% | no | 0.3919 |
| pooled | bm25 | - | fair | 256 | fixed-256 | 0.1190 | -0.0099 | [-0.0213, -0.0014] | 97.50% | yes | 0.0049 |
| pooled | bm25 | - | fair | 256 | section-aware | 0.0780 | -0.0509 | [-0.0650, -0.0390] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 256 | small-to-big | 0.1289 | +0.0000 | [-0.0100, +0.0000] | 99.17% | no | 0.6032 |
| pooled | bm25 | - | fair | 512 | fixed-64 | 0.1581 | -0.0362 | [-0.0496, -0.0261] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | fair | 512 | fixed-128 | 0.1901 | -0.0042 | [-0.0162, +0.0000] | 98.33% | no | 0.1494 |
| pooled | bm25 | - | fair | 512 | fixed-256 | 0.1893 | -0.0050 | [-0.0157, +0.0000] | 95.00% | no | 0.1257 |
| pooled | bm25 | - | fair | 512 | fixed-512 | 0.1753 | -0.0190 | [-0.0349, -0.0060] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | fair | 512 | section-aware | 0.1854 | -0.0089 | [-0.0226, +0.0000] | 98.75% | no | 0.0269 |
| pooled | bm25 | - | fair | 512 | small-to-big | 0.1943 | +0.0000 | [-0.0107, +0.0000] | 99.17% | no | 0.6980 |
| pooled | bm25 | - | fair | 1024 | fixed-64 | 0.2136 | -0.0759 | [-0.0880, -0.0640] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 1024 | fixed-128 | 0.2622 | -0.0273 | [-0.0385, -0.0161] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 1024 | fixed-256 | 0.2697 | -0.0199 | [-0.0309, -0.0088] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 1024 | fixed-512 | 0.2668 | -0.0228 | [-0.0344, -0.0112] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 1024 | section-aware | 0.2896 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9873 |
| pooled | bm25 | - | fair | 1024 | small-to-big | 0.2772 | -0.0124 | [-0.0233, -0.0013] | 95.00% | yes | 0.0127 |
| pooled | bm25 | - | fair | 1024 | fixed-1024 | 0.2337 | -0.0559 | [-0.0704, -0.0412] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 2048 | fixed-64 | 0.2674 | -0.1147 | [-0.1297, -0.1008] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | fair | 2048 | fixed-128 | 0.3276 | -0.0545 | [-0.0692, -0.0407] | 99.17% | yes | 0.0000 |
| pooled | bm25 | - | fair | 2048 | fixed-256 | 0.3546 | -0.0275 | [-0.0410, -0.0142] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 2048 | fixed-512 | 0.3608 | -0.0213 | [-0.0353, -0.0077] | 98.33% | yes | 0.0001 |
| pooled | bm25 | - | fair | 2048 | section-aware | 0.3821 | +0.0000 | [-0.0006, +0.0000] | 98.75% | no | 0.9912 |
| pooled | bm25 | - | fair | 2048 | small-to-big | 0.3696 | -0.0125 | [-0.0269, +0.0000] | 99.17% | no | 0.0087 |
| pooled | bm25 | - | fair | 2048 | fixed-1024 | 0.3396 | -0.0425 | [-0.0592, -0.0260] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | fair | 4096 | fixed-64 | 0.3230 | -0.1270 | [-0.1409, -0.1136] | 97.50% | yes | 0.0000 |
| pooled | bm25 | - | fair | 4096 | fixed-128 | 0.3855 | -0.0645 | [-0.0782, -0.0511] | 99.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 4096 | fixed-256 | 0.4219 | -0.0282 | [-0.0404, -0.0162] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | fair | 4096 | fixed-512 | 0.4395 | -0.0105 | [-0.0210, -0.0002] | 95.00% | yes | 0.0225 |
| pooled | bm25 | - | fair | 4096 | section-aware | 0.4500 | +0.0000 | [-0.0031, +0.0000] | 98.75% | no | 0.9667 |
| pooled | bm25 | - | fair | 4096 | small-to-big | 0.4399 | -0.0101 | [-0.0214, +0.0000] | 99.17% | no | 0.0107 |
| pooled | bm25 | - | fair | 4096 | fixed-1024 | 0.4287 | -0.0213 | [-0.0359, -0.0075] | 97.50% | yes | 0.0001 |
| pooled | bm25 | - | fair | 8192 | fixed-64 | 0.3799 | -0.1306 | [-0.1422, -0.1191] | 95.00% | yes | 0.0000 |
| pooled | bm25 | - | fair | 8192 | fixed-128 | 0.4449 | -0.0655 | [-0.0786, -0.0526] | 98.75% | yes | 0.0000 |
| pooled | bm25 | - | fair | 8192 | fixed-256 | 0.4844 | -0.0260 | [-0.0371, -0.0151] | 98.33% | yes | 0.0000 |
| pooled | bm25 | - | fair | 8192 | fixed-512 | 0.4972 | -0.0133 | [-0.0249, -0.0018] | 97.50% | yes | 0.0045 |
| pooled | bm25 | - | fair | 8192 | section-aware | 0.5104 | +0.0000 | [-0.0030, +0.0000] | 98.75% | no | 0.9741 |
| pooled | bm25 | - | fair | 8192 | small-to-big | 0.5003 | -0.0102 | [-0.0218, +0.0000] | 99.17% | no | 0.0074 |
| pooled | bm25 | - | fair | 8192 | fixed-1024 | 0.4973 | -0.0131 | [-0.0252, -0.0014] | 95.00% | yes | 0.0140 |
| pooled | hybrid | bge-small | production | 128 | fixed-64 | 0.0961 | -0.0162 | [-0.0273, -0.0074] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 128 | fixed-128 | 0.1123 | +0.0000 | [-0.0079, +0.0000] | 97.50% | no | 0.6532 |
| pooled | hybrid | bge-small | production | 128 | section-aware | 0.0289 | -0.0834 | [-0.0975, -0.0720] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 128 | small-to-big | 0.1107 | -0.0017 | [-0.0122, +0.0000] | 98.75% | no | 0.3468 |
| pooled | hybrid | bge-small | production | 256 | fixed-64 | 0.1464 | -0.0265 | [-0.0392, -0.0151] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 256 | fixed-128 | 0.1658 | -0.0071 | [-0.0179, +0.0000] | 97.50% | no | 0.0705 |
| pooled | hybrid | bge-small | production | 256 | fixed-256 | 0.1502 | -0.0227 | [-0.0367, -0.0088] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 256 | section-aware | 0.0937 | -0.0792 | [-0.0941, -0.0649] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 256 | small-to-big | 0.1729 | +0.0000 | [-0.0053, +0.0000] | 98.75% | no | 0.9295 |
| pooled | hybrid | bge-small | production | 512 | fixed-64 | 0.2011 | -0.0475 | [-0.0620, -0.0342] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 512 | fixed-128 | 0.2347 | -0.0140 | [-0.0275, -0.0012] | 98.33% | yes | 0.0042 |
| pooled | hybrid | bge-small | production | 512 | fixed-256 | 0.2349 | -0.0138 | [-0.0255, -0.0023] | 95.00% | yes | 0.0088 |
| pooled | hybrid | bge-small | production | 512 | fixed-512 | 0.2015 | -0.0472 | [-0.0642, -0.0308] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 512 | section-aware | 0.2356 | -0.0131 | [-0.0270, +0.0000] | 97.50% | no | 0.0161 |
| pooled | hybrid | bge-small | production | 512 | small-to-big | 0.2487 | +0.0000 | [-0.0031, +0.0000] | 98.75% | no | 0.9709 |
| pooled | hybrid | bge-small | production | 1024 | fixed-64 | 0.2011 | -0.1396 | [-0.1530, -0.1302] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 1024 | fixed-128 | 0.3109 | -0.0299 | [-0.0426, -0.0213] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 1024 | fixed-256 | 0.3158 | -0.0250 | [-0.0377, -0.0159] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 1024 | fixed-512 | 0.2988 | -0.0420 | [-0.0557, -0.0320] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 1024 | section-aware | 0.3407 | +0.0000 | [-0.0103, +0.0000] | 95.00% | no | 0.5879 |
| pooled | hybrid | bge-small | production | 1024 | small-to-big | 0.3396 | -0.0011 | [-0.0124, +0.0000] | 95.00% | no | 0.4121 |
| pooled | hybrid | bge-small | production | 1024 | fixed-1024 | 0.2437 | -0.0971 | [-0.1131, -0.0852] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 2048 | fixed-64 | 0.2011 | -0.2149 | [-0.2308, -0.2012] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 2048 | fixed-128 | 0.3109 | -0.1052 | [-0.1203, -0.0922] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 2048 | fixed-256 | 0.3969 | -0.0192 | [-0.0314, -0.0084] | 97.50% | yes | 0.0002 |
| pooled | hybrid | bge-small | production | 2048 | fixed-512 | 0.3816 | -0.0344 | [-0.0491, -0.0215] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 2048 | section-aware | 0.4114 | -0.0047 | [-0.0162, +0.0000] | 97.50% | no | 0.1794 |
| pooled | hybrid | bge-small | production | 2048 | small-to-big | 0.4160 | +0.0000 | [-0.0083, +0.0000] | 98.75% | no | 0.8204 |
| pooled | hybrid | bge-small | production | 2048 | fixed-1024 | 0.3364 | -0.0796 | [-0.0973, -0.0634] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | fixed-64 | 0.2011 | -0.2562 | [-0.2727, -0.2403] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | fixed-128 | 0.3109 | -0.1465 | [-0.1635, -0.1305] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | fixed-256 | 0.3969 | -0.0605 | [-0.0736, -0.0478] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | fixed-512 | 0.4574 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 1.0000 |
| pooled | hybrid | bge-small | production | 4096 | section-aware | 0.4345 | -0.0229 | [-0.0373, -0.0085] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | small-to-big | 0.4344 | -0.0230 | [-0.0383, -0.0076] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 4096 | fixed-1024 | 0.4115 | -0.0458 | [-0.0581, -0.0336] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | fixed-64 | 0.2011 | -0.2766 | [-0.2918, -0.2615] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | fixed-128 | 0.3109 | -0.1669 | [-0.1856, -0.1488] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | fixed-256 | 0.3969 | -0.0809 | [-0.0968, -0.0656] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | fixed-512 | 0.4574 | -0.0204 | [-0.0322, -0.0087] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | section-aware | 0.4345 | -0.0433 | [-0.0600, -0.0267] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | small-to-big | 0.4344 | -0.0434 | [-0.0620, -0.0247] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | production | 8192 | fixed-1024 | 0.4778 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 1.0000 |
| pooled | hybrid | bge-small | fair | 128 | fixed-64 | 0.0961 | -0.0162 | [-0.0273, -0.0074] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 128 | fixed-128 | 0.1123 | +0.0000 | [-0.0079, +0.0000] | 97.50% | no | 0.6532 |
| pooled | hybrid | bge-small | fair | 128 | section-aware | 0.0289 | -0.0834 | [-0.0975, -0.0720] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 128 | small-to-big | 0.1107 | -0.0017 | [-0.0128, +0.0000] | 99.17% | no | 0.3468 |
| pooled | hybrid | bge-small | fair | 256 | fixed-64 | 0.1464 | -0.0265 | [-0.0392, -0.0151] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 256 | fixed-128 | 0.1658 | -0.0071 | [-0.0179, +0.0000] | 97.50% | no | 0.0705 |
| pooled | hybrid | bge-small | fair | 256 | fixed-256 | 0.1502 | -0.0227 | [-0.0367, -0.0088] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 256 | section-aware | 0.0937 | -0.0792 | [-0.0941, -0.0649] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 256 | small-to-big | 0.1729 | +0.0000 | [-0.0061, +0.0000] | 99.17% | no | 0.9295 |
| pooled | hybrid | bge-small | fair | 512 | fixed-64 | 0.2012 | -0.0475 | [-0.0619, -0.0341] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 512 | fixed-128 | 0.2347 | -0.0140 | [-0.0275, -0.0012] | 98.33% | yes | 0.0042 |
| pooled | hybrid | bge-small | fair | 512 | fixed-256 | 0.2349 | -0.0138 | [-0.0255, -0.0023] | 95.00% | yes | 0.0088 |
| pooled | hybrid | bge-small | fair | 512 | fixed-512 | 0.2015 | -0.0472 | [-0.0642, -0.0308] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 512 | section-aware | 0.2356 | -0.0131 | [-0.0287, +0.0000] | 98.75% | no | 0.0161 |
| pooled | hybrid | bge-small | fair | 512 | small-to-big | 0.2487 | +0.0000 | [-0.0042, +0.0000] | 99.17% | no | 0.9709 |
| pooled | hybrid | bge-small | fair | 1024 | fixed-64 | 0.2652 | -0.0759 | [-0.0886, -0.0668] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 1024 | fixed-128 | 0.3110 | -0.0300 | [-0.0427, -0.0213] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 1024 | fixed-256 | 0.3158 | -0.0253 | [-0.0379, -0.0161] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 1024 | fixed-512 | 0.2988 | -0.0423 | [-0.0558, -0.0322] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 1024 | section-aware | 0.3411 | +0.0000 | [-0.0100, +0.0000] | 95.00% | no | 0.6071 |
| pooled | hybrid | bge-small | fair | 1024 | small-to-big | 0.3396 | -0.0014 | [-0.0128, +0.0000] | 95.00% | no | 0.3929 |
| pooled | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.2437 | -0.0974 | [-0.1131, -0.0854] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 2048 | fixed-64 | 0.3306 | -0.0908 | [-0.1066, -0.0796] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 2048 | fixed-128 | 0.3764 | -0.0451 | [-0.0614, -0.0342] | 99.17% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 2048 | fixed-256 | 0.3973 | -0.0241 | [-0.0388, -0.0133] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 2048 | fixed-512 | 0.3816 | -0.0398 | [-0.0555, -0.0282] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 2048 | section-aware | 0.4206 | -0.0008 | [-0.0138, +0.0000] | 98.75% | no | 0.4459 |
| pooled | hybrid | bge-small | fair | 2048 | small-to-big | 0.4214 | +0.0000 | [-0.0134, +0.0000] | 99.17% | no | 0.5541 |
| pooled | hybrid | bge-small | fair | 2048 | fixed-1024 | 0.3364 | -0.0850 | [-0.1035, -0.0701] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 4096 | fixed-64 | 0.3891 | -0.1007 | [-0.1143, -0.0875] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 4096 | fixed-128 | 0.4440 | -0.0457 | [-0.0600, -0.0326] | 99.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 4096 | fixed-256 | 0.4639 | -0.0258 | [-0.0379, -0.0146] | 98.33% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 4096 | fixed-512 | 0.4589 | -0.0308 | [-0.0439, -0.0182] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 4096 | section-aware | 0.4898 | +0.0000 | [-0.0050, +0.0000] | 98.75% | no | 0.9247 |
| pooled | hybrid | bge-small | fair | 4096 | small-to-big | 0.4829 | -0.0069 | [-0.0187, +0.0000] | 99.17% | no | 0.0753 |
| pooled | hybrid | bge-small | fair | 4096 | fixed-1024 | 0.4115 | -0.0782 | [-0.0937, -0.0631] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 8192 | fixed-64 | 0.4393 | -0.1105 | [-0.1223, -0.0988] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 8192 | fixed-128 | 0.4962 | -0.0536 | [-0.0667, -0.0412] | 98.75% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 8192 | fixed-256 | 0.5198 | -0.0301 | [-0.0407, -0.0197] | 97.50% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 8192 | fixed-512 | 0.5089 | -0.0409 | [-0.0518, -0.0301] | 95.00% | yes | 0.0000 |
| pooled | hybrid | bge-small | fair | 8192 | section-aware | 0.5498 | +0.0000 | [-0.0040, +0.0000] | 98.75% | no | 0.9442 |
| pooled | hybrid | bge-small | fair | 8192 | small-to-big | 0.5429 | -0.0069 | [-0.0186, +0.0000] | 99.17% | no | 0.0558 |
| pooled | hybrid | bge-small | fair | 8192 | fixed-1024 | 0.4806 | -0.0692 | [-0.0829, -0.0561] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 128 | fixed-64 | 0.1009 | -0.0179 | [-0.0291, -0.0074] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 128 | fixed-128 | 0.1097 | -0.0092 | [-0.0180, -0.0003] | 97.50% | yes | 0.0102 |
| pooled | hybrid | nomic | production | 128 | section-aware | 0.0284 | -0.0904 | [-0.1039, -0.0775] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 128 | small-to-big | 0.1188 | +0.0000 | [-0.0012, +0.0000] | 99.00% | no | 0.9898 |
| pooled | hybrid | nomic | production | 256 | fixed-64 | 0.1504 | -0.0334 | [-0.0452, -0.0218] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 256 | fixed-128 | 0.1703 | -0.0135 | [-0.0247, -0.0026] | 98.33% | yes | 0.0010 |
| pooled | hybrid | nomic | production | 256 | fixed-256 | 0.1568 | -0.0270 | [-0.0418, -0.0125] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 256 | section-aware | 0.0942 | -0.0896 | [-0.1046, -0.0746] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 256 | small-to-big | 0.1838 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 0.9990 |
| pooled | hybrid | nomic | production | 512 | fixed-64 | 0.2060 | -0.0481 | [-0.0629, -0.0345] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 512 | fixed-128 | 0.2442 | -0.0099 | [-0.0219, +0.0000] | 95.00% | no | 0.0452 |
| pooled | hybrid | nomic | production | 512 | fixed-256 | 0.2359 | -0.0181 | [-0.0300, -0.0071] | 95.00% | yes | 0.0006 |
| pooled | hybrid | nomic | production | 512 | fixed-512 | 0.2054 | -0.0487 | [-0.0662, -0.0320] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 512 | section-aware | 0.2416 | -0.0124 | [-0.0274, +0.0000] | 98.33% | no | 0.0227 |
| pooled | hybrid | nomic | production | 512 | small-to-big | 0.2540 | +0.0000 | [-0.0059, +0.0000] | 99.00% | no | 0.9315 |
| pooled | hybrid | nomic | production | 1024 | fixed-64 | 0.2060 | -0.1438 | [-0.1567, -0.1333] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 1024 | fixed-128 | 0.3183 | -0.0315 | [-0.0432, -0.0224] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 1024 | fixed-256 | 0.3171 | -0.0327 | [-0.0445, -0.0231] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 1024 | fixed-512 | 0.3040 | -0.0458 | [-0.0590, -0.0352] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 1024 | section-aware | 0.3498 | +0.0000 | [-0.0076, +0.0000] | 95.00% | no | 0.7571 |
| pooled | hybrid | nomic | production | 1024 | small-to-big | 0.3457 | -0.0041 | [-0.0158, +0.0000] | 95.00% | no | 0.2429 |
| pooled | hybrid | nomic | production | 1024 | fixed-1024 | 0.2465 | -0.1033 | [-0.1185, -0.0902] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 2048 | fixed-64 | 0.2060 | -0.2198 | [-0.2361, -0.2055] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 2048 | fixed-128 | 0.3183 | -0.1075 | [-0.1220, -0.0945] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 2048 | fixed-256 | 0.3993 | -0.0265 | [-0.0402, -0.0146] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 2048 | fixed-512 | 0.3845 | -0.0412 | [-0.0566, -0.0280] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 2048 | section-aware | 0.4218 | -0.0040 | [-0.0162, +0.0000] | 98.33% | no | 0.2229 |
| pooled | hybrid | nomic | production | 2048 | small-to-big | 0.4258 | +0.0000 | [-0.0090, +0.0000] | 99.00% | no | 0.7771 |
| pooled | hybrid | nomic | production | 2048 | fixed-1024 | 0.3432 | -0.0826 | [-0.1003, -0.0665] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 4096 | fixed-64 | 0.2060 | -0.2511 | [-0.2667, -0.2365] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 4096 | fixed-128 | 0.3183 | -0.1387 | [-0.1551, -0.1243] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 4096 | fixed-256 | 0.3993 | -0.0578 | [-0.0699, -0.0465] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 4096 | fixed-512 | 0.4571 | +0.0000 | [-0.0034, +0.0000] | 95.00% | no | 0.9182 |
| pooled | hybrid | nomic | production | 4096 | section-aware | 0.4458 | -0.0112 | [-0.0247, +0.0000] | 98.33% | no | 0.0144 |
| pooled | hybrid | nomic | production | 4096 | small-to-big | 0.4485 | -0.0085 | [-0.0231, +0.0000] | 99.00% | no | 0.0674 |
| pooled | hybrid | nomic | production | 4096 | fixed-1024 | 0.4260 | -0.0311 | [-0.0433, -0.0196] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | fixed-64 | 0.2060 | -0.2837 | [-0.2983, -0.2693] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | fixed-128 | 0.3183 | -0.1714 | [-0.1890, -0.1541] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | fixed-256 | 0.3993 | -0.0904 | [-0.1048, -0.0764] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | fixed-512 | 0.4571 | -0.0327 | [-0.0436, -0.0214] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | section-aware | 0.4458 | -0.0439 | [-0.0603, -0.0273] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | small-to-big | 0.4485 | -0.0412 | [-0.0592, -0.0235] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | production | 8192 | fixed-1024 | 0.4897 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 1.0000 |
| pooled | hybrid | nomic | fair | 128 | fixed-64 | 0.1009 | -0.0179 | [-0.0291, -0.0074] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 128 | fixed-128 | 0.1097 | -0.0092 | [-0.0180, -0.0003] | 97.50% | yes | 0.0102 |
| pooled | hybrid | nomic | fair | 128 | section-aware | 0.0284 | -0.0904 | [-0.1039, -0.0775] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 128 | small-to-big | 0.1188 | +0.0000 | [-0.0014, +0.0000] | 99.17% | no | 0.9898 |
| pooled | hybrid | nomic | fair | 256 | fixed-64 | 0.1504 | -0.0334 | [-0.0452, -0.0218] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 256 | fixed-128 | 0.1703 | -0.0135 | [-0.0247, -0.0026] | 98.33% | yes | 0.0010 |
| pooled | hybrid | nomic | fair | 256 | fixed-256 | 0.1568 | -0.0270 | [-0.0418, -0.0125] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 256 | section-aware | 0.0942 | -0.0896 | [-0.1046, -0.0746] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 256 | small-to-big | 0.1838 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9990 |
| pooled | hybrid | nomic | fair | 512 | fixed-64 | 0.2060 | -0.0481 | [-0.0629, -0.0345] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 512 | fixed-128 | 0.2442 | -0.0099 | [-0.0219, +0.0000] | 95.00% | no | 0.0452 |
| pooled | hybrid | nomic | fair | 512 | fixed-256 | 0.2359 | -0.0181 | [-0.0300, -0.0071] | 95.00% | yes | 0.0006 |
| pooled | hybrid | nomic | fair | 512 | fixed-512 | 0.2054 | -0.0487 | [-0.0662, -0.0320] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 512 | section-aware | 0.2416 | -0.0124 | [-0.0279, +0.0000] | 98.75% | no | 0.0227 |
| pooled | hybrid | nomic | fair | 512 | small-to-big | 0.2540 | +0.0000 | [-0.0063, +0.0000] | 99.17% | no | 0.9315 |
| pooled | hybrid | nomic | fair | 1024 | fixed-64 | 0.2715 | -0.0789 | [-0.0912, -0.0688] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 1024 | fixed-128 | 0.3185 | -0.0320 | [-0.0437, -0.0227] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 1024 | fixed-256 | 0.3171 | -0.0333 | [-0.0451, -0.0235] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 1024 | fixed-512 | 0.3040 | -0.0465 | [-0.0595, -0.0356] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 1024 | section-aware | 0.3504 | +0.0000 | [-0.0070, +0.0000] | 95.00% | no | 0.7831 |
| pooled | hybrid | nomic | fair | 1024 | small-to-big | 0.3458 | -0.0047 | [-0.0164, +0.0000] | 95.00% | no | 0.2169 |
| pooled | hybrid | nomic | fair | 1024 | fixed-1024 | 0.2465 | -0.1039 | [-0.1190, -0.0906] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 2048 | fixed-64 | 0.3347 | -0.0939 | [-0.1094, -0.0822] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 2048 | fixed-128 | 0.3856 | -0.0431 | [-0.0580, -0.0319] | 99.17% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 2048 | fixed-256 | 0.3995 | -0.0291 | [-0.0432, -0.0183] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 2048 | fixed-512 | 0.3845 | -0.0441 | [-0.0599, -0.0318] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 2048 | section-aware | 0.4276 | -0.0010 | [-0.0140, +0.0000] | 98.75% | no | 0.4216 |
| pooled | hybrid | nomic | fair | 2048 | small-to-big | 0.4286 | +0.0000 | [-0.0123, +0.0000] | 99.17% | no | 0.5784 |
| pooled | hybrid | nomic | fair | 2048 | fixed-1024 | 0.3432 | -0.0854 | [-0.1039, -0.0708] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 4096 | fixed-64 | 0.3976 | -0.1006 | [-0.1140, -0.0877] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 4096 | fixed-128 | 0.4472 | -0.0510 | [-0.0649, -0.0381] | 99.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 4096 | fixed-256 | 0.4686 | -0.0296 | [-0.0417, -0.0181] | 98.33% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 4096 | fixed-512 | 0.4587 | -0.0395 | [-0.0523, -0.0274] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 4096 | section-aware | 0.4982 | +0.0000 | [-0.0055, +0.0000] | 98.75% | no | 0.9008 |
| pooled | hybrid | nomic | fair | 4096 | small-to-big | 0.4922 | -0.0060 | [-0.0183, +0.0000] | 99.17% | no | 0.0992 |
| pooled | hybrid | nomic | fair | 4096 | fixed-1024 | 0.4260 | -0.0722 | [-0.0878, -0.0576] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 8192 | fixed-64 | 0.4529 | -0.1002 | [-0.1119, -0.0898] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 8192 | fixed-128 | 0.5062 | -0.0468 | [-0.0600, -0.0348] | 98.75% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 8192 | fixed-256 | 0.5224 | -0.0306 | [-0.0413, -0.0212] | 97.50% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 8192 | fixed-512 | 0.5145 | -0.0385 | [-0.0501, -0.0285] | 95.00% | yes | 0.0000 |
| pooled | hybrid | nomic | fair | 8192 | section-aware | 0.5530 | +0.0000 | [-0.0081, +0.0000] | 98.75% | no | 0.7491 |
| pooled | hybrid | nomic | fair | 8192 | small-to-big | 0.5501 | -0.0029 | [-0.0143, +0.0000] | 99.17% | no | 0.2509 |
| pooled | hybrid | nomic | fair | 8192 | fixed-1024 | 0.4969 | -0.0561 | [-0.0690, -0.0446] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 128 | fixed-64 | 0.1081 | -0.0101 | [-0.0180, -0.0022] | 95.00% | yes | 0.0067 |
| pooled | vector | bge-small | production | 128 | fixed-128 | 0.1182 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9932 |
| pooled | vector | bge-small | production | 128 | section-aware | 0.0292 | -0.0890 | [-0.1028, -0.0755] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | production | 128 | small-to-big | 0.0999 | -0.0183 | [-0.0311, -0.0064] | 99.17% | yes | 0.0001 |
| pooled | vector | bge-small | production | 256 | fixed-64 | 0.1536 | -0.0243 | [-0.0350, -0.0140] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | production | 256 | fixed-128 | 0.1779 | +0.0000 | [-0.0061, +0.0000] | 98.33% | no | 0.8886 |
| pooled | vector | bge-small | production | 256 | fixed-256 | 0.1630 | -0.0149 | [-0.0250, -0.0054] | 95.00% | yes | 0.0014 |
| pooled | vector | bge-small | production | 256 | section-aware | 0.0915 | -0.0864 | [-0.1016, -0.0722] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 256 | small-to-big | 0.1718 | -0.0061 | [-0.0192, +0.0000] | 99.00% | no | 0.1100 |
| pooled | vector | bge-small | production | 512 | fixed-64 | 0.2049 | -0.0351 | [-0.0502, -0.0236] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 512 | fixed-128 | 0.2342 | -0.0058 | [-0.0199, +0.0000] | 98.33% | no | 0.1176 |
| pooled | vector | bge-small | production | 512 | fixed-256 | 0.2251 | -0.0148 | [-0.0292, -0.0037] | 97.50% | yes | 0.0013 |
| pooled | vector | bge-small | production | 512 | fixed-512 | 0.2078 | -0.0322 | [-0.0497, -0.0182] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | production | 512 | section-aware | 0.2353 | -0.0047 | [-0.0187, +0.0000] | 97.50% | no | 0.1901 |
| pooled | vector | bge-small | production | 512 | small-to-big | 0.2400 | +0.0000 | [-0.0119, +0.0000] | 99.00% | no | 0.6910 |
| pooled | vector | bge-small | production | 1024 | fixed-64 | 0.2049 | -0.1273 | [-0.1390, -0.1160] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 1024 | fixed-128 | 0.2951 | -0.0371 | [-0.0483, -0.0262] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 1024 | fixed-256 | 0.3006 | -0.0316 | [-0.0434, -0.0200] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 1024 | fixed-512 | 0.2786 | -0.0535 | [-0.0664, -0.0411] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 1024 | section-aware | 0.3174 | -0.0148 | [-0.0263, -0.0034] | 95.00% | yes | 0.0050 |
| pooled | vector | bge-small | production | 1024 | small-to-big | 0.3322 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9950 |
| pooled | vector | bge-small | production | 1024 | fixed-1024 | 0.2431 | -0.0891 | [-0.1034, -0.0752] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 2048 | fixed-64 | 0.2049 | -0.1845 | [-0.2005, -0.1694] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | production | 2048 | fixed-128 | 0.2951 | -0.0943 | [-0.1093, -0.0797] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | production | 2048 | fixed-256 | 0.3631 | -0.0264 | [-0.0406, -0.0125] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 2048 | fixed-512 | 0.3496 | -0.0398 | [-0.0541, -0.0256] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | production | 2048 | section-aware | 0.3788 | -0.0107 | [-0.0228, +0.0000] | 97.50% | no | 0.0241 |
| pooled | vector | bge-small | production | 2048 | small-to-big | 0.3894 | +0.0000 | [-0.0032, +0.0000] | 99.00% | no | 0.9759 |
| pooled | vector | bge-small | production | 2048 | fixed-1024 | 0.3071 | -0.0823 | [-0.0989, -0.0665] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | production | 4096 | fixed-64 | 0.2049 | -0.1990 | [-0.2146, -0.1851] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | production | 4096 | fixed-128 | 0.2951 | -0.1088 | [-0.1241, -0.0949] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | production | 4096 | fixed-256 | 0.3631 | -0.0408 | [-0.0553, -0.0288] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | production | 4096 | fixed-512 | 0.3976 | -0.0063 | [-0.0200, +0.0000] | 97.50% | no | 0.1518 |
| pooled | vector | bge-small | production | 4096 | section-aware | 0.3915 | -0.0124 | [-0.0255, -0.0009] | 98.33% | yes | 0.0047 |
| pooled | vector | bge-small | production | 4096 | small-to-big | 0.4039 | +0.0000 | [-0.0092, +0.0000] | 99.00% | no | 0.8435 |
| pooled | vector | bge-small | production | 4096 | fixed-1024 | 0.3626 | -0.0413 | [-0.0562, -0.0291] | 97.50% | yes | 0.0000 |
| pooled | vector | bge-small | production | 8192 | fixed-64 | 0.2049 | -0.1990 | [-0.2141, -0.1866] | 97.50% | yes | 0.0000 |
| pooled | vector | bge-small | production | 8192 | fixed-128 | 0.2951 | -0.1088 | [-0.1241, -0.0962] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | production | 8192 | fixed-256 | 0.3631 | -0.0408 | [-0.0547, -0.0302] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | production | 8192 | fixed-512 | 0.3976 | -0.0063 | [-0.0200, +0.0000] | 97.50% | no | 0.0882 |
| pooled | vector | bge-small | production | 8192 | section-aware | 0.3915 | -0.0124 | [-0.0263, -0.0015] | 98.75% | yes | 0.0021 |
| pooled | vector | bge-small | production | 8192 | small-to-big | 0.4039 | +0.0000 | [-0.0126, +0.0000] | 99.00% | no | 0.7238 |
| pooled | vector | bge-small | production | 8192 | fixed-1024 | 0.3987 | -0.0052 | [-0.0187, +0.0000] | 95.00% | no | 0.1859 |
| pooled | vector | bge-small | fair | 128 | fixed-64 | 0.1081 | -0.0101 | [-0.0180, -0.0022] | 95.00% | yes | 0.0067 |
| pooled | vector | bge-small | fair | 128 | fixed-128 | 0.1182 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9932 |
| pooled | vector | bge-small | fair | 128 | section-aware | 0.0292 | -0.0890 | [-0.1028, -0.0755] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 128 | small-to-big | 0.0999 | -0.0183 | [-0.0311, -0.0064] | 99.17% | yes | 0.0001 |
| pooled | vector | bge-small | fair | 256 | fixed-64 | 0.1536 | -0.0243 | [-0.0350, -0.0140] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 256 | fixed-128 | 0.1779 | +0.0000 | [-0.0061, +0.0000] | 98.33% | no | 0.8886 |
| pooled | vector | bge-small | fair | 256 | fixed-256 | 0.1630 | -0.0149 | [-0.0250, -0.0054] | 95.00% | yes | 0.0014 |
| pooled | vector | bge-small | fair | 256 | section-aware | 0.0915 | -0.0864 | [-0.1016, -0.0722] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 256 | small-to-big | 0.1718 | -0.0061 | [-0.0192, +0.0000] | 99.00% | no | 0.1100 |
| pooled | vector | bge-small | fair | 512 | fixed-64 | 0.2050 | -0.0350 | [-0.0501, -0.0236] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 512 | fixed-128 | 0.2344 | -0.0057 | [-0.0199, +0.0000] | 98.33% | no | 0.1194 |
| pooled | vector | bge-small | fair | 512 | fixed-256 | 0.2251 | -0.0149 | [-0.0293, -0.0040] | 97.50% | yes | 0.0013 |
| pooled | vector | bge-small | fair | 512 | fixed-512 | 0.2078 | -0.0323 | [-0.0499, -0.0183] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 512 | section-aware | 0.2356 | -0.0045 | [-0.0194, +0.0000] | 98.75% | no | 0.1996 |
| pooled | vector | bge-small | fair | 512 | small-to-big | 0.2401 | +0.0000 | [-0.0121, +0.0000] | 99.00% | no | 0.6797 |
| pooled | vector | bge-small | fair | 1024 | fixed-64 | 0.2573 | -0.0756 | [-0.0865, -0.0648] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 1024 | fixed-128 | 0.2958 | -0.0372 | [-0.0485, -0.0263] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 1024 | fixed-256 | 0.3006 | -0.0324 | [-0.0443, -0.0208] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 1024 | fixed-512 | 0.2786 | -0.0543 | [-0.0672, -0.0420] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 1024 | section-aware | 0.3199 | -0.0131 | [-0.0246, -0.0015] | 95.00% | yes | 0.0131 |
| pooled | vector | bge-small | fair | 1024 | small-to-big | 0.3330 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9869 |
| pooled | vector | bge-small | fair | 1024 | fixed-1024 | 0.2431 | -0.0899 | [-0.1042, -0.0759] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 2048 | fixed-64 | 0.3100 | -0.0860 | [-0.1003, -0.0730] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 2048 | fixed-128 | 0.3524 | -0.0435 | [-0.0583, -0.0303] | 99.17% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 2048 | fixed-256 | 0.3643 | -0.0317 | [-0.0459, -0.0186] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 2048 | fixed-512 | 0.3496 | -0.0464 | [-0.0611, -0.0328] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 2048 | section-aware | 0.3898 | -0.0061 | [-0.0199, +0.0000] | 98.75% | no | 0.1375 |
| pooled | vector | bge-small | fair | 2048 | small-to-big | 0.3960 | +0.0000 | [-0.0082, +0.0000] | 99.00% | no | 0.8625 |
| pooled | vector | bge-small | fair | 2048 | fixed-1024 | 0.3071 | -0.0889 | [-0.1055, -0.0737] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 4096 | fixed-64 | 0.3595 | -0.0874 | [-0.1024, -0.0763] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 4096 | fixed-128 | 0.4066 | -0.0403 | [-0.0551, -0.0293] | 99.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 4096 | fixed-256 | 0.4155 | -0.0313 | [-0.0465, -0.0209] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 4096 | fixed-512 | 0.3988 | -0.0481 | [-0.0622, -0.0377] | 97.50% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 4096 | section-aware | 0.4461 | -0.0007 | [-0.0145, +0.0000] | 98.75% | no | 0.4442 |
| pooled | vector | bge-small | fair | 4096 | small-to-big | 0.4468 | +0.0000 | [-0.0129, +0.0000] | 99.00% | no | 0.5558 |
| pooled | vector | bge-small | fair | 4096 | fixed-1024 | 0.3626 | -0.0842 | [-0.1003, -0.0721] | 97.50% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 8192 | fixed-64 | 0.4078 | -0.0871 | [-0.1001, -0.0755] | 97.50% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 8192 | fixed-128 | 0.4514 | -0.0434 | [-0.0559, -0.0320] | 98.75% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 8192 | fixed-256 | 0.4611 | -0.0337 | [-0.0463, -0.0227] | 98.33% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 8192 | fixed-512 | 0.4425 | -0.0523 | [-0.0639, -0.0418] | 95.00% | yes | 0.0000 |
| pooled | vector | bge-small | fair | 8192 | section-aware | 0.4896 | -0.0053 | [-0.0183, +0.0000] | 98.75% | no | 0.1535 |
| pooled | vector | bge-small | fair | 8192 | small-to-big | 0.4948 | +0.0000 | [-0.0079, +0.0000] | 99.00% | no | 0.8465 |
| pooled | vector | bge-small | fair | 8192 | fixed-1024 | 0.4008 | -0.0940 | [-0.1077, -0.0816] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 128 | fixed-64 | 0.1234 | -0.0279 | [-0.0402, -0.0162] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | production | 128 | fixed-128 | 0.1377 | -0.0137 | [-0.0247, -0.0029] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | production | 128 | section-aware | 0.0323 | -0.1190 | [-0.1345, -0.1048] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | production | 128 | small-to-big | 0.1513 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| pooled | vector | nomic | production | 256 | fixed-64 | 0.1716 | -0.0429 | [-0.0551, -0.0309] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 256 | fixed-128 | 0.1983 | -0.0161 | [-0.0267, -0.0057] | 97.50% | yes | 0.0001 |
| pooled | vector | nomic | production | 256 | fixed-256 | 0.1859 | -0.0286 | [-0.0435, -0.0142] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 256 | section-aware | 0.1012 | -0.1133 | [-0.1294, -0.0974] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 256 | small-to-big | 0.2145 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9999 |
| pooled | vector | nomic | production | 512 | fixed-64 | 0.2234 | -0.0584 | [-0.0734, -0.0443] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | production | 512 | fixed-128 | 0.2602 | -0.0216 | [-0.0330, -0.0109] | 95.00% | yes | 0.0001 |
| pooled | vector | nomic | production | 512 | fixed-256 | 0.2559 | -0.0259 | [-0.0420, -0.0108] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | production | 512 | fixed-512 | 0.2175 | -0.0643 | [-0.0820, -0.0473] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | production | 512 | section-aware | 0.2721 | -0.0097 | [-0.0222, +0.0000] | 95.00% | no | 0.0625 |
| pooled | vector | nomic | production | 512 | small-to-big | 0.2818 | +0.0000 | [-0.0063, +0.0000] | 99.17% | no | 0.9374 |
| pooled | vector | nomic | production | 1024 | fixed-64 | 0.2234 | -0.1411 | [-0.1535, -0.1299] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 1024 | fixed-128 | 0.3214 | -0.0431 | [-0.0542, -0.0331] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 1024 | fixed-256 | 0.3232 | -0.0414 | [-0.0532, -0.0305] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 1024 | fixed-512 | 0.3031 | -0.0614 | [-0.0752, -0.0489] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 1024 | section-aware | 0.3560 | -0.0086 | [-0.0199, +0.0000] | 95.00% | no | 0.0657 |
| pooled | vector | nomic | production | 1024 | small-to-big | 0.3646 | +0.0000 | [-0.0027, +0.0000] | 95.00% | no | 0.9343 |
| pooled | vector | nomic | production | 1024 | fixed-1024 | 0.2406 | -0.1240 | [-0.1395, -0.1092] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 2048 | fixed-64 | 0.2234 | -0.2002 | [-0.2159, -0.1852] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | production | 2048 | fixed-128 | 0.3214 | -0.1022 | [-0.1167, -0.0886] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 2048 | fixed-256 | 0.3830 | -0.0406 | [-0.0540, -0.0279] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | production | 2048 | fixed-512 | 0.3620 | -0.0616 | [-0.0773, -0.0469] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | production | 2048 | section-aware | 0.4123 | -0.0113 | [-0.0226, -0.0000] | 97.50% | yes | 0.0124 |
| pooled | vector | nomic | production | 2048 | small-to-big | 0.4236 | +0.0000 | [-0.0018, +0.0000] | 99.17% | no | 0.9876 |
| pooled | vector | nomic | production | 2048 | fixed-1024 | 0.3230 | -0.1006 | [-0.1177, -0.0840] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | production | 4096 | fixed-64 | 0.2234 | -0.2189 | [-0.2335, -0.2048] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | production | 4096 | fixed-128 | 0.3214 | -0.1209 | [-0.1347, -0.1070] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | production | 4096 | fixed-256 | 0.3830 | -0.0593 | [-0.0713, -0.0476] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | production | 4096 | fixed-512 | 0.4174 | -0.0250 | [-0.0386, -0.0117] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | production | 4096 | section-aware | 0.4233 | -0.0191 | [-0.0306, -0.0070] | 98.75% | yes | 0.0001 |
| pooled | vector | nomic | production | 4096 | small-to-big | 0.4423 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9999 |
| pooled | vector | nomic | production | 4096 | fixed-1024 | 0.3884 | -0.0539 | [-0.0694, -0.0386] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | production | 8192 | fixed-64 | 0.2234 | -0.2189 | [-0.2317, -0.2066] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 8192 | fixed-128 | 0.3214 | -0.1209 | [-0.1343, -0.1078] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | production | 8192 | fixed-256 | 0.3830 | -0.0593 | [-0.0698, -0.0490] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 8192 | fixed-512 | 0.4174 | -0.0250 | [-0.0369, -0.0132] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | production | 8192 | section-aware | 0.4233 | -0.0191 | [-0.0302, -0.0078] | 98.33% | yes | 0.0001 |
| pooled | vector | nomic | production | 8192 | small-to-big | 0.4423 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9979 |
| pooled | vector | nomic | production | 8192 | fixed-1024 | 0.4241 | -0.0182 | [-0.0312, -0.0054] | 95.00% | yes | 0.0020 |
| pooled | vector | nomic | fair | 128 | fixed-64 | 0.1234 | -0.0279 | [-0.0402, -0.0162] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | fair | 128 | fixed-128 | 0.1377 | -0.0137 | [-0.0247, -0.0029] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | fair | 128 | section-aware | 0.0323 | -0.1190 | [-0.1345, -0.1048] | 99.17% | yes | 0.0000 |
| pooled | vector | nomic | fair | 128 | small-to-big | 0.1513 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| pooled | vector | nomic | fair | 256 | fixed-64 | 0.1716 | -0.0429 | [-0.0551, -0.0309] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 256 | fixed-128 | 0.1983 | -0.0161 | [-0.0267, -0.0057] | 97.50% | yes | 0.0001 |
| pooled | vector | nomic | fair | 256 | fixed-256 | 0.1859 | -0.0286 | [-0.0435, -0.0142] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 256 | section-aware | 0.1012 | -0.1133 | [-0.1294, -0.0974] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 256 | small-to-big | 0.2145 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9999 |
| pooled | vector | nomic | fair | 512 | fixed-64 | 0.2234 | -0.0584 | [-0.0734, -0.0443] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | fair | 512 | fixed-128 | 0.2602 | -0.0216 | [-0.0330, -0.0109] | 95.00% | yes | 0.0001 |
| pooled | vector | nomic | fair | 512 | fixed-256 | 0.2559 | -0.0259 | [-0.0420, -0.0108] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | fair | 512 | fixed-512 | 0.2175 | -0.0643 | [-0.0820, -0.0473] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | fair | 512 | section-aware | 0.2721 | -0.0097 | [-0.0259, +0.0000] | 98.75% | no | 0.0625 |
| pooled | vector | nomic | fair | 512 | small-to-big | 0.2818 | +0.0000 | [-0.0063, +0.0000] | 99.17% | no | 0.9374 |
| pooled | vector | nomic | fair | 1024 | fixed-64 | 0.2785 | -0.0861 | [-0.0979, -0.0749] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 1024 | fixed-128 | 0.3214 | -0.0432 | [-0.0542, -0.0331] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 1024 | fixed-256 | 0.3232 | -0.0414 | [-0.0532, -0.0306] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 1024 | fixed-512 | 0.3031 | -0.0614 | [-0.0752, -0.0490] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 1024 | section-aware | 0.3563 | -0.0083 | [-0.0195, +0.0000] | 95.00% | no | 0.0718 |
| pooled | vector | nomic | fair | 1024 | small-to-big | 0.3646 | +0.0000 | [-0.0030, +0.0000] | 95.00% | no | 0.9282 |
| pooled | vector | nomic | fair | 1024 | fixed-1024 | 0.2406 | -0.1240 | [-0.1395, -0.1093] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 2048 | fixed-64 | 0.3354 | -0.0896 | [-0.1035, -0.0775] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | fair | 2048 | fixed-128 | 0.3843 | -0.0407 | [-0.0543, -0.0292] | 99.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 2048 | fixed-256 | 0.3831 | -0.0420 | [-0.0558, -0.0307] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | fair | 2048 | fixed-512 | 0.3620 | -0.0631 | [-0.0789, -0.0500] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | fair | 2048 | section-aware | 0.4217 | -0.0034 | [-0.0161, +0.0000] | 98.75% | no | 0.2569 |
| pooled | vector | nomic | fair | 2048 | small-to-big | 0.4251 | +0.0000 | [-0.0100, +0.0000] | 99.17% | no | 0.7431 |
| pooled | vector | nomic | fair | 2048 | fixed-1024 | 0.3230 | -0.1020 | [-0.1195, -0.0871] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | fair | 4096 | fixed-64 | 0.3867 | -0.0866 | [-0.0991, -0.0754] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | fair | 4096 | fixed-128 | 0.4325 | -0.0408 | [-0.0535, -0.0294] | 98.75% | yes | 0.0000 |
| pooled | vector | nomic | fair | 4096 | fixed-256 | 0.4389 | -0.0344 | [-0.0462, -0.0247] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | fair | 4096 | fixed-512 | 0.4194 | -0.0540 | [-0.0676, -0.0423] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | fair | 4096 | section-aware | 0.4701 | -0.0032 | [-0.0150, +0.0000] | 98.75% | no | 0.2504 |
| pooled | vector | nomic | fair | 4096 | small-to-big | 0.4733 | +0.0000 | [-0.0090, +0.0000] | 99.17% | no | 0.7496 |
| pooled | vector | nomic | fair | 4096 | fixed-1024 | 0.3888 | -0.0846 | [-0.1005, -0.0705] | 97.50% | yes | 0.0000 |
| pooled | vector | nomic | fair | 8192 | fixed-64 | 0.4353 | -0.0822 | [-0.0929, -0.0720] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 8192 | fixed-128 | 0.4816 | -0.0359 | [-0.0478, -0.0242] | 98.33% | yes | 0.0000 |
| pooled | vector | nomic | fair | 8192 | fixed-256 | 0.4783 | -0.0392 | [-0.0496, -0.0294] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 8192 | fixed-512 | 0.4632 | -0.0543 | [-0.0661, -0.0432] | 95.00% | yes | 0.0000 |
| pooled | vector | nomic | fair | 8192 | section-aware | 0.5106 | -0.0069 | [-0.0192, +0.0000] | 98.75% | no | 0.0805 |
| pooled | vector | nomic | fair | 8192 | small-to-big | 0.5175 | +0.0000 | [-0.0059, +0.0000] | 99.17% | no | 0.9195 |
| pooled | vector | nomic | fair | 8192 | fixed-1024 | 0.4351 | -0.0824 | [-0.0959, -0.0697] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 128 | fixed-64 | 0.2753 | -0.0584 | [-0.0895, -0.0260] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 128 | fixed-128 | 0.2954 | -0.0383 | [-0.0609, -0.0154] | 95.00% | yes | 0.0006 |
| nq | hybrid-rerank | bge-small | production | 128 | section-aware | 0.0560 | -0.2777 | [-0.3135, -0.2426] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 128 | small-to-big | 0.3337 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9994 |
| nq | hybrid-rerank | bge-small | production | 256 | fixed-64 | 0.3707 | -0.1299 | [-0.1610, -0.0988] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 256 | fixed-128 | 0.4323 | -0.0682 | [-0.1006, -0.0365] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 256 | fixed-256 | 0.4247 | -0.0759 | [-0.1145, -0.0380] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 256 | section-aware | 0.2460 | -0.2546 | [-0.2937, -0.2146] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 256 | small-to-big | 0.5006 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | bge-small | production | 512 | fixed-64 | 0.4697 | -0.1913 | [-0.2305, -0.1601] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 512 | fixed-128 | 0.5672 | -0.0938 | [-0.1346, -0.0620] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 512 | fixed-256 | 0.5946 | -0.0663 | [-0.1070, -0.0357] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 512 | fixed-512 | 0.6077 | -0.0533 | [-0.0917, -0.0245] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 512 | section-aware | 0.6610 | +0.0000 | [-0.0304, +0.0000] | 98.33% | no | 0.5993 |
| nq | hybrid-rerank | bge-small | production | 512 | small-to-big | 0.6574 | -0.0036 | [-0.0381, +0.0000] | 98.33% | no | 0.4007 |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.4697 | -0.3510 | [-0.3764, -0.3251] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.6861 | -0.1346 | [-0.1588, -0.1103] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.7347 | -0.0860 | [-0.1103, -0.0612] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.7674 | -0.0533 | [-0.0770, -0.0296] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.8207 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9929 |
| nq | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.7924 | -0.0282 | [-0.0501, -0.0060] | 95.00% | yes | 0.0071 |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.7396 | -0.0811 | [-0.1095, -0.0535] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 2048 | fixed-64 | 0.4697 | -0.4382 | [-0.4669, -0.4086] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 2048 | fixed-128 | 0.6861 | -0.2218 | [-0.2497, -0.1936] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 2048 | fixed-256 | 0.8465 | -0.0614 | [-0.0847, -0.0387] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 2048 | fixed-512 | 0.8642 | -0.0437 | [-0.0672, -0.0209] | 97.50% | yes | 0.0001 |
| nq | hybrid-rerank | bge-small | production | 2048 | section-aware | 0.9079 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9988 |
| nq | hybrid-rerank | bge-small | production | 2048 | small-to-big | 0.8811 | -0.0269 | [-0.0485, -0.0058] | 98.75% | yes | 0.0011 |
| nq | hybrid-rerank | bge-small | production | 2048 | fixed-1024 | 0.8547 | -0.0532 | [-0.0817, -0.0257] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-64 | 0.4697 | -0.4592 | [-0.4879, -0.4374] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-128 | 0.6861 | -0.2428 | [-0.2723, -0.2214] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-256 | 0.8465 | -0.0824 | [-0.1067, -0.0671] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-512 | 0.9284 | -0.0005 | [-0.0171, +0.0000] | 95.00% | no | 0.3840 |
| nq | hybrid-rerank | bge-small | production | 4096 | section-aware | 0.9289 | +0.0000 | [-0.0213, +0.0000] | 98.33% | no | 0.4549 |
| nq | hybrid-rerank | bge-small | production | 4096 | small-to-big | 0.9069 | -0.0220 | [-0.0476, -0.0070] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 4096 | fixed-1024 | 0.9243 | -0.0046 | [-0.0264, +0.0000] | 97.50% | no | 0.1611 |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-64 | 0.4697 | -0.4951 | [-0.5180, -0.4723] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-128 | 0.6861 | -0.2787 | [-0.3051, -0.2529] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-256 | 0.8465 | -0.1183 | [-0.1385, -0.0989] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-512 | 0.9284 | -0.0364 | [-0.0535, -0.0197] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | section-aware | 0.9289 | -0.0359 | [-0.0577, -0.0150] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | small-to-big | 0.9069 | -0.0579 | [-0.0834, -0.0333] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | production | 8192 | fixed-1024 | 0.9648 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| nq | hybrid-rerank | bge-small | fair | 128 | fixed-64 | 0.2753 | -0.0584 | [-0.0895, -0.0260] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 128 | fixed-128 | 0.2954 | -0.0383 | [-0.0609, -0.0154] | 95.00% | yes | 0.0006 |
| nq | hybrid-rerank | bge-small | fair | 128 | section-aware | 0.0560 | -0.2777 | [-0.3135, -0.2426] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 128 | small-to-big | 0.3337 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9994 |
| nq | hybrid-rerank | bge-small | fair | 256 | fixed-64 | 0.3707 | -0.1299 | [-0.1610, -0.0988] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 256 | fixed-128 | 0.4323 | -0.0682 | [-0.1006, -0.0365] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 256 | fixed-256 | 0.4247 | -0.0759 | [-0.1145, -0.0380] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 256 | section-aware | 0.2460 | -0.2546 | [-0.2937, -0.2146] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 256 | small-to-big | 0.5006 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | bge-small | fair | 512 | fixed-64 | 0.4697 | -0.1913 | [-0.2305, -0.1601] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 512 | fixed-128 | 0.5672 | -0.0938 | [-0.1346, -0.0620] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 512 | fixed-256 | 0.5946 | -0.0663 | [-0.1070, -0.0357] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 512 | fixed-512 | 0.6077 | -0.0533 | [-0.0917, -0.0245] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 512 | section-aware | 0.6610 | +0.0000 | [-0.0316, +0.0000] | 98.75% | no | 0.5993 |
| nq | hybrid-rerank | bge-small | fair | 512 | small-to-big | 0.6574 | -0.0036 | [-0.0381, +0.0000] | 98.33% | no | 0.4007 |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.5691 | -0.2516 | [-0.2773, -0.2263] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.6861 | -0.1346 | [-0.1588, -0.1103] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.7347 | -0.0860 | [-0.1103, -0.0612] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.7674 | -0.0533 | [-0.0770, -0.0296] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.8207 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9929 |
| nq | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.7924 | -0.0282 | [-0.0501, -0.0060] | 95.00% | yes | 0.0071 |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.7396 | -0.0811 | [-0.1095, -0.0535] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 2048 | fixed-64 | 0.6427 | -0.2672 | [-0.2949, -0.2391] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 2048 | fixed-128 | 0.7825 | -0.1275 | [-0.1538, -0.1020] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 2048 | fixed-256 | 0.8465 | -0.0634 | [-0.0867, -0.0407] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 2048 | fixed-512 | 0.8642 | -0.0457 | [-0.0703, -0.0215] | 98.33% | yes | 0.0001 |
| nq | hybrid-rerank | bge-small | fair | 2048 | section-aware | 0.9099 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9993 |
| nq | hybrid-rerank | bge-small | fair | 2048 | small-to-big | 0.8814 | -0.0286 | [-0.0502, -0.0075] | 98.75% | yes | 0.0006 |
| nq | hybrid-rerank | bge-small | fair | 2048 | fixed-1024 | 0.8547 | -0.0552 | [-0.0833, -0.0282] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 4096 | fixed-64 | 0.7356 | -0.2143 | [-0.2366, -0.1921] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 4096 | fixed-128 | 0.8361 | -0.1138 | [-0.1342, -0.0936] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 4096 | fixed-256 | 0.9135 | -0.0365 | [-0.0534, -0.0197] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 4096 | fixed-512 | 0.9284 | -0.0215 | [-0.0389, -0.0045] | 97.50% | yes | 0.0019 |
| nq | hybrid-rerank | bge-small | fair | 4096 | section-aware | 0.9499 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9965 |
| nq | hybrid-rerank | bge-small | fair | 4096 | small-to-big | 0.9260 | -0.0240 | [-0.0405, -0.0071] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 4096 | fixed-1024 | 0.9243 | -0.0256 | [-0.0459, -0.0061] | 97.50% | yes | 0.0016 |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-64 | 0.7971 | -0.1718 | [-0.1912, -0.1571] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-128 | 0.8906 | -0.0784 | [-0.0969, -0.0648] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-256 | 0.9442 | -0.0247 | [-0.0371, -0.0169] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-512 | 0.9675 | -0.0014 | [-0.0126, +0.0000] | 95.00% | no | 0.3040 |
| nq | hybrid-rerank | bge-small | fair | 8192 | section-aware | 0.9689 | +0.0000 | [-0.0144, +0.0000] | 98.75% | no | 0.5231 |
| nq | hybrid-rerank | bge-small | fair | 8192 | small-to-big | 0.9459 | -0.0230 | [-0.0414, -0.0110] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | bge-small | fair | 8192 | fixed-1024 | 0.9648 | -0.0041 | [-0.0182, +0.0000] | 95.00% | no | 0.1729 |
| nq | hybrid-rerank | nomic | production | 128 | fixed-64 | 0.2764 | -0.0556 | [-0.0865, -0.0234] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 128 | fixed-128 | 0.2968 | -0.0352 | [-0.0574, -0.0128] | 95.00% | yes | 0.0012 |
| nq | hybrid-rerank | nomic | production | 128 | section-aware | 0.0580 | -0.2740 | [-0.3105, -0.2382] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 128 | small-to-big | 0.3320 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9988 |
| nq | hybrid-rerank | nomic | production | 256 | fixed-64 | 0.3750 | -0.1247 | [-0.1558, -0.0931] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 256 | fixed-128 | 0.4335 | -0.0662 | [-0.0971, -0.0350] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 256 | fixed-256 | 0.4278 | -0.0719 | [-0.1094, -0.0342] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 256 | section-aware | 0.2403 | -0.2594 | [-0.2978, -0.2195] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 256 | small-to-big | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | nomic | production | 512 | fixed-64 | 0.4789 | -0.1821 | [-0.2196, -0.1503] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 512 | fixed-128 | 0.5667 | -0.0943 | [-0.1344, -0.0614] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 512 | fixed-256 | 0.5975 | -0.0635 | [-0.1028, -0.0318] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 512 | fixed-512 | 0.6114 | -0.0496 | [-0.0877, -0.0192] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 512 | section-aware | 0.6610 | +0.0000 | [-0.0267, +0.0000] | 98.33% | no | 0.6864 |
| nq | hybrid-rerank | nomic | production | 512 | small-to-big | 0.6541 | -0.0069 | [-0.0402, +0.0000] | 98.33% | no | 0.3136 |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.4789 | -0.3408 | [-0.3659, -0.3148] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.6887 | -0.1309 | [-0.1555, -0.1065] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.7350 | -0.0847 | [-0.1088, -0.0598] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.7683 | -0.0514 | [-0.0748, -0.0283] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 1024 | section-aware | 0.8197 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9981 |
| nq | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.7871 | -0.0326 | [-0.0541, -0.0103] | 95.00% | yes | 0.0019 |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.7416 | -0.0781 | [-0.1058, -0.0508] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 2048 | fixed-64 | 0.4789 | -0.4288 | [-0.4566, -0.3993] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 2048 | fixed-128 | 0.6887 | -0.2189 | [-0.2474, -0.1906] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 2048 | fixed-256 | 0.8439 | -0.0638 | [-0.0877, -0.0391] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 2048 | fixed-512 | 0.8720 | -0.0357 | [-0.0591, -0.0120] | 97.50% | yes | 0.0005 |
| nq | hybrid-rerank | nomic | production | 2048 | section-aware | 0.9077 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9994 |
| nq | hybrid-rerank | nomic | production | 2048 | small-to-big | 0.8774 | -0.0303 | [-0.0523, -0.0086] | 99.00% | yes | 0.0001 |
| nq | hybrid-rerank | nomic | production | 2048 | fixed-1024 | 0.8577 | -0.0500 | [-0.0781, -0.0225] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-64 | 0.4789 | -0.4529 | [-0.4815, -0.4306] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-128 | 0.6887 | -0.2431 | [-0.2729, -0.2202] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-256 | 0.8439 | -0.0880 | [-0.1107, -0.0717] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-512 | 0.9318 | +0.0000 | [-0.0143, +0.0000] | 95.00% | no | 0.5091 |
| nq | hybrid-rerank | nomic | production | 4096 | section-aware | 0.9299 | -0.0019 | [-0.0230, +0.0000] | 98.33% | no | 0.3715 |
| nq | hybrid-rerank | nomic | production | 4096 | small-to-big | 0.9089 | -0.0229 | [-0.0469, -0.0070] | 98.75% | yes | 0.0003 |
| nq | hybrid-rerank | nomic | production | 4096 | fixed-1024 | 0.9255 | -0.0063 | [-0.0263, +0.0000] | 97.50% | no | 0.1191 |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-64 | 0.4789 | -0.4916 | [-0.5143, -0.4690] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-128 | 0.6887 | -0.2818 | [-0.3086, -0.2562] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-256 | 0.8439 | -0.1267 | [-0.1466, -0.1072] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-512 | 0.9318 | -0.0387 | [-0.0554, -0.0229] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | section-aware | 0.9299 | -0.0406 | [-0.0618, -0.0191] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | small-to-big | 0.9089 | -0.0616 | [-0.0866, -0.0366] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | production | 8192 | fixed-1024 | 0.9705 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| nq | hybrid-rerank | nomic | fair | 128 | fixed-64 | 0.2764 | -0.0556 | [-0.0865, -0.0234] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 128 | fixed-128 | 0.2968 | -0.0352 | [-0.0574, -0.0128] | 95.00% | yes | 0.0012 |
| nq | hybrid-rerank | nomic | fair | 128 | section-aware | 0.0580 | -0.2740 | [-0.3105, -0.2382] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.3320 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9988 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-64 | 0.3750 | -0.1247 | [-0.1558, -0.0931] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-128 | 0.4335 | -0.0662 | [-0.0971, -0.0350] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-256 | 0.4278 | -0.0719 | [-0.1094, -0.0342] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | section-aware | 0.2403 | -0.2594 | [-0.2978, -0.2195] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-64 | 0.4789 | -0.1821 | [-0.2196, -0.1503] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-128 | 0.5667 | -0.0943 | [-0.1344, -0.0614] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-256 | 0.5975 | -0.0635 | [-0.1028, -0.0318] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-512 | 0.6114 | -0.0496 | [-0.0877, -0.0192] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | 0.6610 | +0.0000 | [-0.0281, +0.0000] | 98.75% | no | 0.6864 |
| nq | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.6541 | -0.0069 | [-0.0402, +0.0000] | 98.33% | no | 0.3136 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.5779 | -0.2418 | [-0.2673, -0.2158] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.6887 | -0.1309 | [-0.1555, -0.1065] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.7350 | -0.0847 | [-0.1088, -0.0598] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.7683 | -0.0514 | [-0.0748, -0.0283] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.8197 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9981 |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.7871 | -0.0326 | [-0.0541, -0.0103] | 95.00% | yes | 0.0019 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.7416 | -0.0781 | [-0.1058, -0.0508] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 0.6504 | -0.2583 | [-0.2855, -0.2308] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-128 | 0.7833 | -0.1254 | [-0.1522, -0.0987] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 0.8439 | -0.0648 | [-0.0883, -0.0401] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 0.8720 | -0.0367 | [-0.0615, -0.0115] | 98.33% | yes | 0.0001 |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.9087 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9998 |
| nq | hybrid-rerank | nomic | fair | 2048 | small-to-big | 0.8774 | -0.0313 | [-0.0534, -0.0093] | 99.00% | yes | 0.0001 |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 0.8577 | -0.0510 | [-0.0788, -0.0236] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 0.7466 | -0.2023 | [-0.2243, -0.1798] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-128 | 0.8357 | -0.1133 | [-0.1354, -0.0918] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 0.9147 | -0.0342 | [-0.0507, -0.0187] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 0.9318 | -0.0171 | [-0.0343, -0.0003] | 97.50% | yes | 0.0116 |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.9489 | +0.0000 | [-0.0022, +0.0000] | 98.75% | no | 0.9832 |
| nq | hybrid-rerank | nomic | fair | 4096 | small-to-big | 0.9304 | -0.0186 | [-0.0346, -0.0029] | 98.75% | yes | 0.0015 |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 0.9255 | -0.0234 | [-0.0435, -0.0039] | 97.50% | yes | 0.0037 |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 0.8190 | -0.1540 | [-0.1727, -0.1406] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-128 | 0.8963 | -0.0766 | [-0.0951, -0.0638] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 0.9488 | -0.0241 | [-0.0366, -0.0169] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 0.9722 | -0.0007 | [-0.0115, +0.0000] | 95.00% | no | 0.3082 |
| nq | hybrid-rerank | nomic | fair | 8192 | section-aware | 0.9729 | +0.0000 | [-0.0147, +0.0000] | 98.75% | no | 0.4555 |
| nq | hybrid-rerank | nomic | fair | 8192 | small-to-big | 0.9559 | -0.0170 | [-0.0357, -0.0060] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.9705 | -0.0024 | [-0.0156, +0.0000] | 95.00% | no | 0.2363 |
| nq | bm25 | - | production | 128 | fixed-64 | 0.1356 | -0.0418 | [-0.0665, -0.0247] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | production | 128 | fixed-128 | 0.1769 | -0.0006 | [-0.0201, +0.0000] | 97.50% | no | 0.4784 |
| nq | bm25 | - | production | 128 | section-aware | 0.0390 | -0.1385 | [-0.1710, -0.1144] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | production | 128 | small-to-big | 0.1775 | +0.0000 | [-0.0204, +0.0000] | 98.33% | no | 0.5216 |
| nq | bm25 | - | production | 256 | fixed-64 | 0.2111 | -0.0665 | [-0.0925, -0.0430] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | production | 256 | fixed-128 | 0.2669 | -0.0106 | [-0.0333, +0.0000] | 97.50% | no | 0.1349 |
| nq | bm25 | - | production | 256 | fixed-256 | 0.2591 | -0.0184 | [-0.0475, +0.0000] | 97.50% | no | 0.0521 |
| nq | bm25 | - | production | 256 | section-aware | 0.1640 | -0.1136 | [-0.1472, -0.0806] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | production | 256 | small-to-big | 0.2776 | +0.0000 | [-0.0161, +0.0000] | 98.33% | no | 0.8130 |
| nq | bm25 | - | production | 512 | fixed-64 | 0.3055 | -0.0946 | [-0.1280, -0.0694] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | production | 512 | fixed-128 | 0.3748 | -0.0253 | [-0.0551, -0.0035] | 98.33% | yes | 0.0036 |
| nq | bm25 | - | production | 512 | fixed-256 | 0.4002 | +0.0000 | [-0.0252, +0.0000] | 97.50% | no | 0.5845 |
| nq | bm25 | - | production | 512 | fixed-512 | 0.3711 | -0.0291 | [-0.0644, -0.0016] | 98.33% | yes | 0.0061 |
| nq | bm25 | - | production | 512 | section-aware | 0.3900 | -0.0102 | [-0.0412, +0.0000] | 97.50% | no | 0.1444 |
| nq | bm25 | - | production | 512 | small-to-big | 0.3941 | -0.0060 | [-0.0373, +0.0000] | 98.33% | no | 0.2614 |
| nq | bm25 | - | production | 1024 | fixed-64 | 0.3055 | -0.2684 | [-0.2955, -0.2417] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | production | 1024 | fixed-128 | 0.4956 | -0.0783 | [-0.1039, -0.0536] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | production | 1024 | fixed-256 | 0.5377 | -0.0362 | [-0.0609, -0.0125] | 95.00% | yes | 0.0017 |
| nq | bm25 | - | production | 1024 | fixed-512 | 0.5488 | -0.0252 | [-0.0509, +0.0000] | 95.00% | no | 0.0280 |
| nq | bm25 | - | production | 1024 | section-aware | 0.5739 | +0.0000 | [-0.0013, +0.0000] | 95.00% | no | 0.9673 |
| nq | bm25 | - | production | 1024 | small-to-big | 0.5416 | -0.0323 | [-0.0560, -0.0091] | 95.00% | yes | 0.0030 |
| nq | bm25 | - | production | 1024 | fixed-1024 | 0.4644 | -0.1095 | [-0.1417, -0.0781] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | production | 2048 | fixed-64 | 0.3055 | -0.4094 | [-0.4412, -0.3799] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | production | 2048 | fixed-128 | 0.4956 | -0.2193 | [-0.2537, -0.1892] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | production | 2048 | fixed-256 | 0.6680 | -0.0469 | [-0.0765, -0.0207] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | production | 2048 | fixed-512 | 0.7024 | -0.0125 | [-0.0393, +0.0000] | 97.50% | no | 0.1408 |
| nq | bm25 | - | production | 2048 | section-aware | 0.7149 | +0.0000 | [-0.0137, +0.0000] | 97.50% | no | 0.8591 |
| nq | bm25 | - | production | 2048 | small-to-big | 0.6790 | -0.0359 | [-0.0642, -0.0107] | 98.75% | yes | 0.0001 |
| nq | bm25 | - | production | 2048 | fixed-1024 | 0.6562 | -0.0587 | [-0.0932, -0.0277] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | fixed-64 | 0.3055 | -0.5063 | [-0.5345, -0.4776] | 97.50% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | fixed-128 | 0.4956 | -0.3163 | [-0.3488, -0.2833] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | fixed-256 | 0.6680 | -0.1439 | [-0.1709, -0.1178] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | fixed-512 | 0.8119 | +0.0000 | [-0.0013, +0.0000] | 97.50% | no | 0.9811 |
| nq | bm25 | - | production | 4096 | section-aware | 0.7679 | -0.0440 | [-0.0692, -0.0188] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | small-to-big | 0.7410 | -0.0709 | [-0.1021, -0.0409] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | production | 4096 | fixed-1024 | 0.7907 | -0.0211 | [-0.0438, +0.0000] | 97.50% | no | 0.0189 |
| nq | bm25 | - | production | 8192 | fixed-64 | 0.3055 | -0.5831 | [-0.6078, -0.5585] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | fixed-128 | 0.4956 | -0.3931 | [-0.4267, -0.3596] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | fixed-256 | 0.6680 | -0.2207 | [-0.2511, -0.1907] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | fixed-512 | 0.8119 | -0.0768 | [-0.0994, -0.0547] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | section-aware | 0.7679 | -0.1207 | [-0.1492, -0.0926] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | small-to-big | 0.7410 | -0.1477 | [-0.1801, -0.1155] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | production | 8192 | fixed-1024 | 0.8887 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| nq | bm25 | - | fair | 128 | fixed-64 | 0.1356 | -0.0418 | [-0.0665, -0.0247] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | fair | 128 | fixed-128 | 0.1769 | -0.0006 | [-0.0201, +0.0000] | 97.50% | no | 0.4784 |
| nq | bm25 | - | fair | 128 | section-aware | 0.0390 | -0.1385 | [-0.1710, -0.1144] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | fair | 128 | small-to-big | 0.1775 | +0.0000 | [-0.0204, +0.0000] | 98.33% | no | 0.5216 |
| nq | bm25 | - | fair | 256 | fixed-64 | 0.2111 | -0.0665 | [-0.0925, -0.0430] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 256 | fixed-128 | 0.2669 | -0.0106 | [-0.0333, +0.0000] | 97.50% | no | 0.1349 |
| nq | bm25 | - | fair | 256 | fixed-256 | 0.2591 | -0.0184 | [-0.0475, +0.0000] | 97.50% | no | 0.0521 |
| nq | bm25 | - | fair | 256 | section-aware | 0.1640 | -0.1136 | [-0.1472, -0.0806] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 256 | small-to-big | 0.2776 | +0.0000 | [-0.0161, +0.0000] | 98.33% | no | 0.8130 |
| nq | bm25 | - | fair | 512 | fixed-64 | 0.3055 | -0.0946 | [-0.1280, -0.0694] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | fair | 512 | fixed-128 | 0.3748 | -0.0253 | [-0.0551, -0.0035] | 98.33% | yes | 0.0036 |
| nq | bm25 | - | fair | 512 | fixed-256 | 0.4002 | +0.0000 | [-0.0252, +0.0000] | 97.50% | no | 0.5845 |
| nq | bm25 | - | fair | 512 | fixed-512 | 0.3711 | -0.0291 | [-0.0657, -0.0002] | 98.75% | yes | 0.0061 |
| nq | bm25 | - | fair | 512 | section-aware | 0.3900 | -0.0102 | [-0.0443, +0.0000] | 98.75% | no | 0.1444 |
| nq | bm25 | - | fair | 512 | small-to-big | 0.3941 | -0.0060 | [-0.0373, +0.0000] | 98.33% | no | 0.2614 |
| nq | bm25 | - | fair | 1024 | fixed-64 | 0.4052 | -0.1688 | [-0.1954, -0.1427] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 1024 | fixed-128 | 0.4956 | -0.0783 | [-0.1039, -0.0536] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 1024 | fixed-256 | 0.5377 | -0.0362 | [-0.0609, -0.0125] | 95.00% | yes | 0.0017 |
| nq | bm25 | - | fair | 1024 | fixed-512 | 0.5488 | -0.0252 | [-0.0509, +0.0000] | 95.00% | no | 0.0280 |
| nq | bm25 | - | fair | 1024 | section-aware | 0.5739 | +0.0000 | [-0.0013, +0.0000] | 95.00% | no | 0.9673 |
| nq | bm25 | - | fair | 1024 | small-to-big | 0.5416 | -0.0323 | [-0.0560, -0.0091] | 95.00% | yes | 0.0030 |
| nq | bm25 | - | fair | 1024 | fixed-1024 | 0.4644 | -0.1095 | [-0.1417, -0.0781] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 2048 | fixed-64 | 0.4926 | -0.2243 | [-0.2547, -0.1953] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | fair | 2048 | fixed-128 | 0.5991 | -0.1178 | [-0.1506, -0.0880] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | fair | 2048 | fixed-256 | 0.6680 | -0.0489 | [-0.0787, -0.0220] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 2048 | fixed-512 | 0.7024 | -0.0145 | [-0.0427, +0.0000] | 98.33% | no | 0.1052 |
| nq | bm25 | - | fair | 2048 | section-aware | 0.7169 | +0.0000 | [-0.0150, +0.0000] | 98.75% | no | 0.8947 |
| nq | bm25 | - | fair | 2048 | small-to-big | 0.6810 | -0.0359 | [-0.0641, -0.0101] | 98.75% | yes | 0.0001 |
| nq | bm25 | - | fair | 2048 | fixed-1024 | 0.6562 | -0.0607 | [-0.0955, -0.0293] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | fair | 4096 | fixed-64 | 0.5774 | -0.2344 | [-0.2624, -0.2125] | 97.50% | yes | 0.0000 |
| nq | bm25 | - | fair | 4096 | fixed-128 | 0.6944 | -0.1174 | [-0.1476, -0.0947] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 4096 | fixed-256 | 0.7731 | -0.0388 | [-0.0645, -0.0193] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | fair | 4096 | fixed-512 | 0.8119 | +0.0000 | [-0.0211, +0.0000] | 98.33% | no | 0.5748 |
| nq | bm25 | - | fair | 4096 | section-aware | 0.8099 | -0.0020 | [-0.0270, +0.0000] | 98.75% | no | 0.4167 |
| nq | bm25 | - | fair | 4096 | small-to-big | 0.7820 | -0.0299 | [-0.0603, -0.0098] | 99.17% | yes | 0.0000 |
| nq | bm25 | - | fair | 4096 | fixed-1024 | 0.7907 | -0.0211 | [-0.0477, -0.0012] | 97.50% | yes | 0.0085 |
| nq | bm25 | - | fair | 8192 | fixed-64 | 0.6532 | -0.2364 | [-0.2594, -0.2150] | 95.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 8192 | fixed-128 | 0.7743 | -0.1154 | [-0.1443, -0.0895] | 98.75% | yes | 0.0000 |
| nq | bm25 | - | fair | 8192 | fixed-256 | 0.8452 | -0.0445 | [-0.0693, -0.0224] | 98.33% | yes | 0.0000 |
| nq | bm25 | - | fair | 8192 | fixed-512 | 0.8733 | -0.0164 | [-0.0348, +0.0000] | 98.33% | no | 0.0106 |
| nq | bm25 | - | fair | 8192 | section-aware | 0.8749 | -0.0147 | [-0.0397, +0.0000] | 98.75% | no | 0.0668 |
| nq | bm25 | - | fair | 8192 | small-to-big | 0.8542 | -0.0355 | [-0.0638, -0.0120] | 99.00% | yes | 0.0000 |
| nq | bm25 | - | fair | 8192 | fixed-1024 | 0.8897 | +0.0000 | [-0.0053, +0.0000] | 95.00% | no | 0.9226 |
| nq | hybrid | bge-small | production | 128 | fixed-64 | 0.2078 | -0.0543 | [-0.0820, -0.0291] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 128 | fixed-128 | 0.2621 | +0.0000 | [-0.0145, +0.0000] | 97.50% | no | 0.8359 |
| nq | hybrid | bge-small | production | 128 | section-aware | 0.0470 | -0.2151 | [-0.2490, -0.1835] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 128 | small-to-big | 0.2517 | -0.0104 | [-0.0370, +0.0000] | 98.75% | no | 0.1641 |
| nq | hybrid | bge-small | production | 256 | fixed-64 | 0.3124 | -0.0873 | [-0.1173, -0.0578] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 256 | fixed-128 | 0.3735 | -0.0262 | [-0.0527, +0.0000] | 97.50% | no | 0.0130 |
| nq | hybrid | bge-small | production | 256 | fixed-256 | 0.3517 | -0.0480 | [-0.0816, -0.0128] | 98.33% | yes | 0.0008 |
| nq | hybrid | bge-small | production | 256 | section-aware | 0.2070 | -0.1927 | [-0.2298, -0.1554] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 256 | small-to-big | 0.3997 | +0.0000 | [-0.0040, +0.0000] | 98.75% | no | 0.9862 |
| nq | hybrid | bge-small | production | 512 | fixed-64 | 0.4172 | -0.1240 | [-0.1590, -0.0957] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 512 | fixed-128 | 0.5006 | -0.0406 | [-0.0762, -0.0138] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 512 | fixed-256 | 0.5336 | -0.0076 | [-0.0399, +0.0000] | 97.50% | no | 0.2950 |
| nq | hybrid | bge-small | production | 512 | fixed-512 | 0.4650 | -0.0761 | [-0.1195, -0.0402] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 512 | section-aware | 0.5130 | -0.0282 | [-0.0618, +0.0000] | 97.50% | no | 0.0134 |
| nq | hybrid | bge-small | production | 512 | small-to-big | 0.5411 | +0.0000 | [-0.0282, +0.0000] | 98.75% | no | 0.6916 |
| nq | hybrid | bge-small | production | 1024 | fixed-64 | 0.4172 | -0.2868 | [-0.3152, -0.2658] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 1024 | fixed-128 | 0.6427 | -0.0612 | [-0.0887, -0.0421] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 1024 | fixed-256 | 0.6806 | -0.0234 | [-0.0511, -0.0038] | 95.00% | yes | 0.0116 |
| nq | hybrid | bge-small | production | 1024 | fixed-512 | 0.6698 | -0.0341 | [-0.0632, -0.0126] | 95.00% | yes | 0.0011 |
| nq | hybrid | bge-small | production | 1024 | section-aware | 0.7039 | +0.0000 | [-0.0212, +0.0000] | 95.00% | no | 0.6046 |
| nq | hybrid | bge-small | production | 1024 | small-to-big | 0.7008 | -0.0031 | [-0.0275, +0.0000] | 95.00% | no | 0.3827 |
| nq | hybrid | bge-small | production | 1024 | fixed-1024 | 0.5606 | -0.1433 | [-0.1781, -0.1160] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 2048 | fixed-64 | 0.4172 | -0.4028 | [-0.4318, -0.3779] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 2048 | fixed-128 | 0.6427 | -0.1772 | [-0.2068, -0.1528] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 2048 | fixed-256 | 0.8072 | -0.0127 | [-0.0381, +0.0000] | 97.50% | no | 0.0785 |
| nq | hybrid | bge-small | production | 2048 | fixed-512 | 0.8082 | -0.0117 | [-0.0395, +0.0000] | 97.50% | no | 0.1187 |
| nq | hybrid | bge-small | production | 2048 | section-aware | 0.8097 | -0.0102 | [-0.0341, +0.0000] | 97.50% | no | 0.1079 |
| nq | hybrid | bge-small | production | 2048 | small-to-big | 0.8199 | +0.0000 | [-0.0204, +0.0000] | 98.75% | no | 0.6949 |
| nq | hybrid | bge-small | production | 2048 | fixed-1024 | 0.7575 | -0.0624 | [-0.0982, -0.0339] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | fixed-64 | 0.4172 | -0.4947 | [-0.5219, -0.4674] | 97.50% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | fixed-128 | 0.6427 | -0.2691 | [-0.3013, -0.2393] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | fixed-256 | 0.8072 | -0.1046 | [-0.1301, -0.0800] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | fixed-512 | 0.9119 | +0.0000 | [+0.0000, +0.0000] | 97.50% | no | 1.0000 |
| nq | hybrid | bge-small | production | 4096 | section-aware | 0.8607 | -0.0512 | [-0.0783, -0.0250] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | small-to-big | 0.8559 | -0.0559 | [-0.0839, -0.0272] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 4096 | fixed-1024 | 0.8667 | -0.0452 | [-0.0663, -0.0250] | 97.50% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | fixed-64 | 0.4172 | -0.5180 | [-0.5427, -0.4937] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | fixed-128 | 0.6427 | -0.2925 | [-0.3230, -0.2627] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | fixed-256 | 0.8072 | -0.1280 | [-0.1556, -0.1006] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | fixed-512 | 0.9119 | -0.0233 | [-0.0417, -0.0051] | 98.33% | yes | 0.0010 |
| nq | hybrid | bge-small | production | 8192 | section-aware | 0.8607 | -0.0745 | [-0.1015, -0.0477] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | small-to-big | 0.8559 | -0.0793 | [-0.1090, -0.0496] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | production | 8192 | fixed-1024 | 0.9352 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9990 |
| nq | hybrid | bge-small | fair | 128 | fixed-64 | 0.2078 | -0.0543 | [-0.0820, -0.0291] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 128 | fixed-128 | 0.2621 | +0.0000 | [-0.0145, +0.0000] | 97.50% | no | 0.8359 |
| nq | hybrid | bge-small | fair | 128 | section-aware | 0.0470 | -0.2151 | [-0.2490, -0.1835] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 128 | small-to-big | 0.2517 | -0.0104 | [-0.0379, +0.0000] | 99.00% | no | 0.1641 |
| nq | hybrid | bge-small | fair | 256 | fixed-64 | 0.3124 | -0.0873 | [-0.1173, -0.0578] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 256 | fixed-128 | 0.3735 | -0.0262 | [-0.0527, +0.0000] | 97.50% | no | 0.0130 |
| nq | hybrid | bge-small | fair | 256 | fixed-256 | 0.3517 | -0.0480 | [-0.0842, -0.0107] | 99.00% | yes | 0.0008 |
| nq | hybrid | bge-small | fair | 256 | section-aware | 0.2070 | -0.1927 | [-0.2298, -0.1554] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 256 | small-to-big | 0.3997 | +0.0000 | [-0.0047, +0.0000] | 99.00% | no | 0.9862 |
| nq | hybrid | bge-small | fair | 512 | fixed-64 | 0.4172 | -0.1240 | [-0.1590, -0.0957] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 512 | fixed-128 | 0.5006 | -0.0406 | [-0.0762, -0.0138] | 99.17% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 512 | fixed-256 | 0.5336 | -0.0076 | [-0.0399, +0.0000] | 97.50% | no | 0.2950 |
| nq | hybrid | bge-small | fair | 512 | fixed-512 | 0.4650 | -0.0761 | [-0.1195, -0.0402] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 512 | section-aware | 0.5130 | -0.0282 | [-0.0658, +0.0000] | 98.75% | no | 0.0134 |
| nq | hybrid | bge-small | fair | 512 | small-to-big | 0.5411 | +0.0000 | [-0.0293, +0.0000] | 99.00% | no | 0.6916 |
| nq | hybrid | bge-small | fair | 1024 | fixed-64 | 0.5319 | -0.1720 | [-0.1993, -0.1519] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 1024 | fixed-128 | 0.6427 | -0.0612 | [-0.0887, -0.0421] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 1024 | fixed-256 | 0.6806 | -0.0234 | [-0.0511, -0.0038] | 95.00% | yes | 0.0116 |
| nq | hybrid | bge-small | fair | 1024 | fixed-512 | 0.6698 | -0.0341 | [-0.0632, -0.0126] | 95.00% | yes | 0.0011 |
| nq | hybrid | bge-small | fair | 1024 | section-aware | 0.7039 | +0.0000 | [-0.0212, +0.0000] | 95.00% | no | 0.6046 |
| nq | hybrid | bge-small | fair | 1024 | small-to-big | 0.7008 | -0.0031 | [-0.0275, +0.0000] | 95.00% | no | 0.3827 |
| nq | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.5606 | -0.1433 | [-0.1781, -0.1160] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 2048 | fixed-64 | 0.6427 | -0.1807 | [-0.2091, -0.1561] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 2048 | fixed-128 | 0.7407 | -0.0827 | [-0.1103, -0.0601] | 99.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 2048 | fixed-256 | 0.8072 | -0.0162 | [-0.0415, +0.0000] | 97.50% | no | 0.0373 |
| nq | hybrid | bge-small | fair | 2048 | fixed-512 | 0.8082 | -0.0153 | [-0.0446, +0.0000] | 98.33% | no | 0.0659 |
| nq | hybrid | bge-small | fair | 2048 | section-aware | 0.8147 | -0.0087 | [-0.0354, +0.0000] | 98.75% | no | 0.1663 |
| nq | hybrid | bge-small | fair | 2048 | small-to-big | 0.8234 | +0.0000 | [-0.0207, +0.0000] | 99.00% | no | 0.7305 |
| nq | hybrid | bge-small | fair | 2048 | fixed-1024 | 0.7575 | -0.0659 | [-0.1017, -0.0363] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 4096 | fixed-64 | 0.7356 | -0.1771 | [-0.2034, -0.1578] | 97.50% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 4096 | fixed-128 | 0.8361 | -0.0766 | [-0.1024, -0.0585] | 98.75% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 4096 | fixed-256 | 0.8933 | -0.0194 | [-0.0411, -0.0042] | 98.75% | yes | 0.0008 |
| nq | hybrid | bge-small | fair | 4096 | fixed-512 | 0.9119 | -0.0008 | [-0.0222, +0.0000] | 98.33% | no | 0.4637 |
| nq | hybrid | bge-small | fair | 4096 | section-aware | 0.9127 | +0.0000 | [-0.0215, +0.0000] | 98.75% | no | 0.5299 |
| nq | hybrid | bge-small | fair | 4096 | small-to-big | 0.8973 | -0.0154 | [-0.0389, +0.0000] | 99.00% | no | 0.0056 |
| nq | hybrid | bge-small | fair | 4096 | fixed-1024 | 0.8667 | -0.0460 | [-0.0723, -0.0285] | 97.50% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 8192 | fixed-64 | 0.7971 | -0.1619 | [-0.1797, -0.1446] | 95.00% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 8192 | fixed-128 | 0.8906 | -0.0684 | [-0.0863, -0.0510] | 98.33% | yes | 0.0000 |
| nq | hybrid | bge-small | fair | 8192 | fixed-256 | 0.9442 | -0.0148 | [-0.0286, -0.0014] | 98.33% | yes | 0.0044 |
| nq | hybrid | bge-small | fair | 8192 | fixed-512 | 0.9495 | -0.0095 | [-0.0237, +0.0000] | 98.33% | no | 0.0498 |
| nq | hybrid | bge-small | fair | 8192 | section-aware | 0.9590 | +0.0000 | [-0.0052, +0.0000] | 98.75% | no | 0.9430 |
| nq | hybrid | bge-small | fair | 8192 | small-to-big | 0.9432 | -0.0158 | [-0.0309, -0.0010] | 99.17% | yes | 0.0022 |
| nq | hybrid | bge-small | fair | 8192 | fixed-1024 | 0.9352 | -0.0238 | [-0.0397, -0.0088] | 95.00% | yes | 0.0006 |
| nq | hybrid | nomic | production | 128 | fixed-64 | 0.2236 | -0.0399 | [-0.0672, -0.0142] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | production | 128 | fixed-128 | 0.2501 | -0.0133 | [-0.0332, +0.0000] | 95.00% | no | 0.0911 |
| nq | hybrid | nomic | production | 128 | section-aware | 0.0470 | -0.2164 | [-0.2504, -0.1841] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | production | 128 | small-to-big | 0.2634 | +0.0000 | [-0.0111, +0.0000] | 98.75% | no | 0.9089 |
| nq | hybrid | nomic | production | 256 | fixed-64 | 0.3226 | -0.0885 | [-0.1180, -0.0596] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 256 | fixed-128 | 0.3748 | -0.0362 | [-0.0633, -0.0100] | 98.33% | yes | 0.0007 |
| nq | hybrid | nomic | production | 256 | fixed-256 | 0.3628 | -0.0482 | [-0.0825, -0.0135] | 98.33% | yes | 0.0003 |
| nq | hybrid | nomic | production | 256 | section-aware | 0.2100 | -0.2011 | [-0.2391, -0.1640] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 256 | small-to-big | 0.4111 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9990 |
| nq | hybrid | nomic | production | 512 | fixed-64 | 0.4222 | -0.1172 | [-0.1522, -0.0889] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | production | 512 | fixed-128 | 0.5065 | -0.0330 | [-0.0657, -0.0085] | 97.50% | yes | 0.0010 |
| nq | hybrid | nomic | production | 512 | fixed-256 | 0.5249 | -0.0145 | [-0.0428, +0.0000] | 95.00% | no | 0.1009 |
| nq | hybrid | nomic | production | 512 | fixed-512 | 0.4666 | -0.0729 | [-0.1153, -0.0392] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | production | 512 | section-aware | 0.5300 | -0.0095 | [-0.0408, +0.0000] | 97.50% | no | 0.2256 |
| nq | hybrid | nomic | production | 512 | small-to-big | 0.5395 | +0.0000 | [-0.0264, +0.0000] | 98.75% | no | 0.6725 |
| nq | hybrid | nomic | production | 1024 | fixed-64 | 0.4222 | -0.3077 | [-0.3330, -0.2825] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 1024 | fixed-128 | 0.6378 | -0.0921 | [-0.1162, -0.0690] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 1024 | fixed-256 | 0.6735 | -0.0564 | [-0.0805, -0.0330] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 1024 | fixed-512 | 0.6758 | -0.0542 | [-0.0799, -0.0296] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 1024 | section-aware | 0.7299 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9806 |
| nq | hybrid | nomic | production | 1024 | small-to-big | 0.7052 | -0.0248 | [-0.0480, -0.0012] | 95.00% | yes | 0.0194 |
| nq | hybrid | nomic | production | 1024 | fixed-1024 | 0.5604 | -0.1695 | [-0.2030, -0.1373] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 2048 | fixed-64 | 0.4222 | -0.4130 | [-0.4418, -0.3866] | 98.33% | yes | 0.0000 |
| nq | hybrid | nomic | production | 2048 | fixed-128 | 0.6378 | -0.1975 | [-0.2267, -0.1720] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | production | 2048 | fixed-256 | 0.8094 | -0.0258 | [-0.0495, -0.0050] | 97.50% | yes | 0.0026 |
| nq | hybrid | nomic | production | 2048 | fixed-512 | 0.8079 | -0.0273 | [-0.0546, -0.0049] | 97.50% | yes | 0.0041 |
| nq | hybrid | nomic | production | 2048 | section-aware | 0.8279 | -0.0073 | [-0.0286, +0.0000] | 97.50% | no | 0.2146 |
| nq | hybrid | nomic | production | 2048 | small-to-big | 0.8352 | +0.0000 | [-0.0160, +0.0000] | 98.75% | no | 0.7787 |
| nq | hybrid | nomic | production | 2048 | fixed-1024 | 0.7492 | -0.0861 | [-0.1213, -0.0553] | 98.33% | yes | 0.0000 |
| nq | hybrid | nomic | production | 4096 | fixed-64 | 0.4222 | -0.4837 | [-0.5100, -0.4571] | 97.50% | yes | 0.0000 |
| nq | hybrid | nomic | production | 4096 | fixed-128 | 0.6378 | -0.2681 | [-0.2996, -0.2386] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 4096 | fixed-256 | 0.8094 | -0.0965 | [-0.1204, -0.0730] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 4096 | fixed-512 | 0.9059 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9968 |
| nq | hybrid | nomic | production | 4096 | section-aware | 0.8807 | -0.0253 | [-0.0472, -0.0032] | 98.33% | yes | 0.0029 |
| nq | hybrid | nomic | production | 4096 | small-to-big | 0.8679 | -0.0380 | [-0.0653, -0.0122] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | production | 4096 | fixed-1024 | 0.8756 | -0.0304 | [-0.0498, -0.0110] | 97.50% | yes | 0.0003 |
| nq | hybrid | nomic | production | 8192 | fixed-64 | 0.4222 | -0.5242 | [-0.5477, -0.5005] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | fixed-128 | 0.6378 | -0.3087 | [-0.3400, -0.2784] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | fixed-256 | 0.8094 | -0.1370 | [-0.1645, -0.1091] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | fixed-512 | 0.9059 | -0.0405 | [-0.0584, -0.0234] | 98.33% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | section-aware | 0.8807 | -0.0658 | [-0.0922, -0.0400] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | small-to-big | 0.8679 | -0.0785 | [-0.1065, -0.0501] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | production | 8192 | fixed-1024 | 0.9465 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 1.0000 |
| nq | hybrid | nomic | fair | 128 | fixed-64 | 0.2236 | -0.0399 | [-0.0672, -0.0142] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 128 | fixed-128 | 0.2501 | -0.0133 | [-0.0332, +0.0000] | 95.00% | no | 0.0911 |
| nq | hybrid | nomic | fair | 128 | section-aware | 0.0470 | -0.2164 | [-0.2504, -0.1841] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 128 | small-to-big | 0.2634 | +0.0000 | [-0.0119, +0.0000] | 99.17% | no | 0.9089 |
| nq | hybrid | nomic | fair | 256 | fixed-64 | 0.3226 | -0.0885 | [-0.1180, -0.0596] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 256 | fixed-128 | 0.3748 | -0.0362 | [-0.0633, -0.0100] | 98.33% | yes | 0.0007 |
| nq | hybrid | nomic | fair | 256 | fixed-256 | 0.3628 | -0.0482 | [-0.0848, -0.0109] | 99.00% | yes | 0.0003 |
| nq | hybrid | nomic | fair | 256 | section-aware | 0.2100 | -0.2011 | [-0.2391, -0.1640] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 256 | small-to-big | 0.4111 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9990 |
| nq | hybrid | nomic | fair | 512 | fixed-64 | 0.4222 | -0.1172 | [-0.1522, -0.0889] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 512 | fixed-128 | 0.5065 | -0.0330 | [-0.0657, -0.0085] | 97.50% | yes | 0.0010 |
| nq | hybrid | nomic | fair | 512 | fixed-256 | 0.5249 | -0.0145 | [-0.0428, +0.0000] | 95.00% | no | 0.1009 |
| nq | hybrid | nomic | fair | 512 | fixed-512 | 0.4666 | -0.0729 | [-0.1153, -0.0392] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 512 | section-aware | 0.5300 | -0.0095 | [-0.0446, +0.0000] | 98.75% | no | 0.2256 |
| nq | hybrid | nomic | fair | 512 | small-to-big | 0.5395 | +0.0000 | [-0.0288, +0.0000] | 99.17% | no | 0.6725 |
| nq | hybrid | nomic | fair | 1024 | fixed-64 | 0.5444 | -0.1855 | [-0.2104, -0.1611] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 1024 | fixed-128 | 0.6378 | -0.0921 | [-0.1162, -0.0690] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 1024 | fixed-256 | 0.6735 | -0.0564 | [-0.0805, -0.0330] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 1024 | fixed-512 | 0.6758 | -0.0542 | [-0.0799, -0.0296] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 1024 | section-aware | 0.7299 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9792 |
| nq | hybrid | nomic | fair | 1024 | small-to-big | 0.7055 | -0.0245 | [-0.0476, -0.0009] | 95.00% | yes | 0.0208 |
| nq | hybrid | nomic | fair | 1024 | fixed-1024 | 0.5604 | -0.1695 | [-0.2030, -0.1373] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 2048 | fixed-64 | 0.6504 | -0.1870 | [-0.2155, -0.1629] | 98.33% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 2048 | fixed-128 | 0.7482 | -0.0892 | [-0.1175, -0.0650] | 99.17% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 2048 | fixed-256 | 0.8094 | -0.0280 | [-0.0529, -0.0066] | 98.33% | yes | 0.0010 |
| nq | hybrid | nomic | fair | 2048 | fixed-512 | 0.8079 | -0.0295 | [-0.0576, -0.0059] | 98.33% | yes | 0.0016 |
| nq | hybrid | nomic | fair | 2048 | section-aware | 0.8319 | -0.0055 | [-0.0291, +0.0000] | 98.75% | no | 0.2772 |
| nq | hybrid | nomic | fair | 2048 | small-to-big | 0.8374 | +0.0000 | [-0.0193, +0.0000] | 99.17% | no | 0.7202 |
| nq | hybrid | nomic | fair | 2048 | fixed-1024 | 0.7492 | -0.0883 | [-0.1233, -0.0588] | 98.33% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 4096 | fixed-64 | 0.7466 | -0.1703 | [-0.1929, -0.1485] | 97.50% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 4096 | fixed-128 | 0.8357 | -0.0813 | [-0.1046, -0.0595] | 99.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 4096 | fixed-256 | 0.8962 | -0.0207 | [-0.0378, -0.0049] | 97.50% | yes | 0.0020 |
| nq | hybrid | nomic | fair | 4096 | fixed-512 | 0.9059 | -0.0110 | [-0.0289, +0.0000] | 97.50% | no | 0.0833 |
| nq | hybrid | nomic | fair | 4096 | section-aware | 0.9169 | +0.0000 | [-0.0095, +0.0000] | 98.75% | no | 0.8838 |
| nq | hybrid | nomic | fair | 4096 | small-to-big | 0.9065 | -0.0104 | [-0.0270, +0.0000] | 99.17% | no | 0.0309 |
| nq | hybrid | nomic | fair | 4096 | fixed-1024 | 0.8756 | -0.0413 | [-0.0654, -0.0190] | 97.50% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 8192 | fixed-64 | 0.8190 | -0.1450 | [-0.1617, -0.1292] | 95.00% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 8192 | fixed-128 | 0.8963 | -0.0676 | [-0.0856, -0.0515] | 98.75% | yes | 0.0000 |
| nq | hybrid | nomic | fair | 8192 | fixed-256 | 0.9488 | -0.0151 | [-0.0285, -0.0035] | 98.75% | yes | 0.0004 |
| nq | hybrid | nomic | fair | 8192 | fixed-512 | 0.9570 | -0.0070 | [-0.0198, +0.0000] | 97.50% | no | 0.1117 |
| nq | hybrid | nomic | fair | 8192 | section-aware | 0.9639 | +0.0000 | [-0.0080, +0.0000] | 98.75% | no | 0.8694 |
| nq | hybrid | nomic | fair | 8192 | small-to-big | 0.9542 | -0.0097 | [-0.0230, +0.0000] | 99.17% | no | 0.0122 |
| nq | hybrid | nomic | fair | 8192 | fixed-1024 | 0.9465 | -0.0175 | [-0.0322, -0.0042] | 95.00% | yes | 0.0063 |
| nq | vector | bge-small | production | 128 | fixed-64 | 0.2602 | -0.0411 | [-0.0629, -0.0195] | 95.00% | yes | 0.0002 |
| nq | vector | bge-small | production | 128 | fixed-128 | 0.3013 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9998 |
| nq | vector | bge-small | production | 128 | section-aware | 0.0510 | -0.2503 | [-0.2871, -0.2141] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | production | 128 | small-to-big | 0.2328 | -0.0685 | [-0.1018, -0.0363] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | production | 256 | fixed-64 | 0.3567 | -0.0834 | [-0.1129, -0.0566] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | production | 256 | fixed-128 | 0.4401 | +0.0000 | [-0.0115, +0.0000] | 98.33% | no | 0.9236 |
| nq | vector | bge-small | production | 256 | fixed-256 | 0.4116 | -0.0285 | [-0.0622, +0.0000] | 98.33% | no | 0.0194 |
| nq | vector | bge-small | production | 256 | section-aware | 0.2162 | -0.2239 | [-0.2651, -0.1848] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 256 | small-to-big | 0.4200 | -0.0201 | [-0.0528, +0.0000] | 99.00% | no | 0.0570 |
| nq | vector | bge-small | production | 512 | fixed-64 | 0.4652 | -0.1123 | [-0.1483, -0.0826] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 512 | fixed-128 | 0.5612 | -0.0162 | [-0.0494, +0.0000] | 98.33% | no | 0.0842 |
| nq | vector | bge-small | production | 512 | fixed-256 | 0.5569 | -0.0205 | [-0.0590, +0.0000] | 98.33% | no | 0.0654 |
| nq | vector | bge-small | production | 512 | fixed-512 | 0.5296 | -0.0479 | [-0.0907, -0.0128] | 98.75% | yes | 0.0002 |
| nq | vector | bge-small | production | 512 | section-aware | 0.5578 | -0.0197 | [-0.0499, +0.0000] | 95.00% | no | 0.0744 |
| nq | vector | bge-small | production | 512 | small-to-big | 0.5774 | +0.0000 | [-0.0246, +0.0000] | 99.00% | no | 0.7758 |
| nq | vector | bge-small | production | 1024 | fixed-64 | 0.4652 | -0.2919 | [-0.3170, -0.2669] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 1024 | fixed-128 | 0.6762 | -0.0809 | [-0.1046, -0.0572] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 1024 | fixed-256 | 0.7232 | -0.0339 | [-0.0602, -0.0083] | 95.00% | yes | 0.0054 |
| nq | vector | bge-small | production | 1024 | fixed-512 | 0.6863 | -0.0707 | [-0.0990, -0.0420] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 1024 | section-aware | 0.7257 | -0.0314 | [-0.0579, -0.0057] | 95.00% | yes | 0.0080 |
| nq | vector | bge-small | production | 1024 | small-to-big | 0.7571 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9866 |
| nq | vector | bge-small | production | 1024 | fixed-1024 | 0.6293 | -0.1278 | [-0.1607, -0.0951] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 2048 | fixed-64 | 0.4652 | -0.3913 | [-0.4218, -0.3605] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | production | 2048 | fixed-128 | 0.6762 | -0.1803 | [-0.2099, -0.1515] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | production | 2048 | fixed-256 | 0.8313 | -0.0252 | [-0.0516, +0.0000] | 98.33% | no | 0.0104 |
| nq | vector | bge-small | production | 2048 | fixed-512 | 0.8178 | -0.0387 | [-0.0684, -0.0099] | 98.33% | yes | 0.0005 |
| nq | vector | bge-small | production | 2048 | section-aware | 0.8310 | -0.0255 | [-0.0509, -0.0008] | 97.50% | yes | 0.0104 |
| nq | vector | bge-small | production | 2048 | small-to-big | 0.8565 | +0.0000 | [-0.0054, +0.0000] | 99.00% | no | 0.9787 |
| nq | vector | bge-small | production | 2048 | fixed-1024 | 0.7689 | -0.0876 | [-0.1229, -0.0546] | 98.33% | yes | 0.0000 |
| nq | vector | bge-small | production | 4096 | fixed-64 | 0.4652 | -0.4217 | [-0.4515, -0.3943] | 98.33% | yes | 0.0000 |
| nq | vector | bge-small | production | 4096 | fixed-128 | 0.6762 | -0.2106 | [-0.2437, -0.1829] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 4096 | fixed-256 | 0.8313 | -0.0556 | [-0.0812, -0.0349] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | production | 4096 | fixed-512 | 0.8868 | +0.0000 | [-0.0168, +0.0000] | 97.50% | no | 0.7437 |
| nq | vector | bge-small | production | 4096 | section-aware | 0.8607 | -0.0262 | [-0.0500, -0.0065] | 98.33% | yes | 0.0008 |
| nq | vector | bge-small | production | 4096 | small-to-big | 0.8797 | -0.0072 | [-0.0357, +0.0000] | 99.00% | no | 0.2552 |
| nq | vector | bge-small | production | 4096 | fixed-1024 | 0.8596 | -0.0272 | [-0.0498, -0.0097] | 97.50% | yes | 0.0003 |
| nq | vector | bge-small | production | 8192 | fixed-64 | 0.4652 | -0.4382 | [-0.4678, -0.4088] | 97.50% | yes | 0.0000 |
| nq | vector | bge-small | production | 8192 | fixed-128 | 0.6762 | -0.2271 | [-0.2606, -0.1960] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | production | 8192 | fixed-256 | 0.8313 | -0.0721 | [-0.1002, -0.0447] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | production | 8192 | fixed-512 | 0.8868 | -0.0165 | [-0.0352, +0.0000] | 97.50% | no | 0.0186 |
| nq | vector | bge-small | production | 8192 | section-aware | 0.8607 | -0.0427 | [-0.0698, -0.0168] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | production | 8192 | small-to-big | 0.8797 | -0.0237 | [-0.0551, +0.0000] | 99.00% | no | 0.0231 |
| nq | vector | bge-small | production | 8192 | fixed-1024 | 0.9033 | +0.0000 | [-0.0021, +0.0000] | 95.00% | no | 0.9583 |
| nq | vector | bge-small | fair | 128 | fixed-64 | 0.2602 | -0.0411 | [-0.0629, -0.0195] | 95.00% | yes | 0.0002 |
| nq | vector | bge-small | fair | 128 | fixed-128 | 0.3013 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9998 |
| nq | vector | bge-small | fair | 128 | section-aware | 0.0510 | -0.2503 | [-0.2871, -0.2141] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | fair | 128 | small-to-big | 0.2328 | -0.0685 | [-0.1018, -0.0363] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | fair | 256 | fixed-64 | 0.3567 | -0.0834 | [-0.1129, -0.0566] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | fair | 256 | fixed-128 | 0.4401 | +0.0000 | [-0.0115, +0.0000] | 98.33% | no | 0.9236 |
| nq | vector | bge-small | fair | 256 | fixed-256 | 0.4116 | -0.0285 | [-0.0597, +0.0000] | 97.50% | no | 0.0194 |
| nq | vector | bge-small | fair | 256 | section-aware | 0.2162 | -0.2239 | [-0.2651, -0.1848] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 256 | small-to-big | 0.4200 | -0.0201 | [-0.0528, +0.0000] | 99.00% | no | 0.0570 |
| nq | vector | bge-small | fair | 512 | fixed-64 | 0.4652 | -0.1126 | [-0.1489, -0.0830] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 512 | fixed-128 | 0.5612 | -0.0165 | [-0.0498, +0.0000] | 98.33% | no | 0.0810 |
| nq | vector | bge-small | fair | 512 | fixed-256 | 0.5569 | -0.0208 | [-0.0573, +0.0000] | 97.50% | no | 0.0629 |
| nq | vector | bge-small | fair | 512 | fixed-512 | 0.5296 | -0.0482 | [-0.0887, -0.0142] | 98.33% | yes | 0.0002 |
| nq | vector | bge-small | fair | 512 | section-aware | 0.5588 | -0.0190 | [-0.0494, +0.0000] | 95.00% | no | 0.0812 |
| nq | vector | bge-small | fair | 512 | small-to-big | 0.5777 | +0.0000 | [-0.0248, +0.0000] | 99.00% | no | 0.7747 |
| nq | vector | bge-small | fair | 1024 | fixed-64 | 0.5662 | -0.1917 | [-0.2167, -0.1670] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 1024 | fixed-128 | 0.6762 | -0.0817 | [-0.1053, -0.0582] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 1024 | fixed-256 | 0.7232 | -0.0347 | [-0.0612, -0.0090] | 95.00% | yes | 0.0043 |
| nq | vector | bge-small | fair | 1024 | fixed-512 | 0.6863 | -0.0716 | [-0.0998, -0.0428] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 1024 | section-aware | 0.7277 | -0.0302 | [-0.0567, -0.0044] | 95.00% | yes | 0.0112 |
| nq | vector | bge-small | fair | 1024 | small-to-big | 0.7579 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9845 |
| nq | vector | bge-small | fair | 1024 | fixed-1024 | 0.6293 | -0.1287 | [-0.1614, -0.0958] | 95.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 2048 | fixed-64 | 0.6589 | -0.2047 | [-0.2332, -0.1759] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | fair | 2048 | fixed-128 | 0.7697 | -0.0938 | [-0.1213, -0.0668] | 99.17% | yes | 0.0000 |
| nq | vector | bge-small | fair | 2048 | fixed-256 | 0.8313 | -0.0323 | [-0.0584, -0.0062] | 98.33% | yes | 0.0011 |
| nq | vector | bge-small | fair | 2048 | fixed-512 | 0.8178 | -0.0457 | [-0.0769, -0.0147] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | fair | 2048 | section-aware | 0.8390 | -0.0246 | [-0.0492, -0.0002] | 97.50% | yes | 0.0117 |
| nq | vector | bge-small | fair | 2048 | small-to-big | 0.8636 | +0.0000 | [-0.0041, +0.0000] | 99.00% | no | 0.9872 |
| nq | vector | bge-small | fair | 2048 | fixed-1024 | 0.7689 | -0.0947 | [-0.1295, -0.0613] | 98.33% | yes | 0.0000 |
| nq | vector | bge-small | fair | 4096 | fixed-64 | 0.7409 | -0.1824 | [-0.2074, -0.1584] | 98.33% | yes | 0.0000 |
| nq | vector | bge-small | fair | 4096 | fixed-128 | 0.8511 | -0.0722 | [-0.0946, -0.0500] | 99.00% | yes | 0.0000 |
| nq | vector | bge-small | fair | 4096 | fixed-256 | 0.8945 | -0.0287 | [-0.0519, -0.0053] | 99.00% | yes | 0.0006 |
| nq | vector | bge-small | fair | 4096 | fixed-512 | 0.8868 | -0.0364 | [-0.0593, -0.0130] | 97.50% | yes | 0.0002 |
| nq | vector | bge-small | fair | 4096 | section-aware | 0.8990 | -0.0243 | [-0.0462, -0.0028] | 98.33% | yes | 0.0035 |
| nq | vector | bge-small | fair | 4096 | small-to-big | 0.9233 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 0.9957 |
| nq | vector | bge-small | fair | 4096 | fixed-1024 | 0.8596 | -0.0637 | [-0.0902, -0.0374] | 97.50% | yes | 0.0000 |
| nq | vector | bge-small | fair | 8192 | fixed-64 | 0.8064 | -0.1475 | [-0.1683, -0.1274] | 97.50% | yes | 0.0000 |
| nq | vector | bge-small | fair | 8192 | fixed-128 | 0.8973 | -0.0566 | [-0.0751, -0.0384] | 98.75% | yes | 0.0000 |
| nq | vector | bge-small | fair | 8192 | fixed-256 | 0.9297 | -0.0242 | [-0.0429, -0.0059] | 98.75% | yes | 0.0006 |
| nq | vector | bge-small | fair | 8192 | fixed-512 | 0.9350 | -0.0189 | [-0.0352, -0.0028] | 95.00% | yes | 0.0110 |
| nq | vector | bge-small | fair | 8192 | section-aware | 0.9309 | -0.0230 | [-0.0415, -0.0060] | 98.75% | yes | 0.0004 |
| nq | vector | bge-small | fair | 8192 | small-to-big | 0.9539 | +0.0000 | [-0.0023, +0.0000] | 99.00% | no | 0.9880 |
| nq | vector | bge-small | fair | 8192 | fixed-1024 | 0.9033 | -0.0506 | [-0.0706, -0.0315] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 128 | fixed-64 | 0.2947 | -0.0723 | [-0.1038, -0.0414] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | production | 128 | fixed-128 | 0.3408 | -0.0262 | [-0.0468, -0.0059] | 95.00% | yes | 0.0048 |
| nq | vector | nomic | production | 128 | section-aware | 0.0560 | -0.3110 | [-0.3472, -0.2739] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | production | 128 | small-to-big | 0.3670 | +0.0000 | [-0.0004, +0.0000] | 99.17% | no | 0.9952 |
| nq | vector | nomic | production | 256 | fixed-64 | 0.4012 | -0.1184 | [-0.1492, -0.0883] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | production | 256 | fixed-128 | 0.4827 | -0.0369 | [-0.0628, -0.0110] | 97.50% | yes | 0.0003 |
| nq | vector | nomic | production | 256 | fixed-256 | 0.4728 | -0.0468 | [-0.0809, -0.0137] | 97.50% | yes | 0.0010 |
| nq | vector | nomic | production | 256 | section-aware | 0.2340 | -0.2856 | [-0.3253, -0.2462] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | production | 256 | small-to-big | 0.5196 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9987 |
| nq | vector | nomic | production | 512 | fixed-64 | 0.5019 | -0.1491 | [-0.1893, -0.1229] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | production | 512 | fixed-128 | 0.6093 | -0.0417 | [-0.0825, -0.0152] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | production | 512 | fixed-256 | 0.6359 | -0.0151 | [-0.0489, +0.0000] | 95.00% | no | 0.0734 |
| nq | vector | nomic | production | 512 | fixed-512 | 0.5656 | -0.0854 | [-0.1303, -0.0550] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | production | 512 | section-aware | 0.6510 | +0.0000 | [-0.0354, +0.0000] | 98.75% | no | 0.4795 |
| nq | vector | nomic | production | 512 | small-to-big | 0.6504 | -0.0006 | [-0.0384, +0.0000] | 99.17% | no | 0.4471 |
| nq | vector | nomic | production | 1024 | fixed-64 | 0.5019 | -0.3138 | [-0.3401, -0.2920] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 1024 | fixed-128 | 0.7090 | -0.1067 | [-0.1320, -0.0859] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 1024 | fixed-256 | 0.7677 | -0.0479 | [-0.0734, -0.0274] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 1024 | fixed-512 | 0.7365 | -0.0792 | [-0.1068, -0.0567] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 1024 | section-aware | 0.8157 | +0.0000 | [-0.0160, +0.0000] | 95.00% | no | 0.7280 |
| nq | vector | nomic | production | 1024 | small-to-big | 0.8084 | -0.0073 | [-0.0302, +0.0000] | 95.00% | no | 0.2720 |
| nq | vector | nomic | production | 1024 | fixed-1024 | 0.6257 | -0.1900 | [-0.2230, -0.1608] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 2048 | fixed-64 | 0.5019 | -0.3961 | [-0.4243, -0.3689] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | production | 2048 | fixed-128 | 0.7090 | -0.1889 | [-0.2182, -0.1613] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | production | 2048 | fixed-256 | 0.8577 | -0.0402 | [-0.0649, -0.0175] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | production | 2048 | fixed-512 | 0.8553 | -0.0426 | [-0.0679, -0.0188] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | production | 2048 | section-aware | 0.8979 | +0.0000 | [-0.0121, +0.0000] | 98.75% | no | 0.8713 |
| nq | vector | nomic | production | 2048 | small-to-big | 0.8883 | -0.0096 | [-0.0333, +0.0000] | 99.17% | no | 0.1287 |
| nq | vector | nomic | production | 2048 | fixed-1024 | 0.7902 | -0.1077 | [-0.1401, -0.0773] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | production | 4096 | fixed-64 | 0.5019 | -0.4236 | [-0.4514, -0.4015] | 97.50% | yes | 0.0000 |
| nq | vector | nomic | production | 4096 | fixed-128 | 0.7090 | -0.2164 | [-0.2464, -0.1921] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | production | 4096 | fixed-256 | 0.8577 | -0.0677 | [-0.0915, -0.0497] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | production | 4096 | fixed-512 | 0.9254 | +0.0000 | [-0.0178, +0.0000] | 97.50% | no | 0.6012 |
| nq | vector | nomic | production | 4096 | section-aware | 0.9209 | -0.0045 | [-0.0269, +0.0000] | 98.75% | no | 0.2160 |
| nq | vector | nomic | production | 4096 | small-to-big | 0.9199 | -0.0055 | [-0.0322, +0.0000] | 99.17% | no | 0.1828 |
| nq | vector | nomic | production | 4096 | fixed-1024 | 0.8911 | -0.0343 | [-0.0569, -0.0187] | 97.50% | yes | 0.0000 |
| nq | vector | nomic | production | 8192 | fixed-64 | 0.5019 | -0.4374 | [-0.4622, -0.4136] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | production | 8192 | fixed-128 | 0.7090 | -0.2302 | [-0.2609, -0.2021] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | production | 8192 | fixed-256 | 0.8577 | -0.0816 | [-0.1059, -0.0586] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | production | 8192 | fixed-512 | 0.9254 | -0.0138 | [-0.0294, +0.0000] | 97.50% | no | 0.0213 |
| nq | vector | nomic | production | 8192 | section-aware | 0.9209 | -0.0183 | [-0.0420, +0.0000] | 98.75% | no | 0.0167 |
| nq | vector | nomic | production | 8192 | small-to-big | 0.9199 | -0.0193 | [-0.0475, +0.0000] | 99.17% | no | 0.0249 |
| nq | vector | nomic | production | 8192 | fixed-1024 | 0.9393 | +0.0000 | [-0.0034, +0.0000] | 95.00% | no | 0.9371 |
| nq | vector | nomic | fair | 128 | fixed-64 | 0.2947 | -0.0723 | [-0.1038, -0.0414] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | fair | 128 | fixed-128 | 0.3408 | -0.0262 | [-0.0468, -0.0059] | 95.00% | yes | 0.0048 |
| nq | vector | nomic | fair | 128 | section-aware | 0.0560 | -0.3110 | [-0.3472, -0.2739] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | fair | 128 | small-to-big | 0.3670 | +0.0000 | [-0.0004, +0.0000] | 99.17% | no | 0.9952 |
| nq | vector | nomic | fair | 256 | fixed-64 | 0.4012 | -0.1184 | [-0.1492, -0.0883] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 256 | fixed-128 | 0.4827 | -0.0369 | [-0.0628, -0.0110] | 97.50% | yes | 0.0003 |
| nq | vector | nomic | fair | 256 | fixed-256 | 0.4728 | -0.0468 | [-0.0831, -0.0116] | 98.33% | yes | 0.0010 |
| nq | vector | nomic | fair | 256 | section-aware | 0.2340 | -0.2856 | [-0.3253, -0.2462] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 256 | small-to-big | 0.5196 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 0.9987 |
| nq | vector | nomic | fair | 512 | fixed-64 | 0.5019 | -0.1491 | [-0.1893, -0.1229] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | fair | 512 | fixed-128 | 0.6093 | -0.0417 | [-0.0825, -0.0152] | 99.17% | yes | 0.0000 |
| nq | vector | nomic | fair | 512 | fixed-256 | 0.6359 | -0.0151 | [-0.0527, +0.0000] | 97.50% | no | 0.0734 |
| nq | vector | nomic | fair | 512 | fixed-512 | 0.5656 | -0.0854 | [-0.1303, -0.0550] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | fair | 512 | section-aware | 0.6510 | +0.0000 | [-0.0354, +0.0000] | 98.75% | no | 0.4795 |
| nq | vector | nomic | fair | 512 | small-to-big | 0.6504 | -0.0006 | [-0.0384, +0.0000] | 99.17% | no | 0.4471 |
| nq | vector | nomic | fair | 1024 | fixed-64 | 0.6031 | -0.2126 | [-0.2385, -0.1904] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 1024 | fixed-128 | 0.7090 | -0.1067 | [-0.1320, -0.0859] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 1024 | fixed-256 | 0.7677 | -0.0479 | [-0.0734, -0.0274] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 1024 | fixed-512 | 0.7365 | -0.0792 | [-0.1068, -0.0567] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 1024 | section-aware | 0.8157 | +0.0000 | [-0.0160, +0.0000] | 95.00% | no | 0.7280 |
| nq | vector | nomic | fair | 1024 | small-to-big | 0.8084 | -0.0073 | [-0.0302, +0.0000] | 95.00% | no | 0.2720 |
| nq | vector | nomic | fair | 1024 | fixed-1024 | 0.6257 | -0.1900 | [-0.2230, -0.1608] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 2048 | fixed-64 | 0.6991 | -0.1999 | [-0.2262, -0.1746] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | fair | 2048 | fixed-128 | 0.8052 | -0.0937 | [-0.1188, -0.0703] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 2048 | fixed-256 | 0.8577 | -0.0412 | [-0.0657, -0.0185] | 99.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 2048 | fixed-512 | 0.8553 | -0.0436 | [-0.0690, -0.0198] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | fair | 2048 | section-aware | 0.8989 | +0.0000 | [-0.0122, +0.0000] | 98.75% | no | 0.8633 |
| nq | vector | nomic | fair | 2048 | small-to-big | 0.8896 | -0.0093 | [-0.0329, +0.0000] | 99.17% | no | 0.1367 |
| nq | vector | nomic | fair | 2048 | fixed-1024 | 0.7902 | -0.1087 | [-0.1410, -0.0783] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | fair | 4096 | fixed-64 | 0.7827 | -0.1603 | [-0.1821, -0.1427] | 97.50% | yes | 0.0000 |
| nq | vector | nomic | fair | 4096 | fixed-128 | 0.8712 | -0.0718 | [-0.0914, -0.0561] | 98.75% | yes | 0.0000 |
| nq | vector | nomic | fair | 4096 | fixed-256 | 0.9236 | -0.0194 | [-0.0384, -0.0046] | 98.75% | yes | 0.0004 |
| nq | vector | nomic | fair | 4096 | fixed-512 | 0.9254 | -0.0176 | [-0.0386, -0.0008] | 97.50% | yes | 0.0103 |
| nq | vector | nomic | fair | 4096 | section-aware | 0.9419 | -0.0011 | [-0.0147, +0.0000] | 98.75% | no | 0.4137 |
| nq | vector | nomic | fair | 4096 | small-to-big | 0.9430 | +0.0000 | [-0.0132, +0.0000] | 99.17% | no | 0.5756 |
| nq | vector | nomic | fair | 4096 | fixed-1024 | 0.8911 | -0.0519 | [-0.0776, -0.0311] | 97.50% | yes | 0.0000 |
| nq | vector | nomic | fair | 8192 | fixed-64 | 0.8479 | -0.1171 | [-0.1334, -0.1032] | 95.00% | yes | 0.0000 |
| nq | vector | nomic | fair | 8192 | fixed-128 | 0.9156 | -0.0493 | [-0.0664, -0.0354] | 98.33% | yes | 0.0000 |
| nq | vector | nomic | fair | 8192 | fixed-256 | 0.9545 | -0.0104 | [-0.0248, +0.0000] | 97.50% | no | 0.0252 |
| nq | vector | nomic | fair | 8192 | fixed-512 | 0.9577 | -0.0073 | [-0.0198, +0.0000] | 95.00% | no | 0.0932 |
| nq | vector | nomic | fair | 8192 | section-aware | 0.9649 | +0.0000 | [-0.0090, +0.0000] | 98.75% | no | 0.7428 |
| nq | vector | nomic | fair | 8192 | small-to-big | 0.9609 | -0.0040 | [-0.0166, +0.0000] | 99.17% | no | 0.1387 |
| nq | vector | nomic | fair | 8192 | fixed-1024 | 0.9393 | -0.0257 | [-0.0417, -0.0121] | 95.00% | yes | 0.0001 |
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
