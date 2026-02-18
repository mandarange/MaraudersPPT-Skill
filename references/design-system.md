# Design System Reference

Technical reference for the `design/` package: tokens, themes, layout variants, editorial details, image treatments, and lint rules.

## Architecture Overview

```
Primitive Tokens          e.g. color.gray.900, font.size.24
       |
Semantic Tokens           e.g. color.text.primary, font.body
       |
Theme Resolver            picks token set per theme name
       |
CSS Custom Properties     --color-text-primary, --font-body
       |
Layout Variants           23 types x 2-3 variants each (69 total)
       |
Editorial Layer           running headers, folios, source lines, dividers
       |
Design Lint               per-slide (EQ1, NO, YES) + cross-slide (DQ1) + H-score
```

## Token System

### Three-Tier Hierarchy

| Tier | Scope | Example Token | Example Value |
|------|-------|---------------|---------------|
| Primitive | Raw values | `color.gray.900` | `#1A1A1A` |
| Primitive | Raw values | `color.red.500` | `#D94F4F` |
| Primitive | Raw values | `font.size.24` | `24px` |
| Primitive | Raw values | `spacing.8` | `8px` |
| Semantic | Role-based | `color.text.primary` | `{color.gray.900}` |
| Semantic | Role-based | `color.accent` | `{color.red.500}` |
| Semantic | Role-based | `color.bg.default` | `#FFFFFF` |
| Semantic | Role-based | `color.bg.inverted` | `#2C2C2C` |
| Component | Scoped | `title.font.size` | `40px` |
| Component | Scoped | `body.font.size` | `20px` |
| Component | Scoped | `caption.font.size` | `12px` |
| Component | Scoped | `kpi.value.font.size` | `48px` |

### Token-to-CSS-Var Mapping

| Token Path | CSS Custom Property | Fallback |
|------------|-------------------|----------|
| `color.text.primary` | `--color-text-primary` | `#1A1A1A` |
| `color.text.secondary` | `--color-text-secondary` | `#6B7280` |
| `color.accent` | `--color-accent` | `#D94F4F` |
| `color.bg.default` | `--color-bg-default` | `#FFFFFF` |
| `color.bg.inverted` | `--color-bg-inverted` | `#2C2C2C` |
| `font.family.display` | `--font-display` | `Pretendard` |
| `font.family.body` | `--font-body` | `Pretendard` |
| `spacing.base` | `--spacing-base` | `8px` |

Backward compatibility: all CSS var usages include fallback values via `var(--token, fallback)` so slides render correctly even if the theme resolver fails to inject custom properties.

## Themes

Five built-in themes. Each sets accent color, display font, and background treatment.

| Theme | Accent | Display Font | Background | Use Case |
|-------|--------|-------------|------------|----------|
| `corporate` | `#D94F4F` | Pretendard | White `#FFFFFF` | Default. Business decks, strategy, reports |
| `minimal` | `#374151` | Pretendard | White `#FFFFFF` | Data-heavy, research, technical briefs |
| `bold` | `#E63946` | Pretendard Bold | White `#FFFFFF` | Keynotes, pitches, high-energy presentations |
| `dark` | `#F87171` | Pretendard | Dark `#2C2C2C` | Evening events, screen-first delivery |
| `warm` | `#D97706` | Pretendard | White `#FFF9F0` | Culture, HR, internal comms |

Theme resolution order: explicit user choice > markdown frontmatter `theme:` field > `corporate` default.

## Layout Variants

### 23 Layout Types

Each type has 2-3 visual variants. Total variant pool: 69.

| # | Type | Variants | Primary Use |
|---|------|----------|-------------|
| 1 | `title` | 3 | Opening slide with deck title and subtitle |
| 2 | `section-divider` | 2 | Chapter/section breaks |
| 3 | `text-only` | 3 | Key statements, quotes, emphasis |
| 4 | `text-image` | 3 | Body text alongside a supporting image |
| 5 | `image-full` | 2 | Full-bleed or large-format image |
| 6 | `two-column` | 3 | Side-by-side content comparison |
| 7 | `three-column` | 2 | Triple-panel layouts |
| 8 | `bullet-list` | 3 | Structured bullet points |
| 9 | `numbered-list` | 2 | Sequential steps or ranked items |
| 10 | `table` | 3 | Data tables with header row |
| 11 | `kpi-cards` | 3 | 1-4 key metric cards |
| 12 | `bar-chart` | 2 | Horizontal bar comparisons |
| 13 | `donut-chart` | 2 | Proportion/share visualization |
| 14 | `process-flow` | 3 | Step-based pipelines (3-8 steps) |
| 15 | `timeline` | 2 | Chronological milestones |
| 16 | `comparison` | 3 | Before/after, pro/con |
| 17 | `icon-grid` | 3 | Non-numeric classification (2x2, 2x3, 3x2) |
| 18 | `funnel` | 2 | Stage-based drop-off |
| 19 | `code-block` | 2 | Source code with syntax highlighting |
| 20 | `quote` | 2 | Pull quotes with attribution |
| 21 | `closing` | 3 | CTA, next steps, contact info |
| 22 | `appendix-divider` | 2 | Appendix section break |
| 23 | `executive-summary` | 3 | Auto-generated KPI overview (10+ slide decks) |

### Variant Selection and Rhythm

The rhythm algorithm scores candidate variants to maximize visual variety across the deck.

| Factor | Weight | Description |
|--------|--------|-------------|
| Type uniqueness | 0.30 | Penalize same type appearing within 2-slide window |
| Variant freshness | 0.25 | Prefer variants not yet used in the deck |
| Density alternation | 0.25 | Alternate between high/medium/low density slides |
| Visual weight balance | 0.20 | Avoid consecutive heavy-image or heavy-text slides |

