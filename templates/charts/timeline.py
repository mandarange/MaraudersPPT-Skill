"""Timeline — Release roadmap/milestones.

data = [
    {"date": "2025 Q1", "event": "MVP Launch", "accent": True},
    {"date": "2025 Q2", "event": "Chart Support"},
    {"date": "2025 Q3", "event": "AI Automation"},
]
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.timeline {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 80px;
}

.timeline-line {
  position: absolute;
  left: 80px;
  right: 80px;
  top: 380px;
  height: 2px;
  background: var(--color-border, #E8E8E8);
}

.timeline-item {
  width: 280px;
  position: relative;
  text-align: center;
  z-index: 1;
}

.timeline-item-top {
  padding-bottom: 190px;
}

.timeline-item-bottom {
  padding-top: 190px;
}

.timeline-dot {
  position: absolute;
  left: 130px;
  top: 370px;
  width: 20px;
  height: 20px;
  border-radius: 10px;
  background: var(--color-text, #1A1A1A);
  border: 4px solid var(--color-bg, #FFFFFF);
  box-sizing: border-box;
}

.timeline-dot.is-accent {
  background: var(--color-accent, #D94F4F);
}

.timeline-date {
  margin: 0;
  font-size: 16px;
  line-height: 22px;
  color: var(--color-text-secondary, #555555);
  font-weight: 600;
}

.timeline-event {
  margin: 10px 0 0 0;
  font-size: 18px;
  line-height: 26px;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  letter-spacing: -0.2px;
}"""

CSS = full_css(_CSS)


def render(data: list[dict[str, Any]]) -> str:
    """Timeline HTML. Items are placed alternating top/bottom."""
    items = []
    for i, item in enumerate(data):
        pos = "timeline-item-top" if i % 2 == 0 else "timeline-item-bottom"
        dot_cls = "timeline-dot is-accent" if item.get("accent") else "timeline-dot"
        items.append(
            f'  <div class="timeline-item {pos}">\n'
            f'    <span class="{dot_cls}"></span>\n'
            f'    <p class="timeline-date">{esc(item["date"])}</p>\n'
            f'    <p class="timeline-event">{esc(item["event"])}</p>\n'
            f"  </div>"
        )
    inner = (
        '<div class="timeline">\n'
        '  <div class="timeline-line"></div>\n' + "\n".join(items) + "\n</div>"
    )
    return wrap_html(inner, CSS)
