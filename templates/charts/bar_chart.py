"""Horizontal Bar Chart — numeric comparison between items.

data = [
    {"label": "Q1", "value": 95, "display": "95%", "max": True},
    {"label": "Q2", "value": 78, "display": "78%"},
    {"label": "Q3", "value": 88, "display": "88%", "accent": True},
]
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.bar-chart-h {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  justify-content: center;
  padding: 16px 0;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.bar-label {
  width: 200px;
  margin: 0;
  font-size: 18px;
  line-height: 24px;
  color: var(--color-text-secondary, #555555);
  font-weight: 500;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 40px;
  background: var(--color-surface-alt, #F2F2F2);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 40px;
  background: var(--bar-fill-color, #D0D0D0);
  border-radius: 2px;
}

.bar-fill.is-max {
  background: var(--bar-fill-max-color, #1A1A1A);
}

.bar-fill.is-accent {
  background: var(--color-accent, #D94F4F);
}

.bar-value {
  width: 80px;
  margin: 0;
  text-align: right;
  font-size: 18px;
  line-height: 24px;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}"""

CSS = full_css(_CSS)


def render(data: list[dict[str, Any]]) -> str:
    """Generate bar chart HTML.

    Each item's value is 0-100 (percentage scale).
    max=True highlights the maximum, accent=True applies red accent.
    """
    max_val = max((d["value"] for d in data), default=100)
    rows = []
    for item in data:
        pct = (item["value"] / max_val * 100) if max_val else 0
        if item.get("max"):
            fill_cls = "bar-fill is-max"
        elif item.get("accent"):
            fill_cls = "bar-fill is-accent"
        else:
            fill_cls = "bar-fill"
        rows.append(
            f'  <div class="bar-row">\n'
            f'    <p class="bar-label">{esc(item["label"])}</p>\n'
            f'    <div class="bar-track">'
            f'<div class="{fill_cls}" style="width:{pct:.0f}%;"></div>'
            f"</div>\n"
            f'    <p class="bar-value">{esc(item["display"])}</p>\n'
            f"  </div>"
        )
    inner = f'<div class="bar-chart-h">\n' + "\n".join(rows) + "\n</div>"
    return wrap_html(inner, CSS)
