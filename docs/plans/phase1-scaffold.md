# Phase 1 — Scaffold

**Status:** Active
**Goal:** Project structure, all data models, skeleton CLI with checkpoint plumbing, MDX components in FG4B_Website, prompt stubs, and reference docs. No real API calls. Pipeline runs end-to-end with stubs.
**Last updated:** 2026-04-14

---

## Stack

| Component | Choice | Rationale |
|---|---|---|
| Language | Python 3.12 | Per global rules |
| CLI | Typer + rich | Clean command interface, auto --help |
| Content AI | Claude (Anthropic) | Already integrated in FG4B stack |
| Image AI | OpenAI DALL-E 3 | Existing integration pattern |
| Image hosting | Cloudinary | Existing account + naming convention |
| Config | pydantic-settings + config.yaml | Model names/prompts outside code |
| File watching | watchdog | Preview auto-reload |
| Slug gen | python-slugify | Consistent draft folder names |
| Validation | pydantic v2 | All checkpoint files validated at boundary |

---

## Local Development Setup

```bash
# 1. Verify Python version
python --version   # expect 3.12+

# 2. Activate venv (must already exist from /newproject)
source venv/Scripts/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy .env
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, OPENAI_API_KEY, CLOUDINARY_*, FG4B_WEBSITE_PATH

# 5. Verify imports
python -c "from app.cli import app; print('OK')"

# 6. Verify CLI wires
python -m app.cli --help
```

---

## Project Structure (target for Phase 1)

```
new_blog_writer/
├── app/
│   ├── __init__.py
│   ├── cli.py                     # Typer app, all commands registered
│   ├── pipeline.py                # Orchestrator, 3 modes
│   ├── stages/
│   │   ├── __init__.py
│   │   ├── fg4b_input.py          # Stage 0: clean user prose
│   │   ├── research.py            # Stage 1: KW strategy brief
│   │   ├── draft.py               # Stage 2: article writing
│   │   ├── images.py              # Stage 3: DALL-E + Cloudinary
│   │   └── publish.py             # Stage 4: assemble MDX + deploy
│   └── lib/
│       ├── __init__.py
│       ├── ai_client.py           # Claude API wrapper
│       ├── image_client.py        # DALL-E wrapper (no infographic type)
│       ├── cloudinary_client.py   # Upload + public URL
│       ├── checkpoint.py          # Save/load JSON with pydantic validation
│       ├── content_index.py       # Read FG4B_Website/data/content_index.json
│       └── config.py              # pydantic-settings Settings class
├── prompts/
│   ├── fg4b_input/
│   │   └── stylize.txt            # Stage 0 prompt
│   ├── research/
│   │   └── brief.txt              # Stage 1 prompt — KW strategy + structure
│   ├── draft/
│   │   ├── system.txt             # Writing persona (from style-guide.md)
│   │   ├── article.txt            # Full article directive
│   │   └── fg4b_block.txt         # FG4B block generator prompt
│   └── images/
│       ├── cover.txt              # Cover image DALL-E prompt template
│       └── section.txt            # Body image DALL-E prompt template
├── drafts/                        # Working directory, gitignored
│   └── {slug}/
│       ├── 00_fg4b_input.json     # Stage 0 output (optional)
│       ├── 01_brief.json          # Stage 1 output
│       ├── article.md             # Current draft (always latest)
│       ├── draft_v1.md            # Version history
│       ├── 03_images.json         # Stage 3 output
│       └── images/
│           ├── cover/
│           │   └── cover.png
│           └── body-1/
│               └── body-1.png
├── .claude/
│   └── commands/
│       ├── write.md
│       ├── research.md
│       ├── draft.md
│       ├── images.md
│       ├── publish.md
│       ├── preview.md
│       └── add-image.md
├── docs/
│   ├── roadmap.md
│   ├── style-guide.md             # DONE
│   ├── frontmatter-schema.md      # DONE
│   └── plans/
│       └── phase1-scaffold.md     # THIS FILE
├── tests/
│   ├── __init__.py
│   ├── test_checkpoint.py
│   ├── test_config.py
│   └── test_cli.py
├── config.yaml
├── .env.example
├── .gitignore                     # includes drafts/
├── requirements.txt
├── requirements-test.txt
└── CLAUDE.md
```

