# Slide Image Generation (Phase 4)
> Every content slide must include a visual element.
> Phase 4 uses a strict 3-priority image system and manifest-based cache reuse.

## 4.1 Visual Coverage Audit
After Phase 3 (Visual Blueprint), audit all slides for visual completeness.

| Slide Status | Has Visual? | Action Required | Priority |
|-------------|:-----------:|-----------------|----------|
| Has original MD image (`![alt](path)`) | ✅ | Copy to `assets/`, reference absolute path, never replace | Priority 1 |
| Has chart/infographic intent | ⚠️ | Render with `templates/charts/` and screenshot | Priority 2 |
| Has diagram/composition intent | ⚠️ | Render as HTML and screenshot | Priority 2 |
| Has code block | ✅ | None (code itself is visual) | N/A |
| Has table | ✅ | None (table itself is visual) | N/A |
| `section-divider` | ✅ | None | N/A |
| `title` without visual | ⚠️ | Add subtle conceptual visual | Priority 2 or 3 |
| `text-body` without visual | ❌ | Must add visual support | Priority 2 or 3 |
| `bullet-list` without visual | ❌ | Must add visual support | Priority 2 or 3 |
| `ai-hint` without visual | ❌ | Must add visual support | Priority 2 or 3 |
| `quote` without visual | ❌ | Must add visual support | Priority 2 or 3 |
| `checklist` without visual | ❌ | Must add visual support | Priority 2 or 3 |
| `closing` without visual | ⚠️ | Add subtle conceptual visual | Priority 2 or 3 |

Hard rule:
```
text_only_slide_ratio == 0%  (content slides only)
```

Metric scope:
- `content_slides`: all slides except `title`, `section-divider`, `appendix-divider`, `closing`
- `text_only_content_slides`: content slides with no image/chart/table/code/infographic visual

### Empty Slide Detection (Critical Guard)
```
FOR each slide:
  IF slide.body_content is EMPTY AND slide.visual is NONE:
    -> CRITICAL: blank rendering risk
    -> RECOVERY order:
       1) Re-extract from Phase 1 Section Card (`source_lines`, `must_keep`)
       2) If source is paragraph-only, convert to concise bullets (Phase 2)
       3) If source is heading-only, merge with adjacent compatible slide
       4) If merge impossible, use headline + minimal conceptual visual
    -> NEVER allow title-only blank body
```

## 4.2 Image Prompt Derivation (from Insight Extraction)
Prompt sources are Phase 1 Section Card fields, not keyword extraction.

Primary fields:
- `insight` (first priority)
- `claim` (second priority)
- `headline` (framing)
- `evidence`, `kpi_metrics`, `stakes`, `role` (modifiers)

Do not use `primary_keyword` in v2.0.

### Prompt Derivation Formula
```
visual_intent = interpret(insight, claim, role)
domain = infer_domain(source_section, evidence, must_keep)
tone = infer_tone(stakes, confidence, role)

prompt =
  "{visual_intent} in {domain} context, {tone}, " +
  "professional corporate presentation quality, clean composition, high resolution, " +
  "no text, no logos, no watermarks"
```

### Prompt Construction Rules
Every prompt must include:
1. Core concept from `insight` or `claim`
2. Domain modifier (business/infra/healthcare/finance/etc.)
3. Style modifier (`professional`, `corporate presentation quality`)
4. Quality modifier (`high resolution`, `clear focal subject`)
5. Prohibition clause (`no text, no logos, no watermarks`)

### Insight -> Prompt Examples
```
insight: "결제 한 건에 3초면 하루 10만건 기준 83시간 낭비"
claim: "결제 지연은 운영 인건비와 고객 이탈을 동시에 유발한다"

prompt:
"professional payment operations environment with dramatic clock motif showing cumulative time loss,
 enterprise systems context, urgent but controlled tone, clean composition, high resolution,
 no text, no logos, no watermarks"
```

## 4.3 Image Manifest (`.image-manifest.json`)
All reusable image outputs are tracked in a manifest.

Location:
```
{output_dir}/.image-manifest.json
```

Schema:
```json
{
  "version": "2.0",
  "generated_at": "ISO timestamp",
  "entries": [
    {
      "slide_id": 3,
      "type": "ai-generated",
      "file_path": "assets/ai-img-03-architecture.png",
      "content_hash": "sha256(prompt+params)",
      "data_hash": null,
      "source_insight": "결제 한 건에 3초면 하루 10만건 기준 83시간 낭비",
      "created_at": "ISO timestamp",
      "reusable": true
    },
    {
      "slide_id": 5,
      "type": "chart",
      "file_path": "assets/chart-05-throughput.png",
      "content_hash": null,
      "data_hash": "sha256(chart_data)",
      "source_insight": "피크 처리량 병목이 SLA를 지연시킴",
      "created_at": "ISO timestamp",
      "reusable": true
    },
    {
      "slide_id": 2,
      "type": "original-md",
      "file_path": "assets/md-img-02-architecture.png",
      "content_hash": null,
      "data_hash": null,
      "source_insight": "원본 MD 이미지 사용",
      "created_at": "ISO timestamp",
      "reusable": true
    }
  ]
}
```

