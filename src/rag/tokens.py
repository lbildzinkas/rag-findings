"""The one tokenizer: tiktoken cl100k_base.

Every chunk size, budget and metric in the experiment is expressed in
cl100k_base tokens (decision 21). The BPE file is cached under the
project's data directory so runs do not depend on a writable system temp.

Token character offsets are computed through the UTF-8 byte level:
cl100k tokens partition the text's bytes exactly (a token can even hold
part of a multi-byte character, where per-token str decoding would
corrupt), so offsets are derived from `decode_bytes` and mapped back to
character positions. A character partially covered by a token counts as
part of that token.
"""

from __future__ import annotations

import hashlib
import os
from bisect import bisect_left, bisect_right
from functools import lru_cache
from pathlib import Path

_ENCODING_NAME = "cl100k_base"


def _cache_dir() -> Path:
    """Resolve the tiktoken cache directory, defaulting to data/tiktoken-cache."""
    from .paths import default_paths

    cache = default_paths().data / "tiktoken-cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def _ensure_cache_env() -> None:
    if not os.environ.get("TIKTOKEN_CACHE_DIR"):
        os.environ["TIKTOKEN_CACHE_DIR"] = str(_cache_dir())


@lru_cache(maxsize=1)
def get_encoding():
    """Return the shared cl100k_base encoding, downloading it once."""
    import tiktoken

    _ensure_cache_env()
    return tiktoken.get_encoding(_ENCODING_NAME)


def sha256_text(text: str) -> str:
    """Content hash used as a document's source hash."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TokenText:
    """A text tokenized once, with each token's character offsets.

    Offsets come from the byte level: tokens tile the UTF-8 bytes of the
    text exactly, and byte positions map back to character positions. A
    character straddling two tokens belongs to both.
    """

    def __init__(self, text: str, encoding=None):
        enc = get_encoding() if encoding is None else encoding
        self.text = text
        ids = enc.encode_ordinary(text)
        data = text.encode("utf-8")

        # byte offset where each character starts; char_byte_starts[i] is
        # the byte offset of text[i], plus a final sentinel == len(data)
        char_byte_starts = [0] * (len(text) + 1)
        byte_pos = 0
        for i, ch in enumerate(text):
            char_byte_starts[i] = byte_pos
            byte_pos += len(ch.encode("utf-8"))
        char_byte_starts[len(text)] = byte_pos
        if byte_pos != len(data):  # pragma: no cover - defensive
            raise ValueError("utf-8 byte length mismatch")

        offsets: list[tuple[int, int]] = []
        byte_start = 0
        for tok in ids:
            piece = enc.decode_bytes([tok])
            byte_end = byte_start + len(piece)
            # character span covering [byte_start, byte_end)
            start = bisect_right(char_byte_starts, byte_start) - 1
            end = bisect_left(char_byte_starts, byte_end)
            offsets.append((start, max(end, start + 1)))
            byte_start = byte_end
        if byte_start != len(data):
            raise ValueError("tokenizer did not tile the text exactly")
        self.encoding = enc
        self.token_ids = ids
        self.offsets = offsets
        self._starts = [s for s, _ in offsets]

    def __len__(self) -> int:
        return len(self.token_ids)

    def token_at_char(self, char: int) -> int:
        """Index of the first token starting at or after character `char`
        (len(self) when none does): the token boundary a character boundary
        maps to."""
        return bisect_left(self._starts, char)

    def token_indices_overlapping(self, start: int, end: int) -> frozenset[int]:
        """Indices of tokens whose character span intersects [start, end)."""
        out: list[int] = []
        for i, (s, e) in enumerate(self.offsets):
            if s >= end:
                break
            if e > start:
                out.append(i)
        return frozenset(out)
