"""Run config parsing, validation and content hash."""

from __future__ import annotations

import pytest
import yaml

from rag.config import config_hash, config_yaml, load_config, parse_config

BASE = {
    "dataset": {"name": "qasper", "splits": ["dev", "test"]},
    "chunking": {"method": "fixed", "chunk_tokens": 256, "overlap": 0},
    "pipeline": "bm25",
    "budget": 1024,
    "view": "production",
    "top_n": 8,
    "seed": 0,
    "run_name": "tracer",
}


def test_parse_valid_config():
    cfg = parse_config(dict(BASE))
    assert cfg.dataset == "qasper"
    assert cfg.splits == ("dev", "test")
    assert cfg.chunk_tokens == 256
    assert cfg.budget == 1024
    assert cfg.view == "production"
    assert cfg.top_n == 8
    assert cfg.seed == 0
    assert cfg.search_depth == 100  # default


def test_load_config_from_file(tmp_path):
    path = tmp_path / "tracer.yaml"
    path.write_text(yaml.safe_dump(BASE), encoding="utf-8")
    cfg = load_config(path)
    assert cfg.run_name == "tracer"


def test_config_hash_is_content_based():
    one = parse_config(dict(BASE))
    two = parse_config({**BASE, "run_name": "other"})
    same = parse_config(dict(BASE))
    assert config_hash(one) == config_hash(same)
    assert config_hash(one) != config_hash(two)
    # hash is independent of key order in the raw dict
    shuffled = {k: BASE[k] for k in reversed(list(BASE))}
    assert config_hash(parse_config(shuffled)) == config_hash(one)


def test_config_yaml_is_canonical():
    cfg = parse_config(dict(BASE))
    text = config_yaml(cfg)
    assert text == config_yaml(parse_config(yaml.safe_load(text)))
    assert "name: qasper" in text


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c.update(dataset={"name": "nq", "splits": ["dev"]}),
        lambda c: c.update(chunking={"method": "recursive", "chunk_tokens": 256, "overlap": 0}),
        lambda c: c.update(chunking={"method": "fixed", "chunk_tokens": 256, "overlap": 64}),
        lambda c: c.update(pipeline="vector"),
        lambda c: c.update(budget=0),
        lambda c: c.update(view="sideways"),
        lambda c: c.update(top_n=0),
        lambda c: c.update(dataset={"name": "qasper", "splits": ["train", "bogus"]}),
    ],
)
def test_invalid_configs_rejected(mutate):
    raw = dict(BASE)
    raw = {k: (dict(v) if isinstance(v, dict) else v) for k, v in raw.items()}
    raw["chunking"] = dict(raw["chunking"])
    raw["dataset"] = dict(raw["dataset"])
    mutate(raw)
    with pytest.raises(ValueError):
        parse_config(raw)


def test_missing_keys_rejected():
    with pytest.raises(ValueError):
        parse_config({"dataset": {"name": "qasper"}})
