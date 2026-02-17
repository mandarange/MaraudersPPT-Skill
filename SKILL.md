---
name: MaraudersPPT-Skill
description: >
  Converts Markdown documents into presentation-quality PowerPoint files (.pptx + .pdf).
  Requires explicit "MaraudersMD2PPT" invocation — never self-activates.
  Maps heading hierarchies, tables, code blocks, images, and AI Hint blocks to 23 slide
  layout types. Generates AI photorealistic images via NanoBanana Pro / Gemini API.
  Extracts core keywords to drive action titles, accent words, and visual coverage.
  Fully supports Korean/CJK text with Pretendard font.
license: MIT
allowed-tools: read write bash glob grep edit
compatibility:
  os: [macos, linux, windows]
  requires: [node, python3]
metadata:
  version: "1.2.2"
  author: "MaraudersPPT"
---

# MaraudersPPT Skill

Converts Markdown → presentation-quality PPTX + PDF. For detailed design specs see `docs/design-spec.md`.

| Reference | Contents |
|-----------|----------|
| [Keyword Extraction](references/keyword-extraction.md) | Core keyword extraction rules, per-section output, anti-patterns |
| [Content Distillation](references/content-distillation.md) | Slide text limits, bullet rules, distillation algorithm |
| [Image Generation](references/image-generation.md) | Visual coverage audit, prompt derivation, layout adaptation |
| [Layout Integrity](references/layout-integrity.md) | Safe areas, font metrics, verification checklist, golden rule |
| [Parallel Execution](references/parallel-execution.md) | 5-wave architecture, Playwright batching, performance gains |
| [Visual QA](references/visual-qa.md) | Post-generation visual inspection workflow |
| [Design Spec](docs/design-spec.md) | Colors, typography, 8px grid, infographic CSS |
| [PRD](docs/prd-md-to-pptx-skill.md) | Product requirements, acceptance criteria |

---

## Activation Guard (GATE)

> **Hard gate. NOTHING runs without this.**

```
BEFORE ANY OTHER STEP:
  1. Scan user's message for "MaraudersMD2PPT" (case-insensitive)
  2. IF FOUND → activation_status = "ACTIVATED" → Proceed to Step 0
  3. IF NOT FOUND → HARD FAIL → Output failure message → STOP
```

**On failure, output exactly:**

```
❌ MaraudersMD2PPT Activation Required

This skill requires explicit invocation. Please use one of:
  MaraudersMD2PPT <filepath>
  MaraudersMD2PPT convert this document
  MaraudersMD2PPT run

Without this keyword, the skill pipeline will not execute.
```

**After failure: STOP. No generic conversion. No alternatives. Wait for re-invocation.**

| Valid | Invalid |
|-------|---------|
| `MaraudersMD2PPT docs/prd.md` ✅ | `Convert this markdown to PPT` ❌ |
| `MaraudersMD2PPT run` ✅ | `Make this into a presentation` ❌ |
| `Step 1: update, Step 2: MaraudersMD2PPT docs/prd.md` ✅ | `Use the pptx skill on this file` ❌ |

---

## Execution Contract

> Once activated, Steps 1–8 run to completion with **ZERO mid-flow confirmations**.

**PROHIBITED during pipeline:** "Should I continue?", "Do you want me to proceed?", "Ready to generate?", or any confirmation request. The only permitted confirmation is the Cursor model-switch (1x, before Step 1).

**State tracking throughout pipeline:**
```
activation_status:  "ACTIVATED" | "FAILED"
pipeline_mode:      "SKILL" (must NEVER be "GENERIC" after activation)
environment:        "OpenCode" | "Cursor"
```

---

## Pipeline Steps

### Step 0: Environment Detection

| | OpenCode | Cursor / Other |
|--|----------|----------------|
| `task()` available? | ✅ | ❌ |
| Image generation | Background (Gemini Pro) | Main thread |
| Model switch? | No | **Yes — 1x confirmation** |

