# Slide Image Generation (Step 4)

> **Every slide that lacks a visual element MUST receive a generated image.**
> A slide without graphics is incomplete. No exceptions.

## 4.1 Visual Coverage Audit

After Step 3 (Slide Mapping), scan every slide and classify:

| Slide Status | Has Visual? | Action Required |
|-------------|:-----------:|-----------------|
| Has original MD image (`![alt](path)`) | ✅ | None — use original image |
| Has chart/infographic (auto-detected in Step 2.5) | ✅ | None — use chart rendering |
| Has code block (dark background = visual) | ✅ | None — code itself is visual |
| Has table (native table = visual) | ✅ | None — table itself is visual |
| `section-divider` slide | ✅ | None — inverted background is visual |
| `title` slide | ⚠️ | Generate abstract conceptual image |
| `text-body` slide — **NO visual** | ❌ | **MUST generate image** |
| `bullet-list` slide — **NO visual** | ❌ | **MUST generate image** |
| `ai-hint` slide — **NO visual** | ❌ | **MUST generate image** |
| `quote` slide — **NO visual** | ❌ | **MUST generate image** |
| `checklist` slide — **NO visual** | ❌ | **MUST generate image** |
| `closing` slide | ⚠️ | Generate abstract conceptual image |

**Rule: 0% of content slides may be text-only (excluding code/table/chart slides).**

### Empty Slide Detection (CRITICAL GUARD)

During the visual coverage audit, also check for **empty content**:

```
FOR each slide:
  IF slide.body_content is EMPTY AND slide.visual is NONE:
    → CRITICAL: This slide will render as a blank page
    → RECOVERY (in order):
      1. Re-extract content from source MD section (distillation may have dropped it)
      2. If source section was a plain paragraph → convert to keyword bullet NOW
      3. If section is genuinely empty (heading-only) → merge with adjacent slide
      4. If no merge target → generate AI image from section title + use title as body text
    → NEVER allow a slide to render with only a title and blank body
```

This guard catches content lost during Step 2.9 distillation — especially **plain paragraphs** that were incorrectly treated as deletable content.

## 4.2 Image Prompt Derivation (from Keyword Extraction)

The image prompt is derived directly from Step 2.3's `primary_keyword`:

```
Image Concept = Slide's primary_keyword → One-line visual metaphor

Examples:
  primary_keyword: "processing speed 3x improvement"
  → Image prompt: "professional high-speed data stream flowing through modern server infrastructure, clean white background, high resolution, no text, no logos, no watermarks"

  primary_keyword: "MSA architecture adoption"
  → Image prompt: "interconnected microservices nodes forming a distributed network architecture, professional clean diagram style, high resolution, no text, no logos, no watermarks"

  primary_keyword: "failure rate 73% reduction"
  → Image prompt: "professional quality control dashboard showing dramatic improvement trend, clean minimal design, high resolution, no text, no logos, no watermarks"
```

## 4.3 Prompt Construction Rules

Every image prompt MUST include:
1. **Core concept** derived from `primary_keyword` (1 sentence)
2. **Style keywords**: `"professional"`, `"clean background"`, `"high resolution"`
3. **Prohibition clause**: `"no text, no logos, no watermarks"`
4. **Contextual modifier**: Match the domain of the slide content (tech, business, medical, etc.)
5. **Tone**: Corporate presentation quality — NOT stock photo, NOT artistic illustration

## 4.4 Layout Adaptation When Image Is Added

When a generated image is added to a previously text-only slide:

| Original Layout | New Layout | Image Position |
|----------------|-----------|----------------|
| `text-body` | `image-text` | Left 50% image \| Right 50% text |
| `bullet-list` | `image-text` | Left 50% image \| Right 50% bullets |
| `ai-hint` | `ai-hint` (keep) | Image inserted above hint block (30% height) |
| `quote` | `quote` (keep) | Background image at 15% opacity behind quote |
| `checklist` | `image-text` | Left 40% image \| Right 60% checklist |
| `title` | `title` (keep) | Subtle background image at 10% opacity |
| `closing` | `closing` (keep) | Subtle background image at 10% opacity |

