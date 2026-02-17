# SVG Component Library — Inline SVG for Slide Rendering

> **Purpose**: Production-ready inline SVG patterns for charts, shapes, diagrams, and icons.
> All components render statically in HTML→Playwright→PDF pipeline. Zero external dependencies.
> Canvas: 720pt × 405pt (1920×1080px at 96dpi). Colors: bg `#FFFFFF`, text `#1A1A1A`, accent `#D94F4F`.

---

## 1) Design Principles for SVG in Slides

### 1.1 Why SVG over CSS-only

| Scenario | CSS-only | SVG | Winner |
|----------|----------|-----|--------|
| Bar charts | `width: %` works | `<rect>` more precise | CSS (simpler) |
| Donut charts | `conic-gradient` + mask | `<circle stroke-dasharray>` | SVG (PDF-safe, no mask bugs) |
| Sparklines/trend lines | Not possible | `<polyline>` native | **SVG only** |
| Flow arrows with heads | Pseudo-elements fragile | `<marker>` + `<line>` | **SVG only** |
| Numbered circles | `border-radius` + flexbox | `<circle>` + `<text>` | SVG (precise) |
| Progress arcs | `conic-gradient` | `stroke-dashoffset` | SVG (animatable, precise) |
| Icons (check, arrow, x) | Unicode/emoji | `<path>` crisp at all sizes | **SVG only** |

**Rule**: Use existing CSS chart templates (Section 15.7) when they suffice. Use SVG when:
- Curved shapes, arcs, or precise geometry needed
- Arrow markers / connector lines required
- Trend lines / sparklines needed
- Crisp icons at any scale needed

### 1.2 SVG Rendering Constraints (Playwright PDF)

| Constraint | Rule |
|-----------|------|
| No `<script>` | SVG must be purely declarative — no JavaScript |
| No CSS animations | `@keyframes`, `transition` ignored in PDF capture |
| No `<foreignObject>` | Playwright may not render nested HTML in SVG reliably |
| Font embedding | Use `font-family: Arial, Helvetica, sans-serif` (system fonts guaranteed) |
| `viewBox` required | Always set `viewBox` for scalability. Never use fixed `width`/`height` in px |
| Inline styles only | No external CSS references — use `style=""` or `<style>` block inside SVG |
| No `filter` effects | `<filter>`, `feGaussianBlur` unreliable in PDF render |
| Color compliance | Only palette colors: `#1A1A1A`, `#555555`, `#888888`, `#CCCCCC`, `#E0E0E0`, `#D94F4F`, `#FFFFFF` |

### 1.3 SVG Coordinate System

All SVG components use a standardized `viewBox` system:

```
Full-width chart:  viewBox="0 0 600 300"   (2:1 landscape)
Half-width chart:  viewBox="0 0 300 300"   (1:1 square, for donut/gauge)
Inline icon:       viewBox="0 0 24 24"     (icon standard)
Sparkline:         viewBox="0 0 200 60"    (wide + short)
```

---

## 2) SVG Component Catalog

### 2.1 Horizontal Bar Chart

**Pattern**: `NUM-COMPARE` — numeric comparison across items.
**When**: CSS `.bar-chart-h` (Section 15.7.2) is the primary. Use SVG version when bars need value labels rendered inside bars or when embedding in a mixed SVG composition.

```html
<svg viewBox="0 0 600 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Horizontal bar chart">
  <style>
    .bar-label { font: 500 14px Arial, Helvetica, sans-serif; fill: #555555; }
    .bar-value { font: 700 14px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .bar-fill { rx: 1; ry: 1; }
  </style>

  <!-- Row 1: Q1 — 95% (max) -->
  <text x="70" y="38" text-anchor="end" class="bar-label">Q1</text>
  <rect x="80" y="22" width="0" height="28" fill="#F2F2F2" rx="1" ry="1" class="bar-track" />
  <rect x="80" y="22" width="456" height="28" fill="#F2F2F2" rx="1" ry="1" />
  <rect x="80" y="22" width="433" height="28" fill="#1A1A1A" class="bar-fill" />
  <text x="520" y="42" class="bar-value">95%</text>

  <!-- Row 2: Q2 — 78% -->
  <text x="70" y="98" text-anchor="end" class="bar-label">Q2</text>
  <rect x="80" y="82" width="456" height="28" fill="#F2F2F2" rx="1" ry="1" />
  <rect x="80" y="82" width="356" height="28" fill="#CCCCCC" class="bar-fill" />
  <text x="520" y="102" class="bar-value">78%</text>

  <!-- Row 3: Q3 — 88% (accent) -->
  <text x="70" y="158" text-anchor="end" class="bar-label">Q3</text>
  <rect x="80" y="142" width="456" height="28" fill="#F2F2F2" rx="1" ry="1" />
  <rect x="80" y="142" width="401" height="28" fill="#D94F4F" class="bar-fill" />
  <text x="520" y="162" class="bar-value">88%</text>

  <!-- Row 4: Q4 — 72% -->
  <text x="70" y="218" text-anchor="end" class="bar-label">Q4</text>
  <rect x="80" y="202" width="456" height="28" fill="#F2F2F2" rx="1" ry="1" />
  <rect x="80" y="202" width="328" height="28" fill="#CCCCCC" class="bar-fill" />
  <text x="520" y="222" class="bar-value">72%</text>

  <!-- Axis line -->
  <line x1="80" y1="240" x2="536" y2="240" stroke="#E0E0E0" stroke-width="1" />
</svg>
```

