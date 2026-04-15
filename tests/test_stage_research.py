"""Tests for Stage 1 — Research Brief. All Claude calls are mocked."""
import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.lib import checkpoint, content_index
from app.models import Brief
from app.stages import research

TEST_SLUG = "test-research-slug"
TEST_TOPIC = "how to write a daily job site report"
TEST_TYPE = "how-to"

_VALID_BRIEF = {
    "slug": TEST_SLUG,
    "topic": TEST_TOPIC,
    "article_type": TEST_TYPE,
    "primary_keyword": "daily job site report",
    "semantic_keywords": ["job site report template", "construction daily report"],
    "lsi_keywords": ["site documentation", "crew accountability"],
    "search_intent": "informational",
    "category": "Documentation & Record Keeping",
    "keyword_placement": {
        "meta_title": "Daily Job Site Report Guide for Contractors | FG4B",
        "meta_description": "Learn how to write a daily job site report that keeps your crew accountable and protects your business from disputes.",
        "h1_text": "Daily Job Site Report Guide for Contractors",
        "intro_keywords": ["daily job site report", "site documentation"],
        "image_alt_map": {
            "cover": "contractor filling out a daily job site report on a tablet",
            "body-1": "job site report template on clipboard",
        },
    },
    "sections": [
        {
            "heading": "Why Daily Job Site Reports Matter",
            "level": 2,
            "assigned_keywords": ["job site report"],
            "word_count_target": 300,
            "notes": "Cover liability protection, crew accountability, and billing disputes.",
        },
        {
            "heading": "What to Include in Every Report",
            "level": 2,
            "assigned_keywords": ["daily report template"],
            "word_count_target": 400,
            "notes": "Weather, crew attendance, work completed, materials used, incidents.",
        },
        {
            "heading": "FAQ",
            "level": 2,
            "assigned_keywords": [],
            "word_count_target": 200,
            "notes": "Answer 3 common questions about daily reports.",
        },
        {
            "heading": "Conclusion",
            "level": 2,
            "assigned_keywords": [],
            "word_count_target": 100,
            "notes": "Reinforce value. Soft CTA.",
        },
    ],
    "total_word_count_target": 1800,
    "faq_questions": [
        "How long should a daily job site report take to fill out?",
        "Do I need to keep daily reports after the job is done?",
    ],
    "images": [
        {
            "image_id": "cover",
            "image_type": "cover",
            "style": "graphic-art",
            "placement_after": "",
            "dalle_prompt": "A contractor on a job site reviewing a clipboard with a structured report form.",
            "alt_text": "contractor filling out a daily job site report on a tablet",
            "caption": "A daily report takes 5 minutes but can save hours in disputes.",
        },
        {
            "image_id": "body-1",
            "image_type": "over-the-shoulder",
            "style": "photo-real",
            "placement_after": "What to Include in Every Report",
            "dalle_prompt": "Over the shoulder view of a contractor filling in a structured report form on a tablet at a job site.",
            "alt_text": "job site report template on clipboard",
            "caption": "A structured template ensures nothing gets missed.",
        },
    ],
    "internal_links": [],
    "external_link": {
        "url": "https://www.osha.gov/recordkeeping",
        "anchor_text": "OSHA recordkeeping requirements",
        "placement_section": "Why Daily Job Site Reports Matter",
    },
    "fg4b_block_placement": "Why Daily Job Site Reports Matter",
    "competitor_gap_notes": "Most articles skip the liability protection angle.",
    "created_at": "2026-04-14T12:00:00Z",
}


@pytest.fixture(autouse=True)
def patch_drafts(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)


@pytest.fixture(autouse=True)
def patch_content_index(monkeypatch):
    monkeypatch.setattr(
        content_index,
        "load_content_index",
        lambda: {"posts": [], "topic_clusters": {}, "stats": {}},
    )


@patch("app.stages.research.ai_client.call")
def test_returns_valid_brief(mock_call):
    mock_call.return_value = json.dumps(_VALID_BRIEF)
    result = research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert isinstance(result, Brief)
    assert result.primary_keyword == "daily job site report"
    assert result.category == "Documentation & Record Keeping"


@patch("app.stages.research.ai_client.call")
def test_slug_is_enforced_from_parameter(mock_call):
    """Even if Claude returns a different slug, the pipeline slug must win."""
    tampered = dict(_VALID_BRIEF, slug="claude-made-this-up")
    mock_call.return_value = json.dumps(tampered)
    result = research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert result.slug == TEST_SLUG


@patch("app.stages.research.ai_client.call")
def test_created_at_is_set_by_code(mock_call):
    mock_call.return_value = json.dumps(_VALID_BRIEF)
    result = research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert result.created_at is not None


@patch("app.stages.research.ai_client.call")
def test_handles_json_code_fences(mock_call):
    mock_call.return_value = f"```json\n{json.dumps(_VALID_BRIEF)}\n```"
    result = research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert isinstance(result, Brief)


@patch("app.stages.research.ai_client.call")
def test_saves_checkpoint(mock_call):
    mock_call.return_value = json.dumps(_VALID_BRIEF)
    research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    loaded = checkpoint.load(TEST_SLUG, "01_brief", Brief)
    assert loaded is not None
    assert loaded.primary_keyword == "daily job site report"


@patch("app.stages.research.ai_client.call")
def test_content_index_passed_to_prompt(mock_call, monkeypatch):
    mock_call.return_value = json.dumps(_VALID_BRIEF)
    captured = {}

    original_load_prompt = research.load_prompt

    def spy_load_prompt(path, **vars):
        captured.update(vars)
        return original_load_prompt(path, **vars)

    monkeypatch.setattr(research, "load_prompt", spy_load_prompt)
    research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert "content_index_json" in captured
    assert "posts" in captured["content_index_json"]


@patch("app.stages.research.ai_client.call")
def test_raises_on_invalid_json(mock_call):
    mock_call.return_value = "not json"
    with pytest.raises(ValueError, match="invalid JSON"):
        research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)


@patch("app.stages.research.ai_client.call")
def test_raises_on_missing_required_field(mock_call):
    bad = {k: v for k, v in _VALID_BRIEF.items() if k != "primary_keyword"}
    mock_call.return_value = json.dumps(bad)
    with pytest.raises(ValueError, match="validation"):
        research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)


@patch("app.stages.research.ai_client.call")
def test_loads_fg4b_input_checkpoint_if_present(mock_call, tmp_path, monkeypatch):
    """Stage 1 should silently use Stage 0 checkpoint when it exists."""
    from datetime import timezone
    from app.models import FG4BInput

    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    fg4b = FG4BInput(
        raw_prose="raw",
        styled_block="styled",
        extracted_urls=[],
        user_specified_links=[],
        themes=["speed"],
        created_at=datetime.now(timezone.utc),
    )
    checkpoint.save(TEST_SLUG, "00_fg4b_input", fg4b)

    mock_call.return_value = json.dumps(_VALID_BRIEF)
    captured = {}
    original_load_prompt = research.load_prompt

    def spy(path, **vars):
        captured.update(vars)
        return original_load_prompt(path, **vars)

    monkeypatch.setattr(research, "load_prompt", spy)
    research.run(TEST_SLUG, TEST_TOPIC, TEST_TYPE)
    assert "styled" in captured.get("fg4b_input_json", "")
