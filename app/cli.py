"""Typer CLI entry point for new_blog_writer."""
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import typer
from rich.console import Console
from rich.table import Table
from slugify import slugify

from app.lib import cloudinary_client
from app.lib.config import config, settings
from app.pipeline import Pipeline

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="blog",
    help="AI-powered blog content pipeline for FG4B_Website.",
    no_args_is_help=True,
)
console = Console()

_DRAFTS_DIR = Path(config["paths"]["drafts_dir"])

_STAGE_NAMES = {
    0: "fg4b-input",
    1: "research",
    2: "draft",
    3: "images",
    4: "publish",
}


def _completed_stages(slug: str) -> list[int]:
    """Return list of stage numbers whose checkpoint files exist."""
    slug_dir = _DRAFTS_DIR / slug
    checkpoints = {
        0: "00_fg4b_input.json",
        1: "01_brief.json",
        2: "article.md",
        3: "03_images.json",
        4: "04_publish.json",
    }
    return [n for n, fname in checkpoints.items() if (slug_dir / fname).exists()]


def _insert_image_after_heading(article_text: str, heading: str, component: str) -> str:
    """Insert a BlogImage component immediately after a named H2 heading."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", article_text, re.MULTILINE)
    if not match:
        return article_text
    pos = match.end()
    return article_text[:pos] + "\n\n" + component + "\n" + article_text[pos:]


# ---------------------------------------------------------------------------
# interview helper
# ---------------------------------------------------------------------------

def run_interview():
    """Collect topic, article type, slug, and optional prose interactively."""
    topic = typer.prompt("Main keyword / topic")
    article_type = typer.prompt(
        "Article type",
        default="how-to",
        type=click.Choice(["how-to", "guide", "list", "comparison"]),
    )
    suggested_slug = slugify(topic)
    raw_slug = typer.prompt("Slug", default=suggested_slug)
    slug = slugify(raw_slug)
    add_prose = typer.confirm("Add local experience text?", default=False)
    raw_prose = ""
    if add_prose:
        console.print("[dim]Paste text — blank line to finish:[/dim]")
        lines = []
        for line in sys.stdin:
            stripped = line.rstrip("\n")
            if stripped == "":
                break
            lines.append(stripped)
        raw_prose = "\n".join(lines)
    return slug, topic, article_type, raw_prose


# ---------------------------------------------------------------------------
# write
# ---------------------------------------------------------------------------

@app.command()
def write(
    auto: bool = typer.Option(False, "--auto", help="Run all stages without pausing"),
):
    """Run the full pipeline (default: pause after Stage 1 for review)."""
    slug, topic, article_type, raw_prose = run_interview()
    mode = "auto" if auto else "default"
    console.print(f"[bold]Starting pipeline[/bold] slug=[cyan]{slug}[/cyan] type=[cyan]{article_type}[/cyan] mode=[cyan]{mode}[/cyan]")
    Pipeline(slug=slug, mode=mode).run_from(
        0 if raw_prose else 1,
        raw_prose=raw_prose,
        topic=topic,
        article_type=article_type,
    )


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------

@app.command()
def research():
    """Run Stage 1: keyword strategy brief."""
    slug, topic, article_type, raw_prose = run_interview()
    p = Pipeline(slug=slug, mode="manual")
    if raw_prose:
        p.run_stage(0, raw_prose=raw_prose)
    p.run_stage(1, topic=topic, article_type=article_type)


# ---------------------------------------------------------------------------
# draft
# ---------------------------------------------------------------------------

@app.command()
def draft(
    slug: str = typer.Argument(..., help="Draft slug"),
):
    """Run Stage 2: write article draft."""
    Pipeline(slug=slug, mode="manual").run_stage(2)


# ---------------------------------------------------------------------------
# images
# ---------------------------------------------------------------------------

@app.command()
def images(
    slug: str = typer.Argument(..., help="Draft slug"),
):
    """Run Stage 3: generate and upload images."""
    Pipeline(slug=slug, mode="manual").run_stage(3)


# ---------------------------------------------------------------------------
# publish
# ---------------------------------------------------------------------------

@app.command()
def publish(
    slug: str = typer.Argument(..., help="Draft slug"),
):
    """Run Stage 4: assemble MDX and deploy to FG4B_Website."""
    Pipeline(slug=slug, mode="manual").run_stage(4)


# ---------------------------------------------------------------------------
# preview
# ---------------------------------------------------------------------------

@app.command()
def preview(
    slug: str = typer.Argument(..., help="Draft slug"),
):
    """Open the Astro dev server for a published article."""
    if not settings.fg4b_website_path:
        console.print("[red][FAIL] FG4B_WEBSITE_PATH is not set in .env[/red]")
        raise typer.Exit(1)

    mdx_path = Path(settings.fg4b_website_path) / "src" / "content" / "blog" / f"{slug}.mdx"
    if not mdx_path.exists():
        console.print(
            f"[red][FAIL] {slug}.mdx not found — run /publish first.[/red]"
        )
        raise typer.Exit(1)

    url = f"http://localhost:4321/blog/{slug}"
    console.print(f"[bold]Starting Astro dev server...[/bold]")
    console.print(f"[cyan]Preview URL:[/cyan] {url}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")

    subprocess.run("npm run dev", cwd=settings.fg4b_website_path, shell=True)


# ---------------------------------------------------------------------------
# add-image
# ---------------------------------------------------------------------------

@app.command(name="add-image")
def add_image(
    slug: str = typer.Argument(..., help="Draft slug"),
    image_path: Path = typer.Argument(..., help="Local path to image file"),
    after: str = typer.Option(..., "--after", help="Heading text to insert image after"),
):
    """Upload a local image to Cloudinary and insert it into the article."""
    if not image_path.exists():
        console.print(f"[red][FAIL] Image not found: {image_path}[/red]")
        raise typer.Exit(1)

    article_path = _DRAFTS_DIR / slug / "article.md"
    if not article_path.exists():
        console.print(f"[red][FAIL] article.md not found for slug={slug!r} — run /draft first.[/red]")
        raise typer.Exit(1)

    image_id = image_path.stem
    public_id = f"blog/{slug}/{image_id}"

    console.print(f"Uploading [cyan]{image_path.name}[/cyan] to Cloudinary...")
    image_bytes = image_path.read_bytes()
    url = cloudinary_client.upload(image_bytes, public_id=public_id)
    console.print(f"[green][OK] Uploaded:[/green] {url}")

    component = f'<BlogImage src="{url}" alt="{image_id}" caption="" />'
    article_text = article_path.read_text(encoding="utf-8")
    updated = _insert_image_after_heading(article_text, after, component)

    if updated == article_text:
        console.print(f"[yellow]Warning: heading {after!r} not found in article — image not inserted.[/yellow]")
    else:
        article_path.write_text(updated, encoding="utf-8")
        console.print(f"[green][OK] BlogImage inserted after:[/green] {after!r}")

    console.print("[dim]Run /publish to update the live MDX file.[/dim]")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@app.command(name="list")
def list_drafts():
    """List all slugs in the drafts directory."""
    if not _DRAFTS_DIR.exists():
        console.print("[dim]No drafts yet.[/dim]")
        return
    slugs = sorted(p.name for p in _DRAFTS_DIR.iterdir() if p.is_dir())
    if not slugs:
        console.print("[dim]No drafts yet.[/dim]")
        return
    table = Table(title="Drafts", show_header=True)
    table.add_column("Slug", style="cyan")
    table.add_column("Stages done")
    for s in slugs:
        done = _completed_stages(s)
        stage_str = ", ".join(str(n) for n in done) if done else "--"
        table.add_row(s, stage_str)
    console.print(table)


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status(
    slug: str = typer.Argument(..., help="Draft slug"),
):
    """Show which pipeline stages are complete for a draft."""
    done = set(_completed_stages(slug))
    table = Table(title=f"Status: {slug}", show_header=True)
    table.add_column("Stage")
    table.add_column("Name")
    table.add_column("Done")
    for n, name in _STAGE_NAMES.items():
        table.add_row(str(n), name, "[green][OK][/green]" if n in done else "[dim]--[/dim]")
    console.print(table)


if __name__ == "__main__":
    app()
