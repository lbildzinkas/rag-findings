# RAG chunking: does chunk size depend on query type, and how to test it fairly

Scout report for task `rag-chunking-research`, written 2026-10-10.
Scope: research only. Nothing was installed machine-wide, no paid API was used, no repository was created.
One small local pilot was run on QASPER with the Python standard library only (section 4, script in the appendix).

Claim labels used throughout:

- **[V]** verified by reading the primary source in this session (paper PDF text, official docs page, library source, dataset card or API).
- **[S]** secondary claim: a summary by someone else, or a primary source I could not open in full.
- **[M]** measured by me in this session; the command and output are in section 4 and the appendix.
- **[E]** my estimate or inference; treat as a hypothesis.

---

## 0. Short answer

1. **The hypothesis has real support, but almost all of it is confounded by token budget.** The most-cited study (Bhat et al. 2025) finds 64-128-token chunks best on SQuAD and 512-1024 best on NarrativeQA, TechQA and NQ [V], but it compares chunk sizes at a fixed top-k, so a 1024-token chunk at k=5 gives the reader 16 times the text of a 64-token chunk at k=5, and "relevant chunk" means "contains the answer string" [V]. Larger chunks then win partly because they contain more text.
2. **When the budget is held fixed, small units tend to win even on factoid open-domain QA** (Dense X: propositions beat passages at every word budget [V]). But they lose on narrative text, where propositions were the second-worst method on GutenQA (Recall@20 55.5 against 74.4 for recursive chunks) [V].
3. **My pilot on QASPER (BM25, within-paper, budget-matched) did not support the "context-heavy wants big chunks" half** [M]. With 512 words of context, 64-128-word chunks beat 512-word chunks for single-paragraph and multi-paragraph questions alike. The large-chunk penalty was smaller for multi-paragraph questions (+0.055 and +0.024 on dev and test), but both 95% intervals include zero. The **"precise wants small chunks" half was supported**: for extractive answers, the smallest chunks (32-64 words) recovered the most answer-span tokens at small budgets [M]. At fixed k=5 the same data "proves" the hypothesis for every stratum (+0.56 to +0.61 recall for 512 over 64), which shows how strong the artifact is [M].
4. **The effect depends on the embedding model.** Bhat et al.'s abstract says Stella prefers large chunks and Snowflake small ones, but their own table partly contradicts that (on COVID-QA, Stella peaks at 64 and Snowflake at 1024; on NQ, NewsQA and TechQA, Snowflake peaks at 1024) [V]. The robust point is only that the best size changes with the embedder. Interview-coach's current embedder, bge-small-en-v1.5, has a 512-token maximum input [V], so every chunk above about 512 tokens is truncated before embedding. That alone caps what a chunk-size test can show there.
5. **Strategies that get precision and context together all have the same shape: match on a small unit, return a larger one.** The shapes are small-to-big or parent-document, sentence window, auto-merging, LongRAG's MaxP, and late chunking. The measured gains are modest and mostly from weak setups (section 2). Hybrid BM25 + dense plus a reranker is the best-evidenced lever (Anthropic: retrieval failures 5.7% → 1.9% at top-20 [V]). Interview-coach's ADR 0003 already reached the same conclusion on its own QASPER runs [V].
6. **Chunk-id gold labels cannot compare chunkings.** Interview-coach's glossary currently defines the evaluation set as "questions with the study-material chunks that answer them" [V], and that has to become source spans (file + character offsets + quote) before any chunking experiment. Token-level recall/precision/IoU over spans (Chroma's method) works for any chunking [V].
7. **LLM context-relevance metrics are biased by chunk size by construction.** DeepEval's own docs say contextual relevancy rises if you "use smaller chunks" [V]. TruLens scores each chunk on 0-3 and averages [V]. Use them only as calibrated secondary metrics, never as the primary chunk-size comparison.
8. **QASPER alone is a weak test bed for this hypothesis** [M]. Papers are short (median about 3,400 words, roughly 4.5k tokens), so k × chunk size quickly covers the whole paper. Gold is paragraph-granular even for "precise" questions. Answer type is a poor proxy for "needs context": the multi-paragraph rate is 0.27-0.38 for every answer type. Annotators also disagree on evidence (test: 44% of questions have at least one annotator citing several paragraphs, but only 17% have all annotators doing so). Add Natural Questions, which has a paragraph-level long answer and a short-answer span for the same question.
9. **A fair experiment fits the budget at US$0 paid spend** [E]. It uses fixed token budgets, span gold, two corpora plus the owner's own labelled set, two embedders, BM25, hybrid and rerank, and paired paper-clustered bootstrap statistics. QASPER plus an NQ subset and the full chunker grid needs a few hours of local compute; contextual retrieval on a subset adds a few more (section 5.7).
10. **Repository**: run it as a measured experiment inside interview-coach first and extract it to a separate repo only if it grows into a multi-dataset benchmark (section 6). That is the first grilling question.

---

## 1. Evidence on "larger chunks for context-heavy queries, smaller for precise queries"

### 1.1 Studies that vary chunk size by dataset or query type