**Construction formula**:
```
bar_width = (value / max_value) * max_bar_px
max_bar_px = viewBox_width - label_area - value_area - margins
row_y = start_y + (row_index * row_height)
row_height = bar_height + gap  (typically 28px bar + 32px gap = 60px)
```

**Rules**:
- Max bar = `#1A1A1A` (black), other bars = `#CCCCCC`, accent bar = `#D94F4F`
- Max 6 bars. If >6, split into two charts or use top-N
- Labels right-aligned, values right-aligned after bar track
- Track background: `#F2F2F2`

---

### 2.2 Donut / Circle Chart

**Pattern**: `PCT-BREAKDOWN` — proportional share visualization.
**Math**: Uses SVG `<circle>` with `stroke-dasharray` and `stroke-dashoffset`.

```html
<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Donut chart showing market share">
  <style>
    .donut-label { font: 700 42px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .donut-sublabel { font: 500 14px Arial, Helvetica, sans-serif; fill: #555555; }
    .donut-segment { fill: none; stroke-width: 36; }
  </style>

  <!-- 
    Circle math:
    radius = 100, circumference = 2πr = 628.318
    Segment 1 (APAC 42%): dasharray = 263.9 628.318, offset = 0
    Segment 2 (EMEA 31%): dasharray = 194.8 628.318, offset = -263.9
    Segment 3 (Americas 27%): dasharray = 169.6 628.318, offset = -458.7
    All circles rotate -90deg to start from 12 o'clock
  -->

  <!-- Background ring -->
  <circle cx="150" cy="150" r="100" fill="none" stroke="#F2F2F2" stroke-width="36" />

  <!-- Segment 1: APAC 42% -->
  <circle cx="150" cy="150" r="100" class="donut-segment"
    stroke="#1A1A1A"
    stroke-dasharray="263.9 628.318"
    stroke-dashoffset="0"
    transform="rotate(-90 150 150)" />

  <!-- Segment 2: EMEA 31% -->
  <circle cx="150" cy="150" r="100" class="donut-segment"
    stroke="#888888"
    stroke-dasharray="194.8 628.318"
    stroke-dashoffset="-263.9"
    transform="rotate(-90 150 150)" />

  <!-- Segment 3: Americas 27% (accent) -->
  <circle cx="150" cy="150" r="100" class="donut-segment"
    stroke="#D94F4F"
    stroke-dasharray="169.6 628.318"
    stroke-dashoffset="-458.7"
    transform="rotate(-90 150 150)" />

  <!-- Center text -->
  <text x="150" y="145" text-anchor="middle" class="donut-label">42%</text>
  <text x="150" y="170" text-anchor="middle" class="donut-sublabel">APAC</text>
</svg>
```

**Construction formula**:
```
circumference = 2 * π * radius          // 628.318 for r=100
segment_length = (percentage / 100) * circumference
dash_offset = -(sum of previous segments)
All segments: stroke-dasharray="segment_length circumference"
Rotate -90 to start from top (12 o'clock position)
```

**Segment color rules** (max 5 segments):
```
Segment 1 (largest): #1A1A1A
Segment 2:           #555555
Segment 3:           #888888
Segment 4:           #CCCCCC
Accent (1 max):      #D94F4F
```

---

### 2.3 Sparkline / Trend Line

