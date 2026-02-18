"""Process Flow — Step-based pipeline/procedure.

data = [
    {"step": "01", "label": "Input"},
    {"step": "02", "label": "Parse"},
    {"step": "03", "label": "Map", "active": True},
    {"step": "04", "label": "Generate"},
]
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.process-flow {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.flow-step {
  width: 200px;
  min-height: 140px;
  border: 1px solid var(--color-border, #E0E0E0);
  border-radius: 2px;
  background: var(--color-bg, #FFFFFF);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  position: relative;
}

.flow-step-no {
  margin: 0;
  font-size: 16px;
  line-height: 20px;
  color: var(--color-text-muted, #888888);
  font-weight: 700;
}

.flow-step-label {
  margin: 12px 0 0 0;
  font-size: 20px;
  line-height: 26px;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  text-align: center;
  letter-spacing: -0.2px;
}

.flow-arrow {
  margin: 0;
  font-size: 20px;
  line-height: 20px;
  color: var(--color-text-muted, #CCCCCC);
  flex-shrink: 0;
}

.flow-step-active {
  background: var(--color-text, #1A1A1A);
  border-color: var(--color-text, #1A1A1A);
}

.flow-step-active .flow-step-no {
  color: rgba(255, 255, 255, 0.5);
}

.flow-step-active .flow-step-label {
  color: #FFFFFF;
}

/* 6+ steps compact */
.process-flow.compact .flow-step {
  width: 140px;
  min-height: 110px;
  padding: 14px 8px;
}

.process-flow.compact .flow-step-label {
  font-size: 18px;
  line-height: 24px;
}

.process-flow.compact .flow-arrow {
  font-size: 16px;
}

/* 8+ steps two-row */
.process-flow.two-row {
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px 8px;
}"""

CSS = full_css(_CSS)


def render(data: list[dict[str, Any]]) -> str:
    """Process flow HTML. 3-8 steps recommended."""
    n = len(data)
    extra_cls = ""
    if n >= 8:
        extra_cls = " two-row compact"
    elif n >= 6:
        extra_cls = " compact"

    parts = []
    for i, item in enumerate(data):
        step_cls = "flow-step flow-step-active" if item.get("active") else "flow-step"
        parts.append(
            f'  <div class="{step_cls}">\n'
            f'    <p class="flow-step-no">{esc(item["step"])}</p>\n'
            f'    <p class="flow-step-label">{esc(item["label"])}</p>\n'
            f"  </div>"
        )
        if i < n - 1:
            parts.append('  <p class="flow-arrow">\u2192</p>')

    inner = f'<div class="process-flow{extra_cls}">\n' + "\n".join(parts) + "\n</div>"
    return wrap_html(inner, CSS)
