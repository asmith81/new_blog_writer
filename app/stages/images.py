"""Stage 3 — Images: DALL-E 3 generation + Cloudinary upload + BlogImage insertion."""
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from app.lib import checkpoint, cloudinary_client, image_client
from app.lib.config import config
from app.models import Brief, ImageResult, ImagesOutput

logger = logging.getLogger(__name__)

_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])


def _blog_image_component(url: str, alt: str, caption: str) -> str:
    return f'<BlogImage src="{url}" alt="{alt}" caption="{caption}" />'


def _insert_after_heading(article_text: str, heading: str, component: str) -> str:
    """Insert component immediately after a heading line.

    For cover (heading == ""): insert after the H1 line.
    For body images: insert after the matching ## heading line.
    """
    if not heading:
        # Cover: insert after the first H1 line
        match = re.search(r"^#\s+.+$", article_text, re.MULTILINE)
        if not match:
            logger.warning("No H1 found — prepending cover image.")
            return component + "\n\n" + article_text
        pos = match.end()
    else:
        match = re.search(rf"^##\s+{re.escape(heading)}\s*$", article_text, re.MULTILINE)
        if not match:
            logger.warning("Heading %r not found for image insertion — skipping.", heading)
            return article_text
        pos = match.end()

    return article_text[:pos] + "\n\n" + component + "\n" + article_text[pos:]


def run(slug: str) -> ImagesOutput:
    """Generate images with DALL-E 3, upload to Cloudinary, insert BlogImage components.

    Saves 03_images.json checkpoint.
    Returns ImagesOutput.
    """
    brief: Brief | None = checkpoint.load(slug, "01_brief", Brief)
    if brief is None:
        raise FileNotFoundError(
            f"01_brief.json not found for slug={slug!r}. Run Stage 1 (research) first."
        )

    article_path = _DRAFTS_DIR / slug / "article.md"
    if not article_path.exists():
        raise FileNotFoundError(
            f"article.md not found for slug={slug!r}. Run Stage 2 (draft) first."
        )

    article_text = article_path.read_text(encoding="utf-8")
    results: list[ImageResult] = []

    for img_brief in brief.images:
        image_id = img_brief.image_id
        logger.info("Processing image image_id=%s slug=%s", image_id, slug)

        # Generate
        png_bytes = image_client.generate(img_brief.dalle_prompt, image_id=image_id)

        # Save locally
        img_dir = _DRAFTS_DIR / slug / "images" / image_id
        img_dir.mkdir(parents=True, exist_ok=True)
        local_path = img_dir / f"{image_id}.png"
        local_path.write_bytes(png_bytes)

        # Upload to Cloudinary
        public_id = f"blog/{slug}/{image_id}"
        cloudinary_url = cloudinary_client.upload(png_bytes, public_id=public_id)

        # Insert BlogImage into article
        component = _blog_image_component(cloudinary_url, img_brief.alt_text, img_brief.caption)
        article_text = _insert_after_heading(article_text, img_brief.placement_after, component)

        results.append(ImageResult(
            image_id=image_id,
            local_path=str(local_path),
            cloudinary_url=cloudinary_url,
            alt_text=img_brief.alt_text,
            caption=img_brief.caption,
            placed_in_article=True,
        ))

    # Write updated article
    article_path.write_text(article_text, encoding="utf-8")

    output = ImagesOutput(
        slug=slug,
        images=results,
        completed_at=datetime.now(timezone.utc),
    )
    checkpoint.save(slug, "03_images", output)
    logger.info("Stage 3 complete. slug=%s images=%d", slug, len(results))
    return output
