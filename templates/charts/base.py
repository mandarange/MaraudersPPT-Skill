"""Chart template shared CSS and utilities."""

FONT_STACK = (
    "'Pretendard', 'Apple SD Gothic Neo', 'Malgun Gothic', "
    "'Noto Sans KR', Arial, Helvetica, sans-serif"
)

CONTENT_CSS = """\
.content {
  position: absolute;
  left: var(--layout-safe-margin-x, 100px);
  top: var(--layout-safe-margin-top, 220px);
  width: var(--layout-content-width, 1720px);
  height: var(--layout-content-height, 760px);
  font-family: var(--font-primary, %(font)s);
  color: var(--color-text, #1A1A1A);
  background: var(--color-bg, #FFFFFF);
}""" % {"font": FONT_STACK}

_CAPTURE_CONTENT_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body {
  width: fit-content;
  height: fit-content;
  background: #FFFFFF;
}
.capture-root {
  position: relative !important;
  left: 0 !important;
  top: 0 !important;
  width: var(--layout-content-width, 1720px);
  height: var(--layout-content-height, 760px);
  font-family: var(--font-primary, %(font)s);
  color: var(--color-text, #1A1A1A);
  background: var(--color-bg, #FFFFFF);
  overflow: hidden;
}""" % {"font": FONT_STACK}


def full_css(chart_css: str) -> str:
    """Combine common .content CSS with chart-specific CSS."""
    return CONTENT_CSS + "\n\n" + chart_css


def capture_css(chart_css: str) -> str:
    """Combine capture-root CSS with chart-specific CSS."""
    return _CAPTURE_CONTENT_CSS + "\n\n" + chart_css


def esc(text) -> str:
    """Escape HTML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_html(inner: str, css: str) -> str:
    """Return complete slide HTML (style + content div)."""
    return f'<style>\n{css}\n</style>\n<div class="content">\n{inner}\n</div>'


def wrap_capture_html(
    inner: str,
    css: str,
    width: int = 1720,
    height: int = 760,
) -> str:
    """Return a complete HTML document for Playwright .capture-root screenshot."""
    combined_css = capture_css(css)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ko">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f'  <meta name="viewport" content="width={width}, initial-scale=1">\n'
        f"  <style>\n{combined_css}\n  </style>\n"
        "</head>\n"
        "<body>\n"
        f'  <div class="capture-root" style="width:{width}px;height:{height}px;">\n'
        f"    {inner}\n"
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
