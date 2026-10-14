# R6 - nq grid, production line and ablations: short-answer span recall

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

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.4256 | 0.4256 | 0.0000 |
| fixed-64 | 256 | 0.5314 | 0.5314 | 0.0000 |
| fixed-64 | 512 | 0.6192 | 0.6192 | 0.0000 |
| fixed-64 | 1024 | 0.6192† | 0.6942 | 1.0000 |
| fixed-64 | 2048 | 0.6192† | 0.7351§ | 1.0000 |
| fixed-64 | 4096 | 0.6192† | 0.8060§ | 1.0000 |
| fixed-64 | 8192 | 0.6192† | 0.8314§ | 1.0000 |
| fixed-128 | 128 | 0.4181 | 0.4181 | 0.0000 |
| fixed-128 | 256 | 0.5776 | 0.5776 | 0.0000 |
| fixed-128 | 512 | 0.7071 | 0.7071 | 0.0000 |
| fixed-128 | 1024 | 0.7739 | 0.7739§ | 0.0021 |
| fixed-128 | 2048 | 0.7739† | 0.8318§ | 1.0000 |
| fixed-128 | 4096 | 0.7739† | 0.8649§ | 1.0000 |
| fixed-128 | 8192 | 0.7739† | 0.9122§ | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.5205 | 0.5205 | 0.0000 |
| fixed-256 | 512 | 0.6867§ | 0.6867§ | 0.0000 |
| fixed-256 | 1024 | 0.8031§ | 0.8031§ | 0.0000 |
| fixed-256 | 2048 | 0.8925 | 0.8925§ | 0.0207 |
| fixed-256 | 4096 | 0.8925† | 0.9388§ | 1.0000 |
| fixed-256 | 8192 | 0.8925† | 0.9615§ | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6751§ | 0.6751§ | 0.0000 |
| fixed-512 | 1024 | 0.8206§ | 0.8206§ | 0.0000 |
| fixed-512 | 2048 | 0.9020§ | 0.9020§ | 0.0041 |
| fixed-512 | 4096 | 0.9462 | 0.9462§ | 0.1532 |
| fixed-512 | 8192 | 0.9462† | 0.9710§ | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7781§ | 0.7781§ | 0.0021 |
| fixed-1024 | 2048 | 0.8793§ | 0.8793§ | 0.0041 |
| fixed-1024 | 4096 | 0.9311§ | 0.9311§ | 0.0166 |
| fixed-1024 | 8192 | 0.9683 | 0.9683§ | 0.4348 |
| section-aware | 128 | 0.0642§ | 0.0642§ | 0.0787 |
| section-aware | 256 | 0.2422§ | 0.2422§ | 0.1159 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.1532 |
| section-aware | 1024 | 0.8571§ | 0.8571§ | 0.3892 |
| section-aware | 2048 | 0.9193†§ | 0.9193§ | 0.8489 |
| section-aware | 4096 | 0.9317† | 0.9420§ | 1.0000 |
| section-aware | 8192 | 0.9317† | 0.9648§ | 1.0000 |
| small-to-big | 128 | 0.4605§ | 0.4605§ | 0.0000 |
| small-to-big | 256 | 0.5982§ | 0.5982§ | 0.0269 |
| small-to-big | 512 | 0.6973§ | 0.6973§ | 0.0663 |
| small-to-big | 1024 | 0.8157§ | 0.8157§ | 0.2692 |
| small-to-big | 2048 | 0.8986†§ | 0.8986§ | 0.7909 |
| small-to-big | 4096 | 0.9193† | 0.9337§ | 1.0000 |
| small-to-big | 8192 | 0.9193† | 0.9420§ | 1.0000 |

## Production line: hybrid, then the reranker over the fused top 30, nomic