---

## Data Models (app/lib/models.py or inline in stages)

Define all pydantic models before writing any stage logic. These are the contract between stages.

### Stage 0 — FG4BInput
```python
class UserSpecifiedLink(BaseModel):
    url: str
    context: str           # why user mentioned it
    anchor_suggestion: str # suggested anchor text

class FG4BInput(BaseModel):
    raw_prose: str
    styled_block: str      # brand-voice cleaned version
    extracted_urls: list[str]
    user_specified_links: list[UserSpecifiedLink]
    themes: list[str]      # key pain points/topics surfaced
    created_at: datetime
```

### Stage 1 — Brief
```python
class KeywordPlacement(BaseModel):
    meta_title: str                    # 50-60 chars
    meta_description: str              # 150-160 chars
    h1_text: str                       # exact H1 string
    intro_keywords: list[str]          # KWs for first 100 words
    image_alt_map: dict[str, str]      # image_id -> alt text

class SectionBrief(BaseModel):
    heading: str
    level: int                         # 2 or 3
    assigned_keywords: list[str]
    word_count_target: int
    notes: str                         # writing guidance for this section

class ImageBrief(BaseModel):
    image_id: str                      # "cover", "body-1", "body-2"
    image_type: str                    # "cover"|"hero"|"before-after"|"over-the-shoulder"|"process"
    style: str                         # "graphic-art"|"photo-real"
    placement_after: str               # heading text to place image after
    dalle_prompt: str
    alt_text: str
    caption: str

class InternalLink(BaseModel):
    target_slug: str
    target_title: str
    anchor_text: str
    placement_section: str             # heading text of section to link from

class Brief(BaseModel):
    slug: str
    topic: str
    article_type: str
    primary_keyword: str
    semantic_keywords: list[str]
    lsi_keywords: list[str]
    search_intent: str                 # "informational"|"transactional"
    category: str                      # must match valid category list
    keyword_placement: KeywordPlacement
    sections: list[SectionBrief]       # full hierarchy in order
    total_word_count_target: int
    faq_questions: list[str]
    images: list[ImageBrief]
    internal_links: list[InternalLink]
    external_link: dict                # {url, anchor_text, placement_section}
    fg4b_block_placement: str          # heading text to insert block after
    competitor_gap_notes: str
    created_at: datetime
```

### Stage 2 — ArticleState
```python
class DraftVersion(BaseModel):
    version: int
    filename: str                      # "draft_v1.md"
    created_at: datetime
    word_count: int

class ArticleState(BaseModel):
    slug: str
    article_type: str
    stage_completed: int               # 0-4
    draft_versions: list[DraftVersion]
    current_draft_path: str
    created_at: datetime
    updated_at: datetime
```

### Stage 3 — ImagesOutput
```python
class ImageResult(BaseModel):
    image_id: str
    local_path: str
    cloudinary_url: str
    alt_text: str
    caption: str
    placed_in_article: bool

class ImagesOutput(BaseModel):
    slug: str
    images: list[ImageResult]
    completed_at: datetime
```

### Stage 4 — PublishResult
```python
class PublishResult(BaseModel):
    slug: str
    destination_path: str              # FG4B_Website/src/content/blog/{slug}.mdx
    archive_path: str                  # FG4B_Website/archive/{slug}_{timestamp}/
    published_at: datetime
```

---

## Step 1 — Environment + Config

**Goal:** deps installed, config.yaml complete, pydantic Settings class, .env.example accurate.

Tasks:
- [ ] Fill `requirements.txt`:
  ```
  anthropic
  openai
  cloudinary
  typer[all]
  pydantic>=2.0
  pydantic-settings
  python-dotenv
  rich
  watchdog
  python-slugify
  pyyaml
  httpx
  ```
