# Chart Capture Pipeline

HTML → Browser Capture → PNG stable pipeline for chart/infographic screenshot generation.

Applies to **Priority 2** images (`type=chart`) in the 3-priority image system.

---

## Quick Reference

```python
from templates.charts import render_chart_page

html = render_chart_page("bar_chart", [
    {"label": "Before", "value": 42, "display": "42m"},
    {"label": "After",  "value": 8,  "display": "8m", "max": True},
])
```

```javascript
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function captureChart(html, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

  // Phase 2: Navigate + render wait
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);

  // Phase 3: Measure bounding box + resize viewport
  const el = await page.locator('.capture-root');
  const box = await el.boundingBox();
  if (!box) throw new Error('.capture-root not found');
  await page.setViewportSize({
    width:  Math.ceil(box.x + box.width  + 20),
    height: Math.ceil(box.y + box.height + 20),
  });
  await page.waitForTimeout(100);

  // Phase 4: Element screenshot (NEVER full-page)
  await el.screenshot({ path: outputPath, type: 'png' });

  // Phase 5: Filesystem proof gate
  const stat = fs.statSync(outputPath);
  if (stat.size === 0) throw new Error(`Empty file: ${outputPath}`);

  await browser.close();
  return outputPath;
}
```

---

## 8-Phase Protocol

### Phase 1: Self-Contained HTML Generation

Use `render_chart_page(chart_type, data)` from `templates/charts/`.

Requirements:
- Output is a **complete** HTML document (`<!DOCTYPE html>…`)
- All CSS is inline (no external links)
- No JavaScript dependencies
- `<meta charset="utf-8">` present
- `.capture-root` div contains the visual content
- `position: relative !important` overrides the slide-mode `position: absolute`
- Body uses `width: fit-content; height: fit-content` — no extra whitespace

For custom (non-template) HTML, use `wrap_capture_html()` from `templates/charts/base.py` directly:

```python
from templates.charts.base import wrap_capture_html

html = wrap_capture_html(
    inner='<div class="my-diagram">…</div>',
    css='.my-diagram { display: flex; gap: 24px; }',
    width=1720,
    height=760,
)
```

### Phase 2: Browser Navigation + Render Wait

```javascript
await page.setContent(html, { waitUntil: 'networkidle' });
await page.waitForTimeout(300);  // CSS paint settle
```

- `waitUntil: 'networkidle'` — ensures all resources loaded
- 300ms settle — covers CSS transitions and font rendering
- For font-heavy content, increase to 500ms

### Phase 3: Bounding Box Measurement + Viewport Adjustment

```javascript
const el = await page.locator('.capture-root');
const box = await el.boundingBox();
await page.setViewportSize({
  width:  Math.ceil(box.x + box.width  + 20),
  height: Math.ceil(box.y + box.height + 20),
});
await page.waitForTimeout(100);
```

- Viewport must fully contain `.capture-root` bounding box
- 20px padding prevents sub-pixel clipping at edges
- Second wait allows layout reflow after resize

### Phase 4: Element Screenshot

```javascript
await el.screenshot({ path: outputPath, type: 'png' });
```

**CRITICAL**: Always use **element** screenshot on `.capture-root`.

| Method | Allowed |
|--------|---------|
| `el.screenshot()` | YES — captures exactly the chart |
| `page.screenshot()` | NO — captures viewport (whitespace) |
| `page.screenshot({ fullPage: true })` | PROHIBITED — unpredictable dimensions |

### Phase 5: Filesystem Proof Gate

```javascript
const stat = fs.statSync(outputPath);
if (stat.size === 0) throw new Error(`Empty file: ${outputPath}`);
```

After `screenshot()` returns, **always** verify:
1. File exists at `outputPath`
2. File size > 0 bytes
3. If size < 1 KB, log warning (possible blank render)

### Phase 6: Pillow Auto-Crop (Optional)

```python
from templates.charts.trim import autocrop

autocrop("chart-05-throughput.png", pad=8, bg=(255, 255, 255))
```

- Trims surrounding whitespace using colour-difference detection
- `pad=8` preserves 8px breathing room (matches 8px grid)
- `bg=(255,255,255)` — default white; change for dark themes
- Runs in-place if no `dst` argument
- Requires `Pillow` (`pip install Pillow`)

### Phase 7: Visual Verification

After generation, verify the PNG is usable:

1. Dimensions check — width and height should be reasonable (> 100px each)
2. Not all-white — at least some non-background pixels present
3. Aspect ratio — should approximately match the expected chart proportions

Integration with the visual QA system: see [visual-qa.md](visual-qa.md).

### Phase 8: Manifest + HTML Insertion

```javascript
// Manifest entry
{
  "type": "chart",
  "generator": "playwright-chart",
  "data_hash": "sha256(data + chart_type + template_version)",
  "file_size_bytes": stat.size,
  "width": box.width,
  "height": box.height
}

// Slide HTML insertion
<img src="/absolute/path/to/assets/chart-05-throughput.png"
     alt="Throughput comparison" width="1720" height="760"
     style="object-fit: contain;" />
```

---

## Failure Handling

| Failure | Recovery |
|---------|----------|
| `.capture-root` not found | Re-check HTML generation — missing `render_chart_page()` or `wrap_capture_html()` |
| `boundingBox()` returns null | Element not visible — check CSS `display`, `visibility`, `opacity` |
| Screenshot file 0 bytes | Browser crash or timeout — retry once with fresh browser instance |
| Crop produces tiny image (< 100px) | Possible all-white render — check data input and CSS |
| `Pillow` not installed | Skip Phase 6 (auto-crop is optional enhancement) |

On any failure, fall through to the next priority level in the image pipeline (Priority 2 → Priority 3).

---

## Batch Capture (Wave 4)

For multi-chart decks, reuse a single browser instance:

```javascript
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

for (const chart of charts) {
  const page = await context.newPage();
  // ... Phase 2-5 per chart ...
  await page.close();
}

await browser.close();
```

See [parallel-execution.md](parallel-execution.md) Wave 4 for the full batch strategy.
