---
name: MaraudersPPT-Skill
description: >
  Converts Markdown documents into presentation-quality PDF files.
  Requires explicit "MaraudersMD2PPT" invocation - never self-activates.
  Phase-based pipeline with Semantic Analysis, Narrative Architecture, and Visual Blueprint.
  Maps heading hierarchies, tables, code blocks, images, and AI Hint blocks to 23 slide
  layout types. Generates AI photorealistic images via native image generation (Cursor)
  or background task delegation (OpenCode). Uses Section Cards and narrative roles to drive
  action titles, accent words, visual coverage, and dual-output routing. Fully supports Korean/CJK
  text with Pretendard font.
license: MIT
compatibility:
  os: [macos, linux, windows]
  requires: [node, python3]
metadata:
  version: "2.0.0"
  author: "MaraudersPPT"
---

# MaraudersPPT Skill

Converts Markdown -> presentation-quality PDF. For detailed design specs see `docs/design-spec.md`.

| Reference | Contents |
|-----------|----------|
| [Insight Extraction](references/insight-extraction.md) | Section Card schema, 5 analytical roles, 7 narrative roles, extraction algorithm |
| [Content Distillation](references/content-distillation.md) | Slide text limits, bullet rules, distillation algorithm |
| [Cognitive Layout](references/cognitive-layout.md) | Eye-scanning patterns, Gestalt principles, pre-attentive attributes, spacing system |
| [SVG Components](references/svg-components.md) | Inline SVG library: charts, icons, connectors, progress arcs, sparklines |
| [Image Generation](references/image-generation.md) | 3-priority image system, Image Manifest cache, prompt derivation, layout adaptation |
| [Layout Integrity](references/layout-integrity.md) | Safe areas, font metrics, verification checklist, golden rule |
| [Parallel Execution](references/parallel-execution.md) | 6-wave architecture, parallel render strategy, performance gains |
| [Visual QA](references/visual-qa.md) | Post-generation visual inspection workflow |
| [Design Spec](docs/design-spec.md) | Colors, typography, 8px grid, infographic CSS |
| [PRD](docs/prd-md-to-pptx-skill.md) | Product requirements, acceptance criteria |

---

## Activation Guard (GATE)

> **Hard gate. NOTHING runs without this.**

```
BEFORE ANY OTHER PHASE:
  1. Scan user's message for "MaraudersMD2PPT" (case-insensitive)
  2. IF FOUND -> activation_status = "ACTIVATED" -> Proceed to Phase 0
  3. IF NOT FOUND -> HARD FAIL -> Output failure message -> STOP
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
| `Phase 1: update, Phase 2: MaraudersMD2PPT docs/prd.md` ✅ | `Use the slide skill on this file` ❌ |

---

## Execution Contract

> Once activated, Phases 0-5 run to completion with **ZERO mid-flow confirmations**.

**PROHIBITED during pipeline:** "Should I continue?", "Do you want me to proceed?", "Ready to generate?", or any confirmation request. Zero confirmations in ALL environments.

**State tracking throughout pipeline:**
```
activation_status:  "ACTIVATED" | "FAILED"
pipeline_mode:      "SKILL" (must NEVER be "GENERIC" after activation)
environment:        "OpenCode" | "Cursor"
```

---

## Pipeline Phases

### Phase 0: Input Contract + Environment Detection

#### Phase 0.1 Input Contract

All InputContract fields have sensible defaults. LLM infers from context if user does not specify.

```yaml
InputContract:
  source_md: string
  audience: enum [executive, team, external, mixed]  # default: team
  goal: enum [persuade, inform, decide, inspire]      # default: inform
  time_minutes: number                                 # default: 15
  slide_budget: "auto" | number                        # auto = time_minutes × 1.5
  tone: enum [bold, calm, urgent]                      # default: calm
  cut_policy: enum [ruthless, balanced, preserve-all]  # default: balanced