No chunk exceeds nomic's 8192-token input.

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.4212 | 0.4212 | 0.0000 |
| fixed-64 | 256 | 0.5349 | 0.5349 | 0.0000 |
| fixed-64 | 512 | 0.6159 | 0.6159 | 0.0000 |
| fixed-64 | 1024 | 0.6159† | 0.6825 | 1.0000 |
| fixed-64 | 2048 | 0.6159† | 0.7279§ | 1.0000 |
| fixed-64 | 4096 | 0.6159† | 0.8079§ | 1.0000 |
| fixed-64 | 8192 | 0.6159† | 0.8699§ | 1.0000 |
| fixed-128 | 128 | 0.4098 | 0.4098 | 0.0000 |
| fixed-128 | 256 | 0.5697 | 0.5697 | 0.0000 |
| fixed-128 | 512 | 0.7012 | 0.7012 | 0.0000 |
| fixed-128 | 1024 | 0.7790 | 0.7790§ | 0.0021 |
| fixed-128 | 2048 | 0.7790† | 0.8369§ | 1.0000 |
| fixed-128 | 4096 | 0.7790† | 0.8760§ | 1.0000 |
| fixed-128 | 8192 | 0.7790† | 0.9194§ | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.5267 | 0.5267 | 0.0000 |
| fixed-256 | 512 | 0.6867§ | 0.6867§ | 0.0000 |
| fixed-256 | 1024 | 0.7990§ | 0.7990§ | 0.0000 |
| fixed-256 | 2048 | 0.8860 | 0.8860§ | 0.0104 |
| fixed-256 | 4096 | 0.8860† | 0.9429§ | 1.0000 |
| fixed-256 | 8192 | 0.8860† | 0.9719§ | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6710§ | 0.6710§ | 0.0000 |
| fixed-512 | 1024 | 0.8165§ | 0.8165§ | 0.0000 |
| fixed-512 | 2048 | 0.9041§ | 0.9041§ | 0.0000 |
| fixed-512 | 4096 | 0.9503 | 0.9503§ | 0.1470 |
| fixed-512 | 8192 | 0.9503† | 0.9731§ | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.7822§ | 0.7822§ | 0.0021 |
| fixed-1024 | 2048 | 0.8814§ | 0.8814§ | 0.0021 |
| fixed-1024 | 4096 | 0.9352§ | 0.9352§ | 0.0041 |
| fixed-1024 | 8192 | 0.9731 | 0.9731§ | 0.4079 |
| section-aware | 128 | 0.0600§ | 0.0600§ | 0.0021 |
| section-aware | 256 | 0.2402§ | 0.2402§ | 0.0041 |
| section-aware | 512 | 0.7205§ | 0.7205§ | 0.0269 |
| section-aware | 1024 | 0.8613§ | 0.8613§ | 0.1366 |
| section-aware | 2048 | 0.9275†§ | 0.9275§ | 0.6936 |
| section-aware | 4096 | 0.9400† | 0.9482§ | 1.0000 |
| section-aware | 8192 | 0.9400† | 0.9731§ | 1.0000 |
| small-to-big | 128 | 0.4633§ | 0.4633§ | 0.0021 |
| small-to-big | 256 | 0.6044§ | 0.6044§ | 0.0021 |
| small-to-big | 512 | 0.6952§ | 0.6952§ | 0.0207 |
| small-to-big | 1024 | 0.8199§ | 0.8199§ | 0.1429 |
| small-to-big | 2048 | 0.8965†§ | 0.8965§ | 0.6708 |
| small-to-big | 4096 | 0.9255† | 0.9400§ | 1.0000 |
| small-to-big | 8192 | 0.9255† | 0.9565§ | 1.0000 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.1244, fixed-1024 0.9312, section-aware 0.0092.

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.2961 | 0.2961 | 0.0000 |
| fixed-64 | 256 | 0.4288 | 0.4288 | 0.0000 |
| fixed-64 | 512 | 0.5498 | 0.5498 | 0.0000 |
| fixed-64 | 1024 | 0.5498† | 0.6542 | 1.0000 |
| fixed-64 | 2048 | 0.5498† | 0.7351 | 1.0000 |
| fixed-64 | 4096 | 0.5498† | 0.8060 | 1.0000 |
| fixed-64 | 8192 | 0.5498† | 0.8314 | 1.0000 |
| fixed-128 | 128 | 0.3481 | 0.3481 | 0.0000 |
| fixed-128 | 256 | 0.4709 | 0.4709 | 0.0000 |
| fixed-128 | 512 | 0.5969 | 0.5969 | 0.0000 |
| fixed-128 | 1024 | 0.7452 | 0.7452 | 0.0041 |
| fixed-128 | 2048 | 0.7452† | 0.8050 | 1.0000 |
| fixed-128 | 4096 | 0.7452† | 0.8649 | 1.0000 |
| fixed-128 | 8192 | 0.7452† | 0.9122 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4182 | 0.4182 | 0.0000 |
| fixed-256 | 512 | 0.5930 | 0.5930 | 0.0000 |
| fixed-256 | 1024 | 0.7357 | 0.7357 | 0.0000 |
| fixed-256 | 2048 | 0.8469 | 0.8469 | 0.0207 |
| fixed-256 | 4096 | 0.8469† | 0.9185 | 1.0000 |
| fixed-256 | 8192 | 0.8469† | 0.9615 | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.5379 | 0.5379 | 0.0000 |
| fixed-512 | 1024 | 0.7305 | 0.7305 | 0.0000 |
| fixed-512 | 2048 | 0.8427 | 0.8427 | 0.0041 |
| fixed-512 | 4096 | 0.9181 | 0.9181 | 0.1532 |
| fixed-512 | 8192 | 0.9181† | 0.9503 | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.6145 | 0.6145 | 0.0021 |
| fixed-1024 | 2048 | 0.7867 | 0.7867 | 0.0062 |
| fixed-1024 | 4096 | 0.8834 | 0.8834 | 0.0228 |
| fixed-1024 | 8192 | 0.9393 | 0.9393 | 0.4472 |
| section-aware | 128 | 0.0455 | 0.0455 | 0.0704 |
| section-aware | 256 | 0.2008 | 0.2008 | 0.1304 |
| section-aware | 512 | 0.5673 | 0.5673 | 0.1615 |
| section-aware | 1024 | 0.7412 | 0.7412 | 0.3499 |
| section-aware | 2048 | 0.8323† | 0.8344 | 0.8489 |
| section-aware | 4096 | 0.8799† | 0.9089 | 1.0000 |
| section-aware | 8192 | 0.8799† | 0.9462 | 1.0000 |
| small-to-big | 128 | 0.3015 | 0.3015 | 0.0021 |
| small-to-big | 256 | 0.4880 | 0.4880 | 0.0352 |
| small-to-big | 512 | 0.5709 | 0.5709 | 0.0704 |
| small-to-big | 1024 | 0.7411 | 0.7411 | 0.2774 |
| small-to-big | 2048 | 0.8530† | 0.8563 | 0.8012 |
| small-to-big | 4096 | 0.8758† | 0.9151 | 1.0000 |
| small-to-big | 8192 | 0.8758† | 0.9400 | 1.0000 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, nomic

