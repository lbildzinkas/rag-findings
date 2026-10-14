# R5 - nq grid, production line and ablations: pipeline x embedder x chunking

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

## Retrieval recall and precision by pipeline, embedder and chunking, collection search

Production view: top-N cap 8; fair view: no cap. The production line comes first, then its ablations. Every cell is filled or n/a with its reason.

### Budget 128 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.2753 | 0.2320 | 0.2753 | 0.2320 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.2954 | 0.2612 | 0.2954 | 0.2612 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | section-aware | 0.0560 | 0.0327 | 0.0560 | 0.0327 | 0.0092 ‡ | 0.8940 | 0.9000 |
| hybrid-rerank | bge-small | small-to-big | 0.3337 | 0.2968 | 0.3337 | 0.2968 | 0.0000 | 0.1770 | 0.1780 |
| hybrid-rerank | nomic | fixed-64 | 0.2764 | 0.2335 | 0.2764 | 0.2335 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.2968 | 0.2642 | 0.2968 | 0.2642 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.0580 | 0.0339 | 0.0580 | 0.0339 | 0.0000 | 0.8370 | 0.8370 |
| hybrid-rerank | nomic | small-to-big | 0.3320 | 0.2940 | 0.3320 | 0.2940 | 0.0000 | 0.1710 | 0.1710 |
| hybrid | bge-small | fixed-64 | 0.2078 | 0.1763 | 0.2078 | 0.1763 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.2621 | 0.2269 | 0.2621 | 0.2269 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.0470 | 0.0270 | 0.0470 | 0.0270 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.2517 | 0.2151 | 0.2517 | 0.2151 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.2236 | 0.1898 | 0.2236 | 0.1898 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.2501 | 0.2226 | 0.2501 | 0.2226 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.0470 | 0.0282 | 0.0470 | 0.0282 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.2634 | 0.2271 | 0.2634 | 0.2271 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.2602 | 0.2167 | 0.2602 | 0.2167 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.3013 | 0.2559 | 0.3013 | 0.2559 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.0510 | 0.0287 | 0.0510 | 0.0286 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.2328 | 0.2003 | 0.2328 | 0.1999 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.2947 | 0.2490 | 0.2947 | 0.2490 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.3408 | 0.2954 | 0.3408 | 0.2954 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.0560 | 0.0330 | 0.0560 | 0.0330 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.3670 | 0.3203 | 0.3670 | 0.3203 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.1356 | 0.1143 | 0.1356 | 0.1143 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.1769 | 0.1507 | 0.1769 | 0.1507 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.0390 | 0.0230 | 0.0390 | 0.0230 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.1775 | 0.1551 | 0.1775 | 0.1551 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 256 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.3707 | 0.1605 | 0.3707 | 0.1605 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.4323 | 0.1955 | 0.4323 | 0.1955 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-256 | 0.4247 | 0.1982 | 0.4247 | 0.1982 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | section-aware | 0.2460 | 0.1009 | 0.2460 | 0.1004 | 0.0092 ‡ | 0.8920 | 0.9020 |
| hybrid-rerank | bge-small | small-to-big | 0.5006 | 0.2289 | 0.5006 | 0.2286 | 0.0000 | 0.4130 | 0.4170 |
| hybrid-rerank | nomic | fixed-64 | 0.3750 | 0.1613 | 0.3750 | 0.1613 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.4335 | 0.1970 | 0.4335 | 0.1970 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.4278 | 0.1996 | 0.4278 | 0.1996 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.2403 | 0.0995 | 0.2403 | 0.0995 | 0.0000 | 0.8450 | 0.8450 |
| hybrid-rerank | nomic | small-to-big | 0.4997 | 0.2295 | 0.4997 | 0.2294 | 0.0000 | 0.3940 | 0.3940 |
| hybrid | bge-small | fixed-64 | 0.3124 | 0.1321 | 0.3124 | 0.1321 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.3735 | 0.1650 | 0.3735 | 0.1650 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.3517 | 0.1591 | 0.3517 | 0.1591 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.2070 | 0.0854 | 0.2070 | 0.0851 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.3997 | 0.1776 | 0.3997 | 0.1774 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.3226 | 0.1380 | 0.3226 | 0.1380 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.3748 | 0.1664 | 0.3748 | 0.1664 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.3628 | 0.1698 | 0.3628 | 0.1698 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.2100 | 0.0881 | 0.2100 | 0.0881 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.4111 | 0.1842 | 0.4111 | 0.1842 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.3567 | 0.1533 | 0.3567 | 0.1533 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.4401 | 0.1942 | 0.4401 | 0.1942 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.4116 | 0.1889 | 0.4116 | 0.1889 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.2162 | 0.0924 | 0.2162 | 0.0917 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.4200 | 0.1881 | 0.4200 | 0.1875 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.4012 | 0.1739 | 0.4012 | 0.1739 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.4827 | 0.2147 | 0.4827 | 0.2147 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.4728 | 0.2242 | 0.4728 | 0.2242 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.2340 | 0.0959 | 0.2340 | 0.0959 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.5196 | 0.2373 | 0.5196 | 0.2373 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.2111 | 0.0888 | 0.2111 | 0.0888 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.2669 | 0.1189 | 0.2669 | 0.1189 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.2591 | 0.1189 | 0.2591 | 0.1189 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.1640 | 0.0666 | 0.1640 | 0.0666 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.2776 | 0.1225 | 0.2776 | 0.1225 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 512 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.4697 | 0.1061 | 0.4697 | 0.1061 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.5672 | 0.1321 | 0.5672 | 0.1321 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-256 | 0.5946 | 0.1429 | 0.5946 | 0.1428 | 0.0000 | 0.0030 | 0.0030 |
| hybrid-rerank | bge-small | fixed-512 | 0.6077 | 0.1473 | 0.6077 | 0.1473 | 0.1244 ‡ | 0.0050 | 0.0050 |
| hybrid-rerank | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | bge-small | section-aware | 0.6610 | 0.1633 | 0.6610 | 0.1621 | 0.0092 ‡ | 0.8630 | 0.8880 |
| hybrid-rerank | bge-small | small-to-big | 0.6574 | 0.1636 | 0.6574 | 0.1631 | 0.0000 | 0.8070 | 0.8180 |
| hybrid-rerank | nomic | fixed-64 | 0.4789 | 0.1077 | 0.4789 | 0.1077 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.5667 | 0.1321 | 0.5667 | 0.1321 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.5975 | 0.1444 | 0.5975 | 0.1444 | 0.0000 | 0.0020 | 0.0020 |
| hybrid-rerank | nomic | fixed-512 | 0.6114 | 0.1479 | 0.6114 | 0.1479 | 0.0000 | 0.0070 | 0.0070 |
| hybrid-rerank | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: chunk > budget | n/a: chunk > budget |
| hybrid-rerank | nomic | section-aware | 0.6610 | 0.1623 | 0.6610 | 0.1622 | 0.0000 | 0.8150 | 0.8160 |
| hybrid-rerank | nomic | small-to-big | 0.6541 | 0.1628 | 0.6541 | 0.1627 | 0.0000 | 0.7920 | 0.7920 |
| hybrid | bge-small | fixed-64 | 0.4172 | 0.0914 | 0.4172 | 0.0914 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.5006 | 0.1129 | 0.5006 | 0.1129 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.5336 | 0.1282 | 0.5336 | 0.1282 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.4650 | 0.1137 | 0.4650 | 0.1137 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.5130 | 0.1259 | 0.5130 | 0.1253 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.5411 | 0.1311 | 0.5411 | 0.1309 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.4222 | 0.0929 | 0.4222 | 0.0929 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.5065 | 0.1170 | 0.5065 | 0.1170 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.5249 | 0.1249 | 0.5249 | 0.1249 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.4666 | 0.1168 | 0.4666 | 0.1168 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.5300 | 0.1312 | 0.5300 | 0.1311 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.5395 | 0.1318 | 0.5395 | 0.1317 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.4652 | 0.1024 | 0.4652 | 0.1024 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.5612 | 0.1289 | 0.5612 | 0.1289 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.5569 | 0.1322 | 0.5569 | 0.1322 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.5296 | 0.1290 | 0.5296 | 0.1290 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.5578 | 0.1389 | 0.5588 | 0.1375 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.5774 | 0.1390 | 0.5777 | 0.1387 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.5019 | 0.1116 | 0.5019 | 0.1116 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.6093 | 0.1411 | 0.6093 | 0.1411 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.6359 | 0.1532 | 0.6359 | 0.1532 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.5656 | 0.1415 | 0.5656 | 0.1415 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.6510 | 0.1610 | 0.6510 | 0.1610 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.6504 | 0.1605 | 0.6504 | 0.1605 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.3055 | 0.0665 | 0.3055 | 0.0665 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.3748 | 0.0844 | 0.3748 | 0.0844 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.4002 | 0.0921 | 0.4002 | 0.0921 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.3711 | 0.0935 | 0.3711 | 0.0935 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: chunk > budget | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.3900 | 0.0973 | 0.3900 | 0.0972 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.3941 | 0.0955 | 0.3941 | 0.0955 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 1024 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.4697† | 0.1061† | 0.5691 | 0.0651 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.6861 | 0.0832 | 0.6861 | 0.0832 | 0.0000 | 0.0000 | 0.0010 |
| hybrid-rerank | bge-small | fixed-256 | 0.7347 | 0.0921 | 0.7347 | 0.0921 | 0.0000 | 0.0090 | 0.0090 |
| hybrid-rerank | bge-small | fixed-512 | 0.7674 | 0.0966 | 0.7674 | 0.0966 | 0.1244 ‡ | 0.0320 | 0.0320 |
| hybrid-rerank | bge-small | fixed-1024 | 0.7396 | 0.0947 | 0.7396 | 0.0947 | 0.9312 ‡ | 0.0280 | 0.0280 |
| hybrid-rerank | bge-small | section-aware | 0.8207 | 0.1079 | 0.8207 | 0.1064 | 0.0092 ‡ | 0.8010 | 0.9090 |
| hybrid-rerank | bge-small | small-to-big | 0.7924 | 0.1031 | 0.7924 | 0.1023 | 0.0000 | 0.7530 | 0.8600 |
| hybrid-rerank | nomic | fixed-64 | 0.4789† | 0.1077† | 0.5779 | 0.0664 | 0.0000 | 0.0000 | 0.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.6887 | 0.0836 | 0.6887 | 0.0836 | 0.0000 | 0.0000 | 0.0010 |
| hybrid-rerank | nomic | fixed-256 | 0.7350 | 0.0924 | 0.7350 | 0.0924 | 0.0000 | 0.0040 | 0.0040 |
| hybrid-rerank | nomic | fixed-512 | 0.7683 | 0.0967 | 0.7683 | 0.0967 | 0.0000 | 0.0320 | 0.0320 |
| hybrid-rerank | nomic | fixed-1024 | 0.7416 | 0.0949 | 0.7416 | 0.0949 | 0.0000 | 0.0310 | 0.0310 |
| hybrid-rerank | nomic | section-aware | 0.8197 | 0.1072 | 0.8197 | 0.1067 | 0.0000 | 0.8150 | 0.8540 |
| hybrid-rerank | nomic | small-to-big | 0.7871 | 0.1022 | 0.7871 | 0.1020 | 0.0000 | 0.7870 | 0.8310 |
| hybrid | bge-small | fixed-64 | 0.4172† | 0.0914† | 0.5319 | 0.0598 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.6427 | 0.0754 | 0.6427 | 0.0754 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.6806 | 0.0840 | 0.6806 | 0.0840 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.6698 | 0.0844 | 0.6698 | 0.0844 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.5606 | 0.0737 | 0.5606 | 0.0737 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.7039 | 0.0906 | 0.7039 | 0.0899 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.7008 | 0.0898 | 0.7008 | 0.0891 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.4222† | 0.0929† | 0.5444 | 0.0615 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.6378 | 0.0756 | 0.6378 | 0.0756 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.6735 | 0.0851 | 0.6735 | 0.0851 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.6758 | 0.0843 | 0.6758 | 0.0843 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.5604 | 0.0733 | 0.5604 | 0.0733 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.7299 | 0.0936 | 0.7299 | 0.0933 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.7052 | 0.0897 | 0.7055 | 0.0895 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.4652† | 0.1024† | 0.5662 | 0.0648 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.6762 | 0.0814 | 0.6762 | 0.0814 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.7232 | 0.0899 | 0.7232 | 0.0899 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.6863 | 0.0870 | 0.6863 | 0.0870 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.6293 | 0.0800 | 0.6293 | 0.0800 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.7257 | 0.0955 | 0.7277 | 0.0931 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.7571 | 0.0980 | 0.7579 | 0.0971 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.5019† | 0.1116† | 0.6031 | 0.0693 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.7090 | 0.0858 | 0.7090 | 0.0858 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.7677 | 0.0962 | 0.7677 | 0.0962 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.7365 | 0.0942 | 0.7365 | 0.0942 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.6257 | 0.0808 | 0.6257 | 0.0808 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.8157 | 0.1059 | 0.8157 | 0.1057 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.8084 | 0.1046 | 0.8084 | 0.1045 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.3055† | 0.0665† | 0.4052 | 0.0451 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.4956 | 0.0576 | 0.4956 | 0.0576 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.5377 | 0.0656 | 0.5377 | 0.0656 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.5488 | 0.0690 | 0.5488 | 0.0690 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.4644 | 0.0611 | 0.4644 | 0.0611 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.5739 | 0.0731 | 0.5739 | 0.0728 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.5416 | 0.0677 | 0.5416 | 0.0674 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 2048 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.4697† | 0.1061† | 0.6427 | 0.0376 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.6861† | 0.0832† | 0.7825 | 0.0490 | 0.0000 | 0.0000 | 0.0020 |
| hybrid-rerank | bge-small | fixed-256 | 0.8465 | 0.0546 | 0.8465 | 0.0545 | 0.0000 | 0.0000 | 0.0200 |
| hybrid-rerank | bge-small | fixed-512 | 0.8642 | 0.0569 | 0.8642 | 0.0569 | 0.1244 ‡ | 0.0970 | 0.0970 |
| hybrid-rerank | bge-small | fixed-1024 | 0.8547 | 0.0569 | 0.8547 | 0.0569 | 0.9312 ‡ | 0.0980 | 0.0980 |
| hybrid-rerank | bge-small | section-aware | 0.9079† | 0.0663† | 0.9099 | 0.0606 | 0.0092 ‡ | 0.3060 | 0.9270 |
| hybrid-rerank | bge-small | small-to-big | 0.8811† | 0.0620† | 0.8814 | 0.0587 | 0.0000 | 0.2900 | 0.8930 |
| hybrid-rerank | nomic | fixed-64 | 0.4789† | 0.1077† | 0.6504 | 0.0384 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.7833 | 0.0491 | 0.0000 | 0.0000 | 0.0020 |
| hybrid-rerank | nomic | fixed-256 | 0.8439 | 0.0546 | 0.8439 | 0.0546 | 0.0000 | 0.0000 | 0.0080 |
| hybrid-rerank | nomic | fixed-512 | 0.8720 | 0.0576 | 0.8720 | 0.0576 | 0.0000 | 0.0900 | 0.0900 |
| hybrid-rerank | nomic | fixed-1024 | 0.8577 | 0.0571 | 0.8577 | 0.0571 | 0.0000 | 0.1060 | 0.1060 |
| hybrid-rerank | nomic | section-aware | 0.9077† | 0.0650† | 0.9087 | 0.0609 | 0.0000 | 0.4330 | 0.8770 |
| hybrid-rerank | nomic | small-to-big | 0.8774† | 0.0607† | 0.8774 | 0.0581 | 0.0000 | 0.3830 | 0.8370 |
| hybrid | bge-small | fixed-64 | 0.4172† | 0.0914† | 0.6427 | 0.0376 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.6427† | 0.0754† | 0.7407 | 0.0452 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.8072 | 0.0514 | 0.8072 | 0.0513 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.8082 | 0.0528 | 0.8082 | 0.0528 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.7575 | 0.0506 | 0.7575 | 0.0506 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.8097† | 0.0576† | 0.8147 | 0.0536 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.8199† | 0.0571† | 0.8234 | 0.0537 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.4222† | 0.0929† | 0.6504 | 0.0384 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.6378† | 0.0756† | 0.7482 | 0.0458 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.8094 | 0.0518 | 0.8094 | 0.0518 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.8079 | 0.0529 | 0.8079 | 0.0529 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.7492 | 0.0499 | 0.7492 | 0.0499 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.8279† | 0.0578† | 0.8319 | 0.0549 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.8352† | 0.0575† | 0.8374 | 0.0549 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.4652† | 0.1024† | 0.6589 | 0.0391 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.6762† | 0.0814† | 0.7697 | 0.0484 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.8313 | 0.0536 | 0.8313 | 0.0535 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.8178 | 0.0536 | 0.8178 | 0.0536 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.7689 | 0.0507 | 0.7689 | 0.0507 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.8310† | 0.0630† | 0.8390 | 0.0553 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.8565† | 0.0610† | 0.8636 | 0.0571 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.5019† | 0.1116† | 0.6991 | 0.0418 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.7090† | 0.0858† | 0.8052 | 0.0507 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.8577 | 0.0554 | 0.8577 | 0.0554 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.8553 | 0.0565 | 0.8553 | 0.0565 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.7902 | 0.0522 | 0.7902 | 0.0522 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.8979† | 0.0627† | 0.8989 | 0.0595 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.8883† | 0.0607† | 0.8896 | 0.0587 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.3055† | 0.0665† | 0.4926 | 0.0282 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.4956† | 0.0576† | 0.5991 | 0.0360 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.6680 | 0.0420 | 0.6680 | 0.0420 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.7024 | 0.0446 | 0.7024 | 0.0446 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.6562 | 0.0439 | 0.6562 | 0.0439 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.7149† | 0.0488† | 0.7169 | 0.0462 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.6790† | 0.0458† | 0.6810 | 0.0435 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 4096 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.4697† | 0.1061† | 0.7356 | 0.0222 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.6861† | 0.0832† | 0.8361 | 0.0267 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-256 | 0.8465† | 0.0546† | 0.9135 | 0.0299 | 0.0000 | 0.0000 | 0.0300 |
| hybrid-rerank | bge-small | fixed-512 | 0.9284 | 0.0316 | 0.9284 | 0.0314 | 0.1244 ‡ | 0.0000 | 0.1510 |
| hybrid-rerank | bge-small | fixed-1024 | 0.9243 | 0.0315 | 0.9243 | 0.0315 | 0.9312 ‡ | 0.2170 | 0.2180 |
| hybrid-rerank | bge-small | section-aware | 0.9289† | 0.0557† | 0.9499 | 0.0320 | 0.0092 ‡ | 0.0000 | 0.9580 |
| hybrid-rerank | bge-small | small-to-big | 0.9069† | 0.0494† | 0.9260 | 0.0312 | 0.0000 | 0.0000 | 0.9170 |
| hybrid-rerank | nomic | fixed-64 | 0.4789† | 0.1077† | 0.7466 | 0.0227 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.8357 | 0.0267 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9147 | 0.0300 | 0.0000 | 0.0000 | 0.0160 |
| hybrid-rerank | nomic | fixed-512 | 0.9318 | 0.0318 | 0.9318 | 0.0316 | 0.0000 | 0.0000 | 0.1390 |
| hybrid-rerank | nomic | fixed-1024 | 0.9255 | 0.0315 | 0.9255 | 0.0315 | 0.0000 | 0.2200 | 0.2200 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9489 | 0.0322 | 0.0000 | 0.0000 | 0.8970 |
| hybrid-rerank | nomic | small-to-big | 0.9089† | 0.0482† | 0.9304 | 0.0313 | 0.0000 | 0.0000 | 0.8980 |
| hybrid | bge-small | fixed-64 | 0.4172† | 0.0914† | 0.7356 | 0.0222 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.6427† | 0.0754† | 0.8361 | 0.0267 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.8072† | 0.0514† | 0.8933 | 0.0290 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.9119 | 0.0308 | 0.9119 | 0.0305 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.8667 | 0.0292 | 0.8667 | 0.0292 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.8607† | 0.0501† | 0.9127 | 0.0306 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.8559† | 0.0475† | 0.8973 | 0.0298 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.4222† | 0.0929† | 0.7466 | 0.0227 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.6378† | 0.0756† | 0.8357 | 0.0267 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.8094† | 0.0518† | 0.8962 | 0.0291 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.9059 | 0.0307 | 0.9059 | 0.0305 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.8756 | 0.0299 | 0.8756 | 0.0299 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.8807† | 0.0488† | 0.9169 | 0.0308 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.8679† | 0.0460† | 0.9065 | 0.0303 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.4652† | 0.1024† | 0.7409 | 0.0224 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.6762† | 0.0814† | 0.8511 | 0.0274 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.8313† | 0.0536† | 0.8945 | 0.0297 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.8868 | 0.0303 | 0.8868 | 0.0300 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.8596 | 0.0290 | 0.8596 | 0.0289 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.8607† | 0.0566† | 0.8990 | 0.0300 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.8797† | 0.0512† | 0.9233 | 0.0312 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.5019† | 0.1116† | 0.7827 | 0.0243 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.7090† | 0.0858† | 0.8712 | 0.0282 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.8577† | 0.0554† | 0.9236 | 0.0307 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.9254 | 0.0317 | 0.9254 | 0.0315 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.8911 | 0.0301 | 0.8911 | 0.0301 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.9209† | 0.0515† | 0.9419 | 0.0317 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.9199† | 0.0481† | 0.9430 | 0.0317 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.3055† | 0.0665† | 0.5774 | 0.0172 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.4956† | 0.0576† | 0.6944 | 0.0215 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.6680† | 0.0420† | 0.7731 | 0.0251 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.8119 | 0.0269 | 0.8119 | 0.0267 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.7907 | 0.0270 | 0.7907 | 0.0270 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.7679† | 0.0419† | 0.8099 | 0.0269 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.7410† | 0.0394† | 0.7820 | 0.0257 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