```

#### Phase 0.2 Environment Detection

| | OpenCode | Cursor / Antigravity |
|--|----------|----------------------|
| `task()` available? | ✅ | ❌ |
| Native image gen? | ❌ | ✅ (built-in agent tool) |
| Image generation | Background task via `task()` | Native image gen (Nano Banana Pro) |
| Model switch? | No | **No** |

All environments proceed immediately - no confirmation prompts.

### Phase 1: Semantic Analysis (MD Parsing + Section Cards)

#### Phase 1.1 Input Reception

- Verify MD file path or receive inline MD text
- Confirm file existence and encoding
- **Collect ALL image paths** from MD (`![alt](path)`) - omission prohibited

#### Phase 1.2 Markdown Parsing

- H1 -> document title, H2 -> section separation, **H3 -> sub-header within slide or slide split**
- H3 mapping: If H2 section has 2+ H3 children with substantial content -> split into separate slides per H3. If H3 content is light -> use as **bold sub-header** within parent slide's body area.
- Classify: bullets, tables, code blocks, images, AI Hint blocks, blockquotes, checklists, **plain paragraphs**
- **PARAGRAPH PRESERVATION (CRITICAL)**: Plain text paragraphs (no bullets, no special markup) MUST be converted to keyword bullets - NEVER silently deleted. Every paragraph produces >=1 bullet.
- **MARKDOWN SANITIZATION (MANDATORY)**: Run sanitization in **Phase 1** (before Section Card generation). Remove markdown syntax tokens from display text: heading markers (`#`, `##`, `###`), list markers (`-`, `*`, `+`, `1.`), code fences/backticks (``` / `), and raw link syntax (`[text](url)` -> display text). Token leakage in rendered slide text is a CRITICAL BUG.
- **PARAGRAPH DETECTION RULE**: Plain paragraph = text block without markdown list markers (`-`, `*`, `+`, `1.`), blockquote marker (`>`), or code fence (```).
- **URL/LINK HANDLING**: URLs in source MD -> preserve as display text (shortened if >80 chars). Never discard links silently. Group multiple URLs into a dedicated links slide or footer area.

#### Phase 1.3 Section Card Generation

> Every H2 section must produce one Section Card. Re-analyze weak cards before moving to narrative design.

```yaml
SectionCard (per H2 section):
  source_section: string          # "## Background"
  claim: string                   # one-sentence argument this section makes
  role: enum [problem, solution, evidence, context, meta]
  stakes: enum [high, medium, low]
  must_keep: boolean              # can the story work without this section?
  insight: string                 # the audience's "aha" moment
  headline: string                # action title candidate (<=15 words, with verb + conclusion)
  evidence: string[]              # supporting data points
  accent_candidate: string        # for Bold + #D94F4F (1 per slide max)
  kpi_metrics: string[]           # executive summary candidates
  source_lines: [number, number]  # line range in source MD
  confidence: float               # 0.0-1.0, re-analyze if < 0.5
```

Full extraction rules: [references/insight-extraction.md](references/insight-extraction.md)

#### Phase 1.4 Visual Content Detection

Auto-detect infographic candidates from text content:

| Pattern | Visualization |
|---------|--------------|
| 3+ items with numbers | Bar Chart |
| Percentages ~= 100% | Donut Chart |
| 3-8 sequential steps | Process Flow |
| Before/after comparison | Comparison |
| 1-4 key metrics | KPI Cards |
| 4-8 short items | Icon Grid |
| Chronological events | Timeline |
| Decreasing stages | Funnel |

**Mode: AGGRESSIVE** - convert all mappable content. Use `templates/charts/` Python templates.

### Phase 2: Narrative Architecture (Story Arc + Slide Plan + Dual Output Routing)

#### Phase 2.1 Story Arc Design

Determine the deck-level narrative pattern from Section Card role distribution and user goal.

- `problem-solution`: dominant `problem` + `solution` + `evidence`
- `journey`: chronology-heavy sections with transformation narrative
- `comparison`: alternatives, tradeoffs, A/B framing
- `showcase`: outcomes, capabilities, and impact-first storytelling

Story arc must be explicit before slide ordering begins.

#### Phase 2.2 Slide Role Taxonomy (7 Roles)

Each slide must have exactly one narrative role.

| Role | Purpose | Emotional Curve |
|------|---------|----------------|
| `hook` | Capture attention in first 15 seconds | Curiosity ↑ |
| `problem` | Current situation pain points | Anxiety ↑ |
| `insight` | "Why now" turning point | Realization |
| `solution` | Core proposal | Hope ↑ |
| `proof` | Data/case evidence | Trust ↑ |
| `impact` | Results and vision | Confidence ↑ |
| `cta` | Next action request | Resolution |

#### Phase 2.3 Slide Plan

Slide plan must include sequence, role assignment, source linkage, and routing decisions.

```yaml
slide_plan:
  story_arc: "problem-solution"
  slides:
    - order: 1
      role: "hook"
      message: "결제 한 건에 3초 - 하루 10만 건이면 83시간을 버린다"
      visual_intent: "dramatic-stat"
      source_refs: ["section_card_1"]
  cut_list:
    - source: "## Dependencies"
      reason: "Technical detail, not story-relevant"
      destination: "appendix"    # appendix | speaker_notes | cut
  coverage_report:
    total_source_sections: 8
    in_deck: 5
    in_appendix: 2
    in_speaker_notes: 1
    truly_cut: 0
    coverage_pct: "100%"
```

#### Phase 2.4: Content Distillation (SLIDES ARE NOT DOCUMENTS)

> **The presenter speaks. The slide shows keywords only.** Full rules -> [references/content-distillation.md](references/content-distillation.md)

**Hard limits:**

| Layout | Max Bullets | Words/Bullet | Total Slide Words |
|--------|:-----------:|:------------:|:-----------------:|
| `bullet-list` | 3 (max 4) | **7** | **50 EN / 35 KR** |
| `image-text` | 3 | **5** | **50 EN / 35 KR** |
| All others | - | - | **50 EN / 35 KR** |

**Korean/CJK: 0.7x multiplier.** Bullet = keyword fragment, NOT sentence.

**⚠️ CONTENT PRESERVATION GUARANTEE**: Distillation means CONDENSE, never DELETE. **NEVER truncate with `...`** - rewrite as keyword fragment. **NEVER duplicate title text in body bullets** - title = conclusion, body = evidence.

```
HIERARCHY (in order):
  1. Condense -> keyword fragments (ALWAYS try this first)
  2. If too short to bullet -> use as subtitle or caption text
  3. If section has <15 words total -> merge via SHORT-SECTION-MERGE (Phase 2.6)
  4. ABSOLUTE PROHIBITION: A section that had content in the source MD
     must produce content on the slide. Zero-content slides = CRITICAL BUG.
```

**Paragraph -> Bullet Conversion** (for non-bullet source text):
```
Source paragraph: "This project is licensed under the MIT License."
  -> Bullet: • License: **MIT**

Source paragraph: "Contributions are welcome. Please read the contributing guide."
  -> Bullet: • Contributions welcome - see guide

Source paragraph: "Built with React, TypeScript, and Tailwind CSS for modern web development."
  -> Bullet: • Stack: **React** + TypeScript + Tailwind
```

#### Phase 2.5 Executive Summary

Auto-insert after title slide for 10+ slide decks. Content: 3-5 KPI metrics + 1-line conclusion.

#### Phase 2.6 Slide Flow Optimization

- **MAX-2-TEXT**: 3rd consecutive text slide must be visual
- **FRONT-VISUAL**: >=1 infographic in first 30% of slides
- **AUTO-APPENDIX**: Detailed tables (6+ rows) -> appendix; summaries in main body
- **SHORT-SECTION-MERGE**: Sections with <=2 content lines (e.g., "License: MIT") -> merge into previous slide as a footer/badge, or combine multiple short sections into one `icon-grid` / `highlight-card` slide. NEVER create a standalone slide for <=15 words of body content.
- **MOOD-ARC**: Deck emotional curve must progress tense -> hopeful -> confident.

#### Phase 2.7 Dual Output Routing

Every source section maps to exactly ONE destination:

```
"deck"           -> role is hook/problem/insight/solution/proof/impact/cta AND must_keep=true
"appendix"       -> evidence with stakes=low, detailed tables 6+ rows, tech details
"speaker_notes"  -> context sections that help presenter but do not need a slide
"cut"            -> meta sections (license, contributing), confidence < 0.5
```

Routing is mandatory and audited in `.coverage-report.json`.

### Phase 3: Visual Blueprint (Per-Slide Design + Deck Rhythm)

#### Phase 3.1 Per-Slide Visual Blueprint

> Eye-scanning rules, Gestalt principles, and spacing constraints -> [references/cognitive-layout.md](references/cognitive-layout.md)

Each planned slide gets one visual blueprint before rendering.

```yaml
VisualBlueprint:
  slide_id: number
  role: string          # from Phase 2
  message: string       # from Phase 2
  eye_flow:
    first: string       # what the eye sees first (hero_number, image, headline)
    second: string
    third: string
  composition:
    type: string        # hero-metric, single-statement, split-image-text, evidence-bullets, etc.
    dominant_element: string  # number, image, text, chart
  image_strategy:
    need: enum [original-md, chart, ai-generated, none]
    treatment: enum [background-10%, background-15%, left-50%, full-bleed, top-30%, none]
    prompt_seed: string       # insight-based, not keyword-based
    cache_lookup: object      # Image Manifest cache check
  emphasis:
    accent_word: string
    bold_elements: string[]
  template: string            # composition template name
```

#### Phase 3.2 Deck Rhythm

```yaml
DeckRhythm:
  max_consecutive_same_density: 2
  max_consecutive_same_dominant: 2
  mood_arc_required: true
  visual_variety_score: ">= 0.6"
```

Deck rhythm is validated before entering rendering.

#### Phase 3.3 Visual Intent -> Layout Recipe Mapping

| Visual Intent | Description | Layout Recipes |
|--------------|-------------|----------------|
| `dramatic-stat` | One shocking number | `hero-metric` / `kpi-cards` |
| `contrast-comparison` | Before/after contrast | `comparison` / `bar-chart` |
| `single-statement` | One powerful sentence | `quote-style` (28pt center) |
| `evidence-grid` | Multiple evidence items | `kpi-cards` / `bullet-list` + image |
| `process-reveal` | Step-by-step | `process-flow` / `timeline` |
| `data-proof` | Data-driven proof | `bar-chart` / `donut-chart` / `table` |
| `narrative-image` | Image tells the story | `image` / `image-text` |
| `decision-point` | AI decision/rule highlight | `ai-hint` / `single-statement` |
| `action-items` | Next steps | `closing` / `checklist` |

### Phase 4: Rendering (HTML + Image + PDF)

#### Phase 4.1 Image Handling - 3 Priority System

```
Priority 1: Original MD images -> copy to assets/, absolute path reference. NEVER replace.
Priority 2: HTML code generation -> charts (templates/charts/), diagrams, compositions -> Playwright screenshot
Priority 3: LLM image generation -> insight-based prompt -> Native gen (Cursor) / task() (OpenCode) / HTML concept fallback
```

#### Phase 4.2 Image Manifest (`assets/image-manifest.json`)

Stored inside `assets/` — single source of truth for every image file.

| Field | Purpose |
|-------|---------|
| `type` | `ai-generated` / `chart` / `original-md` / `html-concept` |
| `prompt` | Exact prompt used (AI images only) — enables reproducibility |
| `generator` | Which tool produced the image (`cursor-native`, `opencode-task`, `playwright-chart`, `source-copy`, …) |
| `visual_intent` | Visual intent from Phase 3 VisualBlueprint |
| `width` / `height` / `file_size_bytes` | Quality verification fields |
| `content_hash` | Cache key for AI images: `sha256(prompt + generator_id + render_params)` |
| `data_hash` | Cache key for charts: `sha256(data + chart_type + template_version)` |

- Skip regeneration on cache hit (`hash matches AND file exists AND file_size_bytes > 0`)
- Full schema + cache logic -> [references/image-generation.md](references/image-generation.md)

#### Phase 4.3 HTML Slide Generation

> Inline SVG patterns (charts, icons, connectors, sparklines) -> [references/svg-components.md](references/svg-components.md)

- Individual HTML per slide, CSS inline, 16:9 at 1920x1080px
- Composition templates for structured layouts
- Pretendard font with fallback chain
- **PDF Layout Reliability Rule**: For vertical centering and precise positioning, use `position: absolute` with explicit offsets (e.g., `top: 50%; transform: translateY(-50%)`) or fixed pixel values. Avoid relying solely on `flexbox` for 1080px height distribution, as headless PDF renderers may miscalculate viewport height.
- Use SVG components for: curved shapes, arrow markers, trend lines, crisp icons at any scale

#### Phase 4.4 PDF Rendering

- Playwright opens each HTML slide (1920x1080 viewport)
- Renders each slide to a single-page PDF
- All pages combined into final deck PDF
- Tables, charts, images all rendered natively in HTML/CSS - pixel-perfect in PDF output

### Phase 5: Verification + Output (Layout Integrity + Visual QA + Diagnostic)

#### Phase 5.1 Layout Integrity (ZERO TOLERANCE)

> Full rules -> [references/layout-integrity.md](references/layout-integrity.md)

Key rules remain enforced: safe area boundaries, readable font floor, bullet reduction before split, and no overflow/overlap tolerance.

#### Phase 5.2 Hard Gates

> Hard gates run BEFORE writing PDF. If any gate fails, STOP and report failures.

```
HARD GATES (must all pass):
  1) text_only_slide_ratio == 0%
  2) markdown_token_leakage_count == 0
  3) visual_coverage == 100%
  4) coverage_pct == 100%

