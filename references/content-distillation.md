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

## Distillation Algorithm

```
FOR each content_block:
  1. Extract keywords (Step 2.3)
  2. Rewrite as keyword fragments (noun-phrase, no verbs, no filler)
  3. Count total slide words
  4. IF > 50 words (EN) / 35 words (KR):
     → Split into 2 slides, OR
     → Move supporting detail to appendix
  5. VERIFY: presenter can read entire slide in ≤3 seconds
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
