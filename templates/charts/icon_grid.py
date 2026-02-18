"""Icon Grid — Non-numeric item classification (roles, features, categories).

data = {
    "layout": "2x2",   # "2x2" | "2x3" | "3x2"
    "items": [
        {"icon": "👩‍💻", "title": "Dev Lead", "desc": "Manages code standards and deployment stability"},
        {"icon": "🧭",  "title": "Planner",  "desc": "Organizes requirements and sets priorities"},
        {"icon": "🏢",  "title": "CTO / VP", "desc": "Reviews performance metrics and org alignment"},
        {"icon": "🤖",  "title": "AI User",  "desc": "Runs automated recurring reports"},
    ],
}
"""

from typing import Any

from .base import full_css, esc, wrap_html

_CSS = """\
.icon-grid {
  width: 100%;
  height: 100%;
  display: grid;
  gap: 24px;
}

.icon-grid.cols-2x2 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
}

.icon-grid.cols-2x3 {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
}

.icon-grid.cols-3x2 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, 1fr);
}

.icon-cell {
  border: 1px solid var(--color-border, #E0E0E0);
  border-radius: 2px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--color-bg, #FFFFFF);
}

.icon-emoji {
  margin: 0;
  font-size: 36px;
  line-height: 40px;
}

.icon-title {
  margin: 16px 0 0 0;
  font-size: 18px;
  line-height: 24px;
  color: var(--color-text, #1A1A1A);
  font-weight: 700;
  letter-spacing: -0.2px;
}

.icon-desc {
  margin: 8px 0 0 0;
  font-size: 16px;
  line-height: 24px;
  color: var(--color-text-secondary, #555555);
}"""

CSS = full_css(_CSS)

_LAYOUT_MAP = {"2x2": "cols-2x2", "2x3": "cols-2x3", "3x2": "cols-3x2"}


def render(data: dict[str, Any]) -> str:
    """Icon grid HTML. Layout is selected based on item count."""
    layout = data.get("layout", "2x2")
    grid_cls = _LAYOUT_MAP.get(layout, "cols-2x2")

    cells = []
    for item in data.get("items", []):
        cells.append(
            f'  <div class="icon-cell">\n'
            f'    <p class="icon-emoji">{item["icon"]}</p>\n'
            f'    <p class="icon-title">{esc(item["title"])}</p>\n'
            f'    <p class="icon-desc">{esc(item["desc"])}</p>\n'
            f"  </div>"
        )
    inner = f'<div class="icon-grid {grid_cls}">\n' + "\n".join(cells) + "\n</div>"
    return wrap_html(inner, CSS)