IF any gate fails:
  -> pipeline_status = "FAILED"; do NOT write .pdf
  -> output blocking error report with offending slide numbers
Metric scope: content_slides = all slides except `title`, `section-divider`, `appendix-divider`, `closing`; text_only_slide_ratio = text_only_content_slides / total_content_slides * 100; truncated_sentence_ratio = slides_with_ellipsis_in_title_or_body_or_caption / total_content_slides * 100
```

#### Phase 5.3 Output Structure

```
{original_filename}_slides/
├── v{M}.{m}_{original_filename}.pdf              ← Primary output (deck only)
├── v{M}.{m}_{original_filename}_appendix.pdf     ← Appendix
├── .coverage-report.json                          ← Content routing audit (deck/appendix/notes/cut)
└── assets/                                        ← All image files + manifest
    ├── image-manifest.json                        ← Image cache + metadata for every asset
    ├── md-img-{NN}-{slug}.png                    ← Priority 1: copied from source MD
    ├── chart-{NN}-{slug}.png                     ← Priority 2: chart/diagram screenshots
    └── ai-img-{NN}-{label}.png                   ← Priority 3: LLM-generated images
```

#### Phase 5.4 Diagnostic Report (MANDATORY in every completion message)

```
📊 MaraudersMD2PPT v2.0 Diagnostic Report
─────────────────────────────────────────
Activation:       ✅ ACTIVATED
Pipeline Mode:    SKILL (full pipeline)
Environment:      OpenCode | Cursor
Input Contract:   audience={}, goal={}, time={}min, slides={}
Phases Executed:  [✅] Phases 0-5 (list each)
Narrative:
  Story arc:       {arc_type}
  Slide roles:     hook={}, problem={}, insight={}, solution={}, proof={}, impact={}, cta={}
