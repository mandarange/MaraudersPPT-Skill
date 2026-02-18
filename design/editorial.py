"""Editorial design elements - paratextual system for slide HTML.

These elements add consulting-firm / editorial magazine quality details
that distinguish professional presentations from AI-generated templates.
Elements are injected as absolutely positioned HTML overlays.
"""

from __future__ import annotations

from html import escape


_FOLIO_STYLES = {"number_only", "of_total", "padded", "dash"}
_LABEL_TYPES = {
    "exhibit": "Exhibit",
    "figure": "Figure",
    "table": "Table",
    "chart": "Chart",
}
_CAPTION_ALIGN = {"left", "center", "right"}


def _css_var(
    name: str,
    fallback: str,
    theme_vars: dict[str, str] | None = None,
) -> str:
    if theme_vars and name in theme_vars:
        value = str(theme_vars[name]).strip()
        if value:
            return value
    return f"var(--{name},{fallback})"


def running_header(
    section_name: str,
    theme_vars: dict[str, str] | None = None,
) -> str:
    """Generate running header HTML - top-left, 9pt, muted color."""
    section = escape(section_name.strip().upper())
    muted_color = _css_var("color-text-muted", "#888888", theme_vars)
    return (
        '<div class="editorial-running-header" '
        "style=\"position:absolute;left:100px;top:40px;font-size:9px;"
        f"color:{muted_color};font-weight:500;letter-spacing:0.5px;"
        "text-transform:uppercase;opacity:0.6;z-index:20;\">"
        f"{section}</div>"
    )


def folio(
    slide_number: int,
    total_slides: int | None = None,
    style: str = "number_only",
) -> str:
    """Generate folio (page number) HTML - bottom-right."""
    if style not in _FOLIO_STYLES:
        allowed = ", ".join(sorted(_FOLIO_STYLES))
        raise ValueError(f"Unknown folio style '{style}'. Expected one of: {allowed}")

    if style == "number_only":
        text = str(slide_number)
    elif style == "of_total":
        text = str(slide_number) if total_slides is None else f"{slide_number} / {total_slides}"
    elif style == "padded":
        width = 2 if total_slides is None else max(2, len(str(total_slides)))
        text = f"{slide_number:0{width}d}"
    else:
        text = f"&mdash; {slide_number} &mdash;"

    return (
        '<div class="editorial-folio" '
        "style=\"position:absolute;right:100px;bottom:40px;font-size:10px;"
        "color:var(--color-text-muted,#888888);font-weight:500;"
        "letter-spacing:0.3px;opacity:0.7;z-index:20;\">"
        f"{text}</div>"
    )


def source_citation(source_text: str) -> str:
    """Generate source citation HTML - bottom-left, 8pt."""
    source = escape(source_text.strip())
    if source.lower().startswith("source:"):
        label = source
    else:
        label = f"Source: {source}"
    return (
        '<div class="editorial-source" '
        "style=\"position:absolute;left:100px;bottom:40px;font-size:8px;"
        "color:var(--color-text-muted,#888888);font-weight:400;line-height:1.3;"
        "letter-spacing:0.2px;opacity:0.75;max-width:1280px;z-index:20;\">"
        f"{label}</div>"
    )


def exhibit_label(label_type: str, number: int, title: str | None = None) -> str:
    """Generate exhibit/figure label HTML."""
    normalized_type = label_type.strip().lower()
    if normalized_type not in _LABEL_TYPES:
        allowed = ", ".join(sorted(_LABEL_TYPES))
        raise ValueError(
            f"Unknown exhibit label type '{label_type}'. Expected one of: {allowed}"
        )

    base = f"{_LABEL_TYPES[normalized_type]} {number}"
    if title is not None and title.strip():
        base = f"{base}: {escape(title.strip())}"

    return (
        '<span class="editorial-exhibit-label" '
        "style=\"display:inline-block;font-size:11px;"
        "color:var(--color-text-secondary,#555555);font-weight:600;"
        "letter-spacing:0.4px;text-transform:none;\">"
        f"{base}</span>"
    )


def thin_divider(
    width: str = "100%",
    margin_top: int = 16,
    margin_bottom: int = 24,
) -> str:
    """Generate thin horizontal divider line HTML - 1px, muted color."""
    return (
        '<div class="editorial-divider" '
        f"style=\"width:{escape(width)};height:1px;"
        "background:var(--color-divider,#E0E0E0);"
        f"margin:{margin_top}px 0 {margin_bottom}px 0;\"></div>"
    )


def caption(text: str, align: str = "left") -> str:
    """Generate caption HTML for images/charts - 12pt, muted."""
    normalized_align = align.strip().lower()
    if normalized_align not in _CAPTION_ALIGN:
        allowed = ", ".join(sorted(_CAPTION_ALIGN))
        raise ValueError(
            f"Unknown caption alignment '{align}'. Expected one of: {allowed}"
        )

    return (
        '<p class="editorial-caption" '
        "style=\"font-size:12px;color:var(--color-text-muted,#888888);"
        "line-height:1.4;margin:8px 0 0 0;"
        f"text-align:{normalized_align};\">{escape(text)}</p>"
    )


def confidential_footer(text: str = "CONFIDENTIAL") -> str:
    """Generate confidentiality marker - bottom-center, very subtle."""
    return (
        '<div class="editorial-confidential" '
        "style=\"position:absolute;left:50%;bottom:20px;"
        "transform:translateX(-50%);font-size:8px;"
        "color:var(--color-text-muted,#888888);font-weight:600;"
        "letter-spacing:1px;opacity:0.4;text-transform:uppercase;z-index:20;\">"
        f"{escape(text.strip())}</div>"
    )


def inject_editorial_elements(
    slide_html: str,
    section_name: str | None = None,
    slide_number: int | None = None,
    total_slides: int | None = None,
    source: str | None = None,
    folio_style: str = "number_only",
) -> str:
    """Inject all applicable editorial elements into slide HTML."""
    overlays: list[str] = []

    if section_name is not None and section_name.strip():
        overlays.append(running_header(section_name))

    if slide_number is not None:
        overlays.append(folio(slide_number, total_slides=total_slides, style=folio_style))

    if source is not None and source.strip():
        overlays.append(source_citation(source))

    overlays_html = "".join(overlays)
    return (
        '<div class="editorial-frame" '
        "style=\"position:relative;width:100%;height:100%;\">"
        f"{slide_html}{overlays_html}</div>"
    )
