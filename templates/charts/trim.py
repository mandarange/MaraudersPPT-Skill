"""Pillow-based whitespace auto-cropper for chart screenshots."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Sequence

_Image: Any = None
_ImageOps: Any = None

try:
    from PIL import Image as _Image, ImageOps as _ImageOps  # type: ignore[no-redef]
except ImportError:
    pass


def _find_content_bbox(
    img: Any,
    threshold: int = 250,
) -> tuple[int, int, int, int] | None:
    """BBox of non-background pixels. Background = all channels >= threshold, or alpha == 0."""
    width, height = img.size
    has_alpha = img.mode == "RGBA"
    pixels = img.load()

    x_min, y_min = width, height
    x_max, y_max = -1, -1

    for y in range(height):
        for x in range(width):
            p = pixels[x, y]
            if has_alpha and p[3] == 0:
                continue
            channels = p[:3] if has_alpha else p
            if all(c >= threshold for c in channels):
                continue
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
            if y < y_min:
                y_min = y
            if y > y_max:
                y_max = y

    if x_max < 0:
        return None
    return (x_min, y_min, x_max + 1, y_max + 1)


def autocrop(
    src: str | Path,
    dst: str | Path | None = None,
    padding: int = 4,
    threshold: int = 250,
) -> Path:
    """Trim surrounding whitespace and write the cropped image."""
    if _Image is None:
        raise RuntimeError("Pillow required for auto-crop: pip install Pillow")

    src = Path(src)
    dst = Path(dst) if dst else src

    img = _Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA") if "A" in (img.mode or "") else img.convert("RGB")

    bbox = _find_content_bbox(img, threshold)

    if bbox is None:
        img.save(dst)
        return dst

    cur_padding_l = bbox[0]
    cur_padding_t = bbox[1]
    cur_padding_r = img.width - bbox[2]
    cur_padding_b = img.height - bbox[3]
    already_tight = all(
        p <= padding
        for p in (cur_padding_l, cur_padding_t, cur_padding_r, cur_padding_b)
    )
    if already_tight:
        img.save(dst)
        return dst

    x0 = max(bbox[0] - padding, 0)
    y0 = max(bbox[1] - padding, 0)
    x1 = min(bbox[2] + padding, img.width)
    y1 = min(bbox[3] + padding, img.height)
    img.crop((x0, y0, x1, y1)).save(dst)
    return dst


def main(argv: Sequence[str] | None = None) -> None:
    args = list(argv or sys.argv[1:])

    padding = 4
    threshold = 250

    while args and args[0].startswith("--"):
        flag = args.pop(0)
        if flag == "--padding":
            padding = int(args.pop(0))
        elif flag == "--threshold":
            threshold = int(args.pop(0))
        elif flag == "--dry-run":
            pass
        else:
            print(f"Unknown flag: {flag}", file=sys.stderr)
            sys.exit(1)

    if len(args) < 1:
        print(
            "Usage: trim.py [--padding N] [--threshold N] INPUT [OUTPUT]",
            file=sys.stderr,
        )
        sys.exit(1)

    src = args[0]
    dst = args[1] if len(args) > 1 else None
    result = autocrop(src, dst, padding=padding, threshold=threshold)
    print(result)


if __name__ == "__main__":
    main()