In Cursor only: display Gemini Pro switch guidance, wait for `"continue"` / `"ok"` / `"yes"`, then execute Steps 1–8 without interruption.

### Step 1: Input Reception

- Verify MD file path or receive inline MD text
- Confirm file existence and encoding
- **Collect ALL image paths** from MD (`![alt](path)`) — omission prohibited

### Step 2: Markdown Parsing

- H1 → document title, H2 → section separation
- Classify: bullets, tables, code blocks, images, AI Hint blocks, blockquotes, checklists, **plain paragraphs**
- **PARAGRAPH PRESERVATION (CRITICAL)**: Plain text paragraphs (no bullets, no special markup) MUST be converted to keyword bullets — NEVER silently deleted. Every paragraph produces ≥1 bullet.

### Step 2.3: Core Keyword Extraction (CRITICAL)

> **The single most important step for quality.** Every slide is driven by extracted keywords, not raw text.

Extract `primary_keyword`, `accent_candidate`, `supporting_keywords`, `kpi_metrics` per section. **Full rules → [references/keyword-extraction.md](references/keyword-extraction.md)**

**Quick reference:**

| Output | Usage |
|--------|-------|
| `primary_keyword` | → Action title (sentence ≤15 words) |
| `accent_candidate` | → Bold + `#D94F4F` (1 per slide, word-level) |
| `supporting_keywords` | → Bold only, ranked first in bullets |
| `kpi_metrics` | → Executive summary KPI cards |

### Step 2.5: Visual Content Detection

Auto-detect infographic candidates from text content:

| Pattern | Visualization |
|---------|--------------|
| 3+ items with numbers | Bar Chart |
| Percentages ≈ 100% | Donut Chart |
| 3–8 sequential steps | Process Flow |
| Before/after comparison | Comparison |
| 1–4 key metrics | KPI Cards |
| 4–8 short items | Icon Grid |
| Chronological events | Timeline |
| Decreasing stages | Funnel |

**Mode: AGGRESSIVE** — convert all mappable content. Use `templates/charts/` Python templates.

### Step 2.7: Executive Summary

Auto-insert after title slide for 10+ slide decks. Content: 3–5 KPI metrics + 1-line conclusion.

### Step 2.8: Slide Flow Optimization

- **MAX-2-TEXT**: 3rd consecutive text slide must be visual
- **FRONT-VISUAL**: ≥1 infographic in first 30% of slides
- **AUTO-APPENDIX**: Detailed tables (6+ rows) → appendix; summaries in main body
- **SHORT-SECTION-MERGE**: Sections with ≤2 content lines (e.g., "License: MIT") → merge into previous slide as a footer/badge, or combine multiple short sections into one `icon-grid` / `highlight-card` slide. NEVER create a standalone slide for ≤15 words of body content.

### Step 2.9: Content Distillation (SLIDES ARE NOT DOCUMENTS)

> **The presenter speaks. The slide shows keywords only.** Full rules → [references/content-distillation.md](references/content-distillation.md)

**Hard limits:**

| Layout | Max Bullets | Words/Bullet | Total Slide Words |
|--------|:-----------:|:------------:|:-----------------:|
| `bullet-list` | 3 (max 4) | **7** | **50 EN / 35 KR** |
| `image-text` | 3 | **5** | **50 EN / 35 KR** |
| All others | — | — | **50 EN / 35 KR** |

**Korean/CJK: 0.7x multiplier.** Bullet = keyword fragment, NOT sentence.

**⚠️ CONTENT PRESERVATION GUARANTEE**: Distillation means CONDENSE, never DELETE.

```
HIERARCHY (in order):
  1. Condense → keyword fragments (ALWAYS try this first)
  2. If too short to bullet → use as subtitle or caption text
  3. If section has <15 words total → merge via SHORT-SECTION-MERGE (Step 2.8)
  4. ABSOLUTE PROHIBITION: A section that had content in the source MD
     must produce content on the slide. Zero-content slides = CRITICAL BUG.
```

