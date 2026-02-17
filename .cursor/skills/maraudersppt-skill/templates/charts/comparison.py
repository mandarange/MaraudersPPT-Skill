"""Comparison — Two-axis contrast (Before/After, Legacy/Improved).

data = {
    "left":  {"title": "Legacy Approach", "items": ["Manual cleanup required", "Average 30 min"]},
    "right": {"title": "Skill Automation", "items": ["Auto structure mapping", "Generated in 1-3 min"], "accent": True},
}
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.comparison {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 72px 1fr;
  gap: 16px;
  align-items: stretch;
}

.compare-left,
.compare-right {
  border: 1px solid #E0E0E0;
  border-radius: 2px;
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
}

.compare-left {
  background: #F7F7F7;
}

.compare-right {
  background: #FFFFFF;
}

.compare-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 24px;
  color: #CCCCCC;
  font-weight: 700;
  letter-spacing: 2px;
  position: relative;
}

.compare-divider::before {
  content: "";
  position: absolute;
  left: 35px;
  top: 48px;
  bottom: 48px;
  width: 1px;
  background: #E8E8E8;
}

.compare-title {
  margin: 0 0 24px 0;
  font-size: 24px;
  line-height: 32px;
  color: #1A1A1A;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.compare-title.is-accent {
  color: #D94F4F;
}

.compare-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.compare-list li {
  margin: 0 0 16px 0;
  padding-left: 20px;
  font-size: 18px;
  line-height: 28px;
  color: #555555;
  position: relative;
}

.compare-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 11px;
  width: 6px;
  height: 6px;
  border-radius: 3px;
  background: #CCCCCC;
}

.compare-right .compare-list li::before {
  background: #D94F4F;
}"""

CSS = full_css(_CSS)


def _side_html(side: dict[str, Any], cls: str) -> str:
    title_cls = "compare-title is-accent" if side.get("accent") else "compare-title"
    items = "\n".join(f"      <li>{esc(t)}</li>" for t in side.get("items", []))
    return (
        f'  <div class="{cls}">\n'
        f'    <p class="{title_cls}">{esc(side["title"])}</p>\n'
        f'    <ul class="compare-list">\n{items}\n    </ul>\n'
        f"  </div>"
    )


def render(data: dict[str, Any]) -> str:
    """Comparison slide HTML. 3-5 bullets per side recommended."""
    left = _side_html(data["left"], "compare-left")
    right = _side_html(data["right"], "compare-right")
    inner = (
        '<div class="comparison">\n'
        f"{left}\n"
        '  <div class="compare-divider">VS</div>\n'
        f"{right}\n"
        "</div>"
    )
    return wrap_html(inner, CSS)
