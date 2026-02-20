# Design Diagnosis — Why Output Looks "AI-Generated"

> This document identifies the specific files, functions, and design decisions
> that cause MaraudersPPT output to look templated, uniform, and machine-generated
> rather than human-designed.

---

## Executive Summary

The current system produces **technically correct** but **aesthetically monotonous** output.
Six root causes have been identified, each traced to specific code and specification locations.
The problem is NOT decoration deficiency — it is structural uniformity and missing editorial craft.

---

## Root Cause 1: Zero Layout Variation Within Types

**Severity**: Critical
**Files**: `SKILL.md` (lines 522-549), `docs/design-spec.md` (Section 6)

**Diagnosis**: 23 layout types exist, but each type has exactly ONE visual expression.
Every `bullet-list` slide looks identical to every other `bullet-list` slide.
Every `image-text` slide uses the same 60:40 split. Every `kpi-cards` slide
uses the same grid. In a 15+ slide deck, this creates deadly visual repetition.

**Evidence**:

- `SKILL.md` defines types but zero variants per type
- `docs/design-spec.md` Section 6 lists layouts with single composition each
- No variant selection logic exists anywhere in the codebase
- `DeckRhythm` in `SKILL.md` (line 324) checks `visual_variety_score >= 0.6`
  but has NO mechanism to achieve variety — only validation exists, not generation

**What humans do differently**:
Professional designers use 2-3 compositions per layout type:

- Bullet-list: left-aligned vs. two-column vs. numbered-with-dividers
- Image-text: 60:40 vs. 40:60 vs. full-bleed with text overlay
- KPI: horizontal row vs. stacked vs. hero-number-with-context
- Section divider: centered text vs. asymmetric with section number vs. image band

---

## Root Cause 2: No Design Token System (Hardcoded Everything)

**Severity**: High
**Files**: `templates/charts/base.py`, all 8 chart template files

**Diagnosis**: Every style value is hardcoded directly in CSS strings inside Python files.
Colors, font sizes, spacing, radii — all are literal values scattered across 10+ files.
This makes theming impossible and creates maintenance nightmares.

**Evidence**:

```python
# base.py — hardcoded content area
CONTENT_CSS = """
.content {
  position: absolute;
  left: 100px;     # ← hardcoded
  top: 220px;      # ← hardcoded
  width: 1720px;   # ← hardcoded
  height: 760px;   # ← hardcoded
  color: #1A1A1A;  # ← hardcoded
  background: #FFFFFF;  # ← hardcoded
}"""

# kpi_cards.py — hardcoded everywhere
".kpi-card { border: 1px solid #E0E0E0; border-radius: 2px; }"
".kpi-value { font-size: 56px; color: #1A1A1A; font-weight: 700; }"
".kpi-label { font-size: 16px; color: #555555; }"
```

**Impact**: Cannot create alternate themes. Cannot adjust spacing proportions.
Cannot offer "modern editorial" vs "consulting minimal" styles.

---

## Root Cause 3: Missing Editorial Design Details

**Severity**: High
**Files**: `SKILL.md` (entire Phase 4), `docs/design-spec.md` (Section 5-6)

**Diagnosis**: The specification mentions slide numbers (bottom-right, 10pt) but
omits ALL other editorial details that distinguish professional presentations
from templates:

**Missing elements** (that human designers always include):

1. **Running header / section label** — small text showing current section name
   (e.g., "01 Background" in top-left corner, 10pt, light gray)
2. **Folio / page indicator** — beyond just "3/24", professional decks show
   section context ("Section 2 of 4 | Slide 3")
3. **Figure/exhibit numbers** — charts and tables get "Exhibit 1:", "Figure 3:"
4. **Source/attribution lines** — properly formatted, consistent positioning
5. **Thin divider lines** — 1px lines separating title from content, or footer
6. **Caption system** — unified caption treatment for images, charts, tables
7. **Footnote area** — distinct from caption, for caveats and definitions

**Evidence**: Search for "running header", "folio", "figure number", "exhibit",
"footnote" across all spec files returns zero results. Only "caption" appears
in `design-spec.md` Section 3.3 (font definition only, no placement rules).

---

## Root Cause 4: Chart/Table Templates Lack Insight Layer

**Severity**: High
**Files**: `templates/charts/*.py` (all 8 modules)

**Diagnosis**: Charts render raw data competently, but lack the
"consulting layer" that makes data slides valuable:

**What's missing**:

1. **Insight caption** — One-line interpretation below/above the chart
   ("Key: Q1 outperformed all quarters at 95%, +17pt above average")
2. **Single-point emphasis** — Only `is-max` and `is-accent` exist (binary).
   No visual callout (circle, annotation line, label offset) for THE key finding.
3. **Annotation layer** — Leader lines pointing to notable data points,
   contextual labels ("Target: 90%"), reference lines
4. **Delta/comparison annotations** — Showing change between data points
   with bridge lines or waterfall connections

**Evidence from chart templates**:

