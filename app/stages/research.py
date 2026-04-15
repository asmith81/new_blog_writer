"""Stage 1 — Research: keyword strategy brief."""
import json
import logging
from datetime import datetime, timezone

from pydantic import ValidationError

from app.lib import ai_client, checkpoint, content_index
from app.lib.prompt_utils import load_prompt, strip_fences
from app.models import Brief, FG4BInput

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an SEO content strategist for home service contractor businesses. "
    "Return only valid JSON matching the schema exactly. No markdown, no explanation."
)


def run(slug: str, topic: str, article_type: str) -> Brief:
    """Generate a full keyword strategy brief for the article.

    Loads Stage 0 checkpoint (00_fg4b_input.json) if it exists — optional.
    Saves checkpoint to drafts/{slug}/01_brief.json.
    Returns Brief.
    """
    # Load optional Stage 0 output
    fg4b_input_obj: FG4BInput | None = checkpoint.load(slug, "00_fg4b_input", FG4BInput)
    fg4b_input_json = (
        fg4b_input_obj.model_dump_json(indent=2) if fg4b_input_obj else "none"
    )

    # Load internal link candidates
    try:
        index = content_index.load_content_index()
        content_index_json = json.dumps(index, indent=2)
    except RuntimeError as e:
        logger.warning("Could not load content index: %s — proceeding without it.", e)
        content_index_json = '{"posts": []}'

    user_prompt = load_prompt(
        "research/brief.txt",
        topic=topic,
        article_type=article_type,
        fg4b_input_json=fg4b_input_json,
        content_index_json=content_index_json,
    )

    raw_response = ai_client.call(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=ai_client.config["ai"]["max_tokens"]["research"],
    )

    try:
        data = json.loads(strip_fences(raw_response))
    except json.JSONDecodeError as e:
        logger.error("Stage 1 JSON parse failed. Raw response: %s", raw_response[:500])
        raise ValueError(f"Stage 1: Claude returned invalid JSON — {e}") from e

    # Enforce slug and created_at from pipeline — never trust Claude for these
    data["slug"] = slug
    data["created_at"] = datetime.now(timezone.utc).isoformat()

    try:
        result = Brief.model_validate(data)
    except ValidationError as e:
        logger.error("Stage 1 validation failed. Parsed data keys: %s", list(data.keys()))
        raise ValueError(f"Stage 1: Claude response failed validation — {e}") from e

    checkpoint.save(slug, "01_brief", result)
    logger.info(
        "Stage 1 complete. slug=%s primary_kw=%s sections=%d",
        slug,
        result.primary_keyword,
        len(result.sections),
    )
    return result
