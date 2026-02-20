# MaraudersPPT Skill

A multi-platform Agent Skill (optimized for Gemini 3.1 Pro) that automatically converts Markdown documents into presentation-quality slides (.pdf).
Fully supports execution across Cursor, Claude Code, OpenCode, and Antigravity environments.
Preserves the original Markdown's structure, images, and data while generating a presentation-ready PDF.

> **PDF is the primary presentation output** — all visual elements are designed for static rendering.
> No animations, transitions, buttons, or interactive elements are generated.

---

## Installation

### Claude Code (OpenCode)

```bash
# From your project root
claude mcp add-skill /path/to/MaraudersPPT-Skill
```

Or manually copy the skill directory and reference `SKILL.md` in your configuration.

### Cursor

Clone or copy this repository into your project's `.cursor/skills/` directory:

```bash
# From your project root
cp -r /path/to/MaraudersPPT-Skill .cursor/skills/maraudersppt-skill
```

Cursor will automatically detect the skill from `.cursor/skills/maraudersppt-skill/SKILL.md`.

### Dependencies

After installation, install the required npm packages:

```bash
npm install    # installs playwright, sharp
npx playwright install chromium
```

---

## Invocation

> **This skill does NOT activate automatically.**
> You must explicitly invoke it with `MaraudersMD2PPT`.

```
MaraudersMD2PPT docs/prd.md
MaraudersMD2PPT convert this document
MaraudersMD2PPT run
```

Without the `MaraudersMD2PPT` keyword, requests like "Make this into a PPT" or "Convert to slides" will **never** activate this skill.

---

## Key Features

| Feature                         | Description                                                                                                 |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Auto Slide Mapping**          | H1 → Title, H2 → Section divider, H3 → Sub-header — structure preserved                                     |
| **23 Layout Types**             | Dedicated layouts for text, tables, code, images, lists, KPIs, charts, timelines, etc.                      |
| **Infographic Auto-Conversion** | Detects numeric, comparison, and sequential data patterns → auto-maps to 8 chart types (AGGRESSIVE mode)    |
| **Parallel Execution**          | 6-wave parallel pipeline — AI image gen, chart rendering, and slide HTML gen run concurrently               |
| **Executive Summary**           | Auto-generates a key KPI summary slide right after the title for decks with 10+ slides                      |
| **CTA Closing**                 | Final slide with key message + Next Steps + contact info                                                    |
| **AI Hint Special Handling**    | `[AI RULE]`, `[AI DECISION]`, `[AI NOTE]`, `[AI CONTEXT]` highlighted slides                                |
| **Design Token System**         | 3-tier token architecture (primitive/semantic/component) with CSS custom properties and theme resolution    |
| **5 Theme Packs**               | consulting_minimal, modern_editorial, product_pitch, dark_executive, academic_clean                         |
| **Layout Rhythm Engine**        | 69 layout variants (23 types × 3) with scoring algorithm that prevents visual monotony                      |
| **Editorial Details**           | Running headers, folios, source citations, exhibit labels, dividers — consulting-grade paratextual elements |
| **Human-Likeness Scoring**      | Automated H-score (0.0–1.0) across 5 dimensions with 0.80 pass threshold                                    |
| **Anti-AI Design Lint**         | NO1–NO6 rules block glassmorphism, large radius, deep shadows, neon glow, multi-hue, dashboard UI           |
| **Chart Annotations**           | Insight captions and callout overlays for data-driven storytelling on chart slides                          |
| **Anti-Vibe-Coding Design**     | No rounded cards, no gray backgrounds, no AI dashboard aesthetics — McKinsey/BCG quality                    |
| **16px Minimum Font**           | All chart/infographic content text ≥ 16px (exceptions: slide numbers 10pt, captions 12pt)                   |
| **Mandatory Original Images**   | All `![alt](path)` images from the MD file are inserted into slides (never omitted)                         |
| **AI Image Generation**         | Auto-generates photorealistic content images via Cursor native image gen / OpenCode background tasks        |
| **Persistent Image Reuse**      | Generated images are cached per page key and reused across reruns unless user explicitly requests refresh   |
| **Layout Integrity**            | Auto-validates overflow/overlap/margin violations + up to 3 regeneration attempts                           |
| **Slide Flow Optimization**     | MAX-2-TEXT, FRONT-VISUAL, AUTO-APPENDIX rules applied                                                       |
| **Version Control**             | Each generation outputs `v{M}.{m}_filename.pdf`                                                             |
| **Low-Token File Pipeline**     | Intermediate JSON artifacts are written to disk (`.pipeline/`) to avoid large stdin/stdout payloads         |
| **Cross-Platform**              | Works on macOS, Windows, and Linux — no OS-specific dependencies                                            |
| **Korean/CJK Full Support**     | Pretendard font-based with full fallback chain (Apple SD Gothic Neo → Malgun Gothic → Noto Sans KR)         |
| **Input Contract**              | Audience, goal, and time constraints captured upfront for targeted content generation                       |
| **Section Cards**               | Semantic analysis of content structure with visual blueprint mapping                                        |
| **7-Role Narrative Taxonomy**   | Structured narrative roles (Context, Problem, Solution, Evidence, Impact, Action, Closing)                  |
| **Visual Blueprint**            | Pre-generation layout planning with role-to-slide mapping                                                   |
| **Dual Output**                 | Generates both presentation deck and detailed appendix for comprehensive coverage                           |
| **Image Manifest**              | Cache system for generated images with reuse tracking and refresh control                                   |

