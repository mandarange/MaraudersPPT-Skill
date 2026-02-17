# MaraudersPPT Skill

A Claude Code Skill that automatically converts Markdown documents into presentation-quality slides (.pdf).
Preserves the original Markdown's structure, images, and data while generating a presentation-ready PDF.

> **PDF is the primary presentation output** — all visual elements are designed for static rendering.
> No animations, transitions, buttons, or interactive elements are generated.

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

| Feature | Description |
|---------|-------------|
| **Auto Slide Mapping** | H1 → Title, H2 → Section divider, H3 → Sub-header — structure preserved |
| **23 Layout Types** | Dedicated layouts for text, tables, code, images, lists, KPIs, charts, timelines, etc. |
| **Infographic Auto-Conversion** | Detects numeric, comparison, and sequential data patterns → auto-maps to 8 chart types (AGGRESSIVE mode) |
| **Parallel Execution** | 6-wave parallel pipeline — AI image gen, chart rendering, and slide HTML gen run concurrently |
| **Executive Summary** | Auto-generates a key KPI summary slide right after the title for decks with 10+ slides |
| **CTA Closing** | Final slide with key message + Next Steps + contact info |
| **AI Hint Special Handling** | `[AI RULE]`, `[AI DECISION]`, `[AI NOTE]`, `[AI CONTEXT]` highlighted slides |
| **Anti-Vibe-Coding Design** | No rounded cards, no gray backgrounds, no AI dashboard aesthetics — McKinsey/BCG quality |
| **16px Minimum Font** | All chart/infographic content text ≥ 16px (exceptions: slide numbers 10pt, captions 12pt) |
| **Mandatory Original Images** | All `![alt](path)` images from the MD file are inserted into slides (never omitted) |
| **AI Image Generation** | Auto-generates photorealistic content images via Cursor native image gen / OpenCode background tasks |
| **Persistent Image Reuse** | Generated images are cached per page key and reused across reruns unless user explicitly requests refresh |
| **Layout Integrity** | Auto-validates overflow/overlap/margin violations + up to 3 regeneration attempts |
| **Slide Flow Optimization** | MAX-2-TEXT, FRONT-VISUAL, AUTO-APPENDIX rules applied |
| **Version Control** | Each generation outputs `v{M}.{m}_filename.pdf` |
| **Low-Token File Pipeline** | Intermediate JSON artifacts are written to disk (`.pipeline/`) to avoid large stdin/stdout payloads |
| **Cross-Platform** | Works on macOS, Windows, and Linux — no OS-specific dependencies |
| **Korean/CJK Full Support** | Pretendard font-based with full fallback chain (Apple SD Gothic Neo → Malgun Gothic → Noto Sans KR) |
| **Input Contract** | Audience, goal, and time constraints captured upfront for targeted content generation |
| **Section Cards** | Semantic analysis of content structure with visual blueprint mapping |
| **7-Role Narrative Taxonomy** | Structured narrative roles (Context, Problem, Solution, Evidence, Impact, Action, Closing) |
| **Visual Blueprint** | Pre-generation layout planning with role-to-slide mapping |
| **Dual Output** | Generates both presentation deck and detailed appendix for comprehensive coverage |
| **Image Manifest** | Cache system for generated images with reuse tracking and refresh control |

---

## Design Philosophy

- **Designed for PDF output** — no animations, transitions, or interactive elements
- **White background (`#FFFFFF`) + black text (`#1A1A1A`)** as default. Font size, layout, and readability are paramount
- Accent color (`#D94F4F`) used **only at the word-level Bold** — max 1 per slide
- **1–2 topics per slide**, bullet-point and quantitative style (max 4 bullets, optimal 3)
- 16:9 aspect ratio, 1920×1080px high resolution
- 8px grid-based consistent spacing system
- **Original MD images are mandatory** — `![alt](path)` images must never be omitted

---

## Output Language Rule

> The generated presentation PDF follows the source Markdown's language.
> Korean MD → Korean slides, English MD → English slides, Japanese MD → Japanese slides.
> This skill does NOT translate content — it preserves the original language as-is.

---

## IDE Environment Behavior

| Environment | AI Image Generation | PDF Rendering | Model Switching |
|-------------|-------------------|---------------|-----------------|
| **Cursor 2.4+ / Antigravity** | Native image gen (built-in agent tool) | Playwright-based renderer | **Not required** |
| **OpenCode** | Background task via `task()` | Playwright-based renderer | **Not required** |