No chunk exceeds nomic's 8192-token input.

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.3170 | 0.3170 | 0.0000 |
| fixed-64 | 256 | 0.4385 | 0.4385 | 0.0000 |
| fixed-64 | 512 | 0.5601 | 0.5601 | 0.0000 |
| fixed-64 | 1024 | 0.5601† | 0.6507 | 1.0000 |
| fixed-64 | 2048 | 0.5601† | 0.7279 | 1.0000 |
| fixed-64 | 4096 | 0.5601† | 0.8079 | 1.0000 |
| fixed-64 | 8192 | 0.5601† | 0.8699 | 1.0000 |
| fixed-128 | 128 | 0.3367 | 0.3367 | 0.0000 |
| fixed-128 | 256 | 0.4676 | 0.4676 | 0.0000 |
| fixed-128 | 512 | 0.6071 | 0.6071 | 0.0000 |
| fixed-128 | 1024 | 0.7173 | 0.7173 | 0.0041 |
| fixed-128 | 2048 | 0.7173† | 0.8104 | 1.0000 |
| fixed-128 | 4096 | 0.7173† | 0.8760 | 1.0000 |
| fixed-128 | 8192 | 0.7173† | 0.9194 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4320 | 0.4320 | 0.0000 |
| fixed-256 | 512 | 0.5883 | 0.5883 | 0.0000 |
| fixed-256 | 1024 | 0.7258 | 0.7258 | 0.0000 |
| fixed-256 | 2048 | 0.8615 | 0.8615 | 0.0166 |
| fixed-256 | 4096 | 0.8615† | 0.9248 | 1.0000 |
| fixed-256 | 8192 | 0.8615† | 0.9719 | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.5089 | 0.5089 | 0.0000 |
| fixed-512 | 1024 | 0.7387 | 0.7387 | 0.0000 |
| fixed-512 | 2048 | 0.8438 | 0.8438 | 0.0000 |
| fixed-512 | 4096 | 0.9201 | 0.9201 | 0.1366 |
| fixed-512 | 8192 | 0.9201† | 0.9648 | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.5938 | 0.5938 | 0.0000 |
| fixed-1024 | 2048 | 0.7719 | 0.7719 | 0.0021 |
| fixed-1024 | 4096 | 0.8917 | 0.8917 | 0.0104 |
| fixed-1024 | 8192 | 0.9441 | 0.9441 | 0.3872 |
| section-aware | 128 | 0.0476 | 0.0476 | 0.0021 |
| section-aware | 256 | 0.2029 | 0.2029 | 0.0062 |
| section-aware | 512 | 0.5466 | 0.5466 | 0.0228 |
| section-aware | 1024 | 0.7516 | 0.7516 | 0.1139 |
| section-aware | 2048 | 0.8406† | 0.8447 | 0.6729 |
| section-aware | 4096 | 0.8861† | 0.9172 | 1.0000 |
| section-aware | 8192 | 0.8861† | 0.9586 | 1.0000 |
| small-to-big | 128 | 0.3530 | 0.3530 | 0.0021 |
| small-to-big | 256 | 0.4902 | 0.4902 | 0.0021 |
| small-to-big | 512 | 0.5879 | 0.5879 | 0.0145 |
| small-to-big | 1024 | 0.7439 | 0.7439 | 0.1429 |
| small-to-big | 2048 | 0.8654† | 0.8666 | 0.6749 |
| small-to-big | 4096 | 0.8861† | 0.9110 | 1.0000 |
| small-to-big | 8192 | 0.8861† | 0.9565 | 1.0000 |