- [ ] Fill `requirements-test.txt`: add `pytest-mock` (keep existing pytest, pytest-asyncio, httpx)
- [ ] Update `.env.example`:
  ```
  ANTHROPIC_API_KEY=
  OPENAI_API_KEY=
  CLOUDINARY_CLOUD_NAME=
  CLOUDINARY_API_KEY=
  CLOUDINARY_API_SECRET=
  FG4B_WEBSITE_PATH=C:/Users/alden/dev/FG4B_Website
  ```
- [ ] Create `config.yaml` with AI models, word counts per article type, image sizes, paths
- [ ] Create `app/lib/config.py` — pydantic-settings Settings class reading .env
- [ ] Add `drafts/` to `.gitignore`
- [ ] Verify: `python -c "from app.lib.config import settings; print(settings.model_dump())"` — no crash, all fields present

---

## Step 2 — Data Models

**Goal:** All pydantic models defined, importable, round-trip JSON verified.

Tasks:
- [ ] Create `app/models.py` with all models above
- [ ] Write `tests/test_models.py`:
  - Instantiate each model with sample data
  - Serialize to JSON, deserialize back
  - Verify required field validation fails without required fields
- [ ] Run tests: all pass

---

## Step 3 — Skeleton CLI + Pipeline

**Goal:** All commands exist and run without crashing. Checkpoint manager round-trips to disk.

Tasks:
- [ ] Create `app/lib/checkpoint.py`:
  - `save(slug, stage_name, data: BaseModel) -> Path`
  - `load(slug, stage_name, model_class) -> BaseModel | None`
  - Files written to `drafts/{slug}/{stage_name}.json`
  - Creates directory if not exists
- [ ] Create `app/pipeline.py` with `Pipeline` class:
  - `__init__(slug, mode: Literal["auto", "default", "manual"])`
  - `run_from(stage: int)` — runs stages in sequence from given stage
  - `run_stage(stage: int)` — runs a single stage
  - Each stage call is a stub that prints "Stage N: {name} — not implemented"
- [ ] Create `app/cli.py` with Typer app:
  - `write` command: `topic`, `--type` (default: how-to), `--auto` flag, `--fg4b` option, `--fg4b-file` option
  - `research` command: `slug`
  - `draft` command: `slug`
  - `images` command: `slug`
  - `publish` command: `slug`
  - `preview` command: `slug`
  - `add-image` command: `slug`, `image_path`, `--after` (heading text)
  - `list` command: lists all slugs in drafts/
  - `status` command: `slug`, shows which stages are complete
- [ ] Create `app/stages/__init__.py` and stub files for all 5 stages
- [ ] Write `tests/test_checkpoint.py`:
  - Save a Brief instance, load it back, verify equality
- [ ] Write `tests/test_cli.py`:
  - `python -m app.cli --help` exits 0
  - `python -m app.cli write "test topic" --type how-to` runs without crash (stub output)
  - `python -m app.cli list` runs without crash
- [ ] Run all tests: pass

---

## Step 4 — FG4B_Website MDX Setup

**Goal:** MDX integration active in FG4B_Website. Two components created and rendering.

Tasks (work done in FG4B_Website, not in new_blog_writer):
- [ ] Check `FG4B_Website/package.json` for `@astrojs/mdx` — add if missing
- [ ] Check `FG4B_Website/astro.config.mjs` — add `mdx()` to integrations if missing
- [ ] Create `FG4B_Website/src/components/FG4BBlock.astro`:
  ```astro
  ---
  // Props: none — content passed as slot
  ---
  <aside class="fg4b-block">
    <h4>What This Looks Like at FG4B</h4>
    <div class="fg4b-block__content">
      <slot />
    </div>
  </aside>
  ```
- [ ] Create `FG4B_Website/src/components/BlogImage.astro`:
  ```astro
  ---
  interface Props {
    src: string;
    alt: string;
    caption?: string;
    showCaption?: boolean;
  }
  const { src, alt, caption, showCaption = false } = Astro.props;
  ---
  <figure class="blog-image">
    <img src={src} alt={alt} loading="lazy" />
    {caption && (
      <figcaption class={showCaption ? "caption-visible" : "caption-hidden"}>
        {caption}
      </figcaption>
    )}
  </figure>
  ```
