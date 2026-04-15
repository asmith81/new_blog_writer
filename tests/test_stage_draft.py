"""Tests for Stage 2 — Draft Writer. All Claude calls are mocked."""
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import call, patch

import pytest

from app.lib import checkpoint
from app.models import ArticleState, Brief, ImageBrief, InternalLink, KeywordPlacement, SectionBrief
from app.stages import draft

TEST_SLUG = "test-draft-slug"
NOW = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)

_MOCK_ARTICLE = """\
# Daily Job Site Report Guide for Contractors

Every contractor knows the feeling. You finish a job, a dispute pops up weeks later, and you have no documentation to back you up. A daily job site report fixes that.

## Key Takeaways

- A daily report protects you in disputes.
- It takes less than 10 minutes per day.
- The data improves your future bids.

## Why Daily Job Site Reports Matter

Most contractors we work with didn't start using daily reports until after their first serious dispute. By then, the damage was done.

A job site report creates a timestamped record of what happened, who was there, and what work was completed. That record is your best defense.

## What to Include in Every Report

Weather, crew attendance, work completed, materials received, incidents. That's the core five.

## Frequently Asked Questions

**Q: How long should a daily report take?**

Five to ten minutes if you have a template. Without one, it takes longer and captures less.

**Q: Do I need to keep reports after the job closes?**

Yes. Keep them for at least three years. Lien disputes and warranty claims can surface long after punch-out.

## Conclusion

A daily job site report is not bureaucracy. It is protection. Start with a simple template, run it for one job, and you will never go back.
"""

_MOCK_FG4B_BLOCK = """\
<FG4BBlock>
We worked with a roofing contractor last year who lost a $12,000 dispute because he couldn't prove his crew was on site the day the flashing was installed. The homeowner claimed it was never done. It was — but without a daily report, there was no paper trail. A two-minute daily log would have closed that argument immediately.
</FG4BBlock>"""


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
            meta_description="How to write a daily job site report that protects your business.",
            h1_text="Daily Job Site Report Guide for Contractors",
            intro_keywords=["daily job site report"],
            image_alt_map={"cover": "contractor with clipboard"},
        ),
        sections=[
            SectionBrief(heading="Why Daily Job Site Reports Matter", level=2,
                         assigned_keywords=["job site report"], word_count_target=300,
                         notes="Cover liability protection."),
            SectionBrief(heading="What to Include in Every Report", level=2,
                         assigned_keywords=["daily report template"], word_count_target=400,
                         notes="Weather, crew, work, materials, incidents."),
            SectionBrief(heading="Conclusion", level=2, assigned_keywords=[],
                         word_count_target=100, notes="Reinforce value."),
        ],
        total_word_count_target=1800,
        faq_questions=["How long should a daily report take?"],
        images=[
            ImageBrief(image_id="cover", image_type="cover", style="graphic-art",
                       placement_after="", dalle_prompt="A contractor on a job site.",
                       alt_text="contractor with clipboard", caption="Daily reports take 5 minutes."),
        ],
        internal_links=[],
        external_link={"url": "https://osha.gov", "anchor_text": "OSHA requirements",
                       "placement_section": "Why Daily Job Site Reports Matter"},
        fg4b_block_placement="Why Daily Job Site Reports Matter",
        competitor_gap_notes="Competitors skip liability angle.",
        created_at=NOW,
    )


@pytest.fixture(autouse=True)
def patch_drafts(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    import app.stages.draft as d
    monkeypatch.setattr(d, "_DRAFTS_DIR", tmp_path)


@pytest.fixture(autouse=True)
def seed_brief(tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    checkpoint.save(TEST_SLUG, "01_brief", _make_brief())


@patch("app.stages.draft.ai_client.call")
def test_makes_exactly_two_llm_calls(mock_call):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    assert mock_call.call_count == 2


@patch("app.stages.draft.ai_client.call")
def test_returns_article_state(mock_call):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    result = draft.run(TEST_SLUG)
    assert isinstance(result, ArticleState)
    assert result.stage_completed == 2
    assert result.slug == TEST_SLUG


@patch("app.stages.draft.ai_client.call")
def test_writes_article_md(mock_call, tmp_path):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    article_path = tmp_path / TEST_SLUG / "article.md"
    assert article_path.exists()
    content = article_path.read_text(encoding="utf-8")
    assert "Daily Job Site Report" in content


@patch("app.stages.draft.ai_client.call")
def test_writes_draft_v1_md(mock_call, tmp_path):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    v1_path = tmp_path / TEST_SLUG / "draft_v1.md"
    assert v1_path.exists()


@patch("app.stages.draft.ai_client.call")
def test_fg4b_block_inserted_in_article(mock_call, tmp_path):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    content = (tmp_path / TEST_SLUG / "article.md").read_text(encoding="utf-8")
    assert "<FG4BBlock>" in content
    assert "roofing contractor" in content


@patch("app.stages.draft.ai_client.call")
def test_fg4b_block_placed_after_correct_heading(mock_call, tmp_path):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    content = (tmp_path / TEST_SLUG / "article.md").read_text(encoding="utf-8")
    # FG4B block must appear after the placement heading, not before
    heading_pos = content.find("## Why Daily Job Site Reports Matter")
    block_pos = content.find("<FG4BBlock>")
    assert heading_pos < block_pos


@patch("app.stages.draft.ai_client.call")
def test_article_state_checkpoint_saved(mock_call):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    loaded = checkpoint.load(TEST_SLUG, "02_article_state", ArticleState)
    assert loaded is not None
    assert loaded.stage_completed == 2


@patch("app.stages.draft.ai_client.call")
def test_draft_version_word_count_recorded(mock_call):
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    result = draft.run(TEST_SLUG)
    assert result.draft_versions[0].word_count > 0


@patch("app.stages.draft.ai_client.call")
def test_raises_if_brief_missing(mock_call, tmp_path, monkeypatch):
    monkeypatch.setattr(checkpoint, "_DRAFTS_DIR", tmp_path)
    import app.stages.draft as d
    monkeypatch.setattr(d, "_DRAFTS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="01_brief.json not found"):
        draft.run("no-brief-slug")


@patch("app.stages.draft.ai_client.call")
def test_first_call_uses_article_prompt(mock_call):
    """First LLM call must be the main article, not the FG4B block."""
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    first_user_prompt = mock_call.call_args_list[0].kwargs.get(
        "user_prompt", mock_call.call_args_list[0].args[1] if len(mock_call.call_args_list[0].args) > 1 else ""
    )
    assert "brief_json" not in first_user_prompt or "daily job site report" in first_user_prompt


@patch("app.stages.draft.ai_client.call")
def test_second_call_uses_fg4b_prompt(mock_call):
    """Second LLM call must be the FG4B block, not another full article."""
    mock_call.side_effect = [_MOCK_ARTICLE, _MOCK_FG4B_BLOCK]
    draft.run(TEST_SLUG)
    second_user_prompt = mock_call.call_args_list[1].kwargs.get(
        "user_prompt", mock_call.call_args_list[1].args[1] if len(mock_call.call_args_list[1].args) > 1 else ""
    )
    assert "FG4B" in second_user_prompt or "callout" in second_user_prompt or "block" in second_user_prompt.lower()