## Ablation: vector search only, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.1244, fixed-1024 0.9312, section-aware 0.0092.

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.3917 | 0.3917 | 0.0000 |
| fixed-64 | 256 | 0.4967 | 0.4967 | 0.0000 |
| fixed-64 | 512 | 0.5993 | 0.5993 | 0.0000 |
| fixed-64 | 1024 | 0.5993† | 0.6955 | 1.0000 |
| fixed-64 | 2048 | 0.5993† | 0.7562 | 1.0000 |
| fixed-64 | 4096 | 0.5993† | 0.8028 | 1.0000 |
| fixed-64 | 8192 | 0.5993† | 0.8547 | 1.0000 |
| fixed-128 | 128 | 0.3742 | 0.3742 | 0.0000 |
| fixed-128 | 256 | 0.5310 | 0.5310 | 0.0000 |
| fixed-128 | 512 | 0.6725 | 0.6725 | 0.0000 |
| fixed-128 | 1024 | 0.7664 | 0.7664 | 0.0000 |
| fixed-128 | 2048 | 0.7664† | 0.8371 | 1.0000 |
| fixed-128 | 4096 | 0.7664† | 0.8822 | 1.0000 |
| fixed-128 | 8192 | 0.7664† | 0.9220 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.4585 | 0.4585 | 0.0000 |
| fixed-256 | 512 | 0.6169 | 0.6169 | 0.0000 |
| fixed-256 | 1024 | 0.7682 | 0.7682 | 0.0000 |
| fixed-256 | 2048 | 0.8653 | 0.8653 | 0.0166 |
| fixed-256 | 4096 | 0.8653† | 0.9160 | 1.0000 |
| fixed-256 | 8192 | 0.8653† | 0.9471 | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.5648 | 0.5648 | 0.0000 |
| fixed-512 | 1024 | 0.7267 | 0.7267 | 0.0000 |
| fixed-512 | 2048 | 0.8592 | 0.8592 | 0.0041 |
| fixed-512 | 4096 | 0.9213 | 0.9213 | 0.1532 |
| fixed-512 | 8192 | 0.9213† | 0.9586 | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.6621 | 0.6621 | 0.0021 |
| fixed-1024 | 2048 | 0.7992 | 0.7992 | 0.0062 |
| fixed-1024 | 4096 | 0.8882 | 0.8882 | 0.0207 |
| fixed-1024 | 8192 | 0.9331 | 0.9331 | 0.4928 |
| section-aware | 128 | 0.0600 | 0.0600 | 0.1118 |
| section-aware | 256 | 0.2174 | 0.2174 | 0.2070 |
| section-aware | 512 | 0.5921 | 0.5921 | 0.2402 |
| section-aware | 1024 | 0.7723 | 0.7723 | 0.4700 |
| section-aware | 2048 | 0.8634† | 0.8654 | 0.9089 |
| section-aware | 4096 | 0.8799† | 0.9151 | 1.0000 |
| section-aware | 8192 | 0.8799† | 0.9607 | 1.0000 |
| small-to-big | 128 | 0.2871 | 0.2871 | 0.0269 |
| small-to-big | 256 | 0.5110 | 0.5110 | 0.0952 |
| small-to-big | 512 | 0.5920 | 0.5920 | 0.1366 |
| small-to-big | 1024 | 0.7681 | 0.7681 | 0.3375 |
| small-to-big | 2048 | 0.8675† | 0.8696 | 0.8323 |
| small-to-big | 4096 | 0.8903† | 0.9192 | 1.0000 |
| small-to-big | 8192 | 0.8903† | 0.9565 | 1.0000 |