Constraint: no 3+ consecutive slides with the same layout type. Enforced by `DQ1_CONSECUTIVE_SAME` lint rule.

## Editorial Details

Editorial elements add professional polish. All use CSS classes prefixed with `editorial-`.

| Element | CSS Class | Placement | Font | Size |
|---------|-----------|-----------|------|------|
| Running header | `editorial-header` | Top-left, 40px from top edge | Pretendard | 10px |
| Running folio | `editorial-folio` | Bottom-right, 40px from bottom | Pretendard | 10px |
| Slide number | `editorial-slide-number` | Bottom-right, inside folio area | Pretendard | 10px |
| Source citation | `editorial-source` | Bottom-left, 40px from bottom | Pretendard | 9px |
| Section divider line | `editorial-divider` | Below header, full width minus margins | -- | 1px height |
| Deck title watermark | `editorial-watermark` | Bottom-left on title slide only | Pretendard | 8px |
| Confidentiality mark | `editorial-confidential` | Top-right corner | Pretendard Medium | 8px |

Coverage rules:
- Running header: all slides except `title` and `closing`
- Folio/slide number: all slides except `title`
- Source citation: any slide referencing external data
- Divider line: `section-divider` slides only

## Image Treatment

Four treatment modes for images placed on slides. All sizes in px, canvas 1920x1080.

| Treatment | CSS Class | Dimensions | When to Use |
|-----------|-----------|------------|-------------|
| `contain` | `img-contain` | Max 880x600, aspect-ratio preserved | Default. Photos, diagrams, screenshots |
| `cover` | `img-cover` | Fill container, overflow clipped | `image-full` layout, background images |
| `icon` | `img-icon` | 64x64 or 96x96 | `icon-grid` layout, small decorative elements |
| `chart` | `img-chart` | Max 1200x700, no upscale | Chart screenshots from Playwright render |

All images include `object-fit` matching their treatment. No stretching or distortion permitted. Original markdown images (`![alt](path)`) are never omitted.

## Design Lint

### Per-Slide Rules

| Rule ID | Category | Check | Severity |
|---------|----------|-------|----------|
| `EQ1_OVERFLOW_TEXT` | Layout integrity | Text bounding box within safe area | error |
| `EQ1_OVERFLOW_IMAGE` | Layout integrity | Image bounding box within safe area | error |
| `EQ1_FONT_MINIMUM` | Layout integrity | All text >= 16px (exceptions: slide number 10px, caption 12px) | error |
| `EQ1_SAFE_AREA_TOP` | Layout integrity | Content below 60px top margin | warning |
| `EQ1_SAFE_AREA_BOTTOM` | Layout integrity | Content above 60px bottom margin | warning |
| `EQ1_SAFE_AREA_LEFT` | Layout integrity | Content right of 80px left margin | warning |
| `EQ1_SAFE_AREA_RIGHT` | Layout integrity | Content left of 80px right margin | warning |
| `NO1` | Anti-AI | No glassmorphism (backdrop-filter, translucent panels) | warning |
| `NO2` | Anti-AI | No large border-radius (> 8px on containers) | warning |
| `NO3` | Anti-AI | No deep box-shadows (> 4px blur or > 2 layers) | warning |
| `NO4` | Anti-AI | No neon/glow effects (text-shadow with bright colors) | warning |
| `NO5` | Anti-AI | No gradient backgrounds on content areas | warning |
| `NO6` | Anti-AI | No dashboard-style card grids with rounded corners | warning |
| `YES1_HEADER` | Editorial | Running header present (non-title slides) | info |
| `YES1_FOLIO` | Editorial | Folio/slide number present (non-title slides) | info |
| `YES1_SOURCE` | Editorial | Source citation on data-referencing slides | info |
| `YES1_DIVIDER` | Editorial | Divider line on section-divider slides | info |
| `YES4_HIERARCHY` | Typography | Title size > body size > caption size | warning |
| `YES4_RANGE` | Typography | Title 32-48px, body 18-24px, caption 10-14px | warning |
| `YES4_CAPTION_GAP` | Typography | Caption vertically separated from body by >= 16px | warning |

### Cross-Slide Rules

| Rule ID | Category | Check | Severity |
|---------|----------|-------|----------|
| `DQ1_CONSECUTIVE_SAME` | Rhythm | No 3+ consecutive slides with same layout type | warning |
| `DQ1_VISUAL_MONOTONY` | Rhythm | Density variance across deck >= threshold | info |

### Human-Likeness Score (H-Score)

Composite quality metric. Weighted sum of five dimensions, range 0.00-1.00.

| Dimension | Weight | Measures | Scoring |
|-----------|--------|----------|---------|
| `H1_layout_rhythm` | 0.25 | Variant variety ratio + consecutive-sameness penalty | unique_variants / total_slides - (consecutive_violations * 0.05) |
| `H2_editorial_polish` | 0.20 | Running header/folio coverage, source citations | (slides_with_header + slides_with_folio) / (2 * eligible_slides) |
| `H3_color_restraint` | 0.20 | Single-accent-hue adherence | 1.0 - (extra_accent_colors * 0.15) |
| `H4_typography_hierarchy` | 0.20 | Title/body/caption size separation | fraction of slides with correct 3-tier hierarchy |
| `H5_anti_ai_clean` | 0.15 | Absence of NO1-NO6 violations | 1.0 - (violation_count * 0.10), floor 0.0 |

Pass threshold: **>= 0.80**

Remediation loop: if H-score < 0.80, identify the lowest-scoring dimension, apply targeted fixes to affected slides, re-lint, re-score. Maximum 3 iterations before flagging for manual review.