**Paragraph → Bullet Conversion** (for non-bullet source text):
```
Source paragraph: "This project is licensed under the MIT License."
  → Bullet: • License: **MIT**

Source paragraph: "Contributions are welcome. Please read the contributing guide."
  → Bullet: • Contributions welcome — see guide

Source paragraph: "Built with React, TypeScript, and Tailwind CSS for modern web development."
  → Bullet: • Stack: **React** + TypeScript + Tailwind
```

### Step 3: Slide Mapping

- Determine layout per content block (23 types, see Layout Types below)
- Max 2 topics/slide, max 4 bullets, max 5 table rows / 4 columns, max 12 code lines

**Empty Slide Guard (MANDATORY after mapping):**
```
FOR each mapped slide:
  IF slide.body_content is EMPTY or BLANK:
    → CRITICAL ERROR — content was lost during distillation
    → RECOVERY: Re-extract from source MD section
    → IF source section also empty: merge with adjacent slide or remove slide entirely
    → NEVER render a slide with title but no body/visual
```

### Step 4: Image Generation (MANDATORY)

> **Every non-visual content slide MUST receive an AI-generated image.** Full rules → [references/image-generation.md](references/image-generation.md)

**Quick reference:**
- Slides with images/charts/code/tables → already visual ✅
- `text-body`, `bullet-list`, `ai-hint`, `quote`, `checklist` without visuals → **MUST generate** ❌→✅
- Prompt derived from `primary_keyword` → professional conceptual image
- On generation: `text-body` → `image-text` layout switch (condense text for 50% width)
- **0% text-only content slides allowed**
- **EMPTY SLIDE CATCH**: If a slide reaches Step 4 with NO body content AND no visual → generate image from section title as prompt + add section title as single-line body text. This is the LAST defense against blank slides.

**Generation methods (3 priorities):**
1. **Gemini image gen** — via `task(run_in_background=true)` in OpenCode, or direct in Cursor
2. **HTML concept visual + Playwright screenshot** — ALWAYS WORKS, no external API needed. Create styled HTML (gradient + abstract shapes + keyword) → screenshot as 1920×1080 PNG
3. **SVG geometric placeholder + Sharp** — simplest fallback, minimal visual anchor

**Image save & reference pipeline:**
```
1. mkdir -p "{output_dir}/assets"
2. Save PNG: {output_dir}/assets/ai-img-{NN}-{label}.png
3. In HTML slide: <img src="/absolute/path/to/assets/ai-img-01.png">
4. html2pptx.js reads <img src> → PptxGenJS addImage({ path: ... })
5. Verify: ls -la {output_path} (file exists, size > 0)
```

### Step 5: HTML Slide Generation

- Individual HTML per slide, CSS inline, 16:9 at 1920×1080px
- Pretendard font with fallback chain

### Step 6: PPTX Conversion

- Via `document-skills/pptx`'s `html2pptx.js`
- Tables via PptxGenJS native table API
- AI images via `<img>` tags

### Step 7: Layout Integrity (ZERO TOLERANCE)

> Full rules → [references/layout-integrity.md](references/layout-integrity.md)

**Key rules:**
- Safe area: 68px margins, title ≤188px, body ≤944px
- Font cascade: 18pt → 16pt (NEVER below 16pt) → reduce bullets → split slide
- **Golden rule: If text overflows, the slide has too much text. Fix content, not layout.**
- Max 3 regeneration attempts per slide

### Step 8: Output & Diagnostic Report

```
{original_filename}_pptx/
├── v{M}.{m}_{original_filename}.pptx    ← Editable
├── v{M}.{m}_{original_filename}.pdf     ← Primary output (static, no animations)
└── assets/                               ← Generated charts/images
```

**Diagnostic report (MANDATORY in every completion message):**

```
📊 MaraudersMD2PPT Diagnostic Report
─────────────────────────────────────
Activation:       ✅ ACTIVATED
Pipeline Mode:    SKILL (full pipeline)
Environment:      OpenCode | Cursor
Steps Executed:   [✅] Steps 0–8 (list each)
Quality Metrics:
  Visual coverage:     {N}/{M} (target: 100%)
  Content distillation: All ≤ 50w/35w
  Layout violations:   0
Output: {filepath}
```

