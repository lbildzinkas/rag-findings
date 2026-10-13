"""Run config parsing, validation and content hash."""

from __future__ import annotations

import pytest
import yaml

from rag.config import (
    DatasetRef,
    GridConfig,
    RunConfig,
    config_hash,
    config_yaml,
    load_any_config,
    load_config,
    parse_config,
    parse_grid_config,
)

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
    assert cfg.sources == (DatasetRef("qasper", ("dev", "test")),)
    assert cfg.chunk_tokens == 256
    assert cfg.budget == 1024
    assert cfg.view == "production"
    assert cfg.top_n == 8
    assert cfg.seed == 0
    assert cfg.search_depth == 100  # default


def test_parse_nq_and_pooled_sources():
    nq = parse_config({**BASE, "dataset": {"name": "nq", "splits": ["dev"]}})
    assert nq.dataset == "nq"
    assert nq.sources == (DatasetRef("nq", ("dev",)),)
    assert nq.as_dict()["dataset"] == {"name": "nq", "splits": ["dev"]}

    pooled_raw = {
        "dataset": {
            "name": "pooled",
            "sources": [{"name": "qasper", "splits": ["dev"]}, {"name": "nq", "splits": ["dev"]}],
        }
    }
    pooled = parse_config({**BASE, **pooled_raw})
    assert pooled.dataset == "pooled"
    assert pooled.sources == (DatasetRef("qasper", ("dev",)), DatasetRef("nq", ("dev",)))
    assert pooled.as_dict()["dataset"] == pooled_raw["dataset"]
    # round-trips through the canonical dict and hashes stably
    assert parse_config(pooled.as_dict()) == pooled
    assert config_hash(parse_config(pooled.as_dict())) == config_hash(pooled)


@pytest.mark.parametrize(
    "dataset",
    [
        {"name": "nq", "splits": ["train"]},  # the NQ train split is never loaded
        {"name": "wiki", "splits": ["dev"]},
        {"name": "pooled", "splits": ["dev"]},  # pooled needs sources
        {"name": "pooled", "sources": [{"name": "qasper", "splits": ["dev"]}]},  # one source is not pooled
        {"name": "pooled", "sources": [{"name": "qasper", "splits": ["dev"]}, {"name": "qasper", "splits": ["test"]}]},
        {"name": "pooled", "sources": [{"name": "qasper", "splits": ["dev"]}, {"name": "nq", "splits": ["test"]}]},
        {"sources": [{"name": "qasper", "splits": ["dev"]}, {"name": "nq", "splits": ["dev"]}]},
    ],
)
def test_invalid_dataset_blocks_rejected(dataset):
    with pytest.raises(ValueError):
        parse_config({**BASE, "dataset": dataset})


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
        lambda c: c.update(dataset={"name": "nq", "splits": ["train"]}),
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


GRID = {
    "kind": "grid",
    "dataset": {"name": "qasper", "splits": ["dev", "test"]},
    "pipeline": "bm25",
    "chunkings": [
        {"name": "fixed-64", "method": "fixed", "chunk_tokens": 64},
        {"name": "section-aware", "method": "section_aware", "max_tokens": 512},
        {"name": "small-to-big", "method": "small_to_big", "max_tokens": 512, "child_tokens": 128},
    ],
    "budgets": [128, 256, 512],
    "top_n": 8,
    "side_top_n": 5,
    "scopes": ["collection", "document"],
    "fixed_k": [1, 5, 10],
    "seed": 0,
    "run_name": "grid",
}


def grid(**changes):
    raw = yaml.safe_load(yaml.safe_dump(GRID))
    raw.update(changes)
    return raw


def test_parse_grid_config():
    cfg = parse_grid_config(grid())
    assert [c.name for c in cfg.chunkings] == ["fixed-64", "section-aware", "small-to-big"]
    assert [c.fixed_size for c in cfg.chunkings] == [64, None, None]
    assert cfg.chunkings[2].child_tokens == 128
    assert cfg.budgets == (128, 256, 512)
    assert cfg.search_depth == 1000  # default
    assert parse_grid_config(cfg.as_dict()) == cfg
    assert config_hash(parse_grid_config(grid())) == config_hash(cfg)
    assert "small_to_big" in config_yaml(cfg)


def test_load_any_config_dispatches_on_kind(tmp_path):
    grid_path = tmp_path / "grid.yaml"
    grid_path.write_text(yaml.safe_dump(GRID), encoding="utf-8")
    single_path = tmp_path / "tracer.yaml"
    single_path.write_text(yaml.safe_dump(BASE), encoding="utf-8")
    assert isinstance(load_any_config(grid_path), GridConfig)
    assert isinstance(load_any_config(single_path), RunConfig)


@pytest.mark.parametrize(
    "changes",
    [
        {"pipeline": "vector"},
        {"chunkings": []},
        {"chunkings": [{"name": "a", "method": "fixed", "chunk_tokens": 64}] * 2},
        {"chunkings": [{"name": "a", "method": "semantic", "chunk_tokens": 64}]},
        {"chunkings": [{"name": "a", "method": "fixed", "chunk_tokens": 0}]},
        {"chunkings": [{"name": "a", "method": "fixed", "chunk_tokens": 64, "overlap": 8}]},
        {"chunkings": [{"name": "a", "method": "small_to_big", "max_tokens": 512}]},
        {"budgets": [256, 128]},
        {"budgets": []},
        {"fixed_k": [0, 5]},
        {"top_n": 0},
        {"side_top_n": -1},
        {"scopes": ["document"]},
        {"scopes": ["collection", "galaxy"]},
        {"search_depth": 0},
        {"dataset": {"name": "nq", "splits": ["test"]}},
    ],
)
def test_invalid_grid_configs_rejected(changes):
    with pytest.raises(ValueError):
        parse_grid_config(grid(**changes))
