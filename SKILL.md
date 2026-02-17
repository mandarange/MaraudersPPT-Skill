---
name: maraudersmapmd-to-pptx
description: >
  A skill that converts Markdown documents into structured PowerPoint presentations.
  This skill does NOT activate automatically — users must explicitly invoke
  "MaraudersMD2PPT" to run it. It will never self-activate without invocation.
  Automatically maps MaraudersMapMD-style heading hierarchies, tables, code blocks,
  images, and AI Hint blocks to slide structures, generating presentation-quality
  .pptx files. Leverages document-skills/pptx's html2pptx infrastructure and supports
  AI photorealistic image generation via NanoBanana Pro. Fully supports Korean/CJK text.
license: MIT
allowed-tools:
  - read
  - write
  - bash
  - glob
  - grep
  - edit
metadata:
  version: "1.1"
  author: "MaraudersPPT"
---

# MaraudersPPT Skill

A skill that automatically converts Markdown documents into presentation-quality PPTX.
For detailed design specifications, see `docs/design-spec.md`. For feature requirements, see `docs/prd-md-to-pptx-skill.md`.

---

## ⛔ Invocation Rule (NEVER VIOLATE)

> **This skill only runs when the user explicitly invokes `MaraudersMD2PPT`.**
> Even if a similar request is made (e.g., "Make a PPT", "Convert to slides"), this skill must **never** self-activate without the `MaraudersMD2PPT` keyword.

### Valid Invocation Examples

```
"MaraudersMD2PPT convert this document"
"MaraudersMD2PPT docs/prd.md"
"MaraudersMD2PPT run"
```

### Invalid Invocations (Auto-Activation Prohibited)

```
"Convert this markdown to PPT"              ← No MaraudersMD2PPT keyword → do not activate
"Make this into a presentation"             ← No MaraudersMD2PPT keyword → do not activate
"Convert this to PowerPoint"                ← No MaraudersMD2PPT keyword → do not activate
```

---

## 0) Environment Detection & Model Guide

### Cursor / Non-OpenCode Environments

In Cursor, Antigravity, and other non-OpenCode environments, the model cannot be switched at runtime.
**Before starting work**, display the following message and wait for user confirmation:

```
⚠️ Gemini Pro Model Selection Required

This PPT conversion task requires Gemini Pro for AI image generation.
Please switch your current model to Gemini Pro (gemini-2.5-pro) before proceeding.

How to switch: [IDE Settings] → [Model Selection] → Select Gemini Pro

After switching, type "continue" or "ok" to proceed.
```

- **Confirmation keywords**: `"continue"`, `"proceed"`, `"ok"`, `"yes"`, `"done"`
- **Never** start conversion before user confirmation

### OpenCode Environment

In OpenCode, only the image generation step uses the Gemini Pro model:

- **Main pipeline**: Runs on the user's selected model (MD parsing, mapping, HTML generation, PPTX conversion)
- **Image generation**: Spawned as a Gemini Pro model background task via `task(run_in_background=true)`
- After generation completes, results are collected via `background_output()`

### Environment Detection Method

- Determined by whether the `task()` function is available
- If unavailable → Apply Cursor workflow

---

## 1) Full Workflow

### Step 0: Environment Detection & Model Confirmation

- Detect IDE environment (OpenCode vs Cursor/Others)
- OpenCode: Check background task API → Prepare Gemini Pro for image generation
- Cursor/Others: Display Gemini Pro switch guidance → Wait for user confirmation → Proceed after confirmation

### Step 1: Input Reception

- Verify MD file path or receive inline MD text
- Confirm file existence, verify encoding
- **Collect all image paths from the original MD** (`![alt](path)` format — both local and remote): All images **must** be included in slides — omission is prohibited

### Step 2: Markdown Parsing

- H1 → Extract document title
- H2 → Section separation (create Section[])
- Classify content types within each section:
  - Bullet/numbered lists, tables, code blocks (with language tags), images, AI Hint blocks, blockquotes, checklists, plain text

### Step 2.3: Core Keyword Extraction (CRITICAL — PPT Quality Gate)

> **This is the single most important step for PPT quality.**
> A presentation without properly extracted keywords is just a text dump on slides.
> Every slide MUST be driven by its extracted keywords — not raw MD text.

Extract **core keywords** from each section's content. These keywords drive every downstream decision: action titles, accent words, bullet prioritization, and executive summary content.

#### Extraction Targets (scan in priority order)

| Priority | Source | What to Extract | Example |
|----------|--------|----------------|---------|
| 1 | `**bold text**` | Explicitly emphasized terms | `**3x faster**` → "3x faster" |
| 2 | Numbers + units | Metrics, KPIs, quantitative data | "95%", "$2.4M", "3 seconds → 0.8 seconds" |
| 3 | `[AI DECISION]` / `[AI RULE]` | Key decisions and constraints | "Adopt MSA architecture" |
| 4 | Comparison phrases | Before/after, improved/reduced | "failure rate reduced by 73%" |
| 5 | Proper nouns | Technology, product, company names | "PostgreSQL", "Kubernetes", "MaraudersMapMD" |
| 6 | Action verbs + outcomes | Conclusive statements | "eliminates manual review", "automates deployment" |

#### Per-Section Output

For each H2 section, produce:

