# R8 - chunk size x query type interaction

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

## Chunk size x query type interaction against fixed-128

For each chunking: Δ context = mean recall (chunking − fixed-128) on context questions, Δ precise = the same on precise questions, and interaction = Δ context − Δ precise. A positive interaction means the chunking does relatively better than fixed-128 on context questions than on precise ones. Mixed questions are left out.

| dataset | pipeline | embedder | view | budget | chunking | precise n | context n | Δ context | Δ precise | interaction | CI | CI level | CI excludes 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | hybrid-rerank | nomic | fair | 128 | fixed-64 | 1817 | 904 | -0.0151 | +0.0057 | -0.0207 | [-0.0459, +0.0052] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 128 | section-aware | 1817 | 904 | -0.1312 | -0.0771 | -0.0541 | [-0.0895, -0.0197] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | fair | 128 | small-to-big | 1817 | 904 | +0.0182 | +0.0334 | -0.0152 | [-0.0446, +0.0145] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-64 | 1817 | 904 | -0.0362 | -0.0184 | -0.0179 | [-0.0439, +0.0086] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 256 | fixed-256 | 1817 | 904 | -0.0070 | -0.0297 | +0.0227 | [-0.0056, +0.0519] | 97.50% | no |
| pooled | hybrid-rerank | nomic | fair | 256 | section-aware | 1817 | 904 | -0.1163 | -0.0744 | -0.0419 | [-0.0842, +0.0003] | 99.00% | no |
| pooled | hybrid-rerank | nomic | fair | 256 | small-to-big | 1817 | 904 | +0.0380 | +0.0295 | +0.0085 | [-0.0253, +0.0424] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-64 | 1817 | 904 | -0.0523 | -0.0392 | -0.0131 | [-0.0408, +0.0137] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-256 | 1817 | 904 | +0.0224 | -0.0090 | +0.0313 | [+0.0005, +0.0628] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | fair | 512 | fixed-512 | 1817 | 904 | +0.0098 | -0.0190 | +0.0288 | [-0.0114, +0.0682] | 98.33% | no |
| pooled | hybrid-rerank | nomic | fair | 512 | section-aware | 1817 | 904 | +0.0558 | +0.0402 | +0.0156 | [-0.0274, +0.0585] | 99.00% | no |
| pooled | hybrid-rerank | nomic | fair | 512 | small-to-big | 1817 | 904 | +0.0395 | +0.0514 | -0.0119 | [-0.0507, +0.0256] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 1817 | 904 | -0.0770 | -0.0578 | -0.0192 | [-0.0400, +0.0008] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 1817 | 904 | +0.0190 | +0.0134 | +0.0056 | [-0.0184, +0.0296] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 1817 | 904 | +0.0329 | +0.0187 | +0.0141 | [-0.0148, +0.0434] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | section-aware | 1817 | 904 | +0.0885 | +0.0730 | +0.0155 | [-0.0122, +0.0438] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | small-to-big | 1817 | 904 | +0.0543 | +0.0642 | -0.0098 | [-0.0376, +0.0184] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 1817 | 904 | +0.0034 | -0.0188 | +0.0222 | [-0.0115, +0.0555] | 95.00% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 1817 | 904 | -0.0926 | -0.0767 | -0.0159 | [-0.0421, +0.0096] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 1817 | 904 | +0.0472 | +0.0227 | +0.0245 | [-0.0012, +0.0499] | 97.50% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 1817 | 904 | +0.0583 | +0.0367 | +0.0216 | [-0.0115, +0.0566] | 98.33% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | section-aware | 1817 | 904 | +0.0888 | +0.0822 | +0.0067 | [-0.0280, +0.0398] | 99.00% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | small-to-big | 1817 | 904 | +0.0683 | +0.0698 | -0.0015 | [-0.0349, +0.0323] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 1817 | 904 | +0.0362 | +0.0185 | +0.0177 | [-0.0167, +0.0527] | 97.50% | no |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 1817 | 904 | -0.0582 | -0.0484 | -0.0099 | [-0.0348, +0.0153] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 1817 | 904 | +0.0669 | +0.0371 | +0.0299 | [+0.0047, +0.0559] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 1817 | 904 | +0.0846 | +0.0591 | +0.0256 | [-0.0043, +0.0571] | 98.33% | no |
| pooled | hybrid-rerank | nomic | fair | 4096 | section-aware | 1817 | 904 | +0.0947 | +0.0810 | +0.0137 | [-0.0169, +0.0438] | 99.00% | no |
| pooled | hybrid-rerank | nomic | fair | 4096 | small-to-big | 1817 | 904 | +0.0809 | +0.0793 | +0.0016 | [-0.0280, +0.0329] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 1817 | 904 | +0.0780 | +0.0508 | +0.0272 | [-0.0038, +0.0593] | 97.50% | no |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 1817 | 904 | -0.0591 | -0.0517 | -0.0074 | [-0.0300, +0.0145] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 1817 | 904 | +0.0402 | +0.0097 | +0.0305 | [+0.0074, +0.0534] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 1817 | 904 | +0.0723 | +0.0384 | +0.0338 | [+0.0068, +0.0617] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | fair | 8192 | section-aware | 1817 | 904 | +0.0665 | +0.0485 | +0.0181 | [-0.0112, +0.0474] | 99.00% | no |
| pooled | hybrid-rerank | nomic | fair | 8192 | small-to-big | 1817 | 904 | +0.0569 | +0.0446 | +0.0123 | [-0.0146, +0.0402] | 99.17% | no |
| pooled | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 1817 | 904 | +0.0798 | +0.0423 | +0.0375 | [+0.0062, +0.0700] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | budget | 128 | fixed-64 | 1817 | 904 | -0.0151 | +0.0057 | -0.0207 | [-0.0449, +0.0042] | 98.75% | no |
| pooled | hybrid-rerank | nomic | budget | 128 | section-aware | 1817 | 904 | -0.1312 | -0.0771 | -0.0541 | [-0.0895, -0.0197] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | budget | 128 | small-to-big | 1817 | 904 | +0.0182 | +0.0334 | -0.0152 | [-0.0446, +0.0145] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 256 | fixed-64 | 1817 | 904 | -0.0362 | -0.0184 | -0.0179 | [-0.0430, +0.0071] | 98.75% | no |
| pooled | hybrid-rerank | nomic | budget | 256 | fixed-256 | 1817 | 904 | -0.0070 | -0.0297 | +0.0227 | [-0.0056, +0.0519] | 97.50% | no |
| pooled | hybrid-rerank | nomic | budget | 256 | section-aware | 1817 | 904 | -0.1163 | -0.0744 | -0.0419 | [-0.0842, +0.0003] | 99.00% | no |
| pooled | hybrid-rerank | nomic | budget | 256 | small-to-big | 1817 | 904 | +0.0380 | +0.0295 | +0.0085 | [-0.0253, +0.0424] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-64 | 1817 | 904 | -0.0523 | -0.0392 | -0.0131 | [-0.0387, +0.0121] | 98.75% | no |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-256 | 1817 | 904 | +0.0224 | -0.0090 | +0.0313 | [+0.0005, +0.0628] | 98.33% | yes |
| pooled | hybrid-rerank | nomic | budget | 512 | fixed-512 | 1817 | 904 | +0.0098 | -0.0190 | +0.0288 | [-0.0114, +0.0682] | 98.33% | no |
| pooled | hybrid-rerank | nomic | budget | 512 | section-aware | 1817 | 904 | +0.0558 | +0.0402 | +0.0156 | [-0.0274, +0.0585] | 99.00% | no |
| pooled | hybrid-rerank | nomic | budget | 512 | small-to-big | 1817 | 904 | +0.0395 | +0.0514 | -0.0119 | [-0.0507, +0.0256] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 1817 | 904 | -0.0770 | -0.0578 | -0.0192 | [-0.0400, +0.0008] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 1817 | 904 | +0.0190 | +0.0134 | +0.0056 | [-0.0184, +0.0296] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 1817 | 904 | +0.0329 | +0.0187 | +0.0141 | [-0.0148, +0.0434] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | section-aware | 1817 | 904 | +0.0885 | +0.0730 | +0.0155 | [-0.0122, +0.0438] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | small-to-big | 1817 | 904 | +0.0543 | +0.0642 | -0.0098 | [-0.0376, +0.0184] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 1817 | 904 | +0.0034 | -0.0188 | +0.0222 | [-0.0115, +0.0555] | 95.00% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 1817 | 904 | -0.1244 | -0.1012 | -0.0232 | [-0.0487, +0.0020] | 98.75% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 1817 | 904 | +0.0472 | +0.0227 | +0.0245 | [-0.0012, +0.0499] | 97.50% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 1817 | 904 | +0.0583 | +0.0367 | +0.0216 | [-0.0115, +0.0566] | 98.33% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | section-aware | 1817 | 904 | +0.0888 | +0.0822 | +0.0067 | [-0.0280, +0.0398] | 99.00% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | small-to-big | 1817 | 904 | +0.0683 | +0.0698 | -0.0015 | [-0.0349, +0.0323] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 1817 | 904 | +0.0362 | +0.0185 | +0.0177 | [-0.0167, +0.0527] | 97.50% | no |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 1817 | 904 | -0.1400 | -0.1136 | -0.0265 | [-0.0527, -0.0003] | 99.17% | yes |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 1817 | 904 | +0.0911 | +0.0590 | +0.0320 | [+0.0045, +0.0596] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 1817 | 904 | +0.1088 | +0.0810 | +0.0277 | [-0.0025, +0.0597] | 98.33% | no |
| pooled | hybrid-rerank | nomic | budget | 4096 | section-aware | 1817 | 904 | +0.1177 | +0.1019 | +0.0158 | [-0.0158, +0.0466] | 99.00% | no |
| pooled | hybrid-rerank | nomic | budget | 4096 | small-to-big | 1817 | 904 | +0.1050 | +0.1013 | +0.0037 | [-0.0279, +0.0357] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 1817 | 904 | +0.1021 | +0.0728 | +0.0293 | [-0.0031, +0.0624] | 97.50% | no |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 1817 | 904 | -0.1400 | -0.1136 | -0.0265 | [-0.0524, -0.0010] | 99.00% | yes |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 1817 | 904 | +0.0983 | +0.0688 | +0.0295 | [+0.0033, +0.0562] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 1817 | 904 | +0.1528 | +0.1195 | +0.0333 | [+0.0026, +0.0653] | 98.75% | yes |
| pooled | hybrid-rerank | nomic | budget | 8192 | section-aware | 1817 | 904 | +0.1304 | +0.1146 | +0.0158 | [-0.0155, +0.0469] | 99.00% | no |
| pooled | hybrid-rerank | nomic | budget | 8192 | small-to-big | 1817 | 904 | +0.1274 | +0.1173 | +0.0100 | [-0.0209, +0.0412] | 99.17% | no |
| pooled | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 1817 | 904 | +0.1604 | +0.1234 | +0.0370 | [+0.0034, +0.0714] | 98.33% | yes |
| nq | hybrid-rerank | nomic | fair | 128 | fixed-64 | 500 | 500 | -0.0323 | -0.0084 | -0.0239 | [-0.0784, +0.0324] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 128 | section-aware | 500 | 500 | -0.2286 | -0.2489 | +0.0202 | [-0.0485, +0.0904] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 128 | small-to-big | 500 | 500 | +0.0298 | +0.0407 | -0.0109 | [-0.0717, +0.0506] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-64 | 500 | 500 | -0.0605 | -0.0566 | -0.0039 | [-0.0578, +0.0499] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 256 | fixed-256 | 500 | 500 | +0.0003 | -0.0118 | +0.0121 | [-0.0576, +0.0825] | 99.00% | no |
| nq | hybrid-rerank | nomic | fair | 256 | section-aware | 500 | 500 | -0.1885 | -0.1980 | +0.0094 | [-0.0759, +0.0956] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 256 | small-to-big | 500 | 500 | +0.0684 | +0.0639 | +0.0045 | [-0.0597, +0.0672] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-64 | 500 | 500 | -0.0839 | -0.0917 | +0.0077 | [-0.0446, +0.0605] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-256 | 500 | 500 | +0.0447 | +0.0168 | +0.0279 | [-0.0367, +0.0933] | 99.00% | no |
| nq | hybrid-rerank | nomic | fair | 512 | fixed-512 | 500 | 500 | +0.0358 | +0.0516 | -0.0158 | [-0.0950, +0.0629] | 98.75% | no |
| nq | hybrid-rerank | nomic | fair | 512 | section-aware | 500 | 500 | +0.0820 | +0.1046 | -0.0226 | [-0.1053, +0.0613] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 512 | small-to-big | 500 | 500 | +0.0713 | +0.1035 | -0.0322 | [-0.1063, +0.0420] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 500 | 500 | -0.1139 | -0.1078 | -0.0060 | [-0.0440, +0.0323] | 95.00% | no |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 500 | 500 | +0.0293 | +0.0633 | -0.0340 | [-0.0779, +0.0097] | 95.00% | no |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 500 | 500 | +0.0492 | +0.1099 | -0.0607 | [-0.1137, -0.0088] | 95.00% | yes |
| nq | hybrid-rerank | nomic | fair | 1024 | section-aware | 500 | 500 | +0.1127 | +0.1492 | -0.0365 | [-0.0855, +0.0127] | 95.00% | no |
| nq | hybrid-rerank | nomic | fair | 1024 | small-to-big | 500 | 500 | +0.0755 | +0.1212 | -0.0456 | [-0.0954, +0.0032] | 95.00% | no |
| nq | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 500 | 500 | +0.0280 | +0.0757 | -0.0477 | [-0.1055, +0.0100] | 95.00% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 500 | 500 | -0.1281 | -0.1377 | +0.0097 | [-0.0361, +0.0557] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 500 | 500 | +0.0569 | +0.0643 | -0.0074 | [-0.0588, +0.0418] | 99.00% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 500 | 500 | +0.0714 | +0.1061 | -0.0346 | [-0.0925, +0.0242] | 98.75% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | section-aware | 500 | 500 | +0.1126 | +0.1382 | -0.0256 | [-0.0801, +0.0301] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | small-to-big | 500 | 500 | +0.0829 | +0.1053 | -0.0224 | [-0.0774, +0.0311] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 500 | 500 | +0.0571 | +0.0918 | -0.0347 | [-0.0972, +0.0266] | 98.33% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 500 | 500 | -0.0824 | -0.0957 | +0.0133 | [-0.0293, +0.0569] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 500 | 500 | +0.0798 | +0.0782 | +0.0016 | [-0.0415, +0.0450] | 99.00% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 500 | 500 | +0.0874 | +0.1049 | -0.0174 | [-0.0658, +0.0318] | 98.75% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | section-aware | 500 | 500 | +0.1125 | +0.1140 | -0.0015 | [-0.0490, +0.0463] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | small-to-big | 500 | 500 | +0.0876 | +0.1017 | -0.0141 | [-0.0594, +0.0321] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 500 | 500 | +0.0857 | +0.0940 | -0.0083 | [-0.0599, +0.0431] | 98.33% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 500 | 500 | -0.0691 | -0.0857 | +0.0166 | [-0.0208, +0.0524] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 500 | 500 | +0.0537 | +0.0513 | +0.0024 | [-0.0310, +0.0334] | 99.00% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 500 | 500 | +0.0780 | +0.0738 | +0.0042 | [-0.0346, +0.0418] | 98.75% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | section-aware | 500 | 500 | +0.0796 | +0.0736 | +0.0060 | [-0.0318, +0.0411] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | small-to-big | 500 | 500 | +0.0636 | +0.0556 | +0.0080 | [-0.0277, +0.0426] | 99.17% | no |
| nq | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 500 | 500 | +0.0787 | +0.0697 | +0.0090 | [-0.0317, +0.0490] | 98.33% | no |
| nq | hybrid-rerank | nomic | budget | 128 | fixed-64 | 500 | 500 | -0.0323 | -0.0084 | -0.0239 | [-0.0784, +0.0324] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 128 | section-aware | 500 | 500 | -0.2286 | -0.2489 | +0.0202 | [-0.0485, +0.0904] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 128 | small-to-big | 500 | 500 | +0.0298 | +0.0407 | -0.0109 | [-0.0717, +0.0506] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 256 | fixed-64 | 500 | 500 | -0.0605 | -0.0566 | -0.0039 | [-0.0578, +0.0499] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 256 | fixed-256 | 500 | 500 | +0.0003 | -0.0118 | +0.0121 | [-0.0576, +0.0825] | 99.00% | no |
| nq | hybrid-rerank | nomic | budget | 256 | section-aware | 500 | 500 | -0.1885 | -0.1980 | +0.0094 | [-0.0759, +0.0956] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 256 | small-to-big | 500 | 500 | +0.0684 | +0.0639 | +0.0045 | [-0.0597, +0.0672] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-64 | 500 | 500 | -0.0839 | -0.0917 | +0.0077 | [-0.0446, +0.0605] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-256 | 500 | 500 | +0.0447 | +0.0168 | +0.0279 | [-0.0367, +0.0933] | 99.00% | no |
| nq | hybrid-rerank | nomic | budget | 512 | fixed-512 | 500 | 500 | +0.0358 | +0.0516 | -0.0158 | [-0.0950, +0.0629] | 98.75% | no |
| nq | hybrid-rerank | nomic | budget | 512 | section-aware | 500 | 500 | +0.0820 | +0.1046 | -0.0226 | [-0.1053, +0.0613] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 512 | small-to-big | 500 | 500 | +0.0713 | +0.1035 | -0.0322 | [-0.1063, +0.0420] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 500 | 500 | -0.1139 | -0.1078 | -0.0060 | [-0.0440, +0.0323] | 95.00% | no |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 500 | 500 | +0.0293 | +0.0633 | -0.0340 | [-0.0779, +0.0097] | 95.00% | no |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 500 | 500 | +0.0492 | +0.1099 | -0.0607 | [-0.1137, -0.0088] | 95.00% | yes |
| nq | hybrid-rerank | nomic | budget | 1024 | section-aware | 500 | 500 | +0.1127 | +0.1492 | -0.0365 | [-0.0855, +0.0127] | 95.00% | no |
| nq | hybrid-rerank | nomic | budget | 1024 | small-to-big | 500 | 500 | +0.0755 | +0.1212 | -0.0456 | [-0.0954, +0.0032] | 95.00% | no |
| nq | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 500 | 500 | +0.0280 | +0.0757 | -0.0477 | [-0.1055, +0.0100] | 95.00% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 500 | 500 | -0.1754 | -0.1759 | +0.0005 | [-0.0460, +0.0497] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 500 | 500 | +0.0569 | +0.0643 | -0.0074 | [-0.0588, +0.0418] | 99.00% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 500 | 500 | +0.0714 | +0.1061 | -0.0346 | [-0.0925, +0.0242] | 98.75% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | section-aware | 500 | 500 | +0.1126 | +0.1382 | -0.0256 | [-0.0801, +0.0301] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | small-to-big | 500 | 500 | +0.0829 | +0.1053 | -0.0224 | [-0.0774, +0.0311] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 500 | 500 | +0.0571 | +0.0918 | -0.0347 | [-0.0972, +0.0266] | 98.33% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 500 | 500 | -0.1963 | -0.1961 | -0.0003 | [-0.0456, +0.0481] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 500 | 500 | +0.1110 | +0.1108 | +0.0002 | [-0.0446, +0.0451] | 99.00% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 500 | 500 | +0.1186 | +0.1374 | -0.0188 | [-0.0709, +0.0328] | 98.75% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | section-aware | 500 | 500 | +0.1437 | +0.1465 | -0.0029 | [-0.0539, +0.0483] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | small-to-big | 500 | 500 | +0.1188 | +0.1342 | -0.0154 | [-0.0638, +0.0336] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 500 | 500 | +0.1169 | +0.1265 | -0.0096 | [-0.0647, +0.0450] | 98.33% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 500 | 500 | -0.1963 | -0.1961 | -0.0003 | [-0.0456, +0.0481] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 500 | 500 | +0.1170 | +0.1247 | -0.0078 | [-0.0542, +0.0371] | 99.00% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 500 | 500 | +0.1660 | +0.1707 | -0.0047 | [-0.0535, +0.0425] | 98.75% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | section-aware | 500 | 500 | +0.1617 | +0.1645 | -0.0029 | [-0.0518, +0.0457] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | small-to-big | 500 | 500 | +0.1477 | +0.1465 | +0.0011 | [-0.0461, +0.0473] | 99.17% | no |
| nq | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 500 | 500 | +0.1668 | +0.1666 | +0.0002 | [-0.0486, +0.0479] | 98.33% | no |
| qasper | hybrid-rerank | nomic | fair | 128 | fixed-64 | 1317 | 404 | +0.0063 | +0.0110 | -0.0048 | [-0.0228, +0.0144] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 128 | section-aware | 1317 | 404 | -0.0106 | -0.0119 | +0.0013 | [-0.0246, +0.0256] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 128 | small-to-big | 1317 | 404 | +0.0038 | +0.0306 | -0.0268 | [-0.0488, -0.0046] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | fair | 256 | fixed-64 | 1317 | 404 | -0.0062 | -0.0038 | -0.0024 | [-0.0241, +0.0203] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 256 | fixed-256 | 1317 | 404 | -0.0160 | -0.0365 | +0.0205 | [-0.0056, +0.0461] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 256 | section-aware | 1317 | 404 | -0.0269 | -0.0274 | +0.0005 | [-0.0342, +0.0362] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 256 | small-to-big | 1317 | 404 | +0.0003 | +0.0164 | -0.0161 | [-0.0460, +0.0162] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-64 | 1317 | 404 | -0.0130 | -0.0193 | +0.0062 | [-0.0202, +0.0317] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-256 | 1317 | 404 | -0.0053 | -0.0188 | +0.0135 | [-0.0199, +0.0463] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 512 | fixed-512 | 1317 | 404 | -0.0224 | -0.0458 | +0.0234 | [-0.0148, +0.0596] | 98.33% | no |
| qasper | hybrid-rerank | nomic | fair | 512 | section-aware | 1317 | 404 | +0.0234 | +0.0158 | +0.0076 | [-0.0354, +0.0511] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 512 | small-to-big | 1317 | 404 | +0.0001 | +0.0316 | -0.0315 | [-0.0684, +0.0041] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-64 | 1317 | 404 | -0.0313 | -0.0387 | +0.0074 | [-0.0150, +0.0300] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-256 | 1317 | 404 | +0.0063 | -0.0055 | +0.0119 | [-0.0136, +0.0368] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-512 | 1317 | 404 | +0.0126 | -0.0159 | +0.0285 | [-0.0032, +0.0599] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | section-aware | 1317 | 404 | +0.0586 | +0.0441 | +0.0146 | [-0.0208, +0.0491] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | small-to-big | 1317 | 404 | +0.0281 | +0.0425 | -0.0144 | [-0.0477, +0.0192] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 1024 | fixed-1024 | 1317 | 404 | -0.0271 | -0.0547 | +0.0276 | [-0.0104, +0.0650] | 95.00% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-64 | 1317 | 404 | -0.0486 | -0.0535 | +0.0049 | [-0.0241, +0.0337] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-256 | 1317 | 404 | +0.0351 | +0.0069 | +0.0282 | [-0.0073, +0.0631] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-512 | 1317 | 404 | +0.0420 | +0.0104 | +0.0317 | [-0.0109, +0.0738] | 98.33% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | section-aware | 1317 | 404 | +0.0594 | +0.0609 | -0.0015 | [-0.0460, +0.0430] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | small-to-big | 1317 | 404 | +0.0503 | +0.0563 | -0.0060 | [-0.0451, +0.0344] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 2048 | fixed-1024 | 1317 | 404 | +0.0103 | -0.0094 | +0.0196 | [-0.0255, +0.0658] | 97.50% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-64 | 1317 | 404 | -0.0283 | -0.0304 | +0.0021 | [-0.0278, +0.0326] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-256 | 1317 | 404 | +0.0510 | +0.0214 | +0.0296 | [-0.0042, +0.0633] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-512 | 1317 | 404 | +0.0812 | +0.0417 | +0.0396 | [-0.0017, +0.0833] | 98.33% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | section-aware | 1317 | 404 | +0.0727 | +0.0685 | +0.0042 | [-0.0377, +0.0464] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | small-to-big | 1317 | 404 | +0.0724 | +0.0708 | +0.0017 | [-0.0388, +0.0426] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 4096 | fixed-1024 | 1317 | 404 | +0.0685 | +0.0344 | +0.0340 | [-0.0093, +0.0799] | 97.50% | no |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-64 | 1317 | 404 | -0.0467 | -0.0388 | -0.0080 | [-0.0363, +0.0192] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-256 | 1317 | 404 | +0.0236 | -0.0061 | +0.0296 | [-0.0028, +0.0612] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-512 | 1317 | 404 | +0.0652 | +0.0250 | +0.0402 | [+0.0005, +0.0806] | 98.75% | yes |
| qasper | hybrid-rerank | nomic | fair | 8192 | section-aware | 1317 | 404 | +0.0504 | +0.0389 | +0.0115 | [-0.0317, +0.0557] | 99.17% | no |
| qasper | hybrid-rerank | nomic | fair | 8192 | small-to-big | 1317 | 404 | +0.0486 | +0.0404 | +0.0082 | [-0.0315, +0.0502] | 99.00% | no |
| qasper | hybrid-rerank | nomic | fair | 8192 | fixed-1024 | 1317 | 404 | +0.0812 | +0.0319 | +0.0493 | [+0.0005, +0.0987] | 98.33% | yes |
| qasper | hybrid-rerank | nomic | budget | 128 | fixed-64 | 1317 | 404 | +0.0063 | +0.0110 | -0.0048 | [-0.0228, +0.0144] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 128 | section-aware | 1317 | 404 | -0.0106 | -0.0119 | +0.0013 | [-0.0246, +0.0256] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 128 | small-to-big | 1317 | 404 | +0.0038 | +0.0306 | -0.0268 | [-0.0488, -0.0046] | 99.17% | yes |
| qasper | hybrid-rerank | nomic | budget | 256 | fixed-64 | 1317 | 404 | -0.0062 | -0.0038 | -0.0024 | [-0.0241, +0.0203] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 256 | fixed-256 | 1317 | 404 | -0.0160 | -0.0365 | +0.0205 | [-0.0056, +0.0461] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 256 | section-aware | 1317 | 404 | -0.0269 | -0.0274 | +0.0005 | [-0.0342, +0.0362] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 256 | small-to-big | 1317 | 404 | +0.0003 | +0.0164 | -0.0161 | [-0.0460, +0.0162] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-64 | 1317 | 404 | -0.0130 | -0.0193 | +0.0062 | [-0.0202, +0.0317] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-256 | 1317 | 404 | -0.0053 | -0.0188 | +0.0135 | [-0.0199, +0.0463] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 512 | fixed-512 | 1317 | 404 | -0.0224 | -0.0458 | +0.0234 | [-0.0163, +0.0611] | 98.75% | no |
| qasper | hybrid-rerank | nomic | budget | 512 | section-aware | 1317 | 404 | +0.0234 | +0.0158 | +0.0076 | [-0.0354, +0.0511] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 512 | small-to-big | 1317 | 404 | +0.0001 | +0.0316 | -0.0315 | [-0.0684, +0.0041] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-64 | 1317 | 404 | -0.0313 | -0.0387 | +0.0074 | [-0.0150, +0.0300] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-256 | 1317 | 404 | +0.0063 | -0.0055 | +0.0119 | [-0.0136, +0.0368] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-512 | 1317 | 404 | +0.0126 | -0.0159 | +0.0285 | [-0.0032, +0.0599] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | section-aware | 1317 | 404 | +0.0586 | +0.0441 | +0.0146 | [-0.0208, +0.0491] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | small-to-big | 1317 | 404 | +0.0281 | +0.0425 | -0.0144 | [-0.0477, +0.0192] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 1024 | fixed-1024 | 1317 | 404 | -0.0271 | -0.0547 | +0.0276 | [-0.0104, +0.0650] | 95.00% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-64 | 1317 | 404 | -0.0613 | -0.0729 | +0.0116 | [-0.0181, +0.0404] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-256 | 1317 | 404 | +0.0351 | +0.0069 | +0.0282 | [-0.0073, +0.0631] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-512 | 1317 | 404 | +0.0420 | +0.0104 | +0.0317 | [-0.0127, +0.0758] | 98.75% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | section-aware | 1317 | 404 | +0.0594 | +0.0609 | -0.0015 | [-0.0460, +0.0430] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | small-to-big | 1317 | 404 | +0.0503 | +0.0563 | -0.0060 | [-0.0451, +0.0344] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 2048 | fixed-1024 | 1317 | 404 | +0.0103 | -0.0094 | +0.0196 | [-0.0286, +0.0690] | 98.33% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-64 | 1317 | 404 | -0.0704 | -0.0822 | +0.0119 | [-0.0181, +0.0421] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-256 | 1317 | 404 | +0.0664 | +0.0394 | +0.0270 | [-0.0062, +0.0614] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-512 | 1317 | 404 | +0.0966 | +0.0596 | +0.0370 | [-0.0054, +0.0822] | 98.75% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | section-aware | 1317 | 404 | +0.0857 | +0.0850 | +0.0007 | [-0.0427, +0.0427] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | small-to-big | 1317 | 404 | +0.0879 | +0.0888 | -0.0009 | [-0.0422, +0.0406] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 4096 | fixed-1024 | 1317 | 404 | +0.0839 | +0.0524 | +0.0315 | [-0.0145, +0.0806] | 98.33% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-64 | 1317 | 404 | -0.0704 | -0.0822 | +0.0119 | [-0.0181, +0.0421] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-256 | 1317 | 404 | +0.0752 | +0.0475 | +0.0277 | [-0.0055, +0.0619] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-512 | 1317 | 404 | +0.1365 | +0.1001 | +0.0365 | [-0.0071, +0.0831] | 98.75% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | section-aware | 1317 | 404 | +0.0917 | +0.0956 | -0.0039 | [-0.0486, +0.0400] | 99.17% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | small-to-big | 1317 | 404 | +0.1022 | +0.1062 | -0.0040 | [-0.0457, +0.0377] | 99.00% | no |
| qasper | hybrid-rerank | nomic | budget | 8192 | fixed-1024 | 1317 | 404 | +0.1525 | +0.1070 | +0.0456 | [-0.0034, +0.0966] | 98.33% | no |

CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals; 95% unadjusted at the primary budget of 1024 tokens, Holm-adjusted over the other budgets (the CI level column gives each interval's level).
Budgets where fixed-128 is not scored (its chunk is bigger than the budget) have no interaction rows.