| Study | Datasets | Sizes, retriever | Metric | Result | Confounds |
|---|---|---|---|---|---|
| Bhat et al. 2025, *Rethinking Chunk Size for Long-Document Retrieval* (arXiv 2505.21700) [V] | NarrativeQA, NQ, SQuAD*, NewsQA*, COVID-QA*, TechQA* (* = short docs stitched into ≥50k-character documents) | Fixed token windows 64/128/256/512/1024, **no overlap**, LlamaIndex TokenTextSplitter; Stella-1.5B (decoder, >130k ctx) and Snowflake arctic-embed-l-v2.0 (encoder, 8k ctx) | Recall@1..5 = "relevant chunk in top-k", where the relevant chunk is the one containing the **answer string**; answers filtered to occur once | SQuAD (Stella) R@1: 64 → **0.642**, 512 → 0.498, 1024 → 0.386. NarrativeQA R@1: 0.042 (64) → 0.107 (1024). TechQA R@1: 0.049 (64) → 0.614 (512, Stella) / 0.715 (1024, Snowflake). NQ R@1 peaks at 512 (Stella 0.385) or 1024 (Snowflake 0.477). COVID-QA: Stella best at 64 (0.521), Snowflake best at 1024 (0.542) | Fixed k, so larger chunks get k × size more text. Answer-string matching favours big chunks. Stitched documents. No error bars. The prose and table disagree for SQuAD: the text says recall "increas[es] marginally with larger chunks", while Table 2 shows it falling |
| SmartChunk (Zhang et al., arXiv 2602.22225, Dec 2025) [V] | NarrativeQA, QASPER, QuALITY, NQ, NewsQA (out of domain) | RL-trained planner picks the chunk level per query (sentence … document) | Recall@5 contains gold answer span; GPT-4o judge for QA | Planner chose **avg 1,725 tokens on NarrativeQA** and **~230 on QASPER**. Overall QA 0.564 vs fixed-512 0.285, retrieval recall 0.829 vs 0.648 | Fixed k=5 across levels, so the budget varies. Learned system, not a controlled size sweep. Still the strongest evidence that the *preferred* size varies by dataset and query |
| Mix-of-Granularity (Zhong et al., COLING 2025, arXiv 2406.00456) [V] | Medical MCQA (MIRAGE: MMLU-Med, MedQA, MedMCQA, PubMedQA, BioASQ) | Router picks among 5 levels (½×, 1×, 2×, 4×, 8× MedRAG chunk size), BM25 | Answer accuracy | Router picked the **finest level most often on PubMedQA** ("questions… are typically precise"). Average accuracy gains over single-granularity MedRAG of about 0.01-0.08 depending on LLM, with ±0.02-0.05 per-dataset error bars. Sometimes below no-RAG chain-of-thought | Downstream accuracy only. Top-3 snippets truncated to fit the LLM, so the budget varies |
| NVIDIA blog (Han, June 2025) [S] | FinanceBench, DigitalCorpora767, others | 128-2,048 tokens, 15% overlap; page- and section-level | End-to-end accuracy | Page-level best on average (0.648). "Factoid queries" better with smaller chunks, "analytical" with larger or page-level | Blog, not peer-reviewed. I read only summaries of it. Generation-level metric |
| Jimeno Yepes et al. 2024, *Financial Report Chunking* (arXiv 2402.05131) [V] | FinanceBench (141 questions) | 128/256/512 tokens and element-based chunks, top-10 | Page accuracy (retrieval) and QA accuracy (GPT-4 and manual) | Retrieval page accuracy: 128 → 72.3, 256 → 73.1, **512 → 68.1** (smaller better). Manual QA accuracy: 128 → 35.5, 256 → 36.9, **512 → 48.2** (larger better) | Fixed k=10, so 512 gives 4× the reader budget of 128. A clean example of retrieval and generation metrics disagreeing about chunk size |
| Wang et al. 2024, *Searching for Best Practices in RAG* (arXiv 2407.01219) [V] | First 60 pages of one 10-K (lyft_2021), about 170 generated queries | 128-2,048 tokens | LlamaIndex faithfulness/relevancy | 512: 97.6/97.4, 256: 97.2/97.8, 2,048: 80.4/91.1 | One document, synthetic queries, LLM-judged, no error bars. Weak evidence |
| Chroma, Smith & Troynikov 2024 [V] | 5 small corpora, 472 generated queries with exact-match excerpts | Recursive/token splitters 200-800, semantic chunkers; text-embedding-3-large, k=5 | **Token-level** recall, precision, IoU | Recall is fairly flat (85-92%) across 200-800. Precision and IoU roughly double as size halves (Recursive 800/400 overlap: IoU 1.5; Recursive 200: 6.9) | Fixed k=5 again. Recall standard deviations of about ±30 points. No significance tests. Generated questions are "factual" by prompt design, so the query mix is skewed toward precise |
| LongRAG (Jiang et al. 2024, arXiv 2406.15319) [V] | NQ, HotpotQA (open-domain Wikipedia) | 100-word passages vs 4k-token grouped units | Answer recall@1 / @2 | NQ answer recall@1 52% (DPR passages) → **71%** with 4k units. HotpotQA recall@2 47% → 72% | Recall@1 of a 4k unit against a 100-word passage is the budget confound at its extreme. Scoring each unit by the max over its chunks (MaxP) is itself a small-to-big design |
| Dense X Retrieval (Chen et al., EMNLP 2024, arXiv 2312.06648) [V] | NQ, TQA, WebQ, SQuAD, EntityQuestions (Wikipedia) | Passage vs sentence vs proposition index | Recall@k; EM@l with a **fixed word budget** l=100/500 | Propositions beat passages: Recall@5 +12.0 and +9.3 for the two unsupervised retrievers (35% / 22.5% relative), Recall@20 +10.1 unsupervised / +2.7 supervised. EM@500 +2.7 to +4.1. "Finer-grained retrieval has a higher recall across all numbers of words" (GTR) | Only Wikipedia factoid QA, which is the "precise" half of the hypothesis. Fixed budget, so this is the fair design |
| LumberChunker (Duarte et al. 2024, arXiv 2406.17526) [V] | GutenQA (100 public-domain books, 3,000 "needle" questions) | Semantic, paragraph, recursive, proposition, LLM chunking | DCG@k, Recall@k | Recall@20: propositions **55.5**, recursive 74.4, LLM-segmented 77.9. The authors say propositions excel on "fine-grained, fact-based" Wikipedia text but are "less effective for narrative texts" | Fixed k. LLM chunker uses a paid model |
| Late chunking (Günther et al., arXiv 2409.04701) [V] | BEIR subsets, LongEmbed | 16-512-token chunks, naive vs late | nDCG@10 at **document** level | Late chunking helps most for small chunks. For some reading-comprehension tasks naive chunking wins with large chunks | Document-level relevance, not passage-level |

### 1.2 Where the effect holds and where it does not

- **Holds (direction)** [V]: highly localized, entity-style answers (SQuAD, PubMedQA in MoG, Wikipedia factoids in Dense X) prefer small units. Long, dispersed or narrative answers (NarrativeQA, TechQA, NQ long answers) prefer larger units in fixed-k comparisons. A learned planner, given the choice, picks large units for narrative and small ones for scientific QA (SmartChunk).
- **Model-dependent** [V]: on the same COVID-QA data, Stella's best size is 64 and Snowflake's is 1024 (Bhat). Bhat attributes this to context length and architecture, though the paper's general claim (Stella likes large chunks, Snowflake small ones) does not match its own COVID-QA, NQ, NewsQA and TechQA rows.
- **Does not hold, or not shown, under a fixed budget** [V]+[M]: Dense X finds finer units better at every word budget on factoid QA. My QASPER pilot finds 64-128-word chunks best at a fixed budget for multi-paragraph questions too (section 4). I found **no published study that sweeps chunk size by query type at a matched reader budget with paired significance tests**. That gap is what the proposed experiment fills.

### 1.3 The confounds, and how to neutralise each one

| Confound | Why it matters | Control |
|---|---|---|
| **top-k × chunk size = budget** | Every fixed-k study above hands larger chunks more text. Bhat's 1024 × k=5 is 5,120 tokens against 320 for 64 × 5 [V]. In my pilot the fixed-k=5 "advantage" of 512-word over 64-word chunks is +0.56 to +0.61 token recall, and it flips to −0.07 to −0.10 at a fixed 512-word budget [M] | Report recall at fixed token budgets (B = 256, 512, 1024, 2048). Fill the budget in rank order, then truncate. Report fixed-k only to reproduce the literature |
| **Embedding model context length and pooling** | Text past `max_seq_length` is silently cut off, so a 1024-token chunk embedded by a 512-token model is judged on its first half. bge-small-en-v1.5: 512 [V]. nomic-embed-text-v1.5 and BGE-M3: 8192 [V]. Stella and Snowflake peak at different sizes on the same data [V] | Include one short-context and one long-context embedder. Never test sizes above an embedder's limit without saying so |
| **Overlap** | Raises recall but repeats tokens, and IoU penalises the repetition (Chroma: Recursive 400 with 200 overlap has IoU 3.3, without overlap 3.6) [V]. Overlap neither helped nor hurt in late-chunking experiments [V] | Hold overlap at 0 for the main grid. Test overlap as a single separate factor |
| **Relevance definition** | "Chunk contains the answer string" favours big chunks and fails for abstractive answers. Chunk-id labels break on re-chunking (section 3.2) | Span/token gold |
| **Answer generation versus retrieval-only** | FinanceBench: smaller chunks retrieved the right page more often while larger chunks gave better answers [V]. Readers also show position and distraction effects | Measure retrieval first at a matched budget. Generation goes in a second, smaller arm with the same budget for every configuration |
| **Document length versus budget** | QASPER papers have a median of about 3,400 words [M]. At k=5 × 512 words the reader sees about 2,350 words, roughly two-thirds of a median paper, so "recall" approaches "read the paper" | Small budgets, or longer documents (NQ pages run to about 7k tokens [V, Bhat Table 1]; NarrativeQA about 52k [V]) |
| **Question-type proxy** | Answer type is not "needs context" (section 4) | Label types from gold structure: evidence count and dispersion |