**Pattern**: Compact trend indicator, typically placed next to KPI values.
**Use case**: Show direction of change within a KPI card or inline metric.

```html
<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Trend line showing upward growth">
  <style>
    .spark-line { fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .spark-area { opacity: 0.08; }
    .spark-dot { r: 3; }
  </style>

  <!-- Area fill (subtle) -->
  <polygon
    points="10,48 40,42 70,38 100,30 130,26 160,18 190,12 190,55 10,55"
    fill="#1A1A1A" class="spark-area" />

  <!-- Line -->
  <polyline
    points="10,48 40,42 70,38 100,30 130,26 160,18 190,12"
    class="spark-line" stroke="#1A1A1A" />

  <!-- End dot (current value) -->
  <circle cx="190" cy="12" class="spark-dot" fill="#1A1A1A" />

  <!-- Start dot (reference) -->
  <circle cx="10" cy="48" r="2" fill="#CCCCCC" />
</svg>
```

**Accent variant** (negative trend):
```html
<polyline points="10,12 40,18 70,26 100,30 130,38 160,42 190,48"
  class="spark-line" stroke="#D94F4F" />
<circle cx="190" cy="48" class="spark-dot" fill="#D94F4F" />
```

**Construction formula**:
```
x_step = (viewBox_width - 2*padding) / (data_points - 1)
y_value = viewBox_height - padding - (normalized_value * available_height)
normalized_value = (value - min) / (max - min)
```

**Rules**:
- Positive trend: `#1A1A1A` line + area
- Negative trend: `#D94F4F` line + area
- Flat/neutral: `#888888` line, no area
- Max 12 data points
- Always include end-dot for current value

---

### 2.4 Process Flow with Arrows

**Pattern**: `SEQ-STEPS` — step-based pipeline visualization.
**When**: Use SVG when you need actual arrow markers (not `→` text), curved connectors, or mixed with other SVG elements.

```html
<svg viewBox="0 0 720 160" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Process flow: Input to Output">
  <defs>
    <!-- Arrow marker -->
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#CCCCCC" />
    </marker>
    <marker id="arrow-accent" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <polygon points="0 0, 8 4, 0 8" fill="#D94F4F" />
    </marker>
  </defs>

  <style>
    .step-box { fill: #FFFFFF; stroke: #E0E0E0; stroke-width: 1; rx: 2; ry: 2; }
    .step-box-active { fill: #1A1A1A; stroke: #1A1A1A; }
    .step-no { font: 700 11px Arial, Helvetica, sans-serif; fill: #888888; }
    .step-no-active { fill: rgba(255,255,255,0.5); }
    .step-label { font: 700 14px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .step-label-active { fill: #FFFFFF; }
    .connector { stroke: #CCCCCC; stroke-width: 1.5; fill: none; }
  </style>

  <!-- Step 1 -->
  <rect x="10" y="30" width="120" height="100" class="step-box" />
  <text x="70" y="65" text-anchor="middle" class="step-no">01</text>
  <text x="70" y="90" text-anchor="middle" class="step-label">Input</text>

  <!-- Connector 1→2 -->
  <line x1="130" y1="80" x2="170" y2="80" class="connector" marker-end="url(#arrow)" />

  <!-- Step 2 -->
  <rect x="180" y="30" width="120" height="100" class="step-box" />
  <text x="240" y="65" text-anchor="middle" class="step-no">02</text>
  <text x="240" y="90" text-anchor="middle" class="step-label">Parse</text>

  <!-- Connector 2→3 -->
  <line x1="300" y1="80" x2="340" y2="80" class="connector" marker-end="url(#arrow)" />

  <!-- Step 3 (active) -->
  <rect x="350" y="30" width="120" height="100" class="step-box step-box-active" />
  <text x="410" y="65" text-anchor="middle" class="step-no step-no-active">03</text>
  <text x="410" y="90" text-anchor="middle" class="step-label step-label-active">Map</text>

  <!-- Connector 3→4 -->
  <line x1="470" y1="80" x2="510" y2="80" class="connector" marker-end="url(#arrow)" />

  <!-- Step 4 -->
  <rect x="520" y="30" width="120" height="100" class="step-box" />
  <text x="580" y="65" text-anchor="middle" class="step-no">04</text>
  <text x="580" y="90" text-anchor="middle" class="step-label">Output</text>
</svg>
```

**Construction formula**:
```
step_width = (viewBox_width - total_gap - 2*margin) / num_steps
gap = 40 (connector zone)
step_x = margin + step_index * (step_width + gap)
connector: x1 = step_x + step_width, x2 = next_step_x, y = center_y
```

