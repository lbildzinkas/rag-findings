"""The local reader: Qwen3-8B, 4-bit MLX weights on Apple silicon, through
mlx-lm (ADR 0009, amended 2026-10-17).

macOS only; mlx-lm comes from the optional `prefixes` dependency group
(`uv run --group prefixes rag answers <config>`), so tests and CI never
import this module. The weights are the revision the context prefixes
used, already in data/hf-cache/; they load offline from there.

Every prompt goes through the model's chat template as one user turn
with thinking disabled, and is answered greedily (mlx-lm's default
sampler is argmax) up to the new-token limit, one prompt at a time so
each answer's latency is its own. The call record holds the latency
(prefill plus generation), the prompt and generated token counts and
the finish reason ("stop" or "length").
"""

from __future__ import annotations

import time
from pathlib import Path

from .models import use_project_cache
from .reader import Reading

_WEIGHT_FILES = ["*.json", "*.txt", "model.safetensors"]
# as rag.prefix_model: cap mlx's buffer cache well below the GPU's working set
_BUFFER_CACHE_BYTES = 2 * 2**30


def load_reader(model_id: str, revision: str, data_dir: Path, max_new_tokens: int) -> MlxReader:
    use_project_cache(data_dir, offline=True)
    from huggingface_hub import snapshot_download

    path = snapshot_download(model_id, revision=revision, allow_patterns=_WEIGHT_FILES)
    return MlxReader(Path(path), max_new_tokens)


class MlxReader:
    def __init__(self, path: Path, max_new_tokens: int):
        import mlx.core as mx
        from mlx_lm import load

        mx.set_cache_limit(_BUFFER_CACHE_BYTES)
        self.max_new_tokens = max_new_tokens
        self.model, self.tokenizer = load(str(path))

    def render(self, prompt: str) -> list[int]:
        text = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}], add_generation_prompt=True, enable_thinking=False, tokenize=False
        )
        return self.tokenizer.encode(text, add_special_tokens=False)

    def read(self, prompt: str) -> Reading:
        from mlx_lm import stream_generate

        ids = self.render(prompt)
        started = time.perf_counter()
        text, last = [], None
        for response in stream_generate(self.model, self.tokenizer, ids, max_tokens=self.max_new_tokens):
            text.append(response.text)
            last = response
        latency = time.perf_counter() - started
        return Reading(
            answer="".join(text).strip(),
            meta={
                "latency_seconds": round(latency, 4),
                "prompt_tokens": len(ids),
                "completion_tokens": last.generation_tokens if last else 0,
                "finish_reason": last.finish_reason if last else "length",
            },
        )
