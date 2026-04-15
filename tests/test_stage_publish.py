"""Tests for Stage 4 — Publish. No API calls; file system operations use tmp_path."""
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from app.lib import checkpoint
from app.models import (
    Brief, ImageBrief, ImageResult, ImagesOutput, InternalLink,
    KeywordPlacement, PublishResult, SectionBrief,
)
from app.stages import publish

TEST_SLUG = "test-publish-slug"
NOW = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)

_COVER_URL = "https://res.cloudinary.com/djpz0hosc/image/upload/blog/test-publish-slug/cover.png"

_ARTICLE_WITH_COMPONENTS = """\
# Daily Job Site Report Guide for Contractors

<BlogImage src="https://example.com/cover.png" alt="cover" caption="A caption." />

Every contractor knows the feeling.

## Why Daily Job Site Reports Matter

<FG4BBlock>
We worked with a roofing contractor who lost a dispute.
</FG4BBlock>

## Conclusion

Start with a simple template.
"""

_ARTICLE_PLAIN = """\
# Plain Article

Every contractor knows the feeling.

## Why Reports Matter

Content here.

## Conclusion

Done.
"""


def _make_brief() -> Brief:
    return Brief(
        slug=TEST_SLUG,
        topic="daily job site report",
        article_type="how-to",
        primary_keyword="daily job site report",
        semantic_keywords=[],
        lsi_keywords=[],
        search_intent="informational",
        category="Documentation & Record Keeping",
        keyword_placement=KeywordPlacement(
            meta_title="Daily Job Site Report Guide for Contractors | FG4B",
            meta_description="Learn how to write a daily job site report that protects your business from disputes.",
            h1_text="Daily Job Site Report Guide for Contractors",
            intro_keywords=["daily job site report"],
            image_alt_map={"cover": "contractor with clipboard"},
        ),
        sections=[
            SectionBrief(heading="Why Daily Job Site Reports Matter", level=2,
                         assigned_keywords=[], word_count_target=300, notes=""),
        ],
        total_word_count_target=1800,
        faq_questions=[],
        images=[
            ImageBrief(image_id="cover", image_type="cover", style="graphic-art",
                       placement_after="", dalle_prompt="A contractor.",
                       alt_text="contractor with clipboard", caption="caption"),
        ],
        internal_links=[],
        external_link={"url": "https://osha.gov", "anchor_text": "OSHA", "placement_section": ""},
        fg4b_block_placement="Why Daily Job Site Reports Matter",
        competitor_gap_notes="",
        created_at=NOW,
    )


def _make_images_output() -> ImagesOutput:
    return ImagesOutput(
        slug=TEST_SLUG,
        images=[
            ImageResult(
                image_id="cover",
                local_path="drafts/test-publish-slug/images/cover/cover.png",
                cloudinary_url=_COVER_URL,
                alt_text="contractor with clipboard",
                caption="caption",
                placed_in_article=True,
            )
        ],
        completed_at=NOW,
    )


@pytest.fixture()
def fg4b_website(tmp_path):
    """Create a fake FG4B_Website structure."""
    fg4b = tmp_path / "FG4B_Website"
    (fg4b / "src" / "content" / "blog").mkdir(parents=True)
    (fg4b / "archive").mkdir()
    return fg4b


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch, fg4b_website):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path / "drafts")
    import app.stages.publish as pub
    monkeypatch.setattr(pub, "_DRAFTS_DIR", tmp_path / "drafts")
    monkeypatch.setattr(pub.settings, "fg4b_website_path", str(fg4b_website))

    # Seed brief
    checkpoint.save(TEST_SLUG, "01_brief", _make_brief())

    # Create article.md
    slug_dir = tmp_path / "drafts" / TEST_SLUG
    slug_dir.mkdir(parents=True, exist_ok=True)
    (slug_dir / "article.md").write_text(_ARTICLE_WITH_COMPONENTS, encoding="utf-8")


def test_mdx_file_written_to_correct_path(tmp_path, fg4b_website):
    publish.run(TEST_SLUG)
    dest = fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx"
    assert dest.exists()


def test_frontmatter_title_from_brief(tmp_path, fg4b_website):
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["title"] == "Daily Job Site Report Guide for Contractors | FG4B"


def test_frontmatter_description_from_brief(tmp_path, fg4b_website):
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    fm = yaml.safe_load(content.split("---")[1])
    assert "daily job site report" in fm["description"].lower()


def test_frontmatter_category_from_brief(tmp_path, fg4b_website):
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["category"] == "Documentation & Record Keeping"


def test_frontmatter_hero_image_from_images_output(tmp_path, fg4b_website):
    checkpoint.save(TEST_SLUG, "03_images", _make_images_output())
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["heroImage"] == _COVER_URL


def test_frontmatter_no_hero_image_when_images_missing(tmp_path, fg4b_website):
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    fm = yaml.safe_load(content.split("---")[1])
    assert "heroImage" not in fm


def test_imports_added_when_components_present(fg4b_website):
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    assert "import FG4BBlock" in content
    assert "import BlogImage" in content


def test_imports_omitted_when_no_components(tmp_path, fg4b_website, monkeypatch):
    # Overwrite article with plain markdown (no components)
    import app.stages.publish as pub
    (tmp_path / "drafts" / TEST_SLUG / "article.md").write_text(_ARTICLE_PLAIN, encoding="utf-8")
    publish.run(TEST_SLUG)
    content = (fg4b_website / "src" / "content" / "blog" / f"{TEST_SLUG}.mdx").read_text()
    assert "import FG4BBlock" not in content
    assert "import BlogImage" not in content


def test_archive_directory_created(fg4b_website):
    publish.run(TEST_SLUG)
    archive_entries = list((fg4b_website / "archive").iterdir())
    assert len(archive_entries) == 1
    assert TEST_SLUG in archive_entries[0].name


def test_publish_result_checkpoint_saved():
    publish.run(TEST_SLUG)
    loaded = checkpoint.load(TEST_SLUG, "04_publish", PublishResult)
    assert loaded is not None
    assert loaded.slug == TEST_SLUG


def test_raises_if_brief_missing(tmp_path, fg4b_website, monkeypatch):
    import app.stages.publish as pub
    monkeypatch.setattr(pub, "_DRAFTS_DIR", tmp_path / "drafts")
    with pytest.raises(FileNotFoundError, match="01_brief.json not found"):
        publish.run("no-brief-slug")


def test_raises_if_article_missing(tmp_path, fg4b_website):
    (tmp_path / "drafts" / TEST_SLUG / "article.md").unlink()
    with pytest.raises(FileNotFoundError, match="article.md not found"):
        publish.run(TEST_SLUG)


def test_raises_if_fg4b_website_path_not_set(monkeypatch):
    import app.stages.publish as pub
    monkeypatch.setattr(pub.settings, "fg4b_website_path", "")
    with pytest.raises(RuntimeError, match="FG4B_WEBSITE_PATH"):
        publish.run(TEST_SLUG)