### Budget 8192 tokens

| pipeline | embedder | chunking | production recall | production precision | fair recall | fair precision | truncated chunks | tail used, production view | tail used, fair view |
|---|---|---|---|---|---|---|---|---|---|
| hybrid-rerank | bge-small | fixed-64 | 0.4697† | 0.1061† | 0.7971 | 0.0124 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-128 | 0.6861† | 0.0832† | 0.8906 | 0.0145 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-256 | 0.8465† | 0.0546† | 0.9442 | 0.0157 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | bge-small | fixed-512 | 0.9284† | 0.0316† | 0.9675 | 0.0165 | 0.1244 ‡ | 0.0000 | 0.2070 |
| hybrid-rerank | bge-small | fixed-1024 | 0.9648 | 0.0170 | 0.9648 | 0.0166 | 0.9312 ‡ | 0.0000 | 0.3700 |
| hybrid-rerank | bge-small | section-aware | 0.9289† | 0.0557† | 0.9689 | 0.0166 | 0.0092 ‡ | 0.0000 | 0.9810 |
| hybrid-rerank | bge-small | small-to-big | 0.9069† | 0.0494† | 0.9459 | 0.0161 | 0.0000 | 0.0000 | 0.9890 |
| hybrid-rerank | nomic | fixed-64 | 0.4789† | 0.1077† | 0.8190 | 0.0129 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-128 | 0.6887† | 0.0836† | 0.8963 | 0.0145 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-256 | 0.8439† | 0.0546† | 0.9488 | 0.0159 | 0.0000 | 0.0000 | 1.0000 |
| hybrid-rerank | nomic | fixed-512 | 0.9318† | 0.0318† | 0.9722 | 0.0167 | 0.0000 | 0.0000 | 0.1920 |
| hybrid-rerank | nomic | fixed-1024 | 0.9705 | 0.0171 | 0.9705 | 0.0167 | 0.0000 | 0.0000 | 0.3720 |
| hybrid-rerank | nomic | section-aware | 0.9299† | 0.0541† | 0.9729 | 0.0166 | 0.0000 | 0.0000 | 0.9590 |
| hybrid-rerank | nomic | small-to-big | 0.9089† | 0.0482† | 0.9559 | 0.0162 | 0.0000 | 0.0000 | 0.9800 |
| hybrid | bge-small | fixed-64 | 0.4172† | 0.0914† | 0.7971 | 0.0124 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-128 | 0.6427† | 0.0754† | 0.8906 | 0.0145 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-256 | 0.8072† | 0.0514† | 0.9442 | 0.0157 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-512 | 0.9119† | 0.0308† | 0.9495 | 0.0162 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | fixed-1024 | 0.9352 | 0.0164 | 0.9352 | 0.0160 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | section-aware | 0.8607† | 0.0501† | 0.9590 | 0.0163 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| hybrid | bge-small | small-to-big | 0.8559† | 0.0475† | 0.9432 | 0.0160 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-64 | 0.4222† | 0.0929† | 0.8190 | 0.0129 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-128 | 0.6378† | 0.0756† | 0.8963 | 0.0145 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-256 | 0.8094† | 0.0518† | 0.9488 | 0.0159 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-512 | 0.9059† | 0.0307† | 0.9570 | 0.0163 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | fixed-1024 | 0.9465 | 0.0167 | 0.9465 | 0.0163 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | section-aware | 0.8807† | 0.0488† | 0.9639 | 0.0164 | 0.0000 | n/a: no reranker | n/a: no reranker |
| hybrid | nomic | small-to-big | 0.8679† | 0.0460† | 0.9542 | 0.0162 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-64 | 0.4652† | 0.1024† | 0.8064 | 0.0127 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-128 | 0.6762† | 0.0814† | 0.8973 | 0.0148 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-256 | 0.8313† | 0.0536† | 0.9297 | 0.0157 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-512 | 0.8868† | 0.0303† | 0.9350 | 0.0160 | 0.1244 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | fixed-1024 | 0.9033 | 0.0160 | 0.9033 | 0.0154 | 0.9312 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | section-aware | 0.8607† | 0.0566† | 0.9309 | 0.0158 | 0.0092 ‡ | n/a: no reranker | n/a: no reranker |
| vector | bge-small | small-to-big | 0.8797† | 0.0512† | 0.9539 | 0.0163 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-64 | 0.5019† | 0.1116† | 0.8479 | 0.0135 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-128 | 0.7090† | 0.0858† | 0.9156 | 0.0151 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-256 | 0.8577† | 0.0554† | 0.9545 | 0.0162 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-512 | 0.9254† | 0.0317† | 0.9577 | 0.0164 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | fixed-1024 | 0.9393 | 0.0166 | 0.9393 | 0.0161 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | section-aware | 0.9209† | 0.0515† | 0.9649 | 0.0164 | 0.0000 | n/a: no reranker | n/a: no reranker |
| vector | nomic | small-to-big | 0.9199† | 0.0481† | 0.9609 | 0.0162 | 0.0000 | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-64 | 0.3055† | 0.0665† | 0.6532 | 0.0101 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-128 | 0.4956† | 0.0576† | 0.7743 | 0.0123 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-256 | 0.6680† | 0.0420† | 0.8452 | 0.0139 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-512 | 0.8119† | 0.0269† | 0.8733 | 0.0147 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | fixed-1024 | 0.8887 | 0.0157 | 0.8897 | 0.0154 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | section-aware | 0.7679† | 0.0419† | 0.8749 | 0.0149 | n/a: no embedder | n/a: no reranker | n/a: no reranker |
| bm25 | none | small-to-big | 0.7410† | 0.0394† | 0.8542 | 0.0144 | n/a: no embedder | n/a: no reranker | n/a: no reranker |

`n/a: chunk > budget`: a fixed chunking whose chunk is bigger than the budget is not scored at that budget.
`n/a: no embedder`: BM25 reads no embedder, so it has one row per chunking and nothing to truncate.
`n/a: no reranker`: only the production line reranks, so only it has an unreranked tail.
`truncated chunks`: share of the chunking's chunks longer than the embedder's input limit (in its own tokens, task prefix included), which it embeds truncated; ‡ marks a share above zero.
`tail used`: share of questions whose packing went past the reranked top 30 into the unreranked tail (fused order).
†: the top-N cap binds for at least half of the questions (see R2).
