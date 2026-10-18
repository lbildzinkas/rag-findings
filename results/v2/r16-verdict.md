# R16 - v2-verdict: the pre-registered bar, the tie-break, answers, latency and cost

Config hash: `fa2f43a25994cb11c8f9b360c2735d5e800ccf0e4c97db341e8111dd3bc6a9a5`

## Config

```yaml
answers:
  run: v2-answers
  setups:
  - section-aware
  - oracle
  - no-retrieval
bar:
  confidence: 0.95
  max_loss: 0.01
  min_gain: 0.02
  resamples: 10000
  seed: 0
  tie: 0.01
budget: 1024
budget_top_n: 20
contenders:
- name: late-128
  run: v2-late
  table: r12
- name: late-256
  run: v2-late
  table: r12
- name: confidence routing
  reference_run: v2-baseline
  routed: true
  run: v2-routers
  system: confidence
  table: r11
- name: search-all routing
  reference_run: v2-baseline
  routed: true
  run: v2-routers
  system: search-all
  table: r11
- name: contextual-256
  run: v2-contextual
  table: r13
- name: section-aware-titles
  run: v2-titles
  table: r17
datasets:
- qasper
- nq
depth50:
  contender: section-aware-titles
  runs:
  - v2-titles
  - v2-depth50
embedder: nomic
kind: verdict
latency: results/v2/latency-profile.json
notes:
- The pre-registered order names late chunking, confidence routing, search-all routing
  and contextual chunks. section-aware-titles joined the contenders afterwards (ADR
  0005 amendment, 2026-10-18) and is placed last, so it could never win a tie against
  a pre-registered contender.
oracle:
  chunkings:
  - fixed-64
  - fixed-128
  - fixed-256
  - fixed-512
  - section-aware
  - small-to-big
  - fixed-1024
  run: v2-baseline
pipeline: hybrid-rerank
prefixes_manifest: results/prefixes/fixed-256-qwen3-8b.json
run_name: v2-verdict
scope: collection
secondary_budgets:
- 512
- 2048
side_variants:
- name: contextual-256-prefixed
  run: v2-contextual
  table: r13
top_n: 8
```

## Inputs

| run | config hash |
|---|---|
| nq/v2-baseline | `b88ce9188b6e18537719b8dc5850675abc3f472d121b8683b761ac304b576f9f` |
| nq/v2-contextual | `c2b3f7a5067ebfe8fd56be5157f08019a7f985aa9c57fe528db93ecf9397a053` |
| nq/v2-depth50 | `c890dcea23c364405b79cd1aae2e9603ade83b11641b29c30a7397200f3beeb6` |
| nq/v2-late | `9ef43d53b9923e4098976e4539a9426dd274124f3e2e85c2e00d7827fc568dbd` |
| nq/v2-routers | `f15eabd39780d5ba429c7f3fd8cc8e6b61a5155900ad83094f366ff3b1505c0b` |
| nq/v2-titles | `3bd1a0559ea19a538444eb855a7d0b93a494388536e92193c588ae8363f66b03` |
| qasper/v2-baseline | `28fc1dc15c8ac341b982544b402db094b15997c8b808cf9733d9f9d734cb51d7` |
| qasper/v2-contextual | `01d4edda6b8a81e5cf45e9c645d840b44d539c024c91adadd154c8159ab1865d` |
| qasper/v2-depth50 | `c56e6f53497ce83caea0c09dd53e62c9c880ca19a18eb645ccce6b7b97c90651` |
| qasper/v2-late | `4681531b4fc2cba80eacfd6d6d987877685b745fa621c2cfb91bede19c7a8be7` |
| qasper/v2-routers | `bde74c2df035145fcc0e87b372eb7209b582e35b8fd3f5f3d60730e4deb96b1b` |
| qasper/v2-titles | `0b60e4811932349583d9714f63881085d1a05ccf6f3a85633dc11623bbb3d908` |
| v2-answers | `7863aeefe67178ee6d38f8c3ddbcffc474219e9dc38e235e0463e602a3100b92` |

