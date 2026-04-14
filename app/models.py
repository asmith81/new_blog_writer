from datetime import datetime
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Stage 0 — FG4BInput
# ---------------------------------------------------------------------------

class UserSpecifiedLink(BaseModel):
    url: str
    context: str
    anchor_suggestion: str


class FG4BInput(BaseModel):
    raw_prose: str
    styled_block: str
    extracted_urls: list[str]
    user_specified_links: list[UserSpecifiedLink]
    themes: list[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Stage 1 — Brief
# ---------------------------------------------------------------------------

class KeywordPlacement(BaseModel):
    meta_title: str
    meta_description: str
    h1_text: str
    intro_keywords: list[str]
    image_alt_map: dict[str, str]


class SectionBrief(BaseModel):
    heading: str
    level: int
    assigned_keywords: list[str]
    word_count_target: int
    notes: str


class ImageBrief(BaseModel):
    image_id: str
    image_type: str
    style: str
    placement_after: str
    dalle_prompt: str
    alt_text: str
    caption: str


class InternalLink(BaseModel):
    target_slug: str
    target_title: str
    anchor_text: str
    placement_section: str


class Brief(BaseModel):
    slug: str
    topic: str
    article_type: str
    primary_keyword: str
    semantic_keywords: list[str]
    lsi_keywords: list[str]
    search_intent: str
    category: str
    keyword_placement: KeywordPlacement
    sections: list[SectionBrief]
    total_word_count_target: int
    faq_questions: list[str]
    images: list[ImageBrief]
    internal_links: list[InternalLink]
    external_link: dict
    fg4b_block_placement: str
    competitor_gap_notes: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Stage 2 — ArticleState
# ---------------------------------------------------------------------------

class DraftVersion(BaseModel):
    version: int
    filename: str
    created_at: datetime
    word_count: int


class ArticleState(BaseModel):
    slug: str
    article_type: str
    stage_completed: int
    draft_versions: list[DraftVersion]
    current_draft_path: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Stage 3 — ImagesOutput
# ---------------------------------------------------------------------------

class ImageResult(BaseModel):
    image_id: str
    local_path: str
    cloudinary_url: str
    alt_text: str
    caption: str
    placed_in_article: bool


class ImagesOutput(BaseModel):
    slug: str
    images: list[ImageResult]
    completed_at: datetime


# ---------------------------------------------------------------------------
# Stage 4 — PublishResult
# ---------------------------------------------------------------------------

class PublishResult(BaseModel):
    slug: str
    destination_path: str
    archive_path: str
    published_at: datetime
