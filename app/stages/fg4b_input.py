"""Stage 0 — FG4B Input: clean user prose into brand voice and extract structure."""
import json
import logging
from datetime import datetime, timezone

from pydantic import ValidationError

from app.lib import ai_client, checkpoint
from app.lib.prompt_utils import load_prompt, strip_fences
from app.models import FG4BInput

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a content editor for FG4B. Return only valid JSON matching the schema exactly. "
    "No markdown, no explanation."
)


def run(slug: str, raw_prose: str) -> FG4BInput:
    """Clean raw user prose into FG4B brand voice and extract structured data.

    Saves checkpoint to drafts/{slug}/00_fg4b_input.json.
    Returns FG4BInput.
    """
    user_prompt = load_prompt("fg4b_input/stylize.txt", raw_prose=raw_prose)

    raw_response = ai_client.call(
        system_prompt=_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        max_tokens=ai_client.config["ai"]["max_tokens"]["fg4b_input"],
    )

    try:
        data = json.loads(strip_fences(raw_response))
    except json.JSONDecodeError as e:
        logger.error("Stage 0 JSON parse failed. Raw response: %s", raw_response[:500])
        raise ValueError(f"Stage 0: Claude returned invalid JSON — {e}") from e

    try:
        result = FG4BInput(
            raw_prose=raw_prose,
            created_at=datetime.now(timezone.utc),
            **data,
        )
    except ValidationError as e:
        logger.error("Stage 0 validation failed. Parsed data: %s", data)
        raise ValueError(f"Stage 0: Claude response failed validation — {e}") from e

    checkpoint.save(slug, "00_fg4b_input", result)
    logger.info("Stage 0 complete. slug=%s themes=%s", slug, result.themes)
    return result