Content Coverage:
  Source sections:  {total}
  In deck:         {n} | In appendix: {n} | In notes: {n} | Cut: {n}
  Coverage:        {pct}%
Quality Metrics:
  Visual coverage:     {N}/{M} (target: 100%)
  Text-only ratio:     {pct}% (target: 0%)
  Token leakage count: {n} (target: 0)
  Truncation ratio:    {pct}% (target: 0%)
  Duplicate ratio:     {pct}% (target: < 5%)
  Image cache hits:    {n}/{total} (reused from manifest)
Output: {filepath}
```

#### Phase 5.5 Visual QA

> Full workflow -> [references/visual-qa.md](references/visual-qa.md)

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

Slide language = source MD language. No translation.

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

> **MANDATORY for all slides without visual content.** Full details -> [references/image-generation.md](references/image-generation.md)

| Target | Method |
|--------|--------|
| Slides without visuals | Priority 1: Native image gen (Cursor/Antigravity) / background task (OpenCode) -> Priority 2: HTML concept + Playwright -> Priority 3: LLM image generation fallback when native path unavailable |
| Charts/infographics | HTML templates (`templates/charts/`) -> Playwright screenshot |
| Diagrams/flowcharts | HTML/SVG |
| Original MD images | Copy to `assets/`, reference via absolute path in HTML |

**Pipeline**: Generate PNG -> save to `{output_dir}/assets/` -> reference in HTML via `<img src="/absolute/path/...">` -> Playwright renders HTML slides to PDF with all images embedded.

**Image Manifest rule**: Every generated visual writes metadata into `assets/image-manifest.json` (`type`, `prompt`, `generator`, `visual_intent`, `content_hash`, `data_hash`, `width`, `height`, `file_size_bytes`, `created_at`). Cache hit reuses existing file unless user explicitly requests refresh.

---

## Dependencies

| Dependency | Role | Required |
|-----------|------|----------|
| Native image gen | Built-in agent tool — Cursor / Antigravity (Nano Banana Pro) | Cursor / Antigravity |
| `task()` background gen | OpenCode image generation via background agent | OpenCode only |
| `playwright` | HTML rendering / screenshots | **Required** (npm) |
| `sharp` | Image post-processing | **Required** (npm) |

---

## Validation Checklist

### Phase 0 (Input Contract)
- [ ] `MaraudersMD2PPT` keyword found, `activation_status` == "ACTIVATED"
- [ ] `pipeline_mode` == "SKILL"
- [ ] InputContract populated (defaults if not specified)

### Phase 1 (Semantic Analysis)
- [ ] Every H2 section has a SectionCard with all 12 fields
- [ ] Every SectionCard has role, claim, insight, must_keep
- [ ] confidence >= 0.5 for all kept sections (re-analyze if below)
- [ ] accent_candidate selected per section (1 per slide max)
- [ ] Visual content detection applied (AGGRESSIVE mode)
- [ ] Markdown sanitization applied (zero token leakage)
- [ ] Paragraph preservation: all paragraphs -> keyword bullets

### Phase 2 (Narrative Architecture)
- [ ] Story arc determined and slides ordered by narrative role
- [ ] Every slide has exactly one role from 7-role taxonomy
- [ ] Cut list has reason + destination for every cut section
- [ ] Coverage report: coverage_pct == 100%
- [ ] Content distillation: all slides <= 50w EN / 35w KR
- [ ] Bullets <= 3 (max 4), each <= 7 words, keyword fragments only
- [ ] No ellipsis truncation, no title-body duplication
- [ ] Executive summary present (10+ slides)
- [ ] MAX-2-TEXT, FRONT-VISUAL, AUTO-APPENDIX, SHORT-SECTION-MERGE applied

### Phase 3 (Visual Blueprint)
- [ ] Every slide has VisualBlueprint (eye_flow, composition, image_strategy)
- [ ] Deck Rhythm validated (density variation, mood arc)
- [ ] Visual Intent -> Layout Recipe mapping applied
- [ ] Eye-scanning pattern (Z/F/Center) assigned per slide
- [ ] Gestalt rules applied: proximity, similarity, continuity, figure-ground
- [ ] Pre-attentive attribute (color, size, position) used for primary focus element

### Phase 4 (Rendering)
- [ ] Image priority respected: Original MD -> HTML code -> LLM gen
- [ ] Image Manifest populated and cached
- [ ] 0% text-only content slides
- [ ] Layout adapted on image addition, text condensed
- [ ] SVG used for: donut arcs, sparklines, arrow connectors, crisp icons

### Phase 5 (Verification)
- [ ] Hard gates: text_only=0%, token_leakage=0, coverage=100%
- [ ] Layout integrity: no overflow, no overlap, margins respected
- [ ] Diagnostic report included in completion message

---

## Parallel Execution

> **Full architecture -> [references/parallel-execution.md](references/parallel-execution.md)**

6-wave pipeline: Gate -> Semantic -> Narrative -> Blueprint -> Parallel Render -> Assemble+Verify.

Parallel Render wave runs image generation, chart rendering, and HTML composition concurrently after blueprint lock. Assemble+Verify executes hard-gate validation, coverage audit, and final packaging.

---

## Future Improvements (Post v2.0)

| Item | Description |
|------|-------------|
| CSS Custom Properties | Theme switching via CSS variables |
| Slide Complexity Score | Auto-calculate cognitive complexity and density risk |
| Interactive Presentation Mode | Optional branch for transitions and presenter interactions |
| Multi-language Expansion | Language support beyond Korean/CJK with locale-aware typography |