## Ablation: vector search only, nomic

No chunk exceeds nomic's 8192-token input.

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.4328 | 0.4328 | 0.0000 |
| fixed-64 | 256 | 0.5712 | 0.5712 | 0.0000 |
| fixed-64 | 512 | 0.6605 | 0.6605 | 0.0000 |
| fixed-64 | 1024 | 0.6605† | 0.7265 | 1.0000 |
| fixed-64 | 2048 | 0.6605† | 0.7784 | 1.0000 |
| fixed-64 | 4096 | 0.6605† | 0.8562 | 1.0000 |
| fixed-64 | 8192 | 0.6605† | 0.8929 | 1.0000 |
| fixed-128 | 128 | 0.4304 | 0.4304 | 0.0000 |
| fixed-128 | 256 | 0.6069 | 0.6069 | 0.0000 |
| fixed-128 | 512 | 0.7305 | 0.7305 | 0.0000 |
| fixed-128 | 1024 | 0.8076 | 0.8076 | 0.0000 |
| fixed-128 | 2048 | 0.8076† | 0.8745 | 1.0000 |
| fixed-128 | 4096 | 0.8076† | 0.9086 | 1.0000 |
| fixed-128 | 8192 | 0.8076† | 0.9373 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.5566 | 0.5566 | 0.0000 |
| fixed-256 | 512 | 0.7269 | 0.7269 | 0.0000 |
| fixed-256 | 1024 | 0.8383 | 0.8383 | 0.0000 |
| fixed-256 | 2048 | 0.8912 | 0.8912 | 0.0062 |
| fixed-256 | 4096 | 0.8912† | 0.9450 | 1.0000 |
| fixed-256 | 8192 | 0.8912† | 0.9719 | 1.0000 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.6097 | 0.6097 | 0.0000 |
| fixed-512 | 1024 | 0.7909 | 0.7909 | 0.0000 |
| fixed-512 | 2048 | 0.8876 | 0.8876 | 0.0000 |
| fixed-512 | 4096 | 0.9379 | 0.9379 | 0.1077 |
| fixed-512 | 8192 | 0.9379† | 0.9689 | 1.0000 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.6435 | 0.6435 | 0.0000 |
| fixed-1024 | 2048 | 0.8089 | 0.8089 | 0.0000 |
| fixed-1024 | 4096 | 0.9083 | 0.9083 | 0.0041 |
| fixed-1024 | 8192 | 0.9580 | 0.9580 | 0.4120 |
| section-aware | 128 | 0.0642 | 0.0642 | 0.0021 |
| section-aware | 256 | 0.2422 | 0.2422 | 0.0021 |
| section-aware | 512 | 0.6605 | 0.6605 | 0.0083 |
| section-aware | 1024 | 0.8344 | 0.8344 | 0.0828 |
| section-aware | 2048 | 0.9193† | 0.9193 | 0.5880 |
| section-aware | 4096 | 0.9379† | 0.9545 | 1.0000 |
| section-aware | 8192 | 0.9379† | 0.9710 | 1.0000 |
| small-to-big | 128 | 0.4612 | 0.4612 | 0.0000 |
| small-to-big | 256 | 0.6314 | 0.6314 | 0.0000 |
| small-to-big | 512 | 0.6946 | 0.6946 | 0.0041 |
| small-to-big | 1024 | 0.8364 | 0.8364 | 0.0621 |
| small-to-big | 2048 | 0.9110† | 0.9110 | 0.5818 |
| small-to-big | 4096 | 0.9234† | 0.9390 | 1.0000 |
| small-to-big | 8192 | 0.9234† | 0.9627 | 1.0000 |

## Ablation: BM25 only

### Short-answer span recall, collection search, n = 483 precise questions with a short-answer span

The same packing as R2 (production view: top-N cap 8; fair view: no cap) scored against the short-answer spans instead of the long-answer paragraph.

