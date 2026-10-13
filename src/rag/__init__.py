"""rag-findings: RAG chunking retrieval experiments.

QASPER -> canonical documents -> labelled spans -> chunkings (fixed
windows, section-aware, small-to-big) -> BM25 retrieval -> budget packing
in the production and fair views -> retrieval recall and precision, for a
single-cell tracer run or the full chunking x budget grid.
"""

__version__ = "0.1.0"
