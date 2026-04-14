# new_blog_writer — Project Roadmap

**Version:** v1.0
**Status:** Active
**Last updated:** 2026-04-14

---

## Overview

AI-powered blog content pipeline that produces publish-ready Astro MDX files for FG4B_Website (fg4b.com). Replaces the old Streamlit-based writing system. Targets home service contractors as the audience. Operated entirely via Python CLI and local Claude Code slash commands.

---

## Phase Summary

| Phase | Name | Goal | Status |
|---|---|---|---|
| 1 | Scaffold | Project structure, data models, skeleton CLI, MDX components, reference docs | Complete |
| 2 | MVP | All 5 stages fully implemented with real API calls, preview, add-image | Active |

---

## Build Sequence

### Phase 1 — Scaffold

See `docs/plans/phase1-scaffold.md` for full implementation detail.

**Milestones:**
- [x] Step 1 — Environment + Config: venv, deps, config.yaml, .env, settings class
- [x] Step 2 — Data Models: all Pydantic models for pipeline state
- [x] Step 3 — Skeleton CLI + Pipeline: all commands wired, checkpoint manager working
- [x] Step 4 — FG4B_Website MDX: @astrojs/mdx, FG4BBlock.astro, BlogImage.astro
- [x] Step 5 — Prompt stubs + Reference docs: style-guide.md, frontmatter-schema.md, prompt file stubs
- [x] Step 6 — Local slash commands: .claude/commands/ wired
- [x] Step 7 — Smoke test: CLI help, import check, checkpoint round-trip verified

### Phase 2 — MVP

*(Plan written when Phase 1 accepted)*

High-level scope:
- Stage 0: FG4B input processor (real Claude call)
- Stage 1: Research & Strategy Brief (real Claude call)
- Stage 2: Draft writer (real Claude call)
- Stage 3: Images (DALL-E + Cloudinary, no infographic)
- Stage 4: Publish to FG4B_Website
- Preview command with Astro dev server + file watcher
- add_image command (local path → Cloudinary → insert in article)
- End-to-end test with real article

---

## Current Step

**Phase 2 — Step 1:** Shared lib utilities (ai_client, load_prompt, strip_fences, content_index)

See `docs/plans/phase2-mvp.md` for full detail.

---

## Completed Steps

- Phase 1 — Step 1: Environment + Config (2026-04-14)
- Phase 1 — Step 2: Data Models (2026-04-14)
- Phase 1 — Step 3: Skeleton CLI + Pipeline (2026-04-14)
- Phase 1 — Step 4: FG4B_Website MDX (2026-04-14)
- Phase 1 — Step 5: Prompt stubs + Reference docs (2026-04-14)
- Phase 1 — Step 6: Local slash commands (2026-04-14)
- Phase 1 — Step 7: Smoke test (2026-04-14)
