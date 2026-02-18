"""Static design lint - pre-render quality checks.

Checks slide HTML strings for common design anti-patterns,
accessibility issues, and editorial quality. No browser needed.

Two modes:
1. lint_slide(html) -> list of LintIssue (individual slide)
2. lint_deck(slides) -> list of LintIssue (cross-slide rhythm)
3. human_likeness_score(slides) -> float 0.0-1.0 (H1-H5 scoring)
"""

from __future__ import annotations

from dataclasses import dataclass
import colorsys
import re
from typing import Literal

Severity = Literal["error", "warning", "info"]

CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
SAFE_LEFT = 100
SAFE_TOP = 220
SAFE_RIGHT = 100
SAFE_BOTTOM = 100

_SEVERITY_ORDER: dict[Severity, int] = {
    "error": 0,
    "warning": 1,
    "info": 2,
}

_TAG_RE = re.compile(r"<(?P<tag>[a-zA-Z][\w:-]*)(?P<attrs>[^>]*)>", re.IGNORECASE)
_STYLE_ATTR_RE = re.compile(r"style\s*=\s*([\"'])(?P<style>.*?)\1", re.IGNORECASE | re.DOTALL)
_CLASS_ATTR_RE = re.compile(r"class\s*=\s*([\"'])(?P<class>.*?)\1", re.IGNORECASE | re.DOTALL)
_STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(?P<css>.*?)</style>", re.IGNORECASE | re.DOTALL)
_FONT_SIZE_RE = re.compile(r"font-size\s*:\s*(?P<value>[0-9]+(?:\.[0-9]+)?)px", re.IGNORECASE)
_COLOR_HEX_RE = re.compile(r"#(?P<hex>[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
_COLOR_RGB_RE = re.compile(
    r"rgba?\(\s*(?P<r>\d{1,3})\s*,\s*(?P<g>\d{1,3})\s*,\s*(?P<b>\d{1,3})(?:\s*,\s*(?P<a>[0-9]*\.?[0-9]+))?\s*\)",
    re.IGNORECASE,
)
_STRIP_TAGS_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

_EDITORIAL_FONT_MINIMUMS = {
    "editorial-running-header": 9.0,
    "editorial-folio": 10.0,
    "editorial-source": 8.0,
    "editorial-exhibit-label": 11.0,
    "editorial-caption": 12.0,
    "editorial-confidential": 8.0,
}


@dataclass
class LintIssue:
    rule_id: str
    severity: Severity
    message: str
    slide_index: int | None = None
    suggestion: str | None = None


def _normalize_text(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def _strip_tags(text: str) -> str:
    return _normalize_text(_STRIP_TAGS_RE.sub(" ", text))


def _iter_styled_elements(html: str) -> list[dict[str, str]]:
    elements: list[dict[str, str]] = []
    for match in _TAG_RE.finditer(html):
        attrs = match.group("attrs") or ""
        style_match = _STYLE_ATTR_RE.search(attrs)
        if not style_match:
            continue

        class_match = _CLASS_ATTR_RE.search(attrs)
        classes = ""
        if class_match:
            classes = class_match.group("class")

        elements.append(
            {
                "tag": match.group("tag").lower(),
                "attrs": attrs,
                "style": style_match.group("style"),
                "classes": classes.lower(),
            }
        )
    return elements


def _style_to_dict(style: str) -> dict[str, str]:
    style_map: dict[str, str] = {}
    for declaration in style.split(";"):
        if ":" not in declaration:
            continue
        name, value = declaration.split(":", 1)
        style_name = name.strip().lower()
        style_value = value.strip()
        if style_name:
            style_map[style_name] = style_value
    return style_map


def _parse_px(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"(-?[0-9]+(?:\.[0-9]+)?)px", value, re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def _collect_style_chunks(html: str) -> list[str]:
    chunks: list[str] = []
    for element in _iter_styled_elements(html):
        chunks.append(element["style"])
    for match in _STYLE_BLOCK_RE.finditer(html):
        chunks.append(match.group("css"))
    return chunks


def _font_sizes_in_style(style: str) -> list[float]:
    return [float(match.group("value")) for match in _FONT_SIZE_RE.finditer(style)]


def _collect_font_sizes(html: str) -> list[float]:
    sizes: list[float] = []
    for chunk in _collect_style_chunks(html):
        sizes.extend(_font_sizes_in_style(chunk))
    return sizes


def _is_editorial(classes: str) -> bool:
    return "editorial-" in classes


def _make_issue(
    rule_id: str,
    severity: Severity,
    message: str,
    slide_index: int,
    suggestion: str | None = None,
) -> LintIssue:
    return LintIssue(
        rule_id=rule_id,
        severity=severity,
        message=message,
        slide_index=slide_index,
        suggestion=suggestion,
    )


def _sort_issues(issues: list[LintIssue]) -> list[LintIssue]:
    return sorted(
        issues,
        key=lambda issue: (
            _SEVERITY_ORDER[issue.severity],
            -1 if issue.slide_index is None else issue.slide_index,
            issue.rule_id,
            issue.message,
        ),
    )


def _html_contains_any(html: str, patterns: list[str]) -> bool:
    lowered = html.lower()
    for pattern in patterns:
        if pattern in lowered:
            return True
    return False


def _hue_bucket(rgb: tuple[int, int, int]) -> int | None:
    red, green, blue = rgb
    hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
    if saturation < 0.18 or value < 0.2:
        return None
    return int(hue * 12)


def _extract_rgb_colors(html: str) -> list[tuple[int, int, int]]:
    colors: list[tuple[int, int, int]] = []
    for match in _COLOR_HEX_RE.finditer(html):
        raw = match.group("hex")
        if len(raw) == 3:
            red = int(raw[0] * 2, 16)
            green = int(raw[1] * 2, 16)
            blue = int(raw[2] * 2, 16)
        else:
            red = int(raw[0:2], 16)
            green = int(raw[2:4], 16)
            blue = int(raw[4:6], 16)
        colors.append((red, green, blue))

    for match in _COLOR_RGB_RE.finditer(html):
        alpha_text = match.group("a")
        if alpha_text is not None and float(alpha_text) <= 0:
            continue
        red = max(0, min(255, int(match.group("r"))))
        green = max(0, min(255, int(match.group("g"))))
        blue = max(0, min(255, int(match.group("b"))))
        colors.append((red, green, blue))
    return colors


def _saturated_hue_buckets(html: str) -> set[int]:
    buckets: set[int] = set()
    for rgb in _extract_rgb_colors(html):
        bucket = _hue_bucket(rgb)
        if bucket is None:
            continue
        buckets.add(bucket)
    return buckets


def _dominant_element(html: str) -> str:
    counts = {
        "image": len(re.findall(r"<img\b", html, re.IGNORECASE)),
        "chart": len(
            re.findall(r"<svg\b|<canvas\b|class\s*=\s*[\"'][^\"']*chart", html, re.IGNORECASE)
        ),
        "table": len(re.findall(r"<table\b", html, re.IGNORECASE)),
        "list": len(re.findall(r"<ul\b|<ol\b", html, re.IGNORECASE)),
        "text": max(1, len(_strip_tags(html).split()) // 40),
    }
    return max(counts, key=lambda key: counts[key])


def _infer_column_count(html: str) -> int:
    grid_matches: list[str] = re.findall(
        r"grid-template-columns\s*:\s*([^;\"'}]+)", html, re.IGNORECASE
    )
    if grid_matches:
        raw = str(grid_matches[-1])
        repeat_match = re.search(r"repeat\s*\(\s*(\d+)", raw, re.IGNORECASE)
        if repeat_match:
            return max(1, int(repeat_match.group(1)))
        parts = [part for part in raw.split() if part.strip()]
        if parts:
            return len(parts)

    if re.search(r"display\s*:\s*flex", html, re.IGNORECASE):
        if re.search(r"flex-direction\s*:\s*column", html, re.IGNORECASE):
            return 1
        if re.search(r"justify-content\s*:\s*space-between", html, re.IGNORECASE):
            return 2
    return 1


def _infer_image_zone(html: str) -> str:
    image_match = re.search(
        r"<img\b[^>]*style\s*=\s*([\"'])(?P<style>.*?)\1",
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not image_match:
        if re.search(r"<img\b", html, re.IGNORECASE):
            return "present"
        return "none"

    style_map = _style_to_dict(image_match.group("style"))
    left = _parse_px(style_map.get("left"))
    right = _parse_px(style_map.get("right"))
    top = _parse_px(style_map.get("top"))
    if left is not None:
        return "left" if left < CANVAS_WIDTH / 2 else "right"
    if right is not None:
        return "right"
    if top is not None and top < 300:
        return "top"
    return "center"


def _text_length_bucket(html: str) -> str:
    words = len(_strip_tags(html).split())
    if words < 80:
        return "short"
    if words < 180:
        return "medium"
    return "long"


def _layout_signature(html: str) -> str:
    return f"cols{_infer_column_count(html)}-{_infer_image_zone(html)}-{_text_length_bucket(html)}"


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def check_overflow(html: str, slide_idx: int) -> list[LintIssue]:
    """Check for potential content overflow.
    - Font size * approximate char count vs container width
    - Nested elements that might escape safe area
    """
    issues: list[LintIssue] = []
    for element in _iter_styled_elements(html):
        style_map = _style_to_dict(element["style"])
        width = _parse_px(style_map.get("width"))
        height = _parse_px(style_map.get("height"))
        left = _parse_px(style_map.get("left"))
        top = _parse_px(style_map.get("top"))

        if width is not None and width > CANVAS_WIDTH:
            issues.append(
                _make_issue(
                    "EQ1_OVERFLOW_WIDTH",
                    "error",
                    f"Element width {width:.0f}px exceeds canvas width {CANVAS_WIDTH}px.",
                    slide_idx,
                    "Reduce width or align content to the canvas safe area.",
                )
            )

        if height is not None and height > CANVAS_HEIGHT:
            issues.append(
                _make_issue(
                    "EQ1_OVERFLOW_HEIGHT",
                    "error",
                    f"Element height {height:.0f}px exceeds canvas height {CANVAS_HEIGHT}px.",
                    slide_idx,
                    "Reduce height, split content, or shorten copy.",
                )
            )

        if left is not None and width is not None and left + width > CANVAS_WIDTH:
            issues.append(
                _make_issue(
                    "EQ1_OVERFLOW_X",
                    "warning",
                    "Absolutely positioned element may overflow horizontally.",
                    slide_idx,
                    "Reduce width or move the element inside the content frame.",
                )
            )

        if top is not None and height is not None and top + height > CANVAS_HEIGHT:
            issues.append(
                _make_issue(
                    "EQ1_OVERFLOW_Y",
                    "warning",
                    "Absolutely positioned element may overflow vertically.",
                    slide_idx,
                    "Reduce content volume or move element upward.",
                )
            )

        font_size = _parse_px(style_map.get("font-size"))
        if (
            font_size is not None
            and width is not None
            and "nowrap" in style_map.get("white-space", "").lower()
        ):
            chars_per_line = max(1.0, width / max(1.0, font_size * 0.55))
            if chars_per_line < 12:
                issues.append(
                    _make_issue(
                        "EQ1_OVERFLOW_NOWRAP",
                        "warning",
                        "Narrow nowrap text container may clip content.",
                        slide_idx,
                        "Allow wrapping or increase container width.",
                    )
                )

    return issues


def check_font_minimum(html: str, slide_idx: int) -> list[LintIssue]:
    """Verify all font-size values >= 16px (body), >= 10px (folio/micro).
    Exceptions: editorial elements (folio=10, source=8, exhibit=11, caption=12).
    """
    issues: list[LintIssue] = []
    for element in _iter_styled_elements(html):
        class_names = set(element["classes"].split())
        style = element["style"]
        font_sizes = _font_sizes_in_style(style)
        if not font_sizes:
            continue

        minimum = 16.0
        for class_name, exception_minimum in _EDITORIAL_FONT_MINIMUMS.items():
            if class_name in class_names:
                minimum = exception_minimum
                break

        for font_size in font_sizes:
            if font_size < minimum:
                issues.append(
                    _make_issue(
                        "EQ1_FONT_MINIMUM",
                        "error",
                        f"Font size {font_size:.0f}px is below minimum {minimum:.0f}px.",
                        slide_idx,
                        "Use >=16px for body text, with editorial micro-type exceptions only.",
                    )
                )

    for style_block in _STYLE_BLOCK_RE.finditer(html):
        for match in _FONT_SIZE_RE.finditer(style_block.group("css")):
            font_size = float(match.group("value"))
            if font_size < 8:
                issues.append(
                    _make_issue(
                        "EQ1_FONT_MICRO",
                        "warning",
                        f"CSS font size {font_size:.0f}px is likely unreadable.",
                        slide_idx,
                        "Raise tiny font sizes to at least 8px and prefer 10px+.",
                    )
                )

    return issues


def check_safe_area(html: str, slide_idx: int) -> list[LintIssue]:
    """Check that positioned elements stay within safe margins."""
    issues: list[LintIssue] = []
    for element in _iter_styled_elements(html):
        if _is_editorial(element["classes"]):
            continue

        style_map = _style_to_dict(element["style"])
        position = style_map.get("position", "").lower()
        if position not in {"absolute", "fixed"}:
            continue

        left = _parse_px(style_map.get("left"))
        right = _parse_px(style_map.get("right"))
        top = _parse_px(style_map.get("top"))
        bottom = _parse_px(style_map.get("bottom"))
        width = _parse_px(style_map.get("width"))
        height = _parse_px(style_map.get("height"))

        if left is not None and left < SAFE_LEFT:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_LEFT",
                    "warning",
                    f"Positioned element starts at {left:.0f}px; safe left margin is {SAFE_LEFT}px.",
                    slide_idx,
                    "Move element rightward into the safe area.",
                )
            )

        if top is not None and top < SAFE_TOP:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_TOP",
                    "warning",
                    f"Positioned element starts at {top:.0f}px; safe top margin is {SAFE_TOP}px.",
                    slide_idx,
                    "Move element downward into the content zone.",
                )
            )

        if right is not None and right < SAFE_RIGHT:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_RIGHT",
                    "warning",
                    f"Positioned element right margin {right:.0f}px is below safe margin {SAFE_RIGHT}px.",
                    slide_idx,
                    "Increase right offset to keep content printable.",
                )
            )

        if bottom is not None and bottom < SAFE_BOTTOM:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_BOTTOM",
                    "warning",
                    f"Positioned element bottom margin {bottom:.0f}px is below safe margin {SAFE_BOTTOM}px.",
                    slide_idx,
                    "Increase bottom offset to avoid clipping.",
                )
            )

        if left is not None and width is not None and left + width > CANVAS_WIDTH - SAFE_RIGHT:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_X_BOUNDS",
                    "warning",
                    "Positioned element may exceed right safe boundary.",
                    slide_idx,
                    "Reduce width or move the element leftward.",
                )
            )

        if top is not None and height is not None and top + height > CANVAS_HEIGHT - SAFE_BOTTOM:
            issues.append(
                _make_issue(
                    "EQ1_SAFE_AREA_Y_BOUNDS",
                    "warning",
                    "Positioned element may exceed bottom safe boundary.",
                    slide_idx,
                    "Reduce height or move the element upward.",
                )
            )
    return issues


