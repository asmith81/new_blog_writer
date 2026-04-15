"""Cloudinary image upload wrapper."""
import io
import logging

import cloudinary
import cloudinary.uploader

from app.lib.config import settings

logger = logging.getLogger(__name__)


def _configure():
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


def upload(image_bytes: bytes, public_id: str) -> str:
    """Upload image bytes to Cloudinary and return the secure URL.

    Args:
        image_bytes: Raw image bytes (PNG or JPEG).
        public_id: Cloudinary public_id, e.g. 'blog/my-slug/cover'.

    Returns:
        Secure Cloudinary URL string.
    """
    _configure()
    logger.info("Uploading image to Cloudinary public_id=%s", public_id)
    result = cloudinary.uploader.upload(
        io.BytesIO(image_bytes),
        public_id=public_id,
        resource_type="image",
        overwrite=True,
    )
    url = result["secure_url"]
    logger.debug("Cloudinary upload complete: %s", url)
    return url