---

### 2.5 Timeline

**Pattern**: `CHRONOLOGICAL` — date-ordered milestones along a horizontal axis.

```html
<svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Project timeline">
  <style>
    .tl-line { stroke: #E0E0E0; stroke-width: 2; }
    .tl-dot { r: 8; fill: #1A1A1A; stroke: #FFFFFF; stroke-width: 3; }
    .tl-dot-accent { fill: #D94F4F; }
    .tl-date { font: 600 12px Arial, Helvetica, sans-serif; fill: #555555; }
    .tl-event { font: 700 14px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .tl-desc { font: 400 11px Arial, Helvetica, sans-serif; fill: #888888; }
  </style>

  <!-- Main horizontal line -->
  <line x1="40" y1="100" x2="680" y2="100" class="tl-line" />

  <!-- Milestone 1 (accent — current/first) -->
  <circle cx="120" cy="100" class="tl-dot tl-dot-accent" />
  <text x="120" y="75" text-anchor="middle" class="tl-date">2025 Q1</text>
  <text x="120" y="135" text-anchor="middle" class="tl-event">MVP Launch</text>
  <text x="120" y="152" text-anchor="middle" class="tl-desc">Core engine</text>

  <!-- Milestone 2 -->
  <circle cx="300" cy="100" class="tl-dot" />
  <text x="300" y="75" text-anchor="middle" class="tl-date">2025 Q2</text>
  <text x="300" y="135" text-anchor="middle" class="tl-event">Chart Support</text>
  <text x="300" y="152" text-anchor="middle" class="tl-desc">8 chart types</text>

  <!-- Milestone 3 -->
  <circle cx="480" cy="100" class="tl-dot" />
  <text x="480" y="75" text-anchor="middle" class="tl-date">2025 Q3</text>
  <text x="480" y="135" text-anchor="middle" class="tl-event">AI Automation</text>
  <text x="480" y="152" text-anchor="middle" class="tl-desc">Image gen</text>

  <!-- Milestone 4 -->
  <circle cx="640" cy="100" class="tl-dot" />
  <text x="640" y="75" text-anchor="middle" class="tl-date">2025 Q4</text>
  <text x="640" y="135" text-anchor="middle" class="tl-event">Enterprise</text>
  <text x="640" y="152" text-anchor="middle" class="tl-desc">Multi-theme</text>
</svg>
```

**Construction formula**:
```
item_x = margin + (index / (total_items - 1)) * (viewBox_width - 2*margin)
Top text (date): y = center_y - 25
Bottom text (event): y = center_y + 35
Description: y = center_y + 52
```

---

### 2.6 Icon Shapes

Crisp SVG icons for use inside cards, process steps, or inline with text.
All icons use `viewBox="0 0 24 24"` standard.

#### 2.6.1 Checkmark

```html
<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="11" fill="#1A1A1A" />
  <polyline points="7,12 10.5,15.5 17,8.5" fill="none"
    stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
</svg>
```

#### 2.6.2 Arrow Right

```html
<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <line x1="4" y1="12" x2="20" y2="12" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" />
  <polyline points="14,6 20,12 14,18" fill="none"
    stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
</svg>
```

#### 2.6.3 Circle with Number

```html
<svg viewBox="0 0 32 32" width="32" height="32" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="14" fill="#1A1A1A" />
  <text x="16" y="21" text-anchor="middle"
    font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="#FFFFFF">3</text>
</svg>
```

**Accent variant**:
```html
<circle cx="16" cy="16" r="14" fill="#D94F4F" />
```

#### 2.6.4 Warning Triangle

```html
<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2 L22 20 L2 20 Z" fill="none" stroke="#D94F4F" stroke-width="2"
    stroke-linejoin="round" />
  <line x1="12" y1="9" x2="12" y2="14" stroke="#D94F4F" stroke-width="2" stroke-linecap="round" />
  <circle cx="12" cy="17" r="1" fill="#D94F4F" />
</svg>
```

#### 2.6.5 Cross / X

```html
<svg viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="11" fill="#888888" />
  <line x1="8" y1="8" x2="16" y2="16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" />
  <line x1="16" y1="8" x2="8" y2="16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" />
</svg>
```

#### 2.6.6 Up Arrow (KPI positive)

