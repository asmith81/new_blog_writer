"""Tests for checkpoint save/load round-trip."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.lib import checkpoint
from app.models import Brief, ImageBrief, InternalLink, KeywordPlacement, SectionBrief

NOW = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)
TEST_SLUG = "test-checkpoint-slug"


def make_brief() -> Brief:
    return Brief(
        slug=TEST_SLUG,
        topic="test topic",
        article_type="how-to",
        primary_keyword="test keyword",
        semantic_keywords=["kw1"],
        lsi_keywords=["lsi1"],
        search_intent="informational",
        category="roofing",
        keyword_placement=KeywordPlacement(
            meta_title="Test Title",
            meta_description="Test description for meta.",
            h1_text="Test H1",
            intro_keywords=["test keyword"],
            image_alt_map={"cover": "alt text"},
        ),
        sections=[
            SectionBrief(
                heading="Section One",
                level=2,
                assigned_keywords=["kw1"],
                word_count_target=300,
                notes="Write about this.",
            )
        ],
        total_word_count_target=1800,
        faq_questions=["FAQ question one?"],
        images=[
            ImageBrief(
                image_id="cover",
                image_type="cover",
                style="photo-real",
                placement_after="",
                dalle_prompt="A roofing scene.",
                alt_text="alt text",
                caption="A caption.",
            )
        ],
        internal_links=[
            InternalLink(
                target_slug="other-slug",
                target_title="Other Article",
                anchor_text="other article",
                placement_section="Section One",
            )
        ],
        external_link={"url": "https://example.com", "anchor_text": "example", "placement_section": "Section One"},
        fg4b_block_placement="Section One",
        competitor_gap_notes="None found.",
        created_at=NOW,
    )


@pytest.fixture(autouse=True)
def patch_drafts_dir(tmp_path, monkeypatch):
    """Redirect checkpoint._DRAFTS_DIR to a temp directory for tests."""
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)


def test_save_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    brief = make_brief()
    path = checkpoint.save(TEST_SLUG, "01_brief", brief)
    assert path.exists()
    assert path.suffix == ".json"


def test_save_writes_valid_json(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    brief = make_brief()
    path = checkpoint.save(TEST_SLUG, "01_brief", brief)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["slug"] == TEST_SLUG


def test_load_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    result = checkpoint.load("nonexistent-slug", "01_brief", Brief)
    assert result is None


def test_save_load_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    brief = make_brief()
    checkpoint.save(TEST_SLUG, "01_brief", brief)
    loaded = checkpoint.load(TEST_SLUG, "01_brief", Brief)
    assert loaded == brief


def test_save_creates_parent_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    slug = "nested/slug/test"
    brief = make_brief()
    path = checkpoint.save(slug, "01_brief", brief)
    assert path.exists()
