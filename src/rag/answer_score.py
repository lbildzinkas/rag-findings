"""The datasets' standard answer metrics for one question (the answer
score, glossary), scored against the question's reference answers.

Both datasets' metrics rest on SQuAD-style answer normalisation: lower
case, punctuation removed, articles (a, an, the) removed, whitespace
collapsed. On normalised tokens:

- token F1 (QASPER's answer F1, and Natural Questions context questions
  against the long-answer paragraph): the harmonic mean of the
  prediction's and the reference's token precision and recall,
  maximised over the references;
- short-answer match (Natural Questions precise questions): normalised
  exact match against any reference, with "contains a reference" (the
  normalised prediction contains a normalised reference) as a secondary
  column, because a brief answer can wrap the reference in a few words.

The official QASPER evaluator and SQuAD's script define the same
normalisation; the hand-made cases in tests/test_answer_score.py pin it.
"""

from __future__ import annotations

import re
import string
from collections import Counter
from collections.abc import Sequence

from .query_type import PRECISE

_ARTICLES = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)
_PUNCTUATION = frozenset(string.punctuation)

ANSWER_F1 = "answer_f1"
SHORT_MATCH = "short_match"
CONTAINS = "contains"


def normalize_answer(text: str) -> str:
    """SQuAD-style normalisation: lower case, no punctuation, no articles,
    single spaces."""
    lowered = text.lower()
    without_punctuation = "".join(ch for ch in lowered if ch not in _PUNCTUATION)
    without_articles = _ARTICLES.sub(" ", without_punctuation)
    return " ".join(without_articles.split())


def _token_f1(prediction: str, reference: str) -> float:
    prediction_tokens = normalize_answer(prediction).split()
    reference_tokens = normalize_answer(reference).split()
    common = Counter(prediction_tokens) & Counter(reference_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(prediction_tokens)
    recall = num_same / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def token_f1(prediction: str, references: Sequence[str]) -> float:
    """Token F1 after SQuAD-style normalisation, maximised over references."""
    if not references:
        raise ValueError("token F1 needs at least one reference")
    return max(_token_f1(prediction, reference) for reference in references)


def exact_match(prediction: str, references: Sequence[str]) -> float:
    """Normalised exact match against any reference (0.0 or 1.0)."""
    if not references:
        raise ValueError("exact match needs at least one reference")
    normalized = normalize_answer(prediction)
    return 1.0 if any(normalized == normalize_answer(reference) for reference in references) else 0.0


def contains_reference(prediction: str, references: Sequence[str]) -> float:
    """Whether the normalised prediction contains a normalised reference."""
    if not references:
        raise ValueError("contains needs at least one reference")
    normalized = normalize_answer(prediction)
    return 1.0 if any(normalize_answer(reference) in normalized for reference in references) else 0.0


class AnswerScored:
    """One question's answer score and its secondary column, if any."""

    __slots__ = ("metric", "score", "secondary")

    def __init__(self, metric: str, score: float, secondary: float | None = None):
        self.metric = metric
        self.score = score
        self.secondary = secondary


def score_answer(dataset: str, query_type: str, prediction: str, references: Sequence[str]) -> AnswerScored:
    """The dataset's standard answer metric for one question.

    QASPER: answer F1 over references. Natural Questions: short-answer
    match (with contains as the secondary column) on precise questions,
    token F1 against the long-answer paragraph on context questions.
    """
    if not references:
        raise ValueError(f"{dataset} question needs at least one reference answer")
    if dataset == "qasper":
        return AnswerScored(ANSWER_F1, token_f1(prediction, references))
    if dataset == "nq":
        if query_type == PRECISE:
            return AnswerScored(
                SHORT_MATCH,
                exact_match(prediction, references),
                contains_reference(prediction, references),
            )
        return AnswerScored(ANSWER_F1, token_f1(prediction, references))
    raise ValueError(f"unknown dataset: {dataset}")
