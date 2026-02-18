"""Donut Chart — Proportion/share visualization.

data = {
    "segments": [
        {"label": "APAC", "value": 42, "color": "#1A1A1A"},
        {"label": "EMEA", "value": 31, "color": "#555555"},
        {"label": "Americas", "value": 27, "color": "#D94F4F"},
    ],
    "center": {"value": "42%", "label": "APAC"},
}
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.donut-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 96px;
}

.donut-wrap {
  width: 380px;
  height: 380px;
  border-radius: 190px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  mask: radial-gradient(transparent 62%, black 63%);
  -webkit-mask: radial-gradient(transparent 62%, black 63%);
}

.donut-core {
  width: 240px;
  height: 240px;
  border-radius: 120px;
  background: var(--color-bg, #FFFFFF);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: absolute;
}

.donut-value {
  margin: 0;
  font-size: 52px;
  line-height: 1.1;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
}

.donut-label {
  margin: 8px 0 0 0;
  font-size: 16px;
  line-height: 22px;
  color: var(--color-text-secondary, #555555);
  font-weight: 500;
}

.donut-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 18px;
  line-height: 26px;
  color: var(--color-text-secondary, #555555);
}

.legend-dot {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  display: inline-block;
  flex-shrink: 0;
}"""

CSS = full_css(_CSS)


def _conic_gradient(segments: list[dict[str, Any]]) -> str:
    """Segment list → conic-gradient CSS value."""
    total = sum(s["value"] for s in segments)
    if total == 0:
        return "conic-gradient(#E0E0E0 0deg 360deg)"
    parts = []
    cur = 0.0
    for seg in segments:
        end = cur + (seg["value"] / total) * 360
        parts.append(f"{seg['color']} {cur:.1f}deg {end:.1f}deg")
        cur = end
    return f"conic-gradient({', '.join(parts)})"


def render(data: dict[str, Any]) -> str:
    """Generate donut chart HTML. Max 5 segments."""
    segments = data["segments"]
    center = data.get("center", {})
    gradient = _conic_gradient(segments)

    legend_items = []
    total = sum(s["value"] for s in segments)
    for seg in segments:
        pct = f"{seg['value'] / total * 100:.0f}%" if total else "0%"
        legend_items.append(
            f'    <li class="legend-item">'
            f'<span class="legend-dot" style="background:{seg["color"]};"></span>'
            f"{esc(seg['label'])} {pct}</li>"
        )

    inner = (
        f'<div class="donut-chart">\n'
        f'  <div class="donut-wrap" style="background:{gradient};">\n'
        f'    <div class="donut-core">\n'
        f'      <p class="donut-value">{esc(center.get("value", ""))}</p>\n'
        f'      <p class="donut-label">{esc(center.get("label", ""))}</p>\n'
        f"    </div>\n"
        f"  </div>\n"
        f'  <ul class="donut-legend">\n' + "\n".join(legend_items) + "\n  </ul>\n</div>"
    )
    return wrap_html(inner, CSS)