### Step 9: Visual QA

> Full workflow → [references/visual-qa.md](references/visual-qa.md)

After generation, visually inspect slide thumbnails for rendering issues automated checks cannot detect: text overflow, font rendering, color accuracy, CJK glyph rendering, alignment consistency.

---

## Design Rules Summary

> **Full specs: `docs/design-spec.md`**

### Color Palette

| Role | HEX | Usage |
|------|-----|-------|
| Background | `#FFFFFF` | Slide background |
| Text | `#1A1A1A` | All default text |
| Accent | `#D94F4F` | Word-level Bold only, 1 per slide |
| Subtext | `#555555` | Secondary text |
| Caption | `#888888` | Footnotes |
| Section BG | `#2C2C2C` | section-divider only |
| Code BG | `#1E1E1E` | Code area interior |

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Main Title | Pretendard | 800 | 36pt |
| Slide Title | Pretendard | 700 | 24pt |
| Body | Pretendard | 400 | 18pt (min 16pt) |
| Caption | Pretendard | 300 | 12pt |
| Code | JetBrains Mono | 400 | 13pt |
| Chart content | Pretendard | 400–700 | **min 16px** |

**Fallback**: Pretendard → Apple SD Gothic Neo → Malgun Gothic → Noto Sans KR → sans-serif

### Layout

- 16:9, 1920×1080px, margins ≥0.7", 8px grid
- Accent `#D94F4F`: word-level Bold only, max 1/slide, prohibited on titles/backgrounds

### Anti-Vibe-Coding Rules

- `border-radius` max 2px (no rounded cards)
- Card backgrounds `#FFFFFF` (no `#FAFAFA` gray)
- No `text-transform: uppercase` + excessive `letter-spacing`
- No decorative `::before`/`::after` bars
- No emoji/icon background boxes
- Text color min `#888888`

### Output Language

PPT language = source MD language. No translation.

### Slide Numbers

All slides (except title): `{current}/{total}`, Pretendard Light 10pt `#888888`, bottom-right.

### CTA Closing Slide

Final slide: key message + 2–3 Next Steps + contact/links.

---

## Slide Layout Types (23)

| Layout | Purpose | Background |
|--------|---------|------------|
| `title` | Document title | `#FFFFFF` |
| `executive-summary` | KPI summary | `#FFFFFF` |
| `section-divider` | H2 section start | `#2C2C2C` |
| `text-body` | General text | `#FFFFFF` |
| `bullet-list` | Bullet/numbered list | `#FFFFFF` |
| `table` | Tabular data | `#FFFFFF` |
| `code` | Code block | `#1E1E1E` area |
| `image` | Image-focused | `#FFFFFF` |
| `image-text` | Image + text (60:40) | `#FFFFFF` |
| `chart` | Data visualization | `#FFFFFF` |
| `quote` | Blockquote | `#FFFFFF` |
| `ai-hint` | AI Hint block | `#F5F5F5` |
| `checklist` | Task list | `#FFFFFF` |
| `kpi-cards` | Key metrics | `#FFFFFF` |
| `bar-chart` | Numeric comparison | `#FFFFFF` |
| `donut-chart` | Proportion | `#FFFFFF` |
| `process-flow` | Sequential process | `#FFFFFF` |
| `timeline` | Chronological | `#FFFFFF` |
| `comparison` | Comparison (vs) | `#FFFFFF` |
| `icon-grid` | Category listing | `#FFFFFF` |
| `funnel` | Stage reduction | `#FFFFFF` |
| `appendix-divider` | Appendix start | `#2C2C2C` |
| `closing` | CTA final slide | `#FFFFFF` |

---

## Image Generation Pipeline

> **MANDATORY for all slides without visual content.** Full details → [references/image-generation.md](references/image-generation.md)

