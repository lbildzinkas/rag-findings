"""Answer scoring: SQuAD-style normalisation, token F1, exact match and the
per-dataset dispatch. The hand-made cases pin the official QASPER
evaluator's and SQuAD's normalisation (lower case, punctuation and
articles removed, whitespace collapsed); the max-over-references rule is
the QASPER evaluator's."""

from __future__ import annotations

import pytest

from rag.answer_score import (
    ANSWER_F1,
    CONTAINS,
    SHORT_MATCH,
    contains_reference,
    exact_match,
    normalize_answer,
    score_answer,
    token_f1,
)


def test_normalisation_is_squad_style():
    assert normalize_answer("The Big Apple") == "big apple"
    assert normalize_answer("Hello, World!") == "hello world"
    assert normalize_answer("  extra   spaces  ") == "extra spaces"
    assert normalize_answer("U.S.A.") == "usa"
    assert normalize_answer("don't stop") == "dont stop"
    assert normalize_answer("a an the cat") == "cat"
    assert normalize_answer("") == ""
    # unicode text survives; only ascii punctuation is stripped
    assert normalize_answer("café naïve") == "café naïve"


def test_token_f1_hand_made_cases():
    # identical after normalisation
    assert token_f1("the Big Apple", ["big apple"]) == 1.0
    # no overlap
    assert token_f1("Paris", ["London"]) == 0.0
    # partial overlap: precision 1, recall 1/2 -> F1 2/3
    assert token_f1("Steve Smith", ["Steve"]) == pytest.approx(2 * 1 * 0.5 / 1.5)
    # both empty normalises to no tokens: the official score is 0
    assert token_f1("...", ["!!!"]) == 0.0
    assert token_f1("", [""]) == 0.0
    assert token_f1("", ["Paris"]) == 0.0


def test_token_f1_maximised_over_references():
    assert token_f1("June", ["December", "june 1940"]) == pytest.approx(2 / 3)
    assert token_f1("june", ["December", "June"]) == 1.0


def test_exact_match_is_normalised():
    assert exact_match("The Big Apple.", ["big apple"]) == 1.0
    assert exact_match("big apples", ["big apple"]) == 0.0
    assert exact_match("no", ["No", "yes"]) == 1.0


def test_contains_reference_wraps_the_reference():
    assert contains_reference("The answer is Paris, clearly.", ["paris"]) == 1.0
    assert contains_reference("London", ["paris"]) == 0.0
    assert contains_reference("it is 42", ["41"]) == 0.0


def test_score_answer_dispatches_per_dataset_and_type():
    qasper = score_answer("qasper", "mixed", "Steve Smith", ["Steve", "Steve Smith"])
    assert (qasper.metric, qasper.score, qasper.secondary) == (ANSWER_F1, 1.0, None)

    precise = score_answer("nq", "precise", "the Big Apple.", ["big apple"])
    assert precise.metric == SHORT_MATCH
    assert precise.score == 1.0
    assert precise.secondary == 1.0  # contains as the secondary column

    wrapped = score_answer("nq", "precise", "It is Paris.", ["paris"])
    assert (wrapped.score, wrapped.secondary) == (0.0, 1.0)

    context = score_answer("nq", "context", "the senate has 100 members", ["The Senate consists of 100 members."])
    assert context.metric == ANSWER_F1
    # normalised pred [senate has 100 members] vs ref [senate consists of 100 members]:
    # precision 3/4, recall 3/5
    assert context.score == pytest.approx(2 * (3 / 4) * (3 / 5) / (3 / 4 + 3 / 5))
    assert context.secondary is None


def test_score_answer_needs_references_and_a_known_dataset():
    with pytest.raises(ValueError, match="at least one reference"):
        score_answer("qasper", "mixed", "x", [])
    with pytest.raises(ValueError, match="unknown dataset"):
        score_answer("c4", "precise", "x", ["y"])
    assert CONTAINS == "contains"
