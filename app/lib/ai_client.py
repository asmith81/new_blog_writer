"""Claude API wrapper."""
import logging

import anthropic

from app.lib.config import config, settings

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = config["ai"]["content_model"]
_DEFAULT_MAX_TOKENS = 4000


def call(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    model: str | None = None,
) -> str:
    """Call Claude and return the response text.

    Logs the first 300 chars of the raw response at DEBUG level before returning,
    so parse failures always have diagnostic context.
    """
    resolved_model = model or _DEFAULT_MODEL
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=resolved_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text
    logger.debug("LLM raw response (first 300 chars): %s", raw[:300])
    return raw
