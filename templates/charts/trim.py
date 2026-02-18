"""Pillow-based whitespace auto-cropper for chart screenshots."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Sequence

_Image: Any = None
_ImageChops: Any = None

try:
    from PIL import Image as _Image, ImageChops as _ImageChops  # type: ignore[no-redef]
except ImportError:
    pass


def autocrop(
    src: str | Path,
    dst: str | Path | None = None,
    pad: int = 8,
    bg: tuple[int, int, int] = (255, 255, 255),
) -> Path:
    """Trim surrounding whitespace and write the cropped image."""
    if _Image is None or _ImageChops is None:
        raise RuntimeError("Pillow required for auto-crop: pip install Pillow")

    src = Path(src)
    dst = Path(dst) if dst else src

    img = _Image.open(src).convert("RGB")
    bg_img = _Image.new("RGB", img.size, bg)
    diff = _ImageChops.difference(img, bg_img)
    bbox = diff.getbbox()

    if bbox is None:
        img.save(dst)
        return dst

    x0 = max(bbox[0] - pad, 0)
    y0 = max(bbox[1] - pad, 0)
    x1 = min(bbox[2] + pad, img.width)
    y1 = min(bbox[3] + pad, img.height)
    img.crop((x0, y0, x1, y1)).save(dst)
    return dst


def _parse_bg(raw: str) -> tuple[int, int, int]:
    parts = [int(c.strip()) for c in raw.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected R,G,B — got {raw!r}")
    return (parts[0], parts[1], parts[2])


def main(argv: Sequence[str] | None = None) -> None:
    args = list(argv or sys.argv[1:])

    pad = 8
    bg: tuple[int, int, int] = (255, 255, 255)

    while args and args[0].startswith("--"):
        flag = args.pop(0)
        if flag == "--pad":
            pad = int(args.pop(0))
        elif flag == "--bg":
            bg = _parse_bg(args.pop(0))
        else:
            print(f"Unknown flag: {flag}", file=sys.stderr)
            sys.exit(1)

    if len(args) < 1:
        print("Usage: trim.py [--pad N] [--bg R,G,B] INPUT [OUTPUT]", file=sys.stderr)
        sys.exit(1)

    src = args[0]
    dst = args[1] if len(args) > 1 else None
    result = autocrop(src, dst, pad=pad, bg=bg)
    print(result)


if __name__ == "__main__":
    main()
