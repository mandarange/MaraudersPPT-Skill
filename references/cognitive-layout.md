# Cognitive Layout Principles — Slide Design Rules

> **Purpose**: Actionable layout rules derived from cognitive science, eye-tracking research,
> Gestalt psychology, and consulting presentation standards (McKinsey/BCG).
> These rules are BINDING — the AI must follow them when generating slide layouts.

---

## 1) Eye Scanning Patterns

### 1.1 Three Patterns and When They Apply

Research source: Nielsen Norman Group eye-tracking studies, Tobii eye-tracking data.

| Pattern | Shape | Applies When | Slide Types |
|---------|-------|-------------|-------------|
| **Z-Pattern** | Top-left → Top-right → Bottom-left → Bottom-right | Low text density, mixed content | Default for most slides |
| **F-Pattern** | Top → Left-edge scan → Spot reads right | High text density, bullet-heavy | `bullet-list`, `evidence-bullets`, `text-body` |
| **Center-Focus** | Center dominant → radiate outward | Single dominant element | `hero-metric`, `single-statement`, `donut-chart` |

### 1.2 Actionable Layout Rules from Eye Patterns

#### Z-Pattern Rules (Default)
```
RULE Z-1: Place the most important element (action title) at TOP-LEFT
RULE Z-2: Place supporting visual (chart, image) at TOP-RIGHT or CENTER-RIGHT
RULE Z-3: Place call-to-action or key takeaway at BOTTOM-RIGHT
RULE Z-4: Place secondary text/evidence at BOTTOM-LEFT
RULE Z-5: The diagonal (top-left → bottom-right) is the power axis — 
           place accent/highlight elements along this diagonal
```

#### F-Pattern Rules (Text-heavy slides)
```
RULE F-1: First line (action title) gets FULL attention — make it count
RULE F-2: First 2-3 words of each bullet get the most fixation — 
           front-load keywords, never start with "The", "This", "It"
RULE F-3: Left margin alignment is critical — all bullets must start at same x-coordinate
RULE F-4: Visual weight decreases going down — place strongest evidence in bullet #1
RULE F-5: After bullet #3, attention drops sharply — never exceed 4 bullets
```

#### Center-Focus Rules
```
RULE C-1: Dominant element (number, statement) must be dead-center ±5% of canvas
RULE C-2: Support text goes directly below, never above
RULE C-3: Source/attribution goes bottom margin area
RULE C-4: Nothing competes with the center element — no side panels or distractors
```

---

## 2) Gestalt Principles Applied to Slides

Research source: Wertheimer (1923), Koffka (1935), modern replication by Jakob Nielsen (2024).

### 2.1 Proximity — Group Related Items

> **The brain perceives elements close together as belonging to a single unit.**

```
RULE PROX-1: Related items must have ≤16px gap between them
RULE PROX-2: Unrelated groups must have ≥32px gap (2× the within-group gap)
RULE PROX-3: The ratio of within-group to between-group spacing must be ≥1:2
             (e.g., 8px within, 24px between)
RULE PROX-4: In KPI cards, label→value→delta must form a tight vertical stack
             (8-12px gaps), while card-to-card gap is 24-32px
RULE PROX-5: In bullet lists, sub-bullets indent 20px AND reduce gap to 8px
             to visually nest under parent
```

**Violation example**: Equal spacing between all elements makes everything look like one undifferentiated block. The viewer cannot parse the structure.

### 2.2 Similarity — Visual Consistency Signals Grouping

> **Elements sharing visual attributes (color, size, shape) are perceived as related.**

```
RULE SIM-1: All items in a data series must use the same visual treatment
            (same font size, same weight, same color)
RULE SIM-2: Accent color breaks similarity — use it to signal ONE outlier/highlight
RULE SIM-3: KPI labels must all be the same size (16px), values all the same size (56px)
RULE SIM-4: In process flows, all step boxes must be identical dimensions
            (except the active step, which breaks similarity intentionally)
RULE SIM-5: Bar chart bars must all be the same height — differentiate only by width
RULE SIM-6: Never mix font sizes within a single logical group
```

### 2.3 Enclosure — Boundaries Define Groups

> **Elements enclosed in a boundary are perceived as a distinct group.**

