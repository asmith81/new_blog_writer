"""Tests for ai_client.call() — all Claude API calls are mocked."""
from unittest.mock import MagicMock, patch

import pytest

from app.lib import ai_client


def _make_mock_response(text: str):
    """Build a mock Anthropic messages.create() response."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_returns_response_text(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response('{"result": "ok"}')

    result = ai_client.call(system_prompt="You are helpful.", user_prompt="Say hello.")
    assert result == '{"result": "ok"}'


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_uses_config_model_by_default(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("response")

    ai_client.call(system_prompt="sys", user_prompt="usr")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == ai_client._DEFAULT_MODEL


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_uses_explicit_model_when_passed(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("response")

    ai_client.call(system_prompt="sys", user_prompt="usr", model="claude-haiku-4-5-20251001")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_passes_correct_messages(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("response")

    ai_client.call(system_prompt="Be concise.", user_prompt="What is a roof?")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["system"] == "Be concise."
    assert call_kwargs["messages"] == [{"role": "user", "content": "What is a roof?"}]


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_passes_max_tokens(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("response")

    ai_client.call(system_prompt="sys", user_prompt="usr", max_tokens=8000)

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["max_tokens"] == 8000


@patch("app.lib.ai_client.anthropic.Anthropic")
def test_call_logs_raw_response(mock_anthropic_cls, caplog):
    import logging
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("logged response text")

    with caplog.at_level(logging.DEBUG, logger="app.lib.ai_client"):
        ai_client.call(system_prompt="sys", user_prompt="usr")

    assert "logged response text" in caplog.text
