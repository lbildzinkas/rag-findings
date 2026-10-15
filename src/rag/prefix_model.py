"""The MLX prefix writer: a 4-bit model on Apple silicon through mlx-lm.

macOS only; mlx-lm comes from the optional `prefixes` dependency group
(`uv run --group prefixes rag prefixes <config>`), so tests and CI never
import this module. Weights download once into data/hf-cache/ at the
pinned revision and load offline from there.

The chat template renders the prompt with thinking disabled. The rendered
text is split at the chunk: the head (system turn, the document or window,
the words before the chunk) is prefilled once into a prompt cache, and
each chunk's prompt is only its tail tokens on top of that cache. Chunks
are generated in batches, greedily, up to the new-token limit.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from .models import use_project_cache
from .prefixes import Prefix, PrefixConfig, PromptTemplate

_WEIGHT_FILES = ["*.json", "*.txt", "model.safetensors"]
_SENTINEL = "\x00rag-chunk\x00"
_PREFILL_STEP = 2048


def load_writer(cfg: PrefixConfig, data_dir: Path, prompt: PromptTemplate) -> MlxPrefixWriter:
    use_project_cache(data_dir)
    from huggingface_hub import snapshot_download

    path = snapshot_download(cfg.model_id, revision=cfg.revision, allow_patterns=_WEIGHT_FILES)
    return MlxPrefixWriter(
        model_key=cfg.model_key,
        path=Path(path),
        prompt=prompt,
        max_new_tokens=cfg.max_new_tokens,
        batch_size=cfg.batch_size,
    )


class MlxPrefixWriter:
    def __init__(self, model_key: str, path: Path, prompt: PromptTemplate, max_new_tokens: int, batch_size: int):
        from mlx_lm import load

        self.model_key = model_key
        self.prompt = prompt
        self.max_new_tokens = max_new_tokens
        self.batch_size = batch_size
        self.model, self.tokenizer = load(str(path))

    def render(self, context: str) -> tuple[str, str]:
        """The chat-templated prompt around the chunk: (head, tail)."""
        head, tail = self.prompt.split(context)
        text = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": head + _SENTINEL + tail}],
            add_generation_prompt=True,
            enable_thinking=False,
            tokenize=False,
        )
        if text.count(_SENTINEL) != 1:
            raise ValueError("the chat template changed the chunk slot")
        before, after = text.split(_SENTINEL)
        return before, after

    def _encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text, add_special_tokens=False)

    def write(self, context: str, chunks: Sequence[str]) -> list[Prefix]:
        import mlx.core as mx
        from mlx_lm.generate import BatchGenerator
        from mlx_lm.models.cache import make_prompt_cache

        head, tail = self.render(context)
        head_ids = mx.array(self._encode(head))
        prompt_cache = make_prompt_cache(self.model)
        for start in range(0, head_ids.size, _PREFILL_STEP):
            self.model(head_ids[None, start : start + _PREFILL_STEP], cache=prompt_cache)
            mx.eval([c.state for c in prompt_cache])
        mx.clear_cache()

        generator = BatchGenerator(
            self.model,
            max_tokens=self.max_new_tokens,
            stop_tokens=set(self.tokenizer.eos_token_ids),
            completion_batch_size=self.batch_size,
            prefill_batch_size=self.batch_size,
        )
        try:
            # every prompt reads a merged copy of the one prefilled cache
            uids = generator.insert(
                [self._encode(chunk + tail) for chunk in chunks], caches=[prompt_cache] * len(chunks)
            )
            tokens: dict[int, list[int]] = {uid: [] for uid in uids}
            finish: dict[int, str] = {}
            while responses := generator.next():
                for r in responses:
                    if r.finish_reason != "stop":
                        tokens[r.uid].append(r.token)
                    if r.finish_reason is not None:
                        finish[r.uid] = r.finish_reason
        finally:
            generator.close()
        mx.clear_cache()
        return [
            Prefix(
                text=self.tokenizer.decode(tokens[uid]).strip(),
                n_tokens=len(tokens[uid]),
                truncated=finish[uid] == "length",
            )
            for uid in uids
        ]