def check_no_glassmorphism(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect blur(), backdrop-filter, rgba with high alpha on backgrounds."""
    issues: list[LintIssue] = []

    if re.search(r"backdrop-filter\s*:", html, re.IGNORECASE):
        issues.append(
            _make_issue(
                "NO1_GLASS_BACKDROP",
                "warning",
                "backdrop-filter detected (glassmorphism pattern).",
                slide_idx,
                "Remove backdrop blur and use flat surfaces.",
            )
        )

    if re.search(r"filter\s*:[^;]*\bblur\s*\(", html, re.IGNORECASE):
        issues.append(
            _make_issue(
                "NO1_GLASS_BLUR",
                "warning",
                "blur() filter detected (glassmorphism pattern).",
                slide_idx,
                "Use crisp edges without blur effects.",
            )
        )

    background_rgba = re.finditer(
        r"background(?:-color)?\s*:\s*rgba\([^)]*?,\s*(?P<alpha>[0-9]*\.?[0-9]+)\s*\)",
        html,
        re.IGNORECASE,
    )
    for match in background_rgba:
        alpha = float(match.group("alpha"))
        if alpha >= 0.45:
            issues.append(
                _make_issue(
                    "NO1_GLASS_RGBA",
                    "warning",
                    "High-alpha rgba background detected; can resemble translucent glass UI.",
                    slide_idx,
                    "Prefer opaque neutral backgrounds.",
                )
            )
            break

    return issues


def check_no_large_radius(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect border-radius > 4px (except full-circle donut charts)."""
    issues: list[LintIssue] = []
    for match in re.finditer(r"border-radius\s*:\s*(?P<value>[^;\"'}]+)", html, re.IGNORECASE):
        value = match.group("value").strip()
        context = html[max(0, match.start() - 100) : match.end() + 100].lower()
        if "donut" in context or "pie" in context or "circle" in context:
            continue

        for px_match in re.finditer(r"([0-9]+(?:\.[0-9]+)?)px", value, re.IGNORECASE):
            px_value = float(px_match.group(1))
            if px_value > 4:
                issues.append(
                    _make_issue(
                        "NO2_RADIUS",
                        "warning",
                        f"border-radius {px_value:.0f}px exceeds the <=4px rule.",
                        slide_idx,
                        "Use 0-4px radius for editorial layouts.",
                    )
                )
                break
    return issues


def check_no_large_shadow(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect box-shadow with blur > 4px or spread > 0."""
    issues: list[LintIssue] = []
    for match in re.finditer(r"box-shadow\s*:\s*(?P<value>[^;\"'}]+)", html, re.IGNORECASE):
        value = match.group("value").strip().lower()
        if value in {"none", "0", "0px"}:
            continue

        number_strings: list[str] = re.findall(
            r"(-?[0-9]+(?:\.[0-9]+)?)px", value, re.IGNORECASE
        )
        numbers = [float(number) for number in number_strings]
        if not numbers:
            continue

        blur = abs(numbers[2]) if len(numbers) >= 3 else 0.0
        spread = numbers[3] if len(numbers) >= 4 else 0.0
        if blur > 4 or spread > 0:
            issues.append(
                _make_issue(
                    "NO3_SHADOW",
                    "warning",
                    "box-shadow exceeds anti-AI shadow limits (blur <=4px and spread <=0).",
                    slide_idx,
                    "Remove deep shadows and rely on spacing/dividers instead.",
                )
            )
    return issues


def check_no_neon_glow(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect text-shadow, filter: drop-shadow with bright colors."""
    issues: list[LintIssue] = []
    if re.search(r"text-shadow\s*:", html, re.IGNORECASE):
        issues.append(
            _make_issue(
                "NO4_NEON_TEXT",
                "warning",
                "text-shadow detected; avoid glow-like effects.",
                slide_idx,
                "Use weight and contrast instead of text glow.",
            )
        )

    if re.search(r"drop-shadow\s*\(", html, re.IGNORECASE):
        issues.append(
            _make_issue(
                "NO4_NEON_DROP",
                "warning",
                "drop-shadow filter detected; can create neon/glow aesthetics.",
                slide_idx,
                "Replace with flat color contrast.",
            )
        )

    return issues


def check_color_restraint(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect more than 1 saturated color used in a single slide.
    Neutral colors (gray/black/white) don't count. Only saturated hues.
    """
    issues: list[LintIssue] = []
    hue_buckets = _saturated_hue_buckets(html)
    if len(hue_buckets) > 1:
        issues.append(
            _make_issue(
                "NO5_COLOR_RESTRAINT",
                "warning",
                f"Slide uses {len(hue_buckets)} saturated hue families; target is one accent hue.",
                slide_idx,
                "Limit saturated color usage to one consistent accent.",
            )
        )
    return issues


def check_no_dashboard_ui(html: str, slide_idx: int) -> list[LintIssue]:
    """Detect tab/toggle/pill/badge/card-grid patterns typical of web dashboards."""
    issues: list[LintIssue] = []
    patterns = [
        r"role\s*=\s*[\"']tab[\"']",
        r"class\s*=\s*[\"'][^\"']*(tabs?|toggle|pill|badge|card-grid|widget|dashboard)[^\"']*[\"']",
        r"aria-selected\s*=\s*[\"'](true|false)[\"']",
    ]
    for pattern in patterns:
        if re.search(pattern, html, re.IGNORECASE):
            issues.append(
                _make_issue(
                    "NO6_DASHBOARD_UI",
                    "warning",
                    "Dashboard-like UI pattern detected (tabs/toggles/pills/badges).",
                    slide_idx,
                    "Use narrative layouts, not app UI controls.",
                )
            )
            break
    return issues


def check_editorial_elements(html: str, slide_idx: int) -> list[LintIssue]:
    """Check for presence of editorial details (running header, folio, source citations).
    Info-level (not errors) - suggest adding them if missing.
    """
    issues: list[LintIssue] = []

    has_running_header = "editorial-running-header" in html.lower()
    has_folio = "editorial-folio" in html.lower()
    has_source = "editorial-source" in html.lower() or "source:" in html.lower()
    has_divider = "editorial-divider" in html.lower()

    if not has_running_header:
        issues.append(
            _make_issue(
                "YES1_RUNNING_HEADER",
                "info",
                "Running header is missing.",
                slide_idx,
                "Add `running_header()` for stronger editorial rhythm.",
            )
        )

    if not has_folio:
        issues.append(
            _make_issue(
                "YES1_FOLIO",
                "info",
                "Folio/page number is missing.",
                slide_idx,
                "Add `folio()` for document-grade polish.",
            )
        )

    is_data_slide = _html_contains_any(
        html,
        ["<table", "<svg", "<canvas", "chart", "kpi", "%"],
    )
    if is_data_slide and not has_source:
        issues.append(
            _make_issue(
                "YES1_SOURCE",
                "info",
                "Data-like slide has no source citation.",
                slide_idx,
                "Add `source_citation()` to maintain traceability.",
            )
        )

    if not has_divider:
        issues.append(
            _make_issue(
                "YES1_DIVIDER",
                "info",
                "Thin editorial divider is missing.",
                slide_idx,
                "Add `thin_divider()` under the title zone when appropriate.",
            )
        )

    return issues


def check_typography_hierarchy(html: str, slide_idx: int) -> list[LintIssue]:
    """Check that font sizes create a clear hierarchy.
    Title > subtitle > body > caption. No intermediate sizes that confuse the hierarchy.
    """
    issues: list[LintIssue] = []
    sizes = sorted(set(_collect_font_sizes(html)))
    if not sizes:
        return issues

    if len(sizes) == 1:
        issues.append(
            _make_issue(
                "YES4_TYPE_SINGLE_SIZE",
                "warning",
                "Only one font size detected; hierarchy may be unclear.",
                slide_idx,
                "Use distinct sizes for title, body, and annotation levels.",
            )
        )
        return issues

    if max(sizes) - min(sizes) < 8:
        issues.append(
            _make_issue(
                "YES4_TYPE_RANGE",
                "warning",
                "Font-size range is narrow; typography hierarchy may collapse.",
                slide_idx,
                "Increase contrast between display, body, and caption sizes.",
            )
        )

    descending = sorted(sizes, reverse=True)
    if descending[0] - descending[1] < 6:
        issues.append(
            _make_issue(
                "YES4_TYPE_TOP_GAP",
                "warning",
                "Top two text levels are too close (<6px difference).",
                slide_idx,
                "Increase title size or reduce subtitle size.",
            )
        )

    if len(sizes) > 6:
        issues.append(
            _make_issue(
                "YES4_TYPE_TOO_MANY",
                "info",
                "Many distinct font sizes detected; hierarchy may feel noisy.",
                slide_idx,
                "Consolidate type scale to a smaller set of repeatable sizes.",
            )
        )

    caption_sizes: list[float] = []
    body_sizes: list[float] = []
    for element in _iter_styled_elements(html):
        style_sizes = _font_sizes_in_style(element["style"])
        if not style_sizes:
            continue
        if any(keyword in element["classes"] for keyword in ["caption", "source", "footnote"]):
            caption_sizes.extend(style_sizes)
        else:
            body_sizes.extend([size for size in style_sizes if size >= 16])

    if caption_sizes and body_sizes:
        if min(body_sizes) - max(caption_sizes) < 4:
            issues.append(
                _make_issue(
                    "YES4_TYPE_CAPTION_GAP",
                    "warning",
                    "Caption and body sizes are too close (<4px difference).",
                    slide_idx,
                    "Keep captions visibly smaller than body copy.",
                )
            )

    return issues


def check_consecutive_sameness(slides: list[str], variant_history: list[str]) -> list[LintIssue]:
    """Check that no 2+ consecutive slides use the same variant + same dominant element.
    Uses variant_history from variant_select.VariantState.
    """
    if not slides:
        return []

    variants = variant_history
    if len(variants) != len(slides):
        variants = [_layout_signature(slide) for slide in slides]

    dominants = [_dominant_element(slide) for slide in slides]

    issues: list[LintIssue] = []
    run_length = 1
    for index in range(1, len(slides)):
        if variants[index] == variants[index - 1] and dominants[index] == dominants[index - 1]:
            run_length += 1
            if run_length >= 2:
                issues.append(
                    LintIssue(
                        rule_id="DQ1_CONSECUTIVE_SAME",
                        severity="warning",
                        message=(
                            "Consecutive slides share the same layout variant and dominant element."
                        ),
                        slide_index=index,
                        suggestion="Switch layout or change dominant visual mode on this slide.",
                    )
                )
        else:
            run_length = 1
    return issues


def check_visual_monotony(slides: list[str]) -> list[LintIssue]:
    """Check for structural repetition across slides.
    Detect: same column count, same image placement, same text length patterns.
    """
    if not slides:
        return []

    signatures = [_layout_signature(slide) for slide in slides]
    issues: list[LintIssue] = []

    run_length = 1
    for index in range(1, len(signatures)):
        if signatures[index] == signatures[index - 1]:
            run_length += 1
            if run_length >= 3:
                issues.append(
                    LintIssue(
                        rule_id="DQ1_VISUAL_MONOTONY",
                        severity="warning",
                        message="Three or more consecutive slides have near-identical structure.",
                        slide_index=index,
                        suggestion="Alternate column rhythm, image zone, or text density.",
                    )
                )
        else:
            run_length = 1

    uniqueness_ratio = len(set(signatures)) / len(signatures)
    if len(slides) >= 4 and uniqueness_ratio < 0.5:
        issues.append(
            LintIssue(
                rule_id="DQ1_LOW_VARIETY",
                severity="info",
                message="Deck-level structural variety is low.",
                slide_index=None,
                suggestion="Increase layout diversity while keeping brand consistency.",
            )
        )

    return issues


def lint_slide(html: str, slide_idx: int = 0) -> list[LintIssue]:
    """Run all per-slide lint rules. Returns sorted by severity."""
    issues: list[LintIssue] = []
    checks = [
        check_overflow,
        check_font_minimum,
        check_safe_area,
        check_no_glassmorphism,
        check_no_large_radius,
        check_no_large_shadow,
        check_no_neon_glow,
        check_color_restraint,
        check_no_dashboard_ui,
        check_editorial_elements,
        check_typography_hierarchy,
    ]
    for check in checks:
        issues.extend(check(html, slide_idx))
    return _sort_issues(issues)


def lint_deck(
    slides: list[str],
    variant_history: list[str] | None = None,
) -> list[LintIssue]:
    """Run per-slide + cross-slide lint rules on entire deck."""
    all_issues: list[LintIssue] = []

    for index, slide in enumerate(slides):
        all_issues.extend(lint_slide(slide, index))

    history = variant_history or [_layout_signature(slide) for slide in slides]
    all_issues.extend(check_consecutive_sameness(slides, history))
    all_issues.extend(check_visual_monotony(slides))

    return _sort_issues(all_issues)


def _typography_slide_score(html: str) -> float:
    sizes = sorted(set(_collect_font_sizes(html)))
    if not sizes:
        return 0.4

    has_title = any(size >= 28 for size in sizes)
    has_body = any(16 <= size <= 24 for size in sizes)
    has_caption = any(size <= 13 for size in sizes)
    top_gap = 0.0
    if len(sizes) >= 2:
        descending = sorted(sizes, reverse=True)
        top_gap = 1.0 if descending[0] - descending[1] >= 6 else 0.35
    else:
        top_gap = 0.2

    body_caption_gap = 1.0
    if has_caption and has_body:
        body_sizes = [size for size in sizes if 16 <= size <= 24]
        caption_sizes = [size for size in sizes if size <= 13]
        if body_sizes and caption_sizes:
            body_caption_gap = 1.0 if min(body_sizes) - max(caption_sizes) >= 4 else 0.3

    score = (
        (0.3 if has_title else 0.0)
        + (0.3 if has_body else 0.0)
        + (0.15 if has_caption else 0.05)
        + (0.15 * top_gap)
        + (0.1 * body_caption_gap)
    )

    if len(sizes) > 6:
        score -= 0.1

    return _clamp(score)


def human_likeness_score(
    slides: list[str],
    variant_history: list[str] | None = None,
) -> dict[str, object]:
    """Score a deck on the Human-Likeness scale (0.0 - 1.0).

    Returns:
    {
        "overall": 0.85,
        "details": {
            "H1_layout_rhythm": 0.90,
            "H2_editorial_polish": 0.80,
            "H3_color_restraint": 0.95,
            "H4_typography_hierarchy": 0.85,
            "H5_anti_ai_clean": 0.75,
        },
        "pass": True,
        "issues": [...]
    }
    """
    if not slides:
        return {
            "overall": 0.0,
            "details": {
                "H1_layout_rhythm": 0.0,
                "H2_editorial_polish": 0.0,
                "H3_color_restraint": 0.0,
                "H4_typography_hierarchy": 0.0,
                "H5_anti_ai_clean": 0.0,
            },
            "pass": False,
            "issues": [
                LintIssue(
                    rule_id="HQ_EMPTY_DECK",
                    severity="error",
                    message="No slides provided.",
                    slide_index=None,
                    suggestion="Provide at least one slide HTML string.",
                )
            ],
        }

    total_slides = len(slides)
    variants = variant_history or [_layout_signature(slide) for slide in slides]
    if len(variants) != total_slides:
        variants = [_layout_signature(slide) for slide in slides]

    dominants = [_dominant_element(slide) for slide in slides]
    rhythm_pairs = list(zip(variants, dominants))
    repeated_pairs = sum(
        1
        for index in range(1, total_slides)
        if rhythm_pairs[index] == rhythm_pairs[index - 1]
    )

    run_penalty_units = 0
    run_length = 1
    for index in range(1, total_slides):
        if rhythm_pairs[index] == rhythm_pairs[index - 1]:
            run_length += 1
        else:
            if run_length > 2:
                run_penalty_units += run_length - 2
            run_length = 1
    if run_length > 2:
        run_penalty_units += run_length - 2

    variety_ratio = len(set(variants)) / total_slides
    rhythm_penalty = (repeated_pairs + run_penalty_units) / max(1, total_slides - 1)
    h1_layout_rhythm = _clamp((0.65 * variety_ratio) + (0.35 * (1 - rhythm_penalty)))

    running_header_ratio = sum("editorial-running-header" in slide.lower() for slide in slides) / total_slides
    folio_ratio = sum("editorial-folio" in slide.lower() for slide in slides) / total_slides

    data_slide_indexes = [
        index
        for index, slide in enumerate(slides)
        if _html_contains_any(slide, ["<table", "<svg", "<canvas", "chart", "kpi", "%"])
    ]
    if data_slide_indexes:
        sourced = sum(
            (
                "editorial-source" in slides[index].lower()
                or "source:" in slides[index].lower()
            )
            for index in data_slide_indexes
        )
        source_ratio = sourced / len(data_slide_indexes)

        labeled = sum(
            (
                "editorial-exhibit-label" in slides[index].lower()
                or bool(
                    re.search(
                        r"\b(exhibit|figure|table|chart)\s+\d+",
                        slides[index],
                        re.IGNORECASE,
                    )
                )
            )
            for index in data_slide_indexes
        )
        exhibit_ratio = labeled / len(data_slide_indexes)
    else:
        source_ratio = 1.0
        exhibit_ratio = 1.0

    h2_editorial_polish = _clamp(
        (0.35 * running_header_ratio)
        + (0.35 * folio_ratio)
        + (0.2 * source_ratio)
        + (0.1 * exhibit_ratio)
    )

    hue_sets = [_saturated_hue_buckets(slide) for slide in slides]
    restrained_ratio = sum(1 for hues in hue_sets if len(hues) <= 1) / total_slides

    non_empty_hues = [next(iter(hues)) for hues in hue_sets if len(hues) == 1]
    if non_empty_hues:
        dominant_hue = max(set(non_empty_hues), key=lambda hue: non_empty_hues.count(hue))
        consistent_ratio = sum(
            1 for hues in hue_sets if not hues or dominant_hue in hues
        ) / total_slides
    else:
        consistent_ratio = 1.0

    h3_color_restraint = _clamp((0.7 * restrained_ratio) + (0.3 * consistent_ratio))

    h4_typography_hierarchy = _clamp(
        sum(_typography_slide_score(slide) for slide in slides) / total_slides
    )

    anti_ai_violations = 0
    for index, slide in enumerate(slides):
        anti_ai_violations += len(check_no_glassmorphism(slide, index))
        anti_ai_violations += len(check_no_large_radius(slide, index))
        anti_ai_violations += len(check_no_large_shadow(slide, index))
        anti_ai_violations += len(check_no_neon_glow(slide, index))
        anti_ai_violations += len(check_no_dashboard_ui(slide, index))

    h5_anti_ai_clean = _clamp(1.0 - (0.15 * anti_ai_violations))

    weights: dict[str, float] = {
        "H1_layout_rhythm": 0.25,
        "H2_editorial_polish": 0.20,
        "H3_color_restraint": 0.20,
        "H4_typography_hierarchy": 0.20,
        "H5_anti_ai_clean": 0.15,
    }
    details: dict[str, float] = {
        "H1_layout_rhythm": round(h1_layout_rhythm, 4),
        "H2_editorial_polish": round(h2_editorial_polish, 4),
        "H3_color_restraint": round(h3_color_restraint, 4),
        "H4_typography_hierarchy": round(h4_typography_hierarchy, 4),
        "H5_anti_ai_clean": round(h5_anti_ai_clean, 4),
    }
    overall = (
        details["H1_layout_rhythm"] * weights["H1_layout_rhythm"]
        + details["H2_editorial_polish"] * weights["H2_editorial_polish"]
        + details["H3_color_restraint"] * weights["H3_color_restraint"]
        + details["H4_typography_hierarchy"] * weights["H4_typography_hierarchy"]
        + details["H5_anti_ai_clean"] * weights["H5_anti_ai_clean"]
    )

    issues = lint_deck(slides, variant_history=variants)
    return {
        "overall": round(overall, 4),
        "details": details,
        "pass": overall >= 0.80,
        "issues": issues,
    }