| Target | Method |
|--------|--------|
| Slides without visuals | Priority 1: Gemini → Priority 2: HTML concept visual + Playwright → Priority 3: SVG + Sharp |
| Charts/infographics | HTML templates (`templates/charts/`) → Playwright screenshot |
| Diagrams/flowcharts | HTML/SVG |
| Original MD images | Copy to `assets/`, reference via absolute path in HTML |

**Pipeline**: Generate PNG → save to `{output_dir}/assets/` → reference in HTML via `<img src="/absolute/path/...">` → html2pptx.js embeds via PptxGenJS `addImage({ path })` → PPTX and PDF both render the image.

**Priority 2 (HTML concept visual)** is the most reliable — works in ANY environment with only Playwright (already a dependency). It generates a styled gradient background with abstract shapes and the slide's keyword, then screenshots it as a 1920×1080 PNG.

---

## Dependencies

| Dependency | Role | Required |
|-----------|------|----------|
| `document-skills/pptx` | html2pptx engine, PptxGenJS API | **Required** |
| `NanoBanana Pro` | AI image generation (Gemini CLI Extension) | **Required** |
| `Gemini 2.5 Flash Image API` | NanoBanana fallback | Fallback |
| `pptxgenjs` | PowerPoint generation | **Required** (npm) |
| `playwright` | HTML rendering / screenshots | **Required** (npm) |
| `sharp` | Image post-processing | **Required** (npm) |

---

## Validation Checklist

### Activation & Pipeline
- [ ] `MaraudersMD2PPT` keyword found, `activation_status` == "ACTIVATED"
- [ ] `pipeline_mode` == "SKILL" (never "GENERIC")
- [ ] No mid-pipeline confirmations, diagnostic report included

### Keywords (Step 2.3)
- [ ] Every section has `primary_keyword` and `accent_candidate`
- [ ] Action titles from `primary_keyword` (≤15 words)
- [ ] No unfocused slides (raw text dump prohibited)

### Content (Step 2.9)
- [ ] Total slide text ≤ 50w EN / 35w KR
- [ ] Bullets ≤ 3 (max 4), each ≤ 7 words — keyword fragments only
- [ ] No full sentences, no filler words, CJK 0.7x applied
- [ ] **ZERO empty slides** — every slide with a title has body content or visual
- [ ] Plain paragraphs converted to keyword bullets (never deleted)
- [ ] Short sections (≤2 lines) merged, not standalone slides

### Visual Coverage (Step 4)
- [ ] **0% text-only content slides**
- [ ] AI images derived from `primary_keyword`
- [ ] Layout adapted on image addition, text condensed

### Design
- [ ] Accent `#D94F4F`: 1 per slide, word-level Bold only
- [ ] Body ≥ 16pt, max 3 font sizes/slide
- [ ] Margins ≥ 0.7", no overflow/overlap, 8px grid

### Slide Flow
- [ ] Executive summary present (10+ slides)
- [ ] MAX-2-TEXT, FRONT-VISUAL, AUTO-APPENDIX, **SHORT-SECTION-MERGE** rules applied
- [ ] CTA closing slide with Next Steps

### Charts
- [ ] All chart text ≥ 16px, no uppercase, border-radius ≤ 2px
- [ ] Grayscale base + 1 accent color

---

## Parallel Execution

> **Full architecture → [references/parallel-execution.md](references/parallel-execution.md)**

5-wave pipeline: Gate → Parse → Parallel (images + charts + HTML) → Collect → Assemble + Verify. AI image generation fires first (5–15s), charts render instantly (<100ms), slide HTML generates in foreground while background tasks complete.

---

## Future Improvements (v1.1 Roadmap)

| Item | Description |
|------|-------------|
| `--audience` parameter | `executive` (12 slides, 3 bullets) / `team` (full detail) |
| CSS Custom Properties | Theme switching via CSS variables |
| Hero Metric Layout | Single dramatic number at 120px |
| Slide Complexity Score | Auto-calculate cognitive complexity |