## Verdict

**Verdict: section-aware-titles replaces section-aware.**

Judged on the hybrid-rerank pipeline with nomic, collection search, budget view (top-N cap 20) at 1024 tokens, pooled over qasper and nq, with a 95% CI from the paired, document-clustered bootstrap (10000 resamples, seed 0).

The bar (ADR 0008, read as its amendments record):

1. Gain: pooled retrieval recall at least +0.0200 over section-aware, with the CI excluding 0.
2. Datasets: on each dataset alone, recall no worse than section-aware's by more than 0.0100 (point estimate, the CI reported beside it).
3. Answers: an answer score no worse than section-aware's by more than 0.0100 (point estimate), where the contender's answers were measured.

Tie-break: among the contenders that pass, the highest pooled recall wins unless a simpler one is within 0.0100 of it (point estimates). Simplest first: late-128, late-256, confidence routing, search-all routing, contextual-256, section-aware-titles. Section-aware stays if none passes.

The pre-registered order names late chunking, confidence routing, search-all routing and contextual chunks. section-aware-titles joined the contenders afterwards (ADR 0005 amendment, 2026-10-18) and is placed last, so it could never win a tie against a pre-registered contender.

## Contenders against section-aware

Recall differences from section-aware at the bar's cell. Share of the oracle ceiling captured: (contender - section-aware) / (oracle router - section-aware), point estimates, the oracle router from v2-baseline.

| contender | own table | pooled difference | CI | qasper difference | nq difference | gain | datasets | answers | share of oracle captured | tie-break | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| late-128 | R12 | -0.0686 | [-0.0810, -0.0561] | -0.0534 | -0.1020 | fail | fail | not measured | -50.0% | does not enter | late-128 does not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100). |
| late-256 | R12 | -0.0581 | [-0.0707, -0.0458] | -0.0497 | -0.0765 | fail | fail | not measured | -42.3% | does not enter | late-256 does not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100). |
| confidence routing | R11 | -0.0422 | [-0.0527, -0.0318] | -0.0382 | -0.0511 | fail | fail | not measured | -30.7% | does not enter | confidence routing does not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100). |
| search-all routing | R11 | -0.0250 | [-0.0370, -0.0129] | -0.0200 | -0.0360 | fail | fail | not measured | -18.2% | does not enter | search-all routing does not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100). |
| contextual-256 | R13 | -0.0179 | [-0.0303, -0.0058] | -0.0117 | -0.0317 | fail | fail | not measured | -13.1% | does not enter | contextual-256 does not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100). |
| section-aware-titles | R17 | +0.0228 | [+0.0128, +0.0331] | +0.0168 | +0.0361 | pass | pass | not measured | 16.6% | wins: the only contender that passes | section-aware-titles clears the bar and replaces section-aware. |

Per-dataset intervals (the datasets check reads the point estimates):

- late-128: qasper -0.0534 [-0.0678, -0.0388], nq -0.1020 [-0.1265, -0.0779]
- late-256: qasper -0.0497 [-0.0642, -0.0355], nq -0.0765 [-0.1007, -0.0514]
- confidence routing: qasper -0.0382 [-0.0502, -0.0261], nq -0.0511 [-0.0716, -0.0307]
- search-all routing: qasper -0.0200 [-0.0337, -0.0066], nq -0.0360 [-0.0610, -0.0115]
- contextual-256: qasper -0.0117 [-0.0257, +0.0025], nq -0.0317 [-0.0562, -0.0076]
- section-aware-titles: qasper +0.0168 [+0.0055, +0.0281], nq +0.0361 [+0.0153, +0.0573]

## Section-aware references

Each contender is paired with the section-aware rows of the run behind its own table, so its numbers agree with that table.