```html
<svg viewBox="0 0 16 16" width="16" height="16" xmlns="http://www.w3.org/2000/svg">
  <polygon points="8,2 14,10 2,10" fill="#1A1A1A" />
</svg>
```

#### 2.6.7 Down Arrow (KPI negative)

```html
<svg viewBox="0 0 16 16" width="16" height="16" xmlns="http://www.w3.org/2000/svg">
  <polygon points="8,14 14,6 2,6" fill="#D94F4F" />
</svg>
```

---

### 2.7 Progress Bar / Gauge

**Use case**: Completion %, goal attainment, capacity utilization.

#### 2.7.1 Linear Progress Bar

```html
<svg viewBox="0 0 400 40" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Progress: 73%">
  <style>
    .prog-label { font: 500 12px Arial, Helvetica, sans-serif; fill: #555555; }
    .prog-value { font: 700 14px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
  </style>

  <text x="0" y="12" class="prog-label">Completion</text>
  <text x="400" y="12" text-anchor="end" class="prog-value">73%</text>

  <!-- Track -->
  <rect x="0" y="20" width="400" height="12" rx="2" ry="2" fill="#F2F2F2" />
  <!-- Fill -->
  <rect x="0" y="20" width="292" height="12" rx="2" ry="2" fill="#1A1A1A" />
</svg>
```

#### 2.7.2 Circular Gauge (Semi-circle)

```html
<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Score: 85%">
  <style>
    .gauge-value { font: 700 32px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .gauge-label { font: 500 12px Arial, Helvetica, sans-serif; fill: #555555; }
  </style>

  <!-- 
    Semi-circle gauge: r=80, center at (100,100)
    Half circumference = π * 80 = 251.327
    85% of half = 213.628
  -->

  <!-- Track (half circle) -->
  <path d="M 20,100 A 80,80 0 0,1 180,100" fill="none"
    stroke="#F2F2F2" stroke-width="16" stroke-linecap="round" />

  <!-- Fill (85%) -->
  <path d="M 20,100 A 80,80 0 0,1 180,100" fill="none"
    stroke="#1A1A1A" stroke-width="16" stroke-linecap="round"
    stroke-dasharray="213.6 251.3" />

  <!-- Center text -->
  <text x="100" y="95" text-anchor="middle" class="gauge-value">85%</text>
  <text x="100" y="115" text-anchor="middle" class="gauge-label">Score</text>
</svg>
```

---

### 2.8 Connector Lines (for diagram compositions)

Reusable `<defs>` block for arrow markers + line patterns:

```html
<defs>
  <!-- Standard arrow (dark) -->
  <marker id="arr-dark" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#1A1A1A" />
  </marker>

  <!-- Light arrow (for secondary paths) -->
  <marker id="arr-light" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#CCCCCC" />
  </marker>

  <!-- Accent arrow -->
  <marker id="arr-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#D94F4F" />
  </marker>

  <!-- Circle start marker -->
  <marker id="dot-start" markerWidth="6" markerHeight="6" refX="3" refY="3">
    <circle cx="3" cy="3" r="3" fill="#888888" />
  </marker>
</defs>

<!-- Usage examples -->
<line x1="50" y1="50" x2="200" y2="50" stroke="#1A1A1A" stroke-width="1.5"
  marker-end="url(#arr-dark)" />

<!-- Curved connector -->
<path d="M 50,80 C 100,80 100,120 150,120" stroke="#CCCCCC" stroke-width="1.5"
  fill="none" marker-end="url(#arr-light)" />

<!-- Right-angle connector -->
<polyline points="50,150 100,150 100,200 150,200" stroke="#1A1A1A" stroke-width="1.5"
  fill="none" marker-end="url(#arr-dark)" />
```

---

## 3) Composition Patterns

### 3.1 KPI Card with Sparkline (SVG hybrid)

Combines a KPI value with an inline sparkline:

```html
<div class="kpi-card">
  <p class="kpi-label">Monthly Revenue</p>
  <div style="display: flex; align-items: center; gap: 16px;">
    <p class="kpi-value">$2.4M</p>
    <svg viewBox="0 0 120 40" width="120" height="40" xmlns="http://www.w3.org/2000/svg">
      <polygon points="5,35 20,30 40,28 60,22 80,18 100,12 115,8 115,38 5,38"
        fill="#1A1A1A" opacity="0.06" />
      <polyline points="5,35 20,30 40,28 60,22 80,18 100,12 115,8"
        fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linecap="round" />
      <circle cx="115" cy="8" r="3" fill="#1A1A1A" />
    </svg>
  </div>
  <p class="kpi-delta">▲ +12% vs prev quarter</p>
</div>
```

