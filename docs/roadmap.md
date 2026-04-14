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
| 1 | Scaffold | Project structure, data models, skeleton CLI, MDX components, reference docs | Active |
| 2 | MVP | All 5 stages fully implemented with real API calls, preview, add-image | Pending |

---

## Build Sequence

### Phase 1 — Scaffold

See `docs/plans/phase1-scaffold.md` for full implementation detail.

**Milestones:**
- [ ] Step 1 — Environment + Config: venv, deps, config.yaml, .env, settings class
- [ ] Step 2 — Data Models: all Pydantic models for pipeline state
- [ ] Step 3 — Skeleton CLI + Pipeline: all commands wired, checkpoint manager working
- [ ] Step 4 — FG4B_Website MDX: @astrojs/mdx, FG4BBlock.astro, BlogImage.astro
- [ ] Step 5 — Prompt stubs + Reference docs: style-guide.md, frontmatter-schema.md, prompt file stubs
- [ ] Step 6 — Local slash commands: .claude/commands/ wired
- [ ] Step 7 — Smoke test: CLI help, import check, checkpoint round-trip verified

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

**Phase 1 — Step 1:** Environment + Config

See `docs/plans/phase1-scaffold.md` for full detail.

---

## Completed Steps

*(none yet)*
