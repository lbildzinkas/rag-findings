"""The reader prompt, its hashes, and the reader interface with its
response cache. The template hash is pinned: changing the prompt is a
visible change that moves the hash recorded before any answer exists."""

from __future__ import annotations

from rag.reader import (
    CHUNK_SEPARATOR,
    CONTEXT_HEADING,
    FLOOR_INSTRUCTION,
    INSTRUCTION,
    QUESTION_PREFIX,
    SHORT_INSTRUCTION,
    CachedReader,
    FakeReader,
    LazyReader,
    Reading,
    ResponseCache,
    instruction,
    prompt_hash,
    render_prompt,
    settings_hash,
    template_hash,
)

PINNED_TEMPLATE_HASH = "9bf28410208fd69958bf3e5c67180b2127c7d95d7d13a3740126aa4e5508e5b5"


def test_template_hash_is_pinned():
    assert template_hash() == PINNED_TEMPLATE_HASH


def test_render_prompt_lays_out_instruction_context_question():
    prompt = render_prompt("What is Kerberos?", ("chunk one", "chunk two"), short=False)
    lines = prompt.split("\n")
    assert lines[0] == INSTRUCTION
    assert f"{CONTEXT_HEADING}" in lines
    assert prompt.index("chunk one") < prompt.index("chunk two")  # packed order
    assert prompt.endswith(f"{QUESTION_PREFIX} What is Kerberos?")
    assert prompt.count("\n\n") >= 3


def test_short_answer_addon_and_floor_variant():
    short = render_prompt("q", ("c",), short=True)
    assert short.startswith(f"{INSTRUCTION} {SHORT_INSTRUCTION}")
    floor = render_prompt("q", (), short=False, retrieval=False)
    assert floor.startswith(FLOOR_INSTRUCTION)
    assert "from the context only" not in floor
    assert CONTEXT_HEADING not in floor
    assert floor.endswith(f"{QUESTION_PREFIX} q")
    floor_short = render_prompt("q", (), short=True, retrieval=False)
    assert floor_short.startswith(f"{FLOOR_INSTRUCTION} {SHORT_INSTRUCTION}")


def test_instruction_helper():
    assert instruction(False, True) == INSTRUCTION
    assert instruction(True, True) == f"{INSTRUCTION} {SHORT_INSTRUCTION}"
    assert instruction(False, False) == FLOOR_INSTRUCTION


def test_prompt_and_settings_hashes():
    assert prompt_hash("a") != prompt_hash("b")
    assert settings_hash("m", {"do_sample": False}) == settings_hash("m", {"do_sample": False})
    assert settings_hash("m", {"do_sample": False}) != settings_hash("m", {"do_sample": True})
    assert settings_hash("m", {"a": 1}) != settings_hash("other", {"a": 1})


def test_response_cache_roundtrip_and_key_isolation(tmp_path):
    cache = ResponseCache(tmp_path / "reader-responses.sqlite")
    cache.put("glm-5.3-flash", "settings-a", "prompt one", "answer one")
    assert cache.get("glm-5.3-flash", "settings-a", "prompt one") == "answer one"
    assert cache.get("glm-5.3-flash", "settings-a", "prompt two") is None
    assert cache.get("glm-5.3-flash", "settings-b", "prompt one") is None
    assert cache.get("other-model", "settings-a", "prompt one") is None
    cache.put("glm-5.3-flash", "settings-a", "prompt one", "answer two")  # replace
    assert cache.get("glm-5.3-flash", "settings-a", "prompt one") == "answer two"
    cache.close()
    reopened = ResponseCache(tmp_path / "reader-responses.sqlite")  # persists on disk
    assert reopened.get("glm-5.3-flash", "settings-a", "prompt one") == "answer two"
    reopened.close()


def test_fake_reader_is_deterministic():
    reader = FakeReader(default="canned")
    assert reader.read("anything") == "canned"
    assert reader.prompts == ["anything"]


def test_cached_reader_hits_never_call_the_backend(tmp_path):
    cache = ResponseCache(tmp_path / "reader-responses.sqlite")
    backend = FakeReader(default="from the model")
    reader = CachedReader(cache, "glm-5.3-flash", "settings-a", backend)
    assert reader.read("prompt") == "from the model"
    assert reader.read("prompt") == "from the model"  # served from the cache
    assert len(backend.prompts) == 1  # the backend saw the prompt once
    fresh = CachedReader(cache, "glm-5.3-flash", "settings-a", FakeReader())
    assert fresh.read("prompt") == "from the model"  # a new run resumes free


def test_cached_reader_without_backend_fails_fast(tmp_path):
    cache = ResponseCache(tmp_path / "reader-responses.sqlite")
    reader = CachedReader(cache, "glm-5.3-flash", "settings-a", None)
    try:
        reader.read("prompt")
    except RuntimeError as exc:
        assert "no reader backend" in str(exc)
    else:
        raise AssertionError("expected a RuntimeError")


def test_chunk_separator_is_a_blank_line():
    assert CHUNK_SEPARATOR == "\n\n"


def test_response_cache_keeps_the_call_record(tmp_path):
    cache = ResponseCache(tmp_path / "answers.sqlite")
    cache.put("m", "s", "prompt", "answer", {"latency_seconds": 1.5, "finish_reason": "stop"})
    reading = cache.get_reading("m", "s", "prompt")
    assert reading == Reading(answer="answer", meta={"latency_seconds": 1.5, "finish_reason": "stop"}, cached=True)
    cache.put("m", "s", "bare", "answer")
    assert cache.get_reading("m", "s", "bare").meta == {}


def test_cached_reader_stores_a_backend_reading_and_counts_calls(tmp_path):
    cache = ResponseCache(tmp_path / "answers.sqlite")

    class Backend:
        def read(self, prompt):
            return Reading(answer=f"re: {prompt}", meta={"latency_seconds": 0.25})

    reader = CachedReader(cache, "m", "s", Backend())
    first = reader.reading("p")
    second = reader.reading("p")
    assert first == Reading(answer="re: p", meta={"latency_seconds": 0.25})
    assert second == Reading(answer="re: p", meta={"latency_seconds": 0.25}, cached=True)
    assert reader.calls == 1


def test_lazy_reader_loads_on_the_first_read_only():
    loads = []

    def load():
        loads.append(1)
        return FakeReader(default="x")

    lazy = LazyReader(load)
    assert lazy.loads == 0 and not loads
    assert lazy.read("a") == "x" and lazy.read("b") == "x"
    assert lazy.loads == 1 and len(loads) == 1
