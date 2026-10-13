"""Query type from the labels: precise, context, mixed."""

from __future__ import annotations

import pytest

from rag.query_type import CONTEXT, MIXED, PRECISE, query_type


@pytest.mark.parametrize(
    ("passages", "expected"),
    [
        ([1], PRECISE),
        ([1, 1, 1], PRECISE),
        ([2], CONTEXT),
        ([3, 2], CONTEXT),
        ([1, 2], MIXED),
        ([4, 1, 4], MIXED),
    ],
)
def test_query_type(passages, expected):
    assert query_type(passages) == expected


@pytest.mark.parametrize("passages", [[], [0], [1, 0]])
def test_query_type_needs_usable_annotations(passages):
    with pytest.raises(ValueError):
        query_type(passages)
