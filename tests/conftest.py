"""Shared fixtures: an offline byte-level fake tokenizer and a synthetic
QASPER split factory.

The fake encoding tokenizes at UTF-8 byte granularity, so tests run with
zero downloads (CI runs unit tests on committed fixtures only); the real
cl100k_base path is exercised by the local `rag setup && rag run` on the
actual dataset.
"""

from __future__ import annotations

import hashlib
import json

import pytest


class FakeEncoding:
    """One token per UTF-8 byte: deterministic, offline, multi-byte safe."""

    name = "fake-bytes"

    def encode_ordinary(self, text: str) -> list[int]:
        return list(text.encode("utf-8"))

    def decode_bytes(self, tokens: list[int]) -> bytes:
        return bytes(tokens)


@pytest.fixture
def fake_encoding() -> FakeEncoding:
    return FakeEncoding()


def make_paper(
    doc_id: str,
    abstract: str,
    sections: list[tuple[str, list[str]]],
    figures_and_tables: list[dict] | None = None,
    qas: list[dict] | None = None,
) -> dict:
    return {
        "title": f"Paper {doc_id}",
        "abstract": abstract,
        "full_text": [
            {"section_name": name, "paragraphs": paragraphs} for name, paragraphs in sections
        ],
        "figures_and_tables": figures_and_tables or [],
        "qas": qas or [],
    }


def make_answer(
    evidence: list[str] | None = None,
    unanswerable: bool = False,
    extractive_spans: list[str] | None = None,
) -> dict:
    return {
        "answer": {
            "unanswerable": unanswerable,
            "extractive_spans": extractive_spans or [],
            "yes_no": None,
            "free_form_answer": "",
            "evidence": evidence or [],
            "highlighted_evidence": [],
        }
    }


def make_qa(question_id: str, question: str, answers: list[dict]) -> dict:
    return {"question_id": question_id, "question": question, "answers": answers}


def write_split(path, papers: dict[str, dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(papers, sort_keys=True, indent=1)
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
