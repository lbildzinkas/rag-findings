"""Document store: one canonical text per document (QASPER paper or NQ page).

`build_document` makes a paper's canonical text: the abstract followed
by every section paragraph, joined with blank lines. Each document
records its paragraphs' character spans so evidence can be anchored, and
a source hash (sha256 of the canonical text) so spans can be checked
against their document.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tokens import sha256_text


@dataclass(frozen=True)
class Paragraph:
    """One paragraph of the canonical text: [start, end) plus its section.

    `section_index` numbers the document's sections in order (the abstract
    is 0), so two sections that happen to share a name stay apart.
    """

    start: int
    end: int
    text: str
    section: str
    section_index: int = 0


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
    parts: list[tuple[str, int, str]] = []
    if abstract:
        parts.append(("Abstract", 0, abstract))
    for section_index, (section_name, paragraphs) in enumerate(sections, start=1):
        for para in paragraphs:
            if para:
                parts.append((section_name, section_index, para))
    paragraphs: list[Paragraph] = []
    pos = 0
    pieces: list[str] = []
    for section_name, section_index, para in parts:
        if pieces:
            pieces.append("\n\n")
            pos += 2
        start = pos
        end = pos + len(para)
        pieces.append(para)
        paragraphs.append(Paragraph(start=start, end=end, text=para, section=section_name, section_index=section_index))
        pos = end
    return Document(doc_id=doc_id, text="".join(pieces), paragraphs=tuple(paragraphs))
