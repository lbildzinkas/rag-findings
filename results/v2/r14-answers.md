# R14 - v2-answers: answer score per setup and dataset

Config hash: `7863aeefe67178ee6d38f8c3ddbcffc474219e9dc38e235e0463e602a3100b92`

## Config

```yaml
budget: 1024
confidence: 0.95
dataset:
  name: pooled
  sources:
  - name: qasper
    splits:
    - dev
    - test
  - name: nq
    splits:
    - dev
embedder: nomic
grader:
  effort: medium
  max_attempts: 4
  model: claude-sonnet-5-5
  pause_seconds: 5.0
  prompt: configs/v2/grader-prompt.txt
  prompt_sha256: 8e1445fd3f77ee8252a32e3898c30813dc5d9192406c1fc799e9bc7a84b63c65
  questions_per_dataset: 50
  seed: 0
  threshold: 0.5
kind: answers
oracle_chunkings:
- fixed-64
- fixed-128
- fixed-256
- fixed-512
- section-aware
- small-to-big
- fixed-1024
pipeline: hybrid-rerank
reader:
  max_new_tokens: 256
  model:
    id: mlx-community/Qwen3-8B-4bit
    revision: 545dc4251c05440727734bcd94334791f6ab0192
resamples: 10000
run_name: v2-answers
sample: configs/v2/reader-sample.txt
scope: collection
seed: 0
setups:
- chunking: section-aware
  kind: packed
  name: section-aware
  runs:
    nq: v2-baseline
    qasper: v2-baseline
- kind: oracle
  name: oracle
  runs:
    nq: v2-baseline
    qasper: v2-baseline
- kind: none
  name: no-retrieval
top_n: 20
view: budget
```

## Inputs

- reader prompt template hash: `9bf28410208fd69958bf3e5c67180b2127c7d95d7d13a3740126aa4e5508e5b5`
- reader sample: `configs/v2/reader-sample.txt` (seed 0)
- reader: `mlx-community/Qwen3-8B-4bit@545dc4251c05440727734bcd94334791f6ab0192` (decoding greedy, max_new_tokens 256, thinking False; settings hash `00d28b9deff9e6fee3f46da7efe72fe0ab989a195cbeef3f3471e4ad62b26d92`)
- reader runtime: mlx 0.31.1, mlx-lm 0.29.1

## Answer score per setup and dataset

Answer score: the dataset's standard answer metric per question (QASPER: answer F1; Natural Questions: short-answer match on precise questions, token F1 against the long-answer paragraph on context questions). CIs: paired bootstrap over documents (10000 resamples, seed 0), percentile intervals at 95%.

| dataset | setup | n | answer score | CI | difference from section-aware | CI |
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

## Natural Questions by query type (point estimates)

Precise questions: short-answer match, with contains-a-reference as the secondary column. Context questions: token F1 against the long-answer paragraph.

| setup | precise n | short-answer match | contains | context n | token F1 |
|---|---|---|---|---|---|
| section-aware | 250 | 0.1600 | 0.6560 | 250 | 0.2891 |
| oracle | 250 | 0.1240 | 0.7000 | 250 | 0.3104 |
| no-retrieval | 250 | 0.0520 | 0.2800 | 250 | 0.1974 |

## Reader latency per answer

Seconds per answer for the call that produced it (prompt prefill plus generation, one prompt at a time); generated tokens include the stop token; truncated: answers that hit the new-token limit.

| dataset | setup | n | mean s | median s | p90 s | max s | prompt tokens (mean) | generated tokens (mean) | truncated |
|---|---|---|---|---|---|---|---|---|---|
| pooled | section-aware | 1000 | 3.52 | 3.39 | 4.45 | 7.43 | 1095 | 45.8 | 0 |
| pooled | oracle | 1000 | 3.29 | 3.23 | 4.06 | 6.78 | 1105 | 43.8 | 0 |
| pooled | no-retrieval | 1000 | 0.66 | 0.60 | 1.00 | 3.60 | 31 | 28.7 | 0 |
| nq | section-aware | 500 | 3.35 | 3.22 | 4.19 | 7.19 | 1114 | 37.9 | 0 |
| nq | oracle | 500 | 3.24 | 3.15 | 3.97 | 5.46 | 1120 | 38.9 | 0 |
| nq | no-retrieval | 500 | 0.71 | 0.62 | 1.10 | 3.36 | 33 | 30.7 | 0 |
| qasper | section-aware | 500 | 3.68 | 3.57 | 4.65 | 7.43 | 1076 | 53.6 | 0 |
| qasper | oracle | 500 | 3.35 | 3.27 | 4.09 | 6.78 | 1090 | 48.7 | 0 |
| qasper | no-retrieval | 500 | 0.61 | 0.58 | 0.85 | 3.60 | 29 | 26.6 | 0 |

- answers: 3000 from 2833 distinct prompts (setups that hand the reader the same chunks share one answer); 2738 model calls in the run that wrote this table, 262 answers from the response cache
- reader time, the sum of the distinct prompts' latencies: 1.92 h
- wall time of the run that wrote this table: 110.5 min
- tokens: 2068141 prompt, 110063 generated; a local model, so no per-call cost

No dataset text, prompt or answer is committed: only ids, hashes and scores.