| chunking | budget | production short recall | fair short recall | cap binds |
|---|---|---|---|---|
| fixed-64 | 128 | 0.1853 | 0.1853 | 0.0000 |
| fixed-64 | 256 | 0.2731 | 0.2731 | 0.0000 |
| fixed-64 | 512 | 0.3868 | 0.3868 | 0.0000 |
| fixed-64 | 1024 | 0.3868† | 0.4866 | 1.0000 |
| fixed-64 | 2048 | 0.3868† | 0.5805 | 1.0000 |
| fixed-64 | 4096 | 0.3868† | 0.6311 | 1.0000 |
| fixed-64 | 8192 | 0.3868† | 0.7031 | 1.0000 |
| fixed-128 | 128 | 0.2355 | 0.2355 | 0.0000 |
| fixed-128 | 256 | 0.3472 | 0.3472 | 0.0000 |
| fixed-128 | 512 | 0.4795 | 0.4795 | 0.0000 |
| fixed-128 | 1024 | 0.5615 | 0.5615 | 0.0041 |
| fixed-128 | 2048 | 0.5615† | 0.6617 | 1.0000 |
| fixed-128 | 4096 | 0.5615† | 0.7258 | 1.0000 |
| fixed-128 | 8192 | 0.5615† | 0.8115 | 1.0000 |
| fixed-256 | 128 | n/a | n/a | n/a |
| fixed-256 | 256 | 0.3106 | 0.3106 | 0.0000 |
| fixed-256 | 512 | 0.4890 | 0.4890 | 0.0000 |
| fixed-256 | 1024 | 0.5922 | 0.5922 | 0.0000 |
| fixed-256 | 2048 | 0.7053 | 0.7053 | 0.0083 |
| fixed-256 | 4096 | 0.7053† | 0.8042 | 0.9979 |
| fixed-256 | 8192 | 0.7053† | 0.8597 | 0.9979 |
| fixed-512 | 128 | n/a | n/a | n/a |
| fixed-512 | 256 | n/a | n/a | n/a |
| fixed-512 | 512 | 0.4137 | 0.4137 | 0.0000 |
| fixed-512 | 1024 | 0.6083 | 0.6083 | 0.0000 |
| fixed-512 | 2048 | 0.7470 | 0.7470 | 0.0021 |
| fixed-512 | 4096 | 0.8385 | 0.8385 | 0.0704 |
| fixed-512 | 8192 | 0.8385† | 0.8820 | 0.9979 |
| fixed-1024 | 128 | n/a | n/a | n/a |
| fixed-1024 | 256 | n/a | n/a | n/a |
| fixed-1024 | 512 | n/a | n/a | n/a |
| fixed-1024 | 1024 | 0.4696 | 0.4696 | 0.0000 |
| fixed-1024 | 2048 | 0.6766 | 0.6766 | 0.0041 |
| fixed-1024 | 4096 | 0.8071 | 0.8071 | 0.0062 |
| fixed-1024 | 8192 | 0.9000 | 0.9000 | 0.2754 |
| section-aware | 128 | 0.0352 | 0.0352 | 0.0041 |
| section-aware | 256 | 0.1698 | 0.1698 | 0.0083 |
| section-aware | 512 | 0.4099 | 0.4099 | 0.0166 |
| section-aware | 1024 | 0.5859 | 0.5859 | 0.1491 |
| section-aware | 2048 | 0.7246† | 0.7246 | 0.6480 |
| section-aware | 4096 | 0.7764† | 0.8116 | 0.9979 |
| section-aware | 8192 | 0.7764† | 0.8675 | 0.9979 |
| small-to-big | 128 | 0.2402 | 0.2402 | 0.0000 |
| small-to-big | 256 | 0.3349 | 0.3349 | 0.0041 |
| small-to-big | 512 | 0.4080 | 0.4080 | 0.0311 |
| small-to-big | 1024 | 0.5507 | 0.5507 | 0.1698 |
| small-to-big | 2048 | 0.6923† | 0.6943 | 0.6749 |
| small-to-big | 4096 | 0.7557† | 0.8029 | 0.9979 |
| small-to-big | 8192 | 0.7557† | 0.8592 | 0.9979 |

Precise questions whose short answers are yes or no only have no short-answer span and stay out of these means; they count in R2 and R3.
n/a: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
§: production line only; for at least one question, packing went past the reranked top 30 into the unreranked tail, which continues in fused (hybrid) order.
