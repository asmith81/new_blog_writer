"""Tests for CLI commands — import, help, and basic invocation.

Pipeline stages are mocked so no real API calls are made.
"""
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_help_exits_zero():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "blog" in result.output.lower() or "pipeline" in result.output.lower()


def test_all_commands_listed_in_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ["write", "research", "draft", "images", "publish", "preview", "add-image", "list", "status"]:
        assert cmd in result.output


@patch("app.cli.Pipeline")
def test_write_stub_runs_without_crash(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_from = MagicMock()
    result = runner.invoke(app, ["write", "test topic", "--type", "how-to"])
    assert result.exit_code == 0
    assert "test-topic" in result.output


@patch("app.cli.Pipeline")
def test_write_auto_flag(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_from = MagicMock()
    result = runner.invoke(app, ["write", "test topic", "--auto"])
    assert result.exit_code == 0
    assert "auto" in result.output


@patch("app.cli.Pipeline")
def test_research_stub_runs(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_stage = MagicMock()
    result = runner.invoke(app, ["research", "test-slug"])
    assert result.exit_code == 0
    mock_pipeline_cls.return_value.run_stage.assert_called_once_with(1)


@patch("app.cli.Pipeline")
def test_draft_stub_runs(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_stage = MagicMock()
    result = runner.invoke(app, ["draft", "test-slug"])
    assert result.exit_code == 0
    mock_pipeline_cls.return_value.run_stage.assert_called_once_with(2)


@patch("app.cli.Pipeline")
def test_images_stub_runs(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_stage = MagicMock()
    result = runner.invoke(app, ["images", "test-slug"])
    assert result.exit_code == 0
    mock_pipeline_cls.return_value.run_stage.assert_called_once_with(3)


@patch("app.cli.Pipeline")
def test_publish_stub_runs(mock_pipeline_cls):
    mock_pipeline_cls.return_value.run_stage = MagicMock()
    result = runner.invoke(app, ["publish", "test-slug"])
    assert result.exit_code == 0
    mock_pipeline_cls.return_value.run_stage.assert_called_once_with(4)


def test_list_no_crash_empty():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_status_no_crash():
    result = runner.invoke(app, ["status", "nonexistent-slug"])
    assert result.exit_code == 0
    assert "nonexistent-slug" in result.output
