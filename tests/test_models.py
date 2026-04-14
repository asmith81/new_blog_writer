"""Tests for all pipeline pydantic models — instantiation, JSON round-trip, required field validation."""
import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import (
    ArticleState,
    Brief,
    DraftVersion,
    FG4BInput,
    ImageBrief,
    ImageResult,
    ImagesOutput,
    InternalLink,
    KeywordPlacement,
    PublishResult,
    SectionBrief,
    UserSpecifiedLink,
)

NOW = datetime(2026, 4, 14, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fixtures / sample data
# ---------------------------------------------------------------------------

def make_fg4b_input() -> FG4BInput:
    return FG4BInput(
        raw_prose="We fix roofs fast and cheap.",
        styled_block="Our crew delivers fast, affordable roofing repairs.",
        extracted_urls=["https://fg4b.com/roofing"],
        user_specified_links=[
            UserSpecifiedLink(
                url="https://fg4b.com/roofing",
                context="main service page",
                anchor_suggestion="roofing repairs",
            )
        ],
        themes=["speed", "affordability"],
        created_at=NOW,
    )


def make_brief() -> Brief:
    return Brief(
        slug="how-to-fix-a-leaking-roof",
        topic="leaking roof repair",
        article_type="how-to",
        primary_keyword="how to fix a leaking roof",
        semantic_keywords=["roof leak repair", "stop roof leak"],
        lsi_keywords=["shingle replacement", "roof flashing"],
        search_intent="informational",
        category="roofing",
        keyword_placement=KeywordPlacement(
            meta_title="How to Fix a Leaking Roof | FG4B",
            meta_description="Step-by-step guide to fixing a leaking roof before water damage spreads.",
            h1_text="How to Fix a Leaking Roof",
            intro_keywords=["how to fix a leaking roof", "roof leak repair"],
            image_alt_map={"cover": "homeowner inspecting a leaking roof"},
        ),
        sections=[
            SectionBrief(
                heading="Why Roof Leaks Happen",
                level=2,
                assigned_keywords=["roof leak causes"],
                word_count_target=300,
                notes="Cover flashing, shingles, and improper sealing.",
            )
        ],
        total_word_count_target=1800,
        faq_questions=["How much does it cost to fix a leaking roof?"],
        images=[
            ImageBrief(
                image_id="cover",
                image_type="cover",
                style="photo-real",
                placement_after="",
                dalle_prompt="A homeowner on a ladder inspecting a damaged roof.",
                alt_text="homeowner inspecting a leaking roof",
                caption="Catching a leak early can save thousands in repairs.",
            )
        ],
        internal_links=[
            InternalLink(
                target_slug="roof-replacement-cost",
                target_title="Roof Replacement Cost Guide",
                anchor_text="roof replacement costs",
                placement_section="Why Roof Leaks Happen",
            )
        ],
        external_link={
            "url": "https://www.nrca.net",
            "anchor_text": "National Roofing Contractors Association",
            "placement_section": "Why Roof Leaks Happen",
        },
        fg4b_block_placement="Why Roof Leaks Happen",
        competitor_gap_notes="Competitors skip flashing details.",
        created_at=NOW,
    )


def make_article_state() -> ArticleState:
    return ArticleState(
        slug="how-to-fix-a-leaking-roof",
        article_type="how-to",
        stage_completed=2,
        draft_versions=[
            DraftVersion(
                version=1,
                filename="draft_v1.md",
                created_at=NOW,
                word_count=1823,
            )
        ],
        current_draft_path="drafts/how-to-fix-a-leaking-roof/article.md",
        created_at=NOW,
        updated_at=NOW,
    )


def make_images_output() -> ImagesOutput:
    return ImagesOutput(
        slug="how-to-fix-a-leaking-roof",
        images=[
            ImageResult(
                image_id="cover",
                local_path="drafts/how-to-fix-a-leaking-roof/images/cover/cover.png",
                cloudinary_url="https://res.cloudinary.com/fg4b/image/upload/blog/how-to-fix-a-leaking-roof/cover",
                alt_text="homeowner inspecting a leaking roof",
                caption="Catching a leak early can save thousands.",
                placed_in_article=True,
            )
        ],
        completed_at=NOW,
    )


def make_publish_result() -> PublishResult:
    return PublishResult(
        slug="how-to-fix-a-leaking-roof",
        destination_path="C:/Users/alden/dev/FG4B_Website/src/content/blog/how-to-fix-a-leaking-roof.mdx",
        archive_path="C:/Users/alden/dev/FG4B_Website/archive/how-to-fix-a-leaking-roof_20260414/",
        published_at=NOW,
    )


# ---------------------------------------------------------------------------
# Instantiation tests
# ---------------------------------------------------------------------------

def test_fg4b_input_instantiates():
    obj = make_fg4b_input()
    assert obj.raw_prose == "We fix roofs fast and cheap."
    assert len(obj.user_specified_links) == 1
    assert obj.user_specified_links[0].url == "https://fg4b.com/roofing"


def test_brief_instantiates():
    obj = make_brief()
    assert obj.slug == "how-to-fix-a-leaking-roof"
    assert obj.keyword_placement.h1_text == "How to Fix a Leaking Roof"
    assert len(obj.sections) == 1
    assert len(obj.images) == 1
    assert len(obj.internal_links) == 1


def test_article_state_instantiates():
    obj = make_article_state()
    assert obj.stage_completed == 2
    assert obj.draft_versions[0].word_count == 1823


def test_images_output_instantiates():
    obj = make_images_output()
    assert obj.images[0].placed_in_article is True


def test_publish_result_instantiates():
    obj = make_publish_result()
    assert obj.slug == "how-to-fix-a-leaking-roof"


# ---------------------------------------------------------------------------
# JSON round-trip tests
# ---------------------------------------------------------------------------

def _round_trip(obj):
    raw = obj.model_dump_json()
    data = json.loads(raw)
    return type(obj).model_validate(data)


def test_fg4b_input_round_trip():
    obj = make_fg4b_input()
    restored = _round_trip(obj)
    assert restored == obj


def test_brief_round_trip():
    obj = make_brief()
    restored = _round_trip(obj)
    assert restored == obj


def test_article_state_round_trip():
    obj = make_article_state()
    restored = _round_trip(obj)
    assert restored == obj


def test_images_output_round_trip():
    obj = make_images_output()
    restored = _round_trip(obj)
    assert restored == obj


def test_publish_result_round_trip():
    obj = make_publish_result()
    restored = _round_trip(obj)
    assert restored == obj


# ---------------------------------------------------------------------------
# Required field validation
# ---------------------------------------------------------------------------

def test_fg4b_input_missing_required_field():
    with pytest.raises(ValidationError):
        FG4BInput(
            styled_block="x",
            extracted_urls=[],
            user_specified_links=[],
            themes=[],
            created_at=NOW,
            # raw_prose omitted
        )


def test_brief_missing_slug():
    with pytest.raises(ValidationError):
        Brief(
            topic="x",
            article_type="how-to",
            primary_keyword="x",
            semantic_keywords=[],
            lsi_keywords=[],
            search_intent="informational",
            category="roofing",
            keyword_placement=make_brief().keyword_placement,
            sections=[],
            total_word_count_target=1800,
            faq_questions=[],
            images=[],
            internal_links=[],
            external_link={},
            fg4b_block_placement="",
            competitor_gap_notes="",
            created_at=NOW,
            # slug omitted
        )


def test_image_result_missing_cloudinary_url():
    with pytest.raises(ValidationError):
        ImageResult(
            image_id="cover",
            local_path="drafts/slug/cover.png",
            alt_text="alt",
            caption="cap",
            placed_in_article=False,
            # cloudinary_url omitted
        )


def test_publish_result_missing_destination():
    with pytest.raises(ValidationError):
        PublishResult(
            slug="some-slug",
            archive_path="some/path",
            published_at=NOW,
            # destination_path omitted
        )
