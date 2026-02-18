from __future__ import annotations

from .base import esc

_ANNOTATION_CSS = """\
.chart-insight {
  position: absolute;
  bottom: 12px;
  left: 0;
  right: 0;
  padding: 0 16px;
  font-size: 16px;
  line-height: 22px;
  color: var(--color-text-secondary, #555555);
  font-weight: 500;
  text-align: left;
}

.chart-callout {
  position: absolute;
  padding: 8px 16px;
  font-size: 14px;
  line-height: 20px;
  color: var(--color-text, #1A1A1A);
  font-weight: 600;
  border-left: 2px solid var(--color-accent, #D94F4F);
  background: var(--color-surface, #F7F7F7);
  max-width: 320px;
}

.chart-callout-top-right {
  top: 8px;
  right: 8px;
}

.chart-callout-top-left {
  top: 8px;
  left: 8px;
}

.chart-callout-bottom-right {
  bottom: 40px;
  right: 8px;
}

.chart-callout-bottom-left {
  bottom: 40px;
  left: 8px;
}

.chart-emphasis-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background: var(--color-accent, #D94F4F);
  margin-right: 8px;
  vertical-align: middle;
}
"""

_POSITIONS = {"top-right", "top-left", "bottom-right", "bottom-left"}


def annotation_css() -> str:
    return _ANNOTATION_CSS


def insight_caption(text: str) -> str:
    return f'<div class="chart-insight">{esc(text)}</div>'


def callout(text: str, position: str = "top-right") -> str:
    if position not in _POSITIONS:
        position = "top-right"
    cls = f"chart-callout chart-callout-{position}"
    return (
        f'<div class="{cls}">'
        f'<span class="chart-emphasis-dot"></span>'
        f'{esc(text)}'
        f'</div>'
    )


def wrap_with_annotations(
    chart_html: str,
    insight: str | None = None,
    callout_text: str | None = None,
    callout_position: str = "top-right",
) -> str:
    if not insight and not callout_text:
        return chart_html

    parts = [chart_html]
    css_injection = f"<style>\n{_ANNOTATION_CSS}</style>\n"

    if "</style>" in chart_html:
        parts = [chart_html.replace("</style>", f"{_ANNOTATION_CSS}</style>", 1)]
    else:
        parts = [css_injection + chart_html]

    annotations: list[str] = []
    if callout_text:
        annotations.append(callout(callout_text, callout_position))
    if insight:
        annotations.append(insight_caption(insight))

    if '</div>\n</div>' in parts[0]:
        injection_point = parts[0].rfind('</div>')
        return parts[0][:injection_point] + "\n".join(annotations) + "\n" + parts[0][injection_point:]

    return parts[0] + "\n".join(annotations)
