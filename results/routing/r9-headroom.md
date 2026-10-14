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
| qasper/grid | `97bc8de66def0c97a34aaefe87bc535bd43e7b8f2f2320a696721ee5ab74df62` |

| dataset | documents | precise | context | mixed | questions |
|---|---|---|---|---|---|
| qasper | 684 | 1317 | 404 | 476 | 2197 |

Pipelines: `bm25` (embedder -), `hybrid` (embedder bge-small), `hybrid` (embedder nomic), `hybrid-rerank` (embedder bge-small), `hybrid-rerank` (embedder nomic), `vector` (embedder bge-small), `vector` (embedder nomic).

## The oracle router's chunking per query type, at 1024 tokens

Each cell: the share of the query type's questions for which the oracle router picks the chunking, and their count. Ties go to the smaller chunk, so a question on which every chunking scores the same goes to the smallest candidate; the last row of each block counts those questions.

| dataset | pipeline | embedder | view | budget | chunking | precise | context | mixed | all |
|---|---|---|---|---|---|---|---|---|---|
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
