# R4 - nq grid, production line and ablations: fixed-k

Config hash: `b9cc99a6120a5b239138af5ab75b41aeb4cbebda4ffa6792299a0066f496cc92`

## Config

```yaml
budgets:
- 128
- 256
- 512
- 1024
- 2048
- 4096
- 8192
chunkings:
- chunk_tokens: 64
  method: fixed
  name: fixed-64
- chunk_tokens: 128
  method: fixed
  name: fixed-128
- chunk_tokens: 256
  method: fixed
  name: fixed-256
- chunk_tokens: 512
  method: fixed
  name: fixed-512
- chunk_tokens: 1024
  method: fixed
  name: fixed-1024
- max_tokens: 512
  method: section_aware
  name: section-aware
- child_tokens: 128
  max_tokens: 512
  method: small_to_big
  name: small-to-big
dataset:
  name: nq
  splits:
  - dev
embedders:
- bge-small
- nomic
fixed_k:
- 1
- 5
- 10
kind: grid
pipelines:
- hybrid-rerank
- hybrid
- vector
- bm25
rerank_depth: 30
rrf_k: 60
run_name: grid
scopes:
- collection
- document
search_depth: 1000
seed: 0
side_top_n: 5
top_n: 8
```

## Models

| role | name | model | revision | input limit |
|---|---|---|---|---|
| embedder | bge-small | BAAI/bge-small-en-v1.5 | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` | 512 tokens |
| embedder | nomic | nomic-ai/nomic-embed-text-v1.5 | `e9b6763023c676ca8431644204f50c2b100d9aab` | 8192 tokens |
| reranker | gte-reranker-modernbert-base | Alibaba-NLP/gte-reranker-modernbert-base | `f7481e6055501a30fb19d090657df9ec1f79ab2c` | n/a |

## Dataset

| split | sha256 |
|---|---|
| dev | `633358d753e7a5a534418ab7127957b0c64e98a2bb5ccf41f01879a2f781f4c9` |

## Questions

| query type | n |
|---|---|
| precise | 500 |
| context | 500 |
| mixed | 0 |
| total | 1000 |

## Production line: hybrid, then the reranker over the fused top 30, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.1244, fixed-1024 0.9312, section-aware 0.0092.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.3950 | 0.7090 | 0.8150 | 0.1522 | 0.3599 | 0.4676 |
| fixed-128 | 0.4410 | 0.7910 | 0.8780 | 0.2561 | 0.5574 | 0.6742 |
| fixed-256 | 0.5270 | 0.8630 | 0.9270 | 0.4002 | 0.7530 | 0.8497 |
| fixed-512 | 0.6540 | 0.9170 | 0.9650 | 0.5973 | 0.8872 | 0.9445 |
| fixed-1024 | 0.7520 | 0.9500 | 0.9750 | 0.7370 | 0.9430 | 0.9710 |
| section-aware | 0.5990 | 0.8890 | 0.9380 | 0.5985 | 0.8875 | 0.9370 |
| small-to-big | 0.5650 | 0.8640 | 0.9190 | 0.5645 | 0.8630 | 0.9180 |

## Production line: hybrid, then the reranker over the fused top 30, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.4000 | 0.7180 | 0.8210 | 0.1544 | 0.3648 | 0.4756 |
| fixed-128 | 0.4440 | 0.8020 | 0.8770 | 0.2558 | 0.5654 | 0.6748 |
| fixed-256 | 0.5300 | 0.8580 | 0.9330 | 0.4027 | 0.7515 | 0.8538 |
| fixed-512 | 0.6590 | 0.9200 | 0.9710 | 0.6013 | 0.8897 | 0.9505 |
| fixed-1024 | 0.7540 | 0.9530 | 0.9790 | 0.7390 | 0.9455 | 0.9750 |
| section-aware | 0.6010 | 0.8950 | 0.9400 | 0.6005 | 0.8935 | 0.9390 |
| small-to-big | 0.5630 | 0.8560 | 0.9210 | 0.5625 | 0.8550 | 0.9200 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.1244, fixed-1024 0.9312, section-aware 0.0092.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.3120 | 0.6420 | 0.7650 | 0.1195 | 0.3210 | 0.4338 |
| fixed-128 | 0.3910 | 0.7330 | 0.8510 | 0.2326 | 0.5090 | 0.6374 |
| fixed-256 | 0.4420 | 0.8210 | 0.9130 | 0.3415 | 0.7103 | 0.8220 |
| fixed-512 | 0.5050 | 0.8690 | 0.9450 | 0.4623 | 0.8382 | 0.9242 |
| fixed-1024 | 0.5720 | 0.8920 | 0.9580 | 0.5580 | 0.8850 | 0.9540 |
| section-aware | 0.4280 | 0.7860 | 0.8870 | 0.4275 | 0.7845 | 0.8855 |
| small-to-big | 0.3710 | 0.7760 | 0.8750 | 0.3705 | 0.7750 | 0.8740 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.3230 | 0.6640 | 0.7790 | 0.1253 | 0.3332 | 0.4388 |
| fixed-128 | 0.3890 | 0.7390 | 0.8580 | 0.2252 | 0.5135 | 0.6358 |
| fixed-256 | 0.4470 | 0.8130 | 0.9080 | 0.3478 | 0.7043 | 0.8212 |
| fixed-512 | 0.5110 | 0.8730 | 0.9420 | 0.4638 | 0.8410 | 0.9235 |
| fixed-1024 | 0.5730 | 0.9010 | 0.9610 | 0.5590 | 0.8925 | 0.9570 |
| section-aware | 0.4640 | 0.8160 | 0.8990 | 0.4635 | 0.8150 | 0.8980 |
| small-to-big | 0.4190 | 0.8020 | 0.8910 | 0.4185 | 0.8010 | 0.8900 |

## Ablation: vector search only, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.1244, fixed-1024 0.9312, section-aware 0.0092.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.3800 | 0.7180 | 0.8080 | 0.1499 | 0.3646 | 0.4651 |
| fixed-128 | 0.4420 | 0.7840 | 0.8600 | 0.2649 | 0.5519 | 0.6614 |
| fixed-256 | 0.5020 | 0.8420 | 0.9100 | 0.3918 | 0.7426 | 0.8360 |
| fixed-512 | 0.5700 | 0.8680 | 0.9260 | 0.5263 | 0.8352 | 0.9055 |
| fixed-1024 | 0.6420 | 0.8840 | 0.9260 | 0.6275 | 0.8750 | 0.9190 |
| section-aware | 0.2650 | 0.7910 | 0.8760 | 0.2645 | 0.7895 | 0.8745 |
| small-to-big | 0.2890 | 0.8140 | 0.9020 | 0.2890 | 0.8130 | 0.9005 |

## Ablation: vector search only, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.4400 | 0.7640 | 0.8460 | 0.1754 | 0.4010 | 0.5030 |
| fixed-128 | 0.5060 | 0.8290 | 0.8980 | 0.3023 | 0.5949 | 0.7017 |
| fixed-256 | 0.5740 | 0.8820 | 0.9400 | 0.4480 | 0.7740 | 0.8662 |
| fixed-512 | 0.6120 | 0.9150 | 0.9540 | 0.5583 | 0.8827 | 0.9360 |
| fixed-1024 | 0.6390 | 0.9160 | 0.9520 | 0.6245 | 0.9075 | 0.9480 |
| section-aware | 0.5670 | 0.8820 | 0.9320 | 0.5665 | 0.8805 | 0.9310 |
| small-to-big | 0.5410 | 0.8770 | 0.9370 | 0.5410 | 0.8760 | 0.9360 |

## Ablation: BM25 only

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.2010 | 0.4910 | 0.6220 | 0.0743 | 0.2246 | 0.3212 |
| fixed-128 | 0.2660 | 0.5770 | 0.7130 | 0.1613 | 0.3794 | 0.5058 |
| fixed-256 | 0.3270 | 0.6850 | 0.7870 | 0.2533 | 0.5833 | 0.6910 |
| fixed-512 | 0.4070 | 0.7810 | 0.8570 | 0.3673 | 0.7433 | 0.8333 |
| fixed-1024 | 0.4750 | 0.8350 | 0.9090 | 0.4640 | 0.8270 | 0.9055 |
| section-aware | 0.3250 | 0.6880 | 0.7850 | 0.3245 | 0.6870 | 0.7840 |
| small-to-big | 0.2990 | 0.6390 | 0.7700 | 0.2985 | 0.6385 | 0.7695 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