- **Cursor / Antigravity**: Uses built-in image generation agent tool (powered by Nano Banana Pro) — no model switch needed
- **OpenCode**: Image generation runs as a background task via `task(run_in_background=true)`
- **All environments**: Pipeline proceeds immediately with zero confirmation prompts

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

| Field | Purpose |
|-------|---------|
| `type` | `ai-generated` / `chart` / `original-md` / `html-concept` |
| `prompt` | Exact prompt used to generate AI images (reproducibility) |
| `generator` | Tool that produced the image (`cursor-native`, `playwright-chart`, …) |
| `visual_intent` | Layout role the image fulfills |
| `content_hash` | Cache key for AI images (skip regeneration on match) |
| `data_hash` | Cache key for charts |
| `file_size_bytes` | Integrity check (0 = stale, triggers regeneration) |

- Same hash on re-run → reuse existing image, no regeneration
- Explicit refresh: `--refresh=all`, `--refresh=slide:7`, `--refresh=type:ai-generated`
- Images are never deleted by the pipeline

- `sections.json` (parsed MD sections)
- `slides.json` (summarized slide IR)
- `html-files.json` (render target list)

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

| Type | Purpose |
|------|---------|
| `kpi_cards` | Compare 1–4 key performance indicators |
| `bar_chart` | Numeric comparison across items |
| `donut_chart` | Proportion/share visualization |
| `process_flow` | Step-based pipeline (3–8 steps) |
| `timeline` | Release roadmap/milestones |
| `comparison` | Side-by-side contrast (Before/After) |
| `icon_grid` | Non-numeric item classification (2x2, 2x3, 3x2) |
| `funnel` | Stage-based drop-off pipeline |

---

## Dependencies

| Package | Role | Required |
|---------|------|:--------:|
| `playwright` | HTML rendering / PDF generation / chart screenshots | **Required** |
| `sharp` | Image post-processing (rasterization) | **Required** |
| Native image gen | Built-in agent tool — Cursor / Antigravity (Nano Banana Pro) | Cursor / Antigravity |
| `task()` background gen | OpenCode image generation via background agent | OpenCode only |

---

## Project Structure

```
MaraudersPPT-Skill/
├── README.md                      ← This file
├── SKILL.md                       ← Skill workflow, layouts, checklist (v2.0.0)
├── LICENSE                        ← MIT License
├── package.json                   ← npm dependencies (playwright, sharp)
├── .gitignore                     ← Git ignore rules
├── references/                    ← Detailed reference docs (progressive disclosure)
│   ├── insight-extraction.md      ← Section Card schema, insight extraction algorithm
│   ├── content-distillation.md    ← Slide text limits & distillation algorithm
│   ├── image-generation.md        ← Visual coverage audit & prompt derivation
│   ├── layout-integrity.md        ← Safe areas, font metrics, verification
│   ├── parallel-execution.md      ← 6-wave architecture & performance
│   └── visual-qa.md              ← Post-generation visual inspection
├── templates/
│   ├── charts/                    ← 8 infographic Python templates
│   │   ├── __init__.py            ← render_chart(type, data) dispatcher
│   │   ├── base.py                ← Shared CSS & utilities
│   │   ├── kpi_cards.py           ← KPI card grid
│   │   ├── bar_chart.py           ← Horizontal bar chart
│   │   ├── donut_chart.py         ← Donut chart
│   │   ├── process_flow.py        ← Process flow
│   │   ├── timeline.py            ← Timeline
│   │   ├── comparison.py          ← Side-by-side comparison
│   │   ├── icon_grid.py           ← Icon grid
│   │   └── funnel.py              ← Funnel chart
│   └── compositions/              ← Planned: Section Card composition templates
└── docs/
    ├── design-spec.md             ← Design spec (colors, typography, layout, chart CSS)
    └── prd-md-to-pptx-skill.md    ← Product Requirements Document (PRD)
```

---

## Documentation

| Document | Contents |
|----------|----------|
| [`SKILL.md`](./SKILL.md) | Skill workflow (Phases 0-5), 23 layouts, validation checklist, design rules summary |
| [`references/`](./references/) | Detailed reference docs: insight extraction, content distillation, image generation, layout integrity, parallel execution, visual QA |
| [`docs/design-spec.md`](./docs/design-spec.md) | Color palette, typography, 8px grid, layout specs, 8 infographic CSS specifications |
| [`docs/prd-md-to-pptx-skill.md`](./docs/prd-md-to-pptx-skill.md) | Feature spec, conversion rules, architecture, acceptance criteria |

---

## License

MIT
