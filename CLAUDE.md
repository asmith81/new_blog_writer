# CLAUDE.md

## identity
- Language: Python 3.12+
- Env: always venv, never system Python
- OS: Windows + Git Bash — use forward slashes always
- Secrets: always .env + pydantic-settings, never hardcoded
- Editor: Cursor + Claude Code

## project overview
- Name: new_blog_writer
- Description: AI-powered blog content pipeline producing publish-ready Astro MDX files for FG4B_Website (fg4b.com). Replaces the old Streamlit-based system.
- Primary goal: Internal tool
- Key constraints:
  - Outputs to FG4B_Website/src/content/blog/ as .mdx files
  - Must read FG4B_Website/data/content_index.json for internal link strategy
  - Images hosted on Cloudinary — naming: blog/{slug}/cover, blog/{slug}/body-N
  - Astro frontmatter: title, description, pubDate (required); heroImage, category (optional)
  - All prompt text lives in prompts/ — never embedded in Python source
  - Two separate LLM calls minimum: extraction/structure then generation — never combined
  - FG4B block is a separate LLM call from the main draft

## architecture
- Stack: Python 3.12, Typer CLI, Anthropic Claude (content), OpenAI DALL-E 3 (images), Cloudinary (hosting), pydantic, pydantic-settings, python-dotenv, rich, watchdog, python-slugify, pyyaml
- Directory map: see docs/plans/phase1-scaffold.md
- Key modules:
  - app/cli.py — Typer entry point, all commands
  - app/pipeline.py — orchestrator, handles 3 modes
  - app/stages/fg4b_input.py — Stage 0: clean user prose
  - app/stages/research.py — Stage 1: KW strategy brief
  - app/stages/draft.py — Stage 2: article writing
  - app/stages/images.py — Stage 3: DALL-E generate + Cloudinary upload
  - app/stages/publish.py — Stage 4: assemble MDX + deploy to FG4B_Website
  - app/lib/ai_client.py — Claude API wrapper
  - app/lib/image_client.py — DALL-E wrapper (no infographic)
  - app/lib/cloudinary_client.py — upload + URL
  - app/lib/checkpoint.py — save/load JSON checkpoints
  - app/lib/content_index.py — read FG4B content_index.json
  - app/lib/config.py — pydantic-settings
  - prompts/ — all LLM prompt text as .txt files

## pipeline stages

| Stage | Name | Input | Output |
|-------|------|-------|--------|
| 0 | fg4b-input (optional) | free-form user prose | 00_fg4b_input.json |
| 1 | research | topic + type + stage 0 | 01_brief.json |
| 2 | draft | 01_brief.json | article.md + draft_v1.md |
| 3 | images | brief + article | 03_images.json + article.md updated |
| 4 | publish | article.md | FG4B_Website/src/content/blog/{slug}.mdx |

## three operating modes

| Mode | Flag | Behavior |
|------|------|----------|
| Full auto | --auto | Runs stages 0-4 without pausing |
| Default | (none) | Pauses after Stage 1, shows brief, waits for approval |
| Manual | stage commands | Each stage run independently |

## data model summary (pydantic)

- FG4BInput — Stage 0 output: styled prose, extracted URLs, themes
- Brief — Stage 1 output: full KW strategy, section hierarchy with word targets, image plan, link map
- SectionBrief — per-section: heading, level, assigned KWs, word count target
- ImageBrief — per-image: type, style, placement, prompt, alt text, caption
- InternalLink — target slug, anchor text, placement hint
- ArticleState — current draft path, version list, stage completed
- ImageResult — Stage 3 output per image: local path, Cloudinary URL, placed flag
- PublishResult — Stage 4 output: destination path, archive path, slug

## FG4B_Website dependencies
- FG4B_Website/data/content_index.json — read for internal link candidates
- FG4B_Website/src/content/blog/ — publish destination
- FG4B_Website/src/components/FG4BBlock.astro — FG4B callout block
- FG4B_Website/src/components/BlogImage.astro — image with hidden caption
- FG4B_Website archive/ — draft archive on publish
- FG4B_WEBSITE_PATH env var — absolute path to FG4B_Website repo

## roadmap pointer
- Roadmap: docs/roadmap.md
- Active plan: docs/plans/phase1-scaffold.md
- Current step: Step 1 — Environment + Config

## process rules
- Plan before coding — agree on approach before writing any code
- Write test for each stage immediately after building it — do not move on until it passes
- Run tests before marking any task complete
- Flag scope increases before acting on them
- Never mark a task complete without running the relevant test or showing the output
- Never combine LLM extraction and generation into one prompt call
- All prompt text in prompts/ directory, never in Python source
- Always load_dotenv(".env") with explicit path

## anti-patterns
- Never refactor, rename, or reorganize code outside the current task scope
- Never add dependencies without explicit approval
- Never assume a fix worked — show the output before declaring done
- Never embed prompt text in Python source files
- Never hardcode model names, slugs, or config values in business logic
- Never call load_dotenv() without an explicit path
- Never combine FG4B block generation with the main draft call — separate LLM calls

## file hygiene
- All stages in app/stages/
- All lib utilities in app/lib/
- All prompt text in prompts/{stage}/
- All docs in docs/
- Forward slashes in all paths when running in Git Bash
- Checkpoint files: 00_ through 04_ prefix in drafts/{slug}/

## git discipline
[populate from lessons as patterns emerge]

## known gotchas
[populate during project]

## local slash commands
Located in .claude/commands/ — project-local only.
- /write — full pipeline (default mode or --auto)
- /research — Stage 1 only
- /draft — Stage 2 only
- /images — Stage 3 only
- /publish — Stage 4 only
- /preview — copy to FG4B_Website + open Astro dev server with file watcher
- /add-image — upload local image to Cloudinary and insert into article