### Hash Policy
- `type=ai-generated`: `content_hash = sha256(normalized_prompt + render_params + generator_id)`
- `type=chart`: `data_hash = sha256(normalized_data + chart_type + template_version + style)`
- `type=original-md`: hash fields may remain `null` (deterministic source path)

### Cache Logic (Check -> Hit -> Miss -> Refresh)
```
FOR each slide requiring visual:
  determine type by priority
  compute lookup hash (if applicable)
  lookup manifest by (slide_id, type)

  IF reusable=true AND hash matches AND file exists:
    -> CACHE HIT: reuse file_path
  ELSE:
    -> CACHE MISS: generate/copy and write entry

  IF explicit refresh requested:
    -> bypass hit for selected scope
    -> regenerate and overwrite hash/timestamp
```

Explicit refresh examples: `--refresh=all`, `--refresh=slide:7`, `--refresh=type:ai-generated`, or user request "regenerate all AI images".

Without explicit refresh request, cache hits must be reused.

### Manifest Integrity Rules
- `version` must be `2.0`
- `generated_at` updates every run
- `file_path` is output-relative (`assets/...`)
- stale/missing file paths trigger regeneration
- no duplicate `(slide_id, type)` entries

## 4.4 Layout Adaptation When Image Is Added
When a text-focused layout receives a visual, adapt while preserving claim hierarchy.

| Original Layout | New Layout | Image Placement |
|----------------|-----------|-----------------|
| `text-body` | `image-text` | Left 50% image, right 50% text |
| `bullet-list` | `image-text` | Left 50% image, right 50% bullets |
| `ai-hint` | `ai-hint` (keep) | Top image band (30% height) |
| `quote` | `quote` (keep) | Background image at 15% opacity |
| `checklist` | `image-text` | Left 40% image, right 60% checklist |
| `title` | `title` (keep) | Background image at 10% opacity |
| `closing` | `closing` (keep) | Background image at 10% opacity |

Critical rule:
```
IF switched to image-text:
  -> re-run distillation for reduced text width
  -> keep claim + strongest evidence before secondary details
```

## 4.5 Image Save & Reference Pipeline (Critical)
This pipeline connects image files to HTML rendering and PDF embedding.

### Save Location
```
{output_dir}/assets/
```

Filename examples:
```
assets/md-img-02-architecture.png
assets/chart-05-throughput.png
assets/ai-img-07-reliability.png
```

Create directory before copy/generation:
```bash
mkdir -p "{output_dir}/assets"
```

### HTML Reference Rules
Use absolute file paths in slide HTML:

```html
<!-- CORRECT: absolute path -->
<img src="/absolute/path/to/docs/prd_slides/assets/ai-img-07-reliability.png"
     style="width: 460pt; height: 340pt; object-fit: cover;">

<!-- ALSO CORRECT: file:// URI -->
<img src="file:///absolute/path/to/docs/prd_slides/assets/chart-05-throughput.png"
     style="width: 460pt; height: 340pt; object-fit: cover;">
```

Internal flow:
1. Playwright renders HTML and computes image geometry
2. `el.src` resolves absolute local path
3. Playwright renders the HTML slide with embedded `<img>` tags directly to PDF

PDF rendering also resolves local `<img src>` correctly when rendering local HTML files.

### Image Sizing for Layouts
| Layout | Image Dimensions (pt) | CSS Style |
|--------|----------------------|-----------|
| `image-text` (left 50%) | 460 x 340 | `width: 460pt; height: 340pt; object-fit: cover` |
| `title` (background 10%) | 720 x 405 | `width: 100%; height: 100%; opacity: 0.10` |
| `closing` (background 10%) | 720 x 405 | `width: 100%; height: 100%; opacity: 0.10` |
| `ai-hint` (top 30%) | 720 x 120 | `width: 100%; height: 120pt; object-fit: cover` |
| `quote` (background 15%) | 720 x 405 | `width: 100%; height: 100%; opacity: 0.15` |

## 4.6 Generation Methods (3-Priority Image System)
Priority is strict. Lower priority cannot replace higher availability.

### Priority 1: Original MD Images (Mandatory First)
Source pattern:
```
![alt](relative/or/absolute/path)
```

Rules:
1. Always consume original MD image first
2. Never replace with chart/AI image when source image exists
3. Copy to `assets/md-img-{NN}-{slug}.png`
4. Register manifest entry with `type=original-md`
5. Bind copied file with absolute path in slide HTML

### Priority 2: HTML Code Generation (Charts, Diagrams, Compositions)
Use when Priority 1 is unavailable and intent is structurally renderable.

