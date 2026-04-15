# Phase 2 — MVP

**Status:** Active — Steps 1–7 complete, Step 8 (end-to-end) next
**Goal:** All 5 pipeline stages fully implemented with real API calls. Preview and add-image commands working. End-to-end test publishes a real article to FG4B_Website.
**Last updated:** 2026-04-14

---

## Stack additions (beyond Phase 1)

| Component | Usage |
|---|---|
| Anthropic Claude | Stage 0, 1, 2 LLM calls |
| OpenAI DALL-E 3 | Stage 3 image generation |
| Cloudinary Python SDK | Stage 3 image upload |
| string.Template (stdlib) | load_prompt() safe substitution |
| subprocess / watchdog | Stage 4 preview command |

---

## Design decisions

**Stage 2 uses two LLM calls, never one.**
Main article draft (system.txt + article.txt) and FG4B block (fg4b_block.txt) are always separate calls. This is a hard rule — see CLAUDE.md and master-lessons.

**Full article in one shot.**
Article lengths (1600-2800 words) are well within Claude's output window. Section-by-section generation adds complexity without benefit at this scale.

**content_index.json passed in full.**
Currently 1 post (~32 lines). Pass the full JSON to Stage 1 for internal link candidates. Revisit if it exceeds 50 posts.

**load_prompt() uses safe_substitute().**
All prompt files loaded via a shared `load_prompt(path, **vars)` utility. Uses `string.Template.safe_substitute()` — never `substitute()` — to safely handle `$` patterns in user-supplied content (prices, URLs, etc.).

**strip_fences() applied before every json.loads().**
Claude intermittently wraps JSON output in markdown code fences even when instructed not to. A shared `strip_fences(text)` utility is applied unconditionally before every parse.

**Raw LLM response logged before parsing.**
First 300+ chars logged at DEBUG level before any json.loads() attempt. Eliminates "what did Claude return?" debugging cycle.

**Cloudinary naming convention:**
- Cover: `blog/{slug}/cover`
- Body images: `blog/{slug}/body-1`, `blog/{slug}/body-2`, etc.

---

## Step 1 — Shared lib utilities

**Goal:** All shared utilities built and tested before any stage touches the API.

Tasks:
- [ ] Create `app/lib/prompt_utils.py`:
  - `load_prompt(path: str | Path, **vars) -> str` — reads .txt file, applies `string.Template.safe_substitute(**vars)`
  - `strip_fences(text: str) -> str` — removes leading/trailing ` ```json ` or ` ``` ` fences
- [ ] Create `app/lib/ai_client.py`:
  - `call(system_prompt: str, user_prompt: str, max_tokens: int = 4000, model: str | None = None) -> str`
  - Reads model from `config["ai"]["content_model"]` if not passed
  - Logs raw response (first 300 chars) at DEBUG level before returning
  - Uses `anthropic.Anthropic(api_key=settings.anthropic_api_key)`
- [ ] Create `app/lib/content_index.py`:
  - `load_content_index() -> dict` — reads FG4B_Website/data/content_index.json
  - Returns parsed dict; raises clear error if `FG4B_WEBSITE_PATH` not set or file missing
- [ ] Write `tests/test_prompt_utils.py`:
  - `load_prompt` reads and returns file contents
  - Variable substitution works correctly
  - `$WORD` in substituted value is left unchanged (safe_substitute)
  - `strip_fences` removes ` ```json\n...\n``` ` correctly
  - `strip_fences` is a no-op on clean JSON
- [ ] Write `tests/test_ai_client.py` (mocked):
  - `call()` sends correct system + user messages
  - Returns response text content
  - Uses model from config when none passed
- [ ] Run tests: all pass

---

## Step 2 — Stage 0: FG4B Input

**Goal:** Real Claude call that takes free-form user prose and returns a structured `FG4BInput` object.

Prompt file: `prompts/fg4b_input/stylize.txt`

Tasks:
- [ ] Write `prompts/fg4b_input/stylize.txt` with full prompt:
  - System: brand voice rules from style-guide.md (direct, practical, no jargon, 8th-9th grade)
  - User: takes `$raw_prose`
  - Returns JSON matching FG4BInput schema (styled_block, extracted_urls, user_specified_links, themes)
  - Embed the JSON schema directly in the prompt (not just a description)
