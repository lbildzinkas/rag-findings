# R9 - the oracle router's chunking by query type

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

## The oracle router's chunking per query type, at 1024 tokens

Each cell: the share of the query type's questions for which the oracle router picks the chunking, and their count. Ties go to the smaller chunk, so a question on which every chunking scores the same goes to the smallest candidate; the last row of each block counts those questions.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.5388 (979) | 0.4314 (390) | 0.5756 (274) | 0.5139 (1643) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.1205 (219) | 0.1593 (144) | 0.0840 (40) | 0.1261 (403) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.1090 (198) | 0.1316 (119) | 0.1050 (50) | 0.1148 (367) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.0870 (158) | 0.1106 (100) | 0.0567 (27) | 0.0891 (285) |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0941 (171) | 0.1184 (107) | 0.1134 (54) | 0.1038 (332) |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0297 (54) | 0.0265 (24) | 0.0273 (13) | 0.0285 (91) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0209 (38) | 0.0221 (20) | 0.0378 (18) | 0.0238 (76) |
| pooled | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.4739 (861) | 0.3551 (321) | 0.5252 (250) | 0.4479 (1432) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.5388 (979) | 0.4314 (390) | 0.5756 (274) | 0.5139 (1643) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.1205 (219) | 0.1593 (144) | 0.0840 (40) | 0.1261 (403) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.1090 (198) | 0.1316 (119) | 0.1050 (50) | 0.1148 (367) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.0870 (158) | 0.1106 (100) | 0.0567 (27) | 0.0891 (285) |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.0941 (171) | 0.1184 (107) | 0.1134 (54) | 0.1038 (332) |
| pooled | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0297 (54) | 0.0265 (24) | 0.0273 (13) | 0.0285 (91) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0209 (38) | 0.0221 (20) | 0.0378 (18) | 0.0238 (76) |
| pooled | hybrid-rerank | nomic | budget | 1024 | every chunking tied | 0.4739 (861) | 0.3551 (321) | 0.5252 (250) | 0.4479 (1432) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.3040 (152) | 0.2740 (137) | n/a | 0.2890 (289) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2160 (108) | 0.2380 (119) | n/a | 0.2270 (227) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2020 (101) | 0.1860 (93) | n/a | 0.1940 (194) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1540 (77) | 0.1240 (62) | n/a | 0.1390 (139) |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0780 (39) | 0.1280 (64) | n/a | 0.1030 (103) |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0240 (12) | 0.0280 (14) | n/a | 0.0260 (26) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.2100 (105) | 0.1800 (90) | n/a | 0.1950 (195) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.3040 (152) | 0.2740 (137) | n/a | 0.2890 (289) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.2160 (108) | 0.2380 (119) | n/a | 0.2270 (227) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.2020 (101) | 0.1860 (93) | n/a | 0.1940 (194) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.1540 (77) | 0.1240 (62) | n/a | 0.1390 (139) |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.0780 (39) | 0.1280 (64) | n/a | 0.1030 (103) |
| nq | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0240 (12) | 0.0280 (14) | n/a | 0.0260 (26) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | nomic | budget | 1024 | every chunking tied | 0.2100 (105) | 0.1800 (90) | n/a | 0.1950 (195) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.6279 (827) | 0.6262 (253) | 0.5756 (274) | 0.6163 (1354) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.0843 (111) | 0.0619 (25) | 0.0840 (40) | 0.0801 (176) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.0737 (97) | 0.0644 (26) | 0.1050 (50) | 0.0787 (173) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.0615 (81) | 0.0941 (38) | 0.0567 (27) | 0.0665 (146) |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.1002 (132) | 0.1064 (43) | 0.1134 (54) | 0.1042 (229) |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0319 (42) | 0.0248 (10) | 0.0273 (13) | 0.0296 (65) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0205 (27) | 0.0223 (9) | 0.0378 (18) | 0.0246 (54) |
| qasper | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.5740 (756) | 0.5718 (231) | 0.5252 (250) | 0.5630 (1237) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.6279 (827) | 0.6262 (253) | 0.5756 (274) | 0.6163 (1354) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.0843 (111) | 0.0619 (25) | 0.0840 (40) | 0.0801 (176) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.0737 (97) | 0.0644 (26) | 0.1050 (50) | 0.0787 (173) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.0615 (81) | 0.0941 (38) | 0.0567 (27) | 0.0665 (146) |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.1002 (132) | 0.1064 (43) | 0.1134 (54) | 0.1042 (229) |
| qasper | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0319 (42) | 0.0248 (10) | 0.0273 (13) | 0.0296 (65) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0205 (27) | 0.0223 (9) | 0.0378 (18) | 0.0246 (54) |
| qasper | hybrid-rerank | nomic | budget | 1024 | every chunking tied | 0.5740 (756) | 0.5718 (231) | 0.5252 (250) | 0.5630 (1237) |

