"""Chart template dispatcher.

Usage:
    from templates.charts import render_chart

    html = render_chart("kpi_cards", [
        {"label": "Success Rate", "value": "95%", "delta": "▲ +4%", "accent": True},
        {"label": "Accuracy", "value": "100%"},
    ])

Supported types: kpi_cards, bar_chart, donut_chart, process_flow,
                 timeline, comparison, icon_grid, funnel
"""

from . import (
    kpi_cards,
    bar_chart,
    donut_chart,
    process_flow,
    timeline,
    comparison,
    icon_grid,
    funnel,
)
from .annotations import wrap_with_annotations, insight_caption, callout
from .base import wrap_capture_html as _wrap_capture_html, capture_css

_REGISTRY = {
    "kpi_cards": kpi_cards,
    "bar_chart": bar_chart,
    "donut_chart": donut_chart,
    "process_flow": process_flow,
    "timeline": timeline,
    "comparison": comparison,
    "icon_grid": icon_grid,
    "funnel": funnel,
}


def render_chart(chart_type: str, data) -> str:
    """Return complete slide HTML for the given chart_type and data.

    Args:
        chart_type: Chart kind (kpi_cards, bar_chart, ...)
        data: See each chart module's docstring for schema

    Returns:
        Complete HTML string containing <style> + <div class="content">

    Raises:
        KeyError: Unsupported chart_type
    """
    module = _REGISTRY[chart_type]
    return module.render(data)


def get_css(chart_type: str) -> str:
    """Return full CSS (common + chart-specific) for the chart_type."""
    return _REGISTRY[chart_type].CSS


def list_types() -> list[str]:
    """List available chart types."""
    return list(_REGISTRY.keys())


def render_chart_page(
    chart_type: str,
    data,
    width: int = 1720,
    height: int = 760,
) -> str:
    """Return a complete HTML page for Playwright .capture-root screenshot."""
    module = _REGISTRY[chart_type]
    raw_css = module._CSS  # noqa: SLF001
    inner = module.render(data)

    # Extract body from wrap_html's '<style>…</style>\n<div class="content">…</div>'
    start_tag = '<div class="content">\n'
    end_tag = "\n</div>"
    start_idx = inner.find(start_tag)
    if start_idx == -1:
        fragment = inner
    else:
        content_start = start_idx + len(start_tag)
        content_end = inner.rfind(end_tag)
        fragment = (
            inner[content_start:content_end] if content_end > content_start else inner
        )

    return _wrap_capture_html(fragment, raw_css, width, height)