- [ ] Implement `app/stages/fg4b_input.py`:
  - `run(slug: str, raw_prose: str) -> FG4BInput`
  - Calls `ai_client.call()` with stylize.txt prompt
  - `strip_fences()` → `json.loads()` → `FG4BInput.model_validate()`
  - Saves checkpoint: `00_fg4b_input.json`
  - Returns `FG4BInput`
- [ ] Write `tests/test_stage_fg4b_input.py` (mocked Claude):
  - Returns valid FG4BInput when Claude returns valid JSON
  - Handles JSON wrapped in code fences
  - Saves checkpoint file
  - Raises `ValidationError` on malformed Claude response
- [ ] Run tests: all pass

---

## Step 3 — Stage 1: Research Brief

**Goal:** Real Claude call that produces a full `Brief` object with keyword strategy, section hierarchy, image plan, and internal links.

Prompt file: `prompts/research/brief.txt`

Tasks:
- [ ] Write `prompts/research/brief.txt` with full prompt:
  - System: SEO content strategist for home service contractors
  - User: takes `$topic`, `$article_type`, `$fg4b_input_json` (optional, empty string if not run), `$content_index_json`
  - Returns JSON matching Brief schema exactly
  - Embed the Brief JSON schema in the prompt
  - Valid categories listed in prompt — model must use one of them exactly
- [ ] Implement `app/stages/research.py`:
  - `run(slug: str, topic: str, article_type: str, fg4b_input: FG4BInput | None = None) -> Brief`
  - Loads content_index.json via `content_index.load_content_index()`
  - Builds prompt with `load_prompt()`, substituting topic, article_type, fg4b_input JSON, content_index JSON
  - Calls `ai_client.call()` with `max_tokens=config["ai"]["max_tokens"]["research"]`
  - `strip_fences()` → `json.loads()` → `Brief.model_validate()`
  - Saves checkpoint: `01_brief.json`
  - Returns `Brief`
- [ ] Write `tests/test_stage_research.py` (mocked Claude):
  - Returns valid Brief on valid Claude response
  - Handles code fence wrapping
  - Saves 01_brief.json checkpoint
  - Passes content_index JSON to prompt
  - Raises on malformed Claude response
- [ ] Update `app/cli.py` `write` command to pass topic and article_type to `pipeline.run_from()`
- [ ] Update `app/pipeline.py` to pass correct kwargs through to each stage
- [ ] Run tests: all pass

---

## Step 4 — Stage 2: Draft Writer

**Goal:** Two real Claude calls — main article draft, then FG4B block — producing `article.md` and `draft_v1.md`.

Prompt files: `prompts/draft/system.txt`, `prompts/draft/article.txt`, `prompts/draft/fg4b_block.txt`

Tasks:
- [ ] Write `prompts/draft/system.txt`:
  - Full writing persona from style-guide.md
  - CRAFT framework rules
  - What "bloat" looks like — do not write these patterns
  - Contractor audience context
- [ ] Write `prompts/draft/article.txt`:
  - Takes `$brief_json`
  - Directive: write the full article exactly per the brief
  - Structure rules: H1, intro (PAS), TLDR bullets, H2 sections, FAQ, conclusion
  - Keyword placement rules from brief.keyword_placement
  - BlogImage component syntax for image placement
  - Internal/external link placement rules
  - Returns raw markdown (not JSON)
- [ ] Write `prompts/draft/fg4b_block.txt`:
  - Takes `$topic`, `$placement_context` (surrounding section text)
  - FG4B block guidelines from style-guide.md
  - Returns the `<FG4BBlock>...</FG4BBlock>` MDX component (not JSON)
- [ ] Implement `app/stages/draft.py`:
  - `run(slug: str) -> ArticleState`
  - Loads `01_brief.json` checkpoint → validates as `Brief`
  - **Call 1:** Main article — `ai_client.call(system=system.txt, user=article.txt(brief_json), max_tokens=config["ai"]["max_tokens"]["draft"])`
  - Writes `drafts/{slug}/article.md` and `drafts/{slug}/draft_v1.md`
  - **Call 2:** FG4B block — `ai_client.call(system=system.txt, user=fg4b_block.txt(topic, placement_context), max_tokens=config["ai"]["max_tokens"]["fg4b_block"])`
  - Inserts FG4B block into article.md after `brief.fg4b_block_placement` heading
  - Saves `ArticleState` checkpoint (stage_completed=2)
  - Returns `ArticleState`
