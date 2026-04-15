"""Tests for the add-image CLI command."""
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from app.cli import app
from app.lib.config import config

runner = CliRunner()
TEST_SLUG = "test-add-image-slug"
_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])

_ARTICLE_TEXT = """\
# Test Article Title

Intro paragraph here.

## Installation Process

This section covers the installation.

## Cost Breakdown

Here we discuss costs.

## Conclusion

Final thoughts.
"""

_FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
_CLOUDINARY_URL = "https://res.cloudinary.com/djpz0hosc/image/upload/blog/test-add-image-slug/crew-photo.png"


@pytest.fixture(autouse=True)
def setup_article(tmp_path, monkeypatch):
    import app.cli as cli_module
    monkeypatch.setattr(cli_module, "_DRAFTS_DIR", tmp_path)
    slug_dir = tmp_path / TEST_SLUG
    slug_dir.mkdir(parents=True)
    (slug_dir / "article.md").write_text(_ARTICLE_TEXT, encoding="utf-8")


@pytest.fixture()
def fake_image(tmp_path):
    img = tmp_path / "crew-photo.png"
    img.write_bytes(_FAKE_PNG)
    return img


@patch("app.cli.cloudinary_client.upload")
def test_uploads_image_to_cloudinary(mock_upload, fake_image):
    mock_upload.return_value = _CLOUDINARY_URL
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    assert result.exit_code == 0
    mock_upload.assert_called_once()


@patch("app.cli.cloudinary_client.upload")
def test_upload_uses_correct_public_id(mock_upload, fake_image):
    mock_upload.return_value = _CLOUDINARY_URL
    runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    _, kwargs = mock_upload.call_args
    assert kwargs["public_id"] == f"blog/{TEST_SLUG}/crew-photo"


@patch("app.cli.cloudinary_client.upload")
def test_blog_image_inserted_after_heading(mock_upload, fake_image, tmp_path):
    mock_upload.return_value = _CLOUDINARY_URL
    runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    import app.cli as cli_module
    content = (tmp_path / TEST_SLUG / "article.md").read_text(encoding="utf-8")
    heading_pos = content.find("## Installation Process")
    image_pos = content.find(_CLOUDINARY_URL)
    assert heading_pos < image_pos
    # Image must appear before the next section
    next_section_pos = content.find("## Cost Breakdown")
    assert image_pos < next_section_pos


@patch("app.cli.cloudinary_client.upload")
def test_cloudinary_url_printed(mock_upload, fake_image):
    mock_upload.return_value = _CLOUDINARY_URL
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    # Rich may line-wrap the URL — collapse newlines before asserting
    assert _CLOUDINARY_URL in result.output.replace("\n", "")


@patch("app.cli.cloudinary_client.upload")
def test_publish_reminder_printed(mock_upload, fake_image):
    mock_upload.return_value = _CLOUDINARY_URL
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    assert "publish" in result.output.lower()


def test_exits_if_image_path_not_found(tmp_path):
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(tmp_path / "nonexistent.png"), "--after", "Installation Process"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


@patch("app.cli.cloudinary_client.upload")
def test_exits_if_article_md_missing(mock_upload, fake_image, tmp_path, monkeypatch):
    import app.cli as cli_module
    monkeypatch.setattr(cli_module, "_DRAFTS_DIR", tmp_path)
    # autouse fixture creates article.md — remove it so the command hits the missing-file path
    (tmp_path / TEST_SLUG / "article.md").unlink()
    mock_upload.return_value = _CLOUDINARY_URL
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Installation Process"])
    assert result.exit_code != 0
    assert "article.md not found" in result.output


@patch("app.cli.cloudinary_client.upload")
def test_warns_if_heading_not_found(mock_upload, fake_image):
    mock_upload.return_value = _CLOUDINARY_URL
    result = runner.invoke(app, ["add-image", TEST_SLUG, str(fake_image), "--after", "Nonexistent Heading"])
    assert result.exit_code == 0
    assert "not found" in result.output.lower() or "warning" in result.output.lower()