Routes:
- `templates/charts/` for data-driven visuals
- custom HTML for diagrams/compositions
- Playwright screenshot to PNG for stable embedding

Chart example:
```python
from templates.charts import render_chart

html = render_chart("bar_chart", [
    {"label": "Before", "value": 42, "display": "42m"},
    {"label": "After", "value": 8, "display": "8m", "max": True}
])
```

HTML concept visual code (retained fallback):
```javascript
const { chromium } = require('playwright');
const path = require('path');

async function generateConceptImage(insightText, label, outputDir, slideIndex) {
  const html = `<html><body style="margin:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);font-family:sans-serif;overflow:hidden;">
    <div style="max-width:980px;color:#fff;font-size:48px;font-weight:700;line-height:1.3;text-align:center;opacity:.9;">${insightText}</div>
  </body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent(html, { waitUntil: 'networkidle' });
  const out = path.join(outputDir, `ai-img-${String(slideIndex).padStart(2, '0')}-${label}.png`);
  await page.screenshot({ path: out, type: 'png' });
  await browser.close();
  return out;
}
```

Manifest rule for Priority 2:
- `type=chart`
- set `data_hash`
- reuse on hash match

### Priority 3: LLM Image Generation (Insight-Based)
Use when Priority 1 is unavailable and Priority 2 is not sufficient for narrative needs.

Prompt source:
- required: `insight`, `claim`
- optional: `role`, `stakes`, `headline`, `evidence`

Execution:
1. Build prompt from Section 4.2
2. Compute `content_hash`
3. Check manifest hit/miss
4. Generate on miss and save to `assets/ai-img-{NN}-{label}.png`
5. Register as `type=ai-generated`

If direct LLM generation is unavailable, fallback to HTML concept screenshot.

## 4.7 Environment-Specific Execution
| Environment | Priority 1 | Priority 2 | Priority 3 |
|-------------|-----------|-----------|-----------|
| **Cursor 2.4+ / Antigravity** | Original MD image copy | HTML code generation + Playwright screenshot | Native image generation from insight prompt |
| **OpenCode** | Original MD image copy | HTML code generation + Playwright screenshot | Background `task(run_in_background=true)` generation |
| **Other / No native image gen** | Original MD image copy | HTML code generation + Playwright screenshot (**primary generated route**) | HTML concept visual or SVG placeholder fallback |

Detection order: 1) MD image exists -> Priority 1, 2) chart/diagram/composition fit -> Priority 2, 3) else Priority 3, 4) if Priority 3 fails -> HTML concept fallback.

## 4.8 Image Quality Requirements
| Item | Standard |
|------|----------|
| Resolution | 1920 x 1080 px |
| Format | PNG (JPEG acceptable) |
| File size | Under 5MB |
| Style | Professional, clean, conceptual |
| Colors | Harmonized with slide palette |
| Prohibited | No text, logos, watermarks, busy backgrounds |
| Save location | `{output_dir}/assets/ai-img-{NN}-{label}.png` |

Additional checks: clear focal subject, no low-contrast noise behind text zones, no decorative clutter.

## 4.9 Failure Handling
```
FOR each slide requiring visual support:
  TRY Priority 1 (original MD image)
    -> if exists: copy, manifest update, bind html, continue

  CHECK manifest cache
    -> if hit and file valid: reuse, continue

  TRY Priority 2 (HTML chart/diagram/composition screenshot)
    -> if success: manifest(data_hash), continue
    -> if fail: warn, go Priority 3

  TRY Priority 3 (LLM image from insight + claim)
    -> if success: manifest(content_hash), continue
    -> if fail: warn, run HTML concept fallback

  TRY HTML concept fallback
    -> if success: manifest update, continue
    -> if fail: try SVG placeholder

  TRY SVG placeholder
    -> if success: continue with warning
    -> if fail: mark visual-missing and FAIL pipeline

  AFTER each slide:
    -> verify file exists
    -> verify file size > 0
    -> verify absolute html src

AFTER all slides:
  -> compute text_only_slide_ratio
  -> IF > 0%: HARD FAIL (do not write PDF)
```

Diagnostic log format:
```
[IMG-OK]    Slide 2: md-img-02-architecture.png (Priority 1: original-md)
[IMG-OK]    Slide 5: chart-05-throughput.png (Priority 2: chart, cache hit)
[IMG-OK]    Slide 7: ai-img-07-reliability.png (Priority 3: ai-generated)
[IMG-WARN]  Slide 9: ai-img-09-risk.png (fallback: HTML concept visual)
[IMG-FAIL]  Slide 11: generation failed -> visual-missing (PIPELINE FAIL)
```

Failure policy:
- any `visual-missing` slide blocks output
- do not write `.pdf` if hard gates fail
- report failing slide IDs and last attempted priority path