- [ ] Write `tests/test_stage_draft.py` (mocked Claude, two call assertions):
  - Makes exactly two LLM calls (main article + FG4B block)
  - Writes article.md and draft_v1.md
  - FG4B block inserted at correct heading
  - ArticleState checkpoint saved with stage_completed=2
- [ ] Run tests: all pass

---

## Step 5 — Stage 3: Images

**Goal:** DALL-E 3 generates each image from the brief; Cloudinary receives the upload; BlogImage components inserted into article.md.

Tasks:
- [ ] Create `app/lib/image_client.py`:
  - `generate(prompt: str, size: str = "1792x1024") -> bytes` — calls DALL-E 3, returns PNG bytes
  - Uses `openai.OpenAI(api_key=settings.openai_api_key)`
  - No infographic type — skip if `image_type == "infographic"` (not in schema, but defensive)
- [ ] Create `app/lib/cloudinary_client.py`:
  - `upload(image_bytes: bytes, public_id: str) -> str` — uploads to Cloudinary, returns secure URL
  - `public_id` pattern: `blog/{slug}/{image_id}` (e.g. `blog/my-slug/cover`)
  - Uses `cloudinary.config(cloud_name=..., api_key=..., api_secret=...)` from settings
- [ ] Implement `app/stages/images.py`:
  - `run(slug: str) -> ImagesOutput`
  - Loads `01_brief.json` → `Brief`
  - For each `ImageBrief` in `brief.images`:
    - Call `image_client.generate(dalle_prompt, size)` — size from config by image_id (cover vs body)
    - Save PNG to `drafts/{slug}/images/{image_id}/{image_id}.png`
    - Call `cloudinary_client.upload(bytes, public_id=f"blog/{slug}/{image_id}")`
    - Record `ImageResult`
  - Insert `<BlogImage>` components into article.md at `placement_after` heading
  - Save `03_images.json` checkpoint
  - Returns `ImagesOutput`
- [ ] Write `tests/test_stage_images.py` (mocked DALL-E + Cloudinary):
  - Calls generate() once per image in brief
  - Saves PNG files locally
  - Uploads each to Cloudinary with correct public_id
  - BlogImage components inserted in article.md at correct headings
  - 03_images.json checkpoint saved
- [ ] Run tests: all pass

---

## Step 6 — Stage 4: Publish

**Goal:** Assemble frontmatter + imports + article body into a valid `.mdx` file at `FG4B_Website/src/content/blog/{slug}.mdx`. Archive draft.

Tasks:
- [ ] Implement `app/stages/publish.py`:
  - `run(slug: str) -> PublishResult`
  - Loads `01_brief.json` → `Brief`
  - Loads `03_images.json` → `ImagesOutput`
  - Reads `drafts/{slug}/article.md`
  - Assembles frontmatter:
    - `title` ← `brief.keyword_placement.meta_title`
    - `description` ← `brief.keyword_placement.meta_description`
    - `pubDate` ← today's date (YYYY-MM-DD)
    - `heroImage` ← cover image Cloudinary URL from `ImagesOutput`
    - `category` ← `brief.category`
  - Prepends MDX imports (FG4BBlock, BlogImage) if article contains those components
  - Writes to `{FG4B_WEBSITE_PATH}/src/content/blog/{slug}.mdx`
  - Archives draft: copies `drafts/{slug}/` to `{FG4B_WEBSITE_PATH}/archive/{slug}_{YYYYMMDD_HHMMSS}/`
  - Saves `04_publish.json` checkpoint
  - Returns `PublishResult`
- [ ] Write `tests/test_stage_publish.py`:
  - MDX file written to correct path
  - Frontmatter fields match brief + images_output
  - Import block present when article contains FG4BBlock/BlogImage
  - Import block absent when article contains neither
  - Archive directory created
  - PublishResult checkpoint saved
