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


def full_css(chart_css: str) -> str:
    """Combine common .content CSS with chart-specific CSS."""
    return CONTENT_CSS + "\n\n" + chart_css


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