---

## 2. Strategies that aim for both precision and context

"Fits M4 Max" assumes 36 GB unified memory and local models through sentence-transformers or MLX [E].

| Strategy | What it is | Measured gain, and on what | Cost | Fits a local M4 Max setup? |
|---|---|---|---|---|
| **Small-to-big / parent-document** | Index small child chunks; on a hit, return the parent (section, paragraph or fixed parent) | Wang et al.: small2big faithfulness 95.7 → 96.7 (one 10-K, about 170 synthetic queries) [V]. LongRAG's MaxP (score a long unit by its best chunk) is the same idea at scale, with large recall@1 gains but budget-confounded [V]. No rigorous budget-matched study found | Extra docstore lookup. Budget must be capped or parents swamp the context | **Yes.** Trivial in LanceDB (store `parent_id` and the span) |
| **Sentence window** | Embed single sentences; return ±N surrounding sentences (LlamaIndex `SentenceWindowNodeParser` + `MetadataReplacementPostProcessor`) | Wang et al.: "sliding window" 97.4/96.9 vs original 95.7/95.4 on the same weak setup [V]. The LlamaIndex demo page was not reachable (404) | Many more vectors (one per sentence) | Yes, but index size grows about 10× [E] |
| **Auto-merging (hierarchical)** | 2048/512/128 hierarchy; if enough sibling leaves are retrieved, merge into the parent [V] | LlamaIndex's own demo: correctness 4.27 vs 4.21 base, relevancy and faithfulness identical, pairwise preference 0.525, on 60 GPT-4-generated questions about one paper; described as "roughly the same" [V] | Docstore and merge logic | Yes. Weak evidence of benefit |
| **Propositions (Dense X)** | LLM rewrites text into atomic, self-contained facts; index those | Recall@5 +9 to +12 for unsupervised retrievers; EM@500 +2.7 to +4.1 on Wikipedia factoid QA [V]. **Worse on narrative** (GutenQA R@20 55.5 vs 74.4) [V] | One LLM pass over the corpus. Index has about 6× more units than passages (English Wikipedia: 256.9M propositions of 11.2 words on average vs 41.4M passages of 58.5 words) [V] | Possible locally with the Apache-2.0 `propositionizer-wiki-flan-t5-large` [V], but it was trained on Wikipedia. Its fit for markdown study notes is untested |
| **Mix-of-granularity / routing** | Index several sizes; a router (trained, or a rule on query type) picks the level | MoG: about +0.01 to +0.08 average accuracy on medical MCQA, BM25 retriever [V]. SmartChunk: large QA gains over fixed 512 and comparable to RAPTOR at about 1/5 of the cost [V] | Multiple indexes. Router training (MoG: about 12 GB GPU, about 4 h per training run [V]) | Multi-index: yes. A trained router is premature unless an interaction is first shown to exist |
| **Late chunking** | Run a long-context embedder over the whole document, then mean-pool token embeddings per chunk span | +1.5 to +1.9 nDCG@10 averaged over 3 models × 4 BEIR sets [V]. Independent replication mixed: helps Jina-V2/V3, **hurts BGE-M3 badly** (NFCorpus nDCG@5 0.246 → 0.070) and Stella on MS MARCO (0.630 → 0.503) [V] | One long forward pass per document | Yes, for **mean-pooling** long models (nomic-embed-text-v1.5: mean pooling, 8k [V]). BGE-M3 uses CLS pooling and Qwen3-Embedding uses last-token pooling [V], which probably explains the BGE-M3 failure [E]. jina-embeddings-v3 is CC BY-NC 4.0 [V], so it is unsuitable for an MIT project. Chonkie ships a `LateChunker` [V] |
| **RAPTOR** | Recursive clustering plus LLM summaries; retrieve over the collapsed tree with a token cap | QASPER F1 (UnifiedQA, SBERT): 36.23 → 36.70; with GPT-4 reader 55.7 [V]. Equal 2,000-token budget for baselines [V] | One LLM summary per cluster per level. About 4% of summaries had minor hallucinations [V]. SmartChunk measured RAPTOR at 0.398 USD per query in its setup [V] | Feasible with a local LLM. Small QASPER gain; poor value for this project [E] |
| **Contextual retrieval** | LLM writes 50-100 tokens situating each chunk in its document; prepend before embedding and BM25 | Anthropic: failure rate (1 − recall@20) 5.7% → 3.7% (contextual embeddings), 2.9% (+ contextual BM25), **1.9%** (+ rerank) on codebases, fiction, arXiv and science papers [V]. One-time cost about 1.02 USD per million document tokens with prompt caching [V]. Independent: small gain with Jina-V3 + BM25 fusion + rerank on 20% of NFCorpus (nDCG@5 0.303 → 0.317), no error bars [V] | One LLM call per chunk; the whole document is prefix-cacheable | Yes, with a local MLX model or the GLM plan; see the runtime estimate in 5.7 |
| **Hybrid BM25 + dense (RRF)** | Fuse lexical and dense rankings | Part of Anthropic's 49% reduction (contextual BM25) [V]. Interview-coach ADR 0003 records that "the fused top 30 already held almost all the evidence" on its own QASPER runs [V] | Negligible | Already chosen (LanceDB) |
| **Cross-encoder reranking** | Rescore top-N with a cross-encoder | Anthropic: 2.9% → 1.9% failures [V]. ADR 0003: "the largest single gain" on the project's QASPER measurements [V] | N × query-chunk forward passes. Grows with chunk length | Yes. gte-reranker-modernbert-base (Apache-2.0, 8k positions) [V]; bge-reranker-v2-m3 and Qwen3-Reranker-0.6B are Apache-2.0 [V] |
| **Semantic chunking** | Split where adjacent-sentence embeddings diverge | Not justified by consistent gains over fixed size (Qu et al.) [V]. Chroma: Kamradt default slightly below average (recall 83.6). Their own ClusterSemanticChunker and LLM chunker reach 91.3/91.9 vs 89.5 for recursive 400, with no significance testing and ±25-30 SD [V] | Embedding pass at index time | Confirms the earlier decision to skip it |

Take-away [E]: every "precision + context" method decouples **the unit you match on** from **the unit you return**. The experiment should therefore vary these two separately. The match unit is the chunk size. The return unit is the same chunk, a sentence window, or the parent paragraph or section. Hold the reader's budget fixed.

---

## 3. Evaluating a chunk-size comparison fairly

### 3.1 What the common metrics actually compute

