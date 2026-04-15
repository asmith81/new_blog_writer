"""Stage 2 — Draft: write article markdown + FG4B block (two separate LLM calls)."""
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from app.lib import ai_client, checkpoint
from app.lib.config import config
from app.lib.prompt_utils import load_prompt
from app.models import ArticleState, Brief, DraftVersion

logger = logging.getLogger(__name__)

_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])


def _word_count(text: str) -> int:
    return len(text.split())


def _get_section_context(article_text: str, heading: str, max_chars: int = 600) -> str:
    """Return up to max_chars of text from the section starting at heading."""
    pattern = re.compile(rf"^##\s+{re.escape(heading)}", re.MULTILINE)
    match = pattern.search(article_text)
    if not match:
        return article_text[:max_chars]
    start = match.start()
    return article_text[start : start + max_chars]


def _insert_fg4b_block(article_text: str, heading: str, block: str) -> str:
    """Insert the FG4B block at the end of the named H2 section (before the next ## heading)."""
    pattern = re.compile(rf"(^##\s+{re.escape(heading)}.*?)(?=\n##\s|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(article_text)
    if not match:
        logger.warning("FG4B block placement heading not found: %r — appending to end.", heading)
        return article_text.rstrip() + f"\n\n{block}\n"
    insertion_point = match.end()
    return article_text[:insertion_point].rstrip() + f"\n\n{block}\n" + article_text[insertion_point:]


def run(slug: str) -> ArticleState:
    """Write the full article draft and FG4B block.

    Two LLM calls — main article then FG4B block — per project rules.
    Saves article.md, draft_v1.md, and ArticleState checkpoint.
    Returns ArticleState.
    """
    # Load brief
    brief: Brief | None = checkpoint.load(slug, "01_brief", Brief)
    if brief is None:
        raise FileNotFoundError(
            f"01_brief.json not found for slug={slug!r}. Run Stage 1 (research) first."
        )

    system_prompt = load_prompt("draft/system.txt")

    # --- Call 1: Main article draft ---
    article_user_prompt = load_prompt(
        "draft/article.txt",
        brief_json=brief.model_dump_json(indent=2),
    )
    logger.info("Stage 2 Call 1: generating main article draft for slug=%s", slug)
    article_text = ai_client.call(
        system_prompt=system_prompt,
        user_prompt=article_user_prompt,
        max_tokens=config["ai"]["max_tokens"]["draft"],
    )

    # --- Call 2: FG4B block ---
    placement_context = _get_section_context(article_text, brief.fg4b_block_placement)
    fg4b_user_prompt = load_prompt(
        "draft/fg4b_block.txt",
        topic=brief.topic,
        placement_context=placement_context,
    )
    logger.info("Stage 2 Call 2: generating FG4B block for slug=%s", slug)
    fg4b_block = ai_client.call(
        system_prompt=system_prompt,
        user_prompt=fg4b_user_prompt,
        max_tokens=config["ai"]["max_tokens"]["fg4b_block"],
    ).strip()

    # Insert FG4B block into article
    final_article = _insert_fg4b_block(article_text, brief.fg4b_block_placement, fg4b_block)

    # Write article files
    slug_dir = _DRAFTS_DIR / slug
    slug_dir.mkdir(parents=True, exist_ok=True)

    article_path = slug_dir / "article.md"
    draft_v1_path = slug_dir / "draft_v1.md"
    article_path.write_text(final_article, encoding="utf-8")
    draft_v1_path.write_text(final_article, encoding="utf-8")

    now = datetime.now(timezone.utc)
    wc = _word_count(final_article)
    logger.info("Stage 2 complete. slug=%s word_count=%d", slug, wc)

    state = ArticleState(
        slug=slug,
        article_type=brief.article_type,
        stage_completed=2,
        draft_versions=[
            DraftVersion(version=1, filename="draft_v1.md", created_at=now, word_count=wc)
        ],
        current_draft_path=str(article_path),
        created_at=now,
        updated_at=now,
    )
    checkpoint.save(slug, "02_article_state", state)
    return state
