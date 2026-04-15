"""Tests for load_prompt() and strip_fences()."""
from pathlib import Path

import pytest

from app.lib.prompt_utils import load_prompt, strip_fences


# ---------------------------------------------------------------------------
# load_prompt
# ---------------------------------------------------------------------------

def test_load_prompt_reads_file(tmp_path, monkeypatch):
    import app.lib.prompt_utils as pu
    monkeypatch.setattr(pu, "_PROMPTS_DIR", tmp_path)
    (tmp_path / "test.txt").write_text("Hello world", encoding="utf-8")
    assert load_prompt("test.txt") == "Hello world"


def test_load_prompt_substitutes_variables(tmp_path, monkeypatch):
    import app.lib.prompt_utils as pu
    monkeypatch.setattr(pu, "_PROMPTS_DIR", tmp_path)
    (tmp_path / "tpl.txt").write_text("Topic: $topic\nType: $article_type", encoding="utf-8")
    result = load_prompt("tpl.txt", topic="roofing", article_type="how-to")
    assert result == "Topic: roofing\nType: how-to"


def test_load_prompt_safe_substitute_leaves_unknown_vars(tmp_path, monkeypatch):
    """$USD or $4M in user-supplied content must not raise — safe_substitute leaves them."""
    import app.lib.prompt_utils as pu
    monkeypatch.setattr(pu, "_PROMPTS_DIR", tmp_path)
    (tmp_path / "tpl.txt").write_text("Context: $context", encoding="utf-8")
    result = load_prompt("tpl.txt", context="Earned $4M last year via $USD invoices")
    assert "$4M" in result
    assert "$USD" in result


def test_load_prompt_missing_file_raises(tmp_path, monkeypatch):
    import app.lib.prompt_utils as pu
    monkeypatch.setattr(pu, "_PROMPTS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent.txt")


def test_load_prompt_subdirectory(tmp_path, monkeypatch):
    import app.lib.prompt_utils as pu
    monkeypatch.setattr(pu, "_PROMPTS_DIR", tmp_path)
    subdir = tmp_path / "research"
    subdir.mkdir()
    (subdir / "brief.txt").write_text("Brief for $topic", encoding="utf-8")
    result = load_prompt("research/brief.txt", topic="gutters")
    assert result == "Brief for gutters"


# ---------------------------------------------------------------------------
# strip_fences
# ---------------------------------------------------------------------------

def test_strip_fences_json_fence():
    raw = '```json\n{"key": "value"}\n```'
    assert strip_fences(raw) == '{"key": "value"}'


def test_strip_fences_plain_fence():
    raw = '```\n{"key": "value"}\n```'
    assert strip_fences(raw) == '{"key": "value"}'


def test_strip_fences_noop_on_clean_json():
    raw = '{"key": "value"}'
    assert strip_fences(raw) == '{"key": "value"}'


def test_strip_fences_handles_whitespace():
    raw = '  ```json\n{"key": "value"}\n```  '
    assert strip_fences(raw) == '{"key": "value"}'


def test_strip_fences_multiline_json():
    raw = '```json\n{\n  "slug": "test",\n  "topic": "roofing"\n}\n```'
    result = strip_fences(raw)
    assert result.startswith("{")
    assert result.endswith("}")
    assert '"slug"' in result