- [ ] Run tests: all pass

---

## Step 7 — Preview + add-image commands

**Goal:** `preview` opens the Astro dev server at the article URL. `add-image` uploads a local image and inserts a BlogImage component.

Tasks:

### preview
- [ ] Implement `app/cli.py` `preview` command:
  - Verify `{FG4B_WEBSITE_PATH}/src/content/blog/{slug}.mdx` exists
  - Spawn `npm run dev` in FG4B_WEBSITE_PATH as subprocess (non-blocking)
  - Print local URL: `http://localhost:4321/blog/{slug}`
  - Print "Press Ctrl+C to stop the dev server"
  - Block on subprocess (let user kill it)
- [ ] Write `tests/test_preview.py`:
  - Exits with error if .mdx not published yet
  - Calls subprocess with correct args
  - Prints correct URL

### add-image
- [ ] Implement `app/cli.py` `add-image` command:
  - Accept `slug`, `image_path`, `--after` heading text
  - Validate image_path exists
  - Generate `image_id` from filename stem (`crew-photo.jpg` → `crew-photo`)
  - Upload via `cloudinary_client.upload(bytes, public_id=f"blog/{slug}/{image_id}")`
  - Insert `<BlogImage src="{url}" alt="{image_id}" caption="" />` after heading in article.md
  - Print Cloudinary URL and confirm insertion
  - Remind user to run `publish` again
- [ ] Write `tests/test_add_image.py`:
  - Uploads image to Cloudinary with correct public_id
  - BlogImage component inserted after correct heading
  - Errors cleanly if image_path not found

---

## Step 8 — End-to-end test

**Goal:** A real article published from scratch. Verified in FG4B_Website Astro build.

This step uses real API calls — it is a manual verification, not an automated test.

Procedure:
1. `python -m app.cli write "how to write a daily job site report for roofing contractors" --type how-to`
2. Review the printed brief (Stage 1 output)
3. Approve and run: `python -m app.cli draft {slug}`
4. Review article.md — word count, structure, FG4B block placement
5. Run: `python -m app.cli images {slug}`
6. Review Cloudinary URLs — verify images generated and uploaded
7. Run: `python -m app.cli publish {slug}`
8. Open FG4B_Website in terminal: `npm run build` — verify 0 errors, new page appears
9. Run: `python -m app.cli preview {slug}` — verify article renders in browser

**Pass criteria:**
- [ ] Brief contains valid slug, keyword_placement, 5+ sections, 2+ images, 1+ internal links
- [ ] article.md is 1600-2000 words, contains FG4B block, at least 2 BlogImage components
- [ ] 03_images.json contains cover + 2 body images, all Cloudinary URLs live and loading
- [ ] {slug}.mdx in FG4B_Website/src/content/blog/ with correct frontmatter
- [ ] `npm run build` in FG4B_Website exits 0, page appears in build output
- [ ] Article renders correctly in browser via `preview`

---

## Build order and milestones

| Milestone | Proves |
|---|---|
| Step 1 complete | Shared utilities solid — all stages can build on them |
| Step 2 complete | Stage 0 live — brand voice processing works |
| Step 3 complete | Stage 1 live — research brief generated and checkpointed |
| Step 4 complete | Stage 2 live — full article drafted with FG4B block |
| Step 5 complete | Stage 3 live — images generated and in Cloudinary |
| Step 6 complete | Stage 4 live — MDX file published to FG4B_Website |
| Step 7 complete | All commands functional end-to-end |
| Step 8 complete | **Phase 2 accepted — pipeline is production-ready** |

---

## Constraints carried from master-lessons.md

Applied to this phase:
- Two-step LLM processing: extraction separate from generation
- `safe_substitute()` not `substitute()` in all prompt loading
- `strip_fences()` unconditionally before every `json.loads()`
- Log raw LLM response (300+ chars) before parsing
- Validate LLM output with Pydantic at the boundary
- Never embed prompt text in Python source
- `load_dotenv(".env")` with explicit path
- ASCII-only CLI output (`[OK]`, `[FAIL]`)
- pydantic-settings field names must match .env keys exactly
- Never combine FG4B block generation with the main draft call