### 3.2 Decision Tree / Flow Diagram

For complex multi-path flows, combine boxes + connectors:

```html
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Decision flow">
  <defs>
    <marker id="flow-arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#CCCCCC" />
    </marker>
  </defs>
  <style>
    .node { fill: #FFFFFF; stroke: #E0E0E0; stroke-width: 1; rx: 2; }
    .node-active { fill: #1A1A1A; stroke: #1A1A1A; }
    .node-text { font: 700 13px Arial, Helvetica, sans-serif; fill: #1A1A1A; }
    .node-text-active { fill: #FFFFFF; }
    .decision { fill: #FFFFFF; stroke: #E0E0E0; stroke-width: 1; }
    .edge { stroke: #CCCCCC; stroke-width: 1.5; fill: none; }
    .edge-label { font: 400 10px Arial, Helvetica, sans-serif; fill: #888888; }
  </style>

  <!-- Start node -->
  <rect x="240" y="10" width="120" height="50" class="node node-active" />
  <text x="300" y="40" text-anchor="middle" class="node-text node-text-active">Start</text>

  <!-- Connector to decision -->
  <line x1="300" y1="60" x2="300" y2="100" class="edge" marker-end="url(#flow-arr)" />

  <!-- Decision diamond -->
  <polygon points="300,100 370,150 300,200 230,150" class="decision" />
  <text x="300" y="155" text-anchor="middle" class="node-text">Condition?</text>

  <!-- Yes branch -->
  <line x1="370" y1="150" x2="480" y2="150" class="edge" marker-end="url(#flow-arr)" />
  <text x="420" y="143" class="edge-label">Yes</text>
  <rect x="490" y="125" width="100" height="50" class="node" />
  <text x="540" y="155" text-anchor="middle" class="node-text">Action A</text>

  <!-- No branch -->
  <line x1="230" y1="150" x2="120" y2="150" class="edge" marker-end="url(#flow-arr)" />
  <text x="170" y="143" class="edge-label">No</text>
  <rect x="10" y="125" width="100" height="50" class="node" />
  <text x="60" y="155" text-anchor="middle" class="node-text">Action B</text>
</svg>
```

---

## 4) Integration Rules

### 4.1 How SVG Components Are Used in the Pipeline

```
1. AI detects data pattern (Section 15.6)
2. If pattern maps to SVG-appropriate type:
   → Generate inline SVG with computed values
   → Embed directly in slide HTML (<div class="content">...</div>)
3. Playwright renders HTML (with SVG) → PDF page
```

### 4.2 SVG vs CSS Chart Decision Matrix

| Feature Needed | Use CSS (Section 15.7) | Use SVG (this section) |
|---------------|:---:|:---:|
| Simple bar chart | ✅ | — |
| Donut with `conic-gradient` working | ✅ | — |
| Donut needs PDF-safe rendering | — | ✅ |
| Sparkline / trend line | — | ✅ |
| Arrow connectors between shapes | — | ✅ |
| Numbered step circles | — | ✅ |
| Flow diagram with decision nodes | — | ✅ |
| Progress arc / gauge | — | ✅ |
| Icon shapes (check, arrow, x) | — | ✅ |
| KPI card with inline sparkline | Mixed | ✅ (sparkline part) |

### 4.3 Color Mapping (Palette Compliance)

| Role | SVG Fill/Stroke | HEX |
|------|----------------|-----|
| Primary data / max bar / active node | `fill` or `stroke` | `#1A1A1A` |
| Secondary data | `fill` or `stroke` | `#555555` |
| Tertiary data | `fill` or `stroke` | `#888888` |
| Quaternary data | `fill` or `stroke` | `#CCCCCC` |
| Track / background | `fill` | `#F2F2F2` |
| Grid / axis / border | `stroke` | `#E0E0E0` |
| Accent (max 1 per chart) | `fill` or `stroke` | `#D94F4F` |
| Text on dark fill | `fill` | `#FFFFFF` |

### 4.4 Accessibility

- All SVG roots: `role="img"` + `aria-label="description"`
- Data labels always present (never color-only encoding)
- Minimum stroke-width: `1.5px` for lines, `1px` for borders
- Font minimum: `11px` for SVG text (maps to ~12pt at slide scale)
