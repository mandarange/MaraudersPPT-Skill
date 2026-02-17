"""Funnel — Stage-based drop-off pipeline (Awareness → Conversion → Purchase).

data = [
    {"label": "Awareness",  "value": "10K"},
    {"label": "Interest",   "value": "7.5K"},
    {"label": "Decision",   "value": "5K", "accent": True},
    {"label": "Action",     "value": "2.5K"},
    {"label": "Repurchase", "value": "1K"},
]
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.funnel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.funnel-stage {
  margin: 0 auto;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-sizing: border-box;
  border-radius: 2px;
}

.stage-1 { background: #1A1A1A; }
.stage-2 { background: #444444; }
.stage-3 { background: #777777; }
.stage-4 { background: #B0B0B0; }
.stage-5 { background: #E8E8E8; }

.funnel-stage.is-accent {
  background: #D94F4F;
}

.funnel-label {
  margin: 0;
  font-size: 18px;
  line-height: 24px;
  font-weight: 600;
  letter-spacing: -0.2px;
}

.funnel-value {
  margin: 0;
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stage-1 .funnel-label, .stage-1 .funnel-value,
.stage-2 .funnel-label, .stage-2 .funnel-value,
.stage-3 .funnel-label, .stage-3 .funnel-value,
.funnel-stage.is-accent .funnel-label,
.funnel-stage.is-accent .funnel-value {
  color: #FFFFFF;
}

.stage-4 .funnel-label, .stage-4 .funnel-value { color: #333333; }
.stage-5 .funnel-label, .stage-5 .funnel-value { color: #555555; }"""

CSS = full_css(_CSS)

# Grayscale stage palette (up to 7 stages)
_STAGE_COLORS = [
    "#1A1A1A",
    "#444444",
    "#666666",
    "#888888",
    "#AAAAAA",
    "#CCCCCC",
    "#E8E8E8",
]
_LIGHT_THRESHOLD = 3  # Use dark text from this index onward


def render(data: list[dict[str, Any]]) -> str:
    """Funnel HTML. Stage width decreases linearly."""
    n = len(data)
    stages = []
    for i, item in enumerate(data):
        width_pct = 100 - (i * (80 / max(n - 1, 1)))
        stage_num = min(i + 1, 5)
        accent = " is-accent" if item.get("accent") else ""
        stages.append(
            f'  <div class="funnel-stage stage-{stage_num}{accent}" '
            f'style="width:{width_pct:.0f}%;">\n'
            f'    <p class="funnel-label">{esc(item["label"])}</p>\n'
            f'    <p class="funnel-value">{esc(item["value"])}</p>\n'
            f"  </div>"
        )
    inner = '<div class="funnel">\n' + "\n".join(stages) + "\n</div>"
    return wrap_html(inner, CSS)
