"""Tests for Stage 0 — FG4B Input. All Claude calls are mocked."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.lib import checkpoint
from app.models import FG4BInput
from app.stages import fg4b_input

TEST_SLUG = "test-fg4b-input-slug"

_VALID_RESPONSE = {
    "styled_block": "Our crew fixes roofs fast. No callbacks, no excuses.",
    "extracted_urls": ["https://fg4b.com/roofing"],
    "user_specified_links": [
        {
            "url": "https://fg4b.com/roofing",
            "context": "main roofing service page",
            "anchor_suggestion": "roofing repairs",
        }
    ],
    "themes": ["fast turnaround", "quality workmanship"],
}

_RAW_PROSE = "We fix roofs fast and cheap. Check out fg4b.com/roofing for more."


@pytest.fixture(autouse=True)
def patch_drafts(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)


@patch("app.stages.fg4b_input.ai_client.call")
def test_returns_valid_fg4b_input(mock_call):
    mock_call.return_value = json.dumps(_VALID_RESPONSE)
    result = fg4b_input.run(TEST_SLUG, _RAW_PROSE)
    assert isinstance(result, FG4BInput)
    assert result.raw_prose == _RAW_PROSE
    assert result.styled_block == _VALID_RESPONSE["styled_block"]
    assert result.themes == _VALID_RESPONSE["themes"]


@patch("app.stages.fg4b_input.ai_client.call")
def test_handles_json_wrapped_in_code_fences(mock_call):
    mock_call.return_value = f"```json\n{json.dumps(_VALID_RESPONSE)}\n```"
    result = fg4b_input.run(TEST_SLUG, _RAW_PROSE)
    assert isinstance(result, FG4BInput)
    assert result.styled_block == _VALID_RESPONSE["styled_block"]


@patch("app.stages.fg4b_input.ai_client.call")
def test_saves_checkpoint(mock_call, tmp_path):
    mock_call.return_value = json.dumps(_VALID_RESPONSE)
    fg4b_input.run(TEST_SLUG, _RAW_PROSE)
    saved = checkpoint.load(TEST_SLUG, "00_fg4b_input", FG4BInput)
    assert saved is not None
    assert saved.raw_prose == _RAW_PROSE


@patch("app.stages.fg4b_input.ai_client.call")
def test_raw_prose_preserved_in_output(mock_call):
    mock_call.return_value = json.dumps(_VALID_RESPONSE)
    result = fg4b_input.run(TEST_SLUG, _RAW_PROSE)
    assert result.raw_prose == _RAW_PROSE


@patch("app.stages.fg4b_input.ai_client.call")
def test_raises_on_invalid_json(mock_call):
    mock_call.return_value = "this is not json at all"
    with pytest.raises(ValueError, match="invalid JSON"):
        fg4b_input.run(TEST_SLUG, _RAW_PROSE)


@patch("app.stages.fg4b_input.ai_client.call")
def test_raises_on_missing_required_field(mock_call):
    bad_response = {k: v for k, v in _VALID_RESPONSE.items() if k != "styled_block"}
    mock_call.return_value = json.dumps(bad_response)
    with pytest.raises(ValueError, match="validation"):
        fg4b_input.run(TEST_SLUG, _RAW_PROSE)


@patch("app.stages.fg4b_input.ai_client.call")
def test_created_at_is_set_by_code(mock_call):
    """created_at must be set by the pipeline, not trusted from Claude."""
    mock_call.return_value = json.dumps(_VALID_RESPONSE)
    result = fg4b_input.run(TEST_SLUG, _RAW_PROSE)
    assert result.created_at is not None
