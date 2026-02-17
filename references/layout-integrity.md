# Layout Integrity Verification (Step 7)

> **The layout system must NEVER break. Text overflow is a CRITICAL failure.**
> If Step 2.9 (Content Distillation) worked correctly, overflow should be impossible.
> This step is the final safety net — NOT the primary defense.

## 7.1 Safe Area Dimensions (Pixel-Based)

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

## 7.2 Maximum Renderable Text Per Area

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

## 7.3 Verification Checklist (Auto-Run After EACH Slide)

| # | Verification Item | On Failure | Max Attempts |
|---|-------------------|-----------|:------------:|
| 1 | **Text within body area** (y + height ≤ 944px) | Font reduction cascade | 3 |
| 2 | **Title within title area** (y + height ≤ 188px) | Rewrite title shorter (NEVER truncate with `...`) | 1 |
| 3 | **No element overlap** (bounding box intersection = 0) | Reposition → regenerate | 3 |
| 4 | **Margins respected** (all content x ≥ 68px, x+w ≤ 1852px) | Reposition | 1 |
| 5 | **Image ratio preserved** (aspect ratio distortion < 2%) | Restore original ratio | 1 |
| 6 | **Grid alignment** (coordinates snap to 8px grid) | Coordinate correction | 1 |

## 7.4 Font Reduction Cascade (Last Resort Only)

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

## 7.5 URL / Long-Text Rendering Rules

> **URLs, file paths, and code snippets need special wrap treatment to prevent visual breakage.**

### CSS Rules for Long Text (MANDATORY in all slide HTML)

```css
/* Apply to ALL slide body text containers */
.slide-body {
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: none;            /* Never auto-hyphenate */
}

/* URLs and code — monospace, controlled wrap */
.slide-body a, .slide-body code, .slide-url {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14pt;          /* Slightly smaller than body for URLs */
  word-break: normal;       /* Avoid mid-token breaks */
  overflow-wrap: break-word;
  color: #555555;
}
```

### URL Display Policy

| URL Length | Action |
|:----------:|--------|
| ≤40 chars | Display inline as-is |
| 41–80 chars | Display on own line, full URL, monospace 14pt |
| >80 chars | **Shorten to display label** — e.g., `open-vsx.org/.../marauders-map-md` |
| Multiple URLs | Move to footer area or "Links" appendix slide |

**Rule**: URLs must NEVER wrap mid-domain. If a URL must break, break at `/` path separators only.

```
❌ WRONG (URL breaks mid-word):
   https://open-vsx.org/extension/manda
   range/marauders-map-md

✅ CORRECT (break at path separator):
   https://open-vsx.org/extension/
   mandarange/marauders-map-md

✅ BEST (shortened display):
   open-vsx.org/.../marauders-map-md
```

### File Path / Code Rendering

- File paths: monospace, 14pt, `#555555`
- Code snippets: respect `code` layout (dark background), max 12 lines per slide
- Long single-line code: `overflow-x: auto` with horizontal scroll hint, NOT wrap

## 7.6 The Golden Rule

```
IF text overflows the slide:
  THE SLIDE HAS TOO MUCH TEXT. Period.
  Go back to Step 2.9 and distill the content further.
  Reducing font size to fit more text is NEVER the answer.
  A slide with 16pt text crammed wall-to-wall is worse than overflow.
```
