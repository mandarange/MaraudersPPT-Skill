# Insight Extraction — Section Card Generation (Phase 1.3)

This document defines Phase 1 semantic analysis for MaraudersPPT Skill v2.0.
Purpose: convert each H2 section into a reliable `SectionCard` that preserves argument structure,
supports narrative planning, and enables deterministic visual/text downstream behavior.

## Scope and Pipeline Position

### Phase alignment

- Runs in Phase 1.3 after markdown sanitization and H2 parsing.
- Input unit: one H2 section with all child blocks.
- Output unit: one `SectionCard` per H2 section.
- Re-analysis is mandatory when `confidence < 0.5`.

### Downstream references

- Text compression rules: `references/content-distillation.md`.
- Visual prompt/image routing rules: `references/image-generation.md`.

## SectionCard Schema (12 Fields)

### Canonical schema

```yaml
SectionCard:
  source_section: string # "## Background"
  claim: string # one-sentence argument this section makes
  role: enum [problem, solution, evidence, context, meta]
  stakes: enum [high, medium, low]
  must_keep: boolean # can the story work without this section?
  insight: string # the audience's "aha" moment
  headline: string # action title candidate (<=15 words, with verb + conclusion)
  evidence: string[] # supporting data points
  accent_candidate: string # for Bold + #D94F4F (1 per slide max)
  kpi_metrics: string[] # executive summary candidates
  source_lines: [number, number] # line range in source MD
  confidence: float # 0.0-1.0, re-analyze if < 0.5
```

### Field definitions

| Field              | Meaning                  | Extraction guidance                   | Validation            |
| ------------------ | ------------------------ | ------------------------------------- | --------------------- |
| `source_section`   | Source anchor H2         | Preserve exact H2 text                | Must start with `## ` |
| `claim`            | Core section argument    | One sentence, decision-relevant       | Must be declarative   |
| `role`             | Analytical function      | Choose one dominant function          | Enum only             |
| `stakes`           | Omission consequence     | Estimate decision impact              | Enum only             |
| `must_keep`        | Story necessity          | True if core logic breaks without it  | Boolean only          |
| `insight`          | Audience realization     | "Aha" reframing, not topic summary    | Non-empty             |
| `headline`         | Slide-ready action title | <=15 words, verb + conclusion         | Verb required         |
| `evidence`         | Supporting proof points  | Quantitative or verifiable signals    | String array          |
| `accent_candidate` | Single emphasis phrase   | Highest rhetorical leverage token     | One phrase            |
| `kpi_metrics`      | Executive-scan metrics   | Rates, deltas, costs, throughput      | String array          |
| `source_lines`     | Traceability span        | `[start, end]` line range             | start <= end          |
| `confidence`       | Reliability score        | Semantic coherence + evidence quality | `0.0..1.0`            |

### Schema invariants

- Exactly these 12 fields; no additional keys.
- `claim`, `insight`, and `headline` must not collapse into one sentence.
- `accent_candidate` is a candidate token only, not styling output.
- `kpi_metrics` prefers measurable values over descriptive prose.

## Phase 1 Analytical Roles (5)

### Role definitions

| Role       | What it answers             | Signals                           | Guardrail                  |
| ---------- | --------------------------- | --------------------------------- | -------------------------- |
| `problem`  | What is failing now?        | pain, bottleneck, loss, risk      | Do not let fix dominate    |
| `solution` | What should be done?        | proposal, method, plan            | Must be actionable         |
| `evidence` | Why believe this?           | data, benchmark, case, experiment | Proof must dominate        |
| `context`  | What background is needed?  | history, constraints, definitions | Keep neutral framing       |
| `meta`     | How is this work organized? | scope, method, governance         | Administrative intent only |

### Role assignment guidance

- Choose by dominant rhetorical weight, not paragraph order.
- Data inside a proposal section usually remains `solution`, not `evidence`.
- Terminology/setup sections are generally `context`.
- Process/manual sections are generally `meta`.

## Phase 2 Narrative Roles (7) and Emotional Curve

### Narrative taxonomy

| Role       | Purpose                               | Emotional curve |
| ---------- | ------------------------------------- | --------------- |
| `hook`     | Capture attention in first 15 seconds | Curiosity up    |
| `problem`  | Surface pain and urgency              | Anxiety up      |
| `insight`  | Reveal turning point                  | Realization     |
| `solution` | Present core proposal                 | Hope up         |
| `proof`    | Validate with data/cases              | Trust up        |
| `impact`   | Show outcomes and future value        | Confidence up   |
| `cta`      | Ask for concrete next action          | Resolution      |

### Emotional pacing intent

- Early sequence: `hook` -> `problem`.
- Mid sequence: `insight` -> `solution`.
- Late sequence: `proof` -> `impact`.
- Close sequence: `cta` with owner and timing.

## Analytical -> Narrative Mapping

### Mapping table

| Analytical role | Primary narrative role | Secondary options    | Mapping rationale                           |
| --------------- | ---------------------- | -------------------- | ------------------------------------------- |
| `problem`       | `problem`              | `hook`, `insight`    | Pain can open urgency or trigger pivot      |
| `solution`      | `solution`             | `impact`, `cta`      | Execution can route to value or ask         |
| `evidence`      | `proof`                | `impact`, `insight`  | Validation supports trust and turning point |
| `context`       | `hook`                 | `insight`, `problem` | Background can frame stakes early           |
| `meta`          | `cta`                  | `hook`               | Governance often supports decision ask      |

