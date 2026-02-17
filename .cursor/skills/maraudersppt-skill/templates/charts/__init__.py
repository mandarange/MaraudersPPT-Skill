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
