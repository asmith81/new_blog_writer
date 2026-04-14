# Frontmatter Schema — FG4B_Website Astro MDX

> Source of truth for all frontmatter fields on blog posts published to FG4B_Website.
> Defined in FG4B_Website/src/content.config.ts.
> Pipeline Stage 4 (publish.py) assembles this block before writing the .mdx file.

---

## Required Fields

```yaml
title: "Post Title Here"
description: "150-160 char SEO meta description."
pubDate: 2026-04-14
```

| Field | Type | Rules |
|-------|------|-------|
| `title` | string | 50-60 chars. Primary keyword in first 3 words. No clickbait numbers unless the article is a listicle. |
| `description` | string | 150-160 chars exactly. Primary keyword present. Answers the search intent. Ends with a period. No quotes. |
| `pubDate` | date (YYYY-MM-DD) | Publication date. Set by pipeline at publish time. Never manually edited after publish without also updating `updatedDate`. |

---

## Optional Fields

```yaml
updatedDate: 2026-04-14   # set when meaningfully revised
heroImage: "https://res.cloudinary.com/djpz0hosc/image/upload/v.../blog/{slug}/cover.png"
category: "Business Growth & Scaling Strategies"
```

| Field | Type | Rules |
|-------|------|-------|
| `updatedDate` | date | Only set when content is materially revised — not for typo fixes or image swaps. |
| `heroImage` | string (URL) | Always a Cloudinary URL. Pattern: `https://res.cloudinary.com/{cloud}/image/upload/{version}/blog/{slug}/cover.{ext}`. Set by Stage 3 (images). |
| `category` | string | Must match an existing category exactly (see list below). Set by Stage 1 (research brief) based on article type and topic. |

---

## Valid Categories

These match the category taxonomy used across FG4B_Website. Do not invent new categories without updating this list and the website.

```
Business Growth & Scaling Strategies
Financial Management & Profitability
Operations & Workflow Optimization
Technology & Digital Tools
Documentation & Record Keeping
Field & Crew Management
```

---

## Complete Example — Published Post

```yaml
---
title: Creating a Receipt Management System for Contractors
description: Build an effective receipt management system for contractors to improve job costing accuracy, maximize tax deductions, and boost profit margins.
pubDate: '2026-03-30'
category: Financial Management & Profitability
heroImage: https://res.cloudinary.com/djpz0hosc/image/upload/v1774923216/blog/contractor-receipt-management-system/cover.png
---
```

---

## Pipeline Assembly Rules (Stage 4)

1. `title` — use `brief.keyword_placement.meta_title` (generated in Stage 1)
2. `description` — use `brief.keyword_placement.meta_description` (generated in Stage 1)
3. `pubDate` — set to today's date at publish time
4. `heroImage` — use `images_output.cover_url` (set in Stage 3)
5. `category` — use `brief.category` (Stage 1 assigns from valid list above)
6. `updatedDate` — omit on first publish; add when revising existing post

---

## MDX File Structure

Every published file follows this structure:

```mdx
---
title: "..."
description: "..."
pubDate: YYYY-MM-DD
category: "..."
heroImage: "https://..."
---

import FG4BBlock from '../../components/FG4BBlock.astro';
import BlogImage from '../../components/BlogImage.astro';

[article body...]
```

The import block is inserted automatically by Stage 4 when the article contains FG4B blocks or BlogImage components. It is omitted if neither component is used.