---

## Design Philosophy

- **Designed for PDF output** — no animations, transitions, or interactive elements
- **Theme-driven styling** — CSS custom properties with `var(--token, fallback)` for backward-compatible theming
- **Neutral + 1 accent** color principle — restrained palette, no multi-hue chaos
- **1–2 topics per slide**, bullet-point and quantitative style (max 4 bullets, optimal 3)
- 16:9 aspect ratio, 1920×1080px high resolution
- 8px grid-based consistent spacing system
- **Layout rhythm** — variant selection algorithm prevents consecutive same-feel slides
- **Editorial design, not decoration** — thin dividers, captions, exhibit labels, running headers instead of blobs/glows/gradients
- **Original MD images are mandatory** — `![alt](path)` images must never be omitted

---

## Output Language Rule

> The generated presentation PDF follows the source Markdown's language.
> Korean MD → Korean slides, English MD → English slides, Japanese MD → Japanese slides.
> This skill does NOT translate content — it preserves the original language as-is.

---

## Execution Environments (Optimized for Gemini 3.1 Pro)

This skill is heavily optimized for **Gemini 3.1 Pro**, ensuring accurate YAML parsing, reliable layout integrity, and zero token leakage.

| Environment                   | AI Image Generation                    | PDF Rendering             |
| ----------------------------- | -------------------------------------- | ------------------------- |
| **Cursor**                    | Native image gen (built-in agent tool) | Playwright-based renderer |
| **Claude Code**               | Standard Markdown-to-PDF generation    | Playwright-based renderer |
| **OpenCode**                  | Background task via `task()`           | Playwright-based renderer |
| **Antigravity**               | Native image gen (built-in agent tool) | Playwright-based renderer |

- **Cursor / Antigravity**: Uses built-in image generation agent tool — no model switch needed.
- **OpenCode**: Image generation runs as a background task via `task(run_in_background=true)`.
- **All environments**: Pipeline proceeds immediately with zero confirmation prompts.

---

## Output Structure

```
docs/
├── prd.md                              ← Original Markdown
└── prd_slides/                         ← Auto-generated folder
    ├── v1.0_prd.pdf                    ← Presentation PDF (primary output)
    ├── v1.0_prd_appendix.pdf           ← Appendix (cut/low-stakes sections)
    ├── .coverage-report.json           ← Content routing audit
    └── assets/                         ← All generated images + manifest
        ├── image-manifest.json         ← Image cache + full metadata
        ├── md-img-02-architecture.png  ← Priority 1: copied from source MD
        ├── chart-05-throughput.png     ← Priority 2: chart/diagram screenshot
        └── ai-img-07-reliability.png   ← Priority 3: AI-generated image
```

### Image Manifest (Persistent Reuse)

Every generated image is recorded in `assets/image-manifest.json`:

| Field             | Purpose                                                               |
| ----------------- | --------------------------------------------------------------------- |
| `type`            | `ai-generated` / `chart` / `original-md` / `html-concept`             |
| `prompt`          | Exact prompt used to generate AI images (reproducibility)             |
| `generator`       | Tool that produced the image (`cursor-native`, `playwright-chart`, …) |
| `visual_intent`   | Layout role the image fulfills                                        |
| `content_hash`    | Cache key for AI images (skip regeneration on match)                  |
| `data_hash`       | Cache key for charts                                                  |
| `file_size_bytes` | Integrity check (0 = stale, triggers regeneration)                    |

- Same hash on re-run → reuse existing image, no regeneration
- Explicit refresh: `--refresh=all`, `--refresh=slide:7`, `--refresh=type:ai-generated`
- Images are never deleted by the pipeline

---

## Chart Templates

The `templates/charts/` Python modules generate HTML for 8 infographic types by simply passing data:

```python
from templates.charts import render_chart

# KPI Cards
html = render_chart("kpi_cards", [
    {"label": "Success Rate", "value": "95%", "delta": "▲ +4%", "accent": True},
    {"label": "Accuracy", "value": "100%"},
])

# Horizontal Bar Chart
html = render_chart("bar_chart", [
    {"label": "Q1", "value": 95, "display": "95%", "max": True},
    {"label": "Q2", "value": 78, "display": "78%"},
])
```

| Type           | Purpose                                         |
| -------------- | ----------------------------------------------- |
| `kpi_cards`    | Compare 1–4 key performance indicators          |
| `bar_chart`    | Numeric comparison across items                 |
| `donut_chart`  | Proportion/share visualization                  |
| `process_flow` | Step-based pipeline (3–8 steps)                 |
| `timeline`     | Release roadmap/milestones                      |
| `comparison`   | Side-by-side contrast (Before/After)            |
| `icon_grid`    | Non-numeric item classification (2x2, 2x3, 3x2) |
| `funnel`       | Stage-based drop-off pipeline                   |

---

## Dependencies

| Package                 | Role                                                         |       Required       |
| ----------------------- | ------------------------------------------------------------ | :------------------: |
| `playwright`            | HTML rendering / PDF generation / chart screenshots          |     **Required**     |
| `sharp`                 | Image post-processing (rasterization)                        |     **Required**     |
| Native image gen        | Built-in agent tool — Cursor / Antigravity (Nano Banana Pro) | Cursor / Antigravity |
| `task()` background gen | OpenCode image generation via background agent               |    OpenCode only     |

---

## Project Structure

```
MaraudersPPT-Skill/
├── README.md                      ← This file
├── SKILL.md                       ← Skill workflow, layouts, checklist (v2.1.0)
├── LICENSE                        ← MIT License
├── package.json                   ← npm dependencies (playwright, sharp)
├── .gitignore                     ← Git ignore rules
├── design/                        ← Design system Python package
│   ├── __init__.py                ← Public API (33 exports)
│   ├── tokens.py                  ← 3-tier design token dictionary
│   ├── vars.py                    ← Token path → CSS custom property mapping
│   ├── resolve.py                 ← ThemeResolver: tokens + theme → :root CSS
│   ├── themes.py                  ← 5 theme packs
│   ├── variants.py                ← 23 layout types × 3 variants (69 total)
│   ├── variant_select.py          ← Rhythm-based variant scoring algorithm
│   ├── editorial.py               ← Running headers, folios, citations, labels, dividers
│   ├── image_treatment.py         ← 4 image treatment strategies
│   └── lint.py                    ← Static design lint + human-likeness scoring
├── references/                    ← Detailed reference docs (progressive disclosure)
│   ├── design-system.md           ← Token/theme/variant/lint architecture reference
│   ├── insight-extraction.md      ← Section Card schema, insight extraction algorithm
│   ├── content-distillation.md    ← Slide text limits & distillation algorithm
│   ├── image-generation.md        ← Visual coverage audit & prompt derivation
│   ├── layout-integrity.md        ← Safe areas, font metrics, verification
│   ├── parallel-execution.md      ← 6-wave architecture & performance
│   ├── visual-qa.md               ← Post-generation visual inspection + H-score
│   ├── cognitive-layout.md        ← Cognitive science-based layout rules (eye-tracking, Gestalt)
│   └── svg-components.md          ← Inline SVG component library for charts & diagrams
├── templates/
│   ├── charts/                    ← 8 infographic Python templates
│   │   ├── __init__.py            ← render_chart(type, data) dispatcher
│   │   ├── base.py                ← Shared CSS & utilities (tokenized)
│   │   ├── annotations.py         ← Chart insight captions & callout overlays
│   │   ├── kpi_cards.py           ← KPI card grid
│   │   ├── bar_chart.py           ← Horizontal bar chart
│   │   ├── donut_chart.py         ← Donut chart
│   │   ├── process_flow.py        ← Process flow
│   │   ├── timeline.py            ← Timeline
│   │   ├── comparison.py          ← Side-by-side comparison
│   │   ├── icon_grid.py           ← Icon grid
│   │   └── funnel.py              ← Funnel chart
└── docs/
    ├── design-spec.md             ← Design spec (colors, typography, tokens, themes, variants)
    └── prd-md-to-pptx-skill.md    ← Product Requirements Document (PRD)
```

