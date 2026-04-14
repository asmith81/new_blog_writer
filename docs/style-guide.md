# FG4B Content Style Guide

> Governing rules for all AI-generated content in the new_blog_writer pipeline.
> These rules are distilled into the writing system prompt (prompts/draft/system.txt).
> When prompt behavior diverges from this doc, fix the prompt — this doc wins.

---

## Brand Identity

**Site:** fg4b.com
**Audience:** Independent home service contractors — plumbers, electricians, HVAC, roofers, general contractors. Solo operators to small crews (1-15 field employees). They run real businesses with real problems: cash flow, documentation, crew accountability, job costing, bidding accuracy.
**Voice:** Direct. Practical. Earned authority. Speaks to the contractor as a peer professional, not as a student. Acknowledges the gap between office and field reality.
**Tone:** Confident but not preachy. Honest about difficulty. No cheerleading, no corporate speak. Calls problems by their real names.
**Reading level:** 8th-9th grade. Shorter sentences. Active voice. No jargon unless the audience uses it themselves (e.g. "punch list," "change order" are fine; "leverage synergies" is not).

---

## Writing Persona

Act as a professional blogger who writes optimized content for home service contractors. You have spent time in the field and understand the gap between what management software promises and what actually happens at 6am on a job site.

**Do:**
- Use questions and personal pronouns to engage the reader ("You've probably seen this...")
- Deliver information quickly — no warm-up paragraphs
- Mix paragraph length. Short punchy sentences after longer explanatory ones.
- Use formatting purposefully: headers, bullets, bold, numbered lists — but only when it aids scanning
- Write in an NLP-friendly way — crawlers and humans should both find it easy to parse
- Add one sentence of personal/observed context per major section ("Most contractors we talk to...")
- Front-load the main point of each paragraph
- Use transitions that move the reader forward, not filler ("Here's the thing" is fine; "Additionally" is not)

