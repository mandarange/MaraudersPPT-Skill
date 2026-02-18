"""KPI Cards — grid comparing 1-4 key performance indicators.

data = [
    {"label": "Success Rate", "value": "95%", "delta": "▲ +4%", "accent": True},
    {"label": "Accuracy", "value": "100%"},
    {"label": "Avg Processing", "value": "2m", "delta": "▼ -18%"},
]
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 32px;
  width: 100%;
  height: 100%;
  align-content: center;
}

.kpi-card {
  border: 1px solid var(--color-border, #E0E0E0);
  border-radius: 2px;
  padding: 40px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--color-bg, #FFFFFF);
}

.kpi-card.is-accent {
  border-left: 4px solid var(--kpi-accent-color, #D94F4F);
}

.kpi-label {
  margin: 0 0 20px 0;
  font-size: 16px;
  line-height: 22px;
  color: var(--color-text-secondary, #555555);
  font-weight: 600;
}

.kpi-value {
  margin: 0;
  font-size: 56px;
  line-height: 1.1;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
}

.kpi-delta {
  margin: 20px 0 0 0;
  font-size: 16px;
  line-height: 22px;
  color: var(--color-text-muted, #888888);
  font-weight: 500;
}"""

CSS = full_css(_CSS)


def render(data: list[dict[str, Any]]) -> str:
    """Generate KPI card HTML. Up to 4 cards recommended."""
    cards = []
    for item in data:
        cls = "kpi-card is-accent" if item.get("accent") else "kpi-card"
        delta = esc(item.get("delta", "—"))
        cards.append(
            f'  <div class="{cls}">\n'
            f'    <p class="kpi-label">{esc(item["label"])}</p>\n'
            f'    <p class="kpi-value">{esc(item["value"])}</p>\n'
            f'    <p class="kpi-delta">{delta}</p>\n'
            f"  </div>"
        )
    inner = f'<div class="kpi-grid">\n' + "\n".join(cards) + "\n</div>"
    return wrap_html(inner, CSS)