| contender | own table | contender run | section-aware reference run | differs from v2-baseline (R7) |
|---|---|---|---|---|
| late-128 | R12 | v2-late | v2-late | no question at any cell read here |
| late-256 | R12 | v2-late | v2-late | no question at any cell read here |
| confidence routing | R11 | v2-routers | v2-baseline | no question at any cell read here |
| search-all routing | R11 | v2-routers | v2-baseline | no question at any cell read here |
| contextual-256 | R13 | v2-contextual | v2-contextual | no question at any cell read here |
| section-aware-titles | R17 | v2-titles | v2-titles | no question at any cell read here |

## R7 reproduced at the bar's cell

The same bootstrap, recomputed from the baseline runs: the best single chunking is re-selected inside every resample, as in R7.

| group | best single chunking | section-aware recall | oracle router recall | routing headroom | CI |
|---|---|---|---|---|---|
| pooled | section-aware | 0.4269 | 0.5641 | +0.1373 | [+0.1263, +0.1485] |
| nq | section-aware | 0.8197 | 0.9583 | +0.1386 | [+0.1184, +0.1594] |
| qasper | section-aware | 0.2480 | 0.3847 | +0.1367 | [+0.1238, +0.1496] |

Oracle router minus section-aware, pooled (the share's denominator): +0.1373.

## Answer scores (the reader stage, R14)

| group | setup | n | answer score | CI | difference from section-aware | CI |
|---|---|---|---|---|---|---|
| pooled | section-aware | 1000 | 0.1822 | [+0.1682, +0.1962] | - | - |
| pooled | oracle | 1000 | 0.1889 | [+0.1750, +0.2028] | +0.0067 | [-0.0037, +0.0168] |
| pooled | no-retrieval | 1000 | 0.1193 | [+0.1101, +0.1290] | -0.0628 | [-0.0760, -0.0496] |
| nq | section-aware | 500 | 0.2246 | [+0.1999, +0.2492] | - | - |
| nq | oracle | 500 | 0.2172 | [+0.1943, +0.2404] | -0.0074 | [-0.0257, +0.0102] |
| nq | no-retrieval | 500 | 0.1247 | [+0.1093, +0.1416] | -0.0998 | [-0.1233, -0.0764] |
| qasper | section-aware | 500 | 0.1398 | [+0.1269, +0.1530] | - | - |
| qasper | oracle | 500 | 0.1606 | [+0.1461, +0.1760] | +0.0208 | [+0.0112, +0.0308] |
| qasper | no-retrieval | 500 | 0.1140 | [+0.1045, +0.1233] | -0.0258 | [-0.0384, -0.0137] |

The reader stage read section-aware, oracle, no-retrieval only. No contender's answers were measured (late-128, late-256, confidence routing, search-all routing, contextual-256, section-aware-titles): the answer guard was dropped by the 2026-10-17 amendment to ADR 0008, and the reader stage's three setups were fixed before section-aware-titles ran, so the answers check reads "not measured" and decides nothing.

## Secondary results (they decide nothing)

### Other budgets, budget view

Pooled recall difference from section-aware. CIs: 95% unadjusted at 1024 tokens, Holm-adjusted over the other budgets per system, as in v1 (the level column gives each interval's level).

| system | 512 difference | CI | level | 1024 difference | CI | level | 2048 difference | CI | level |
|---|---|---|---|---|---|---|---|---|---|
| late-128 | -0.0348 | [-0.0500, -0.0195] | 97.50% | -0.0686 | [-0.0810, -0.0561] | 95.00% | -0.0706 | [-0.0827, -0.0584] | 95.00% |
| late-256 | -0.0422 | [-0.0577, -0.0269] | 97.50% | -0.0581 | [-0.0707, -0.0458] | 95.00% | -0.0487 | [-0.0600, -0.0372] | 95.00% |
| confidence routing | -0.0626 | [-0.0762, -0.0491] | 97.50% | -0.0422 | [-0.0527, -0.0318] | 95.00% | -0.0573 | [-0.0673, -0.0471] | 95.00% |
| search-all routing | +0.0084 | [-0.0036, +0.0206] | 95.00% | -0.0250 | [-0.0370, -0.0129] | 95.00% | -0.0200 | [-0.0327, -0.0077] | 97.50% |
| contextual-256 | +0.0015 | [-0.0142, +0.0169] | 97.50% | -0.0179 | [-0.0303, -0.0058] | 95.00% | -0.0118 | [-0.0241, +0.0007] | 97.50% |
| section-aware-titles | +0.0183 | [+0.0069, +0.0300] | 95.00% | +0.0228 | [+0.0128, +0.0331] | 95.00% | +0.0255 | [+0.0144, +0.0368] | 97.50% |
| contextual-256-prefixed | -0.0915 | [-0.1081, -0.0752] | 97.50% | -0.0584 | [-0.0712, -0.0458] | 95.00% | -0.0358 | [-0.0469, -0.0248] | 95.00% |

### Production view (top-N cap 8), 1024 tokens

| system | pooled difference | CI | qasper difference | nq difference |
|---|---|---|---|---|
| late-128 | -0.0680 | [-0.0804, -0.0556] | -0.0525 | -0.1020 |
| late-256 | -0.0574 | [-0.0701, -0.0451] | -0.0488 | -0.0765 |
| confidence routing | -0.0540 | [-0.0647, -0.0435] | -0.0489 | -0.0652 |
| search-all routing | -0.0266 | [-0.0385, -0.0146] | -0.0222 | -0.0361 |
| contextual-256 | -0.0173 | [-0.0296, -0.0052] | -0.0108 | -0.0317 |
| section-aware-titles | +0.0234 | [+0.0133, +0.0336] | +0.0177 | +0.0361 |
| contextual-256-prefixed | -0.0577 | [-0.0705, -0.0452] | -0.0401 | -0.0966 |

### Side variants at the bar's cell

- contextual-256-prefixed (R13, not a contender): -0.0584 [-0.0712, -0.0458]; qasper -0.0410, nq -0.0966; would not clear the bar (its pooled gain is below +0.0200; nq and qasper alone are below -0.0100).

### Depth-50 side run

Section-aware and section-aware-titles reranked to depth 50 (v2-depth50) next to depth 30 (v2-titles), at the bar's cell, pooled.

| system | recall, depth 30 | recall, depth 50 | depth 50 - depth 30 | CI |
|---|---|---|---|---|
| section-aware | 0.4269 | 0.4319 | +0.0051 | [+0.0006, +0.0096] |
| section-aware-titles | 0.4497 | 0.4529 | +0.0032 | [-0.0018, +0.0084] |

| rerank depth | section-aware-titles - section-aware | CI | per dataset | bar's retrieval checks |
|---|---|---|---|---|
| 30 | +0.0228 | [+0.0128, +0.0331] | qasper +0.0168, nq +0.0361 | pass |
| 50 | +0.0209 | [+0.0108, +0.0311] | qasper +0.0155, nq +0.0327 | pass |

Section-aware's budget-view list packs chunks from past the reranked head for 66.8% of questions at depth 30 and 58.2% at depth 50. A depth-50 rerank moves the margin from +0.0228 to +0.0209; it does not change whether the margin clears the bar's retrieval checks.

## Adoption profile

### Query path, uncached

Milliseconds per question, mean / median / p90, over 100 seeded questions (50 nq, 50 qasper; seed 0), after 1 untimed warm-up question per system. Every query vector and reranker score is computed by the model (the embedding and score caches are not used); searches run over the runs' own indexes, 1000 deep. Probe config hash `eaece7587765084e81c5450701c5abd356f814257914faddb6749c40ea841449`.

| system | searches | reranker pairs (mean) | query embedding ms | searches ms | reranker ms | total ms |
|---|---|---|---|---|---|---|
| section-aware | 2 | 30.0 | 12.0 / 9.3 / 12.6 | 27.7 / 22.1 / 31.1 | 804.1 / 743.1 / 1101.1 | 843.8 / 787.2 / 1167.7 |
| late-128 | 2 | 30.0 | 10.6 / 9.7 / 13.8 | 35.7 / 29.0 / 41.7 | 269.8 / 262.6 / 333.2 | 316.1 / 294.3 / 373.5 |
| late-256 | 2 | 30.0 | 9.8 / 9.0 / 11.9 | 33.3 / 21.7 / 33.4 | 494.4 / 471.2 / 594.7 | 537.5 / 506.5 / 636.9 |
| confidence routing | 14 | 204.1 | 10.1 / 9.2 / 13.6 | 227.0 / 195.0 / 327.3 | 5761.6 / 5562.8 / 6949.4 | 5998.7 / 5807.6 / 7351.4 |
| search-all routing | 14 | 50.0 | 9.1 / 9.0 / 10.4 | 204.6 / 199.8 / 301.3 | 1607.6 / 1504.5 / 2137.3 | 1821.3 / 1721.3 / 2353.1 |
| contextual-256 | 2 | 30.0 | 10.1 / 9.4 / 12.0 | 27.0 / 22.4 / 30.7 | 605.3 / 583.5 / 711.5 | 642.4 / 623.7 / 756.5 |
| section-aware-titles | 2 | 30.0 | 10.3 / 9.4 / 12.4 | 29.9 / 23.0 / 35.8 | 819.3 / 748.7 / 1104.8 | 859.5 / 789.8 / 1148.1 |

- hardware: machine Mac16,6, chip Apple M4 Max, memory 36 GB, os macOS 27.0.1, device mps
- versions: chonkie 1.7.0, lancedb 0.40.0, pyarrow 26.0.0, python 3.12.11, pyyaml 6.0.3, rag-findings 0.1.0, sentence-transformers 5.7.0, tiktoken 0.14.0, torch 2.14.1, transformers 4.57.6
- models: embedder `nomic-ai/nomic-embed-text-v1.5@e9b6763023c676ca8431644204f50c2b100d9aab`, reranker `Alibaba-NLP/gte-reranker-modernbert-base@f7481e6055501a30fb19d090657df9ec1f79ab2c`

### Index-time cost

- qasper: section-aware indexes 12850 chunks; search-all and confidence routing index all 7 chunkings, 147935 chunks.
- nq: section-aware indexes 33915 chunks; search-all and confidence routing index all 7 chunkings, 401638 chunks.
- qasper: late chunking reads every document whole, 759 windows of at most 8192 tokens over 697 documents, one embedding pass serving late-128 and late-256.
- nq: late chunking reads every document whole, 1574 windows of at most 8192 tokens over 1000 documents, one embedding pass serving late-128 and late-256.
- contextual-256: one prefix per fixed-256 chunk written by `mlx-community/Qwen3-8B-4bit@545dc4251c05`, 49690 chunks in 30.4 h of generation (qasper 7.6 h, nq 22.8 h).
- section-aware-titles: a header per chunk from the dataset's own document and section titles; no model.

### Reader cost per question

- no-retrieval: 0.66 s per answer, 31 prompt tokens on average (mlx-community/Qwen3-8B-4bit@545dc4251c05440727734bcd94334791f6ab0192, local, no per-call cost).
- oracle: 3.29 s per answer, 1105 prompt tokens on average (mlx-community/Qwen3-8B-4bit@545dc4251c05440727734bcd94334791f6ab0192, local, no per-call cost).
- section-aware: 3.52 s per answer, 1095 prompt tokens on average (mlx-community/Qwen3-8B-4bit@545dc4251c05440727734bcd94334791f6ab0192, local, no per-call cost).

These tables regenerate byte-identically from the same runs and seed: nothing run-specific enters them.