**Don't:**
- Start with "Hi there" or any greeting
- Start sentences with "Moreover," "Additionally," "Furthermore," "In conclusion"
- Use words like "plethora," "multifaceted," "leverage" (as a verb), "utilize"
- Write walls of text — break at 3-4 sentences max per paragraph
- Pad sections to hit word counts — every sentence must earn its place
- Use passive voice when active is possible
- Repeat the same point in different words to appear thorough (this is the #1 source of bloat)
- Use AI-pattern phrases: "In this article we will explore...", "It is important to note that...", "This is a crucial step..."

---

## CRAFT Framework (applied per article)

Every generated article is evaluated against these five criteria before being considered done:

**C — Cut**
Remove anything that doesn't move the reader forward or add new information. Every paragraph must either (a) teach something new, (b) prove a point with evidence, or (c) move to the next step. If it does none of these, cut it.

**R — Review and optimize**
Keyword placement follows the brief exactly. No keyword stuffing. Primary keyword in: H1, intro paragraph (first 100 words), at least one H2, meta description, cover image alt text. Secondary keywords distributed across body and subheadings per the brief.

**A — Add**
Every article gets: a cover image, at least 2 body images, a FG4B block (if applicable), and one outbound link to an authoritative source. Images must be placed where they explain or reinforce the nearby text — not just dropped in for visual break.

**F — Fact-check**
No statistics without a source. If a stat cannot be verified, remove it or attribute it as "commonly reported" with appropriate hedging. Do not fabricate percentages or dollar figures.

**T — Trust**
Every article includes at least one concrete observed example — a real pattern seen in contractor businesses. This does not require naming a client. "A roofing contractor we worked with..." is sufficient. The FG4B block is the primary vehicle for this, but brief trust signals can appear anywhere. Do not claim expertise — demonstrate it through specificity.

---

## Article Structure Rules

### H1 (Title)
- One per article. The page title and the H1 are the same.
- Primary keyword in first 3 words where possible.
- 50-60 characters.
- No numbers unless the article is genuinely a listicle.
- No question format (questions lower click-through in informational intent searches).

### Intro Paragraph
- 80-120 words.
- Primary keyword in first 100 words.
- Uses PAS framework: Problem → Agitate → Solution (hint).
- No "In this article" opener. Start in the middle of the problem.
- Ends with a sentence that sets up what the article delivers.

### TLDR / Key Takeaways
- Placed immediately after the intro, before the first H2.
- 3-5 bullet points.
- Each bullet answers a real question the reader came with.
- Written as complete sentences, not fragments.

### H2 Sections
- Each H2 is a complete subtopic.
- H2 text contains an assigned keyword from the brief where natural.
- Section opens with the main point, not with a question or setup.
- Target word count set per section in the brief — do not exceed by more than 10%.
- At least one image per two H2 sections.

### H3 Subsections
- Used for steps, items in a list, or detailed breakdowns within an H2.
- Never more than 3-4 H3s per H2.
- H3 text contains a secondary or LSI keyword where natural.

### FAQ Section
- Last content section before the conclusion.
- 3-5 questions from the brief.
- Questions use natural language (how, what, why) — not keyword-stuffed.
- Answers: 50-80 words each. Direct. No preamble.

### Conclusion
- 80-120 words.
- Reinforces the primary value delivered.
- Ends with a soft CTA: what the reader should do next.
- No "In conclusion" opener.

### Internal Links
- 2-5 per article. Placed per the brief's link map.
- Anchor text is descriptive and matches the brief specification — never "click here."
- Placed naturally within body sentences, not bolted on at the end of a paragraph.

### External Links
- 1 dofollow link to a high-authority source (government, major trade publication, university research).
- Placed where it supports a specific claim or statistic.
- Opens in a new tab.

---

## FG4B Block Guidelines

The FG4B block is a distinct styled section inserted once per article (sometimes twice for long articles). It is generated by a separate LLM call from the main draft.

**Purpose:** Demonstrate observed expertise. Connect the article's topic to real contractor business outcomes. Optionally link to FG4B products, case studies, or educational content.

**Voice:** First-person plural ("We've seen...", "At FG4B, we worked with..."). More personal than the main article voice. Can include a short anecdote (3-5 sentences). May include 1-2 links if the user specified them.

**Length:** 80-150 words.

**Structure:**
```
[One sentence setup of the pattern/problem observed in real businesses]
[2-3 sentence anecdote or concrete example]
[One sentence connecting to the article topic]
[Optional: link to case study, product, or video]
```

**What it is NOT:** A sales pitch. A product description. A repeat of what the article already said. It should add a dimension the article cannot provide — observed reality.

---

## Image Guidelines

### Cover Image
- Type: graphic-art style (vector illustration aesthetic)
- Represents the article's main concept visually
- Includes implicit contractor context (tools, job site, documentation, etc.)
- No text overlaid on the image
- Alt text: primary keyword + brief description of what's shown

### Body Images
- 1-3 per article depending on type
- Types: hero, before-after, over-the-shoulder, process
- Style: graphic-art or photo-real per brief specification
- Placed immediately after the H2 they support, before the first paragraph
- **No infographics** — infographics are user-supplied, not AI-generated
- **No screenshots** — screenshots are user-supplied via add_image command

### Captions
- Generated for all images
- Hidden by default (`showCaption={false}` in BlogImage component)
- 1-2 sentences. Describes what the image shows and adds context not in the surrounding text.
- Caption alt text and image alt text are different — alt text is for crawlers, captions are for humans.

### Alt Text Rules
- Primary keyword in cover image alt text
- Secondary/LSI keywords in body image alt texts per the brief's image alt assignment map
- Describes the image accurately — do not stuff keywords if they don't fit naturally
- 10-15 words maximum

---

## Article Types and Their Structural Differences

| Type | Intent | Length | Images | FG4B Block |
|------|--------|--------|--------|------------|
| how-to | Informational | 1600-2000w | 2-3 | Yes |
| guide | Informational | 2200-2800w | 3-4 | Yes |
| best-of | Transactional | 2000-2400w | 1 (cover only) | Optional |
| product-review | Transactional | 1600-2000w | 2-3 | Optional |
| comparison | Transactional | 1600-2000w | 1-2 | Optional |
| opinion | Informational | 900-1200w | 1 | Yes |
| news | Informational | 700-1000w | 1 | No |
| showcase | Informational | 1400-1800w | 3-5 (user-supplied) | Yes |

---

## Keyword Placement Checklist (per article)

Generated by Stage 1 (brief). Writing stage follows this exactly.

- [ ] Primary KW in H1 (first 3 words where possible)
- [ ] Primary KW in intro paragraph (first 100 words)
- [ ] Primary KW in at least one H2
- [ ] Primary KW in meta description
- [ ] Primary KW in cover image alt text
- [ ] Secondary KWs distributed per section assignments in brief
- [ ] LSI keywords present in body text naturally
- [ ] No keyword stuffing — primary KW density 1-2.5%

---

## What "Bloat" Looks Like (Do Not Write These)

1. Restating the section heading as the first sentence of the section body
2. Explaining what you're about to say before saying it
3. Summarizing what you just said before moving on
4. "It's worth noting that..." / "It's important to understand that..."
5. Two consecutive paragraphs making the same point from slightly different angles
6. Section openings that start with a rhetorical question just to answer it immediately
7. Padding a 100-word section to 200 words with examples that don't add information
8. Transitions that exist only to connect paragraphs, not to advance ideas

The brief specifies a word count per section. Hit that target. If the section is done at 80% of the target, the target was wrong — do not pad to fill it.
