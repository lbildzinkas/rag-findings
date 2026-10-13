"""Query type from the labels, decided in hindsight.

The passage-count rule, used when a dataset's labels do not decide the
type directly (QASPER): a question is precise when every usable
annotation cites one passage, context when every usable annotation
cites several, and mixed otherwise. Natural Questions labels decide the
type instead (short answer means precise, long-answer-only means
context); `labels.question_query_type` dispatches between the two rules.
A usable annotation is one with at least one labelled span; a passage is
one distinct labelled span. Mixed questions count in every mean but not in
the query-type contrasts. The routing decision never sees the query type:
it is stored per question for the analysis only.
"""

from __future__ import annotations

from collections.abc import Sequence

PRECISE = "precise"
CONTEXT = "context"
MIXED = "mixed"
QUERY_TYPES = (PRECISE, CONTEXT, MIXED)


def query_type(passages_per_annotation: Sequence[int]) -> str:
    """Classify a question from the passage count of each usable annotation."""
    if not passages_per_annotation or any(n <= 0 for n in passages_per_annotation):
        raise ValueError("query type needs at least one usable annotation, each citing a passage")
    if all(n == 1 for n in passages_per_annotation):
        return PRECISE
    if all(n > 1 for n in passages_per_annotation):
        return CONTEXT
    return MIXED
