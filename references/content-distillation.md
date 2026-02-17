# Slide Content Distillation (Step 2.9)

> **A slide is a visual aid, not a document.**
> If there's too much text on a slide, the slide is WRONG — not "overflowing."
> The problem is never layout capacity. The problem is failing to distill.
>
> **The presenter speaks. The slide shows keywords only.**
> If the audience can read the slide instead of listening, you've failed.

## The Core Rule

```
Every piece of text on a slide must pass this test:
  "Can I remove this and still deliver the message?"
  If YES → REMOVE IT.
  If NO  → SHORTEN IT to the fewest possible words.
```

## Hard Content Limits per Layout Type

These are not "maximums before overflow." These are **good slide design limits.**
Exceeding these means the content is poorly distilled — fix the content, not the layout.

| Layout | Title | Body | Bullets | Words/Bullet |
|--------|:-----:|:----:|:-------:|:------------:|
| `title` | 8 words | 10 words (subtitle) | — | — |
| `executive-summary` | 6 words | 15 words (conclusion) | — | — |
| `section-divider` | 6 words | — | — | — |
| `text-body` | 10 words | 40 words | — | — |
| `bullet-list` | 10 words | — | **3** (max 4) | **7** |
| `image-text` | 8 words | — | 3 | **5** |
| `table` | 8 words | — | — | — |
| `code` | 8 words | — | — | — |
| `ai-hint` | 8 words | 30 words | — | — |
| `quote` | — | 20 words (quote) | — | — |
| `checklist` | 8 words | — | 4 items | 6 |
| `closing` | 8 words | — | 3 steps | 5 |

**Korean/CJK**: Apply **0.7x multiplier** (e.g., 7 words → 한국어 약 5단어/12음절).

## Bullet = Keyword Fragment, Not Sentence

```
❌ WRONG (sentence on a slide):
   • "The processing speed was improved from an average of 3 seconds to 0.8 seconds"

✅ CORRECT (keyword fragment):
   • Processing speed: **3s → 0.8s**

❌ WRONG (too many words):
   • "We adopted MSA architecture because we needed independent deployment capability"

✅ CORRECT:
   • MSA 도입 → 독립 배포 가능
```

**Per-bullet rule**: If a bullet has more than 7 words, it's a sentence. Rewrite as a keyword fragment.

## Slide Total Text Budget

```
ENTIRE slide (title + all body text combined):
  English: MAX 50 words total
  Korean:  MAX 35 words total (≈60 syllables)

If you exceed this budget, the slide has too much content.
Split or move detail to appendix.
```

## Content Preservation Guarantee

> **Distillation = CONDENSE, never DELETE.**

```
HIERARCHY (in order of preference):
  1. Condense → keyword fragments (ALWAYS try this first)
  2. If too short to bullet → use as subtitle or caption text
  3. If section has <15 words total → merge via SHORT-SECTION-MERGE (Step 2.8)
  4. ABSOLUTE PROHIBITION: A section that had content in the source MD
     must produce content on the slide. Zero-content slides = CRITICAL BUG.
```

### Paragraph → Bullet Conversion (MANDATORY for non-bullet source text)

Plain paragraphs (text without `- `, `* `, `1. ` prefixes) are the #1 source of content loss.
They MUST be converted to keyword bullets — NEVER silently dropped.

```
Source: "This project is licensed under the MIT License."
  → • License: **MIT**

Source: "Contributions are welcome. Please read the contributing guide before submitting PRs."
  → • Contributions welcome — see guide

Source: "Built with React, TypeScript, and Tailwind CSS for modern web development."
  → • Stack: **React** + TypeScript + Tailwind

Source: "For questions, contact team@example.com or open an issue on GitHub."
  → • Contact: team@example.com / GitHub Issues
```

**Rule**: Every source paragraph produces **at least 1 bullet**. If the paragraph contains multiple distinct ideas, produce 1 bullet per idea (up to 3 max).

### Short Section Handling

Sections with ≤2 content lines (e.g., "License", "Contributing", "Contact"):

| Source Lines | Action |
|:------------:|--------|
| 0 lines (heading only) | Merge heading into previous slide's footer/badge area |
| 1 line | Merge as badge into previous slide, OR combine with other short sections into `icon-grid` |
| 2 lines | Convert to 1–2 keyword bullets, merge into previous slide if <15 total words |

**NEVER** create a standalone slide for ≤15 words of body content.

## Distillation Algorithm

```
FOR each content_block:
  0. CLASSIFY content type: bullet list | paragraph | table | code | mixed
  1. IF paragraph → Convert to keyword bullets FIRST (see Paragraph → Bullet above)
  2. Extract keywords (Step 2.3)
  3. Rewrite as keyword fragments (noun-phrase, no verbs, no filler)
  4. Count total slide words
  5. IF > 50 words (EN) / 35 words (KR):
     → Split into 2 slides, OR
     → Move supporting detail to appendix
  6. IF < 15 words AND section is short → Merge with adjacent (SHORT-SECTION-MERGE)
  7. VERIFY: slide body is NOT empty after distillation (CRITICAL CHECK)
  8. VERIFY: presenter can read entire slide in ≤3 seconds
```

## Anti-Patterns (ALL PROHIBITED)

| What | Why It's Wrong | Fix |
|------|---------------|-----|
| Full sentences on slides | Audience reads instead of listens | Keyword fragments only |
| 5+ bullets | Cognitive overload | Max 3 (rarely 4) |
| Bullet longer than 1 line | It's a paragraph disguised as a bullet | Condense to ≤7 words |
| Prose paragraphs on slides | This is a document, not a slide | Extract 2-3 keyword bullets |
| Repeating title content in body | Redundancy wastes space | Title = conclusion, body = evidence |
| Filler words ("In order to", "It is important that") | Zero information value | Delete completely |
| **Deleting paragraphs entirely** | **Content loss — empty slides** | **Convert to keyword bullets FIRST** |
| **Empty slide body** | **Critical rendering failure** | **Re-extract from source, merge, or add visual** |
| **1-line section as standalone slide** | **Wasted slide, poor flow** | **Merge via SHORT-SECTION-MERGE** |