```
Section Keywords = {
  section_title: "Background",
  primary_keyword: "processing speed 3x improvement",     ← Single most impactful phrase (drives action title)
  accent_candidate: "3 seconds → 0.8 seconds",            ← For Bold+#D94F4F treatment (1 per slide max)
  supporting_keywords: ["failure rate 73% reduction", "MSA architecture"],  ← Secondary emphasis (Bold only)
  kpi_metrics: ["95% success rate", "2.5% → 0.7% failure rate"],           ← Feed executive summary
}
```

#### Keyword Usage Rules (MANDATORY)

| Usage Point | How Keywords Are Applied |
|-------------|------------------------|
| **Action Title** | `primary_keyword` → Rewrite as complete sentence (≤15 words) with verb + conclusion |
| **Accent Word** | `accent_candidate` → Apply Bold + `#D94F4F` (1 per slide, word-level only) |
| **Bullet Priority** | Bullets containing `supporting_keywords` ranked first in slide |
| **Executive Summary** | Top 3–5 `kpi_metrics` across all sections → KPI cards |
| **Slide Focus** | Each slide must revolve around its `primary_keyword` — no unfocused slides |

#### Keyword Density Control

- **Per slide**: Exactly 1 `accent_candidate` (Bold + Red) + up to 2 `supporting_keywords` (Bold only)
- **Per deck**: All `kpi_metrics` must appear in Executive Summary
- **If no keywords found in section**: Flag as low-value content → candidate for merge with adjacent section or appendix

#### Anti-Pattern: Raw Text Dump (PROHIBITED)

```
❌ WRONG — Dumping MD text directly onto slide:
   Title: "Background"
   Body: "The existing payment system has the following problems:
          Slow processing speed (average 3 seconds),
          High failure rate (2.5%), No monitoring"

✅ CORRECT — Keyword-driven slide:
   Title: "Processing speed 3x bottleneck demands architecture overhaul"
   Body: • Processing speed: **3 seconds** average (target: <1s)
         • Failure rate: **2.5%** — 73% above industry benchmark
         • Zero monitoring coverage across all services
   Accent: "3 seconds" in Bold + #D94F4F
```

### Step 2.5: Visual Content Detection

Analyze parsing results to identify candidates for automatic infographic conversion from text content:

| Pattern | Trigger | Visualization Type |
|---------|---------|-------------------|
| `NUM-COMPARE` | 3+ items each containing numeric values | Bar Chart |
| `PCT-BREAKDOWN` | Percentages summing to ~100% | Donut Chart |
| `SEQ-STEPS` | 3–8 sequential steps | Process Flow |
| `BEFORE-AFTER` | vs/before/after comparison | Comparison |
| `KEY-METRIC` | 1–4 key metrics + labels | KPI Cards |
| `CATEGORY-LIST` | 4–8 short items (no numbers) | Icon Grid |
| `CHRONOLOGICAL` | Dates/periods + chronological events | Timeline |
| `NARROWING-STAGES` | Decreasing quantity stages | Funnel |

**Detection mode**: AGGRESSIVE — Convert all mappable content to visualizations
**Priority**: Visualization candidates > Plain text/table layouts
**Verification**: Confirm visualization conversion doesn't cause information loss

**Chart rendering**: Use `templates/charts/` Python templates — pass data only to generate HTML.

```python
from templates.charts import render_chart
html = render_chart("kpi_cards", [{"label": "Success Rate", "value": "95%", "accent": True}])
```

### Step 2.7: Auto-Generate Executive Summary

Auto-insert an `executive-summary` slide right after the title slide, summarizing the document's key content as 3–5 KPI/key messages:

