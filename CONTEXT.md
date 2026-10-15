# RAG findings

Research on how to chunk documents for retrieval-augmented generation: experiments and evaluations that measure which chunking retrieves the right text for which kind of question, as a step towards routing each query to the chunking that suits it.

## Language

### Chunking and budget

**Chunking**:
One way of splitting source text into retrievable units, defined by its method and size, such as fixed 256-token windows, section-aware splitting or small-to-big.
_Avoid_: chunk strategy, splitter, chunk config

**Small-to-big**:
A chunking that matches the question against small chunks and returns each matched chunk's larger parent when the parent still fits the token budget, otherwise the matched chunk itself.
_Avoid_: parent-document retrieval, hierarchical chunking

**Section-aware chunking**:
A chunking whose units follow the document's own sections and paragraphs instead of fixed token windows.
_Avoid_: structural chunking, semantic chunking

**Late chunking**:
Embed the whole document first, then cut the token embeddings into chunks, so each chunk's vector carries its surroundings.

**Contextual chunk**:
A chunk indexed with a short context prefix written for it at index time; the prefix helps search and is not part of the text handed to the reader.

**Token budget**:
The fixed amount of retrieved text, in tokens, handed to the reader for one question, filled with whole chunks in reranked order and never cut mid-chunk.
_Avoid_: context window, context size, top-k

**Top-N cap**:
The most reranked chunks sent to the reader for one question, whatever room is left in the token budget.
_Avoid_: top-k, k, chunk limit

**Production view**:
Results with the top-N cap applied inside the token budget, as a production system would send them.
_Avoid_: capped results, realistic view

**Fair view**:
Results with no top-N cap, the token budget filled with as many whole chunks as fit, so every chunking gets the same amount of text.
_Avoid_: uncapped view, budget-only view

**Budget view**:
Results with as many reranked whole chunks as fit the token budget, at most 20 per question.

### Retrieval

**Production line**:
The retrieval pipeline the experiment treats as the real system: keyword and vector search fused into one ranking, then reranked.
_Avoid_: main pipeline, default retriever, baseline

**Ablation**:
A retrieval pipeline that removes part of the production line, such as keyword search only, vector search only, or fused search without the reranker, to show what each part contributes.
_Avoid_: baseline, variant

**Collection search**:
Retrieval over every document in the evaluation set at once, the main setting; searching only within the question's own document is a secondary setting.
_Avoid_: global search, corpus search

### Labels and metrics

**Evaluation set**:
The frozen set of questions, each with the labelled spans that answer it, used to score every chunking and retrieval pipeline.
_Avoid_: test set, golden set, benchmark

**Label**:
Ground truth recorded for a question, such as the labelled spans that answer it, taken from the source dataset or made by the owner.
_Avoid_: gold, annotation, ground-truth chunk

**Labelled span**:
The exact source text that answers a question, identified by its document, start and end character offsets, quoted text and source hash, so it can be scored against any chunking.
_Avoid_: gold chunk, gold passage, evidence chunk

**Retrieval recall**:
The share of a question's labelled-span text that appears in the retrieved text within the token budget.
_Avoid_: hit rate, recall@k, coverage

**Retrieval precision**:
The share of the retrieved text within the token budget that falls inside the question's labelled spans.
_Avoid_: context relevancy, precision@k

**Grader**:
A model call that decides pass or fail for one check on one generated answer; not used in v1, which scores retrieval only.
_Avoid_: judge, evaluator, scorer

**Answer score**:
The dataset's standard answer metric for one question.

**Reader**:
The language model that answers a question from the retrieved chunks.

### Routing

**Query type**:
Whether a question is precise, context or mixed, decided from the labels in hindsight and never available to a router: for Natural Questions, short answer means precise and long-answer-only means context; for QASPER, precise means every usable annotation cites one passage, context that every one cites several, and mixed otherwise (only that rule produces mixed questions).
_Avoid_: question category, intent, query class

**Best single chunking**:
The one chunking with the highest mean score across all questions at a given token budget.
_Avoid_: best chunk size, winner, default chunking

**Oracle router**:
A router that picks, per question and in hindsight, the chunking that scored best for it; an upper bound on routing, never a real system.
_Avoid_: ideal router, perfect router, upper-bound model

**Routing headroom**:
The oracle router's score minus the best single chunking's score at the same token budget: the most any router could gain over using one chunking.
_Avoid_: routing gain, oracle gap, lift

**Routing decision**:
The chunking a router picks for a question from the query text alone.
_Avoid_: route, prediction, query classification

**Search-all routing**:
Search every chunking's index, fuse the lists, rerank the top of the fused list, and pack by budget, counting overlapping text only once.

**Confidence routing**:
Search each chunking's index separately and use the chunking whose top results the reranker scores highest.