```python
# bar_chart.py — renders bars and values, nothing more
# No annotation parameter, no insight_caption, no callout support
def render(data: list[dict[str, Any]]) -> str:
    # ... just bars, labels, values

# kpi_cards.py — renders label+value+delta, no insight context
# No trend sparkline, no target comparison, no annotation
```

**What McKinsey/BCG do**: Every data slide has a "so what" annotation.
A bar chart without an insight caption is just data, not communication.

---

## Root Cause 5: Image Treatment Is "Insert and Forget"

**Severity**: Medium-High
**Files**: `references/image-generation.md` (Section 4.4-4.5)

**Diagnosis**: Images are placed into slides with basic sizing rules
but NO treatment pipeline:

**Current behavior** (from `image-generation.md`):

- Images get `object-fit: cover` with fixed dimensions
- Title/closing backgrounds get opacity 10-15%
- That's it — no crop strategy, no tone unification, no caption

**What's missing**:

1. **Crop-to-focus**: Centering on the subject, using rule-of-thirds
2. **Tone unification**: Mono/desaturated filter to match deck palette
3. **Readability overlay**: When text sits on image, scrim or gradient overlay
4. **Caption/source pairing**: "Figure 3: System architecture (Source: Engineering team)"
5. **Background panel strategy**: For complex images, solid text panel instead of overlay

**Evidence**: `image-generation.md` Section 4.4 shows layout adaptation table.
All entries are pure sizing — zero treatment rules. No filter, crop, or overlay logic.

---

## Root Cause 6: Single Color/Typography Scheme (No Theming)

**Severity**: Medium
**Files**: `docs/design-spec.md` (Sections 2-3), `SKILL.md` (lines 466-498)

**Diagnosis**: The entire system has ONE fixed color palette and ONE typography stack.
Every deck looks identical at the macro level. Professional presentation systems
offer at minimum 3-5 theme presets that vary color temperature, type weight, and motif.

**Evidence**:

- `design-spec.md` Section 2: Single palette (#FFFFFF, #1A1A1A, #D94F4F)
- `SKILL.md` Design Rules Summary: same palette repeated
- PRD Section 7.3 explicitly says: "Theme presets (dark, minimal, vibrant) have been removed.
  Single theme (professional) with minimal color principle applied."
- No CSS variable usage, no theme parameter in any template

**Impact**: A consulting deck, a product pitch, and an academic presentation
all look identical. The user cannot differentiate their output's "personality."

---

## Secondary Issues

### 6a. Deck Rhythm Validation Without Generation

`SKILL.md` Phase 3.2 defines `DeckRhythm` validation rules
(`max_consecutive_same_density: 2`, `visual_variety_score >= 0.6`)
but provides NO mechanism to ACHIEVE these targets.
Validation without generation capability = guaranteed failures.

### 6b. No Editorial Grid Beyond 8px Snap

The 8px grid system handles spacing but not editorial layout:

- No column grid (12-column or similar) for asymmetric compositions
- No baseline grid for typography alignment across slides
- No named regions (title zone, body zone, footer zone defined but not as named CSS areas)

### 6c. Comparison Template Uses ::before (Anti-Pattern)

`comparison.py` line 52-60 uses `::before` pseudo-element for the divider line,
which is listed as a prohibited pattern in `design-spec.md` Section 1.1
("Forbidden Pattern: `::before` decorative bar").

### 6d. Process Flow Uses Text Arrow Instead of SVG

`process_flow.py` uses Unicode `→` character for arrows between steps,
while `svg-components.md` Section 2.4 provides proper SVG arrow markers.
Text arrows render inconsistently across fonts and sizes.

---

## Priority Fix Order

| Priority | Root Cause                  | Effort |             Impact              |
| :------: | --------------------------- | :----: | :-----------------------------: |
|    1     | Layout Variant System (RC1) |  High  | Highest — eliminates repetition |
|    2     | Design Token System (RC2)   |  High  |   Enables all downstream work   |
|    3     | Editorial Details (RC3)     | Medium |  "Human touch" differentiator   |
|    4     | Chart Annotations (RC4)     | Medium | Consulting-quality data slides  |
|    5     | Theme Packs (RC6)           | Medium |    Personality/customization    |
|    6     | Image Treatment (RC5)       | Medium |   Professional image handling   |

---

## Measurement: Before vs After

| Metric                        |       Current       |                   Target                   |
| ----------------------------- | :-----------------: | :----------------------------------------: |
| Layout variants per type      |          1          |                    2-3                     |
| Themes available              |          1          |                     5                      |
| Design tokens (centralized)   |          0          |                    50+                     |
| Editorial details per slide   |  1 (slide number)   | 4+ (folio, section label, figure#, source) |
| Chart annotation support      | Binary (max/accent) |  Full (caption, callout, reference line)   |
| Image treatment strategies    |    1 (size+fit)     |       4 (crop, tone, overlay, panel)       |
| Human-likeness score system   |        None         |          5-axis automated scoring          |
| visual_variety_score achieved |  ~0.3 (estimated)   |                  >= 0.75                   |
