# R4 - qasper grid, production line and ablations: fixed-k

Config hash: `97bc8de66def0c97a34aaefe87bc535bd43e7b8f2f2320a696721ee5ab74df62`

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
| dev | `2ae7ee62a65b1c4225791c70de80c2aad4e8998cf1fd4f09a53103db4f21af93` |
| test | `6e29ad410e6e39aa1936017fb965b30a20eb2e7751997f55b97c9d281aa884e5` |

## Questions

| query type | n |
|---|---|
| precise | 1317 |
| context | 404 |
| mixed | 476 |
| total | 2197 |

## Production line: hybrid, then the reranker over the fused top 30, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.8856, fixed-1024 0.9101, section-aware 0.0810.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0774 | 0.2330 | 0.3022 | 0.0201 | 0.0809 | 0.1178 |
| fixed-128 | 0.0787 | 0.2553 | 0.3118 | 0.0323 | 0.1333 | 0.1835 |
| fixed-256 | 0.0951 | 0.2922 | 0.3391 | 0.0587 | 0.2118 | 0.2598 |
| fixed-512 | 0.1274 | 0.3245 | 0.3741 | 0.0944 | 0.2759 | 0.3254 |
| fixed-1024 | 0.1739 | 0.3528 | 0.4001 | 0.1499 | 0.3256 | 0.3727 |
| section-aware | 0.1129 | 0.2909 | 0.3432 | 0.1029 | 0.2732 | 0.3261 |
| small-to-big | 0.1088 | 0.2713 | 0.3309 | 0.1000 | 0.2537 | 0.3120 |

## Production line: hybrid, then the reranker over the fused top 30, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0765 | 0.2349 | 0.3018 | 0.0205 | 0.0809 | 0.1193 |
| fixed-128 | 0.0810 | 0.2558 | 0.3173 | 0.0340 | 0.1336 | 0.1863 |
| fixed-256 | 0.0942 | 0.2895 | 0.3364 | 0.0575 | 0.2088 | 0.2566 |
| fixed-512 | 0.1311 | 0.3254 | 0.3746 | 0.0972 | 0.2747 | 0.3270 |
| fixed-1024 | 0.1725 | 0.3582 | 0.4083 | 0.1485 | 0.3299 | 0.3809 |
| section-aware | 0.1111 | 0.2936 | 0.3464 | 0.1012 | 0.2765 | 0.3268 |
| small-to-big | 0.1065 | 0.2790 | 0.3418 | 0.0982 | 0.2590 | 0.3202 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.8856, fixed-1024 0.9101, section-aware 0.0810.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0692 | 0.2012 | 0.2558 | 0.0207 | 0.0695 | 0.1019 |
| fixed-128 | 0.0810 | 0.2121 | 0.2695 | 0.0379 | 0.1146 | 0.1556 |
| fixed-256 | 0.0910 | 0.2276 | 0.2831 | 0.0555 | 0.1634 | 0.2170 |
| fixed-512 | 0.1061 | 0.2408 | 0.3027 | 0.0781 | 0.2004 | 0.2602 |
| fixed-1024 | 0.1152 | 0.2476 | 0.3136 | 0.0982 | 0.2216 | 0.2894 |
| section-aware | 0.0783 | 0.2189 | 0.2754 | 0.0708 | 0.2031 | 0.2583 |
| small-to-big | 0.0801 | 0.2198 | 0.2799 | 0.0707 | 0.2039 | 0.2621 |

## Ablation: hybrid (BM25 + vector, reciprocal rank fusion), no reranker, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0696 | 0.2003 | 0.2681 | 0.0205 | 0.0716 | 0.1069 |
| fixed-128 | 0.0883 | 0.2262 | 0.2817 | 0.0387 | 0.1230 | 0.1684 |
| fixed-256 | 0.0970 | 0.2312 | 0.2877 | 0.0596 | 0.1654 | 0.2192 |
| fixed-512 | 0.1129 | 0.2467 | 0.3059 | 0.0836 | 0.2068 | 0.2642 |
| fixed-1024 | 0.1206 | 0.2544 | 0.3168 | 0.1028 | 0.2337 | 0.2954 |
| section-aware | 0.0783 | 0.2180 | 0.2836 | 0.0690 | 0.2026 | 0.2658 |
| small-to-big | 0.0883 | 0.2308 | 0.2922 | 0.0787 | 0.2114 | 0.2740 |

## Ablation: vector search only, bge-small

Share of chunks longer than bge-small's 512-token input, embedded truncated: fixed-512 0.8856, fixed-1024 0.9101, section-aware 0.0810.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0669 | 0.1634 | 0.2153 | 0.0190 | 0.0595 | 0.0840 |
| fixed-128 | 0.0646 | 0.1639 | 0.2144 | 0.0295 | 0.0861 | 0.1218 |
| fixed-256 | 0.0751 | 0.1657 | 0.2139 | 0.0454 | 0.1162 | 0.1573 |
| fixed-512 | 0.0801 | 0.1748 | 0.2185 | 0.0594 | 0.1437 | 0.1858 |
| fixed-1024 | 0.0792 | 0.1616 | 0.2030 | 0.0669 | 0.1427 | 0.1826 |
| section-aware | 0.0646 | 0.1593 | 0.2066 | 0.0572 | 0.1465 | 0.1932 |
| small-to-big | 0.0614 | 0.1711 | 0.2185 | 0.0546 | 0.1568 | 0.2032 |

## Ablation: vector search only, nomic

No chunk exceeds nomic's 8192-token input.

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0787 | 0.1812 | 0.2353 | 0.0222 | 0.0642 | 0.0952 |
| fixed-128 | 0.0856 | 0.1866 | 0.2426 | 0.0382 | 0.1012 | 0.1417 |
| fixed-256 | 0.0833 | 0.1871 | 0.2399 | 0.0501 | 0.1278 | 0.1772 |
| fixed-512 | 0.0797 | 0.1812 | 0.2321 | 0.0574 | 0.1476 | 0.1974 |
| fixed-1024 | 0.0769 | 0.1807 | 0.2230 | 0.0647 | 0.1631 | 0.2044 |
| section-aware | 0.0760 | 0.1834 | 0.2326 | 0.0678 | 0.1678 | 0.2141 |
| small-to-big | 0.0860 | 0.2080 | 0.2572 | 0.0775 | 0.1929 | 0.2385 |

## Ablation: BM25 only

### Fixed-k retrieval, collection search (for comparison with the literature only)

| chunking | hit@1 | hit@5 | hit@10 | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|
| fixed-64 | 0.0596 | 0.1780 | 0.2353 | 0.0170 | 0.0608 | 0.0894 |
| fixed-128 | 0.0746 | 0.2066 | 0.2745 | 0.0332 | 0.1071 | 0.1573 |
| fixed-256 | 0.0869 | 0.2271 | 0.2845 | 0.0526 | 0.1624 | 0.2168 |
| fixed-512 | 0.1161 | 0.2645 | 0.3286 | 0.0826 | 0.2198 | 0.2841 |
| fixed-1024 | 0.1507 | 0.3027 | 0.3600 | 0.1277 | 0.2784 | 0.3358 |
| section-aware | 0.0683 | 0.2053 | 0.2722 | 0.0602 | 0.1900 | 0.2558 |
| small-to-big | 0.0715 | 0.2117 | 0.2763 | 0.0619 | 0.1953 | 0.2581 |

Units are whole retrieved chunks with no token budget (small-to-big: the distinct parents of the matched children). A unit is relevant when it overlaps the labelled spans; hit@k is whether any of the top k is relevant, recall@k the share of the document's relevant units in the top k, best annotator kept.