**CRITICAL**: When layout switches to `image-text`, the text content MUST be condensed to fit the reduced text area (50–60% of slide width). Apply content distillation limits for `image-text` layout.

## 4.5 Image Save & Reference Pipeline (CRITICAL)

> **This is the pipeline that connects generated images to the final PPTX/PDF.**
> If this is broken, images won't appear even if generation succeeds.

### Save Location

All generated images MUST be saved to:
```
{output_dir}/assets/ai-img-{NN}-{label}.png

Example:
  docs/prd_pptx/assets/ai-img-01-architecture.png
  docs/prd_pptx/assets/ai-img-02-performance.png
```

Create the `assets/` directory before generating any images:
```bash
mkdir -p "{output_dir}/assets"
```

### HTML Reference (how html2pptx.js picks up images)

In the HTML slide file, reference images using **absolute file paths**:

```html
<!-- CORRECT — absolute path (html2pptx.js resolves file:// URIs) -->
<img src="/absolute/path/to/docs/prd_pptx/assets/ai-img-01-architecture.png"
     style="width: 460pt; height: 340pt; object-fit: cover;">

<!-- ALSO CORRECT — file:// URI (html2pptx.js strips file:// prefix) -->
<img src="file:///absolute/path/to/docs/prd_pptx/assets/ai-img-01-architecture.png"
     style="width: 460pt; height: 340pt; object-fit: cover;">
```

**How it works internally**:
1. Playwright renders the HTML slide → `getBoundingClientRect()` gets image position/size
2. `el.src` captures the full path (Playwright resolves relative paths to `file://` URIs)
3. html2pptx.js strips `file://` prefix → passes to PptxGenJS `addImage({ path: ... })`
4. PptxGenJS reads the PNG from disk → embeds into PPTX

**For PDF generation**: Playwright's `page.pdf()` also resolves local `<img src>` paths correctly when rendering HTML files from disk.

### Image Sizing for Slide Layouts

| Layout | Image Dimensions (pt) | CSS Style |
|--------|----------------------|-----------|
| `image-text` (left 50%) | 460 × 340 | `width: 460pt; height: 340pt; object-fit: cover` |
| `title` (background 10%) | 720 × 405 | `width: 100%; height: 100%; opacity: 0.10` |
| `closing` (background 10%) | 720 × 405 | `width: 100%; height: 100%; opacity: 0.10` |
| `ai-hint` (top 30%) | 720 × 120 | `width: 100%; height: 120pt; object-fit: cover` |
| `quote` (background 15%) | 720 × 405 | `width: 100%; height: 100%; opacity: 0.15` |

## 4.6 Generation Methods (3 paths, in priority order)

### Priority 1A: Native Image Generation (Cursor / Antigravity)

> **Cursor 2.4+** and **Google Antigravity** have built-in image generation agent tools (powered by Nano Banana Pro / Gemini 3 Pro Image). The agent generates images when you describe them — no CLI commands, no model switching, no installation required.

**How it works:**
1. The skill describes the desired image in natural language
2. Cursor's agent invokes its built-in image generation tool
3. The generated image is saved to the project's `assets/` folder by default
4. The image is shown inline in chat as a preview

**Generation per slide:**
```
For EACH slide needing an image:
  Generate a photorealistic image for a presentation slide.
  Concept: {image_prompt_from_4.2}
  Save to: {output_dir}/assets/ai-img-{NN}-{label}.png
  Requirements: 1920x1080px, PNG, professional corporate style,
  clean background, NO text/logos/watermarks.
```

**Batch generation** (describe all needed images, let agent generate sequentially):
```
FOR EACH slide needing an image:
  → Describe image using prompt from Section 4.2
  → Agent generates via native image gen tool → saves to {output_dir}/assets/
  → Verify: ls -la {output_path} (file exists, size > 0)
```

**Key advantages over CLI approach:**
- Zero setup — works out of the box in Cursor 2.4+ and Google Antigravity
- No model switching — image gen works regardless of selected chat model
- Saves directly to project `assets/` folder
- Inline preview in chat for immediate visual verification

### Priority 1B: Background Task Delegation (OpenCode environments)

**OpenCode** — use `task()` to delegate image generation to a background agent:

```
For EACH slide needing an image:
  task(
    run_in_background=true,
    category="quick",
    prompt="Generate a photorealistic image for a presentation slide.
            Concept: {image_prompt_from_4.2}
            Save the image to: {output_dir}/assets/ai-img-{NN}-{label}.png
            Requirements: 1920x1080px, PNG, professional corporate style,
            clean background, NO text/logos/watermarks.
            Use image generation or create a high-quality HTML visual
            and screenshot it with Playwright."
  )
```

**Note**: Background tasks run in parallel — fire all image generation tasks at once, continue with other pipeline work, then collect results before Step 5.

### Priority 2: HTML Concept Visual + Playwright Screenshot (ALWAYS WORKS)

> **This is the reliable fallback that works in ANY environment with zero external dependencies.**
> Generate a styled HTML visual and screenshot it with Playwright.

Create a Node.js script that generates a concept visual:

```javascript
// generate-concept-image.js
const { chromium } = require('playwright');
const path = require('path');

async function generateConceptImage(keyword, label, outputDir, slideIndex) {
  // Color palette derived from slide design
  const colors = [
    { bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', text: '#fff' },
    { bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', text: '#fff' },
    { bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', text: '#fff' },
    { bg: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', text: '#fff' },
    { bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', text: '#333' },
    { bg: 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)', text: '#333' },
  ];
  const palette = colors[slideIndex % colors.length];

  const html = `<!DOCTYPE html>
<html><head><style>
  body { margin:0; width:1920px; height:1080px; display:flex;
         align-items:center; justify-content:center;
         background:${palette.bg}; font-family:sans-serif; overflow:hidden; }
  .container { text-align:center; padding:80px; }
  .icon { font-size:200px; opacity:0.15; margin-bottom:40px; }
  .keyword { font-size:48px; font-weight:700; color:${palette.text};
             opacity:0.9; letter-spacing:2px; text-transform:uppercase;
             max-width:900px; line-height:1.3; }
  .shapes { position:absolute; top:0; left:0; width:100%; height:100%;
            pointer-events:none; overflow:hidden; }
  .circle { position:absolute; border-radius:50%; opacity:0.08;
            background:${palette.text}; }
  .c1 { width:400px; height:400px; top:-100px; right:-100px; }
  .c2 { width:300px; height:300px; bottom:-80px; left:-80px; }
  .c3 { width:200px; height:200px; top:40%; left:10%; }
  .line { position:absolute; background:${palette.text}; opacity:0.06; }
  .l1 { width:2px; height:600px; top:100px; left:30%; transform:rotate(15deg); }
  .l2 { width:2px; height:500px; top:200px; right:25%; transform:rotate(-10deg); }
</style></head><body>
  <div class="shapes">
    <div class="circle c1"></div><div class="circle c2"></div>
    <div class="circle c3"></div><div class="line l1"></div>
    <div class="line l2"></div>
  </div>
  <div class="container">
    <div class="keyword">${keyword}</div>
  </div>
</body></html>`;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent(html, { waitUntil: 'networkidle' });
  const outputPath = path.join(outputDir, `ai-img-${String(slideIndex).padStart(2,'0')}-${label}.png`);
  await page.screenshot({ path: outputPath, type: 'png' });
  await browser.close();
  return outputPath;
}

module.exports = { generateConceptImage };
```

**Usage from the pipeline** (batch all slides in one browser instance):

```javascript
const { chromium } = require('playwright');

async function batchGenerateConceptImages(slides, outputDir) {
  const browser = await chromium.launch();
  const results = [];
  for (const slide of slides) {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    // ... set HTML content with slide.primary_keyword ...
    const outputPath = `${outputDir}/ai-img-${slide.index}-${slide.label}.png`;
    await page.screenshot({ path: outputPath, type: 'png' });
    await page.close();
    results.push(outputPath);
  }
  await browser.close();
  return results;
}
```

**CRITICAL**: Before using this method, rasterize the gradient background to PNG using Sharp (html2pptx.js does NOT support CSS gradients directly):

```javascript
const sharp = require('sharp');

// Rasterize gradient background for PPTX (CSS gradients not supported by html2pptx)
// The concept image is a screenshot — so gradients are already rasterized in the PNG
// Use the generated PNG directly in <img src="..."> in the slide HTML
```

