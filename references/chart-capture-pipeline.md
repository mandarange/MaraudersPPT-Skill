# Chart Capture Pipeline

HTML → Browser Capture → PNG stable pipeline for chart/infographic screenshot generation.

Applies to **Priority 2** images (`type=chart`) in the 3-priority image system.

---

## Why This Pipeline Exists

| Failure Mode | Cause | Solution |
|---|---|---|
| PNG not generated | External script dependency | Single browser tool, one-shot capture |
| Unwanted whitespace | full-page screenshot + body padding | element screenshot + zero-padding CSS + auto-crop |
| Edge clipping | viewport smaller than content | bounding box measurement → viewport auto-expand (48px gutter) |
| Aspect ratio distortion | arbitrary clip dimensions | preserve measured bounding box ratio exactly |
| PNG is viewport-sized | agent used page screenshot instead of element screenshot | dimension sanity check — PNG > 1.5× bbox → re-capture |
| File missing on disk | async I/O race | filesystem proof gate — verify before path insertion |
| Render HTML deleted mid-capture | temp file cleanup | keep HTML until capture verified |

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

async function captureChart(html, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

  // Phase 2: navigate + render wait
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);

  // Phase 3: measure bbox + resize viewport
  const el = await page.locator('.capture-root');
  let box = await el.boundingBox();
  if (!box) throw new Error('.capture-root not found');
  await page.setViewportSize({
    width:  Math.ceil(box.x + box.width  + 48),
    height: Math.ceil(box.y + box.height + 48),
  });
  await page.waitForTimeout(100);
  box = await el.boundingBox();  // re-measure after reflow

  // Phase 4: element screenshot (NEVER full-page)
  await el.screenshot({ path: outputPath, type: 'png' });

  // Phase 5: dimension sanity check
  const sharp = require('sharp');
  const meta = await sharp(outputPath).metadata();
  if (meta.width > box.width * 1.5 || meta.height > box.height * 1.5) {
    fs.unlinkSync(outputPath);
    throw new Error('PNG dimensions exceed 1.5× bbox — wrong capture method');
  }

  // Phase 6: filesystem proof gate
  const stat = fs.statSync(outputPath);
  if (stat.size === 0) throw new Error(`Empty file: ${outputPath}`);
  if (stat.size < 1024) console.warn(`Warning: ${outputPath} < 1KB — possible blank`);

  await browser.close();
  return outputPath;
}
```

---

## 9-Phase Protocol

### Phase 1: Self-Contained HTML Generation

Use `render_chart_page(chart_type, data)` from `templates/charts/`.

Requirements:
- Output is a **complete** HTML document (`<!DOCTYPE html>…`)
- All CSS is inline (no external CDN links)
- No JavaScript dependencies
- `<meta charset="utf-8">` present
- `.capture-root` div contains the visual content
- `position: relative !important` overrides the slide-mode `position: absolute`

**Critical CSS rules** (NEVER omit or change — each prevents a specific capture failure):

| CSS Rule | Reason |
|---|---|
| `* { margin: 0; padding: 0; }` | Remove browser default margins (body has 8px by default) |
| `body { width: fit-content }` | Body shrinks to content instead of expanding to viewport |
| `body { display: inline-block }` | REQUIRED for `fit-content` to actually shrink-wrap |
| `body { overflow: hidden }` | Prevent scrollbars |
| `.capture-root { display: inline-block }` | Capture target bbox matches content exactly |
| `.capture-root { margin: 0; padding: 0 }` | No outer spacing leaking into element screenshot |

**Forbidden on body or .capture-root:**
- `width: 100%`, `display: block`, or fixed `width`/`height` in CSS (viewport expansion)
- `body { padding: ... }` (leaks into layout even if not captured directly)
- External CDN links (breaks offline)

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
await page.waitForTimeout(400);  // minimum — CSS paint + font settle
```

- `waitUntil: 'networkidle'` — ensures all resources loaded
- **400ms minimum** — covers CSS transitions and font rendering
- Complex diagrams with many elements: 800ms
- CSS transitions present: transition duration + 100ms
- Without this wait, `display: inline-block` + `fit-content` may not have resolved content size yet

### Phase 3: Bounding Box Measurement + Viewport Adjustment

```javascript
const el = await page.locator('.capture-root');
let box = await el.boundingBox();
if (!box) throw new Error('.capture-root not found or invisible');

// Expand viewport to fully contain element + 48px safety gutter (24px × 2 sides)
await page.setViewportSize({
  width:  Math.ceil(box.x + box.width  + 48),
  height: Math.ceil(box.y + box.height + 48),
});
await page.waitForTimeout(100);

// MUST re-measure — viewport resize triggers reflow
box = await el.boundingBox();
```

- Browser does NOT render content outside viewport — element screenshot clips at viewport edge
- 48px gutter (24px per side) prevents sub-pixel edge clipping
- **Re-measure after resize is mandatory** — reflow may change element position/size

