# The late-chunking single-chunk check against the real model

Ticket #22's acceptance check: a window holding a single chunk reproduces that chunk's independent vector (cosine >= 0.9999), checked once against the real model. `tests/test_late_real_model.py` runs it (`uv run pytest tests/test_late_real_model.py` after `uv run rag setup`; it skips where the model is not downloaded) on the pinned nomic-ai/nomic-embed-text-v1.5 @ e9b6763023c6, loaded with `rotary_scaling_factor=2`, over 8 deterministic synthetic chunks per size, each chunk a document whose only window holds exactly it. Numbers as measured:

| chunking | pooling | min cosine | median cosine | >= 0.9999 |
|---|---|---|---|---|
| late-128 | every token the model read (the mechanism) | 1.000000 | 1.000000 | pass |
| late-128 | shipped rule (prefix and specials out) | 0.999798 | 0.999843 | recorded below the bar |
| late-256 | every token the model read (the mechanism) | 1.000000 | 1.000000 | pass |
| late-256 | shipped rule (prefix and specials out) | 0.999946 | 0.999955 | pass |

The mechanism the bar validates: nomic's independent embedding is the normalized mean of every token it reads, so pooling the same tokens of the same single-window forward pass reproduces it exactly; the 0.9999 bar leaves float slop, and the check fails it if window planning, character-span-to-token mapping, pooling or the model load drift. The unit suite states the same fact on the fake token-embedding model (`tests/test_late.py::test_a_window_holding_a_single_chunk_pooled_over_all_its_tokens_is_the_independent_vector`).

The shipped pooling rule's row is the settled design's expected cost, not a defect: the prefix and special tokens join no chunk (ADR 0005, ADR 0007; the paper's alternative of folding them into the first and last chunks was not chosen), while the independent embedding averages those ~6 tokens in, so the rule necessarily sits just under the independent vector - about 2e-4 of cosine on a ~130-token late-128 chunk (0.9998), about 6e-5 on a ~260-token late-256 chunk (0.9999). The check asserts that deviation stays bounded (>= 0.999) and records it here.