Since the concept image is a **Playwright screenshot** (raster PNG), CSS gradients ARE captured correctly. The gradient limitation only applies to HTML slides processed by html2pptx.js directly.

### Priority 3: SVG Geometric Placeholder (simplest fallback)

If even Playwright is unavailable, generate a minimal SVG and rasterize with Sharp:

```javascript
const sharp = require('sharp');

async function generatePlaceholder(keyword, outputPath) {
  const svg = `<svg width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#F8F9FA"/>
    <circle cx="960" cy="440" r="200" fill="none" stroke="#D94F4F" stroke-width="3" opacity="0.3"/>
    <circle cx="960" cy="440" r="140" fill="none" stroke="#D94F4F" stroke-width="2" opacity="0.2"/>
    <circle cx="960" cy="440" r="80" fill="none" stroke="#D94F4F" stroke-width="1.5" opacity="0.15"/>
    <text x="960" y="750" text-anchor="middle" font-family="sans-serif"
          font-size="36" fill="#888888" opacity="0.6">${keyword}</text>
  </svg>`;

  await sharp(Buffer.from(svg)).png().toFile(outputPath);
}
```

## 4.7 Environment-Specific Execution

| Environment | Priority 1 | Priority 2 | Priority 3 |
|-------------|-----------|-----------|-----------|
| **Cursor 2.4+ / Antigravity** | Native image gen (built-in agent tool) → saves to `assets/` | HTML concept visual + Playwright screenshot | SVG + Sharp placeholder |
| **OpenCode** | `task(run_in_background=true)` → background agent generates images | HTML concept visual + Playwright screenshot (if task fails) | SVG + Sharp placeholder |
| **Other / No image gen** | Skip | HTML concept visual + Playwright screenshot (**primary method**) | SVG + Sharp placeholder |

**IMPORTANT**: In environments without native image gen or `task()`, Priority 2 (HTML concept visual) becomes the **primary** method. It always works because it only needs Playwright (already a dependency).

**Environment detection order:**
1. Cursor / Antigravity environment → use native image generation (Priority 1A)
2. OpenCode environment (`task()` available) → use background delegation (Priority 1B)
3. Neither available → skip to Priority 2 (HTML concept visual)

## 4.8 Image Quality Requirements

| Item | Standard |
|------|----------|
| Resolution | 1920 × 1080 px |
| Format | PNG (JPEG acceptable) |
| File size | Under 5MB |
| Style | Professional, clean, conceptual |
| Colors | Visual harmony with slide palette |
| Prohibited | No text, logos, watermarks, busy backgrounds |
| Save location | `{output_dir}/assets/ai-img-{NN}-{label}.png` |

## 4.9 Failure Handling

```
FOR each slide needing an image:
  TRY Priority 1A (Cursor native image gen) or Priority 1B (OpenCode background task)
    → Describe image using prompt from Section 4.2
    → IF success: verify file at {output_dir}/assets/, continue
    → IF fail: log warning, try Priority 2

  TRY Priority 2 (HTML concept visual + Playwright)
    → IF success: save PNG, continue
    → IF fail: log warning, try Priority 3

  TRY Priority 3 (SVG + Sharp placeholder)
    → IF success: save PNG, continue
    → IF fail: CRITICAL — log error, but STILL generate slide (title-only as last resort)

  AFTER all attempts:
    → Verify file exists at expected path: ls -la {output_path}
    → Verify file size > 0 bytes
    → IF file missing or empty: regenerate with Priority 3
```

**Log format for diagnostics:**
```
[IMG-OK]  Slide 3: ai-img-03-architecture.png (Priority 1: native image gen, 312KB)
[IMG-OK]  Slide 5: ai-img-05-performance.png (Priority 1: background task, 245KB)
[IMG-OK]  Slide 7: ai-img-07-deployment.png (Priority 2: HTML concept, 89KB)
[IMG-WARN] Slide 8: ai-img-08-security.png (Priority 3: SVG placeholder, 12KB)
[IMG-FAIL] Slide 9: generation failed — title-only slide (CRITICAL)
```
