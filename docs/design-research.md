# Design Research — Implementable Patterns for Human-Quality Presentations

> Competitive + academic research synthesis. Only patterns directly applicable
> to MaraudersPPT's HTML→Playwright→PDF pipeline are included.
> Research conducted: Feb 2026

---

## Sources Analyzed

### Competitors
- Beautiful.ai (Smart Slides, 60+ type library)
- Gamma.app (card layout system, accent image positioning)
- Pitch.com (10-grid layout system, editorial design)
- Tome.app (design token/theming approach)
- Genspark AI Slides (template style)

### Academic / Research
- PPTAGENT (EMNLP 2025) — Functional-type classification + editing actions
- AutoPresent (arXiv:2501.00912, Berkeley/CMU) — Iterative refinement
- Self-Refine (NeurIPS 2023, Madaan et al.) — LLM self-correction
- SlideAudit (UIST 2025, UW) — Taxonomy of slide design flaws
- AesthetiQ (arXiv:2503.00591) — Aesthetic-aware preference alignment
- Kikuchi et al. (ACM MM 2021) — Constrained layout generation
- LayoutRectifier (arXiv:2508.11177) — Grid alignment + containment
- Ngo/Teo/Byrne — 14 formal aesthetic measures
- Lok/Feiner/Ngai (CHI 2004) — Visual balance evaluation

### Editorial / Consulting
- McKinsey Pyramid Principle (Barbara Minto)
- BCG slide design methodology (Deckary MBB Guide, 2026)
- Consulting Slide Standards (Deckary, Aug 2025)

---

## 10 Adopted Patterns

### Pattern 1: Functional-Type → Layout Variant Dispatch
**Source**: PPTAGENT (EMNLP 2025), Beautiful.ai
**Adopted**: YES — core of our variant library system

Classify each slide into a functional type (title, narrative, comparison, data,
list, quote, divider, process) BEFORE selecting a layout variant. Different
functional types get different spatial grammars. This is the primary mechanism
for breaking structural uniformity.

PPTAGENT finding: Models that extract "slide-level functional types and content schemas"
from reference decks significantly outperform flat generation on Content, Design, and Coherence.

### Pattern 2: Deck-Level Rhythm via Layout Sequence Constraints
**Source**: Gamma.app card system, Kikuchi et al. (ACM MM 2021)
**Adopted**: YES — integrated into variant selection algorithm

Enforce sequence constraints: no two consecutive slides may use the same
layout variant. Gamma's card system alternates accent image positions
(top/right/left/background/none) to create visual rhythm.

Implementation: Track `layout_history` during generation. Before assigning
a variant, check constraints. If violated, select next-best variant from pool.

### Pattern 3: Action-Title Enforcement
**Source**: McKinsey/BCG/Bain standards (Deckary MBB Guide)
**Adopted**: YES — already in SKILL.md, strengthened in QA rules

Every slide title must be a complete sentence stating a conclusion.
The deck's argument must be readable from titles alone.
Post-processing validation: check for verb, word limit ≤15, no generic patterns.

### Pattern 4: Visual Weight Map Balancing
**Source**: Lok/Feiner/Ngai (CHI 2004), Ngo/Teo/Byrne aesthetic measures
**Adopted**: PARTIAL — simplified as heuristic balance check

Compute visual weight per element, check left-right balance.
Full implementation deferred; simplified version checks that dominant elements
are not all on one side and white space ≥ 20% of slide area.

### Pattern 5: Textual-to-Visual Self-Verification Loop
**Source**: arXiv:2502.15412 (Shanghai Jiao Tong), AutoPresent, Self-Refine
**Adopted**: YES — integrated as Draft→Critique→Patch loop

After generating a slide, render to PNG, then run structured critique.
AutoPresent found +3.2 points improvement from iterative refinement.
Key insight: provide RENDERED output (not code) as feedback input.

