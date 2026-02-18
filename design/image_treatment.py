"""Image treatment pipeline - strategies for professional image handling.

Instead of "insert and forget", images get treatment that integrates them
into the slide's visual hierarchy. All treatments output CSS properties.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TreatmentType = Literal[
    "crop_focus",
    "muted_tone",
    "readability_overlay",
    "background_panel",
]


@dataclass(frozen=True)
class ImageTreatment:
    """CSS-based image treatment specification."""

    id: TreatmentType
    label: str
    description: str
    css_properties: dict[str, str]
    container_css: dict[str, str]


TREATMENTS: dict[TreatmentType, ImageTreatment] = {
    "crop_focus": ImageTreatment(
        id="crop_focus",
        label="Crop to Focus",
        description=(
            "Object-fit: cover with strategic positioning. "
            "Image fills container, cropped to content center."
        ),
        css_properties={
            "object-fit": "cover",
            "object-position": "center 30%",
            "width": "100%",
            "height": "100%",
        },
        container_css={
            "overflow": "hidden",
            "border-radius": "2px",
        },
    ),
    "muted_tone": ImageTreatment(
        id="muted_tone",
        label="Muted/Desaturated",
        description=(
            "Reduce saturation + slight brightness increase "
            "for a restrained, editorial tone."
        ),
        css_properties={
            "filter": "saturate(0.4) brightness(1.05) contrast(0.95)",
            "object-fit": "cover",
            "width": "100%",
            "height": "100%",
        },
        container_css={
            "overflow": "hidden",
        },
    ),
    "readability_overlay": ImageTreatment(
        id="readability_overlay",
        label="Readability Overlay",
        description=(
            "Semi-transparent dark overlay for text readability on image "
            "backgrounds. Gradient from bottom. Requires `.img-overlay` class "
            "and `overlay_css()` style block."
        ),
        css_properties={
            "object-fit": "cover",
            "width": "100%",
            "height": "100%",
        },
        container_css={
            "position": "relative",
            "overflow": "hidden",
        },
    ),
    "background_panel": ImageTreatment(
        id="background_panel",
        label="Background Panel",
        description=(
            "Image as subtle background panel - very low opacity, behind content."
        ),
        css_properties={
            "object-fit": "cover",
            "width": "100%",
            "height": "100%",
            "opacity": "0.08",
            "filter": "saturate(0) brightness(1.2)",
        },
        container_css={
            "position": "absolute",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "z-index": "0",
            "overflow": "hidden",
        },
    ),
}


def _to_inline_css(properties: dict[str, str]) -> str:
    return ";".join(f"{name}:{value}" for name, value in properties.items()) + ";"


def get_treatment(treatment_type: TreatmentType) -> ImageTreatment:
    """Get a treatment by type."""
    return TREATMENTS[treatment_type]


def treatment_to_css(treatment: ImageTreatment) -> str:
    """Convert treatment to inline CSS string for the img element."""
    return _to_inline_css(treatment.css_properties)


def container_to_css(treatment: ImageTreatment) -> str:
    """Convert treatment container CSS to inline style string."""
    return _to_inline_css(treatment.container_css)


def overlay_css() -> str:
    """Return CSS for the readability overlay pseudo-element."""
    return (
        "<style>"
        ".img-overlay::after{"
        "content:'';"
        "position:absolute;"
        "bottom:0;left:0;right:0;"
        "height:60%;"
        "background:linear-gradient(transparent,rgba(0,0,0,0.55));"
        "pointer-events:none;"
        "}"
        "</style>"
    )


def suggest_treatment(
    context: str,
    has_text_overlay: bool = False,
    is_background: bool = False,
    is_hero: bool = False,
) -> TreatmentType:
    """Suggest the best treatment based on image context."""
    _ = context
    if is_background:
        return "background_panel"
    if has_text_overlay:
        return "readability_overlay"
    if is_hero:
        return "crop_focus"
    return "muted_tone"
