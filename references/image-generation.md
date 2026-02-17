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

## 4.5 Generation Paths

```
Priority 1 — NanoBanana Pro (Gemini CLI Extension):
  CLI:  /generate "prompt" --count=1 --styles="photorealistic" --preview
  Output: ./nanobanana-output/*.png

Priority 2 — Gemini API Direct (fallback):
  Model:    gemini-2.5-flash-image
  Endpoint: POST /v1beta/models/gemini-2.5-flash-image:generateContent
  Response: base64 PNG inline data → decode → save to file
```

## 4.6 Environment-Specific Execution

| Environment | Execution Method |
|-------------|-----------------|
| OpenCode | `task(run_in_background=true)` → Gemini Pro background task — fire ALL image tasks in parallel |
| Cursor | Direct execution in main thread (full Gemini Pro model) — sequential |

## 4.7 Image Quality Requirements

| Item | Standard |
|------|----------|
| Resolution | 1920 × 1080 px |
| Format | PNG (JPEG acceptable) |
| File size | Under 5MB |
| Style | Professional, clean, conceptual |
| Colors | Visual harmony with slide palette (#FFFFFF background, grayscale tones) |
| Prohibited | No text, logos, watermarks, busy backgrounds |
| Save location | `{original_filename}_pptx/assets/ai-img-{nn}-{label}.png` |

## 4.8 Failure Handling

If image generation fails after exhausting all paths (NanoBanana Pro + Gemini API):
1. **Do NOT leave the slide without a visual** — use a minimal geometric placeholder
2. Log a warning: `"[WARNING] Image generation failed for slide {N} — using geometric placeholder"`
3. Generate a simple SVG-based geometric shape (circle, hexagon, or abstract lines) in the slide's accent color as a minimal visual anchor
4. **Never leave a content slide as pure text**