- **Target**: Documents generating 10+ slides
- **Content**: 3–5 key metrics extracted from the entire document + 1-line conclusion
- **Layout**: `executive-summary` (KPI Cards variant)
- **Position**: Immediately after the title slide (Slide #2)

### Step 2.8: Slide Flow Optimization

Optimize slide sequence before mapping:

**Consecutive Text Slide Prevention (MAX-2-TEXT)**:
- If text-only slides (`text-body`, `bullet-list`) appear **2 in a row**, the 3rd must be a visual slide (infographic, image, chart)
- If no visualizable content exists, attempt conversion to `icon-grid` or `comparison`

**Early Infographic Placement Rule**:
- Place at least 1 infographic in the **first 30%** of total slides
- Move high visual-impact slides (KPI, Bar Chart, Comparison) earlier

**Auto Appendix Separation Rule**:
- Auto-move detailed tables (6+ rows), QA checklists, dependency lists, etc. to `appendix` section
- Keep only summary versions (3 rows or fewer) in the main body + "Details: See Appendix" footnote

### Step 2.9: Slide Content Distillation (SLIDES ARE NOT DOCUMENTS)

> **A slide is a visual aid, not a document.**
> If there's too much text on a slide, the slide is WRONG — not "overflowing."
> The problem is never layout capacity. The problem is failing to distill.
>
> **The presenter speaks. The slide shows keywords only.**
> If the audience can read the slide instead of listening, you've failed.

#### The Core Rule

```
Every piece of text on a slide must pass this test:
  "Can I remove this and still deliver the message?"
  If YES → REMOVE IT.
  If NO  → SHORTEN IT to the fewest possible words.
```

#### Hard Content Limits per Layout Type

These are not "maximums before overflow." These are **good slide design limits.**
Exceeding these means the content is poorly distilled — fix the content, not the layout.

| Layout | Title | Body | Bullets | Words/Bullet |
|--------|:-----:|:----:|:-------:|:------------:|
| `title` | 8 words | 10 words (subtitle) | — | — |
| `executive-summary` | 6 words | 15 words (conclusion) | — | — |
| `section-divider` | 6 words | — | — | — |
| `text-body` | 10 words | 40 words | — | — |
| `bullet-list` | 10 words | — | **3** (max 4) | **7** |
| `image-text` | 8 words | — | 3 | **5** |
| `table` | 8 words | — | — | — |
| `code` | 8 words | — | — | — |
| `ai-hint` | 8 words | 30 words | — | — |
| `quote` | — | 20 words (quote) | — | — |
| `checklist` | 8 words | — | 4 items | 6 |
| `closing` | 8 words | — | 3 steps | 5 |

**Korean/CJK**: Apply **0.7x multiplier** (e.g., 7 words → 한국어 약 5단어/12음절).

#### Bullet = Keyword Fragment, Not Sentence

```
❌ WRONG (sentence on a slide):
   • "The processing speed was improved from an average of 3 seconds to 0.8 seconds"

✅ CORRECT (keyword fragment):
   • Processing speed: **3s → 0.8s**

❌ WRONG (too many words):
   • "We adopted MSA architecture because we needed independent deployment capability"

✅ CORRECT:
   • MSA 도입 → 독립 배포 가능
```

**Per-bullet rule**: If a bullet has more than 7 words, it's a sentence. Rewrite as a keyword fragment.

#### Slide Total Text Budget

```
ENTIRE slide (title + all body text combined):
  English: MAX 50 words total
  Korean:  MAX 35 words total (≈60 syllables)

If you exceed this budget, the slide has too much content.
Split or move detail to appendix.
```

#### Distillation Algorithm

```
FOR each content_block:
  1. Extract keywords (Step 2.3)
  2. Rewrite as keyword fragments (noun-phrase, no verbs, no filler)
  3. Count total slide words
  4. IF > 50 words (EN) / 35 words (KR):
     → Split into 2 slides, OR
     → Move supporting detail to appendix
  5. VERIFY: presenter can read entire slide in ≤3 seconds
```

#### Anti-Patterns (ALL PROHIBITED)

| What | Why It's Wrong | Fix |
|------|---------------|-----|
| Full sentences on slides | Audience reads instead of listens | Keyword fragments only |
| 5+ bullets | Cognitive overload | Max 3 (rarely 4) |
| Bullet longer than 1 line | It's a paragraph disguised as a bullet | Condense to ≤7 words |
| Prose paragraphs on slides | This is a document, not a slide | Extract 2-3 keyword bullets |
| Repeating title content in body | Redundancy wastes space | Title = conclusion, body = evidence |
| Filler words ("In order to", "It is important that") | Zero information value | Delete completely |

### Step 3: Slide Mapping

- Determine slide layout for each content block (see Section 5)
- Auto-split based on content volume:
  - Max **2 topics** per slide
  - Max **4 bullets** (split if exceeded, optimal 3)
  - Max **5 rows** / **4 columns** for tables (split or move to appendix if exceeded)
  - Max **12 lines** for code (split if exceeded)

### Step 4: Slide Image Generation (MANDATORY for all non-visual slides)

> **Every slide that lacks a visual element MUST receive a generated image.**
> A slide without graphics is incomplete. No exceptions.

#### 4.1 Visual Coverage Audit

After Step 3 (Slide Mapping), scan every slide and classify:

| Slide Status | Has Visual? | Action Required |
|-------------|:-----------:|-----------------|
| Has original MD image (`![alt](path)`) | ✅ | None — use original image |
| Has chart/infographic (auto-detected in Step 2.5) | ✅ | None — use chart rendering |
| Has code block (dark background = visual) | ✅ | None — code itself is visual |
| Has table (native table = visual) | ✅ | None — table itself is visual |
| `section-divider` slide | ✅ | None — inverted background is visual |
| `title` slide | ⚠️ | Generate abstract conceptual image |
| `text-body` slide — **NO visual** | ❌ | **MUST generate image** |
| `bullet-list` slide — **NO visual** | ❌ | **MUST generate image** |
| `ai-hint` slide — **NO visual** | ❌ | **MUST generate image** |
| `quote` slide — **NO visual** | ❌ | **MUST generate image** |
| `checklist` slide — **NO visual** | ❌ | **MUST generate image** |
| `closing` slide | ⚠️ | Generate abstract conceptual image |

**Rule: 0% of content slides may be text-only (excluding code/table/chart slides).**

#### 4.2 Image Prompt Derivation (from Keyword Extraction)

The image prompt is derived directly from Step 2.3's `primary_keyword`:

```
Image Concept = Slide's primary_keyword → One-line visual metaphor

Examples:
  primary_keyword: "processing speed 3x improvement"
  → Image prompt: "professional high-speed data stream flowing through modern server infrastructure, clean white background, high resolution, no text, no logos, no watermarks"

  primary_keyword: "MSA architecture adoption"
  → Image prompt: "interconnected microservices nodes forming a distributed network architecture, professional clean diagram style, high resolution, no text, no logos, no watermarks"

  primary_keyword: "failure rate 73% reduction"
  → Image prompt: "professional quality control dashboard showing dramatic improvement trend, clean minimal design, high resolution, no text, no logos, no watermarks"
```

#### 4.3 Prompt Construction Rules

Every image prompt MUST include:
1. **Core concept** derived from `primary_keyword` (1 sentence)
2. **Style keywords**: `"professional"`, `"clean background"`, `"high resolution"`
3. **Prohibition clause**: `"no text, no logos, no watermarks"`
4. **Contextual modifier**: Match the domain of the slide content (tech, business, medical, etc.)
5. **Tone**: Corporate presentation quality — NOT stock photo, NOT artistic illustration

#### 4.4 Layout Adaptation When Image Is Added

When a generated image is added to a previously text-only slide:

| Original Layout | New Layout | Image Position |
|----------------|-----------|----------------|
| `text-body` | `image-text` | Left 50% image \| Right 50% text |
| `bullet-list` | `image-text` | Left 50% image \| Right 50% bullets |
| `ai-hint` | `ai-hint` (keep) | Image inserted above hint block (30% height) |
| `quote` | `quote` (keep) | Background image at 15% opacity behind quote |
| `checklist` | `image-text` | Left 40% image \| Right 60% checklist |
| `title` | `title` (keep) | Subtle background image at 10% opacity |
| `closing` | `closing` (keep) | Subtle background image at 10% opacity |

**CRITICAL**: When layout switches to `image-text`, the text content MUST be condensed to fit the reduced text area (50–60% of slide width). Apply Step 2.9 content limits for `image-text` layout.

#### 4.5 Generation Paths

```
Priority 1 — NanoBanana Pro (Gemini CLI Extension):
  CLI:  /generate "prompt" --count=1 --styles="photorealistic" --preview
  Output: ./nanobanana-output/*.png

Priority 2 — Gemini API Direct (fallback):
  Model:    gemini-2.5-flash-image
  Endpoint: POST /v1beta/models/gemini-2.5-flash-image:generateContent
  Response: base64 PNG inline data → decode → save to file
```

#### 4.6 Environment-Specific Execution

| Environment | Execution Method |
|-------------|-----------------|
| OpenCode | `task(run_in_background=true)` → Gemini Pro background task — fire ALL image tasks in parallel |
| Cursor | Direct execution in main thread (full Gemini Pro model) — sequential |

#### 4.7 Image Quality Requirements

| Item | Standard |
|------|----------|
| Resolution | 1920 × 1080 px |
| Format | PNG (JPEG acceptable) |
| File size | Under 5MB |
| Style | Professional, clean, conceptual |
| Colors | Visual harmony with slide palette (#FFFFFF background, grayscale tones) |
| Prohibited | No text, logos, watermarks, busy backgrounds |
| Save location | `{original_filename}_pptx/assets/ai-img-{nn}-{label}.png` |

#### 4.8 Failure Handling

If image generation fails after exhausting all paths (NanoBanana Pro + Gemini API):
1. **Do NOT leave the slide without a visual** — use a minimal geometric placeholder
2. Log a warning: `"[WARNING] Image generation failed for slide {N} — using geometric placeholder"`
3. Generate a simple SVG-based geometric shape (circle, hexagon, or abstract lines) in the slide's accent color as a minimal visual anchor
4. **Never leave a content slide as pure text**

### Step 5: HTML Slide Generation

- Generate each slide as an individual HTML file
- Apply design rules (see Section 2)
- 16:9, 1920 × 1080 px (Full HD)
- CSS inline applied
- Pretendard font (with fallback chain)

### Step 6: PPTX Conversion

- Leverage `document-skills/pptx`'s `html2pptx.js`
- HTML → PPTX conversion
- Tables generated natively via PptxGenJS table API
- AI-generated images inserted via `<img>` tags

### Step 7: Layout Integrity Verification (ZERO TOLERANCE — SLIDES MUST NEVER OVERFLOW)

> **The layout system must NEVER break. Text overflow is a CRITICAL failure.**
> If Step 2.9 (Content Volume Pre-Check) worked correctly, overflow should be impossible.
> This step is the final safety net — NOT the primary defense.

#### 7.1 Safe Area Dimensions (Pixel-Based)

All content must fit within these absolute boundaries:

```
Slide: 1920 × 1080 px
Margins: 0.7" = 67.2px (round to 68px) on all sides

┌──────────────── 1920px ────────────────┐
│ 68px margin                            │
│  ┌──────────── 1784px ──────────────┐  │
│  │ TITLE AREA                       │  │  ← Top 68px to 188px (120px height)
│  │ 1784 × 120 px                    │  │
│  ├──────────────────────────────────┤  │
│  │ 32px gap                         │  │
│  ├──────────────────────────────────┤  │
│  │ BODY AREA                        │  │  ← 220px to 944px (724px height)
│  │ 1784 × 724 px                    │  │
│  │                                  │  │
│  │                                  │  │
│  ├──────────────────────────────────┤  │
│  │ FOOTER (slide number, caption)   │  │  ← 952px to 1012px (60px height)
│  │ 1784 × 60 px                     │  │
│  └──────────────────────────────────┘  │
│                                  68px  │
└────────────────────────────────────────┘
```

#### 7.2 Maximum Renderable Text Per Area

Based on Pretendard font metrics at standard sizes:

| Area | Dimensions | At 18pt (body) | At 16pt (min body) | At 24pt (title) |
|------|-----------|:--------------:|:------------------:|:---------------:|
| Title | 1784 × 120px | ~5 lines | ~6 lines | **~3 lines** |
| Body (full) | 1784 × 724px | ~25 lines | ~29 lines | — |
| Body (image-text, text side) | 860 × 724px | ~25 lines (narrow) | ~29 lines | — |
| Body (image-text, text side, Korean) | 860 × 724px | ~20 lines | ~23 lines | — |

**Character estimates per line (Pretendard):**
- English at 18pt: ~70 characters per line (1784px width)
- Korean at 18pt: ~45 characters per line (wider glyphs)
- English at 16pt: ~80 characters per line
- Korean at 16pt: ~52 characters per line

#### 7.3 Verification Checklist (Auto-Run After EACH Slide)

| # | Verification Item | On Failure | Max Attempts |
|---|-------------------|-----------|:------------:|
| 1 | **Text within body area** (y + height ≤ 944px) | Font reduction cascade | 3 |
| 2 | **Title within title area** (y + height ≤ 188px) | Truncate title to 1 line | 1 |
| 3 | **No element overlap** (bounding box intersection = 0) | Reposition → regenerate | 3 |
| 4 | **Margins respected** (all content x ≥ 68px, x+w ≤ 1852px) | Reposition | 1 |
| 5 | **Image ratio preserved** (aspect ratio distortion < 2%) | Restore original ratio | 1 |
| 6 | **Grid alignment** (coordinates snap to 8px grid) | Coordinate correction | 1 |

#### 7.4 Font Reduction Cascade (Last Resort Only)

> If Step 2.9 pre-check worked, this cascade should RARELY trigger.

```
Step 1: Body 18pt → 16pt (ABSOLUTE minimum — NEVER below 16pt)
Step 2: Sub-header 20pt → 18pt
Step 3: Reduce bullet count (4 → 3 → 2)
Step 4: Condense text (remove secondary details, keep keywords only)
Step 5: Force slide split (create continuation slide)
```

- Title (24pt) and caption (12pt) are **NEVER reduced**
- **All chart/infographic content text is NEVER reduced below 16px**
- Max **3 regeneration attempts**. After 3 failures → adopt best result + **log critical warning**

#### 7.5 The Golden Rule

```
IF text overflows the slide:
  THE SLIDE HAS TOO MUCH TEXT. Period.
  Go back to Step 2.9 and distill the content further.
  Reducing font size to fit more text is NEVER the answer.
  A slide with 16pt text crammed wall-to-wall is worse than overflow.
```

### Step 8: Output

> **The final output is a static PDF.** No animations, transitions, buttons, or interactive elements needed.

- Create a dedicated folder in the same path as the original MD file
- Output versioned files:

```
{original_filename}_pptx/
├── v{M}.{m}_{original_filename}.pptx    ← Editable
├── v{M}.{m}_{original_filename}.pdf     ← Sharing/presentation (primary output)
└── assets/                               ← Generated charts/images
```

- **PDF is the primary presentation output** — all visual elements are designed for static rendering
- No animations, slide transitions, click events, buttons, or interactive elements are generated

---

## 2) Design Rules Summary

> **For detailed specs, see `docs/design-spec.md`. Below is a key summary.**

### Color Palette

| Role | HEX | Usage |
|------|-----|-------|
| Background | `#FFFFFF` | Slide background |
| Text | `#1A1A1A` | All default text |
| Accent | `#D94F4F` | **Word-level** Bold only, **1 per slide** |
| Subtext | `#555555` | Supplementary text, 2nd-level bullets |
| Caption | `#888888` | Footnotes, data sources |
| Divider Background | `#F5F5F5` | AI Hint blocks, code block outer background |
| Section Background | `#2C2C2C` | section-divider slides only |
| Code Background | `#1E1E1E` | Code area interior |

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Main Title | Pretendard | ExtraBold (800) | 36pt |
| Section Header | Pretendard | Bold (700) | 28pt |
| Slide Title | Pretendard | Bold (700) | 24pt |
| Body | Pretendard | Regular (400) | 18pt (min 16pt) |
| Sub-header | Pretendard | SemiBold (600) | 20pt |
| Caption | Pretendard | Light (300) | 12pt |
| Code | JetBrains Mono | Regular | 13pt |
| **Chart Content** | Pretendard | Regular–Bold | **Min 16px** |

> **Chart/Infographic 16px minimum rule**: All content text within charts — labels, legends, dates, values, descriptions — must be **16px or larger**. Only exceptions: slide numbers (10pt) and captions/footnotes (12pt).

**Font fallback**: Pretendard → Apple SD Gothic Neo → Malgun Gothic → Noto Sans KR → sans-serif

### Layout Specs

- **Aspect ratio**: 16:9 fixed (13.333" × 7.5")
- **Resolution**: 1920 × 1080 px
- **Margins**: Minimum 0.7" (all sides)
- **Title area**: Fixed at top 15%
- **Body area**: Top 20% to bottom 90%

### Accent Color Usage Rules

- `#D94F4F` (Soft Red) used **at the word level only**
- Must be paired with Bold
- **Max 1 per slide**
- Prohibited on titles/sentences/backgrounds/borders

### Anti-Vibe-Coding Rules

> Exclude typical AI-generated dashboard/SaaS styles. Details: `docs/design-spec.md` Section 1.1

- `border-radius` max **2px** (rounded cards prohibited)
- Card backgrounds are `#FFFFFF` (gray backgrounds like FAFAFA prohibited)
- `text-transform: uppercase` + excessive `letter-spacing` prohibited
- Decorative `::before`/`::after` bars prohibited
- Emoji/icon background boxes prohibited
- Text color below `#999999` prohibited (minimum `#888888`; body text `#555555` or darker)

### Output Language Rule

> The generated PPT output follows the source Markdown's language.
> Korean MD → Korean slides, English MD → English slides, Japanese MD → Japanese slides.
> This skill does NOT translate content — it preserves the original language as-is.

### Slide Numbers

- All slides (except title) show page numbers at bottom-right
- Format: `{current}/{total}` (e.g., `3/24`)
- Font: Pretendard Light, 10pt, `#888888`
- Position: Bottom-right, within margins

### Slide Flow Rules

- **MAX-2-TEXT**: After 2 consecutive text-only slides, the next must be a visual slide
- **FRONT-VISUAL**: At least 1 infographic in the first 30% of total slides
- **AUTO-APPENDIX**: Detailed tables/checklists auto-separated to appendix; only summaries in main body

### CTA Closing Slide

- Final slide includes **specific call-to-action (CTA)** instead of just "Thank You"
- Content: 1-line key message + 2–3 Next Steps + contact/links
- Example: "Next Steps: 1) Start pilot project 2) Team onboarding 3) Performance review (2 weeks)"

---

## 3) Image Generation Pipeline

> **MANDATORY for all slides without visual content.**
> Every content slide must have a visual element. Text-only slides are prohibited.
> Charts/diagrams/icons use existing HTML/SVG pipeline — AI generation covers remaining visual gaps.

### Scope

| Target | AI Generation | Existing Pipeline |
|--------|:---:|:---:|
| **Slides without any visual** | **✅ MANDATORY** | — |
| Photorealistic photos/illustrations | ✅ | — |
| Charts/Infographics | — | HTML (Section 15 of design-spec) |
| Diagrams/Flowcharts | — | HTML/SVG |
| Icons/Decorations | — | SVG/Emoji |

### Image Prompt Source

Each generated image prompt is derived from the slide's `primary_keyword` (extracted in Step 2.3):
- Convert `primary_keyword` → one-line visual concept
- Add: `"professional"`, `"clean background"`, `"high resolution"`, `"no text, no logos, no watermarks"`
- Result: A professional conceptual image that visually represents the slide's core message

### Quality Criteria

| Item | Standard |
|------|----------|
| Resolution | 1920 × 1080 px |
| Format | PNG (JPEG acceptable) |
| File size | Under 5MB |
| Style | Professional, clean, conceptual (derived from `primary_keyword`) |
| Colors | Visual harmony with slide palette |
| Prohibited | No text, logos, or watermarks |
| Save location | `{filename}_pptx/assets/ai-img-{nn}-{label}.png` |

### Failure Handling

If AI image generation fails → use minimal SVG geometric placeholder. **Never leave a slide without visuals.**

---

## 4) Layout Integrity (NEVER BREAK)

> **The layout system must never break.**

### Absolute Prohibitions

| Rule | On Violation |
|------|-------------|
| No overflow | Font reduction or split |
| No overlap | Reposition or split |
| No alignment drift | Grid realignment |
| No title position changes | Force coordinate restoration |
| No margin violation | Content reduction/split |

### Element Collision Priority

```
1. Title area (always fixed, never moves)
2. Margins 0.7" (inviolable)
3. Body text (priority over images)
4. Images/Charts (can be scaled down)
5. Captions/Sources (can be omitted first)
```

---

## 5) Slide Layout Types (23 Types)

| Layout | Purpose | Alignment | Background |
|--------|---------|-----------|------------|
| `title` | Document title | Center | `#FFFFFF` |
| `executive-summary` | Key KPI/message summary | Center | `#FFFFFF` |
| `section-divider` | H2 section start (2+ content slides only) | Center | `#2C2C2C` (inverted) |
| `text-body` | General text | Left | `#FFFFFF` |
| `bullet-list` | Bullet/numbered list | Left | `#FFFFFF` |
| `table` | Tabular data | Left | `#FFFFFF` |
| `code` | Code block | Left | `#1E1E1E` (code area only) |
| `image` | Image-focused | Center | `#FFFFFF` |
| `image-text` | Image + description | 2-column (60:40) | `#FFFFFF` |
| `chart` | Data visualization | Center | `#FFFFFF` |
| `quote` | Blockquote | Center | `#FFFFFF` |
| `ai-hint` | AI Hint block | Left | `#F5F5F5` |
| `checklist` | Task list | Left | `#FFFFFF` |
| `kpi-cards` | Key metric emphasis | Center | `#FFFFFF` |
| `bar-chart` | Numeric comparison | Left | `#FFFFFF` |
| `donut-chart` | Proportion distribution | Center | `#FFFFFF` |
| `process-flow` | Sequential process | Center | `#FFFFFF` |
| `timeline` | Chronological events | Center | `#FFFFFF` |
| `comparison` | Comparison (vs) | Left | `#FFFFFF` |
| `icon-grid` | Category listing | Center | `#FFFFFF` |
| `funnel` | Stage-based reduction | Center | `#FFFFFF` |
| `appendix-divider` | Appendix section start | Center | `#2C2C2C` (inverted) |
| `closing` | CTA final slide | Center | `#FFFFFF` |

---

## 5.1) Future Improvements (v1.1 Roadmap)

> Items agreed upon in a 6-expert design review session, scheduled for v1.1 implementation.

| Item | Description | Consensus Level |
|------|-------------|----------------|
| `--audience` parameter | `executive` (12 slides, 3 bullets, no code) / `team` (default, full detail) mode branching | 6/6 agreed |
| ~~Speaker Notes generation~~ | ~~Per-slide presentation coaching notes~~ — Unnecessary for PDF output, excluded | — |
| CSS Custom Properties | Define colors/fonts/spacing as CSS variables for easier theme switching | 4/6 agreed |
| Hero Metric Layout | Center a single dramatic number at 120px — static impact slide | 3/6 agreed |
| Slide Complexity Score | Auto-calculate cognitive complexity (word count, jargon density, data points) | 3/6 agreed |

---

## 6) Dependencies & Prerequisites

| Dependency | Role | Required |
|-----------|------|----------|
| `document-skills/pptx` | html2pptx rendering engine, PptxGenJS API | **Required** |
| `NanoBanana Pro` | Gemini CLI Extension — AI image generation (mandatory for visual coverage) | **Required** |
| `Gemini 2.5 Flash Image API` | NanoBanana Pro fallback — direct API call | **Fallback** |
| `pptxgenjs` | PowerPoint file generation library | **Required** (npm) |
| `playwright` | HTML rendering → Image/PPTX conversion | **Required** (npm) |
| `sharp` | Image post-processing (rasterization) | **Required** (npm) |

---

## 7) Validation Checklist

Verify the following after each slide generation:

### Keyword Extraction (Step 2.3)
- [ ] Every section has a `primary_keyword` extracted
- [ ] `accent_candidate` identified for each slide (1 per slide)
- [ ] Action title derived from `primary_keyword` (complete sentence ≤15 words)
- [ ] No slide exists without keyword focus (raw text dump prohibited)

### Content Distillation (Step 2.9)
- [ ] Total slide text ≤ 50 words (EN) / 35 words (KR)
- [ ] Bullet count ≤ 3 (max 4 only when necessary)
- [ ] Every bullet ≤ 7 words — keyword fragment, NOT sentence
- [ ] No full sentences in body text (noun-phrase style only)
- [ ] No filler words ("In order to", "It is important that", etc.)
- [ ] Slide readable in ≤ 3 seconds
- [ ] CJK multiplier applied (0.7× for Korean)

### Colors
- [ ] 3 or fewer colors used (background + text + accent)
- [ ] Accent color (`#D94F4F`) exactly 1 per slide (on `accent_candidate` word)
- [ ] WCAG AA contrast ratio met

### Typography
- [ ] Title is an action title (complete sentence with conclusion, from `primary_keyword`)
- [ ] Body minimum 16pt
- [ ] Max 3 font sizes per slide
- [ ] Bold used max 2 places per slide (`accent_candidate` + 1 `supporting_keyword`)

### Structure
- [ ] 1–2 topics per slide
- [ ] 4 or fewer bullets (optimal 3)
- [ ] All numbers/data include source attribution
- [ ] Margins 0.7" or more maintained
- [ ] Slide numbers displayed (except title)

### Readability
- [ ] Understandable within 60 seconds
- [ ] No text clipping/overlap
- [ ] Images minimum 1280x720px

### Text Style
- [ ] Bullet-point style (no sentence-form text)
- [ ] Numeric/quantitative expressions prioritized
- [ ] Parallel structure maintained

### Visual Coverage (Step 4 — MANDATORY)
- [ ] **Every content slide has a visual element** (image, chart, table, code, or AI-generated image)
- [ ] **0% text-only content slides** (section-divider excluded)
- [ ] AI-generated images derived from slide's `primary_keyword`
- [ ] Layout adapted when image added (`text-body` → `image-text`, etc.)
- [ ] Text condensed to fit reduced area when layout switches

### Charts/Data Visualization
- [ ] HTML rendering → Playwright screenshot method
- [ ] Resolution 1920x1080px or higher
- [ ] Chart font: Pretendard
- [ ] Grayscale base, accent limited to 1 color
- [ ] Data label/legend readability
- [ ] Pattern/label pairing (no color-only differentiation)
- [ ] All chart content text **minimum 16px**
- [ ] No `text-transform: uppercase`
- [ ] `border-radius` max 2px
- [ ] Card/cell background `#FFFFFF` (no gray backgrounds)
- [ ] No emoji/icon background boxes
- [ ] No decorative `::before`/`::after` bars

### Layout Integrity (Step 7 — ZERO TOLERANCE)
- [ ] All elements within safe area (68px margins = 0.7")
- [ ] All text within body area (y + height ≤ 944px)
- [ ] Title within title area (y + height ≤ 188px)
- [ ] No element overlap (bounding box intersection = 0)
- [ ] Title position identical across slides
- [ ] **No text overflow (CRITICAL — must be 0 occurrences)**
- [ ] No image ratio distortion (< 2% deviation)
- [ ] Grid alignment consistency (8px grid snap)

### AI Image Generation
- [ ] **ALL non-visual slides received generated images**
- [ ] Resolution 1920x1080px or higher
- [ ] PNG format
- [ ] Under 5MB
- [ ] Palette harmony verified
- [ ] No text/logos/watermarks
- [ ] Properly saved in `assets/` directory

### Slide Flow
- [ ] Executive Summary slide present (10+ slide decks)
- [ ] Text-only slides max 2 consecutive (MAX-2-TEXT rule)
- [ ] At least 1 infographic in first 30% (FRONT-VISUAL rule)
- [ ] Detailed tables/checklists separated to appendix (AUTO-APPENDIX rule)
- [ ] Closing slide includes CTA (call-to-action)

### Visualization Infographics
- [ ] Data pattern auto-detection accuracy (false positive rate under 5%)
- [ ] No information loss after visualization conversion
- [ ] CSS infographic Playwright PDF rendering works correctly
- [ ] print-color-adjust: exact applied
- [ ] Infographic font palette compliance (background #FFF, text #1A1A1A)
- [ ] conic-gradient (donut), flexbox (process), CSS Grid (KPI/icon) rendering correctly
- [ ] Accent color #D94F4F used max 1 per slide
- [ ] All infographics within 1720×760px content area

---

## 8) Parallel Execution Optimization

> **For LLMs that support parallel sub-agent execution** (e.g., OpenCode with `task(run_in_background=true)`),
> the workflow should be parallelized across independent tasks to minimize total conversion time.

### 8.1 Parallel Wave Architecture

The conversion pipeline is organized into **5 waves**. Tasks within each wave execute in parallel; waves execute sequentially.

```
Wave 1 — Sequential (fast, <1s)
├── Step 0: Environment Detection
├── Step 1: Input Reception
├── Step 2: MD Parsing
├── Step 2.3: Core Keyword Extraction (CRITICAL)
├── Step 2.5: Visual Content Detection
├── Step 2.7: Executive Summary Generation
├── Step 2.8: Slide Flow Optimization
├── Step 2.9: Content Volume Pre-Check (OVERFLOW PREVENTION)
└── Step 3: Slide Mapping

Wave 2 — PARALLEL (main bottleneck, optimize here)
├── [Background] AI Image Generation — MANDATORY for ALL non-visual slides (NanoBanana Pro / Gemini API)
├── [Background] Chart HTML Generation (templates/charts/ → render_chart())
├── [Background] Chart Screenshot Capture (Playwright batch)
└── [Foreground] Non-chart Slide HTML Generation

Wave 3 — PARALLEL (asset collection)
├── Collect AI image results (background_output()) — expect MORE images now (mandatory coverage)
├── Collect chart screenshots
└── Post-process images (Sharp resize/optimize if needed)

Wave 4 — Sequential (assembly)
├── Assemble all slide HTMLs with final assets
├── Adapt layouts for slides receiving AI images (text-body → image-text, etc.)
├── PPTX Conversion (html2pptx.js)
└── PDF Generation (Playwright page.pdf())

Wave 5 — Sequential (verification)
├── Layout Integrity Verification (Step 7 — pixel-based safe area checks)
├── Visual Coverage Audit (confirm 0% text-only content slides)
├── Output file writing (versioned)
└── Completion report
```

### 8.2 Wave 2 Parallelization Detail

Wave 2 is the primary bottleneck. The following tasks are **fully independent** and should run concurrently:

| Task | Agent/Method | Blocking? | Typical Duration |
|------|-------------|-----------|-----------------|
| AI Image Generation | `task(run_in_background=true)` — Gemini Pro | No (background) | 5–15s per image |
| Chart HTML Rendering | `render_chart(type, data)` — Python templates | No (instant) | <100ms per chart |
| Chart Screenshots | Playwright batch — one browser, multiple pages | No (background) | 1–3s per chart |
| Slide HTML Generation | Sequential HTML file writes | Yes (foreground) | <1s per slide |

**Optimal execution pattern (OpenCode):**

```python
# Wave 2: Fire all independent tasks in parallel

# 1. AI Images — background (longest task, start first)
image_tasks = []
for slide in slides_needing_images:
    tid = task(
        run_in_background=True,
        prompt=f"Generate photorealistic image: {slide.image_prompt}",
        # ... NanoBanana Pro / Gemini API
    )
    image_tasks.append(tid)

# 2. Chart rendering — instant, no background needed
chart_htmls = {}
for slide in slides_needing_charts:
    chart_htmls[slide.id] = render_chart(slide.chart_type, slide.chart_data)

# 3. Chart screenshots — batch in single Playwright instance
# Open one browser, create multiple pages in parallel
chart_screenshots = batch_screenshot(chart_htmls)  # Playwright

# 4. Non-chart slide HTMLs — generate while charts render
slide_htmls = generate_slide_htmls(mapped_slides)

# Wave 3: Collect background results
for tid in image_tasks:
    result = background_output(task_id=tid)
    # Insert into corresponding slide
```

### 8.3 Playwright Batch Screenshot Optimization

When multiple charts need screenshots, use a **single browser instance** with concurrent pages:

```javascript
// GOOD: Single browser, multiple pages (parallel)
const browser = await chromium.launch();
const screenshots = await Promise.all(
  chartHtmls.map(async (html, i) => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.setContent(html, { waitUntil: 'networkidle' });
    const buf = await page.screenshot({ type: 'png' });
    await page.close();
    return { id: i, buffer: buf };
  })
);
await browser.close();

// BAD: Sequential — one page at a time
for (const html of chartHtmls) {
  const page = await browser.newPage();
  // ... screenshot one by one (N × slower)
}
```

### 8.4 Parallelization Rules

| Rule | Description |
|------|-------------|
| **Start longest tasks first** | AI image generation takes 5–15s — always fire first |
| **Batch Playwright ops** | One `chromium.launch()`, multiple `newPage()` calls |
| **Never block on images** | Generate all slide HTMLs while images render in background |
| **Collect results lazily** | Only call `background_output()` when results are actually needed (Wave 3) |
| **Fail independently** | If one chart screenshot fails, others continue. Retry failed ones only |
| **Resource limits** | Max 8 concurrent Playwright pages (memory constraint) |
| **Cursor fallback** | In non-OpenCode environments, execute sequentially — no `task()` available |

### 8.5 Expected Performance Gains

| Document Size | Sequential | Parallel (OpenCode) | Speedup |
|--------------|-----------|-------------------|---------|
| Small (<50 lines, 0 images) | ~15s | ~10s | 1.5× |
| Medium (50–300 lines, 2–3 images) | ~45s | ~20s | 2.2× |
| Large (300+ lines, 5+ images) | ~120s | ~35s | 3.4× |

> **Note**: Speedup is primarily from overlapping AI image generation with slide HTML generation. Chart rendering is already fast (<100ms) and contributes minimal savings.
