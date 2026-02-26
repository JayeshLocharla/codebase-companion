"""Tests for app.config."""

import os

import pytest

from app.config import Config, validate_environment


def test_config_defaults():
    cfg = Config()
    assert cfg.openai_model == "gpt-3.5-turbo"
    assert cfg.retriever_k == 4
    assert cfg.default_max_files == 3


def test_config_from_env_reads_openai_model(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    cfg = Config.from_env()
    assert cfg.openai_model == "gpt-4o"


def test_config_from_env_reads_max_files(monkeypatch):
    monkeypatch.setenv("MAX_FILES", "10")
    cfg = Config.from_env()
    assert cfg.default_max_files == 10


def test_validate_environment_raises_when_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
        validate_environment()


def test_validate_environment_passes_when_key_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")
    # Should not raise
    validate_environment()
