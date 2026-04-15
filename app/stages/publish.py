"""Stage 4 — Publish: assemble MDX and deploy to FG4B_Website."""
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from app.lib import checkpoint
from app.lib.config import config, settings
from app.models import Brief, ImagesOutput, PublishResult

logger = logging.getLogger(__name__)

_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])

_IMPORT_FG4B = "import FG4BBlock from '../../components/FG4BBlock.astro';"
_IMPORT_BLOG_IMAGE = "import BlogImage from '../../components/BlogImage.astro';"


def _build_frontmatter(brief: Brief, images_output: ImagesOutput | None) -> str:
    data: dict = {
        "title": brief.keyword_placement.meta_title,
        "description": brief.keyword_placement.meta_description,
        "pubDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "category": brief.category,
    }
    if images_output:
        cover = next((r for r in images_output.images if r.image_id == "cover"), None)
        if cover:
            data["heroImage"] = cover.cloudinary_url

    return "---\n" + yaml.dump(data, allow_unicode=True, default_flow_style=False).rstrip() + "\n---"


def _build_imports(article_body: str) -> str:
    lines = []
    if "<FG4BBlock" in article_body:
        lines.append(_IMPORT_FG4B)
    if "<BlogImage" in article_body:
        lines.append(_IMPORT_BLOG_IMAGE)
    return "\n".join(lines)


def run(slug: str) -> PublishResult:
    """Assemble frontmatter + imports + article body and write to FG4B_Website.

    - 01_brief.json: required
    - article.md: required
    - 03_images.json: optional — heroImage omitted if missing
    - Saves 04_publish.json checkpoint.
    - Returns PublishResult.
    """
    if not settings.fg4b_website_path:
        raise RuntimeError("FG4B_WEBSITE_PATH is not set in .env")

    fg4b_root = Path(settings.fg4b_website_path)

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

    images_output: ImagesOutput | None = checkpoint.load(slug, "03_images", ImagesOutput)

    article_body = article_path.read_text(encoding="utf-8")

    # Assemble MDX
    frontmatter = _build_frontmatter(brief, images_output)
    imports = _build_imports(article_body)

    parts = [frontmatter, ""]
    if imports:
        parts += [imports, ""]
    parts.append(article_body.strip())
    mdx_content = "\n".join(parts) + "\n"

    # Write to FG4B_Website
    dest_dir = fg4b_root / "src" / "content" / "blog"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{slug}.mdx"
    dest_path.write_text(mdx_content, encoding="utf-8")
    logger.info("Stage 4: wrote %s", dest_path)

    # Archive draft
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_path = fg4b_root / "archive" / f"{slug}_{timestamp}"
    shutil.copytree(str(_DRAFTS_DIR / slug), str(archive_path))
    logger.info("Stage 4: archived to %s", archive_path)

    result = PublishResult(
        slug=slug,
        destination_path=str(dest_path),
        archive_path=str(archive_path),
        published_at=datetime.now(timezone.utc),
    )
    checkpoint.save(slug, "04_publish", result)
    logger.info("Stage 4 complete. slug=%s dest=%s", slug, dest_path)
    return result
