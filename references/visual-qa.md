# Visual QA Workflow (Phase 5.5)

> **After PDF generation, visually inspect slides to catch rendering issues that automated checks cannot detect.**

## When to Run Visual QA

- After every PDF generation (Phase 5 assembly)
- Before reporting completion to the user

## QA Process

### Step 1: Generate Slide Thumbnails

Convert the generated PDF to per-slide images for inspection:

```bash
# Option A: pdftoppm (if available)
pdftoppm -png -r 150 output.pdf slide

# Option B: Playwright page screenshot
# Open each slide HTML in Playwright and capture screenshots

# Option C: direct PDF thumbnails (fallback)
pdftoppm -jpeg -r 150 output.pdf slide
```

### Step 1.5: Automated Design Lint (Pre-Visual)

Before manual visual inspection, run the static design lint:

```python
from design.lint import lint_deck, human_likeness_score

issues = lint_deck(slide_htmls, variant_history=variant_ids)
errors = [i for i in issues if i.severity == "error"]
result = human_likeness_score(slide_htmls)
```

#### Lint Rule Categories

| Category          | Rules                                                   | Severity      |
| ----------------- | ------------------------------------------------------- | ------------- |
| Layout integrity  | EQ1*OVERFLOW*_, EQ1*FONT_MINIMUM, EQ1_SAFE_AREA*_       | error/warning |
| Anti-AI guards    | NO1-NO6 (glass, radius, shadow, neon, color, dashboard) | warning       |
| Editorial quality | YES1 (header, folio, source, divider)                   | info          |
| Typography        | YES4 (hierarchy, range, caption gap)                    | warning       |
| Rhythm            | DQ1_CONSECUTIVE_SAME, DQ1_VISUAL_MONOTONY               | warning/info  |

#### Human-Likeness Score (H-Score)

| Dimension               | Weight | Measures                                        |
| ----------------------- | ------ | ----------------------------------------------- |
| H1_layout_rhythm        | 0.25   | Variety ratio + consecutive-sameness penalty    |
| H2_editorial_polish     | 0.20   | Running header/folio coverage, source citations |
| H3_color_restraint      | 0.20   | Single-accent-hue adherence                     |
| H4_typography_hierarchy | 0.20   | Title/body/caption size separation              |
| H5_anti_ai_clean        | 0.15   | Absence of NO1-NO6 violations                   |

Threshold: >= 0.80 to pass. Below threshold: identify lowest dimension, apply targeted fixes, re-score (max 3 iterations).

### Step 2: Visual Inspection Checklist

For each slide thumbnail, verify:

| #   | Check                          | What to Look For                                                              |
| --- | ------------------------------ | ----------------------------------------------------------------------------- |
| 1   | **Text overflow**              | Any text clipped at slide edges or overlapping other elements                 |
| 2   | **Image placement**            | Images within margins, not stretched/distorted                                |
| 3   | **Font rendering**             | Pretendard loaded correctly, no fallback font artifacts                       |
| 4   | **Color accuracy**             | Accent #D94F4F visible, backgrounds correct (#FFFFFF / #2C2C2C)               |
| 5   | **Alignment**                  | Consistent title positions across slides, grid-aligned elements               |
| 6   | **Chart readability**          | All labels ≥ 16px, legends visible, data labels not overlapping               |
| 7   | **Slide numbers**              | Present on all slides except title, format `{N}/{total}`                      |
| 8   | **Visual coverage**            | No text-only content slides (every slide has a visual element)                |
| 9   | **CJK rendering**              | Korean/Japanese text renders without tofu (□) or missing glyphs               |
| 10  | **White space**                | Adequate breathing room, no cramped layouts                                   |
| 11  | **Ellipsis truncation**        | Scan ALL text for `...` — any truncated text = CRITICAL BUG, must rewrite     |
| 12  | **Title–body duplication**     | Title text repeated in body bullets = wasted space, must deduplicate          |
| 13  | **URL integrity**              | URLs not broken mid-domain, display-shortened if >80 chars, readable          |
| 14  | **Section structure**          | H3 sub-headings preserved as bold sub-headers or separate slides              |
| 15  | **Information density**        | Each slide conveys unique info — no "item list + truncated sentence" patterns |
| 16  | **Visual Blueprint adherence** | Composition matches blueprint spec for each slide                             |
| 17  | **Deck rhythm**                | Density variation across deck (no 3+ same-density consecutive slides)         |
| 18  | **Coverage report**            | All source sections accounted for (coverage_pct = 100%)                       |
| 19  | **Image Manifest consistency** | Cached images still valid, no stale references                                |
| 20  | **Mood arc**                   | Emotional progression follows story arc (tense→hopeful→confident)             |
| 21  | **Design lint clean**          | No `error` severity lint issues in `lint_deck()` output                       |
| 22  | **H-Score >= 0.80**            | `human_likeness_score()` overall >= 0.80                                      |
| 23  | **Anti-AI compliance**         | No glassmorphism, large radius, deep shadows, neon glow                       |
| 24  | **Editorial elements**         | Running headers, folios, source citations present                             |

### Step 3: Report Issues

If any visual issues are found:

```
⚠️ Visual QA Issues Found:
  Slide 4: Title text clipped at right margin
  Slide 7: Chart legend overlaps bar labels
  Slide 12: Korean text showing fallback font

Action: Regenerating affected slides...
```

Fix issues and re-run QA on affected slides only.

### Step 4: Automated Quality Gates (MANDATORY)

Compute the following metrics before final completion:

Scope definition:

- `content_slides` = all slides except `title`, `section-divider`, `appendix-divider`, `closing`
- `text_only_content_slides` = content slides with no image/chart/table/code/infographic visual
- `slides_with_ellipsis` = slides with `...` in title/body/caption text (exclude chart labels, slide numbers)

| Metric                         | Formula                                                                               | Target   | Hard Fail Condition |
| ------------------------------ | ------------------------------------------------------------------------------------- | -------- | ------------------- |
| `text_only_slide_ratio`        | `text_only_content_slides / total_content_slides * 100`                               | `0%`     | `> 0%`              |
| `markdown_token_leakage_count` | Count of leaked tokens (`###`, `##`, `#`, ```,`, raw `[text](url)`, raw list markers) | `0`      | `> 0`               |
| `truncated_sentence_ratio`     | `slides_with_ellipsis / total_content_slides * 100`                                   | `0%`     | `> 0%`              |
| `duplicate_text_ratio`         | `slides_with_title_body_overlap_over_50pct / total_slides * 100`                      | `< 5%`   | `>= 5%`             |
| `coverage_pct`                 | `truly_cut + in_deck + in_appendix + in_speaker_notes == total_source_sections`       | `100%`   | `< 100%`            |
| `blueprint_adherence_ratio`    | `slides_matching_blueprint / total_slides * 100`                                      | `>= 90%` | `< 80%`             |

If any hard fail condition is met:

```
❌ Quality Gate Failed

- Do NOT finalize output as "complete"
- Regenerate affected slides
- Recompute metrics
- Only pass when all gates meet targets
```

## Automated vs Manual QA

| Automated (Phase 5.1)       | Visual QA (This Step)     |
| --------------------------- | ------------------------- |
| Pixel-based boundary checks | Rendering fidelity        |
| Bounding box intersection   | Visual balance/aesthetics |
| Font size compliance        | Font rendering quality    |
| Margin calculations         | Overall slide readability |

**Both are required.** Automated checks catch measurable violations; visual QA catches rendering and aesthetic issues that math cannot detect.