- [ ] Add CSS for `.fg4b-block` and `.caption-hidden` / `.caption-visible` to FG4B_Website global styles
- [ ] Create a test `.mdx` file in FG4B_Website that uses both components
- [ ] Run `npm run dev` in FG4B_Website and verify both components render
- [ ] Delete test file

---

## Step 5 — Prompt Stubs + Reference Docs

**Goal:** All prompt directories and stub files exist. style-guide.md and frontmatter-schema.md complete (already done).

Tasks:
- [ ] Create `prompts/fg4b_input/stylize.txt` — stub: "TODO: Stage 0 prompt"
- [ ] Create `prompts/research/brief.txt` — stub: "TODO: Stage 1 prompt"
- [ ] Create `prompts/draft/system.txt` — stub: "TODO: Writing persona"
- [ ] Create `prompts/draft/article.txt` — stub: "TODO: Article writing directive"
- [ ] Create `prompts/draft/fg4b_block.txt` — stub: "TODO: FG4B block prompt"
- [ ] Create `prompts/images/cover.txt` — stub: "TODO: Cover image prompt"
- [ ] Create `prompts/images/section.txt` — stub: "TODO: Section image prompt"
- [ ] Verify: `python -c "from pathlib import Path; assert Path('prompts/research/brief.txt').exists()"` — passes

---

## Step 6 — Local Slash Commands

**Goal:** All 7 commands defined in `.claude/commands/` and usable from Claude Code.

Tasks:
- [ ] Create `.claude/commands/write.md`
- [ ] Create `.claude/commands/research.md`
- [ ] Create `.claude/commands/draft.md`
- [ ] Create `.claude/commands/images.md`
- [ ] Create `.claude/commands/publish.md`
- [ ] Create `.claude/commands/preview.md`
- [ ] Create `.claude/commands/add-image.md`

Each file follows the pattern:
```markdown
Run [description].

Usage: /[command] [args]

Steps:
1. Ensure venv is active: source venv/Scripts/activate
2. Run: python -m app.cli [command] $ARGUMENTS
3. Show output and next steps
```

---

## Step 7 — Smoke Test

**Goal:** Full scaffold verified. No runtime errors on import or CLI invocation.

Tasks:
- [ ] `python -c "from app.cli import app; print('CLI import OK')"` — passes
- [ ] `python -m app.cli --help` — all 9 commands listed
- [ ] `python -m app.cli write "test" --type how-to` — stub output, no crash
- [ ] `python -m app.cli list` — shows empty list or drafts, no crash
- [ ] `pytest tests/` — all tests pass
- [ ] Checkpoint round-trip test passes (save Brief → load Brief → assert equal)
- [ ] Config loads: `python -c "from app.lib.config import settings; print('Config OK')"`

---

## Build Order and Milestones

| Milestone | What it proves |
|---|---|
| 1. Step 1 complete | Deps installed, config works, environment is clean |
| 2. Step 2 complete | All data contracts defined — stages can be built against them |
| 3. Step 3 complete | CLI wires end-to-end — skeleton runs without crashing |
| 4. Step 4 complete | MDX components live in FG4B_Website — output format locked |
| 5. Steps 5-6 complete | Prompt scaffolding and slash commands ready for Phase 2 |
| 6. Step 7 complete | Phase 1 accepted — ready to start Phase 2 |

**Do not begin Phase 2 until Step 7 smoke test passes completely.**

---

## What Comes Next (Phase 2)

Phase 2 implements real LLM calls in each stage and adds the preview/add-image commands. Plan written after Phase 1 is accepted.

High-level Phase 2 scope:
- Stage 0: real Claude call with stylize.txt prompt
- Stage 1: real Claude call with brief.txt prompt, reads content_index.json
- Stage 2: real Claude call with article.txt + system.txt + fg4b_block.txt
- Stage 3: real DALL-E calls + Cloudinary uploads, article.md updated with real URLs
- Stage 4: assemble frontmatter, write .mdx, archive, update content_index.json
- Preview: copy to FG4B_Website, spawn npm run dev, watchdog watches article.md
- add_image: local path → Cloudinary → insert BlogImage component at specified heading
- End-to-end test: publish a real article from scratch