### Phase 4: Element Screenshot

```javascript
await el.screenshot({ path: outputPath, type: 'png' });
```

| Method | Allowed |
|--------|---------|
| `el.screenshot()` | **YES** — captures exactly the element |
| `page.screenshot()` | **NO** — captures entire viewport (whitespace) |
| `page.screenshot({ fullPage: true })` | **PROHIBITED** — unpredictable dimensions |

### Phase 5: Dimension Sanity Check

```javascript
const sharp = require('sharp');
const meta = await sharp(outputPath).metadata();

if (meta.width > box.width * 1.5 || meta.height > box.height * 1.5) {
  fs.unlinkSync(outputPath);
  // Re-capture with correct element selector
  throw new Error('PNG dimensions > 1.5× bbox — likely viewport capture instead of element');
}
```

**Why this check exists:** AI agents sometimes ignore element screenshot instructions and fall back to viewport/full-page capture. Prompt instructions alone cannot guarantee the capture method — the output dimensions are the only reliable verification.

If sanity check fails → delete PNG, re-attempt from Phase 4 with verified `.capture-root` selector.

### Phase 6: Filesystem Proof Gate

```javascript
const stat = fs.statSync(outputPath);
if (stat.size === 0) throw new Error(`Empty: ${outputPath}`);
if (stat.size < 1024) console.warn(`Warning: ${outputPath} < 1KB — possible blank`);
```

After `screenshot()` returns, **always** verify:
1. File exists at `outputPath`
2. File size > 0 bytes
3. Size < 1 KB → log warning (possible blank render)

On failure:
1. Wait 800ms
2. Retry from Phase 2
3. Second failure → treat as HTML/CSS problem, fix and retry
4. **Never proceed with missing/empty file**

### Phase 7: Auto-Crop (Pillow)

```python
from templates.charts.trim import autocrop

autocrop("chart-05-throughput.png", padding=4, threshold=250)
```

| Parameter | Default | Description |
|---|---|---|
| `padding` | 4 | Minimum whitespace to preserve around content (px) |
| `threshold` | 250 | Channel value >= this → background pixel |

- **Threshold-based detection**: tolerates anti-aliasing artifacts near edges (exact-match would miss `(254,254,255)` pixels)
- **RGBA support**: fully transparent pixels (alpha == 0) are treated as background
- Returns immediately if existing padding <= `padding` (already tight)
- Runs in-place if no `dst` argument
- Requires `Pillow` (`pip install Pillow`) — optional enhancement, skip if unavailable

### Phase 8: Visual Verification

After generation, verify the PNG is usable:

1. Dimensions > 100px each (not a degenerate crop)
2. Not all-background (at least some content pixels)
3. Aspect ratio approximately matches expected chart proportions
4. No edge clipping (chart content fully visible)
5. No excessive whitespace

Problem found → fix HTML/CSS → retry from Phase 2.

Integration with visual QA system: see [visual-qa.md](visual-qa.md).

### Phase 9: Manifest + HTML Insertion

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

// Slide HTML insertion (only AFTER filesystem proof gate passes)
<img src="/absolute/path/to/assets/chart-05-throughput.png"
     alt="Throughput comparison" width="1720" height="760"
     style="object-fit: contain;" />
```

**Never insert image path into HTML/Markdown before filesystem proof gate passes.**

---

## Failure Handling

| Failure | Recovery |
|---------|----------|
| `.capture-root` not found | Re-check HTML generation — missing `render_chart_page()` or `wrap_capture_html()` |
| `boundingBox()` returns null | Element not visible — check CSS `display`, `visibility`, `opacity` |
| PNG dimensions > 1.5× bbox | Wrong capture method — delete PNG, re-capture with element screenshot |
| Screenshot file 0 bytes | Browser crash or timeout — wait 800ms, retry from Phase 2 with fresh page |
| Screenshot file < 1 KB | Possible blank render — check data input and CSS |
| Crop produces tiny image (< 100px) | All-background render — check data input |
| `Pillow` not installed | Skip Phase 7 (auto-crop is optional) |
| Second retry fails | Fall through to next priority level (Priority 2 → Priority 3) |

---

## Batch Capture (Wave 4)

For multi-chart decks, reuse a single browser instance:

```javascript
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

for (const chart of charts) {
  const page = await context.newPage();
  // ... Phase 2–8 per chart ...
  await page.close();
}

await browser.close();
```

See [parallel-execution.md](parallel-execution.md) Wave 4 for the full batch strategy.

---

## Render HTML Lifecycle

For iterative workflows where charts are regenerated:

```
Filename: <chart-name>.render_v{N}.html
- Initial: render_v1.html
- Revision: render_v2.html (N+1)
- SSOT: keep only latest version, delete older after capture succeeds
- Capture failure: keep current HTML (never delete), delete PNG only, retry
```
