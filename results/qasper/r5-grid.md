# R5 - qasper grid, production line and ablations: pipeline x embedder x chunking

Config hash: `46651182bfedaccb9c330b18a924d2d702dc741790be26d25893cab39e4f32a2`

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
  name: qasper
  splits:
  - dev
  - test
embedders:
- bge-small
- nomic
fixed_k:
- 1
- 5
- 10
kind: grid
pipelines:
- production
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
| dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| query type | n |
|---|---|
| precise | 1317 |
| context | 404 |
| mixed | 476 |
| total | 2197 |

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.0526 | 0.0647 | 0.0526 | 0.0647 | 0.0000 | 0.0109 | 0.0109 |
| production | bge-small | fixed-128 | 0.0416 | 0.0556 | 0.0416 | 0.0556 | 0.0000 | 0.0123 | 0.0123 |
| production | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | section-aware | 0.0313 | 0.0284 | 0.0313 | 0.0284 | 0.0810 ‡ | 0.5849 | 0.5849 |
| production | bge-small | small-to-big | 0.0708 | 0.0856 | 0.0708 | 0.0856 | 0.0000 | 0.2239 | 0.2249 |
| production | nomic | fixed-64 | 0.0524 | 0.0630 | 0.0524 | 0.0630 | 0.0000 | 0.0091 | 0.0091 |
| production | nomic | fixed-128 | 0.0439 | 0.0569 | 0.0439 | 0.0569 | 0.0000 | 0.0141 | 0.0141 |
| production | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | section-aware | 0.0315 | 0.0292 | 0.0315 | 0.0292 | 0.0000 | 0.5403 | 0.5403 |
| production | nomic | small-to-big | 0.0690 | 0.0839 | 0.0690 | 0.0839 | 0.0000 | 0.2358 | 0.2362 |
| hybrid | bge-small | fixed-64 | 0.0453 | 0.0525 | 0.0453 | 0.0525 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.0442 | 0.0516 | 0.0442 | 0.0516 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.0207 | 0.0203 | 0.0207 | 0.0203 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.0465 | 0.0588 | 0.0465 | 0.0588 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.0451 | 0.0546 | 0.0451 | 0.0546 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.0457 | 0.0598 | 0.0457 | 0.0598 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.0199 | 0.0201 | 0.0199 | 0.0201 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.0530 | 0.0666 | 0.0530 | 0.0666 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0389 | 0.0461 | 0.0389 | 0.0460 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.0349 | 0.0420 | 0.0349 | 0.0420 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.0193 | 0.0173 | 0.0193 | 0.0173 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.0394 | 0.0462 | 0.0394 | 0.0462 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0454 | 0.0545 | 0.0454 | 0.0545 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.0452 | 0.0576 | 0.0452 | 0.0576 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.0215 | 0.0199 | 0.0215 | 0.0199 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.0531 | 0.0631 | 0.0531 | 0.0631 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0351 | 0.0431 | 0.0351 | 0.0431 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.0388 | 0.0467 | 0.0388 | 0.0467 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.0167 | 0.0164 | 0.0167 | 0.0164 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.0411 | 0.0531 | 0.0411 | 0.0531 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.0863 | 0.0521 | 0.0863 | 0.0521 | 0.0000 | 0.0255 | 0.0255 |
| production | bge-small | fixed-128 | 0.0935 | 0.0610 | 0.0935 | 0.0610 | 0.0000 | 0.0278 | 0.0278 |
| production | bge-small | fixed-256 | 0.0632 | 0.0427 | 0.0632 | 0.0427 | 0.0000 | 0.0237 | 0.0241 |
| production | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | section-aware | 0.0619 | 0.0357 | 0.0619 | 0.0357 | 0.0810 ‡ | 0.6004 | 0.6004 |
| production | bge-small | small-to-big | 0.1080 | 0.0646 | 0.1080 | 0.0645 | 0.0000 | 0.4706 | 0.4807 |
| production | nomic | fixed-64 | 0.0879 | 0.0536 | 0.0879 | 0.0536 | 0.0000 | 0.0209 | 0.0209 |
| production | nomic | fixed-128 | 0.0936 | 0.0603 | 0.0936 | 0.0603 | 0.0000 | 0.0296 | 0.0296 |
| production | nomic | fixed-256 | 0.0620 | 0.0425 | 0.0620 | 0.0425 | 0.0000 | 0.0232 | 0.0232 |
| production | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | section-aware | 0.0634 | 0.0365 | 0.0634 | 0.0365 | 0.0000 | 0.5844 | 0.5844 |
| production | nomic | small-to-big | 0.1066 | 0.0643 | 0.1066 | 0.0643 | 0.0000 | 0.4984 | 0.4989 |
| hybrid | bge-small | fixed-64 | 0.0708 | 0.0422 | 0.0708 | 0.0422 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.0713 | 0.0455 | 0.0713 | 0.0455 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.0585 | 0.0399 | 0.0585 | 0.0399 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.0421 | 0.0235 | 0.0421 | 0.0235 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.0697 | 0.0467 | 0.0697 | 0.0466 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.0720 | 0.0423 | 0.0720 | 0.0423 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.0772 | 0.0486 | 0.0772 | 0.0486 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.0630 | 0.0436 | 0.0630 | 0.0436 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.0416 | 0.0243 | 0.0416 | 0.0243 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.0804 | 0.0517 | 0.0804 | 0.0517 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0611 | 0.0355 | 0.0611 | 0.0355 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.0586 | 0.0372 | 0.0586 | 0.0371 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.0498 | 0.0351 | 0.0498 | 0.0351 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.0347 | 0.0183 | 0.0347 | 0.0183 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.0588 | 0.0374 | 0.0588 | 0.0373 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0670 | 0.0398 | 0.0670 | 0.0398 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.0689 | 0.0447 | 0.0689 | 0.0447 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.0553 | 0.0390 | 0.0553 | 0.0390 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.0407 | 0.0230 | 0.0407 | 0.0230 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.0756 | 0.0476 | 0.0756 | 0.0476 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0610 | 0.0372 | 0.0610 | 0.0372 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.0645 | 0.0402 | 0.0645 | 0.0402 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.0552 | 0.0363 | 0.0552 | 0.0363 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.0389 | 0.0214 | 0.0389 | 0.0214 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.0613 | 0.0402 | 0.0613 | 0.0402 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.1245 | 0.0383 | 0.1245 | 0.0382 | 0.0000 | 0.0000 | 0.0646 |
| production | bge-small | fixed-128 | 0.1410 | 0.0466 | 0.1410 | 0.0466 | 0.0000 | 0.0578 | 0.0605 |
| production | bge-small | fixed-256 | 0.1271 | 0.0445 | 0.1271 | 0.0445 | 0.0000 | 0.0496 | 0.0496 |
| production | bge-small | fixed-512 | 0.0970 | 0.0348 | 0.0970 | 0.0348 | 0.8856 ‡ | 0.0519 | 0.0533 |
| production | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| production | bge-small | section-aware | 0.1559 | 0.0563 | 0.1559 | 0.0563 | 0.0810 ‡ | 0.6218 | 0.6254 |
| production | bge-small | small-to-big | 0.1664 | 0.0572 | 0.1664 | 0.0572 | 0.0000 | 0.6340 | 0.6636 |
| production | nomic | fixed-64 | 0.1241 | 0.0379 | 0.1241 | 0.0379 | 0.0000 | 0.0000 | 0.0460 |
| production | nomic | fixed-128 | 0.1411 | 0.0467 | 0.1411 | 0.0467 | 0.0000 | 0.0528 | 0.0528 |
| production | nomic | fixed-256 | 0.1249 | 0.0443 | 0.1249 | 0.0443 | 0.0000 | 0.0510 | 0.0510 |
| production | nomic | fixed-512 | 0.1006 | 0.0361 | 0.1006 | 0.0361 | 0.0000 | 0.0624 | 0.0624 |
| production | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| production | nomic | section-aware | 0.1570 | 0.0555 | 0.1570 | 0.0555 | 0.0000 | 0.5576 | 0.5626 |
| production | nomic | small-to-big | 0.1640 | 0.0568 | 0.1640 | 0.0568 | 0.0000 | 0.6891 | 0.6946 |
| hybrid | bge-small | fixed-64 | 0.1028 | 0.0317 | 0.1029 | 0.0315 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.1136 | 0.0369 | 0.1136 | 0.0369 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.0989 | 0.0340 | 0.0989 | 0.0340 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.0815 | 0.0313 | 0.0815 | 0.0313 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.1093 | 0.0392 | 0.1093 | 0.0392 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.1156 | 0.0406 | 0.1156 | 0.0405 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.1075 | 0.0333 | 0.1075 | 0.0332 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.1248 | 0.0405 | 0.1248 | 0.0405 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.1043 | 0.0361 | 0.1043 | 0.0361 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.0864 | 0.0341 | 0.0864 | 0.0341 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.1104 | 0.0390 | 0.1104 | 0.0390 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.1241 | 0.0441 | 0.1241 | 0.0441 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0864 | 0.0263 | 0.0866 | 0.0259 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.0853 | 0.0282 | 0.0856 | 0.0282 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.0741 | 0.0269 | 0.0741 | 0.0267 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.0613 | 0.0234 | 0.0613 | 0.0234 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.0885 | 0.0318 | 0.0885 | 0.0318 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.0864 | 0.0303 | 0.0864 | 0.0302 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0967 | 0.0292 | 0.0967 | 0.0292 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.1013 | 0.0335 | 0.1013 | 0.0335 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.0829 | 0.0306 | 0.0829 | 0.0306 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.0591 | 0.0234 | 0.0591 | 0.0234 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.0996 | 0.0358 | 0.0996 | 0.0358 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.1140 | 0.0406 | 0.1140 | 0.0406 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0910 | 0.0280 | 0.0910 | 0.0279 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1060 | 0.0344 | 0.1060 | 0.0344 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.0934 | 0.0320 | 0.0934 | 0.0320 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.0862 | 0.0319 | 0.0862 | 0.0319 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.0922 | 0.0331 | 0.0922 | 0.0331 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.1034 | 0.0373 | 0.1034 | 0.0373 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.1245† | 0.0383† | 0.1617 | 0.0255 | 0.0000 | 0.0000 | 0.1475 |
| production | bge-small | fixed-128 | 0.1958 | 0.0332 | 0.1958 | 0.0329 | 0.0000 | 0.0000 | 0.1270 |
| production | bge-small | fixed-256 | 0.2058 | 0.0357 | 0.2058 | 0.0357 | 0.0000 | 0.1193 | 0.1252 |
| production | bge-small | fixed-512 | 0.1858 | 0.0348 | 0.1858 | 0.0348 | 0.8856 ‡ | 0.1179 | 0.1197 |
| production | bge-small | fixed-1024 | 0.1521 | 0.0286 | 0.1521 | 0.0286 | 0.9101 ‡ | 0.0751 | 0.0760 |
| production | bge-small | section-aware | 0.2458 | 0.0466 | 0.2460 | 0.0465 | 0.0810 ‡ | 0.5321 | 0.6076 |
| production | bge-small | small-to-big | 0.2333 | 0.0431 | 0.2333 | 0.0429 | 0.0000 | 0.5503 | 0.6987 |
| production | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1634 | 0.0255 | 0.0000 | 0.0000 | 0.1020 |
| production | nomic | fixed-128 | 0.1985 | 0.0338 | 0.1985 | 0.0336 | 0.0000 | 0.0000 | 0.0979 |
| production | nomic | fixed-256 | 0.2019 | 0.0352 | 0.2019 | 0.0352 | 0.0000 | 0.1070 | 0.1070 |
| production | nomic | fixed-512 | 0.1890 | 0.0356 | 0.1890 | 0.0356 | 0.0000 | 0.1302 | 0.1311 |
| production | nomic | fixed-1024 | 0.1509 | 0.0284 | 0.1509 | 0.0284 | 0.0000 | 0.0833 | 0.0833 |
| production | nomic | section-aware | 0.2471 | 0.0467 | 0.2480 | 0.0467 | 0.0000 | 0.5039 | 0.5831 |
| production | nomic | small-to-big | 0.2377 | 0.0444 | 0.2377 | 0.0444 | 0.0000 | 0.6545 | 0.7183 |
| hybrid | bge-small | fixed-64 | 0.1028† | 0.0317† | 0.1438 | 0.0225 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.1598 | 0.0271 | 0.1600 | 0.0267 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.1497 | 0.0271 | 0.1497 | 0.0271 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.1299 | 0.0249 | 0.1299 | 0.0249 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.0994 | 0.0200 | 0.0994 | 0.0200 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.1754 | 0.0339 | 0.1759 | 0.0338 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.1752 | 0.0327 | 0.1752 | 0.0325 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.1075† | 0.0333† | 0.1473 | 0.0233 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.1729 | 0.0296 | 0.1731 | 0.0295 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.1549 | 0.0274 | 0.1549 | 0.0274 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.1347 | 0.0265 | 0.1347 | 0.0265 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.1036 | 0.0211 | 0.1036 | 0.0211 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.1768 | 0.0334 | 0.1777 | 0.0334 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.1820 | 0.0342 | 0.1820 | 0.0341 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0864† | 0.0263† | 0.1167 | 0.0178 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.1217 | 0.0208 | 0.1226 | 0.0203 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.1082 | 0.0196 | 0.1082 | 0.0193 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.0931 | 0.0177 | 0.0931 | 0.0177 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.0673 | 0.0138 | 0.0673 | 0.0138 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.1315 | 0.0245 | 0.1343 | 0.0244 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.1388† | 0.0254† | 0.1395 | 0.0253 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0967† | 0.0292† | 0.1308 | 0.0204 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.1450 | 0.0246 | 0.1450 | 0.0245 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.1208 | 0.0230 | 0.1208 | 0.0230 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.1059 | 0.0214 | 0.1059 | 0.0214 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.0653 | 0.0141 | 0.0653 | 0.0141 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.1467 | 0.0268 | 0.1472 | 0.0267 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.1625 | 0.0301 | 0.1626 | 0.0301 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0910† | 0.0280† | 0.1265 | 0.0198 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1560 | 0.0261 | 0.1560 | 0.0260 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.1476 | 0.0259 | 0.1476 | 0.0259 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.1384 | 0.0264 | 0.1384 | 0.0264 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.1286 | 0.0253 | 0.1286 | 0.0253 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.1601 | 0.0300 | 0.1601 | 0.0300 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.1568 | 0.0296 | 0.1568 | 0.0295 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.1245† | 0.0383† | 0.1886 | 0.0150 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-128 | 0.1958† | 0.0332† | 0.2373 | 0.0200 | 0.0000 | 0.0000 | 0.2777 |
| production | bge-small | fixed-256 | 0.2617 | 0.0244 | 0.2618 | 0.0240 | 0.0000 | 0.0000 | 0.2467 |
| production | bge-small | fixed-512 | 0.2555 | 0.0255 | 0.2558 | 0.0255 | 0.8856 ‡ | 0.2344 | 0.2481 |
| production | bge-small | fixed-1024 | 0.2411 | 0.0240 | 0.2411 | 0.0240 | 0.9101 ‡ | 0.1834 | 0.1853 |
| production | bge-small | section-aware | 0.3031† | 0.0320† | 0.3074 | 0.0296 | 0.0810 ‡ | 0.1375 | 0.6454 |
| production | bge-small | small-to-big | 0.2893† | 0.0299† | 0.2925 | 0.0282 | 0.0000 | 0.0901 | 0.7037 |
| production | nomic | fixed-64 | 0.1241† | 0.0379† | 0.1910 | 0.0151 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-128 | 0.1985† | 0.0338† | 0.2434 | 0.0209 | 0.0000 | 0.0000 | 0.1903 |
| production | nomic | fixed-256 | 0.2599 | 0.0243 | 0.2599 | 0.0240 | 0.0000 | 0.0000 | 0.2089 |
| production | nomic | fixed-512 | 0.2596 | 0.0256 | 0.2596 | 0.0256 | 0.0000 | 0.2472 | 0.2576 |
| production | nomic | fixed-1024 | 0.2430 | 0.0241 | 0.2430 | 0.0241 | 0.0000 | 0.2012 | 0.2021 |
| production | nomic | section-aware | 0.3033† | 0.0320† | 0.3076 | 0.0297 | 0.0000 | 0.1202 | 0.5976 |
| production | nomic | small-to-big | 0.2933† | 0.0304† | 0.2975 | 0.0289 | 0.0000 | 0.1620 | 0.7142 |
| hybrid | bge-small | fixed-64 | 0.1028† | 0.0317† | 0.1886 | 0.0150 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.1598† | 0.0271† | 0.2105 | 0.0178 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.2101 | 0.0197 | 0.2107 | 0.0194 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.1875 | 0.0188 | 0.1875 | 0.0187 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.1447 | 0.0150 | 0.1447 | 0.0150 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.2300† | 0.0245† | 0.2413 | 0.0232 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.2322† | 0.0235† | 0.2384 | 0.0226 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.1075† | 0.0333† | 0.1910 | 0.0151 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.1729† | 0.0296† | 0.2205 | 0.0190 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.2126 | 0.0201 | 0.2129 | 0.0199 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.1918 | 0.0197 | 0.1918 | 0.0197 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.1584 | 0.0169 | 0.1584 | 0.0169 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.2369† | 0.0251† | 0.2436 | 0.0233 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.2394† | 0.0242† | 0.2425 | 0.0235 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0864† | 0.0263† | 0.1511 | 0.0117 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.1217† | 0.0208† | 0.1625 | 0.0136 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.1499† | 0.0144† | 0.1518 | 0.0137 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.1365 | 0.0138 | 0.1365 | 0.0137 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.0969 | 0.0102 | 0.0969 | 0.0102 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.1729† | 0.0195† | 0.1854 | 0.0177 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.1768† | 0.0178† | 0.1831 | 0.0169 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0967† | 0.0292† | 0.1699 | 0.0135 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.1450† | 0.0246† | 0.1928 | 0.0163 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.1669 | 0.0160 | 0.1670 | 0.0158 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.1374 | 0.0143 | 0.1374 | 0.0142 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.1104 | 0.0118 | 0.1104 | 0.0118 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.1913† | 0.0215† | 0.2045 | 0.0199 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.2121† | 0.0216† | 0.2136 | 0.0208 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0910† | 0.0280† | 0.1649 | 0.0132 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1560† | 0.0261† | 0.2040 | 0.0174 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.2120 | 0.0195 | 0.2120 | 0.0193 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.2053 | 0.0201 | 0.2053 | 0.0201 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.1955 | 0.0198 | 0.1955 | 0.0198 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.2231† | 0.0225† | 0.2297 | 0.0219 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.2247† | 0.0227† | 0.2279 | 0.0219 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.1245† | 0.0383† | 0.2311 | 0.0093 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-128 | 0.1958† | 0.0332† | 0.2656 | 0.0114 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-256 | 0.2617† | 0.0244† | 0.3009 | 0.0141 | 0.0000 | 0.0000 | 0.4461 |
| production | bge-small | fixed-512 | 0.3211 | 0.0170 | 0.3220 | 0.0164 | 0.8856 ‡ | 0.0000 | 0.4574 |
| production | bge-small | fixed-1024 | 0.3132 | 0.0165 | 0.3132 | 0.0164 | 0.9101 ‡ | 0.3550 | 0.3655 |
| production | bge-small | section-aware | 0.3119† | 0.0298† | 0.3445 | 0.0169 | 0.0810 ‡ | 0.0000 | 0.7656 |
| production | bge-small | small-to-big | 0.3010† | 0.0269† | 0.3324 | 0.0163 | 0.0000 | 0.0000 | 0.7715 |
| production | nomic | fixed-64 | 0.1241† | 0.0379† | 0.2387 | 0.0096 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-128 | 0.1985† | 0.0338† | 0.2703 | 0.0116 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3000 | 0.0143 | 0.0000 | 0.0000 | 0.3901 |
| production | nomic | fixed-512 | 0.3202† | 0.0171† | 0.3209 | 0.0165 | 0.0000 | 0.0000 | 0.4779 |
| production | nomic | fixed-1024 | 0.3143 | 0.0166 | 0.3143 | 0.0166 | 0.0000 | 0.3842 | 0.4110 |
| production | nomic | section-aware | 0.3101† | 0.0300† | 0.3443 | 0.0170 | 0.0000 | 0.0000 | 0.7237 |
| production | nomic | small-to-big | 0.3057† | 0.0273† | 0.3404 | 0.0166 | 0.0000 | 0.0000 | 0.7806 |
| hybrid | bge-small | fixed-64 | 0.1028† | 0.0317† | 0.2311 | 0.0093 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.1598† | 0.0271† | 0.2656 | 0.0114 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.2101† | 0.0197† | 0.2685 | 0.0125 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.2505† | 0.0132† | 0.2528 | 0.0128 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.2044 | 0.0110 | 0.2044 | 0.0110 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.2405† | 0.0230† | 0.2973 | 0.0146 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.2425† | 0.0211† | 0.2943 | 0.0143 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.1075† | 0.0333† | 0.2387 | 0.0096 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.1729† | 0.0296† | 0.2703 | 0.0116 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.2126† | 0.0201† | 0.2739 | 0.0129 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.2527† | 0.0134† | 0.2551 | 0.0129 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.2213 | 0.0120 | 0.2213 | 0.0120 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.2479† | 0.0239† | 0.3076 | 0.0150 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.2576† | 0.0218† | 0.3036 | 0.0149 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0864† | 0.0263† | 0.1859 | 0.0073 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.1217† | 0.0208† | 0.2042 | 0.0086 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.1499† | 0.0144† | 0.1974 | 0.0093 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.1749† | 0.0096† | 0.1766 | 0.0091 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.1364 | 0.0073 | 0.1364 | 0.0072 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.1779† | 0.0186† | 0.2399 | 0.0117 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.1873† | 0.0162† | 0.2300 | 0.0110 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0967† | 0.0292† | 0.2065 | 0.0083 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.1450† | 0.0246† | 0.2328 | 0.0101 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.1669† | 0.0160† | 0.2183 | 0.0105 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.1861† | 0.0106† | 0.1890 | 0.0100 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.1597 | 0.0089 | 0.1601 | 0.0088 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.1968† | 0.0204† | 0.2553 | 0.0126 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.2249† | 0.0191† | 0.2596 | 0.0128 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0910† | 0.0280† | 0.2072 | 0.0083 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1560† | 0.0261† | 0.2449 | 0.0106 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.2120† | 0.0195† | 0.2620 | 0.0122 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.2691 | 0.0135 | 0.2700 | 0.0132 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.2640 | 0.0138 | 0.2640 | 0.0138 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.2396† | 0.0217† | 0.2862 | 0.0140 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.2406† | 0.0203† | 0.2842 | 0.0139 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| production | bge-small | fixed-64 | 0.1245† | 0.0383† | 0.2767 | 0.0056 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-128 | 0.1958† | 0.0332† | 0.3168 | 0.0069 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-256 | 0.2617† | 0.0244† | 0.3266 | 0.0078 | 0.0000 | 0.0000 | 1.0000 |
| production | bge-small | fixed-512 | 0.3211† | 0.0170† | 0.3520 | 0.0091 | 0.8856 ‡ | 0.0000 | 0.6932 |
| production | bge-small | fixed-1024 | 0.3591† | 0.0104† | 0.3614 | 0.0098 | 0.9101 ‡ | 0.0000 | 0.6136 |
| production | bge-small | section-aware | 0.3119† | 0.0298† | 0.3694 | 0.0090 | 0.0810 ‡ | 0.0000 | 0.9654 |
| production | bge-small | small-to-big | 0.3010† | 0.0269† | 0.3639 | 0.0090 | 0.0000 | 0.0000 | 0.9759 |
| production | nomic | fixed-64 | 0.1241† | 0.0379† | 0.2862 | 0.0058 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-128 | 0.1985† | 0.0338† | 0.3286 | 0.0072 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-256 | 0.2599† | 0.0243† | 0.3283 | 0.0080 | 0.0000 | 0.0000 | 1.0000 |
| production | nomic | fixed-512 | 0.3202† | 0.0171† | 0.3598 | 0.0094 | 0.0000 | 0.0000 | 0.6850 |
| production | nomic | fixed-1024 | 0.3692† | 0.0108† | 0.3708 | 0.0101 | 0.0000 | 0.0000 | 0.6618 |
| production | nomic | section-aware | 0.3101† | 0.0300† | 0.3695 | 0.0091 | 0.0000 | 0.0000 | 0.9672 |
| production | nomic | small-to-big | 0.3057† | 0.0273† | 0.3696 | 0.0091 | 0.0000 | 0.0000 | 0.9577 |
| hybrid | bge-small | fixed-64 | 0.1028† | 0.0317† | 0.2767 | 0.0056 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.1598† | 0.0271† | 0.3168 | 0.0069 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.2101† | 0.0197† | 0.3266 | 0.0078 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.2505† | 0.0132† | 0.3084 | 0.0079 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.2696† | 0.0080† | 0.2737 | 0.0075 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.2405† | 0.0230† | 0.3636 | 0.0089 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.2425† | 0.0211† | 0.3607 | 0.0089 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.1075† | 0.0333† | 0.2862 | 0.0058 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.1729† | 0.0296† | 0.3286 | 0.0072 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.2126† | 0.0201† | 0.3283 | 0.0080 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.2527† | 0.0134† | 0.3131 | 0.0080 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.2818† | 0.0087† | 0.2922 | 0.0081 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.2479† | 0.0239† | 0.3660 | 0.0090 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.2576† | 0.0218† | 0.3662 | 0.0090 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.0864† | 0.0263† | 0.2263 | 0.0046 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.1217† | 0.0208† | 0.2485 | 0.0053 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.1499† | 0.0144† | 0.2478 | 0.0060 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.1749† | 0.0096† | 0.2183 | 0.0056 | 0.8856 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.1690† | 0.0052† | 0.1721 | 0.0047 | 0.9101 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.1779† | 0.0186† | 0.2887 | 0.0071 | 0.0810 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.1873† | 0.0162† | 0.2859 | 0.0069 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.0967† | 0.0292† | 0.2475 | 0.0050 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.1450† | 0.0246† | 0.2841 | 0.0062 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.1669† | 0.0160† | 0.2616 | 0.0064 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.1861† | 0.0106† | 0.2382 | 0.0063 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.1896† | 0.0065† | 0.2057 | 0.0056 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.1968† | 0.0204† | 0.3037 | 0.0075 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.2249† | 0.0191† | 0.3157 | 0.0079 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.0910† | 0.0280† | 0.2555 | 0.0053 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1560† | 0.0261† | 0.2950 | 0.0065 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.2120† | 0.0195† | 0.3202 | 0.0077 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.2691† | 0.0135† | 0.3260 | 0.0082 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.3162† | 0.0090† | 0.3187 | 0.0086 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.2396† | 0.0217† | 0.3445 | 0.0085 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.2406† | 0.0203† | 0.3392 | 0.0085 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
