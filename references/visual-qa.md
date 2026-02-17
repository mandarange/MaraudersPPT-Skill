# Visual QA Workflow

> **After PPTX/PDF generation, visually inspect slides to catch rendering issues that automated checks cannot detect.**

## When to Run Visual QA

- After every PPTX + PDF generation (Step 8)
- Before reporting completion to the user

## QA Process

### Step 1: Generate Slide Thumbnails

Convert the generated PDF to per-slide images for inspection:

```bash
# Option A: pdftoppm (if available)
pdftoppm -png -r 150 output.pdf slide

# Option B: Playwright page screenshot
# Open each slide HTML in Playwright and capture screenshots

# Option C: LibreOffice export (fallback)
soffice --headless --convert-to pdf --outdir /tmp output.pptx
pdftoppm -png -r 150 /tmp/output.pdf slide
```

### Step 2: Visual Inspection Checklist

For each slide thumbnail, verify:

| # | Check | What to Look For |
|---|-------|-----------------|
| 1 | **Text overflow** | Any text clipped at slide edges or overlapping other elements |
| 2 | **Image placement** | Images within margins, not stretched/distorted |
| 3 | **Font rendering** | Pretendard loaded correctly, no fallback font artifacts |
| 4 | **Color accuracy** | Accent #D94F4F visible, backgrounds correct (#FFFFFF / #2C2C2C) |
| 5 | **Alignment** | Consistent title positions across slides, grid-aligned elements |
| 6 | **Chart readability** | All labels ≥ 16px, legends visible, data labels not overlapping |
| 7 | **Slide numbers** | Present on all slides except title, format `{N}/{total}` |
| 8 | **Visual coverage** | No text-only content slides (every slide has a visual element) |
| 9 | **CJK rendering** | Korean/Japanese text renders without tofu (□) or missing glyphs |
| 10 | **White space** | Adequate breathing room, no cramped layouts |

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

## Automated vs Manual QA

| Automated (Step 7) | Visual QA (This Step) |
|--------------------|----------------------|
| Pixel-based boundary checks | Rendering fidelity |
| Bounding box intersection | Visual balance/aesthetics |
| Font size compliance | Font rendering quality |
| Margin calculations | Overall slide readability |

**Both are required.** Automated checks catch measurable violations; visual QA catches rendering and aesthetic issues that math cannot detect.