---

## Documentation

| Document                                                         | Contents                                                                                       |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`SKILL.md`](./SKILL.md)                                         | Skill workflow (Phases 0-5 + 1.5), 23 layouts, design system integration, validation checklist |
| [`docs/design-spec.md`](./docs/design-spec.md)                   | Color palette, typography, 8px grid, layout specs, tokens, themes, variants, editorial         |
| [`docs/prd-md-to-pptx-skill.md`](./docs/prd-md-to-pptx-skill.md) | Product requirements, conversion rules, architecture, acceptance criteria                      |

### Reference Docs (`references/`)

| Document                                                          | Contents                                                                         |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [`insight-extraction.md`](./references/insight-extraction.md)     | Section Card schema, 5 analytical roles, 7 narrative roles, extraction algorithm |
| [`content-distillation.md`](./references/content-distillation.md) | Slide text limits, bullet rules, distillation algorithm                          |
| [`image-generation.md`](./references/image-generation.md)         | 3-priority image system, Image Manifest cache, prompt derivation                 |
| [`layout-integrity.md`](./references/layout-integrity.md)         | Safe areas, font metrics, overflow verification checklist                        |
| [`parallel-execution.md`](./references/parallel-execution.md)     | 6-wave pipeline architecture, parallel render strategy                           |
| [`design-system.md`](./references/design-system.md)               | Token/theme/variant architecture, editorial details, lint rules                  |
| [`visual-qa.md`](./references/visual-qa.md)                       | Post-generation visual inspection + automated design lint + H-score              |
| [`cognitive-layout.md`](./references/cognitive-layout.md)         | Eye-tracking patterns, Gestalt principles, McKinsey/BCG layout rules             |
| [`svg-components.md`](./references/svg-components.md)             | Inline SVG patterns for charts, shapes, diagrams in HTML→PDF pipeline            |

---

## Design System

The `design/` Python package provides a token-driven theming and quality assurance system.

```python
from design import ThemeResolver, TOKENS, get_theme, select_variant, VariantState
from design import inject_editorial_elements, lint_deck, human_likeness_score

resolver = ThemeResolver(TOKENS, get_theme("consulting_minimal"))
theme_css = resolver.to_inline_style_block()

state = VariantState()
variant = select_variant("body_text", state, {"word_count": 120})

score = human_likeness_score(all_slide_htmls)
assert score["pass"], f"H-score {score['overall']:.2f} < 0.80"
```

### Themes

| Theme                | Accent           | Character                         |
| -------------------- | ---------------- | --------------------------------- |
| `consulting_minimal` | Navy #003087     | McKinsey/BCG corporate clarity    |
| `modern_editorial`   | Red #C41E3A      | Magazine-style editorial polish   |
| `product_pitch`      | Cobalt #1B4FD8   | Modern SaaS/startup energy        |
| `dark_executive`     | Steel #8A94A6    | Premium dark-mode for high-stakes |
| `academic_clean`     | Burgundy #8B0000 | Scholarly restraint               |

### Anti-AI Design Lint

| Rule | Blocks                               |
| ---- | ------------------------------------ |
| NO1  | Glassmorphism, backdrop-filter, blur |
| NO2  | border-radius > 4px                  |
| NO3  | box-shadow blur > 4px                |
| NO4  | text-shadow, drop-shadow             |
| NO5  | Multiple saturated hues per slide    |
| NO6  | Dashboard UI (tabs, toggles, pills)  |

---

## License

MIT
