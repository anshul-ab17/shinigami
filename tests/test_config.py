import os
from pathlib import Path
from shinigami.config import Settings, load_settings


def test_settings_defaults():
    s = Settings()
    assert s.provider == "claude"
    assert s.claude_model == "claude-sonnet-4-6"
    assert s.openai_model == "gpt-4o"
    assert isinstance(s.output_dir, Path)


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("SHINIGAMI_PROVIDER", "openai")
    s = Settings()
    assert s.provider == "openai"


def test_load_settings_from_yaml(tmp_path):
    config = tmp_path / "shinigami.config.yaml"
    config.write_text("provider: openai\nopenai_model: gpt-4o-mini\n")
    s = load_settings(config)
    assert s.provider == "openai"
    assert s.openai_model == "gpt-4o-mini"


def test_load_settings_no_file():
    s = load_settings(None)
    assert s.provider == "claude"
