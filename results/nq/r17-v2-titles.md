# R17 - nq v2-titles: section-aware chunks with their titles next to section-aware

Config hash: `dbcb66db9a440d7a1b9b0cccc5a543070880f7651bd7bf993987388f11c5054a`

## Config

```yaml
chunkings:
- section-aware
- section-aware-titles
embedder: nomic
gate:
  budget: 1024
  confidence: 0.95
  max_loss: 0.01
  min_gain: 0.02
  resamples: 10000
  seed: 0
  view: budget
kind: contenders
notes:
- section-aware-titles keeps section-aware's spans and searches them with the dataset's
  own document and section title in front, for search only (BM25, the vector and the
  reranker pairs); the reader and the recall score see the chunk text, and the budget
  counts only that text. No language model is involved.
pairs:
- - section-aware-titles
  - section-aware
pipeline: hybrid-rerank
run_name: v2-titles
runs:
- qasper/v2-titles
- nq/v2-titles
scope: collection
table: r17
title: section-aware chunks with their titles next to section-aware
```

## Runs

| run | dataset | questions | config hash |
|---|---|---|---|
| qasper/v2-titles | qasper | 2197 | `0b60e4811932349583d9714f63881085d1a05ccf6f3a85633dc11623bbb3d908` |
| nq/v2-titles | nq | 1000 | `3bd1a0559ea19a538444eb855a7d0b93a494388536e92193c588ae8363f66b03` |

## Dataset

| dataset | split | sha256 |
|---|---|---|
| qasper | dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| qasper | test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |
| nq | dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

Retrieval recall and precision, hybrid-rerank with nomic, collection search: nq (n = 1000) and pooled (qasper + nq) (n = 3197), means over questions.

## Budget view (top-N cap 20)

| chunking | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0580 | 0.0339 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.2403 | 0.0995 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.6600 | 0.1620 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.8197 | 0.1067 | 0.4269 | 0.0655 |
| section-aware | 2048 | 0.9087 | 0.0609 | 0.4956 | 0.0394 |
| section-aware | 4096 | 0.9489 | 0.0323 | 0.5325 | 0.0218 |
| section-aware | 8192 | 0.9669 | 0.0211 | 0.5438 | 0.0159 |
| section-aware-titles | 128 | 0.0701 | 0.0400 | 0.0474 | 0.0365 |
| section-aware-titles | 256 | 0.2621 | 0.1062 | 0.1296 | 0.0615 |
| section-aware-titles | 512 | 0.6678 | 0.1688 | 0.3327 | 0.0975 |
| section-aware-titles | 1024 | 0.8558 | 0.1132 | 0.4497 | 0.0702 |
| section-aware-titles | 2048 | 0.9401 | 0.0637 | 0.5211 | 0.0424 |
| section-aware-titles | 4096 | 0.9721 | 0.0344 | 0.5568 | 0.0240 |
| section-aware-titles | 8192 | 0.9891 | 0.0251 | 0.5689 | 0.0183 |

## Production view (top-N cap 8)

| chunking | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|
| section-aware | 128 | 0.0580 | 0.0339 | 0.0398 | 0.0307 |
| section-aware | 256 | 0.2403 | 0.0995 | 0.1188 | 0.0562 |
| section-aware | 512 | 0.6600 | 0.1621 | 0.3143 | 0.0888 |
| section-aware | 1024 | 0.8197 | 0.1072 | 0.4262 | 0.0656 |
| section-aware | 2048 | 0.9077 | 0.0650 | 0.4923 | 0.0424 |
| section-aware | 4096 | 0.9299 | 0.0541 | 0.5040 | 0.0375 |
| section-aware | 8192 | 0.9299 | 0.0541 | 0.5040 | 0.0375 |
| section-aware-titles | 128 | 0.0701 | 0.0405 | 0.0474 | 0.0367 |
| section-aware-titles | 256 | 0.2621 | 0.1083 | 0.1296 | 0.0621 |
| section-aware-titles | 512 | 0.6678 | 0.1721 | 0.3327 | 0.0985 |
| section-aware-titles | 1024 | 0.8558 | 0.1171 | 0.4497 | 0.0715 |
| section-aware-titles | 2048 | 0.9401 | 0.0729 | 0.5168 | 0.0470 |
| section-aware-titles | 4096 | 0.9641 | 0.0605 | 0.5332 | 0.0416 |
| section-aware-titles | 8192 | 0.9641 | 0.0605 | 0.5332 | 0.0416 |

## Contender minus reference

| contender - reference | view | budget | nq recall | nq precision | pooled recall | pooled precision |
|---|---|---|---|---|---|---|
| section-aware-titles - section-aware | budget | 128 | +0.0121 | +0.0061 | +0.0076 | +0.0059 |
| section-aware-titles - section-aware | budget | 256 | +0.0218 | +0.0068 | +0.0108 | +0.0052 |
| section-aware-titles - section-aware | budget | 512 | +0.0078 | +0.0068 | +0.0183 | +0.0087 |
| section-aware-titles - section-aware | budget | 1024 | +0.0361 | +0.0065 | +0.0228 | +0.0047 |
| section-aware-titles - section-aware | budget | 2048 | +0.0314 | +0.0028 | +0.0255 | +0.0029 |
| section-aware-titles - section-aware | budget | 4096 | +0.0232 | +0.0021 | +0.0244 | +0.0021 |
| section-aware-titles - section-aware | budget | 8192 | +0.0221 | +0.0040 | +0.0251 | +0.0024 |
| section-aware-titles - section-aware | production | 128 | +0.0121 | +0.0066 | +0.0076 | +0.0060 |
| section-aware-titles - section-aware | production | 256 | +0.0218 | +0.0089 | +0.0108 | +0.0059 |
| section-aware-titles - section-aware | production | 512 | +0.0078 | +0.0101 | +0.0183 | +0.0097 |
| section-aware-titles - section-aware | production | 1024 | +0.0361 | +0.0099 | +0.0234 | +0.0059 |
| section-aware-titles - section-aware | production | 2048 | +0.0324 | +0.0079 | +0.0244 | +0.0047 |
| section-aware-titles - section-aware | production | 4096 | +0.0341 | +0.0064 | +0.0292 | +0.0040 |
| section-aware-titles - section-aware | production | 8192 | +0.0341 | +0.0064 | +0.0292 | +0.0040 |
## Bar verdict (pre-registered)

Judged on the hybrid-rerank pipeline with nomic, budget view (top-N cap 20), 1024-token budget, pooled over the runs' datasets, with a 95% CI from the paired, document-clustered bootstrap (10000 resamples, seed 0).

- section-aware-titles - section-aware, pooled: +0.0228 [+0.0128, +0.0331]; nq +0.0361, qasper +0.0168.
- **Verdict: section-aware-titles clears the bar** (pooled gain at least +0.0200 with a CI excluding 0, and neither dataset alone below -0.0100).


n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.

section-aware-titles keeps section-aware's spans and searches them with the dataset's own document and section title in front, for search only (BM25, the vector and the reranker pairs); the reader and the recall score see the chunk text, and the budget counts only that text. No language model is involved.