### Mapping constraints

- Planning can be one-to-many, but each final slide has one narrative role.
- Preserve `source_section` and `source_lines` for traceability.
- If `must_keep=true`, route to deck/appendix with explicit reason.

## Extraction Algorithm (Phase 1.3)

### Phase 1.3.1 Parse H2 boundaries

- Segment markdown by H2.
- Bind child blocks until next H2.
- Record `[start, end]` line span.

### Phase 1.3.2 Normalize content units

- Convert paragraphs, bullets, tables, code intent, and image captions into analyzable units.
- Preserve links and references as possible evidence.
- Ensure markdown token sanitization is complete in Phase 1.

### Phase 1.3.3 Extract claim

- Synthesize one sentence that states what the section argues.
- Prefer causal, decision-relevant language.
- Reject topic-label summaries.

### Phase 1.3.4 Assign analytical role

- Score role candidates using dominant intent signals.
- Select one role from `problem|solution|evidence|context|meta`.
- Resolve ties by section conclusion emphasis.

### Phase 1.3.5 Derive stakes and must_keep

- Estimate omission impact on decision quality.
- Set `stakes=high` when omission can change recommendation.
- Set `must_keep=true` when logic/proof is non-redundant.

### Phase 1.3.6 Identify evidence and kpi_metrics

- Extract quantitative and verifiable support into `evidence`.
- Promote executive-scan numbers into `kpi_metrics`.
- Keep phrasing compact and scan-friendly.

### Phase 1.3.7 Select insight, headline, accent_candidate

- Write `insight` as the audience turning realization.
- Generate `headline` with verb + conclusion (<=15 words).
- Choose one high-leverage `accent_candidate` phrase.

### Phase 1.3.8 Compute confidence

- Score consistency among `claim`, `role`, `insight`, `evidence`, and source text.
- Increase confidence for specific and traceable evidence.
- Decrease confidence for mixed intent or speculative interpretation.

## Confidence Scoring Rules

### High confidence (0.8+)

- Claim is explicit in source text.
- Role has clear dominance with minimal overlap.
- Evidence is concrete (numbers, entities, reproducible facts).
- Insight follows directly from claim/evidence.
- Headline aligns with claim without semantic drift.

### Medium confidence (0.5-0.79)

- Claim is inferable but partially implicit.
- Role is plausible with some overlap.
- Evidence exists but is incomplete or weakly quantified.

### Low confidence (<0.5)

- Section lacks coherent argument.
- Role conflict remains unresolved.
- Evidence is missing or disconnected from claim.
- Insight/headline require speculation.

### Re-analysis protocol

- If `confidence < 0.5`, re-run Phase 1.3 extraction for that section.
- Re-check role dominance, claim wording, and evidence linkage.
- If still low, reduce stakes and mark for appendix-safe routing.

## Anti-Patterns and Common Mistakes

### Keyword stuffing

- Symptom: dense nouns with weak argument structure.
- Failure mode: large evidence list but no usable insight.
- Correction: force one claim and causal support.

### Missing claim

- Symptom: topic summary without argument sentence.
- Failure mode: unstable role mapping.
- Correction: generate claim before any role decision.

### Role confusion

- Symptom: problem and solution mixed with no dominance.
- Failure mode: broken emotional arc in Phase 2.
- Correction: pick dominant role; move secondary material to evidence.

### Accent overuse

- Symptom: multiple candidate phrases compete.
- Failure mode: weak hierarchy and style-rule violations.
- Correction: keep exactly one `accent_candidate`.

## Example: H2 Section -> SectionCard

### Source H2 section

```md
## Checkout Latency

Average checkout time increased from 1.8s to 3.1s after the Q3 release.
This adds approximately 83 lost processing hours per day at 100k daily transactions.

- Conversion dropped 4.2% week-over-week
- Mobile users account for 71% of affected traffic
- Timeout incidents rose from 0.3% to 1.1%
```

### Extracted SectionCard

```yaml
SectionCard:
  source_section: "## Checkout Latency"
  claim: "Checkout latency after Q3 now causes measurable revenue and throughput loss."
  role: problem
  stakes: high
  must_keep: true
  insight: "Latency is no longer technical noise; it is a direct business loss driver."
  headline: "Reduce checkout latency to recover conversion and processing capacity"
  evidence:
    - "Average checkout increased 1.8s -> 3.1s after Q3 release"
    - "~83 processing hours lost per day at 100k daily transactions"
    - "Conversion decreased 4.2% week-over-week"
    - "Timeout incidents increased 0.3% -> 1.1%"
  accent_candidate: "83 lost hours/day"
  kpi_metrics:
    - "3.1s average checkout"
    - "-4.2% conversion WoW"
    - "1.1% timeout rate"
  source_lines: [1, 9]
  confidence: 0.92
```

### Why confidence is high

- Claim, role, and evidence are mutually consistent.
- Multiple quantified signals support the same argument direction.
- Insight reframes technical latency into executive impact.
