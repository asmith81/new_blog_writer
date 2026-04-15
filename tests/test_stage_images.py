"""Tests for Stage 3 — Images. DALL-E and Cloudinary calls are mocked."""
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import call, patch

import pytest

from app.lib import checkpoint, cloudinary_client, image_client
from app.models import Brief, ImageBrief, ImagesOutput, InternalLink, KeywordPlacement, SectionBrief
from app.stages import images

TEST_SLUG = "test-images-slug"
NOW = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)

_FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # minimal fake PNG bytes
_COVER_URL = "https://res.cloudinary.com/djpz0hosc/image/upload/blog/test-images-slug/cover.png"
_BODY1_URL = "https://res.cloudinary.com/djpz0hosc/image/upload/blog/test-images-slug/body-1.png"

_ARTICLE_TEXT = """\
# Daily Job Site Report Guide for Contractors

Every contractor knows the feeling.

## Why Daily Job Site Reports Matter

Most contractors we work with didn't start using daily reports until after their first dispute.

## What to Include in Every Report

Weather, crew attendance, work completed.

## Conclusion

Start with a simple template.
"""


def _make_brief() -> Brief:
    return Brief(
        slug=TEST_SLUG,
        topic="daily job site report",
        article_type="how-to",
        primary_keyword="daily job site report",
        semantic_keywords=["job site report template"],
        lsi_keywords=["site documentation"],
        search_intent="informational",
        category="Documentation & Record Keeping",
        keyword_placement=KeywordPlacement(
            meta_title="Daily Job Site Report Guide | FG4B",
            meta_description="How to write a daily job site report.",
            h1_text="Daily Job Site Report Guide for Contractors",
            intro_keywords=["daily job site report"],
            image_alt_map={
                "cover": "contractor with clipboard",
                "body-1": "job site report on tablet",
            },
        ),
        sections=[
            SectionBrief(heading="Why Daily Job Site Reports Matter", level=2,
                         assigned_keywords=[], word_count_target=300, notes=""),
            SectionBrief(heading="Conclusion", level=2,
                         assigned_keywords=[], word_count_target=100, notes=""),
        ],
        total_word_count_target=1800,
        faq_questions=[],
        images=[
            ImageBrief(
                image_id="cover",
                image_type="cover",
                style="graphic-art",
                placement_after="",
                dalle_prompt="A contractor on a job site with a clipboard.",
                alt_text="contractor with clipboard",
                caption="Daily reports take 5 minutes.",
            ),
            ImageBrief(
                image_id="body-1",
                image_type="over-the-shoulder",
                style="photo-real",
                placement_after="Why Daily Job Site Reports Matter",
                dalle_prompt="Over-the-shoulder view of contractor filling out a report.",
                alt_text="job site report on tablet",
                caption="A structured template ensures nothing is missed.",
            ),
        ],
        internal_links=[],
        external_link={"url": "https://osha.gov", "anchor_text": "OSHA", "placement_section": ""},
        fg4b_block_placement="Why Daily Job Site Reports Matter",
        competitor_gap_notes="",
        created_at=NOW,
    )


@pytest.fixture(autouse=True)
def patch_drafts(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    import app.stages.images as img_stage
    monkeypatch.setattr(img_stage, "_DRAFTS_DIR", tmp_path)


@pytest.fixture(autouse=True)
def seed_fixtures(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    checkpoint.save(TEST_SLUG, "01_brief", _make_brief())
    slug_dir = tmp_path / TEST_SLUG
    slug_dir.mkdir(parents=True, exist_ok=True)
    (slug_dir / "article.md").write_text(_ARTICLE_TEXT, encoding="utf-8")


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_returns_images_output(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    result = images.run(TEST_SLUG)
    assert isinstance(result, ImagesOutput)
    assert len(result.images) == 2


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_generate_called_once_per_image(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    assert mock_generate.call_count == 2


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_upload_uses_correct_public_ids(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    upload_calls = [c.kwargs["public_id"] for c in mock_upload.call_args_list]
    assert f"blog/{TEST_SLUG}/cover" in upload_calls
    assert f"blog/{TEST_SLUG}/body-1" in upload_calls


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_png_files_saved_locally(mock_generate, mock_upload, tmp_path):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    assert (tmp_path / TEST_SLUG / "images" / "cover" / "cover.png").exists()
    assert (tmp_path / TEST_SLUG / "images" / "body-1" / "body-1.png").exists()


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_cover_blog_image_inserted_after_h1(mock_generate, mock_upload, tmp_path):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    content = (tmp_path / TEST_SLUG / "article.md").read_text(encoding="utf-8")
    h1_pos = content.find("# Daily Job Site Report")
    cover_pos = content.find(_COVER_URL)
    assert h1_pos < cover_pos


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_body_image_inserted_after_correct_heading(mock_generate, mock_upload, tmp_path):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    content = (tmp_path / TEST_SLUG / "article.md").read_text(encoding="utf-8")
    heading_pos = content.find("## Why Daily Job Site Reports Matter")
    body_pos = content.find(_BODY1_URL)
    assert heading_pos < body_pos
    # body-1 must come BEFORE the next section
    next_section_pos = content.find("## What to Include")
    assert body_pos < next_section_pos


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_checkpoint_saved(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    images.run(TEST_SLUG)
    loaded = checkpoint.load(TEST_SLUG, "03_images", ImagesOutput)
    assert loaded is not None
    assert len(loaded.images) == 2


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_image_results_have_correct_cloudinary_urls(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    result = images.run(TEST_SLUG)
    urls = {r.image_id: r.cloudinary_url for r in result.images}
    assert urls["cover"] == _COVER_URL
    assert urls["body-1"] == _BODY1_URL


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_all_images_marked_placed(mock_generate, mock_upload):
    mock_generate.return_value = _FAKE_PNG
    mock_upload.side_effect = [_COVER_URL, _BODY1_URL]
    result = images.run(TEST_SLUG)
    assert all(r.placed_in_article for r in result.images)


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_raises_if_brief_missing(mock_generate, mock_upload, tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    import app.stages.images as img_stage
    monkeypatch.setattr(img_stage, "_DRAFTS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="01_brief.json not found"):
        images.run("no-brief-slug")


@patch("app.stages.images.cloudinary_client.upload")
@patch("app.stages.images.image_client.generate")
def test_raises_if_article_missing(mock_generate, mock_upload, tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    import app.stages.images as img_stage
    monkeypatch.setattr(img_stage, "_DRAFTS_DIR", tmp_path)
    checkpoint.save("no-article-slug", "01_brief", _make_brief())
    with pytest.raises(FileNotFoundError, match="article.md not found"):
        images.run("no-article-slug")
