# R15 - v2-answers: the model-graded check of the answer score

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

- grader: `claude-sonnet-5-5` (served by `claude-sonnet-5-5`) through the `claude` command-line tool in headless mode (2.1.296 (Claude Code)), effort medium, no tools, on a subscription login; never a paid API
- grader prompt: `configs/v2/grader-prompt.txt` (sha256 `8e1445fd3f77ee8252a32e3898c30813dc5d9192406c1fc799e9bc7a84b63c65`), fixed before any answer existed
- graded: 100 questions (50 per dataset, Natural Questions half precise and half context, seed 0) x 3 setups = 300 answers; 286 grader calls in the run that wrote this table, 14 from the cache
- tokens: 294095 input, 9958 output
- agreement: the answer score counts as a pass at or above 0.5 (short-answer match: an exact match), and agrees when that matches the grader's verdict

## Agreement per dataset

AUC: the chance that a random answer the grader passes has a higher answer score than a random one it fails, ties counting half (1.0: the score separates them perfectly; 0.5: no better than chance).

| dataset | answers | grader pass rate | mean answer score | mean score, passes | mean score, fails | AUC | agreement |
|---|---|---|---|---|---|---|---|
| pooled | 300 | 0.4233 | 0.1430 | 0.2046 | 0.0977 | 0.6037 | 0.6167 |
| qasper | 150 | 0.1800 | 0.1221 | 0.2592 | 0.0920 | 0.8097 | 0.8467 |
| nq | 150 | 0.6667 | 0.1639 | 0.1899 | 0.1118 | 0.5654 | 0.3867 |
| nq precise | 75 | 0.6800 | 0.0533 | 0.0784 | 0.0000 | 0.5392 | 0.3733 |
| nq context | 75 | 0.6533 | 0.2744 | 0.3059 | 0.2150 | 0.6962 | 0.4000 |

Natural Questions precise questions scored by contains-a-reference instead: agreement 0.7733, AUC 0.8002, mean of passes 0.7255 against fails 0.1250.

## Per setup

| dataset | setup | answers | grader pass rate | mean answer score | agreement |
|---|---|---|---|---|---|
| pooled | section-aware | 100 | 0.5400 | 0.1657 | 0.5200 |
| pooled | oracle | 100 | 0.4700 | 0.1494 | 0.5700 |
| pooled | no-retrieval | 100 | 0.2600 | 0.1139 | 0.7600 |
| qasper | section-aware | 50 | 0.2600 | 0.1279 | 0.7800 |
| qasper | oracle | 50 | 0.1800 | 0.1338 | 0.8600 |
| qasper | no-retrieval | 50 | 0.1000 | 0.1047 | 0.9000 |
| nq | section-aware | 50 | 0.8200 | 0.2035 | 0.2600 |
| nq | oracle | 50 | 0.7600 | 0.1649 | 0.2800 |
| nq | no-retrieval | 50 | 0.4200 | 0.1232 | 0.6200 |

## Does the setup ranking hold under the grader?

| dataset | by mean answer score | by grader pass rate | same order |
|---|---|---|---|
| pooled | section-aware > oracle > no-retrieval | section-aware > oracle > no-retrieval | yes |
| qasper | oracle > section-aware > no-retrieval | section-aware > oracle > no-retrieval | no |
| nq | section-aware > oracle > no-retrieval | section-aware > oracle > no-retrieval | yes |

No dataset text, prompt or answer is committed: only ids, hashes, scores and verdicts.