## The same, among the questions where the chunkings differ

Leaves out the questions on which every chunking scores the same, so the tie-break does not decide the picks.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1234 (118) | 0.1184 (69) | 0.1062 (24) | 0.1195 (211) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2291 (219) | 0.2470 (144) | 0.1770 (40) | 0.2283 (403) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2071 (198) | 0.2041 (119) | 0.2212 (50) | 0.2079 (367) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1653 (158) | 0.1715 (100) | 0.1195 (27) | 0.1615 (285) |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.1789 (171) | 0.1835 (107) | 0.2389 (54) | 0.1881 (332) |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0565 (54) | 0.0412 (24) | 0.0575 (13) | 0.0516 (91) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0397 (38) | 0.0343 (20) | 0.0796 (18) | 0.0431 (76) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.1234 (118) | 0.1184 (69) | 0.1062 (24) | 0.1195 (211) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.2291 (219) | 0.2470 (144) | 0.1770 (40) | 0.2283 (403) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.2071 (198) | 0.2041 (119) | 0.2212 (50) | 0.2079 (367) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.1653 (158) | 0.1715 (100) | 0.1195 (27) | 0.1615 (285) |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.1789 (171) | 0.1835 (107) | 0.2389 (54) | 0.1881 (332) |
| pooled | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0565 (54) | 0.0412 (24) | 0.0575 (13) | 0.0516 (91) |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0397 (38) | 0.0343 (20) | 0.0796 (18) | 0.0431 (76) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1190 (47) | 0.1146 (47) | n/a | 0.1168 (94) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2734 (108) | 0.2902 (119) | n/a | 0.2820 (227) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2557 (101) | 0.2268 (93) | n/a | 0.2410 (194) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1949 (77) | 0.1512 (62) | n/a | 0.1727 (139) |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0987 (39) | 0.1561 (64) | n/a | 0.1280 (103) |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0304 (12) | 0.0341 (14) | n/a | 0.0323 (26) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0278 (11) | 0.0268 (11) | n/a | 0.0273 (22) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.1190 (47) | 0.1146 (47) | n/a | 0.1168 (94) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.2734 (108) | 0.2902 (119) | n/a | 0.2820 (227) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.2557 (101) | 0.2268 (93) | n/a | 0.2410 (194) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.1949 (77) | 0.1512 (62) | n/a | 0.1727 (139) |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.0987 (39) | 0.1561 (64) | n/a | 0.1280 (103) |
| nq | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0304 (12) | 0.0341 (14) | n/a | 0.0323 (26) |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0278 (11) | 0.0268 (11) | n/a | 0.0273 (22) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1266 (71) | 0.1272 (22) | 0.1062 (24) | 0.1219 (117) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.1979 (111) | 0.1445 (25) | 0.1770 (40) | 0.1833 (176) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.1729 (97) | 0.1503 (26) | 0.2212 (50) | 0.1802 (173) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1444 (81) | 0.2197 (38) | 0.1195 (27) | 0.1521 (146) |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.2353 (132) | 0.2486 (43) | 0.2389 (54) | 0.2385 (229) |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0749 (42) | 0.0578 (10) | 0.0575 (13) | 0.0677 (65) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0481 (27) | 0.0520 (9) | 0.0796 (18) | 0.0563 (54) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 0.1266 (71) | 0.1272 (22) | 0.1062 (24) | 0.1219 (117) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-128 | 0.1979 (111) | 0.1445 (25) | 0.1770 (40) | 0.1833 (176) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 0.1729 (97) | 0.1503 (26) | 0.2212 (50) | 0.1802 (173) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 0.1444 (81) | 0.2197 (38) | 0.1195 (27) | 0.1521 (146) |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | 0.2353 (132) | 0.2486 (43) | 0.2389 (54) | 0.2385 (229) |
| qasper | hybrid-rerank | nomic | budget | 1024 | small-to-big | 0.0749 (42) | 0.0578 (10) | 0.0575 (13) | 0.0677 (65) |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 0.0481 (27) | 0.0520 (9) | 0.0796 (18) | 0.0563 (54) |
