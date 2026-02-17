# Parallel Execution Optimization (Section 8)

> **For LLMs that support parallel sub-agent execution** (e.g., OpenCode with `task(run_in_background=true)`),
> the workflow should be parallelized across independent tasks to minimize total conversion time.

## Wave Architecture

The conversion pipeline is organized into **5 waves**. Tasks within each wave execute in parallel; waves execute sequentially.

```
Wave 0 — Gate (instant)
└── Activation Guard: Verify MaraudersMD2PPT keyword → PASS or HARD FAIL

Wave 1 — Sequential (fast, <1s)
├── Step 0: Execution Contract + Environment Setup
├── Step 1: Input Reception
├── Step 2: MD Parsing
├── Step 2.3: Core Keyword Extraction (CRITICAL)
├── Step 2.5: Visual Content Detection
├── Step 2.7: Executive Summary Generation
├── Step 2.8: Slide Flow Optimization
├── Step 2.9: Content Distillation
└── Step 3: Slide Mapping

Wave 2 — PARALLEL (main bottleneck, optimize here)
├── [Background] AI Image Generation — MANDATORY for ALL non-visual slides
├── [Background] Chart HTML Generation (templates/charts/ → render_chart())
├── [Background] Chart Screenshot Capture (Playwright batch)
└── [Foreground] Non-chart Slide HTML Generation

Wave 3 — PARALLEL (asset collection)
├── Collect AI image results (background_output())
├── Collect chart screenshots
└── Post-process images (Sharp resize/optimize if needed)

Wave 4 — Sequential (assembly)
├── Assemble all slide HTMLs with final assets
├── Adapt layouts for slides receiving AI images (text-body → image-text, etc.)
├── PPTX Conversion (html2pptx.js)
└── PDF Generation (Playwright page.pdf())

Wave 5 — Sequential (verification)
├── Layout Integrity Verification (Step 7)
├── Visual Coverage Audit (confirm 0% text-only content slides)
├── Output file writing (versioned)
└── Completion report + Diagnostic Report
```

## Wave 2 Parallelization Detail

Wave 2 is the primary bottleneck. The following tasks are **fully independent** and should run concurrently:

| Task | Agent/Method | Blocking? | Typical Duration |
|------|-------------|-----------|-----------------|
| AI Image Generation | Cursor native image gen / `task(run_in_background=true)` | No (background) | 5–15s per image |
| Chart HTML Rendering | `render_chart(type, data)` — Python templates | No (instant) | <100ms per chart |
| Chart Screenshots | Playwright batch — one browser, multiple pages | No (background) | 1–3s per chart |
| Slide HTML Generation | Sequential HTML file writes | Yes (foreground) | <1s per slide |

**Optimal execution pattern (OpenCode):**

```python
# Wave 2: Fire all independent tasks in parallel

# 1. AI Images — background (longest task, start first)
image_tasks = []
for slide in slides_needing_images:
    tid = task(
        run_in_background=True,
        prompt=f"Generate photorealistic image: {slide.image_prompt}",
        # ... native image gen (Cursor) or background agent (OpenCode)
    )
    image_tasks.append(tid)

# 2. Chart rendering — instant, no background needed
chart_htmls = {}
for slide in slides_needing_charts:
    chart_htmls[slide.id] = render_chart(slide.chart_type, slide.chart_data)

# 3. Chart screenshots — batch in single Playwright instance
chart_screenshots = batch_screenshot(chart_htmls)  # Playwright

# 4. Non-chart slide HTMLs — generate while charts render
slide_htmls = generate_slide_htmls(mapped_slides)

# Wave 3: Collect background results
for tid in image_tasks:
    result = background_output(task_id=tid)
    # Insert into corresponding slide
```

## Playwright Batch Screenshot Optimization

When multiple charts need screenshots, use a **single browser instance** with concurrent pages:

```javascript
// GOOD: Single browser, multiple pages (parallel)
const browser = await chromium.launch();
const screenshots = await Promise.all(
  chartHtmls.map(async (html, i) => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.setContent(html, { waitUntil: 'networkidle' });
    const buf = await page.screenshot({ type: 'png' });
    await page.close();
    return { id: i, buffer: buf };
  })
);
await browser.close();

// BAD: Sequential — one page at a time
for (const html of chartHtmls) {
  const page = await browser.newPage();
  // ... screenshot one by one (N × slower)
}
```

## Parallelization Rules

| Rule | Description |
|------|-------------|
| **Start longest tasks first** | AI image generation takes 5–15s — always fire first |
| **Batch Playwright ops** | One `chromium.launch()`, multiple `newPage()` calls |
| **Never block on images** | Generate all slide HTMLs while images render in background |
| **Collect results lazily** | Only call `background_output()` when results are actually needed (Wave 3) |
| **Fail independently** | If one chart screenshot fails, others continue. Retry failed ones only |
| **Resource limits** | Max 8 concurrent Playwright pages (memory constraint) |
| **Cursor fallback** | In non-OpenCode environments, execute sequentially — no `task()` available |

## Expected Performance Gains

| Document Size | Sequential | Parallel (OpenCode) | Speedup |
|--------------|-----------|-------------------|---------|
| Small (<50 lines, 0 images) | ~15s | ~10s | 1.5× |
| Medium (50–300 lines, 2–3 images) | ~45s | ~20s | 2.2× |
| Large (300+ lines, 5+ images) | ~120s | ~35s | 3.4× |

> **Note**: Speedup is primarily from overlapping AI image generation with slide HTML generation. Chart rendering is already fast (<100ms) and contributes minimal savings.