Implementation: Generate → Render PNG → Critique (lint + visual QA) →
Patch (targeted edits, NOT regeneration) → Re-render. Max 2 iterations.

### Pattern 6: SlideAudit Taxonomy for QA
**Source**: SlideAudit (UIST 2025, UW)
**Adopted**: YES — encoded as design lint rules

Taxonomy of slide design flaws from 2,400 annotated slides:
- Typography: size inconsistency, >2 font families, long lines, tight leading
- Layout: misalignment, unequal margins, overlap, margin bleeding
- Color: low contrast, >3 accent colors, double-saturation
- Content: sentence bullets, >5 bullets, title-body duplication

### Pattern 7: Paratextual System (Running Headers, Folios, Captions)
**Source**: BCG/McKinsey anatomy, Pitch.com grid system
**Adopted**: YES — primary editorial differentiator

Professional decks use persistent elements across slides:
1. Running header: Section name, top-left, 8-9pt, muted color
2. Folio: Slide number, bottom-right, `{current}/{total}`
3. Source citations: Bottom, 7-8pt, left-aligned
4. Exhibit labels: "Exhibit 1:", "Figure 3:" for charts/tables
5. Thin divider line: 1px separator between title zone and body

These elements occupy reserved zones (24-32px top and bottom).
Absence of paratextual layer is one of the clearest signals of AI generation.

### Pattern 8: Asymmetric Grid Variants
**Source**: LayoutRectifier (arXiv:2508.11177), Pitch.com 10-grid system
**Adopted**: YES — part of layout variant library

Four grid variants per slide type:
- Golden ratio: 38% / 62% (narrative slides)
- Rule of thirds: 33% / 67% (image + text)
- Symmetric: 50% / 50% (comparison)
- Dominant left: 65% / 35% (data + annotation)

Key rule: text zone minimum width 280px for readable line length.

### Pattern 9: Typographic Optical Scale
**Source**: Alibaba Typography research (Feb 2026), BCG "smart simplicity"
**Adopted**: YES — integrated into design token typography scale

Optical size variants: different tracking, leading, and weight at different sizes:
- Display (48pt): tracking -20, leading 1.1
- Headline (32pt): tracking -10, leading 1.2
- Body (16pt): tracking +10, leading 1.5
- Caption (11pt): tracking +20, leading 1.4

Key optical rules:
- Tracking increases as size decreases
- Leading decreases as size increases
- Never same weight for two different hierarchy levels

### Pattern 10: MECE Validation + Pyramid Ordering
**Source**: McKinsey Pyramid Principle, PPTAGENT coherence dimension
**Adopted**: PARTIAL — title-chain validation at deck level

Validate that all slide titles form a coherent argument chain.
MECE checking on bullet lists: no semantic overlap, no coverage gaps.
Full semantic analysis deferred; structural validation implemented.

---

## Key Synthesis

Research converges on three root causes of the AI aesthetic:

1. **Structural uniformity** — every slide uses same layout → Fix: Patterns #1, #2, #8
2. **Content-agnostic rendering** — layout doesn't respond to meaning → Fix: Patterns #1, #3, #10
3. **No paratextual scaffolding** — no headers/folios/citations → Fix: Pattern #7

The gap between AI and human slides is largest in **layout coherence** and
**deck-level structural coherence**, not individual slide content quality.
Highest-leverage interventions are at the DECK level (rhythm, sequencing,
paratextual layer), not the SLIDE level (element polish).

---

## Not Adopted (With Reasoning)

| Pattern | Reason |
|---------|--------|
| Full GAN-based layout generation | Too complex for Skill-based system; LLM instruction-following is sufficient |
| 3D chart rendering | Violates anti-vibe-coding rules |
| Animation/transition design | PDF output only — no motion |
| Multi-font pairing systems | Single font family (Pretendard) is correct for Korean/CJK support |
| Real-time layout optimization | Pipeline is batch, not interactive |
