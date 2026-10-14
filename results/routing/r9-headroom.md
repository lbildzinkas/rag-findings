# R9 - the oracle router's chunking by query type

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

## The oracle router's chunking per query type, at 1024 tokens

Each cell: the share of the query type's questions for which the oracle router picks the chunking, and their count. Ties go to the smaller chunk, so a question on which every chunking scores the same goes to the smallest candidate; the last row of each block counts those questions.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.5036 (915) | 0.3540 (320) | 0.5819 (277) | 0.4729 (1512) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.1420 (258) | 0.2091 (189) | 0.0840 (40) | 0.1523 (487) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.1277 (232) | 0.1515 (137) | 0.1113 (53) | 0.1320 (422) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.0897 (163) | 0.1073 (97) | 0.0504 (24) | 0.0888 (284) |
| pooled | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.0914 (166) | 0.1228 (111) | 0.1092 (52) | 0.1029 (329) |
| pooled | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0237 (43) | 0.0299 (27) | 0.0252 (12) | 0.0256 (82) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0220 (40) | 0.0254 (23) | 0.0378 (18) | 0.0253 (81) |
| pooled | hybrid-rerank | bge-small | production | 1024 | every chunking tied | 0.4739 (861) | 0.3230 (292) | 0.5609 (267) | 0.4442 (1420) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.5377 (977) | 0.4093 (370) | 0.5987 (285) | 0.5105 (1632) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.1194 (217) | 0.1692 (153) | 0.0735 (35) | 0.1267 (405) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.1216 (221) | 0.1416 (128) | 0.1050 (50) | 0.1248 (399) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.0864 (157) | 0.1029 (93) | 0.0483 (23) | 0.0854 (273) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.0892 (162) | 0.1217 (110) | 0.1113 (53) | 0.1017 (325) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0237 (43) | 0.0299 (27) | 0.0252 (12) | 0.0256 (82) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0220 (40) | 0.0254 (23) | 0.0378 (18) | 0.0253 (81) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | every chunking tied | 0.4750 (863) | 0.3418 (309) | 0.5525 (263) | 0.4489 (1435) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.5047 (917) | 0.3739 (338) | 0.5630 (268) | 0.4764 (1523) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.1447 (263) | 0.1980 (179) | 0.0903 (43) | 0.1517 (485) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.1139 (207) | 0.1427 (129) | 0.1113 (53) | 0.1217 (389) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.0892 (162) | 0.1150 (104) | 0.0588 (28) | 0.0920 (294) |
| pooled | hybrid-rerank | nomic | production | 1024 | section-aware | 0.0952 (173) | 0.1217 (110) | 0.1113 (53) | 0.1051 (336) |
| pooled | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0314 (57) | 0.0265 (24) | 0.0273 (13) | 0.0294 (94) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0209 (38) | 0.0221 (20) | 0.0378 (18) | 0.0238 (76) |
| pooled | hybrid-rerank | nomic | production | 1024 | every chunking tied | 0.4739 (861) | 0.3396 (307) | 0.5399 (257) | 0.4457 (1425) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.5388 (979) | 0.4314 (390) | 0.5756 (274) | 0.5139 (1643) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.1205 (219) | 0.1593 (144) | 0.0840 (40) | 0.1261 (403) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.1090 (198) | 0.1316 (119) | 0.1050 (50) | 0.1148 (367) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.0870 (158) | 0.1106 (100) | 0.0567 (27) | 0.0891 (285) |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0941 (171) | 0.1184 (107) | 0.1134 (54) | 0.1038 (332) |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0297 (54) | 0.0265 (24) | 0.0273 (13) | 0.0285 (91) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0209 (38) | 0.0221 (20) | 0.0378 (18) | 0.0238 (76) |
| pooled | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.4739 (861) | 0.3551 (321) | 0.5252 (250) | 0.4479 (1432) |
| pooled | bm25 | - | production | 1024 | fixed-64 | 0.5927 (1077) | 0.4624 (418) | 0.6765 (322) | 0.5683 (1817) |
| pooled | bm25 | - | production | 1024 | fixed-128 | 0.1310 (238) | 0.1593 (144) | 0.0924 (44) | 0.1332 (426) |
| pooled | bm25 | - | production | 1024 | fixed-256 | 0.0914 (166) | 0.1338 (121) | 0.0651 (31) | 0.0995 (318) |
| pooled | bm25 | - | production | 1024 | fixed-512 | 0.0743 (135) | 0.0951 (86) | 0.0588 (28) | 0.0779 (249) |
| pooled | bm25 | - | production | 1024 | section-aware | 0.0556 (101) | 0.0819 (74) | 0.0546 (26) | 0.0629 (201) |
| pooled | bm25 | - | production | 1024 | small-to-big | 0.0248 (45) | 0.0243 (22) | 0.0252 (12) | 0.0247 (79) |
| pooled | bm25 | - | production | 1024 | fixed-1024 | 0.0303 (55) | 0.0431 (39) | 0.0273 (13) | 0.0335 (107) |
| pooled | bm25 | - | production | 1024 | every chunking tied | 0.5696 (1035) | 0.4204 (380) | 0.6429 (306) | 0.5383 (1721) |
| pooled | bm25 | - | fair | 1024 | fixed-64 | 0.6219 (1130) | 0.5044 (456) | 0.6954 (331) | 0.5996 (1917) |
| pooled | bm25 | - | fair | 1024 | fixed-128 | 0.1090 (198) | 0.1239 (112) | 0.0819 (39) | 0.1092 (349) |
| pooled | bm25 | - | fair | 1024 | fixed-256 | 0.0870 (158) | 0.1283 (116) | 0.0609 (29) | 0.0948 (303) |
| pooled | bm25 | - | fair | 1024 | fixed-512 | 0.0726 (132) | 0.0940 (85) | 0.0588 (28) | 0.0766 (245) |
| pooled | bm25 | - | fair | 1024 | section-aware | 0.0550 (100) | 0.0819 (74) | 0.0546 (26) | 0.0626 (200) |
| pooled | bm25 | - | fair | 1024 | small-to-big | 0.0248 (45) | 0.0243 (22) | 0.0231 (11) | 0.0244 (78) |
| pooled | bm25 | - | fair | 1024 | fixed-1024 | 0.0297 (54) | 0.0431 (39) | 0.0252 (12) | 0.0328 (105) |
| pooled | bm25 | - | fair | 1024 | every chunking tied | 0.5575 (1013) | 0.4237 (383) | 0.6218 (296) | 0.5292 (1692) |
| pooled | hybrid | bge-small | production | 1024 | fixed-64 | 0.5762 (1047) | 0.4137 (374) | 0.6429 (306) | 0.5402 (1727) |
| pooled | hybrid | bge-small | production | 1024 | fixed-128 | 0.1447 (263) | 0.1991 (180) | 0.0756 (36) | 0.1498 (479) |
| pooled | hybrid | bge-small | production | 1024 | fixed-256 | 0.0919 (167) | 0.1527 (138) | 0.0903 (43) | 0.1089 (348) |
| pooled | hybrid | bge-small | production | 1024 | fixed-512 | 0.0655 (119) | 0.0841 (76) | 0.0483 (23) | 0.0682 (218) |
| pooled | hybrid | bge-small | production | 1024 | section-aware | 0.0759 (138) | 0.0819 (74) | 0.0756 (36) | 0.0776 (248) |
| pooled | hybrid | bge-small | production | 1024 | small-to-big | 0.0286 (52) | 0.0365 (33) | 0.0441 (21) | 0.0332 (106) |
| pooled | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0171 (31) | 0.0321 (29) | 0.0231 (11) | 0.0222 (71) |
| pooled | hybrid | bge-small | production | 1024 | every chunking tied | 0.5382 (978) | 0.3662 (331) | 0.6218 (296) | 0.5020 (1605) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-64 | 0.6114 (1111) | 0.4735 (428) | 0.6723 (320) | 0.5815 (1859) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-128 | 0.1211 (220) | 0.1549 (140) | 0.0588 (28) | 0.1214 (388) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-256 | 0.0853 (155) | 0.1438 (130) | 0.0819 (39) | 0.1013 (324) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-512 | 0.0638 (116) | 0.0796 (72) | 0.0483 (23) | 0.0660 (211) |
| pooled | hybrid | bge-small | fair | 1024 | section-aware | 0.0737 (134) | 0.0796 (72) | 0.0714 (34) | 0.0751 (240) |
| pooled | hybrid | bge-small | fair | 1024 | small-to-big | 0.0281 (51) | 0.0365 (33) | 0.0441 (21) | 0.0328 (105) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0165 (30) | 0.0321 (29) | 0.0231 (11) | 0.0219 (70) |
| pooled | hybrid | bge-small | fair | 1024 | every chunking tied | 0.5311 (965) | 0.3684 (333) | 0.6113 (291) | 0.4970 (1589) |
| pooled | hybrid | nomic | production | 1024 | fixed-64 | 0.5718 (1039) | 0.4038 (365) | 0.6408 (305) | 0.5346 (1709) |
| pooled | hybrid | nomic | production | 1024 | fixed-128 | 0.1486 (270) | 0.1980 (179) | 0.1071 (51) | 0.1564 (500) |
| pooled | hybrid | nomic | production | 1024 | fixed-256 | 0.0991 (180) | 0.1416 (128) | 0.0693 (33) | 0.1067 (341) |
| pooled | hybrid | nomic | production | 1024 | fixed-512 | 0.0671 (122) | 0.1128 (102) | 0.0504 (24) | 0.0776 (248) |
| pooled | hybrid | nomic | production | 1024 | section-aware | 0.0666 (121) | 0.0841 (76) | 0.0735 (35) | 0.0726 (232) |
| pooled | hybrid | nomic | production | 1024 | small-to-big | 0.0314 (57) | 0.0332 (30) | 0.0357 (17) | 0.0325 (104) |
| pooled | hybrid | nomic | production | 1024 | fixed-1024 | 0.0154 (28) | 0.0265 (24) | 0.0231 (11) | 0.0197 (63) |
| pooled | hybrid | nomic | production | 1024 | every chunking tied | 0.5316 (966) | 0.3540 (320) | 0.6050 (288) | 0.4923 (1574) |
| pooled | hybrid | nomic | fair | 1024 | fixed-64 | 0.6087 (1106) | 0.4624 (418) | 0.6576 (313) | 0.5746 (1837) |
| pooled | hybrid | nomic | fair | 1024 | fixed-128 | 0.1216 (221) | 0.1538 (139) | 0.0924 (44) | 0.1264 (404) |
| pooled | hybrid | nomic | fair | 1024 | fixed-256 | 0.0947 (172) | 0.1372 (124) | 0.0693 (33) | 0.1029 (329) |
| pooled | hybrid | nomic | fair | 1024 | fixed-512 | 0.0649 (118) | 0.1073 (97) | 0.0504 (24) | 0.0748 (239) |
| pooled | hybrid | nomic | fair | 1024 | section-aware | 0.0644 (117) | 0.0819 (74) | 0.0735 (35) | 0.0707 (226) |
| pooled | hybrid | nomic | fair | 1024 | small-to-big | 0.0303 (55) | 0.0321 (29) | 0.0357 (17) | 0.0316 (101) |
| pooled | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0154 (28) | 0.0254 (23) | 0.0210 (10) | 0.0191 (61) |
| pooled | hybrid | nomic | fair | 1024 | every chunking tied | 0.5223 (949) | 0.3695 (334) | 0.5924 (282) | 0.4895 (1565) |
| pooled | vector | bge-small | production | 1024 | fixed-64 | 0.6032 (1096) | 0.4369 (395) | 0.7059 (336) | 0.5715 (1827) |
| pooled | vector | bge-small | production | 1024 | fixed-128 | 0.1332 (242) | 0.1892 (171) | 0.0714 (34) | 0.1398 (447) |
| pooled | vector | bge-small | production | 1024 | fixed-256 | 0.0947 (172) | 0.1560 (141) | 0.0588 (28) | 0.1067 (341) |
| pooled | vector | bge-small | production | 1024 | fixed-512 | 0.0561 (102) | 0.0752 (68) | 0.0378 (18) | 0.0588 (188) |
| pooled | vector | bge-small | production | 1024 | section-aware | 0.0633 (115) | 0.0730 (66) | 0.0861 (41) | 0.0694 (222) |
| pooled | vector | bge-small | production | 1024 | small-to-big | 0.0396 (72) | 0.0476 (43) | 0.0231 (11) | 0.0394 (126) |
| pooled | vector | bge-small | production | 1024 | fixed-1024 | 0.0099 (18) | 0.0221 (20) | 0.0168 (8) | 0.0144 (46) |
| pooled | vector | bge-small | production | 1024 | every chunking tied | 0.5575 (1013) | 0.3883 (351) | 0.6618 (315) | 0.5252 (1679) |
| pooled | vector | bge-small | fair | 1024 | fixed-64 | 0.6307 (1146) | 0.4967 (449) | 0.7185 (342) | 0.6059 (1937) |
| pooled | vector | bge-small | fair | 1024 | fixed-128 | 0.1106 (201) | 0.1438 (130) | 0.0609 (29) | 0.1126 (360) |
| pooled | vector | bge-small | fair | 1024 | fixed-256 | 0.0875 (159) | 0.1449 (131) | 0.0567 (27) | 0.0992 (317) |
| pooled | vector | bge-small | fair | 1024 | fixed-512 | 0.0561 (102) | 0.0719 (65) | 0.0357 (17) | 0.0576 (184) |
| pooled | vector | bge-small | fair | 1024 | section-aware | 0.0649 (118) | 0.0730 (66) | 0.0882 (42) | 0.0707 (226) |
| pooled | vector | bge-small | fair | 1024 | small-to-big | 0.0402 (73) | 0.0476 (43) | 0.0231 (11) | 0.0397 (127) |
| pooled | vector | bge-small | fair | 1024 | fixed-1024 | 0.0099 (18) | 0.0221 (20) | 0.0168 (8) | 0.0144 (46) |
| pooled | vector | bge-small | fair | 1024 | every chunking tied | 0.5526 (1004) | 0.4060 (367) | 0.6387 (304) | 0.5239 (1675) |
| pooled | vector | nomic | production | 1024 | fixed-64 | 0.5894 (1071) | 0.4181 (378) | 0.6975 (332) | 0.5571 (1781) |
| pooled | vector | nomic | production | 1024 | fixed-128 | 0.1475 (268) | 0.1947 (176) | 0.0861 (41) | 0.1517 (485) |
| pooled | vector | nomic | production | 1024 | fixed-256 | 0.0870 (158) | 0.1449 (131) | 0.0672 (32) | 0.1004 (321) |
| pooled | vector | nomic | production | 1024 | fixed-512 | 0.0550 (100) | 0.0940 (85) | 0.0483 (23) | 0.0651 (208) |
| pooled | vector | nomic | production | 1024 | section-aware | 0.0726 (132) | 0.0863 (78) | 0.0672 (32) | 0.0757 (242) |
| pooled | vector | nomic | production | 1024 | small-to-big | 0.0380 (69) | 0.0376 (34) | 0.0273 (13) | 0.0363 (116) |
| pooled | vector | nomic | production | 1024 | fixed-1024 | 0.0105 (19) | 0.0243 (22) | 0.0063 (3) | 0.0138 (44) |
| pooled | vector | nomic | production | 1024 | every chunking tied | 0.5443 (989) | 0.3695 (334) | 0.6660 (317) | 0.5130 (1640) |
| pooled | vector | nomic | fair | 1024 | fixed-64 | 0.6280 (1141) | 0.4801 (434) | 0.7143 (340) | 0.5990 (1915) |
| pooled | vector | nomic | fair | 1024 | fixed-128 | 0.1167 (212) | 0.1449 (131) | 0.0735 (35) | 0.1182 (378) |
| pooled | vector | nomic | fair | 1024 | fixed-256 | 0.0826 (150) | 0.1361 (123) | 0.0672 (32) | 0.0954 (305) |
| pooled | vector | nomic | fair | 1024 | fixed-512 | 0.0539 (98) | 0.0918 (83) | 0.0483 (23) | 0.0638 (204) |
| pooled | vector | nomic | fair | 1024 | section-aware | 0.0704 (128) | 0.0852 (77) | 0.0630 (30) | 0.0735 (235) |
| pooled | vector | nomic | fair | 1024 | small-to-big | 0.0380 (69) | 0.0376 (34) | 0.0273 (13) | 0.0363 (116) |
| pooled | vector | nomic | fair | 1024 | fixed-1024 | 0.0105 (19) | 0.0243 (22) | 0.0063 (3) | 0.0138 (44) |
| pooled | vector | nomic | fair | 1024 | every chunking tied | 0.5388 (979) | 0.3883 (351) | 0.6471 (308) | 0.5124 (1638) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.2140 (107) | 0.1680 (84) | n/a | 0.1910 (191) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.2700 (135) | 0.3120 (156) | n/a | 0.2910 (291) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.2240 (112) | 0.2080 (104) | n/a | 0.2160 (216) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.1680 (84) | 0.1340 (67) | n/a | 0.1510 (151) |
| nq | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.0780 (39) | 0.1280 (64) | n/a | 0.1030 (103) |
| nq | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0240 (12) | 0.0280 (14) | n/a | 0.0260 (26) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | bge-small | production | 1024 | every chunking tied | 0.1660 (83) | 0.1300 (65) | n/a | 0.1480 (148) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.2980 (149) | 0.2600 (130) | n/a | 0.2790 (279) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.2140 (107) | 0.2480 (124) | n/a | 0.2310 (231) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.2100 (105) | 0.1900 (95) | n/a | 0.2000 (200) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.1580 (79) | 0.1260 (63) | n/a | 0.1420 (142) |
| nq | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.0740 (37) | 0.1260 (63) | n/a | 0.1000 (100) |
| nq | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0240 (12) | 0.0280 (14) | n/a | 0.0260 (26) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | bge-small | fair | 1024 | every chunking tied | 0.2000 (100) | 0.1740 (87) | n/a | 0.1870 (187) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.2240 (112) | 0.1860 (93) | n/a | 0.2050 (205) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.2720 (136) | 0.2980 (149) | n/a | 0.2850 (285) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.2140 (107) | 0.2060 (103) | n/a | 0.2100 (210) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.1620 (81) | 0.1300 (65) | n/a | 0.1460 (146) |
| nq | hybrid-rerank | nomic | production | 1024 | section-aware | 0.0800 (40) | 0.1300 (65) | n/a | 0.1050 (105) |
| nq | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0260 (13) | 0.0280 (14) | n/a | 0.0270 (27) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | nomic | production | 1024 | every chunking tied | 0.1700 (85) | 0.1440 (72) | n/a | 0.1570 (157) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.3040 (152) | 0.2740 (137) | n/a | 0.2890 (289) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2160 (108) | 0.2380 (119) | n/a | 0.2270 (227) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2020 (101) | 0.1860 (93) | n/a | 0.1940 (194) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1540 (77) | 0.1240 (62) | n/a | 0.1390 (139) |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0780 (39) | 0.1280 (64) | n/a | 0.1030 (103) |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0240 (12) | 0.0280 (14) | n/a | 0.0260 (26) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0220 (11) | 0.0220 (11) | n/a | 0.0220 (22) |
| nq | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.2100 (105) | 0.1800 (90) | n/a | 0.1950 (195) |
| nq | bm25 | - | production | 1024 | fixed-64 | 0.2980 (149) | 0.2800 (140) | n/a | 0.2890 (289) |
| nq | bm25 | - | production | 1024 | fixed-128 | 0.2520 (126) | 0.2340 (117) | n/a | 0.2430 (243) |
| nq | bm25 | - | production | 1024 | fixed-256 | 0.1820 (91) | 0.1880 (94) | n/a | 0.1850 (185) |
| nq | bm25 | - | production | 1024 | fixed-512 | 0.1420 (71) | 0.1300 (65) | n/a | 0.1360 (136) |
| nq | bm25 | - | production | 1024 | section-aware | 0.0580 (29) | 0.1000 (50) | n/a | 0.0790 (79) |
| nq | bm25 | - | production | 1024 | small-to-big | 0.0220 (11) | 0.0240 (12) | n/a | 0.0230 (23) |
| nq | bm25 | - | production | 1024 | fixed-1024 | 0.0460 (23) | 0.0440 (22) | n/a | 0.0450 (45) |
| nq | bm25 | - | production | 1024 | every chunking tied | 0.2600 (130) | 0.2340 (117) | n/a | 0.2470 (247) |
| nq | bm25 | - | fair | 1024 | fixed-64 | 0.3700 (185) | 0.3500 (175) | n/a | 0.3600 (360) |
| nq | bm25 | - | fair | 1024 | fixed-128 | 0.1920 (96) | 0.1720 (86) | n/a | 0.1820 (182) |
| nq | bm25 | - | fair | 1024 | fixed-256 | 0.1760 (88) | 0.1820 (91) | n/a | 0.1790 (179) |
| nq | bm25 | - | fair | 1024 | fixed-512 | 0.1380 (69) | 0.1280 (64) | n/a | 0.1330 (133) |
| nq | bm25 | - | fair | 1024 | section-aware | 0.0560 (28) | 0.1000 (50) | n/a | 0.0780 (78) |
| nq | bm25 | - | fair | 1024 | small-to-big | 0.0220 (11) | 0.0240 (12) | n/a | 0.0230 (23) |
| nq | bm25 | - | fair | 1024 | fixed-1024 | 0.0460 (23) | 0.0440 (22) | n/a | 0.0450 (45) |
| nq | bm25 | - | fair | 1024 | every chunking tied | 0.2740 (137) | 0.2560 (128) | n/a | 0.2650 (265) |
| nq | hybrid | bge-small | production | 1024 | fixed-64 | 0.2620 (131) | 0.1920 (96) | n/a | 0.2270 (227) |
| nq | hybrid | bge-small | production | 1024 | fixed-128 | 0.2880 (144) | 0.2900 (145) | n/a | 0.2890 (289) |
| nq | hybrid | bge-small | production | 1024 | fixed-256 | 0.1880 (94) | 0.2180 (109) | n/a | 0.2030 (203) |
| nq | hybrid | bge-small | production | 1024 | fixed-512 | 0.1300 (65) | 0.1340 (67) | n/a | 0.1320 (132) |
| nq | hybrid | bge-small | production | 1024 | section-aware | 0.0720 (36) | 0.0840 (42) | n/a | 0.0780 (78) |
| nq | hybrid | bge-small | production | 1024 | small-to-big | 0.0300 (15) | 0.0480 (24) | n/a | 0.0390 (39) |
| nq | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0300 (15) | 0.0340 (17) | n/a | 0.0320 (32) |
| nq | hybrid | bge-small | production | 1024 | every chunking tied | 0.2040 (102) | 0.1420 (71) | n/a | 0.1730 (173) |
| nq | hybrid | bge-small | fair | 1024 | fixed-64 | 0.3480 (174) | 0.2880 (144) | n/a | 0.3180 (318) |
| nq | hybrid | bge-small | fair | 1024 | fixed-128 | 0.2220 (111) | 0.2180 (109) | n/a | 0.2200 (220) |
| nq | hybrid | bge-small | fair | 1024 | fixed-256 | 0.1740 (87) | 0.2040 (102) | n/a | 0.1890 (189) |
| nq | hybrid | bge-small | fair | 1024 | fixed-512 | 0.1300 (65) | 0.1280 (64) | n/a | 0.1290 (129) |
| nq | hybrid | bge-small | fair | 1024 | section-aware | 0.0660 (33) | 0.0800 (40) | n/a | 0.0730 (73) |
| nq | hybrid | bge-small | fair | 1024 | small-to-big | 0.0300 (15) | 0.0480 (24) | n/a | 0.0390 (39) |
| nq | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0300 (15) | 0.0340 (17) | n/a | 0.0320 (32) |
| nq | hybrid | bge-small | fair | 1024 | every chunking tied | 0.2320 (116) | 0.1620 (81) | n/a | 0.1970 (197) |
| nq | hybrid | nomic | production | 1024 | fixed-64 | 0.2620 (131) | 0.1920 (96) | n/a | 0.2270 (227) |
| nq | hybrid | nomic | production | 1024 | fixed-128 | 0.2840 (142) | 0.2920 (146) | n/a | 0.2880 (288) |
| nq | hybrid | nomic | production | 1024 | fixed-256 | 0.2020 (101) | 0.1940 (97) | n/a | 0.1980 (198) |
| nq | hybrid | nomic | production | 1024 | fixed-512 | 0.1400 (70) | 0.1580 (79) | n/a | 0.1490 (149) |
| nq | hybrid | nomic | production | 1024 | section-aware | 0.0660 (33) | 0.0980 (49) | n/a | 0.0820 (82) |
| nq | hybrid | nomic | production | 1024 | small-to-big | 0.0200 (10) | 0.0360 (18) | n/a | 0.0280 (28) |
| nq | hybrid | nomic | production | 1024 | fixed-1024 | 0.0260 (13) | 0.0300 (15) | n/a | 0.0280 (28) |
| nq | hybrid | nomic | production | 1024 | every chunking tied | 0.2000 (100) | 0.1320 (66) | n/a | 0.1660 (166) |
| nq | hybrid | nomic | fair | 1024 | fixed-64 | 0.3600 (180) | 0.2800 (140) | n/a | 0.3200 (320) |
| nq | hybrid | nomic | fair | 1024 | fixed-128 | 0.2060 (103) | 0.2200 (110) | n/a | 0.2130 (213) |
| nq | hybrid | nomic | fair | 1024 | fixed-256 | 0.1900 (95) | 0.1880 (94) | n/a | 0.1890 (189) |
| nq | hybrid | nomic | fair | 1024 | fixed-512 | 0.1340 (67) | 0.1500 (75) | n/a | 0.1420 (142) |
| nq | hybrid | nomic | fair | 1024 | section-aware | 0.0640 (32) | 0.0960 (48) | n/a | 0.0800 (80) |
| nq | hybrid | nomic | fair | 1024 | small-to-big | 0.0200 (10) | 0.0360 (18) | n/a | 0.0280 (28) |
| nq | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0260 (13) | 0.0300 (15) | n/a | 0.0280 (28) |
| nq | hybrid | nomic | fair | 1024 | every chunking tied | 0.2220 (111) | 0.1700 (85) | n/a | 0.1960 (196) |
| nq | vector | bge-small | production | 1024 | fixed-64 | 0.2300 (115) | 0.1880 (94) | n/a | 0.2090 (209) |
| nq | vector | bge-small | production | 1024 | fixed-128 | 0.3060 (153) | 0.2980 (149) | n/a | 0.3020 (302) |
| nq | vector | bge-small | production | 1024 | fixed-256 | 0.2100 (105) | 0.2360 (118) | n/a | 0.2230 (223) |
| nq | vector | bge-small | production | 1024 | fixed-512 | 0.1260 (63) | 0.1040 (52) | n/a | 0.1150 (115) |
| nq | vector | bge-small | production | 1024 | section-aware | 0.0760 (38) | 0.0860 (43) | n/a | 0.0810 (81) |
| nq | vector | bge-small | production | 1024 | small-to-big | 0.0320 (16) | 0.0640 (32) | n/a | 0.0480 (48) |
| nq | vector | bge-small | production | 1024 | fixed-1024 | 0.0200 (10) | 0.0240 (12) | n/a | 0.0220 (22) |
| nq | vector | bge-small | production | 1024 | every chunking tied | 0.1700 (85) | 0.1300 (65) | n/a | 0.1500 (150) |
| nq | vector | bge-small | fair | 1024 | fixed-64 | 0.3120 (156) | 0.2900 (145) | n/a | 0.3010 (301) |
| nq | vector | bge-small | fair | 1024 | fixed-128 | 0.2380 (119) | 0.2200 (110) | n/a | 0.2290 (229) |
| nq | vector | bge-small | fair | 1024 | fixed-256 | 0.1980 (99) | 0.2160 (108) | n/a | 0.2070 (207) |
| nq | vector | bge-small | fair | 1024 | fixed-512 | 0.1260 (63) | 0.1020 (51) | n/a | 0.1140 (114) |
| nq | vector | bge-small | fair | 1024 | section-aware | 0.0740 (37) | 0.0840 (42) | n/a | 0.0790 (79) |
| nq | vector | bge-small | fair | 1024 | small-to-big | 0.0320 (16) | 0.0640 (32) | n/a | 0.0480 (48) |
| nq | vector | bge-small | fair | 1024 | fixed-1024 | 0.0200 (10) | 0.0240 (12) | n/a | 0.0220 (22) |
| nq | vector | bge-small | fair | 1024 | every chunking tied | 0.2060 (103) | 0.1760 (88) | n/a | 0.1910 (191) |
| nq | vector | nomic | production | 1024 | fixed-64 | 0.2320 (116) | 0.1940 (97) | n/a | 0.2130 (213) |
| nq | vector | nomic | production | 1024 | fixed-128 | 0.3060 (153) | 0.3100 (155) | n/a | 0.3080 (308) |
| nq | vector | nomic | production | 1024 | fixed-256 | 0.2240 (112) | 0.2000 (100) | n/a | 0.2120 (212) |
| nq | vector | nomic | production | 1024 | fixed-512 | 0.1140 (57) | 0.1180 (59) | n/a | 0.1160 (116) |
| nq | vector | nomic | production | 1024 | section-aware | 0.0800 (40) | 0.1060 (53) | n/a | 0.0930 (93) |
| nq | vector | nomic | production | 1024 | small-to-big | 0.0240 (12) | 0.0460 (23) | n/a | 0.0350 (35) |
| nq | vector | nomic | production | 1024 | fixed-1024 | 0.0200 (10) | 0.0260 (13) | n/a | 0.0230 (23) |
| nq | vector | nomic | production | 1024 | every chunking tied | 0.1760 (88) | 0.1320 (66) | n/a | 0.1540 (154) |
| nq | vector | nomic | fair | 1024 | fixed-64 | 0.3240 (162) | 0.3000 (150) | n/a | 0.3120 (312) |
| nq | vector | nomic | fair | 1024 | fixed-128 | 0.2340 (117) | 0.2220 (111) | n/a | 0.2280 (228) |
| nq | vector | nomic | fair | 1024 | fixed-256 | 0.2120 (106) | 0.1840 (92) | n/a | 0.1980 (198) |
| nq | vector | nomic | fair | 1024 | fixed-512 | 0.1100 (55) | 0.1180 (59) | n/a | 0.1140 (114) |
| nq | vector | nomic | fair | 1024 | section-aware | 0.0760 (38) | 0.1040 (52) | n/a | 0.0900 (90) |
| nq | vector | nomic | fair | 1024 | small-to-big | 0.0240 (12) | 0.0460 (23) | n/a | 0.0350 (35) |
| nq | vector | nomic | fair | 1024 | fixed-1024 | 0.0200 (10) | 0.0260 (13) | n/a | 0.0230 (23) |
| nq | vector | nomic | fair | 1024 | every chunking tied | 0.2060 (103) | 0.1840 (92) | n/a | 0.1950 (195) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.6135 (808) | 0.5842 (236) | 0.5819 (277) | 0.6013 (1321) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.0934 (123) | 0.0817 (33) | 0.0840 (40) | 0.0892 (196) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.0911 (120) | 0.0817 (33) | 0.1113 (53) | 0.0938 (206) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.0600 (79) | 0.0743 (30) | 0.0504 (24) | 0.0605 (133) |
| qasper | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.0964 (127) | 0.1163 (47) | 0.1092 (52) | 0.1029 (226) |
| qasper | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0235 (31) | 0.0322 (13) | 0.0252 (12) | 0.0255 (56) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0220 (29) | 0.0297 (12) | 0.0378 (18) | 0.0269 (59) |
| qasper | hybrid-rerank | bge-small | production | 1024 | every chunking tied | 0.5907 (778) | 0.5619 (227) | 0.5609 (267) | 0.5790 (1272) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.6287 (828) | 0.5941 (240) | 0.5987 (285) | 0.6158 (1353) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.0835 (110) | 0.0718 (29) | 0.0735 (35) | 0.0792 (174) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.0881 (116) | 0.0817 (33) | 0.1050 (50) | 0.0906 (199) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.0592 (78) | 0.0743 (30) | 0.0483 (23) | 0.0596 (131) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.0949 (125) | 0.1163 (47) | 0.1113 (53) | 0.1024 (225) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0235 (31) | 0.0322 (13) | 0.0252 (12) | 0.0255 (56) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0220 (29) | 0.0297 (12) | 0.0378 (18) | 0.0269 (59) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | every chunking tied | 0.5793 (763) | 0.5495 (222) | 0.5525 (263) | 0.5680 (1248) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.6112 (805) | 0.6064 (245) | 0.5630 (268) | 0.5999 (1318) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.0964 (127) | 0.0743 (30) | 0.0903 (43) | 0.0910 (200) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.0759 (100) | 0.0644 (26) | 0.1113 (53) | 0.0815 (179) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.0615 (81) | 0.0965 (39) | 0.0588 (28) | 0.0674 (148) |
| qasper | hybrid-rerank | nomic | production | 1024 | section-aware | 0.1010 (133) | 0.1114 (45) | 0.1113 (53) | 0.1051 (231) |
| qasper | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0334 (44) | 0.0248 (10) | 0.0273 (13) | 0.0305 (67) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0205 (27) | 0.0223 (9) | 0.0378 (18) | 0.0246 (54) |
| qasper | hybrid-rerank | nomic | production | 1024 | every chunking tied | 0.5892 (776) | 0.5817 (235) | 0.5399 (257) | 0.5772 (1268) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.6279 (827) | 0.6262 (253) | 0.5756 (274) | 0.6163 (1354) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.0843 (111) | 0.0619 (25) | 0.0840 (40) | 0.0801 (176) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.0737 (97) | 0.0644 (26) | 0.1050 (50) | 0.0787 (173) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.0615 (81) | 0.0941 (38) | 0.0567 (27) | 0.0665 (146) |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.1002 (132) | 0.1064 (43) | 0.1134 (54) | 0.1042 (229) |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0319 (42) | 0.0248 (10) | 0.0273 (13) | 0.0296 (65) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0205 (27) | 0.0223 (9) | 0.0378 (18) | 0.0246 (54) |
| qasper | hybrid-rerank | nomic | fair | 1024 | every chunking tied | 0.5740 (756) | 0.5718 (231) | 0.5252 (250) | 0.5630 (1237) |
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
| qasper | hybrid | bge-small | production | 1024 | fixed-64 | 0.6955 (916) | 0.6881 (278) | 0.6429 (306) | 0.6827 (1500) |
| qasper | hybrid | bge-small | production | 1024 | fixed-128 | 0.0904 (119) | 0.0866 (35) | 0.0756 (36) | 0.0865 (190) |
| qasper | hybrid | bge-small | production | 1024 | fixed-256 | 0.0554 (73) | 0.0718 (29) | 0.0903 (43) | 0.0660 (145) |
| qasper | hybrid | bge-small | production | 1024 | fixed-512 | 0.0410 (54) | 0.0223 (9) | 0.0483 (23) | 0.0391 (86) |
| qasper | hybrid | bge-small | production | 1024 | section-aware | 0.0774 (102) | 0.0792 (32) | 0.0756 (36) | 0.0774 (170) |
| qasper | hybrid | bge-small | production | 1024 | small-to-big | 0.0281 (37) | 0.0223 (9) | 0.0441 (21) | 0.0305 (67) |
| qasper | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0121 (16) | 0.0297 (12) | 0.0231 (11) | 0.0178 (39) |
| qasper | hybrid | bge-small | production | 1024 | every chunking tied | 0.6651 (876) | 0.6436 (260) | 0.6218 (296) | 0.6518 (1432) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-64 | 0.7115 (937) | 0.7030 (284) | 0.6723 (320) | 0.7014 (1541) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-128 | 0.0828 (109) | 0.0767 (31) | 0.0588 (28) | 0.0765 (168) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-256 | 0.0516 (68) | 0.0693 (28) | 0.0819 (39) | 0.0614 (135) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-512 | 0.0387 (51) | 0.0198 (8) | 0.0483 (23) | 0.0373 (82) |
| qasper | hybrid | bge-small | fair | 1024 | section-aware | 0.0767 (101) | 0.0792 (32) | 0.0714 (34) | 0.0760 (167) |
| qasper | hybrid | bge-small | fair | 1024 | small-to-big | 0.0273 (36) | 0.0223 (9) | 0.0441 (21) | 0.0300 (66) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0114 (15) | 0.0297 (12) | 0.0231 (11) | 0.0173 (38) |
| qasper | hybrid | bge-small | fair | 1024 | every chunking tied | 0.6446 (849) | 0.6238 (252) | 0.6113 (291) | 0.6336 (1392) |
| qasper | hybrid | nomic | production | 1024 | fixed-64 | 0.6894 (908) | 0.6658 (269) | 0.6408 (305) | 0.6746 (1482) |
| qasper | hybrid | nomic | production | 1024 | fixed-128 | 0.0972 (128) | 0.0817 (33) | 0.1071 (51) | 0.0965 (212) |
| qasper | hybrid | nomic | production | 1024 | fixed-256 | 0.0600 (79) | 0.0767 (31) | 0.0693 (33) | 0.0651 (143) |
| qasper | hybrid | nomic | production | 1024 | fixed-512 | 0.0395 (52) | 0.0569 (23) | 0.0504 (24) | 0.0451 (99) |
| qasper | hybrid | nomic | production | 1024 | section-aware | 0.0668 (88) | 0.0668 (27) | 0.0735 (35) | 0.0683 (150) |
| qasper | hybrid | nomic | production | 1024 | small-to-big | 0.0357 (47) | 0.0297 (12) | 0.0357 (17) | 0.0346 (76) |
| qasper | hybrid | nomic | production | 1024 | fixed-1024 | 0.0114 (15) | 0.0223 (9) | 0.0231 (11) | 0.0159 (35) |
| qasper | hybrid | nomic | production | 1024 | every chunking tied | 0.6576 (866) | 0.6287 (254) | 0.6050 (288) | 0.6409 (1408) |
| qasper | hybrid | nomic | fair | 1024 | fixed-64 | 0.7031 (926) | 0.6881 (278) | 0.6576 (313) | 0.6905 (1517) |
| qasper | hybrid | nomic | fair | 1024 | fixed-128 | 0.0896 (118) | 0.0718 (29) | 0.0924 (44) | 0.0869 (191) |
| qasper | hybrid | nomic | fair | 1024 | fixed-256 | 0.0585 (77) | 0.0743 (30) | 0.0693 (33) | 0.0637 (140) |
| qasper | hybrid | nomic | fair | 1024 | fixed-512 | 0.0387 (51) | 0.0545 (22) | 0.0504 (24) | 0.0442 (97) |
| qasper | hybrid | nomic | fair | 1024 | section-aware | 0.0645 (85) | 0.0644 (26) | 0.0735 (35) | 0.0665 (146) |
| qasper | hybrid | nomic | fair | 1024 | small-to-big | 0.0342 (45) | 0.0272 (11) | 0.0357 (17) | 0.0332 (73) |
| qasper | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0114 (15) | 0.0198 (8) | 0.0210 (10) | 0.0150 (33) |
| qasper | hybrid | nomic | fair | 1024 | every chunking tied | 0.6363 (838) | 0.6163 (249) | 0.5924 (282) | 0.6231 (1369) |
| qasper | vector | bge-small | production | 1024 | fixed-64 | 0.7449 (981) | 0.7450 (301) | 0.7059 (336) | 0.7365 (1618) |
| qasper | vector | bge-small | production | 1024 | fixed-128 | 0.0676 (89) | 0.0545 (22) | 0.0714 (34) | 0.0660 (145) |
| qasper | vector | bge-small | production | 1024 | fixed-256 | 0.0509 (67) | 0.0569 (23) | 0.0588 (28) | 0.0537 (118) |
| qasper | vector | bge-small | production | 1024 | fixed-512 | 0.0296 (39) | 0.0396 (16) | 0.0378 (18) | 0.0332 (73) |
| qasper | vector | bge-small | production | 1024 | section-aware | 0.0585 (77) | 0.0569 (23) | 0.0861 (41) | 0.0642 (141) |
| qasper | vector | bge-small | production | 1024 | small-to-big | 0.0425 (56) | 0.0272 (11) | 0.0231 (11) | 0.0355 (78) |
| qasper | vector | bge-small | production | 1024 | fixed-1024 | 0.0061 (8) | 0.0198 (8) | 0.0168 (8) | 0.0109 (24) |
| qasper | vector | bge-small | production | 1024 | every chunking tied | 0.7046 (928) | 0.7079 (286) | 0.6618 (315) | 0.6959 (1529) |
| qasper | vector | bge-small | fair | 1024 | fixed-64 | 0.7517 (990) | 0.7525 (304) | 0.7185 (342) | 0.7447 (1636) |
| qasper | vector | bge-small | fair | 1024 | fixed-128 | 0.0623 (82) | 0.0495 (20) | 0.0609 (29) | 0.0596 (131) |
| qasper | vector | bge-small | fair | 1024 | fixed-256 | 0.0456 (60) | 0.0569 (23) | 0.0567 (27) | 0.0501 (110) |
| qasper | vector | bge-small | fair | 1024 | fixed-512 | 0.0296 (39) | 0.0347 (14) | 0.0357 (17) | 0.0319 (70) |
| qasper | vector | bge-small | fair | 1024 | section-aware | 0.0615 (81) | 0.0594 (24) | 0.0882 (42) | 0.0669 (147) |
| qasper | vector | bge-small | fair | 1024 | small-to-big | 0.0433 (57) | 0.0272 (11) | 0.0231 (11) | 0.0360 (79) |
| qasper | vector | bge-small | fair | 1024 | fixed-1024 | 0.0061 (8) | 0.0198 (8) | 0.0168 (8) | 0.0109 (24) |
| qasper | vector | bge-small | fair | 1024 | every chunking tied | 0.6841 (901) | 0.6906 (279) | 0.6387 (304) | 0.6755 (1484) |
| qasper | vector | nomic | production | 1024 | fixed-64 | 0.7251 (955) | 0.6955 (281) | 0.6975 (332) | 0.7137 (1568) |
| qasper | vector | nomic | production | 1024 | fixed-128 | 0.0873 (115) | 0.0520 (21) | 0.0861 (41) | 0.0806 (177) |
| qasper | vector | nomic | production | 1024 | fixed-256 | 0.0349 (46) | 0.0767 (31) | 0.0672 (32) | 0.0496 (109) |
| qasper | vector | nomic | production | 1024 | fixed-512 | 0.0326 (43) | 0.0644 (26) | 0.0483 (23) | 0.0419 (92) |
| qasper | vector | nomic | production | 1024 | section-aware | 0.0699 (92) | 0.0619 (25) | 0.0672 (32) | 0.0678 (149) |
| qasper | vector | nomic | production | 1024 | small-to-big | 0.0433 (57) | 0.0272 (11) | 0.0273 (13) | 0.0369 (81) |
| qasper | vector | nomic | production | 1024 | fixed-1024 | 0.0068 (9) | 0.0223 (9) | 0.0063 (3) | 0.0096 (21) |
| qasper | vector | nomic | production | 1024 | every chunking tied | 0.6841 (901) | 0.6634 (268) | 0.6660 (317) | 0.6764 (1486) |
| qasper | vector | nomic | fair | 1024 | fixed-64 | 0.7434 (979) | 0.7030 (284) | 0.7143 (340) | 0.7296 (1603) |
| qasper | vector | nomic | fair | 1024 | fixed-128 | 0.0721 (95) | 0.0495 (20) | 0.0735 (35) | 0.0683 (150) |
| qasper | vector | nomic | fair | 1024 | fixed-256 | 0.0334 (44) | 0.0767 (31) | 0.0672 (32) | 0.0487 (107) |
| qasper | vector | nomic | fair | 1024 | fixed-512 | 0.0326 (43) | 0.0594 (24) | 0.0483 (23) | 0.0410 (90) |
| qasper | vector | nomic | fair | 1024 | section-aware | 0.0683 (90) | 0.0619 (25) | 0.0630 (30) | 0.0660 (145) |
| qasper | vector | nomic | fair | 1024 | small-to-big | 0.0433 (57) | 0.0272 (11) | 0.0273 (13) | 0.0369 (81) |
| qasper | vector | nomic | fair | 1024 | fixed-1024 | 0.0068 (9) | 0.0223 (9) | 0.0063 (3) | 0.0096 (21) |
| qasper | vector | nomic | fair | 1024 | every chunking tied | 0.6651 (876) | 0.6411 (259) | 0.6471 (308) | 0.6568 (1443) |

