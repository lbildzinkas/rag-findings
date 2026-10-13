"""Document store: one canonical text per paper.

The canonical text is the abstract followed by every section paragraph,
joined with blank lines. Each document records its paragraphs' character
spans so evidence can be anchored, and a source hash (sha256 of the
canonical text) so spans can be checked against their document.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokens import sha256_text


@dataclass(frozen=True)
class Paragraph:
    """One paragraph of the canonical text: [start, end) plus its section."""

    start: int
    end: int
    text: str
    section: str


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    paragraphs: tuple[Paragraph, ...]

    @property
    def source_hash(self) -> str:
        return sha256_text(self.text)

    def paragraph_spans(self) -> list[tuple[int, int]]:
        return [(p.start, p.end) for p in self.paragraphs]


def build_document(doc_id: str, abstract: str, sections: list[tuple[str, list[str]]]) -> Document:
    """Join the abstract and section paragraphs into one canonical text.

    `sections` is a list of (section_name, paragraphs). Empty strings are
    skipped; paragraphs are separated by blank lines.
    """
    parts: list[tuple[str, str]] = []
    if abstract:
        parts.append(("Abstract", abstract))
    for section_name, paragraphs in sections:
        for para in paragraphs:
            if para:
                parts.append((section_name, para))
    paragraphs: list[Paragraph] = []
    pos = 0
    pieces: list[str] = []
    for section_name, para in parts:
        if pieces:
            pieces.append("\n\n")
            pos += 2
        start = pos
        end = pos + len(para)
        pieces.append(para)
        paragraphs.append(Paragraph(start=start, end=end, text=para, section=section_name))
        pos = end
    return Document(doc_id=doc_id, text="".join(pieces), paragraphs=tuple(paragraphs))