| Framework | Metric | Definition | Chunk-size behaviour |
|---|---|---|---|
| Ragas [V] | `ContextPrecision` (LLM, with reference) | Each retrieved chunk is judged relevant against the reference; mean of precision@k at relevant ranks, a rank-weighted (average-precision-like) score | Bigger chunks are more often judged "relevant", so a coarse index scores higher |
| | `IDBasedContextPrecision` | retrieved ids ∩ reference ids / retrieved ids, **not rank-aware** | Undefined across chunkings, because ids change |
| | `ContextRecall` (LLM) | reference claims attributable to retrieved context / total reference claims | Budget-sensitive: more text means more claims attributable |
| | `NonLLMContextRecall`, `IDBasedContextRecall` | string-similarity or id matching against reference contexts | String matching works across chunkings; ids do not |
| DeepEval [V] | Contextual Precision | (1 / #relevant) Σ_k (relevant up to k / k) · r_k, judged against `expected_output` | Same as Ragas LLM precision |
| | Contextual Recall | attributable expected-output statements / total | Budget-sensitive |
| | Contextual Relevancy | relevant statements in the retrieved context / all statements; the docs say "to raise it, return fewer marginal chunks (lower top-K) or use smaller chunks" | **Structurally favours small chunks**: a precision-style ratio |
| TruLens [V, library source] | Context Relevance | LLM scores each chunk 0-3, normalised to 0-1; the documented example aggregates chunks with `np.mean` | Mean over chunks; larger chunks dilute relevance |
| Chroma chunking eval [V] | Token recall, precision, Precision_Ω, IoU | Over token sets: recall = \|t_e ∩ t_r\| / \|t_e\|, precision = \|t_e ∩ t_r\| / \|t_r\|, IoU = \|t_e ∩ t_r\| / (\|t_e\| + \|t_r\| − \|t_e ∩ t_r\|). Duplicates from overlap count in the denominator. Precision_Ω = precision when all chunks containing excerpt tokens are retrieved (an upper bound) | **Chunking-agnostic.** Recommended primary family |

The earlier design study defined context precision as average precision and context recall as gold items found. That matches Ragas' and DeepEval's **LLM** variants, but Ragas' **ID-based** precision is flat, not rank-aware [V]. Pick explicitly which one is meant.

### 3.2 Why chunk-id gold breaks, and the fix

- A gold label "chunk 17 answers Q" refers to one chunking. Re-chunk and chunk 17 no longer exists, or now holds different text, so recall and precision for the new chunking are undefined or silently wrong. Interview-coach's `CONTEXT.md` currently defines the **Evaluation set** as "the frozen, committed set of questions with the study-material chunks that answer them" [V], which builds this problem in.
- **Fix:** store gold as **evidence spans**: `(source_id, char_start, char_end, quote)` in the immutable source text, with a content hash of the source version. Each chunk records its own `(source_id, char_start, char_end)`. Every metric is then computed by overlap: token recall@budget, IoU, and a span hit (≥ x% of a gold span covered). Keep the quote so spans can be re-anchored by fuzzy search when the source file changes. Chroma does exactly this with exact-match excerpts [V]; Bhat does a cruder version with answer-string matching [V].
- QASPER: evidence paragraphs map to character spans by exact string match for **91.5-92.8%** of text evidence strings; the rest need fuzzy matching [M].

### 3.3 Datasets with span-level evidence and a mix of question types

| Dataset | Licence | Gold granularity | Precise vs context mix | Use |
|---|---|---|---|---|
| **QASPER** v0.3 [V] | CC BY 4.0 [V] | Evidence paragraphs (plus figures/tables); extractive answer spans; several annotators on dev/test | Answer types: extractive 51.8%, abstractive 24.2%, yes/no 13.9%, unanswerable 10.2% [V]. Multi-paragraph evidence per annotation about 30% [M] | Primary. Already loaded in interview-coach. 281 dev papers / 1,005 Q; 416 test papers / 1,451 Q [M] |
| **Natural Questions** [V] | CC BY-SA 3.0 [V] | **Long answer** (paragraph or table) and **short answer** span(s) on the same Wikipedia page; dev 7,830 five-way annotated [S] | 35% short answer, 13% long-answer-only, 1% yes/no, 51% no answer [S, from the paper's figure via a search summary] | Best natural contrast: for the same question, "find the span" vs "find the paragraph", and long-answer-only questions are context-type. Pages about 7k tokens [V, Bhat Table 1] |
| **HotpotQA** (distractor) | CC BY-SA 4.0 [V] | Supporting-fact sentences across 2 paragraphs | Multi-hop by design | Optional: tests dispersed evidence across documents, which chunk size cannot fix [E] |
| **CLAPNQ** | Apache-2.0 [V] | Gold passages from NQ with long-form, cohesive answers | Long-form ("context") answers | Optional context-heavy set built on NQ |
| **Chroma chunking-eval set** | MIT repo [V] | 472 queries with exact-match excerpts over 5 corpora | Mostly factual by prompt design | Cheap cross-check with its token metrics |
| **RAGBench** | CC BY 4.0 for the compilation [V]; component licences vary (it includes MS MARCO, CUAD and others) | GPT-4-labelled relevant and utilised **sentences** within fixed retrieved contexts | 12 domains | Not a retrieval corpus (contexts are pre-retrieved), but useful to **calibrate an LLM relevance judge** against sentence labels |
| NarrativeQA | Apache-2.0 [V] | Answers only (no evidence spans) | Context-heavy | Only as Bhat did it (answer-string match). Not recommended as gold |
| QuALITY | No licence on the HF card I checked | No evidence spans | Long-document multiple choice | Skip |
| **Owner's own set** on System Design Primer + Tech Interview Handbook | Source licences per the sources list | Span gold labelled by the owner | Labelled by the owner | Decides the production question. 100-200 questions are enough for a first read (section 3.6) |

### 3.4 Labelling query types

Ranked by reliability [E, informed by M]:

1. **Deterministic from gold structure (primary):** number of gold spans or paragraphs (1 vs ≥2), dispersion (token distance from first to last gold span), and total gold length. No model involved and fully reproducible. On QASPER, about 30% of questions are multi-paragraph per annotation [M].
2. **Dataset-native type:** NQ short-answer vs long-answer-only. QASPER answer type is **weak**: the multi-paragraph rate is 0.22-0.38 for every type, and median evidence length is 115-133 words for every type [M].
3. **Owner labels** for the own set: precise (definition, number, named fact) vs explanatory (why, compare, trade-off, design). Record this at question-writing time.
4. **LLM classifier** only as a scalable stand-in, calibrated against (1) or (3) on at least 100 items, reporting agreement (Cohen's κ) [E].

### 3.5 LLM judge vs deterministic metrics

- Deterministic span metrics are the **primary** retrieval metrics. They are free, exact and chunking-agnostic.
- LLM judges are needed for answer correctness on abstractive answers and for unlabelled production traffic. Known biases include position, **verbosity** and self-enhancement; GPT-4-class judges reach above 80% agreement with humans (Zheng et al. 2023) [V]. Verbosity bias matters here because larger chunks produce longer contexts and answers [E].
- **Calibration:** ARES uses about 150 human-labelled items and prediction-powered inference (PPI) to put confidence intervals on judge-estimated scores [V]. Plan [E]: about 100-150 owner labels per judged check. Report judge-vs-owner agreement (κ) and use a judge from a different model family than the answerer (for example GLM-5.3 answers, Claude judges).

### 3.6 Statistics

- **Paired by question:** every configuration answers the same questions; analyse per-question differences. Paired standard errors are smaller whenever configurations agree on which questions are hard (Miller 2024) [V].
- **Cluster by document:** questions on the same paper are correlated. Clustered standard errors can be about 3× the naive ones in real evals (Miller 2024, Table 4) [V]. Use a paper-level (cluster) bootstrap or the clustered formula.
- **Primary contrast decided in advance:** the interaction [(size_L − size_S) | context-type] − [(size_L − size_S) | precise-type] at a fixed budget. Report the 95% CI. Correct or limit secondary contrasts (Holm) [E].
- **How many questions** [M→E]: in the pilot on QASPER test (1,256 Q, 402 papers), the interaction's 95% CI half-width was about 0.056. 80% power at α = 0.05 needs a half-width of about MDE/2.8 × 1.96, so the minimum detectable interaction is about 0.08 on QASPER test alone and about 0.062 on dev + test pooled (about 2,100 Q). Detecting a 0.04 interaction needs about 2.4× more clustered data, which is the reason to add an NQ subset. A main effect between two sizes, such as 512 vs 64, already resolves to about ±0.03 with about 900 questions [M].
- The `ranx` library (MIT) has built-in paired tests (t-test, Fisher randomisation) [S for its feature list]. A cluster bootstrap is about 20 lines of code (appendix).

---

## 4. Local pilot: QASPER, BM25, budget-matched (what I ran and what it showed)

**Purpose:** check, before designing anything expensive, whether the fixed-k vs fixed-budget distinction changes the answer on the owner's own benchmark.

**Setup** [M]: QASPER v0.3 dev and test from the official S3 tarballs. Within-paper BM25 (k1 = 1.2, b = 0.75) implemented in the Python standard library. Fixed word windows of 32, 64, 128, 256 and 512 **words** (about 1.3 tokens per word), no overlap, crossing paragraph boundaries. Gold is the word positions of the annotator's text-evidence paragraphs. Every score takes the max over annotators. Questions are excluded when unanswerable, when their evidence is only figures or tables, or when an evidence string has no exact paragraph match (dev 163, test 195 excluded). Strata: single- vs multi-paragraph evidence. Answer-span gold: the word positions of the extractive answer spans inside the evidence. The CI is a paired, paper-clustered bootstrap with 2,000 resamples. Runtime is about 5 s per split on the M4 Max.

**Dataset facts** [M]: median paper length is 3,326-3,655 words depending on split (p90 about 5,000-5,700). The median paragraph is about 60 words. Evidence strings match paragraphs exactly 91.5-92.8% of the time. Test-set annotator disagreement: 44% of questions have at least one annotator with multi-paragraph evidence, 17% have all annotators agreeing on multi-paragraph, and the union of annotators' evidence is multi-paragraph for 59%.

**Results, test split** (dev replicates the pattern; full outputs in the appendix):

| Metric | Stratum (n) | 32 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|---|
| hit@5 (fixed k: "Bhat-style") | all (1,256) | 0.610 | 0.664 | 0.731 | 0.833 | **0.939** |
| words handed over at k=5 | all | 160 | 319 | 633 | 1,247 | 2,325 |
| evidence token recall, **budget 512 words** | single-para (916) | 0.411 | 0.468 | **0.486** | 0.459 | 0.379 |
| | multi-para (340) | 0.354 | 0.385 | **0.408** | 0.367 | 0.320 |
| evidence token recall, **budget 1024 words** | single-para | 0.580 | 0.637 | **0.690** | 0.681 | 0.622 |
| | multi-para | 0.511 | 0.573 | **0.608** | 0.592 | 0.556 |
| answer-**span** recall, budget 256 (extractive only) | single-para (483) | **0.388** | 0.385 | 0.338 | 0.261 | 0.169 |
| | multi-para (198) | **0.298** | 0.251 | 0.225 | 0.183 | 0.150 |

Paired, paper-clustered differences (budget 512 words):

| Contrast | dev | test |
|---|---|---|
| 512 − 64, single-para | −0.102 [−0.143, −0.060] | −0.089 [−0.122, −0.056] |
| 512 − 64, multi-para | −0.047 [−0.098, +0.005] | −0.065 [−0.112, −0.013] |
| **Interaction** (multi − single) of (512 − 64) | +0.055 [−0.011, +0.122] | +0.024 [−0.032, +0.080] |
| Same 512 − 64, fixed k=5 instead of budget | +0.589 [+0.559, +0.616] | +0.564 [+0.543, +0.584] |

**Reading** [M]+[E]:

- Fixed-k reporting makes large chunks look about 0.56-0.59 better for **every** question type. Under a fixed budget the sign flips. Most published support for the hypothesis lives in this artifact.
- Under a fixed budget, 64-128-word chunks (about 85-170 tokens) are best for both strata with this retriever. The interaction points the hypothesised way (large chunks are penalised less on multi-paragraph questions) but is small and not significant in either split.
- The precise half holds: answer-span recall peaks at the smallest sizes at small budgets, so a precise query wants a small unit.
- **Limits:** BM25 only (dense embedders, rerankers and contextual prefixes may shift the optimum, and Bhat shows the optimum is model-dependent); words, not tokens; truncation at the budget penalises chunks larger than the budget (sizes above 512 were excluded from the 512 comparison for that reason); QASPER's "multi-paragraph" stratum is a noisy proxy given the annotator disagreement; short papers.

---

## 5. Proposed experiment (local, about US$0 paid)

### 5.1 Hypotheses (decided before running)

- **H1 (interaction, primary):** at a fixed reader budget B ∈ {512, 1024} tokens, [Δ(512 − 128) | context-type] − [Δ(512 − 128) | precise-type] > 0 for evidence token recall. Supported if the 95% cluster-bootstrap CI excludes 0 on ≥ 2 corpora and ≥ 2 embedders. Rejected in practical terms if the CI lies entirely below +0.03 (an equivalence margin decided in advance).
- **H2 (precise half):** answer-span recall@B is maximised at ≤ 128 tokens for precise questions.
- **H3 (decoupling):** small-to-big (match 128, return the parent paragraph or section, capped at B) beats the best single size on context-type questions without losing on precise ones.

### 5.2 Corpora and query sets

| Set | Size used | Query-type label |
|---|---|---|
| QASPER dev + test | about 2,100 answerable questions (after evidence filtering), about 700 papers; unanswerable questions go to an abstention metric | Evidence count and dispersion (primary); answer type (secondary) |
| Natural Questions dev, subset | 1,000-1,500 questions with a long answer, stratified short-answer vs long-answer-only, retrieval within the page | Native: short span vs long-answer-only |
| Owner set (SDP + THH) | 100-200 questions with span gold | Owner label (precise / explanatory) plus evidence structure |
| Chroma eval set (optional) | 472 | Cross-check only |

### 5.3 Chunkers and sizes

- Fixed token windows: **64, 128, 256, 512**, plus **1024 only for the long-context embedder**. Overlap 0 in the main grid; one 15% overlap cell at 256 as a side factor.
- Heading-aware recursive (markdown) at 256 and 512 with the heading path as prefix (the owner's current design), on SDP/THH and on QASPER sections.
- Natural unit: QASPER paragraph; NQ paragraph/table candidate.
- **Small-to-big:** match on 128, return the containing paragraph or section (budget-capped).
- **Sentence window:** ±2 sentences around a sentence hit (budget-capped).
- **Contextual prefix** (subset): 50-100-token LLM context on the 256 chunker.
- Late chunking (optional, v2): nomic-embed-text-v1.5 with Chonkie's `LateChunker`.

### 5.4 Retrievers

BM25 (LanceDB FTS or `bm25s`), dense **bge-small-en-v1.5** (the current model, 512 limit) and **nomic-embed-text-v1.5** (8k, mean pooling, Apache-2.0), hybrid RRF, and hybrid + **gte-reranker-modernbert-base** rerank of the top 30. That is 4 retrieval pipelines × about 6 chunkers × 2 corpora, with contextual and late chunking on subsets only.

### 5.5 Metrics

Primary: evidence **token recall @ B** for B ∈ {256, 512, 1024, 2048} tokens. Secondary: token IoU and precision at B (Chroma), answer-span recall @ B (extractive or short answers), and hit@k plus fixed-k recall to reproduce the literature. Optional generation arm on about 300 questions × 4 best configurations: GLM-5.3 answers from exactly B tokens, scored by the QASPER answer-F1 evaluator (`qasper_evaluator.py` ships in the test tarball [V]) and a Claude judge calibrated on about 100 owner labels. Abstention accuracy on unanswerable questions.

### 5.6 Expected table (template, with the pilot's BM25 values as the prior)

| Config @ B=1024 | precise-type recall | context-type recall | Δ vs fixed-128 (precise) | Δ vs fixed-128 (context) | Interaction |
|---|---|---|---|---|---|
| fixed-64 | | | | | |
| fixed-128 (reference) | ≈0.69 (pilot, single-para) | ≈0.61 (pilot, multi-para) | 0 | 0 | 0 |
| fixed-256 | | | | | |
| fixed-512 | ≈0.62 | ≈0.56 | ≈−0.07 | ≈−0.05 | ≈+0.02 (CI spans 0) |
| heading-aware 512 | | | | | |
| small-to-big 128→para | prediction: ≈ fixed-128 | prediction: ≥ fixed-128 | | | H3 |
| + contextual prefix | prediction: + a few points | prediction: + a few points | | | |

Each cell gets mean [95% cluster-bootstrap CI], one table per embedder and corpus. If H1 is true, the context-type column peaks at a larger size than the precise column with a positive, non-zero interaction. If it is false, both columns peak at the same small size (the pilot's outcome under BM25).

### 5.7 Runtime and cost estimate [E: throughput unmeasured on this machine; measure in the first step]

| Step | Volume | Estimate on M4 Max | Paid cost |
|---|---|---|---|
| Embed QASPER (about 3.2M tokens) × 5 chunkers × 2 embedders | about 32M tokens | bge-small: tens of minutes; nomic: 1-2 h | 0 |
| NQ subset (about 1,500 pages × about 7k tokens ≈ 10M) × 5 × 2 | about 100M tokens | Several hours; cut to 500 pages if slow | 0 |
| Rerank top 30 | about 3,600 Q × 30 × configs | 1-3 h | 0 |
| Contextual prefixes (local 8-14B model via MLX) | 150 papers ≈ 2.5k chunks | 2-4 h, with the paper as a reused prompt prefix | 0 |
| Generation arm | 300 Q × 4 configs | GLM plan quota | 0 (subscription) |
| Judge calibration and judging | about 100 labels + 1,200 judgements | Claude subscription, headless | 0 (subscription) |
| Metrics, bootstrap | | Minutes | 0 |

Total: one to two evenings of unattended compute, US$0 paid. The US$2 cap is untouched unless the owner chooses paid context generation (Anthropic's own figure is about 1.02 USD per million document tokens with caching [V]). The terms of service for headless Claude Code and the GLM coding plan at this volume were **not verified** here; the owner should confirm them.

### 5.8 Libraries and tools

| Tool | Licence [V] | Maintenance (GitHub `pushed_at`, observed 2026-10-10) [V] | Use |
|---|---|---|---|
| LanceDB | Apache-2.0 | 2026-10-10 | Index, FTS, hybrid (already chosen) |
| sentence-transformers | Apache-2.0 | 2026-10-08 | Embedders and cross-encoders in-process |
| bge-small-en-v1.5 / nomic-embed-text-v1.5 | MIT / Apache-2.0 | n/a (HF models) | Short- vs long-context embedder |
| gte-reranker-modernbert-base, bge-reranker-v2-m3, Qwen3-Reranker-0.6B | Apache-2.0 | n/a | Reranker |
| Chonkie (now `feyninc/chonkie`) | MIT | 2026-10-03 | Token, recursive, sentence, semantic, **late** chunkers |
| chunking_evaluation (Chroma) | MIT | 2025-12-13 | Reference token metrics and its 472-query set |
| bm25s | MIT | 2026-10-08 | Fast BM25 if not using LanceDB FTS |
| ranx | MIT | 2025-08-07 | Rank metrics and paired significance tests |
| ir_measures | Apache-2.0 | 2026-09-30 | Standard IR metrics |
| Ragas (moved to `vibrantlabsai/ragas`) | Apache-2.0 | **2026-02-24** (no push for about 7 months) | Secondary LLM metrics only; check maintenance before adopting |
| DeepEval | Apache-2.0 | 2026-10-10 | Secondary LLM metrics |
| TruLens | MIT | 2026-10-09 | Secondary (context relevance) |
| ARES | Apache-2.0 | 2025-03-28 | PPI calibration idea (could reimplement PPI in a few lines) |
| mlx-lm | MIT | 2026-10-10 | Local LLM for contextual prefixes |
| LlamaIndex / LangChain | MIT | active | Reference implementations of sentence window, auto-merging, parent-document; not needed as dependencies |
| RAPTOR reference | MIT | 2024-09-03 | Not recommended (section 2) |
| Mix-of-Granularity code | NOASSERTION | 2025-01-26 | Licence unclear; reference only |

---

## 6. New repository or an experiment inside interview-coach?

Facts [V]: interview-coach is a public MIT project on `master` with 31 files: ADRs 0001-0005, a LangGraph skeleton, and no retrieval code yet. ADR 0003 already fixes LanceDB hybrid search, bge-small and gte-reranker, citing "the project's own QASPER measurements". A QASPER-loading task (`ic-qasper-load`) is under way. The study material (SDP README about 12k words; THH content about 380 KB of markdown) totals roughly **115k tokens** [E: from file sizes]. That is under Anthropic's "under 200k tokens, consider putting the whole knowledge base in the prompt" threshold [V], so a **no-retrieval long-context baseline** belongs in the production comparison, if the model's context allows.

| | Inside interview-coach (`evals/chunking/`, results recorded as an ADR) | New repository |
|---|---|---|
| Fit with the goal "improve my RAG" | Direct: same index, models and evaluation-set format; results change an ADR | Indirect: findings must be ported |
| Fit with "prove the hypothesis" | Fine, if the harness is dataset-agnostic (span gold interface) | Cleaner story; easier to write up and share as a standalone benchmark |
| Cost | No duplicated plumbing; one dependency set | Duplicates LanceDB, models, loaders |
| Risks | Scope creep inside a learning app; heavy data (NQ) in a product repo, though data stays out of git per ADR 0002 | Drift from the real system; the experiment may never reach production |
| Required change either way | The **Evaluation set** definition must move from chunk ids to source spans | Same |

**Recommendation** [E]: run it inside interview-coach as a measured experiment, with a small dataset-agnostic core (spans, budgeted retrieval, metrics, cluster bootstrap). Extract it to a new repo only if it grows to ≥ 2 external datasets plus a reusable library. The span-gold change has to land in interview-coach regardless.

---

## 7. Confirmations and corrections to the earlier design study

| Earlier conclusion | Status after this research |
|---|---|
| Split by markdown headings with the heading path as prefix; cap at 300-500 tokens; recursive second pass; 0-10% overlap | **Keep, but test smaller leaves.** The cap fits bge-small's 512-token limit [V]. The pilot found 85-170-token units best at a fixed budget with BM25 [M]. Test 128-256 leaves with small-to-big return before freezing 300-500 |
| Skip semantic chunking | **Confirmed** (Qu et al. [V]; Chroma's Kamradt default below average [V]) |
| Contextual retrieval as a measured experiment; Anthropic −35% / −49% / −67% | **Numbers verified** (5.7% → 3.7% → 2.9% → 1.9% failures at top-20 [V]). Caveat: vendor-run, recall@20 with top-20, no CIs. The one independent replication found a small gain without error bars [V] |
| Context precision = average precision of the retrieved list; context recall = gold items found; deterministic when chunk ids are known | **Correct as definitions, wrong as an implementation for chunk-size experiments.** Ragas' ID-based precision is flat, not AP [V]. Chunk ids do not survive re-chunking. Use span/token gold |
| QASPER: retrieve within one paper; paragraph as relevance unit; unanswerable → abstention; error bars clustered by paper | **Confirmed, with additions** [M]: papers are short (k × size saturates quickly, so use budgets); 7-8.5% of evidence needs fuzzy matching; take max over annotators (evidence disagreement is large); answer type is a weak proxy for "needs context". Clustering is supported by Miller (up to 3× SE) [V] |

---

## 8. Open design questions for the grilling

Each question has options and a recommendation. Rounds go from scope to mechanics.

### Round 1: goal and scope

1. **What should the experiment decide?**
   (a) a general claim about chunk size × query type; (b) the chunking for interview-coach; (c) both, with (b) as the deliverable and (a) as a side table.
   **Recommend (c).**
2. **Where does it live?**
   (a) inside interview-coach under `evals/chunking/`; (b) a new repo; (c) start in (a), extract later.
   **Recommend (c)** (section 6).
3. **How is the hypothesis framed?**
   (a) at fixed top-k (as the literature does); (b) at a fixed reader token budget; (c) both, with (b) primary.
   **Recommend (c)**, so results stay comparable with Bhat et al. while the decision rests on (b).

### Round 2: data and labels

4. **Which corpora?**
   (a) QASPER only; (b) QASPER + NQ subset; (c) (b) + own SDP/THH set; (d) (c) + Chroma set.
   **Recommend (c).** QASPER alone can detect only an interaction of about 0.06 or more [M→E], and the own set decides production.
5. **Gold format for the evaluation set?**
   (a) chunk ids (current glossary); (b) source character spans + quote + source hash; (c) quotes only, re-anchored at runtime.
   **Recommend (b)**, and amend the `CONTEXT.md` "Evaluation set" definition.
6. **How to label query type?**
   (a) dataset-native (QASPER answer type, NQ short/long); (b) deterministic from gold structure; (c) owner labels; (d) LLM classifier.
   **Recommend (b) primary, (c) on the own set, (a) for NQ, (d) only if calibrated (κ reported).**
7. **How many owner-labelled questions?**
   (a) 50; (b) 100-150; (c) 300.
   **Recommend (b)**: enough for judge calibration (ARES uses about 150 [V]) and a first read of main effects.

### Round 3: systems under test

8. **Embedders?**
   (a) bge-small only; (b) + nomic-embed-text-v1.5; (c) + Qwen3-Embedding-0.6B as well.
   **Recommend (b)**: one short-context and one long-context mean-pooling model, which also enables late chunking. Add (c) only if (a) and (b) disagree.
9. **Chunk grid?**
   (a) 64/128/256/512 (+1024 for the long model), overlap 0; (b) the same plus an overlap factor and heading-aware variants.
   **Recommend (b), with overlap as one side cell only.**
10. **Which "precision + context" strategies in v1?**
    (a) small-to-big + sentence window + reranker; (b) (a) + contextual prefix on a subset; (c) (b) + late chunking; (d) everything including propositions, RAPTOR and routing.
    **Recommend (b) for v1, late chunking in v2; skip propositions, RAPTOR and trained routing** unless v1 shows an interaction worth routing on.
11. **Include a no-retrieval long-context baseline for the study material?**
    (a) yes; (b) no.
    **Recommend (a)** if GLM-5.3's context window holds about 115k tokens. That limit was not verified here.

### Round 4: metrics and statistics

12. **Primary retrieval metric?**
    (a) token recall @ fixed budget; (b) hit@k; (c) LLM context relevancy/precision.
    **Recommend (a)** at B = 512 and 1024, with IoU secondary; (b) only for literature comparison; (c) secondary and calibrated.
13. **Include a generation arm?**
    (a) no, retrieval only; (b) yes on about 300 questions × 4 configurations with QASPER F1 + a calibrated cross-family judge; (c) yes on everything.
    **Recommend (b).**
14. **Statistical protocol?**
    (a) report means; (b) paired, paper-clustered bootstrap CIs for all contrasts; (c) (b) + a primary contrast and an equivalence margin decided in advance.
    **Recommend (c)**: interaction at B = 1024, margin 0.03.

### Round 5: budget and adoption

15. **Who writes contextual prefixes?**
    (a) local MLX model; (b) GLM coding plan; (c) Claude headless; (d) paid API under the US$2 cap.
    **Recommend (a) on a 150-paper subset**, with (b) as fallback after checking its terms.
16. **What result changes interview-coach's chunking ADR?**
    (a) any improvement; (b) Δ recall@1024 ≥ +0.03 with the CI excluding 0 on the own set and on QASPER; (c) also no regression on precise questions.
    **Recommend (b) + (c).**

---

## 9. Sources

Papers (PDF text read in this session unless marked):

- Bhat, Rudat, Spiekermann, Flores-Herr. *Rethinking Chunk Size For Long-Document Retrieval: A Multi-Dataset Analysis.* arXiv 2505.21700 (2025). Code: github.com/fraunhofer-iais/chunking-strategies
- Zhang et al. *SmartChunk Retrieval: Query-Aware Chunk Compression with Planning.* arXiv 2602.22225 (2025)
- Zhong et al. *Mix-of-Granularity.* COLING 2025, arXiv 2406.00456
- Chen et al. *Dense X Retrieval: What Retrieval Granularity Should We Use?* EMNLP 2024, arXiv 2312.06648
- Duarte et al. *LumberChunker.* arXiv 2406.17526
- Günther et al. *Late Chunking.* arXiv 2409.04701
- Singh & Merola. *Reconstructing Context: Evaluating Advanced Chunking Strategies for RAG.* arXiv 2504.19754
- Sarthi et al. *RAPTOR.* ICLR 2024, arXiv 2401.18059
- Qu, Tu, Bao. *Is Semantic Chunking Worth the Computational Cost?* arXiv 2410.13070
- Wang et al. *Searching for Best Practices in RAG.* arXiv 2407.01219
- Jimeno Yepes et al. *Financial Report Chunking for Effective RAG.* arXiv 2402.05131
- Jiang et al. *LongRAG.* arXiv 2406.15319
- Dasigi et al. *A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers (QASPER).* NAACL 2021, arXiv 2105.03011
- Friel, Belyi et al. *RAGBench.* arXiv 2407.11005
- Saad-Falcon et al. *ARES.* arXiv 2311.09476
- Miller. *Adding Error Bars to Evals.* arXiv 2411.00640
- Zheng et al. *Judging LLM-as-a-Judge.* arXiv 2306.05685 (abstract only)
- Kwiatkowski et al. *Natural Questions.* TACL 2019 (statistics via search summary, [S])
- Also downloaded and skimmed, not relied on: arXiv 2603.06976 (36 chunkers, LLM-graded nDCG), 2606.18781 (DICE), 2606.00881 (chunking survey), 2605.22834 (QASC), 2510.20356 (FreeChunker), 2310.03025 (Retrieval meets long-context LLMs)

Technical reports and docs:

- Smith & Troynikov, *Evaluating Chunking Strategies for Retrieval*, Chroma, July 2024: https://www.trychroma.com/research/evaluating-chunking
- Anthropic, *Introducing Contextual Retrieval*: https://www.anthropic.com/news/contextual-retrieval
- Ragas context precision / recall: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/ and …/context_recall/
- DeepEval contextual relevancy / precision / recall: https://deepeval.com/docs/metrics-contextual-relevancy (and -precision, -recall)
- TruLens RAG triad: https://www.trulens.org/getting_started/core_concepts/rag_triad/ and source `src/feedback/trulens/feedback/llm_provider.py` (`context_relevance`, 0-3 scale)
- LlamaIndex auto-merging retriever: https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/
- NVIDIA, *Finding the Best Chunking Strategy for Accurate AI Responses* (June 2025): https://developer.nvidia.com/blog/finding-the-best-chunking-strategy-for-accurate-ai-responses/ ([S], read via summaries)
- Licences and model configs: Hugging Face API/cards for each dataset and model listed; GitHub API for repository licences and activity
- interview-coach: https://github.com/lbildzinkas/interview-coach (ADR 0003, CONTEXT.md, file tree)

---

## Appendix A: commands run

```sh
# papers (20 PDFs) -> text
curl -sL -o $id.pdf https://arxiv.org/pdf/$id && pdftotext -layout $id.pdf $id.txt
# QASPER v0.3
curl -sSLO https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz
curl -sSLO https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz
# descriptive stats and the pilot (stdlib only, python3 -I)
python3 -I qasper_stats.py qasper
python3 -I pilot_bm25.py qasper dev
python3 -I pilot_bm25.py qasper test
```

QASPER descriptive output [M]:

```
== train: papers=888 questions=2593 ; paper words median=3655 p10=1879 p90=5710
  answer type: abstractive 610, extractive 1314, yes_no 397, unanswerable 272
  text evidence strings exactly matching a paragraph: 3402/3678 = 0.925
== dev: papers=281 questions=1005 ; paper words median=3436 p10=1864 p90=4947
  answer type: extractive 530, abstractive 264, yes_no 116, unanswerable 95
  text evidence exact match: 1314/1436 = 0.915
  extractive multi-para=0.27 ev words median=119 ; abstractive 0.36 / 133 ; yes_no 0.22 / 122
== test: papers=416 questions=1451 ; paper words median=3326 p10=1851 p90=5372
  answer type: extractive 732, abstractive 371, unanswerable 139, yes_no 209
  text evidence exact match: 2022/2179 = 0.928
  extractive multi-para=0.29 ev words median=115 ; abstractive 0.38 / 131 ; yes_no 0.29 / 118
multi-paragraph evidence: per-annotation 0.30-0.33 ; test any-annotator 0.44, all-annotators 0.17, union 0.59
```

Pilot output, dev split (test is in section 4) [M]:

```
split=dev papers=281 evaluated_questions=842 skipped=163
[A] fixed k  hit@5 all: 32:0.563 64:0.628 128:0.697 256:0.786 512:0.925 ; words@5: 160 319 634 1252 2347
[B] budget 512  single_para: 32:0.366 64:0.425 128:0.423 256:0.377 512:0.324
                multi_para:  32:0.307 64:0.359 128:0.348 256:0.340 512:0.312
    budget 1024 single_para: 32:0.543 64:0.607 128:0.639 256:0.609 512:0.566
                multi_para:  32:0.473 64:0.537 128:0.559 256:0.556 512:0.567
[C2] interaction (256-64): +0.029 [-0.027,+0.086] ; (512-64): +0.055 [-0.011,+0.122]
[E] span recall @256 extractive single_para: 32:0.383 64:0.350 128:0.300 256:0.256 512:0.173
```

## Appendix B: pilot script (`pilot_bm25.py`, Python standard library only)

```python
"""Pilot: does the best chunk size depend on query type once the token budget is fixed?
QASPER, within-paper BM25, fixed-size word windows. Gold evidence = word positions of the
annotated evidence paragraphs (exact string match), so labels survive any re-chunking.
Scores take the max over annotators (QASPER-style)."""
import json, math, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(sys.argv[1]); SPLIT = sys.argv[2] if len(sys.argv) > 2 else "dev"
SIZES = [32, 64, 128, 256, 512]; KS = [1, 3, 5]; BUDGETS = [128, 256, 512, 1024]
STOP = set("a an the of to in and or for on with by is are was were be been this that these those it its as at from which what how do does did they their we our".split())
TOK = re.compile(r"\w+")

def terms(text): return [t for t in TOK.findall(text.lower()) if t not in STOP]

def bm25_rank(query, chunks, k1=1.2, b=0.75):
    docs = [Counter(terms(c)) for c in chunks]; lens = [sum(d.values()) for d in docs]
    avg = sum(lens) / max(len(lens), 1) or 1.0; df = Counter(t for d in docs for t in d); n = len(docs)
    scores = []
    for d, dl in zip(docs, lens):
        s = 0.0
        for t in terms(query):
            if t in d:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)); tf = d[t]
                s += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avg))
        scores.append(s)
    return sorted(range(n), key=lambda i: (-scores[i], i))

def build_paper(p):
    paras = [p["abstract"]] + [x for sec in p["full_text"] for x in sec["paragraphs"] if x.strip()]
    words, para_span = [], {}
    for para in paras:
        w = para.split(); para_span.setdefault(para, (len(words), len(words) + len(w))); words.extend(w)
    return words, para_span

def chunk(words, size): return [(i, min(i + size, len(words))) for i in range(0, len(words), size)]

def gold_sets(qa, para_span, words_ref):
    out = []
    for a in qa["answers"]:
        ans = a["answer"]
        if ans["unanswerable"]: continue
        ev = [e for e in ans["evidence"] if not e.startswith("FLOAT SELECTED")]
        if not ev or any(e not in para_span for e in ev): continue
        pos = set()
        for e in ev: s, t = para_span[e]; pos.update(range(s, t))
        atype = "yes_no" if ans["yes_no"] is not None else ("extractive" if ans["extractive_spans"] else "abstractive")
        span_pos = set()
        for span in ans["extractive_spans"]:
            sw = span.split()
            for e in ev:
                s, t = para_span[e]; pw = words_ref[s:t]
                for i in range(len(pw) - len(sw) + 1):
                    if sw and pw[i:i + len(sw)] == sw: span_pos.update(range(s + i, s + i + len(sw))); break
        out.append((pos, len(ev), atype, span_pos))
    return out

def evaluate(ranked, gold):
    res = {}
    for k in KS:
        top = ranked[:k]
        res[f"hit@{k}"] = float(max(any(any(s <= x < t for x in g) for s, t in top) for g, *_ in gold))
        got = set().union(*(range(s, t) for s, t in top))
        res[f"tokrec@{k}"] = max(len(g & got) / len(g) for g, *_ in gold); res[f"words@{k}"] = float(len(got))
    for B in BUDGETS:
        got, left = set(), B
        for s, t in ranked:
            if left <= 0: break
            take = min(t - s, left); got.update(range(s, s + take)); left -= take
        res[f"tokrec_B{B}"] = max(len(g & got) / len(g) for g, *_ in gold)
        res[f"iou_B{B}"] = max(len(g & got) / len(g | got) for g, *_ in gold)
        spans = [sp for *_, sp in gold if sp]
        if spans: res[f"spanrec_B{B}"] = max(len(sp & got) / len(sp) for sp in spans)
    return res

# main loop: for each paper, chunk at every size, BM25-rank chunks per question, evaluate();
# strata = single_para / multi_para (first usable annotation) and answer type.
# cluster_boot_diff(): resample papers with replacement (2,000 iterations), recompute the
# paired mean difference (size_a - size_b) over all questions in the resampled papers,
# report the 2.5th / 97.5th percentiles. interaction_boot(): same resampling, statistic =
# mean diff in multi_para minus mean diff in single_para.
```