## The same, among the questions where the chunkings differ

Leaves out the questions on which every chunking scores the same, so the tie-break does not decide the picks.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.0565 (54) | 0.0458 (28) | 0.0478 (10) | 0.0518 (92) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.2699 (258) | 0.3088 (189) | 0.1914 (40) | 0.2741 (487) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.2427 (232) | 0.2239 (137) | 0.2536 (53) | 0.2375 (422) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.1705 (163) | 0.1585 (97) | 0.1148 (24) | 0.1598 (284) |
| pooled | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.1736 (166) | 0.1814 (111) | 0.2488 (52) | 0.1851 (329) |
| pooled | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0450 (43) | 0.0441 (27) | 0.0574 (12) | 0.0461 (82) |
| pooled | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0418 (40) | 0.0376 (23) | 0.0861 (18) | 0.0456 (81) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.1195 (114) | 0.1025 (61) | 0.1033 (22) | 0.1118 (197) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.2275 (217) | 0.2571 (153) | 0.1643 (35) | 0.2299 (405) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.2317 (221) | 0.2151 (128) | 0.2347 (50) | 0.2264 (399) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.1646 (157) | 0.1563 (93) | 0.1080 (23) | 0.1549 (273) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.1698 (162) | 0.1849 (110) | 0.2488 (53) | 0.1844 (325) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0451 (43) | 0.0454 (27) | 0.0563 (12) | 0.0465 (82) |
| pooled | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0419 (40) | 0.0387 (23) | 0.0845 (18) | 0.0460 (81) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.0586 (56) | 0.0519 (31) | 0.0502 (11) | 0.0553 (98) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.2751 (263) | 0.2998 (179) | 0.1963 (43) | 0.2737 (485) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.2165 (207) | 0.2161 (129) | 0.2420 (53) | 0.2195 (389) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.1695 (162) | 0.1742 (104) | 0.1279 (28) | 0.1659 (294) |
| pooled | hybrid-rerank | nomic | production | 1024 | section-aware | 0.1810 (173) | 0.1843 (110) | 0.2420 (53) | 0.1896 (336) |
| pooled | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0596 (57) | 0.0402 (24) | 0.0594 (13) | 0.0530 (94) |
| pooled | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0397 (38) | 0.0335 (20) | 0.0822 (18) | 0.0429 (76) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1234 (118) | 0.1184 (69) | 0.1062 (24) | 0.1195 (211) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2291 (219) | 0.2470 (144) | 0.1770 (40) | 0.2283 (403) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2071 (198) | 0.2041 (119) | 0.2212 (50) | 0.2079 (367) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1653 (158) | 0.1715 (100) | 0.1195 (27) | 0.1615 (285) |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.1789 (171) | 0.1835 (107) | 0.2389 (54) | 0.1881 (332) |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0565 (54) | 0.0412 (24) | 0.0575 (13) | 0.0516 (91) |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0397 (38) | 0.0343 (20) | 0.0796 (18) | 0.0431 (76) |
| pooled | bm25 | - | production | 1024 | fixed-64 | 0.0537 (42) | 0.0725 (38) | 0.0941 (16) | 0.0650 (96) |
| pooled | bm25 | - | production | 1024 | fixed-128 | 0.3043 (238) | 0.2748 (144) | 0.2588 (44) | 0.2886 (426) |
| pooled | bm25 | - | production | 1024 | fixed-256 | 0.2123 (166) | 0.2309 (121) | 0.1824 (31) | 0.2154 (318) |
| pooled | bm25 | - | production | 1024 | fixed-512 | 0.1726 (135) | 0.1641 (86) | 0.1647 (28) | 0.1687 (249) |
| pooled | bm25 | - | production | 1024 | section-aware | 0.1292 (101) | 0.1412 (74) | 0.1529 (26) | 0.1362 (201) |
| pooled | bm25 | - | production | 1024 | small-to-big | 0.0575 (45) | 0.0420 (22) | 0.0706 (12) | 0.0535 (79) |
| pooled | bm25 | - | production | 1024 | fixed-1024 | 0.0703 (55) | 0.0744 (39) | 0.0765 (13) | 0.0725 (107) |
| pooled | bm25 | - | fair | 1024 | fixed-64 | 0.1455 (117) | 0.1401 (73) | 0.1944 (35) | 0.1495 (225) |
| pooled | bm25 | - | fair | 1024 | fixed-128 | 0.2463 (198) | 0.2150 (112) | 0.2167 (39) | 0.2319 (349) |
| pooled | bm25 | - | fair | 1024 | fixed-256 | 0.1965 (158) | 0.2226 (116) | 0.1611 (29) | 0.2013 (303) |
| pooled | bm25 | - | fair | 1024 | fixed-512 | 0.1642 (132) | 0.1631 (85) | 0.1556 (28) | 0.1628 (245) |
| pooled | bm25 | - | fair | 1024 | section-aware | 0.1244 (100) | 0.1420 (74) | 0.1444 (26) | 0.1329 (200) |
| pooled | bm25 | - | fair | 1024 | small-to-big | 0.0560 (45) | 0.0422 (22) | 0.0611 (11) | 0.0518 (78) |
| pooled | bm25 | - | fair | 1024 | fixed-1024 | 0.0672 (54) | 0.0749 (39) | 0.0667 (12) | 0.0698 (105) |
| pooled | hybrid | bge-small | production | 1024 | fixed-64 | 0.0822 (69) | 0.0750 (43) | 0.0556 (10) | 0.0766 (122) |
| pooled | hybrid | bge-small | production | 1024 | fixed-128 | 0.3135 (263) | 0.3141 (180) | 0.2000 (36) | 0.3009 (479) |
| pooled | hybrid | bge-small | production | 1024 | fixed-256 | 0.1990 (167) | 0.2408 (138) | 0.2389 (43) | 0.2186 (348) |
| pooled | hybrid | bge-small | production | 1024 | fixed-512 | 0.1418 (119) | 0.1326 (76) | 0.1278 (23) | 0.1369 (218) |
| pooled | hybrid | bge-small | production | 1024 | section-aware | 0.1645 (138) | 0.1291 (74) | 0.2000 (36) | 0.1558 (248) |
| pooled | hybrid | bge-small | production | 1024 | small-to-big | 0.0620 (52) | 0.0576 (33) | 0.1167 (21) | 0.0666 (106) |
| pooled | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0369 (31) | 0.0506 (29) | 0.0611 (11) | 0.0446 (71) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-64 | 0.1714 (146) | 0.1664 (95) | 0.1568 (29) | 0.1679 (270) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-128 | 0.2582 (220) | 0.2452 (140) | 0.1514 (28) | 0.2413 (388) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-256 | 0.1819 (155) | 0.2277 (130) | 0.2108 (39) | 0.2015 (324) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-512 | 0.1362 (116) | 0.1261 (72) | 0.1243 (23) | 0.1312 (211) |
| pooled | hybrid | bge-small | fair | 1024 | section-aware | 0.1573 (134) | 0.1261 (72) | 0.1838 (34) | 0.1493 (240) |
| pooled | hybrid | bge-small | fair | 1024 | small-to-big | 0.0599 (51) | 0.0578 (33) | 0.1135 (21) | 0.0653 (105) |
| pooled | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0352 (30) | 0.0508 (29) | 0.0595 (11) | 0.0435 (70) |
| pooled | hybrid | nomic | production | 1024 | fixed-64 | 0.0858 (73) | 0.0771 (45) | 0.0904 (17) | 0.0832 (135) |
| pooled | hybrid | nomic | production | 1024 | fixed-128 | 0.3173 (270) | 0.3065 (179) | 0.2713 (51) | 0.3081 (500) |
| pooled | hybrid | nomic | production | 1024 | fixed-256 | 0.2115 (180) | 0.2192 (128) | 0.1755 (33) | 0.2101 (341) |
| pooled | hybrid | nomic | production | 1024 | fixed-512 | 0.1434 (122) | 0.1747 (102) | 0.1277 (24) | 0.1528 (248) |
| pooled | hybrid | nomic | production | 1024 | section-aware | 0.1422 (121) | 0.1301 (76) | 0.1862 (35) | 0.1429 (232) |
| pooled | hybrid | nomic | production | 1024 | small-to-big | 0.0670 (57) | 0.0514 (30) | 0.0904 (17) | 0.0641 (104) |
| pooled | hybrid | nomic | production | 1024 | fixed-1024 | 0.0329 (28) | 0.0411 (24) | 0.0585 (11) | 0.0388 (63) |
| pooled | hybrid | nomic | fair | 1024 | fixed-64 | 0.1809 (157) | 0.1474 (84) | 0.1598 (31) | 0.1667 (272) |
| pooled | hybrid | nomic | fair | 1024 | fixed-128 | 0.2546 (221) | 0.2439 (139) | 0.2268 (44) | 0.2475 (404) |
| pooled | hybrid | nomic | fair | 1024 | fixed-256 | 0.1982 (172) | 0.2175 (124) | 0.1701 (33) | 0.2016 (329) |
| pooled | hybrid | nomic | fair | 1024 | fixed-512 | 0.1359 (118) | 0.1702 (97) | 0.1237 (24) | 0.1464 (239) |
| pooled | hybrid | nomic | fair | 1024 | section-aware | 0.1348 (117) | 0.1298 (74) | 0.1804 (35) | 0.1385 (226) |
| pooled | hybrid | nomic | fair | 1024 | small-to-big | 0.0634 (55) | 0.0509 (29) | 0.0876 (17) | 0.0619 (101) |
| pooled | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0323 (28) | 0.0404 (23) | 0.0515 (10) | 0.0374 (61) |
| pooled | vector | bge-small | production | 1024 | fixed-64 | 0.1032 (83) | 0.0796 (44) | 0.1304 (21) | 0.0975 (148) |
| pooled | vector | bge-small | production | 1024 | fixed-128 | 0.3010 (242) | 0.3092 (171) | 0.2112 (34) | 0.2945 (447) |
| pooled | vector | bge-small | production | 1024 | fixed-256 | 0.2139 (172) | 0.2550 (141) | 0.1739 (28) | 0.2246 (341) |
| pooled | vector | bge-small | production | 1024 | fixed-512 | 0.1269 (102) | 0.1230 (68) | 0.1118 (18) | 0.1238 (188) |
| pooled | vector | bge-small | production | 1024 | section-aware | 0.1430 (115) | 0.1193 (66) | 0.2547 (41) | 0.1462 (222) |
| pooled | vector | bge-small | production | 1024 | small-to-big | 0.0896 (72) | 0.0778 (43) | 0.0683 (11) | 0.0830 (126) |
| pooled | vector | bge-small | production | 1024 | fixed-1024 | 0.0224 (18) | 0.0362 (20) | 0.0497 (8) | 0.0303 (46) |
| pooled | vector | bge-small | fair | 1024 | fixed-64 | 0.1747 (142) | 0.1527 (82) | 0.2209 (38) | 0.1721 (262) |
| pooled | vector | bge-small | fair | 1024 | fixed-128 | 0.2472 (201) | 0.2421 (130) | 0.1686 (29) | 0.2365 (360) |
| pooled | vector | bge-small | fair | 1024 | fixed-256 | 0.1956 (159) | 0.2439 (131) | 0.1570 (27) | 0.2083 (317) |
| pooled | vector | bge-small | fair | 1024 | fixed-512 | 0.1255 (102) | 0.1210 (65) | 0.0988 (17) | 0.1209 (184) |
| pooled | vector | bge-small | fair | 1024 | section-aware | 0.1451 (118) | 0.1229 (66) | 0.2442 (42) | 0.1485 (226) |
| pooled | vector | bge-small | fair | 1024 | small-to-big | 0.0898 (73) | 0.0801 (43) | 0.0640 (11) | 0.0834 (127) |
| pooled | vector | bge-small | fair | 1024 | fixed-1024 | 0.0221 (18) | 0.0372 (20) | 0.0465 (8) | 0.0302 (46) |
| pooled | vector | nomic | production | 1024 | fixed-64 | 0.0990 (82) | 0.0772 (44) | 0.0943 (15) | 0.0906 (141) |
| pooled | vector | nomic | production | 1024 | fixed-128 | 0.3237 (268) | 0.3088 (176) | 0.2579 (41) | 0.3115 (485) |
| pooled | vector | nomic | production | 1024 | fixed-256 | 0.1908 (158) | 0.2298 (131) | 0.2013 (32) | 0.2062 (321) |
| pooled | vector | nomic | production | 1024 | fixed-512 | 0.1208 (100) | 0.1491 (85) | 0.1447 (23) | 0.1336 (208) |
| pooled | vector | nomic | production | 1024 | section-aware | 0.1594 (132) | 0.1368 (78) | 0.2013 (32) | 0.1554 (242) |
| pooled | vector | nomic | production | 1024 | small-to-big | 0.0833 (69) | 0.0596 (34) | 0.0818 (13) | 0.0745 (116) |
| pooled | vector | nomic | production | 1024 | fixed-1024 | 0.0229 (19) | 0.0386 (22) | 0.0189 (3) | 0.0283 (44) |
| pooled | vector | nomic | fair | 1024 | fixed-64 | 0.1933 (162) | 0.1501 (83) | 0.1905 (32) | 0.1777 (277) |
| pooled | vector | nomic | fair | 1024 | fixed-128 | 0.2530 (212) | 0.2369 (131) | 0.2083 (35) | 0.2425 (378) |
| pooled | vector | nomic | fair | 1024 | fixed-256 | 0.1790 (150) | 0.2224 (123) | 0.1905 (32) | 0.1956 (305) |
| pooled | vector | nomic | fair | 1024 | fixed-512 | 0.1169 (98) | 0.1501 (83) | 0.1369 (23) | 0.1309 (204) |
| pooled | vector | nomic | fair | 1024 | section-aware | 0.1527 (128) | 0.1392 (77) | 0.1786 (30) | 0.1507 (235) |
| pooled | vector | nomic | fair | 1024 | small-to-big | 0.0823 (69) | 0.0615 (34) | 0.0774 (13) | 0.0744 (116) |
| pooled | vector | nomic | fair | 1024 | fixed-1024 | 0.0227 (19) | 0.0398 (22) | 0.0179 (3) | 0.0282 (44) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.0576 (24) | 0.0437 (19) | n/a | 0.0505 (43) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.3237 (135) | 0.3586 (156) | n/a | 0.3415 (291) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.2686 (112) | 0.2391 (104) | n/a | 0.2535 (216) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.2014 (84) | 0.1540 (67) | n/a | 0.1772 (151) |
| nq | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.0935 (39) | 0.1471 (64) | n/a | 0.1209 (103) |
| nq | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0288 (12) | 0.0322 (14) | n/a | 0.0305 (26) |
| nq | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0264 (11) | 0.0253 (11) | n/a | 0.0258 (22) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.1225 (49) | 0.1041 (43) | n/a | 0.1132 (92) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.2675 (107) | 0.3002 (124) | n/a | 0.2841 (231) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.2625 (105) | 0.2300 (95) | n/a | 0.2460 (200) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.1975 (79) | 0.1525 (63) | n/a | 0.1747 (142) |
| nq | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.0925 (37) | 0.1525 (63) | n/a | 0.1230 (100) |
| nq | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0300 (12) | 0.0339 (14) | n/a | 0.0320 (26) |
| nq | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0275 (11) | 0.0266 (11) | n/a | 0.0271 (22) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.0651 (27) | 0.0491 (21) | n/a | 0.0569 (48) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.3277 (136) | 0.3481 (149) | n/a | 0.3381 (285) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.2578 (107) | 0.2407 (103) | n/a | 0.2491 (210) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.1952 (81) | 0.1519 (65) | n/a | 0.1732 (146) |
| nq | hybrid-rerank | nomic | production | 1024 | section-aware | 0.0964 (40) | 0.1519 (65) | n/a | 0.1246 (105) |
| nq | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0313 (13) | 0.0327 (14) | n/a | 0.0320 (27) |
| nq | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0265 (11) | 0.0257 (11) | n/a | 0.0261 (22) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1190 (47) | 0.1146 (47) | n/a | 0.1168 (94) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.2734 (108) | 0.2902 (119) | n/a | 0.2820 (227) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.2557 (101) | 0.2268 (93) | n/a | 0.2410 (194) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1949 (77) | 0.1512 (62) | n/a | 0.1727 (139) |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.0987 (39) | 0.1561 (64) | n/a | 0.1280 (103) |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0304 (12) | 0.0341 (14) | n/a | 0.0323 (26) |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0278 (11) | 0.0268 (11) | n/a | 0.0273 (22) |
| nq | bm25 | - | production | 1024 | fixed-64 | 0.0514 (19) | 0.0601 (23) | n/a | 0.0558 (42) |
| nq | bm25 | - | production | 1024 | fixed-128 | 0.3405 (126) | 0.3055 (117) | n/a | 0.3227 (243) |
| nq | bm25 | - | production | 1024 | fixed-256 | 0.2459 (91) | 0.2454 (94) | n/a | 0.2457 (185) |
| nq | bm25 | - | production | 1024 | fixed-512 | 0.1919 (71) | 0.1697 (65) | n/a | 0.1806 (136) |
| nq | bm25 | - | production | 1024 | section-aware | 0.0784 (29) | 0.1305 (50) | n/a | 0.1049 (79) |
| nq | bm25 | - | production | 1024 | small-to-big | 0.0297 (11) | 0.0313 (12) | n/a | 0.0305 (23) |
| nq | bm25 | - | production | 1024 | fixed-1024 | 0.0622 (23) | 0.0574 (22) | n/a | 0.0598 (45) |
| nq | bm25 | - | fair | 1024 | fixed-64 | 0.1322 (48) | 0.1263 (47) | n/a | 0.1293 (95) |
| nq | bm25 | - | fair | 1024 | fixed-128 | 0.2645 (96) | 0.2312 (86) | n/a | 0.2476 (182) |
| nq | bm25 | - | fair | 1024 | fixed-256 | 0.2424 (88) | 0.2446 (91) | n/a | 0.2435 (179) |
| nq | bm25 | - | fair | 1024 | fixed-512 | 0.1901 (69) | 0.1720 (64) | n/a | 0.1810 (133) |
| nq | bm25 | - | fair | 1024 | section-aware | 0.0771 (28) | 0.1344 (50) | n/a | 0.1061 (78) |
| nq | bm25 | - | fair | 1024 | small-to-big | 0.0303 (11) | 0.0323 (12) | n/a | 0.0313 (23) |
| nq | bm25 | - | fair | 1024 | fixed-1024 | 0.0634 (23) | 0.0591 (22) | n/a | 0.0612 (45) |
| nq | hybrid | bge-small | production | 1024 | fixed-64 | 0.0729 (29) | 0.0583 (25) | n/a | 0.0653 (54) |
| nq | hybrid | bge-small | production | 1024 | fixed-128 | 0.3618 (144) | 0.3380 (145) | n/a | 0.3495 (289) |
| nq | hybrid | bge-small | production | 1024 | fixed-256 | 0.2362 (94) | 0.2541 (109) | n/a | 0.2455 (203) |
| nq | hybrid | bge-small | production | 1024 | fixed-512 | 0.1633 (65) | 0.1562 (67) | n/a | 0.1596 (132) |
| nq | hybrid | bge-small | production | 1024 | section-aware | 0.0905 (36) | 0.0979 (42) | n/a | 0.0943 (78) |
| nq | hybrid | bge-small | production | 1024 | small-to-big | 0.0377 (15) | 0.0559 (24) | n/a | 0.0472 (39) |
| nq | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0377 (15) | 0.0396 (17) | n/a | 0.0387 (32) |
| nq | hybrid | bge-small | fair | 1024 | fixed-64 | 0.1510 (58) | 0.1504 (63) | n/a | 0.1507 (121) |
| nq | hybrid | bge-small | fair | 1024 | fixed-128 | 0.2891 (111) | 0.2601 (109) | n/a | 0.2740 (220) |
| nq | hybrid | bge-small | fair | 1024 | fixed-256 | 0.2266 (87) | 0.2434 (102) | n/a | 0.2354 (189) |
| nq | hybrid | bge-small | fair | 1024 | fixed-512 | 0.1693 (65) | 0.1527 (64) | n/a | 0.1606 (129) |
| nq | hybrid | bge-small | fair | 1024 | section-aware | 0.0859 (33) | 0.0955 (40) | n/a | 0.0909 (73) |
| nq | hybrid | bge-small | fair | 1024 | small-to-big | 0.0391 (15) | 0.0573 (24) | n/a | 0.0486 (39) |
| nq | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0391 (15) | 0.0406 (17) | n/a | 0.0399 (32) |
| nq | hybrid | nomic | production | 1024 | fixed-64 | 0.0775 (31) | 0.0691 (30) | n/a | 0.0731 (61) |
| nq | hybrid | nomic | production | 1024 | fixed-128 | 0.3550 (142) | 0.3364 (146) | n/a | 0.3453 (288) |
| nq | hybrid | nomic | production | 1024 | fixed-256 | 0.2525 (101) | 0.2235 (97) | n/a | 0.2374 (198) |
| nq | hybrid | nomic | production | 1024 | fixed-512 | 0.1750 (70) | 0.1820 (79) | n/a | 0.1787 (149) |
| nq | hybrid | nomic | production | 1024 | section-aware | 0.0825 (33) | 0.1129 (49) | n/a | 0.0983 (82) |
| nq | hybrid | nomic | production | 1024 | small-to-big | 0.0250 (10) | 0.0415 (18) | n/a | 0.0336 (28) |
| nq | hybrid | nomic | production | 1024 | fixed-1024 | 0.0325 (13) | 0.0346 (15) | n/a | 0.0336 (28) |
| nq | hybrid | nomic | fair | 1024 | fixed-64 | 0.1774 (69) | 0.1325 (55) | n/a | 0.1542 (124) |
| nq | hybrid | nomic | fair | 1024 | fixed-128 | 0.2648 (103) | 0.2651 (110) | n/a | 0.2649 (213) |
| nq | hybrid | nomic | fair | 1024 | fixed-256 | 0.2442 (95) | 0.2265 (94) | n/a | 0.2351 (189) |
| nq | hybrid | nomic | fair | 1024 | fixed-512 | 0.1722 (67) | 0.1807 (75) | n/a | 0.1766 (142) |
| nq | hybrid | nomic | fair | 1024 | section-aware | 0.0823 (32) | 0.1157 (48) | n/a | 0.0995 (80) |
| nq | hybrid | nomic | fair | 1024 | small-to-big | 0.0257 (10) | 0.0434 (18) | n/a | 0.0348 (28) |
| nq | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0334 (13) | 0.0361 (15) | n/a | 0.0348 (28) |
| nq | vector | bge-small | production | 1024 | fixed-64 | 0.0723 (30) | 0.0667 (29) | n/a | 0.0694 (59) |
| nq | vector | bge-small | production | 1024 | fixed-128 | 0.3687 (153) | 0.3425 (149) | n/a | 0.3553 (302) |
| nq | vector | bge-small | production | 1024 | fixed-256 | 0.2530 (105) | 0.2713 (118) | n/a | 0.2624 (223) |
| nq | vector | bge-small | production | 1024 | fixed-512 | 0.1518 (63) | 0.1195 (52) | n/a | 0.1353 (115) |
| nq | vector | bge-small | production | 1024 | section-aware | 0.0916 (38) | 0.0989 (43) | n/a | 0.0953 (81) |
| nq | vector | bge-small | production | 1024 | small-to-big | 0.0386 (16) | 0.0736 (32) | n/a | 0.0565 (48) |
| nq | vector | bge-small | production | 1024 | fixed-1024 | 0.0241 (10) | 0.0276 (12) | n/a | 0.0259 (22) |
| nq | vector | bge-small | fair | 1024 | fixed-64 | 0.1335 (53) | 0.1383 (57) | n/a | 0.1360 (110) |
| nq | vector | bge-small | fair | 1024 | fixed-128 | 0.2997 (119) | 0.2670 (110) | n/a | 0.2831 (229) |
| nq | vector | bge-small | fair | 1024 | fixed-256 | 0.2494 (99) | 0.2621 (108) | n/a | 0.2559 (207) |
| nq | vector | bge-small | fair | 1024 | fixed-512 | 0.1587 (63) | 0.1238 (51) | n/a | 0.1409 (114) |
| nq | vector | bge-small | fair | 1024 | section-aware | 0.0932 (37) | 0.1019 (42) | n/a | 0.0977 (79) |
| nq | vector | bge-small | fair | 1024 | small-to-big | 0.0403 (16) | 0.0777 (32) | n/a | 0.0593 (48) |
| nq | vector | bge-small | fair | 1024 | fixed-1024 | 0.0252 (10) | 0.0291 (12) | n/a | 0.0272 (22) |
| nq | vector | nomic | production | 1024 | fixed-64 | 0.0680 (28) | 0.0714 (31) | n/a | 0.0697 (59) |
| nq | vector | nomic | production | 1024 | fixed-128 | 0.3714 (153) | 0.3571 (155) | n/a | 0.3641 (308) |
| nq | vector | nomic | production | 1024 | fixed-256 | 0.2718 (112) | 0.2304 (100) | n/a | 0.2506 (212) |
| nq | vector | nomic | production | 1024 | fixed-512 | 0.1383 (57) | 0.1359 (59) | n/a | 0.1371 (116) |
| nq | vector | nomic | production | 1024 | section-aware | 0.0971 (40) | 0.1221 (53) | n/a | 0.1099 (93) |
| nq | vector | nomic | production | 1024 | small-to-big | 0.0291 (12) | 0.0530 (23) | n/a | 0.0414 (35) |
| nq | vector | nomic | production | 1024 | fixed-1024 | 0.0243 (10) | 0.0300 (13) | n/a | 0.0272 (23) |
| nq | vector | nomic | fair | 1024 | fixed-64 | 0.1486 (59) | 0.1422 (58) | n/a | 0.1453 (117) |
| nq | vector | nomic | fair | 1024 | fixed-128 | 0.2947 (117) | 0.2721 (111) | n/a | 0.2832 (228) |
| nq | vector | nomic | fair | 1024 | fixed-256 | 0.2670 (106) | 0.2255 (92) | n/a | 0.2460 (198) |
| nq | vector | nomic | fair | 1024 | fixed-512 | 0.1385 (55) | 0.1446 (59) | n/a | 0.1416 (114) |
| nq | vector | nomic | fair | 1024 | section-aware | 0.0957 (38) | 0.1275 (52) | n/a | 0.1118 (90) |
| nq | vector | nomic | fair | 1024 | small-to-big | 0.0302 (12) | 0.0564 (23) | n/a | 0.0435 (35) |
| nq | vector | nomic | fair | 1024 | fixed-1024 | 0.0252 (10) | 0.0319 (13) | n/a | 0.0286 (23) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-64 | 0.0557 (30) | 0.0508 (9) | 0.0478 (10) | 0.0530 (49) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-128 | 0.2282 (123) | 0.1864 (33) | 0.1914 (40) | 0.2119 (196) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-256 | 0.2226 (120) | 0.1864 (33) | 0.2536 (53) | 0.2227 (206) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-512 | 0.1466 (79) | 0.1695 (30) | 0.1148 (24) | 0.1438 (133) |
| qasper | hybrid-rerank | bge-small | production | 1024 | section-aware | 0.2356 (127) | 0.2655 (47) | 0.2488 (52) | 0.2443 (226) |
| qasper | hybrid-rerank | bge-small | production | 1024 | small-to-big | 0.0575 (31) | 0.0734 (13) | 0.0574 (12) | 0.0605 (56) |
| qasper | hybrid-rerank | bge-small | production | 1024 | fixed-1024 | 0.0538 (29) | 0.0678 (12) | 0.0861 (18) | 0.0638 (59) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-64 | 0.1173 (65) | 0.0989 (18) | 0.1033 (22) | 0.1106 (105) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-128 | 0.1986 (110) | 0.1593 (29) | 0.1643 (35) | 0.1834 (174) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-256 | 0.2094 (116) | 0.1813 (33) | 0.2347 (50) | 0.2097 (199) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-512 | 0.1408 (78) | 0.1648 (30) | 0.1080 (23) | 0.1380 (131) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | section-aware | 0.2256 (125) | 0.2582 (47) | 0.2488 (53) | 0.2371 (225) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | small-to-big | 0.0560 (31) | 0.0714 (13) | 0.0563 (12) | 0.0590 (56) |
| qasper | hybrid-rerank | bge-small | fair | 1024 | fixed-1024 | 0.0523 (29) | 0.0659 (12) | 0.0845 (18) | 0.0622 (59) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-64 | 0.0536 (29) | 0.0592 (10) | 0.0502 (11) | 0.0538 (50) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-128 | 0.2348 (127) | 0.1775 (30) | 0.1963 (43) | 0.2153 (200) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-256 | 0.1848 (100) | 0.1538 (26) | 0.2420 (53) | 0.1927 (179) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-512 | 0.1497 (81) | 0.2308 (39) | 0.1279 (28) | 0.1593 (148) |
| qasper | hybrid-rerank | nomic | production | 1024 | section-aware | 0.2458 (133) | 0.2663 (45) | 0.2420 (53) | 0.2487 (231) |
| qasper | hybrid-rerank | nomic | production | 1024 | small-to-big | 0.0813 (44) | 0.0592 (10) | 0.0594 (13) | 0.0721 (67) |
| qasper | hybrid-rerank | nomic | production | 1024 | fixed-1024 | 0.0499 (27) | 0.0533 (9) | 0.0822 (18) | 0.0581 (54) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 0.1266 (71) | 0.1272 (22) | 0.1062 (24) | 0.1219 (117) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-128 | 0.1979 (111) | 0.1445 (25) | 0.1770 (40) | 0.1833 (176) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 0.1729 (97) | 0.1503 (26) | 0.2212 (50) | 0.1802 (173) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 0.1444 (81) | 0.2197 (38) | 0.1195 (27) | 0.1521 (146) |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 0.2353 (132) | 0.2486 (43) | 0.2389 (54) | 0.2385 (229) |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 0.0749 (42) | 0.0578 (10) | 0.0575 (13) | 0.0677 (65) |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 0.0481 (27) | 0.0520 (9) | 0.0796 (18) | 0.0563 (54) |
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
| qasper | hybrid | bge-small | production | 1024 | fixed-64 | 0.0907 (40) | 0.1250 (18) | 0.0556 (10) | 0.0889 (68) |
| qasper | hybrid | bge-small | production | 1024 | fixed-128 | 0.2698 (119) | 0.2431 (35) | 0.2000 (36) | 0.2484 (190) |
| qasper | hybrid | bge-small | production | 1024 | fixed-256 | 0.1655 (73) | 0.2014 (29) | 0.2389 (43) | 0.1895 (145) |
| qasper | hybrid | bge-small | production | 1024 | fixed-512 | 0.1224 (54) | 0.0625 (9) | 0.1278 (23) | 0.1124 (86) |
| qasper | hybrid | bge-small | production | 1024 | section-aware | 0.2313 (102) | 0.2222 (32) | 0.2000 (36) | 0.2222 (170) |
| qasper | hybrid | bge-small | production | 1024 | small-to-big | 0.0839 (37) | 0.0625 (9) | 0.1167 (21) | 0.0876 (67) |
| qasper | hybrid | bge-small | production | 1024 | fixed-1024 | 0.0363 (16) | 0.0833 (12) | 0.0611 (11) | 0.0510 (39) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-64 | 0.1880 (88) | 0.2105 (32) | 0.1568 (29) | 0.1851 (149) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-128 | 0.2329 (109) | 0.2039 (31) | 0.1514 (28) | 0.2087 (168) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-256 | 0.1453 (68) | 0.1842 (28) | 0.2108 (39) | 0.1677 (135) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-512 | 0.1090 (51) | 0.0526 (8) | 0.1243 (23) | 0.1019 (82) |
| qasper | hybrid | bge-small | fair | 1024 | section-aware | 0.2158 (101) | 0.2105 (32) | 0.1838 (34) | 0.2075 (167) |
| qasper | hybrid | bge-small | fair | 1024 | small-to-big | 0.0769 (36) | 0.0592 (9) | 0.1135 (21) | 0.0820 (66) |
| qasper | hybrid | bge-small | fair | 1024 | fixed-1024 | 0.0321 (15) | 0.0789 (12) | 0.0595 (11) | 0.0472 (38) |
| qasper | hybrid | nomic | production | 1024 | fixed-64 | 0.0931 (42) | 0.1000 (15) | 0.0904 (17) | 0.0938 (74) |
| qasper | hybrid | nomic | production | 1024 | fixed-128 | 0.2838 (128) | 0.2200 (33) | 0.2713 (51) | 0.2687 (212) |
| qasper | hybrid | nomic | production | 1024 | fixed-256 | 0.1752 (79) | 0.2067 (31) | 0.1755 (33) | 0.1812 (143) |
| qasper | hybrid | nomic | production | 1024 | fixed-512 | 0.1153 (52) | 0.1533 (23) | 0.1277 (24) | 0.1255 (99) |
| qasper | hybrid | nomic | production | 1024 | section-aware | 0.1951 (88) | 0.1800 (27) | 0.1862 (35) | 0.1901 (150) |
| qasper | hybrid | nomic | production | 1024 | small-to-big | 0.1042 (47) | 0.0800 (12) | 0.0904 (17) | 0.0963 (76) |
| qasper | hybrid | nomic | production | 1024 | fixed-1024 | 0.0333 (15) | 0.0600 (9) | 0.0585 (11) | 0.0444 (35) |
| qasper | hybrid | nomic | fair | 1024 | fixed-64 | 0.1837 (88) | 0.1871 (29) | 0.1598 (31) | 0.1787 (148) |
| qasper | hybrid | nomic | fair | 1024 | fixed-128 | 0.2463 (118) | 0.1871 (29) | 0.2268 (44) | 0.2307 (191) |
| qasper | hybrid | nomic | fair | 1024 | fixed-256 | 0.1608 (77) | 0.1935 (30) | 0.1701 (33) | 0.1691 (140) |
| qasper | hybrid | nomic | fair | 1024 | fixed-512 | 0.1065 (51) | 0.1419 (22) | 0.1237 (24) | 0.1171 (97) |
| qasper | hybrid | nomic | fair | 1024 | section-aware | 0.1775 (85) | 0.1677 (26) | 0.1804 (35) | 0.1763 (146) |
| qasper | hybrid | nomic | fair | 1024 | small-to-big | 0.0939 (45) | 0.0710 (11) | 0.0876 (17) | 0.0882 (73) |
| qasper | hybrid | nomic | fair | 1024 | fixed-1024 | 0.0313 (15) | 0.0516 (8) | 0.0515 (10) | 0.0399 (33) |
| qasper | vector | bge-small | production | 1024 | fixed-64 | 0.1362 (53) | 0.1271 (15) | 0.1304 (21) | 0.1332 (89) |
| qasper | vector | bge-small | production | 1024 | fixed-128 | 0.2288 (89) | 0.1864 (22) | 0.2112 (34) | 0.2171 (145) |
| qasper | vector | bge-small | production | 1024 | fixed-256 | 0.1722 (67) | 0.1949 (23) | 0.1739 (28) | 0.1766 (118) |
| qasper | vector | bge-small | production | 1024 | fixed-512 | 0.1003 (39) | 0.1356 (16) | 0.1118 (18) | 0.1093 (73) |
| qasper | vector | bge-small | production | 1024 | section-aware | 0.1979 (77) | 0.1949 (23) | 0.2547 (41) | 0.2111 (141) |
| qasper | vector | bge-small | production | 1024 | small-to-big | 0.1440 (56) | 0.0932 (11) | 0.0683 (11) | 0.1168 (78) |
| qasper | vector | bge-small | production | 1024 | fixed-1024 | 0.0206 (8) | 0.0678 (8) | 0.0497 (8) | 0.0359 (24) |
| qasper | vector | bge-small | fair | 1024 | fixed-64 | 0.2139 (89) | 0.2000 (25) | 0.2209 (38) | 0.2132 (152) |
| qasper | vector | bge-small | fair | 1024 | fixed-128 | 0.1971 (82) | 0.1600 (20) | 0.1686 (29) | 0.1837 (131) |
| qasper | vector | bge-small | fair | 1024 | fixed-256 | 0.1442 (60) | 0.1840 (23) | 0.1570 (27) | 0.1543 (110) |
| qasper | vector | bge-small | fair | 1024 | fixed-512 | 0.0938 (39) | 0.1120 (14) | 0.0988 (17) | 0.0982 (70) |
| qasper | vector | bge-small | fair | 1024 | section-aware | 0.1947 (81) | 0.1920 (24) | 0.2442 (42) | 0.2062 (147) |
| qasper | vector | bge-small | fair | 1024 | small-to-big | 0.1370 (57) | 0.0880 (11) | 0.0640 (11) | 0.1108 (79) |
| qasper | vector | bge-small | fair | 1024 | fixed-1024 | 0.0192 (8) | 0.0640 (8) | 0.0465 (8) | 0.0337 (24) |
| qasper | vector | nomic | production | 1024 | fixed-64 | 0.1298 (54) | 0.0956 (13) | 0.0943 (15) | 0.1153 (82) |
| qasper | vector | nomic | production | 1024 | fixed-128 | 0.2764 (115) | 0.1544 (21) | 0.2579 (41) | 0.2489 (177) |
| qasper | vector | nomic | production | 1024 | fixed-256 | 0.1106 (46) | 0.2279 (31) | 0.2013 (32) | 0.1533 (109) |
| qasper | vector | nomic | production | 1024 | fixed-512 | 0.1034 (43) | 0.1912 (26) | 0.1447 (23) | 0.1294 (92) |
| qasper | vector | nomic | production | 1024 | section-aware | 0.2212 (92) | 0.1838 (25) | 0.2013 (32) | 0.2096 (149) |
| qasper | vector | nomic | production | 1024 | small-to-big | 0.1370 (57) | 0.0809 (11) | 0.0818 (13) | 0.1139 (81) |
| qasper | vector | nomic | production | 1024 | fixed-1024 | 0.0216 (9) | 0.0662 (9) | 0.0189 (3) | 0.0295 (21) |
| qasper | vector | nomic | fair | 1024 | fixed-64 | 0.2336 (103) | 0.1724 (25) | 0.1905 (32) | 0.2122 (160) |
| qasper | vector | nomic | fair | 1024 | fixed-128 | 0.2154 (95) | 0.1379 (20) | 0.2083 (35) | 0.1989 (150) |
| qasper | vector | nomic | fair | 1024 | fixed-256 | 0.0998 (44) | 0.2138 (31) | 0.1905 (32) | 0.1419 (107) |
| qasper | vector | nomic | fair | 1024 | fixed-512 | 0.0975 (43) | 0.1655 (24) | 0.1369 (23) | 0.1194 (90) |
| qasper | vector | nomic | fair | 1024 | section-aware | 0.2041 (90) | 0.1724 (25) | 0.1786 (30) | 0.1923 (145) |
| qasper | vector | nomic | fair | 1024 | small-to-big | 0.1293 (57) | 0.0759 (11) | 0.0774 (13) | 0.1074 (81) |
| qasper | vector | nomic | fair | 1024 | fixed-1024 | 0.0204 (9) | 0.0621 (9) | 0.0179 (3) | 0.0279 (21) |
