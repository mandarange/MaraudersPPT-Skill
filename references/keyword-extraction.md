# Core Keyword Extraction (Step 2.3)

> **This is the single most important step for PPT quality.**
> A presentation without properly extracted keywords is just a text dump on slides.
> Every slide MUST be driven by its extracted keywords — not raw MD text.

Extract **core keywords** from each section's content. These keywords drive every downstream decision: action titles, accent words, bullet prioritization, and executive summary content.

## Extraction Targets (scan in priority order)

| Priority | Source | What to Extract | Example |
|----------|--------|----------------|---------|
| 1 | `**bold text**` | Explicitly emphasized terms | `**3x faster**` → "3x faster" |
| 2 | Numbers + units | Metrics, KPIs, quantitative data | "95%", "$2.4M", "3 seconds → 0.8 seconds" |
| 3 | `[AI DECISION]` / `[AI RULE]` | Key decisions and constraints | "Adopt MSA architecture" |
| 4 | Comparison phrases | Before/after, improved/reduced | "failure rate reduced by 73%" |
| 5 | Proper nouns | Technology, product, company names | "PostgreSQL", "Kubernetes", "MaraudersMapMD" |
| 6 | Action verbs + outcomes | Conclusive statements | "eliminates manual review", "automates deployment" |

## Per-Section Output

For each H2 section, produce:

```
Section Keywords = {
  section_title: "Background",
  primary_keyword: "processing speed 3x improvement",     ← Single most impactful phrase (drives action title)
  accent_candidate: "3 seconds → 0.8 seconds",            ← For Bold+#D94F4F treatment (1 per slide max)
  supporting_keywords: ["failure rate 73% reduction", "MSA architecture"],  ← Secondary emphasis (Bold only)
  kpi_metrics: ["95% success rate", "2.5% → 0.7% failure rate"],           ← Feed executive summary
}
```

## Keyword Usage Rules (MANDATORY)

| Usage Point | How Keywords Are Applied |
|-------------|------------------------|
| **Action Title** | `primary_keyword` → Rewrite as complete sentence (≤15 words) with verb + conclusion |
| **Accent Word** | `accent_candidate` → Apply Bold + `#D94F4F` (1 per slide, word-level only) |
| **Bullet Priority** | Bullets containing `supporting_keywords` ranked first in slide |
| **Executive Summary** | Top 3–5 `kpi_metrics` across all sections → KPI cards |
| **Slide Focus** | Each slide must revolve around its `primary_keyword` — no unfocused slides |

## Keyword Density Control

- **Per slide**: Exactly 1 `accent_candidate` (Bold + Red) + up to 2 `supporting_keywords` (Bold only)
- **Per deck**: All `kpi_metrics` must appear in Executive Summary
- **If no keywords found in section**: Flag as low-value content → candidate for merge with adjacent section or appendix

## Anti-Pattern: Raw Text Dump (PROHIBITED)

```
❌ WRONG — Dumping MD text directly onto slide:
   Title: "Background"
   Body: "The existing payment system has the following problems:
          Slow processing speed (average 3 seconds),
          High failure rate (2.5%), No monitoring"

✅ CORRECT — Keyword-driven slide:
   Title: "Processing speed 3x bottleneck demands architecture overhaul"
   Body: • Processing speed: **3 seconds** average (target: <1s)
         • Failure rate: **2.5%** — 73% above industry benchmark
         • Zero monitoring coverage across all services
   Accent: "3 seconds" in Bold + #D94F4F
```
