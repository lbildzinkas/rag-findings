"""Section-aware chunks indexed with their document and section titles.

The cheapest form of context enrichment on the best single chunking
(issue 36, ADR 0005): a titled chunking keeps the section-aware
chunking's exact spans, and each chunk's search text is its title
header, a blank line and the chunk text - exactly a contextual chunk's
prefix (see rag.contextual), written by no model:

- the header comes only from the dataset's own title and section fields:
  a QASPER chunk reads `Paper: <paper title>. Section: <section name>.`
  (the abstract is the section named `Abstract`); a Natural Questions
  page's canonical text already opens every section with its heading, so
  its header adds only the page title, `Page: <page title>.`;
- the header is used for search only: the BM25 index reads the search
  text, the embedder embeds it and the reranker scores (question, search
  text) pairs, while packing, scoring and the reader see the chunk's own
 span and the budget counts only its tokens.

An empty part is skipped (a paper without a title, an unnamed section),
so a chunk with neither carries no header and is searched by its own
text. Vectors and reranker scores are cached under the model key plus
`#titles`, so they never collide with the plain section-aware chunking's
entries for the same spans.
"""

from __future__ import annotations

from .chunking import Chunk
from .documents import Document

KEY_SUFFIX = "#titles"  # the suffix of the embedder's and reranker's cache keys


def key_suffix() -> str:
    """The cache-key suffix of a titled chunking's vectors and scores."""
    return KEY_SUFFIX


def chunk_section(doc: Document, chunk: Chunk) -> str:
    """The name of the section a section-aware chunk sits in: the section
    of its first paragraph (the chunkings' cuts never cross a section, so
    every paragraph a chunk covers shares one name)."""
    for paragraph in doc.paragraphs:
        if paragraph.end > chunk.start:
            return paragraph.section
    return ""


def header(doc: Document, chunk: Chunk) -> str:
    """A chunk's title header from the dataset's own fields: the document
    title, then the section name unless the document's canonical text
    already opens its sections with their headings (Natural Questions
    pages, whose chunks begin with the heading itself)."""
    parts: list[str] = []
    title = " ".join(doc.title.split())
    if title:
        parts.append(f"{'Page' if doc.headings_in_text else 'Paper'}: {title}")
    if not doc.headings_in_text:
        section = " ".join(chunk_section(doc, chunk).split())
        if section:
            parts.append(f"Section: {section}")
    return ". ".join(parts) + "." if parts else ""


def chunk_headers(documents: dict[str, Document], chunks) -> dict:
    """Every chunk's header keyed by (document source hash, start, end),
    the span key the search-text and cache paths read."""
    out: dict[tuple[str, int, int], str] = {}
    for chunk in chunks:
        doc = documents[chunk.doc_id]
        out[(doc.source_hash, chunk.start, chunk.end)] = header(doc, chunk)
    return out
