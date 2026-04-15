"""DALL-E 3 image generation wrapper."""
import logging

import httpx
import openai

from app.lib.config import config, settings

logger = logging.getLogger(__name__)

_IMAGE_MODEL = config["ai"]["image_model"]
_COVER_SIZE = config["images"]["cover_size"]
_BODY_SIZE = config["images"]["body_size"]


def _size_for_image_id(image_id: str) -> str:
    """Return the DALL-E size string for a given image_id."""
    return _COVER_SIZE if image_id == "cover" else _BODY_SIZE


def generate(prompt: str, image_id: str = "body") -> bytes:
    """Generate an image with DALL-E 3 and return the PNG bytes.

    Args:
        prompt: DALL-E 3 image prompt.
        image_id: 'cover' for wide format (1792x1024), anything else for square (1024x1024).

    Returns:
        Raw PNG bytes.
    """
    size = _size_for_image_id(image_id)
    client = openai.OpenAI(api_key=settings.openai_api_key)

    logger.info("Generating image image_id=%s size=%s", image_id, size)
    response = client.images.generate(
        model=_IMAGE_MODEL,
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    logger.debug("DALL-E returned URL: %s", image_url)

    # Download image bytes
    img_response = httpx.get(image_url, follow_redirects=True, timeout=30)
    img_response.raise_for_status()
    return img_response.content