```
RULE ENC-1: Use `border: 1px solid #E0E0E0` to group related content into cards
RULE ENC-2: Use background color contrast (#F5F5F5 vs #FFFFFF) as soft enclosure
RULE ENC-3: Never use rounded corners >2px (per Anti-Vibe-Coding rules)
RULE ENC-4: The enclosure must be subtle — if the border draws more attention
            than the content, it's too heavy
RULE ENC-5: Section divider slides use full-slide enclosure (dark background)
            to mark a major group transition
```

### 2.4 Continuity — Aligned Elements Form a Flow

> **The eye follows lines, curves, and alignments naturally.**

```
RULE CONT-1: Vertical left-alignment of all body text creates an implicit reading line
RULE CONT-2: Timeline dots must sit on a perfectly straight horizontal line
RULE CONT-3: Process flow arrows must form a single horizontal or L-shaped path
RULE CONT-4: In multi-column layouts, column top edges must align exactly
RULE CONT-5: Grid lines in charts must be evenly spaced and perfectly parallel
RULE CONT-6: If elements can be aligned, they MUST be aligned — 
              misalignment by even 2px breaks continuity perception
```

### 2.5 Figure-Ground — Separate Content from Canvas

> **The brain separates foreground (content) from background (canvas).**

```
RULE FG-1: White space is not empty — it's the ground that defines figure boundaries
RULE FG-2: Minimum margin 0.7" (67px) on all sides — content IS the figure
RULE FG-3: Charts float on white — never fill the entire content area edge-to-edge
RULE FG-4: On section-divider slides, inverted colors (dark bg) signal a different layer
RULE FG-5: When using background images, text must have solid/high-opacity backing
            to maintain figure-ground separation
```

### 2.6 Common Fate — Elements Moving/Changing Together Belong Together

> In static slides, "common fate" translates to consistent visual direction.

```
RULE CF-1: In bar charts, all bars grow from the same baseline (left edge)
RULE CF-2: In timelines, all events flow left-to-right (never reverse)
RULE CF-3: In process flows, all arrows point the same direction
RULE CF-4: Funnel stages narrow consistently (never widen between stages)
RULE CF-5: KPI deltas with ▲ all use the same color; ▼ all use the same color
```

---

## 3) Pre-Attentive Attributes

Research source: Healey & Enns (2012), Colin Ware "Information Visualization" (2012), Treisman (1985).

> Pre-attentive attributes are processed in <200ms — before conscious attention.
> Use them to direct the viewer's eye to the ONE thing that matters.

### 3.1 Attribute Hierarchy for Slides

| Attribute | Processing Speed | Best For | Slide Application |
|-----------|:---:|---------|-------------------|
| **Color hue** | ~50ms | Categorical distinction | Accent `#D94F4F` pops against `#1A1A1A` grayscale |
| **Size** | ~80ms | Quantitative comparison | KPI hero number (120px) vs body text (18px) |
| **Orientation** | ~100ms | Direction/trend | ▲/▼ arrows for delta indicators |
| **Length** | ~100ms | Quantitative ranking | Bar chart bar widths |
| **Position** | ~120ms | Spatial clustering | Element placement in Z-pattern |
| **Shape** | ~150ms | Categorical coding | Circle vs square nodes in diagrams |
| **Enclosure** | ~180ms | Grouping | Card borders, section backgrounds |

### 3.2 Actionable Rules

```
RULE PA-1: Use exactly ONE pre-attentive channel per slide to signal importance
           (color OR size, rarely both — never 3+)
RULE PA-2: Accent color (#D94F4F) must appear on ≤1 element per slide
           to remain pre-attentively distinct
RULE PA-3: The hero number in a KPI slide must be ≥3× the body text size
           to trigger size-based pre-attention (56px vs 16px = 3.5×)
RULE PA-4: Bar chart highlight: change fill color to accent on exactly 1 bar
RULE PA-5: Don't encode data using ONLY color — add labels, patterns, or position
           (color-blind safety per Section 13.2)
RULE PA-6: If everything is bold, nothing is bold — 
           max 2 bold elements per slide
```

---

## 4) Working Memory Constraints (Miller's Law)

Research source: Miller (1956) "The Magical Number Seven, Plus or Minus Two", 
Cowan (2001) revised to 4±1 chunks, Sweller Cognitive Load Theory (1988).

### 4.1 Modern Understanding

> Miller's original 7±2 was for items in short-term memory.
> Cowan's revised estimate is **4±1 chunks** for working memory.
> For slide comprehension: **the audience can hold 3-5 independent ideas simultaneously.**

### 4.2 Slide Content Rules (Cognitive Load)

```
RULE WM-1: Maximum 4 bullet points per slide (3 optimal)
           → 4 items = within Cowan's 4±1 limit
RULE WM-2: Maximum 5 data segments in a donut chart
           → 5 categories is the upper bound of comparison capacity
RULE WM-3: Maximum 6 bars in a bar chart
           → Beyond 6, viewers cannot maintain relative comparisons
RULE WM-4: Maximum 8 steps in a process flow
           → 8 exceeds raw capacity but chunking (groups of 2-3) recovers it
RULE WM-5: Each slide communicates exactly 1 message
           → One "so what" per slide, stated in the action title
RULE WM-6: The 60-second rule — if understanding takes >60s, the slide is overloaded
RULE WM-7: Reduce extraneous load: remove chart junk, decorative elements,
           unnecessary gridlines, redundant labels
RULE WM-8: Chunking increases capacity — group 8 items into 3 labeled groups
           to stay within working memory limits
```

### 4.3 Extraneous vs Intrinsic vs Germane Load

| Load Type | Definition | Slide Action |
|-----------|-----------|--------------|
| **Extraneous** | Caused by bad design, not content | ELIMINATE: decorations, chart junk, unclear labels |
| **Intrinsic** | Caused by content complexity | MANAGE: simplify data, chunk information |
| **Germane** | Effort spent building understanding | MAXIMIZE: clear hierarchy, good labels, logical flow |

```
RULE CL-1: Every visual element must carry information — 
           if removing it loses nothing, remove it
RULE CL-2: Redundant encoding (label + color + position all saying the same thing)
           is acceptable because it reduces intrinsic load
RULE CL-3: Consistent layout across slides reduces extraneous load — 
           title position, margin, font size must be identical slide-to-slide
```

---

## 5) Visual Hierarchy Rules

Research source: BCG slide design principles, McKinsey Pyramid Principle, Tufte (2001).

### 5.1 The Four-Level Hierarchy

Every slide must have exactly 4 levels of visual weight:

| Level | Element | Visual Treatment | Attention Share |
|:-----:|---------|-----------------|:---------------:|
| 1 | **Hero element** | Largest size, boldest weight, accent color possible | 40-50% |
| 2 | **Action title** | 24pt Bold, full width, top position | 25-30% |
| 3 | **Supporting evidence** | 18pt Regular, bullets or labels | 15-20% |
| 4 | **Attribution/source** | 12pt Light, bottom margin, gray | 5% |

```
RULE VH-1: Every slide must have a clear Level 1 (hero) element
           — if you can't point to it instantly, the hierarchy is flat
RULE VH-2: The size ratio between adjacent levels must be ≥1.25:1
           (24pt title : 18pt body = 1.33 ✓)
RULE VH-3: Weight contrast supplements size: Level 1 = ExtraBold (800),
           Level 2 = Bold (700), Level 3 = Regular (400), Level 4 = Light (300)
RULE VH-4: Color contrast reinforces hierarchy: Level 1 = #1A1A1A or #D94F4F,
           Level 3 = #555555, Level 4 = #888888
RULE VH-5: Position reinforces hierarchy: Level 1/2 top-left or center,
           Level 4 bottom-right
```

### 5.2 The "Squint Test"

> Close your eyes to slits and look at the slide.
> The elements you can still distinguish are the hierarchy levels.
> If you see an undifferentiated blob, the hierarchy has failed.

```
RULE SQUINT-1: At 25% zoom, the action title and hero element must be legible
RULE SQUINT-2: At 25% zoom, the overall layout structure (columns, chart, text block)
               must be identifiable
RULE SQUINT-3: If two elements appear to be the same size at 25% zoom
               but serve different hierarchy levels, increase the size differential
```

---

## 6) Consulting Slide Standards (McKinsey/BCG Distilled)

Research source: BCG slide writing methodology (Slideworks analysis), McKinsey Pyramid Principle, 
analyst academy BCG slide breakdown, deckary.com MBB guide (2026).

### 6.1 The One-Message Rule

```
RULE MSG-1: Each slide communicates exactly ONE insight
RULE MSG-2: The action title IS the message — a complete sentence with a verb
            and a conclusion ("Revenue grew 23% driven by APAC expansion")
RULE MSG-3: If you need two messages, you need two slides
RULE MSG-4: The body exists only to SUPPORT the title claim with evidence
RULE MSG-5: Read only the titles of all slides — they should tell the complete story
```

### 6.2 Margin and White Space

```
RULE WS-1: Minimum margin: 0.7" (67px) on all four sides — inviolable
RULE WS-2: White space ≥20% of total slide area
RULE WS-3: Content area is 1720×760px (within 1920×1080 slide with margins)
RULE WS-4: Between title and body: 32px (4× on 8px grid)
RULE WS-5: Between bullet items: 16px (2× on 8px grid)
RULE WS-6: Between major content blocks: 24px (3× on 8px grid)
RULE WS-7: Charts/images should have 16px breathing room on all sides
RULE WS-8: Never fill content area edge-to-edge — 
           leave ≥10% padding within the content zone
```

### 6.3 Chart Selection (Consulting Standard)

| Data Type | Chart Type | Why |
|-----------|-----------|-----|
| Comparison across items | Horizontal bar | Easiest to read labels + compare lengths |
| Proportion / share | Donut chart | Center value gives immediate context |
| Trend over time | Sparkline or line chart | Direction visible at a glance |
| Sequential process | Process flow | Step progression is natural left-to-right |
| Before/after | Side-by-side comparison | Parallel structure enables rapid comparison |
| KPI highlights | KPI cards | Numbers as hero elements |
| Timeline | Timeline | Chronological left-to-right mapping |

```
RULE CHART-1: Never use 3D charts — they distort perception of values
RULE CHART-2: Never use pie charts — donut with center value is always better
RULE CHART-3: Horizontal bars > vertical bars for category comparison
              (labels are readable, no rotation needed)
RULE CHART-4: Direct label data points — don't make viewers cross-reference a legend
RULE CHART-5: Maximum 1 chart per slide (complexity rule)
RULE CHART-6: Source/attribution required below every chart
```

### 6.4 Title Architecture (BCG Method)

```
RULE TITLE-1: Action title = complete sentence with verb + conclusion
              ❌ "Market Analysis"
              ✅ "Domestic market grows 12% annually, doubling in 3 years"

RULE TITLE-2: Maximum 15 words (Korean: ~25 characters)

RULE TITLE-3: Front-load the conclusion — most important fact goes first
              ❌ "After analyzing competitor data, we found a 4-point advantage"
              ✅ "We lead competitors on 4 of 6 core criteria"

RULE TITLE-4: Include quantification wherever possible
              ❌ "Costs were significantly reduced"
              ✅ "Operating costs reduced 37% via automation"

RULE TITLE-5: Reading all titles in sequence must tell the full story
              — this is the "title test" used by senior partners
```

---

## 7) Spatial Layout Algorithms

### 7.1 The 8px Grid System

All element placement snaps to multiples of 8px:

```
Canvas: 1920 × 1080px
Safe area: 100px,100px → 1820px,980px (margins)
Grid: 240 columns × 135 rows (at 8px intervals)

Standard snap points:
  8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, ...

Element placement:
  x, y, width, height must all be multiples of 8px
  Exception: text baseline can be any pixel, but container snaps to grid
```

### 7.2 Content Zone Allocation

Based on eye-tracking heat maps for slide scanning:

```
┌─────────────────────────────────────────────┐
│  TITLE ZONE (top 15%)                       │  ← 100% attention on scan entry
│  100px - 260px                              │
├─────────────────────────────────────────────┤
│                                             │
│  PRIMARY CONTENT ZONE (60%)                 │  ← 70-80% of viewing time
│  280px - 920px                              │
│                                             │
│  [ Hero element / Chart / Bullets ]         │
│                                             │
├─────────────────────────────────────────────┤
│  SOURCE / FOOTER ZONE (bottom 10%)          │  ← 5-10% attention
│  940px - 1040px                             │
└─────────────────────────────────────────────┘
```

### 7.3 Two-Column Split Rules

```
RULE SPLIT-1: 50:50 split — use when both sides have equal importance
RULE SPLIT-2: 60:40 split — use when one side has more content (text=60%)
RULE SPLIT-3: 65:35 split — use for chart + KPI sidebar layout
RULE SPLIT-4: Column gap must be 24-32px (3-4× on 8px grid)
RULE SPLIT-5: Column tops must align exactly
RULE SPLIT-6: Never split into 3+ columns on a slide — 
              cognitive load exceeds working memory
```

---

## 8) Information Density Guidelines

### 8.1 The Signal-to-Noise Ratio

Research source: Tufte, "The Visual Display of Quantitative Information" (2001).

```
RULE SNR-1: Data-ink ratio should approach 1.0 — 
            every pixel of ink should represent data
RULE SNR-2: Remove chart junk: background patterns, 3D effects, 
            gradient fills, excessive gridlines
RULE SNR-3: Use thin gridlines (#E0E0E0, 1px, dashed) not thick borders
RULE SNR-4: Remove default chart legends when direct labeling is possible
RULE SNR-5: Axis labels only where they add understanding — 
            if the data labels are sufficient, omit the axis
```

### 8.2 Content Density Targets

| Slide Type | Target Density | Words | Visual Elements |
|-----------|:---:|:---:|:---:|
| Hero metric | Very low | 5-10 | 1 number + 1 label |
| Single statement | Low | 10-20 | 1 sentence |
| Bullet list | Medium | 25-35 | 3-4 bullets |
| Data dashboard | Medium-high | 15-25 | KPI cards + 1 chart |
| Evidence bullets | Medium | 25-40 | 3-4 bullets + accent |
| Comparison | Medium | 30-40 | 2 columns × 3-4 items |
| Process flow | Low-medium | 15-25 | 3-8 labeled steps |

### 8.3 The 3-Second Rule

> **The viewer should grasp the slide's main message within 3 seconds.**

```
RULE 3S-1: The action title delivers the message in <2 seconds of reading
RULE 3S-2: The hero element (chart, number, image) confirms the message 
           in the next 1 second
RULE 3S-3: If neither the title nor the hero communicates the message,
           the slide fails the 3-second test
RULE 3S-4: Supporting text exists for the PRESENTER to elaborate,
           not for the audience to read
```

---

## 9) Deck-Level Rhythm and Flow

### 9.1 Narrative Arc

Research source: BCG storylining methodology, Minto Pyramid Principle.

```
RULE ARC-1: Deck follows: Context → Problem → Solution → Evidence → Impact → Action
RULE ARC-2: Each section transition uses a section-divider slide (dark bg)
RULE ARC-3: Visual density should oscillate: 
            high-density → low-density → high-density
            (never 3+ consecutive same-density slides)
RULE ARC-4: Maximum 2 consecutive slides with the same dominant element type
            (e.g., two chart slides in a row is OK, three is not)
RULE ARC-5: The deck must start with impact (Executive Summary)
            and end with action (CTA Closing)
```

### 9.2 Visual Variety Score

```
variety_score = unique_compositions / total_slides

RULE VAR-1: Variety score must be ≥0.6 (60% unique compositions)
RULE VAR-2: Track dominant_element across slides: 
            number, image, text, chart — alternate them
RULE VAR-3: Track composition type: hero-metric, split, evidence, comparison —
            no type should exceed 25% of total slides
```

### 9.3 Slide Count Guidelines

| Presentation Duration | Slide Count | Seconds/Slide |
|:---:|:---:|:---:|
| 5 min | 8-12 | 25-38s |
| 10 min | 15-20 | 30-40s |
| 20 min | 25-35 | 34-48s |
| 30 min | 35-45 | 40-51s |

```
RULE COUNT-1: Target 30-45 seconds per slide (average)
RULE COUNT-2: Data-heavy slides get 45-60 seconds
RULE COUNT-3: Statement/hero slides get 15-20 seconds
RULE COUNT-4: Section dividers get 5-10 seconds (transition only)
```

---

## 10) Summary: Top 20 Rules (Quick Reference)

| # | Rule | Source |
|---|------|--------|
| 1 | One message per slide, stated as action title | BCG/McKinsey |
| 2 | Maximum 4 bullets (optimal 3) | Cowan's 4±1 |
| 3 | 3-second comprehension test | Eye-tracking |
| 4 | Z-pattern default layout (title top-left, visual top-right) | Nielsen Norman |
| 5 | Front-load keywords in bullets (F-pattern first-word fixation) | Eye-tracking |
| 6 | Exactly 1 accent color instance per slide | Pre-attentive theory |
| 7 | 4-level visual hierarchy (hero → title → support → source) | Gestalt + consulting |
| 8 | Proximity ratio 1:2 (within-group : between-group spacing) | Gestalt proximity |
| 9 | All elements snap to 8px grid | Consistency = reduced cognitive load |
| 10 | Maximum 5 donut segments, 6 bars, 8 process steps | Working memory limits |
| 11 | Minimum 20% white space per slide | BCG standard |
| 12 | Squint test: hierarchy visible at 25% zoom | Consulting QA |
| 13 | No 3D charts, no pie charts (donut only), no chart junk | Tufte |
| 14 | Direct-label data points, minimize legends | Cognitive load reduction |
| 15 | Title test: reading only titles tells the full story | McKinsey Pyramid |
| 16 | Visual variety score ≥0.6 across deck | Deck rhythm |
| 17 | Max 2 consecutive same-density slides | Oscillation principle |
| 18 | Consistent positioning: title at same coordinates across all slides | Continuity principle |
| 19 | Body text minimum 16pt, hero number minimum 56px | Readability + size pre-attention |
| 20 | Source attribution on every data slide | Consulting credibility standard |
