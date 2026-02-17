# Parallel Execution Optimization (6-Wave Architecture)

> **For LLMs that support parallel sub-agent execution** (e.g., OpenCode with `task(run_in_background=true)`),
> the workflow should be parallelized across independent tasks to minimize total conversion time.

## Wave Architecture

The conversion pipeline is organized into **6 waves**. Tasks within each wave execute in parallel; waves execute sequentially.

```
Wave 0 — Gate (instant)
└── Activation Guard: Verify MaraudersMD2PPT keyword → PASS or HARD FAIL
└── Input Contract collection (defaults if not specified)

Wave 1 — Sequential (LLM reasoning, ~5-10s)
├── Phase 0: Environment Detection
├── Phase 1.1: Input Reception
├── Phase 1.2: MD Parsing
├── Phase 1.3: Section Card Generation
└── Phase 1.4: Visual Content Detection

Wave 2 — Sequential (LLM reasoning, ~5-10s)
├── Phase 2.1: Story Arc Design
├── Phase 2.2: Slide Role Assignment (7-Role Taxonomy)
├── Phase 2.3: Slide Plan Generation
├── Phase 2.4: Content Distillation
├── Phase 2.5: Executive Summary
├── Phase 2.6: Slide Flow Optimization
└── Phase 2.7: Dual Output Routing

Wave 3 — Sequential (LLM reasoning, ~3-5s)
└── Phase 3: Visual Blueprint Generation (per-slide + deck rhythm)

Wave 4 — PARALLEL (main bottleneck, optimize here)
├── [Background] Priority 3 AI Image Generation (insight-based prompts) — LONGEST, fire first
├── [Background] Chart HTML Generation (templates/charts/ → render_chart())
├── [Background] Chart Screenshot Capture (Playwright batch)
└── [Foreground] Slide HTML Generation (composition templates)

Wave 5 — Sequential (assembly + verification)
├── Collect AI image results (background_output())
├── Collect chart screenshots
├── Image Manifest update (.image-manifest.json)
├── Assemble all slide HTMLs with final assets
├── Layout adaptation for slides receiving images
├── PDF Rendering (Playwright)
├── PDF Generation (Playwright page.pdf())
├── Appendix PDF Generation
├── Layout Integrity Verification (Phase 5.1)
├── Hard Gates check (Phase 5.2)
├── Visual QA (Phase 5.5)
├── Coverage Report generation
└── Output file writing (versioned) + Diagnostic Report
```

## Wave Execution Model

**Waves 1–3 (LLM Reasoning)**: Sequential, non-parallelizable. LLM must reason through semantic analysis, narrative architecture, and visual blueprint generation. These phases cannot be parallelized because each depends on the previous phase's output.

**Wave 4 (I/O Bottleneck)**: Fully parallelizable. Image generation, chart rendering, and HTML composition are independent I/O operations. Fire longest tasks first (AI image generation takes 5–15s per image).

**Wave 5 (Assembly)**: Sequential. Collects results from Wave 4, validates hard gates, and writes final outputs.

## Wave 4 Parallelization Detail

Wave 4 is the primary bottleneck. The following tasks are **fully independent** and should run concurrently:

| Task | Agent/Method | Blocking? | Typical Duration |
|------|-------------|-----------|-----------------|
| AI Image Generation | Cursor native image gen / `task(run_in_background=true)` | No (background) | 5–15s per image |
| Chart HTML Rendering | `render_chart(type, data)` — Python templates | No (instant) | <100ms per chart |
| Chart Screenshots | Playwright batch — one browser, multiple pages | No (background) | 1–3s per chart |
| Slide HTML Generation | Sequential HTML file writes | Yes (foreground) | <1s per slide |

**Image Manifest Cache Check**: Before firing AI image generation, check `.image-manifest.json` for cache hits. Skip generation for matching `content_hash` entries (unless user explicitly requests refresh).

**Optimal execution pattern (OpenCode):**

```python
# Wave 4: Fire all independent tasks in parallel

# 1. AI Images — background (longest task, start first)
# Check Image Manifest cache first
image_tasks = []
for slide in slides_needing_images:
    cache_hit = check_image_manifest(slide.image_key)
    if cache_hit:
        # Reuse cached image
        image_tasks.append({"cached": True, "path": cache_hit["path"]})
    else:
        # Generate new image
        tid = task(
            run_in_background=True,
            prompt=f"Generate photorealistic image: {slide.image_prompt}",
        )
        image_tasks.append({"cached": False, "task_id": tid})

# 2. Chart rendering — instant, no background needed
chart_htmls = {}
for slide in slides_needing_charts:
    chart_htmls[slide.id] = render_chart(slide.chart_type, slide.chart_data)

# 3. Chart screenshots — batch in single Playwright instance
chart_screenshots = batch_screenshot(chart_htmls)  # Playwright

# 4. Non-chart slide HTMLs — generate while charts render
slide_htmls = generate_slide_htmls(mapped_slides)

# Wave 5: Collect background results
for item in image_tasks:
    if item["cached"]:
        # Use cached path
        pass
    else:
        result = background_output(task_id=item["task_id"])
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
| Small (<50 lines, 0 images) | ~12s | ~10s | 1.2× |
| Medium (50–300 lines, 2–3 images) | ~40s | ~18s | 2.2× |
| Large (300+ lines, 5+ images) | ~110s | ~32s | 3.4× |

> **Note**: Speedup is primarily from overlapping AI image generation with slide HTML generation and chart rendering. Chart rendering is already fast (<100ms) and contributes minimal savings. Image Manifest cache hits further reduce Wave 4 duration.
