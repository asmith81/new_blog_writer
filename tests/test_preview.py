"""Tests for the preview CLI command."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()
TEST_SLUG = "test-preview-slug"


@pytest.fixture()
def fg4b_website(tmp_path):
    fg4b = tmp_path / "FG4B_Website"
    blog_dir = fg4b / "src" / "content" / "blog"
    blog_dir.mkdir(parents=True)
    (blog_dir / f"{TEST_SLUG}.mdx").write_text("---\ntitle: Test\n---\n", encoding="utf-8")
    return fg4b


@patch("app.cli.subprocess.run")
@patch("app.cli.settings")
def test_preview_spawns_npm_dev(mock_settings, mock_subprocess, fg4b_website):
    mock_settings.fg4b_website_path = str(fg4b_website)
    mock_subprocess.return_value = MagicMock(returncode=0)
    result = runner.invoke(app, ["preview", TEST_SLUG])
    assert result.exit_code == 0
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    assert "npm run dev" in str(call_args)


@patch("app.cli.subprocess.run")
@patch("app.cli.settings")
def test_preview_prints_correct_url(mock_settings, mock_subprocess, fg4b_website):
    mock_settings.fg4b_website_path = str(fg4b_website)
    mock_subprocess.return_value = MagicMock(returncode=0)
    result = runner.invoke(app, ["preview", TEST_SLUG])
    assert result.exit_code == 0
    assert f"localhost:4321/blog/{TEST_SLUG}" in result.output


@patch("app.cli.subprocess.run")
@patch("app.cli.settings")
def test_preview_uses_fg4b_website_as_cwd(mock_settings, mock_subprocess, fg4b_website):
    mock_settings.fg4b_website_path = str(fg4b_website)
    mock_subprocess.return_value = MagicMock(returncode=0)
    runner.invoke(app, ["preview", TEST_SLUG])
    call_kwargs = mock_subprocess.call_args.kwargs
    assert call_kwargs.get("cwd") == str(fg4b_website)


@patch("app.cli.settings")
def test_preview_exits_if_mdx_not_published(mock_settings, tmp_path):
    fg4b = tmp_path / "FG4B_Website"
    (fg4b / "src" / "content" / "blog").mkdir(parents=True)
    mock_settings.fg4b_website_path = str(fg4b)
    result = runner.invoke(app, ["preview", "unpublished-slug"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "publish" in result.output.lower()


@patch("app.cli.settings")
def test_preview_exits_if_fg4b_path_not_set(mock_settings):
    mock_settings.fg4b_website_path = ""
    result = runner.invoke(app, ["preview", TEST_SLUG])
    assert result.exit_code != 0
    assert "FG4B_WEBSITE_PATH" in result.output
