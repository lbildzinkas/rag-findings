# R7 - routing headroom and the router gate

Config hash: `ef70a24ab11c06fa815083633dec2e4975554f07b2467dfe4fdb6f0064839c5c`

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
interaction_reference: fixed-128
kind: headroom
primary_budget: 1024
resamples: 10000
run_name: v2-budget-view
runs:
- qasper/v2-baseline
- nq/v2-baseline
scope: collection
seed: 0
top_n: 20
view: budget
```

## Inputs

| run | run config hash |
|---|---|
| qasper/v2-baseline | `28fc1dc15c8ac341b982544b402db094b15997c8b808cf9733d9f9d734cb51d7` |
| nq/v2-baseline | `b88ce9188b6e18537719b8dc5850675abc3f472d121b8683b761ac304b576f9f` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| nq | 1000 | 500 | 500 | 0 | 1000 |
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `hybrid-rerank` (embedder nomic).

## Routing headroom

Best single chunking: highest mean retrieval recall at the budget. Oracle router: per question, the chunking with the highest recall (ties to the smaller chunk). Routing headroom: oracle router minus best single chunking; the best single chunking is re-selected inside every resample.

| dataset | pipeline | embedder | view | budget | best single chunking | best single recall | oracle router recall | routing headroom | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.1512 | 0.2352 | +0.0840 | [+0.0742, +0.0945] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.2296 | 0.3566 | +0.1271 | [+0.1151, +0.1393] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.3173 | 0.4774 | +0.1601 | [+0.1452, +0.1720] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.4269 | 0.5641 | +0.1373 | [+0.1263, +0.1485] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.4956 | 0.6044 | +0.1088 | [+0.0968, +0.1212] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.5334 | 0.6372 | +0.1038 | [+0.0927, +0.1146] | 97.50% | yes |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.5584 | 0.6703 | +0.1119 | [+0.1006, +0.1181] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.1512 | 0.2352 | +0.0840 | [+0.0742, +0.0945] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.2296 | 0.3566 | +0.1271 | [+0.1151, +0.1393] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | budget | 512 | small-to-big | 0.3173 | 0.4774 | +0.1601 | [+0.1452, +0.1720] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.4269 | 0.5641 | +0.1373 | [+0.1263, +0.1485] | 95.00% | yes |
| pooled | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.4956 | 0.6021 | +0.1065 | [+0.0945, +0.1190] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.5325 | 0.6286 | +0.0962 | [+0.0852, +0.1070] | 97.50% | yes |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 0.5584 | 0.6456 | +0.0872 | [+0.0779, +0.0961] | 95.00% | yes |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.3320 | 0.4837 | +0.1517 | [+0.1295, +0.1760] | 99.17% | yes |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.4997 | 0.7057 | +0.2060 | [+0.1797, +0.2324] | 99.00% | yes |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | 0.6600 | 0.8857 | +0.2257 | [+0.1947, +0.2500] | 98.75% | yes |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.8197 | 0.9583 | +0.1386 | [+0.1184, +0.1594] | 95.00% | yes |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.9087 | 0.9847 | +0.0760 | [+0.0569, +0.0955] | 98.33% | yes |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.9489 | 0.9927 | +0.0438 | [+0.0300, +0.0585] | 97.50% | yes |
| nq | hybrid-rerank | nomic | fair | 8192 | section-aware | 0.9729 | 0.9981 | +0.0251 | [+0.0153, +0.0304] | 95.00% | yes |
| nq | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.3320 | 0.4837 | +0.1517 | [+0.1295, +0.1760] | 99.17% | yes |
| nq | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.4997 | 0.7057 | +0.2060 | [+0.1797, +0.2324] | 99.00% | yes |
| nq | hybrid-rerank | nomic | budget | 512 | section-aware | 0.6600 | 0.8857 | +0.2257 | [+0.1947, +0.2500] | 98.75% | yes |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.8197 | 0.9583 | +0.1386 | [+0.1184, +0.1594] | 95.00% | yes |
| nq | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.9087 | 0.9845 | +0.0758 | [+0.0566, +0.0953] | 98.33% | yes |
| nq | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.9489 | 0.9926 | +0.0437 | [+0.0299, +0.0585] | 97.50% | yes |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 0.9722 | 0.9981 | +0.0258 | [+0.0165, +0.0320] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.0690 | 0.1221 | +0.0531 | [+0.0437, +0.0632] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.1066 | 0.1977 | +0.0911 | [+0.0787, +0.1040] | 99.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.1640 | 0.2915 | +0.1275 | [+0.1121, +0.1424] | 98.75% | yes |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.2480 | 0.3847 | +0.1367 | [+0.1238, +0.1496] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | 0.3076 | 0.4312 | +0.1237 | [+0.1084, +0.1388] | 98.33% | yes |
| qasper | hybrid-rerank | nomic | fair | 4096 | section-aware | 0.3443 | 0.4754 | +0.1311 | [+0.1159, +0.1444] | 97.50% | yes |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 0.3708 | 0.5211 | +0.1503 | [+0.1345, +0.1584] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.0690 | 0.1221 | +0.0531 | [+0.0437, +0.0632] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.1066 | 0.1977 | +0.0911 | [+0.0787, +0.1040] | 99.00% | yes |
| qasper | hybrid-rerank | nomic | budget | 512 | small-to-big | 0.1640 | 0.2915 | +0.1275 | [+0.1121, +0.1424] | 98.75% | yes |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.2480 | 0.3847 | +0.1367 | [+0.1238, +0.1496] | 95.00% | yes |
| qasper | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.3076 | 0.4281 | +0.1205 | [+0.1054, +0.1357] | 98.33% | yes |
| qasper | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.3429 | 0.4630 | +0.1201 | [+0.1048, +0.1330] | 97.50% | yes |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 0.3708 | 0.4852 | +0.1144 | [+0.1016, +0.1261] | 95.00% | yes |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Query-type oracle (secondary; does not change the gate)

The best chunking per labelled query type, applied to every question of that type. Query types come from the labels in hindsight, so no real router has them.

| dataset | pipeline | embedder | view | budget | precise pick | context pick | mixed pick | query-type oracle recall | gain over best single | CI | CI level | oracle router minus query-type oracle | CI | CI level |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | small-to-big | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0013] | 99.17% | +0.0840 | [+0.0742, +0.0944] | 99.17% |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0019] | 99.17% | +0.1271 | [+0.1151, +0.1392] | 99.00% |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | section-aware | small-to-big | 0.3219 | +0.0046 | [+0.0000, +0.0117] | 99.17% | +0.1554 | [+0.1411, +0.1686] | 98.75% |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0034] | 95.00% | +0.1373 | [+0.1262, +0.1479] | 95.00% |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | section-aware | 0.4956 | +0.0000 | [+0.0000, +0.0030] | 99.17% | +0.1088 | [+0.0968, +0.1211] | 98.33% |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | section-aware | section-aware | 0.5334 | +0.0000 | [+0.0000, +0.0083] | 99.17% | +0.1038 | [+0.0921, +0.1130] | 97.50% |
| pooled | hybrid-rerank | nomic | fair | 8192 | section-aware | fixed-1024 | section-aware | 0.5620 | +0.0036 | [+0.0000, +0.0112] | 99.17% | +0.1083 | [+0.0967, +0.1147] | 95.00% |
| pooled | hybrid-rerank | nomic | budget | 128 | small-to-big | small-to-big | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0013] | 99.17% | +0.0840 | [+0.0742, +0.0944] | 99.17% |
| pooled | hybrid-rerank | nomic | budget | 256 | small-to-big | small-to-big | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0019] | 99.17% | +0.1271 | [+0.1151, +0.1392] | 99.00% |
| pooled | hybrid-rerank | nomic | budget | 512 | small-to-big | section-aware | small-to-big | 0.3219 | +0.0046 | [+0.0000, +0.0117] | 99.17% | +0.1554 | [+0.1411, +0.1686] | 98.75% |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | section-aware | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0034] | 95.00% | +0.1373 | [+0.1262, +0.1479] | 95.00% |
| pooled | hybrid-rerank | nomic | budget | 2048 | section-aware | section-aware | section-aware | 0.4956 | +0.0000 | [+0.0000, +0.0030] | 99.17% | +0.1065 | [+0.0945, +0.1188] | 98.33% |
| pooled | hybrid-rerank | nomic | budget | 4096 | section-aware | section-aware | section-aware | 0.5325 | +0.0000 | [+0.0000, +0.0088] | 99.17% | +0.0962 | [+0.0842, +0.1051] | 97.50% |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.5584 | +0.0000 | [+0.0000, +0.0092] | 99.17% | +0.0872 | [+0.0769, +0.0935] | 95.00% |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | small-to-big | n/a | 0.3320 | +0.0000 | [+0.0000, +0.0060] | 99.17% | +0.1517 | [+0.1295, +0.1756] | 99.17% |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | n/a | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2060 | [+0.1797, +0.2324] | 99.00% |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | section-aware | n/a | 0.6600 | +0.0000 | [+0.0000, +0.0182] | 99.17% | +0.2257 | [+0.1925, +0.2478] | 98.75% |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | n/a | 0.8197 | +0.0000 | [+0.0000, +0.0024] | 95.00% | +0.1386 | [+0.1184, +0.1590] | 95.00% |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | n/a | 0.9087 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0760 | [+0.0569, +0.0952] | 98.33% |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | section-aware | n/a | 0.9489 | +0.0000 | [+0.0000, +0.0082] | 99.17% | +0.0438 | [+0.0299, +0.0571] | 97.50% |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-512 | section-aware | n/a | 0.9730 | +0.0001 | [+0.0000, +0.0077] | 99.17% | +0.0250 | [+0.0142, +0.0287] | 95.00% |
| nq | hybrid-rerank | nomic | budget | 128 | small-to-big | small-to-big | n/a | 0.3320 | +0.0000 | [+0.0000, +0.0060] | 99.17% | +0.1517 | [+0.1295, +0.1756] | 99.17% |
| nq | hybrid-rerank | nomic | budget | 256 | small-to-big | small-to-big | n/a | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 99.17% | +0.2060 | [+0.1797, +0.2324] | 99.00% |
| nq | hybrid-rerank | nomic | budget | 512 | section-aware | section-aware | n/a | 0.6600 | +0.0000 | [+0.0000, +0.0182] | 99.17% | +0.2257 | [+0.1925, +0.2478] | 98.75% |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | section-aware | n/a | 0.8197 | +0.0000 | [+0.0000, +0.0024] | 95.00% | +0.1386 | [+0.1184, +0.1590] | 95.00% |
| nq | hybrid-rerank | nomic | budget | 2048 | section-aware | section-aware | n/a | 0.9087 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0758 | [+0.0566, +0.0950] | 98.33% |
| nq | hybrid-rerank | nomic | budget | 4096 | section-aware | section-aware | n/a | 0.9489 | +0.0000 | [+0.0000, +0.0082] | 99.17% | +0.0437 | [+0.0299, +0.0570] | 97.50% |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-512 | fixed-1024 | n/a | 0.9726 | +0.0004 | [+0.0000, +0.0078] | 99.17% | +0.0255 | [+0.0153, +0.0306] | 95.00% |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | fixed-64 | small-to-big | 0.0694 | +0.0005 | [+0.0000, +0.0037] | 99.17% | +0.0527 | [+0.0427, +0.0625] | 99.17% |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | small-to-big | small-to-big | 0.1066 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0911 | [+0.0780, +0.1031] | 99.00% |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | section-aware | small-to-big | 0.1683 | +0.0043 | [+0.0000, +0.0101] | 99.17% | +0.1232 | [+0.1078, +0.1376] | 98.75% |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | section-aware | section-aware | 0.2480 | +0.0000 | [+0.0000, +0.0080] | 95.00% | +0.1367 | [+0.1223, +0.1477] | 95.00% |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | section-aware | section-aware | 0.3076 | +0.0000 | [+0.0000, +0.0087] | 99.17% | +0.1237 | [+0.1077, +0.1372] | 98.33% |
| qasper | hybrid-rerank | nomic | fair | 4096 | small-to-big | fixed-512 | section-aware | 0.3472 | +0.0029 | [+0.0000, +0.0138] | 99.17% | +0.1282 | [+0.1116, +0.1401] | 97.50% |
| qasper | hybrid-rerank | nomic | fair | 8192 | small-to-big | fixed-1024 | section-aware | 0.3761 | +0.0053 | [+0.0000, +0.0157] | 99.17% | +0.1451 | [+0.1284, +0.1533] | 95.00% |
| qasper | hybrid-rerank | nomic | budget | 128 | small-to-big | fixed-64 | small-to-big | 0.0694 | +0.0005 | [+0.0000, +0.0037] | 99.17% | +0.0527 | [+0.0427, +0.0625] | 99.17% |
| qasper | hybrid-rerank | nomic | budget | 256 | small-to-big | small-to-big | small-to-big | 0.1066 | +0.0000 | [+0.0000, +0.0047] | 99.17% | +0.0911 | [+0.0780, +0.1031] | 99.00% |
| qasper | hybrid-rerank | nomic | budget | 512 | small-to-big | section-aware | small-to-big | 0.1683 | +0.0043 | [+0.0000, +0.0101] | 99.17% | +0.1232 | [+0.1078, +0.1376] | 98.75% |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | section-aware | section-aware | 0.2480 | +0.0000 | [+0.0000, +0.0080] | 95.00% | +0.1367 | [+0.1223, +0.1477] | 95.00% |
| qasper | hybrid-rerank | nomic | budget | 2048 | section-aware | section-aware | section-aware | 0.3076 | +0.0000 | [+0.0000, +0.0087] | 99.17% | +0.1205 | [+0.1045, +0.1339] | 98.33% |
| qasper | hybrid-rerank | nomic | budget | 4096 | small-to-big | fixed-512 | section-aware | 0.3472 | +0.0043 | [+0.0000, +0.0142] | 99.17% | +0.1158 | [+0.0998, +0.1280] | 97.50% |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | fixed-1024 | fixed-1024 | 0.3708 | +0.0000 | [+0.0000, +0.0151] | 99.17% | +0.1144 | [+0.0992, +0.1220] | 95.00% |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).

## Each chunking against the best single chunking

Difference: the chunking's mean recall minus the best single chunking's, with the best re-selected inside every resample (so the best chunking's own difference is 0 with a CI at or below 0). Best in resamples: the share of resamples in which the chunking was the best single chunking.

| dataset | pipeline | embedder | view | budget | chunking | mean recall | difference from best | CI | CI level | CI excludes 0 | best in resamples |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 128 | fixed-64 | 0.1225 | -0.0288 | [-0.0415, -0.0158] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | fixed-128 | 0.1230 | -0.0282 | [-0.0408, -0.0154] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | section-aware | 0.0398 | -0.1115 | [-0.1264, -0.0970] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-64 | 0.1777 | -0.0519 | [-0.0657, -0.0383] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-128 | 0.1999 | -0.0296 | [-0.0439, -0.0159] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-256 | 0.1764 | -0.0531 | [-0.0703, -0.0363] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | section-aware | 0.1188 | -0.1108 | [-0.1268, -0.0944] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0000] | 99.00% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-64 | 0.2351 | -0.0823 | [-0.0982, -0.0688] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-128 | 0.2742 | -0.0431 | [-0.0597, -0.0291] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-256 | 0.2727 | -0.0446 | [-0.0615, -0.0303] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-512 | 0.2601 | -0.0573 | [-0.0760, -0.0413] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 512 | section-aware | 0.3143 | -0.0030 | [-0.0178, +0.0000] | 98.75% | no | 0.3088 |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.3173 | +0.0000 | [-0.0124, +0.0000] | 99.00% | no | 0.6912 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.2931 | -0.1338 | [-0.1466, -0.1208] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.3519 | -0.0750 | [-0.0874, -0.0626] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.3686 | -0.0582 | [-0.0706, -0.0459] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.3702 | -0.0567 | [-0.0697, -0.0435] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9990 |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.4096 | -0.0173 | [-0.0280, -0.0065] | 95.00% | yes | 0.0010 |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.3353 | -0.0915 | [-0.1073, -0.0756] | 95.00% | yes | 0.0000 |
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
| pooled | hybrid-rerank | nomic | budget | 128 | fixed-64 | 0.1225 | -0.0288 | [-0.0415, -0.0158] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 128 | fixed-128 | 0.1230 | -0.0282 | [-0.0408, -0.0154] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 128 | section-aware | 0.0398 | -0.1115 | [-0.1264, -0.0970] | 99.17% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.1512 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | budget | 256 | fixed-64 | 0.1777 | -0.0519 | [-0.0657, -0.0383] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 256 | fixed-128 | 0.1999 | -0.0296 | [-0.0439, -0.0159] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 256 | fixed-256 | 0.1764 | -0.0531 | [-0.0703, -0.0363] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 256 | section-aware | 0.1188 | -0.1108 | [-0.1268, -0.0944] | 99.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.2296 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 1.0000 |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-64 | 0.2351 | -0.0823 | [-0.0982, -0.0688] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-128 | 0.2742 | -0.0431 | [-0.0597, -0.0291] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-256 | 0.2727 | -0.0446 | [-0.0615, -0.0303] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-512 | 0.2601 | -0.0573 | [-0.0760, -0.0413] | 98.75% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 512 | section-aware | 0.3143 | -0.0030 | [-0.0174, +0.0000] | 98.33% | no | 0.3088 |
| pooled | hybrid-rerank | nomic | budget | 512 | small-to-big | 0.3173 | +0.0000 | [-0.0121, +0.0000] | 98.75% | no | 0.6912 |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.2931 | -0.1338 | [-0.1466, -0.1208] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.3519 | -0.0750 | [-0.0874, -0.0626] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.3686 | -0.0582 | [-0.0706, -0.0459] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.3702 | -0.0567 | [-0.0697, -0.0435] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.4269 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9990 |
| pooled | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.4096 | -0.0173 | [-0.0280, -0.0065] | 95.00% | yes | 0.0010 |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.3353 | -0.0915 | [-0.1073, -0.0756] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 0.3091 | -0.1865 | [-0.2019, -0.1710] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-128 | 0.4123 | -0.0833 | [-0.0977, -0.0691] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 0.4426 | -0.0530 | [-0.0664, -0.0393] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 0.4512 | -0.0444 | [-0.0592, -0.0295] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.4956 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9998 |
| pooled | hybrid-rerank | nomic | budget | 2048 | small-to-big | 0.4789 | -0.0167 | [-0.0296, -0.0042] | 99.17% | yes | 0.0002 |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 0.4353 | -0.0603 | [-0.0772, -0.0433] | 98.33% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 0.3091 | -0.2234 | [-0.2383, -0.2088] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-128 | 0.4256 | -0.1069 | [-0.1198, -0.0945] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 0.4923 | -0.0402 | [-0.0516, -0.0288] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 0.5120 | -0.0205 | [-0.0330, -0.0080] | 97.50% | yes | 0.0002 |
| pooled | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.5325 | +0.0000 | [-0.0033, +0.0000] | 98.33% | no | 0.9508 |
| pooled | hybrid-rerank | nomic | budget | 4096 | small-to-big | 0.5249 | -0.0075 | [-0.0187, +0.0000] | 98.75% | no | 0.0490 |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 0.5055 | -0.0270 | [-0.0412, -0.0126] | 97.50% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 0.3091 | -0.2493 | [-0.2635, -0.2354] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-128 | 0.4256 | -0.1328 | [-0.1455, -0.1209] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 0.5003 | -0.0580 | [-0.0692, -0.0478] | 95.00% | yes | 0.0000 |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 0.5512 | -0.0071 | [-0.0162, +0.0000] | 95.00% | no | 0.0634 |
| pooled | hybrid-rerank | nomic | budget | 8192 | section-aware | 0.5438 | -0.0146 | [-0.0294, -0.0005] | 98.75% | yes | 0.0044 |
| pooled | hybrid-rerank | nomic | budget | 8192 | small-to-big | 0.5437 | -0.0146 | [-0.0297, -0.0007] | 99.00% | yes | 0.0034 |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 0.5584 | +0.0000 | [-0.0022, +0.0000] | 95.00% | no | 0.9288 |
| nq | hybrid-rerank | nomic | fair | 128 | fixed-64 | 0.2764 | -0.0556 | [-0.0865, -0.0234] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 128 | fixed-128 | 0.2968 | -0.0352 | [-0.0574, -0.0128] | 95.00% | yes | 0.0012 |
| nq | hybrid-rerank | nomic | fair | 128 | section-aware | 0.0580 | -0.2740 | [-0.3105, -0.2382] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | 0.3320 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9988 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-64 | 0.3750 | -0.1247 | [-0.1558, -0.0931] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-128 | 0.4335 | -0.0662 | [-0.0971, -0.0350] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-256 | 0.4278 | -0.0719 | [-0.1094, -0.0342] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | section-aware | 0.2403 | -0.2594 | [-0.2978, -0.2195] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-64 | 0.4789 | -0.1811 | [-0.2188, -0.1501] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-128 | 0.5667 | -0.0933 | [-0.1332, -0.0611] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-256 | 0.5975 | -0.0625 | [-0.1024, -0.0312] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-512 | 0.6104 | -0.0496 | [-0.0876, -0.0197] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | 0.6600 | +0.0000 | [-0.0291, +0.0000] | 98.75% | no | 0.6606 |
| nq | hybrid-rerank | nomic | fair | 512 | small-to-big | 0.6541 | -0.0059 | [-0.0395, +0.0000] | 98.33% | no | 0.3394 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.5779 | -0.2418 | [-0.2673, -0.2158] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.6887 | -0.1309 | [-0.1555, -0.1065] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.7350 | -0.0847 | [-0.1088, -0.0598] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.7683 | -0.0514 | [-0.0748, -0.0283] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.8197 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9981 |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.7871 | -0.0326 | [-0.0541, -0.0103] | 95.00% | yes | 0.0019 |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.7406 | -0.0791 | [-0.1069, -0.0519] | 95.00% | yes | 0.0000 |
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
| nq | hybrid-rerank | nomic | budget | 128 | fixed-64 | 0.2764 | -0.0556 | [-0.0865, -0.0234] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 128 | fixed-128 | 0.2968 | -0.0352 | [-0.0574, -0.0128] | 95.00% | yes | 0.0012 |
| nq | hybrid-rerank | nomic | budget | 128 | section-aware | 0.0580 | -0.2740 | [-0.3105, -0.2382] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.3320 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 0.9988 |
| nq | hybrid-rerank | nomic | budget | 256 | fixed-64 | 0.3750 | -0.1247 | [-0.1558, -0.0931] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 256 | fixed-128 | 0.4335 | -0.0662 | [-0.0971, -0.0350] | 99.17% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 256 | fixed-256 | 0.4278 | -0.0719 | [-0.1094, -0.0342] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 256 | section-aware | 0.2403 | -0.2594 | [-0.2978, -0.2195] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.4997 | +0.0000 | [+0.0000, +0.0000] | 98.33% | no | 1.0000 |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-64 | 0.4789 | -0.1811 | [-0.2188, -0.1501] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-128 | 0.5667 | -0.0933 | [-0.1332, -0.0611] | 99.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-256 | 0.5975 | -0.0625 | [-0.1024, -0.0312] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-512 | 0.6104 | -0.0496 | [-0.0876, -0.0197] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 512 | section-aware | 0.6600 | +0.0000 | [-0.0291, +0.0000] | 98.75% | no | 0.6606 |
| nq | hybrid-rerank | nomic | budget | 512 | small-to-big | 0.6541 | -0.0059 | [-0.0395, +0.0000] | 98.33% | no | 0.3394 |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.5779 | -0.2418 | [-0.2673, -0.2158] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.6887 | -0.1309 | [-0.1555, -0.1065] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.7350 | -0.0847 | [-0.1088, -0.0598] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.7683 | -0.0514 | [-0.0748, -0.0283] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.8197 | +0.0000 | [+0.0000, +0.0000] | 95.00% | no | 0.9981 |
| nq | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.7871 | -0.0326 | [-0.0541, -0.0103] | 95.00% | yes | 0.0019 |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.7406 | -0.0791 | [-0.1069, -0.0519] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 0.6076 | -0.3010 | [-0.3287, -0.2730] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-128 | 0.7833 | -0.1254 | [-0.1522, -0.0987] | 98.75% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 0.8439 | -0.0648 | [-0.0883, -0.0401] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 0.8720 | -0.0367 | [-0.0615, -0.0115] | 98.33% | yes | 0.0001 |
| nq | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.9087 | +0.0000 | [+0.0000, +0.0000] | 98.75% | no | 0.9998 |
| nq | hybrid-rerank | nomic | budget | 2048 | small-to-big | 0.8774 | -0.0313 | [-0.0538, -0.0089] | 99.17% | yes | 0.0001 |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 0.8577 | -0.0510 | [-0.0788, -0.0236] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 0.6076 | -0.3413 | [-0.3667, -0.3159] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-128 | 0.8038 | -0.1451 | [-0.1688, -0.1223] | 98.33% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 0.9147 | -0.0342 | [-0.0507, -0.0187] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 0.9318 | -0.0171 | [-0.0343, -0.0003] | 97.50% | yes | 0.0116 |
| nq | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.9489 | +0.0000 | [-0.0022, +0.0000] | 98.75% | no | 0.9832 |
| nq | hybrid-rerank | nomic | budget | 4096 | small-to-big | 0.9304 | -0.0186 | [-0.0346, -0.0029] | 98.75% | yes | 0.0015 |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 0.9255 | -0.0234 | [-0.0435, -0.0039] | 97.50% | yes | 0.0037 |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 0.6076 | -0.3646 | [-0.3880, -0.3449] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-128 | 0.8038 | -0.1684 | [-0.1915, -0.1493] | 97.50% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 0.9247 | -0.0475 | [-0.0624, -0.0369] | 95.00% | yes | 0.0000 |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 0.9722 | +0.0000 | [-0.0091, +0.0000] | 95.00% | no | 0.5429 |
| nq | hybrid-rerank | nomic | budget | 8192 | section-aware | 0.9669 | -0.0053 | [-0.0215, +0.0000] | 98.75% | no | 0.1123 |
| nq | hybrid-rerank | nomic | budget | 8192 | small-to-big | 0.9509 | -0.0213 | [-0.0406, -0.0079] | 99.00% | yes | 0.0002 |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 0.9705 | -0.0017 | [-0.0130, +0.0000] | 95.00% | no | 0.3446 |
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
| qasper | hybrid-rerank | nomic | budget | 128 | fixed-64 | 0.0524 | -0.0165 | [-0.0282, -0.0052] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 128 | fixed-128 | 0.0439 | -0.0250 | [-0.0371, -0.0136] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 128 | section-aware | 0.0315 | -0.0375 | [-0.0515, -0.0243] | 99.17% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 128 | small-to-big | 0.0690 | +0.0000 | [+0.0000, +0.0000] | 99.17% | no | 1.0000 |
| qasper | hybrid-rerank | nomic | budget | 256 | fixed-64 | 0.0879 | -0.0187 | [-0.0330, -0.0056] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 256 | fixed-128 | 0.0936 | -0.0130 | [-0.0246, -0.0020] | 95.00% | yes | 0.0106 |
| qasper | hybrid-rerank | nomic | budget | 256 | fixed-256 | 0.0620 | -0.0446 | [-0.0623, -0.0274] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 256 | section-aware | 0.0634 | -0.0431 | [-0.0576, -0.0287] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 256 | small-to-big | 0.1066 | +0.0000 | [-0.0019, +0.0000] | 99.17% | no | 0.9894 |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-64 | 0.1241 | -0.0400 | [-0.0561, -0.0255] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-128 | 0.1411 | -0.0229 | [-0.0400, -0.0069] | 99.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-256 | 0.1249 | -0.0391 | [-0.0565, -0.0228] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-512 | 0.1006 | -0.0634 | [-0.0847, -0.0442] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 512 | section-aware | 0.1570 | -0.0070 | [-0.0214, +0.0000] | 98.33% | no | 0.1197 |
| qasper | hybrid-rerank | nomic | budget | 512 | small-to-big | 0.1640 | +0.0000 | [-0.0082, +0.0000] | 99.17% | no | 0.8803 |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.1634 | -0.0846 | [-0.0996, -0.0705] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.1985 | -0.0495 | [-0.0639, -0.0358] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.2019 | -0.0462 | [-0.0605, -0.0324] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.1890 | -0.0591 | [-0.0752, -0.0436] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.2480 | +0.0000 | [-0.0019, +0.0000] | 95.00% | no | 0.9513 |
| qasper | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.2377 | -0.0103 | [-0.0223, +0.0000] | 95.00% | no | 0.0487 |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.1509 | -0.0972 | [-0.1167, -0.0781] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 0.1732 | -0.1344 | [-0.1525, -0.1165] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-128 | 0.2434 | -0.0642 | [-0.0823, -0.0467] | 98.75% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 0.2599 | -0.0477 | [-0.0639, -0.0312] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 0.2596 | -0.0479 | [-0.0664, -0.0299] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 2048 | section-aware | 0.3076 | +0.0000 | [-0.0041, +0.0000] | 98.33% | no | 0.9544 |
| qasper | hybrid-rerank | nomic | budget | 2048 | small-to-big | 0.2975 | -0.0101 | [-0.0251, +0.0000] | 99.17% | no | 0.0456 |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 0.2430 | -0.0646 | [-0.0861, -0.0439] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 0.1732 | -0.1697 | [-0.1883, -0.1541] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-128 | 0.2534 | -0.0895 | [-0.1068, -0.0754] | 98.33% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 0.3000 | -0.0429 | [-0.0585, -0.0300] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 0.3209 | -0.0220 | [-0.0389, -0.0075] | 97.50% | yes | 0.0003 |
| qasper | hybrid-rerank | nomic | budget | 4096 | section-aware | 0.3429 | +0.0000 | [-0.0118, +0.0000] | 98.33% | no | 0.6600 |
| qasper | hybrid-rerank | nomic | budget | 4096 | small-to-big | 0.3404 | -0.0025 | [-0.0178, +0.0000] | 99.17% | no | 0.3396 |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 0.3143 | -0.0286 | [-0.0479, -0.0120] | 97.50% | yes | 0.0001 |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 0.1732 | -0.1976 | [-0.2156, -0.1806] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-128 | 0.2534 | -0.1174 | [-0.1358, -0.1007] | 97.50% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 0.3072 | -0.0636 | [-0.0780, -0.0503] | 95.00% | yes | 0.0000 |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 0.3596 | -0.0111 | [-0.0237, +0.0000] | 95.00% | no | 0.0320 |
| qasper | hybrid-rerank | nomic | budget | 8192 | section-aware | 0.3512 | -0.0195 | [-0.0396, -0.0016] | 98.75% | yes | 0.0036 |
| qasper | hybrid-rerank | nomic | budget | 8192 | small-to-big | 0.3584 | -0.0124 | [-0.0331, +0.0000] | 99.17% | no | 0.0493 |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 0.3708 | +0.0000 | [-0.0040, +0.0000] | 95.00% | no | 0.9151 |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).
