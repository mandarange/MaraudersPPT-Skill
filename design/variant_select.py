from __future__ import annotations

from dataclasses import dataclass, field
import importlib
import re
from typing import Literal, cast

DominantElement = Literal["text", "image", "data", "whitespace", "mixed"]
ContentDensity = Literal["sparse", "medium", "dense"]


@dataclass(frozen=True)
class LayoutVariant:
    id: str
    layout_type: str
    variant_key: str
    label: str
    dominant_element: DominantElement
    content_density: ContentDensity
    split_ratio: str | None
    css_overrides: dict[str, str]
    description: str


def _fallback_variant() -> LayoutVariant:
    return LayoutVariant(
        id="body_text.default",
        layout_type="body_text",
        variant_key="default",
        label="Standard Body",
        dominant_element="text",
        content_density="medium",
        split_ratio=None,
        css_overrides={},
        description="Fallback default when variant registry is unavailable.",
    )


def _normalize_dominant(value: object) -> DominantElement:
    dominant = str(value)
    if dominant not in {"text", "image", "data", "whitespace", "mixed"}:
        dominant = "mixed"
    return cast(DominantElement, dominant)


def _normalize_density(value: object) -> ContentDensity:
    density = str(value)
    if density not in {"sparse", "medium", "dense"}:
        density = "medium"
    return cast(ContentDensity, density)


def _read_attr(raw_variant: object, name: str) -> object:
    return cast(object, getattr(raw_variant, name, None))


def _coerce_variant(raw_variant: object) -> LayoutVariant | None:
    variant_id = _read_attr(raw_variant, "id")
    layout_type = _read_attr(raw_variant, "layout_type")
    variant_key = _read_attr(raw_variant, "variant_key")
    label = _read_attr(raw_variant, "label")
    dominant = _read_attr(raw_variant, "dominant_element")
    density = _read_attr(raw_variant, "content_density")
    split_ratio_raw = _read_attr(raw_variant, "split_ratio")
    description = _read_attr(raw_variant, "description")
    raw_overrides = _read_attr(raw_variant, "css_overrides")

    if not isinstance(variant_id, str):
        return None
    if not isinstance(layout_type, str):
        return None
    if not isinstance(variant_key, str):
        return None
    if not isinstance(label, str):
        return None
    if not isinstance(description, str):
        return None
    if split_ratio_raw is not None and not isinstance(split_ratio_raw, str):
        return None
    if not isinstance(raw_overrides, dict):
        return None

    css_overrides: dict[str, str] = {}
    for key_obj, value_obj in cast(dict[object, object], raw_overrides).items():
        if not isinstance(key_obj, str) or not isinstance(value_obj, str):
            return None
        css_overrides[key_obj] = value_obj

    return LayoutVariant(
        id=variant_id,
        layout_type=layout_type,
        variant_key=variant_key,
        label=label,
        dominant_element=_normalize_dominant(dominant),
        content_density=_normalize_density(density),
        split_ratio=split_ratio_raw,
        css_overrides=css_overrides,
        description=description,
    )


def _load_registry() -> tuple[
    dict[str, list[LayoutVariant]],
    dict[str, LayoutVariant],
    LayoutVariant,
]:
    fallback = _fallback_variant()

    module = None
    for module_name in ("design.variants", "variants"):
        try:
            module = importlib.import_module(module_name)
            break
        except ModuleNotFoundError:
            continue

    if module is None:
        return {fallback.layout_type: [fallback]}, {fallback.id: fallback}, fallback

    raw_registry = getattr(module, "VARIANTS", {})
    registry: dict[str, list[LayoutVariant]] = {}

    if isinstance(raw_registry, dict):
        for layout_type_obj, raw_variants_obj in cast(dict[object, object], raw_registry).items():
            if not isinstance(layout_type_obj, str) or not isinstance(raw_variants_obj, list):
                continue

            variants: list[LayoutVariant] = []
            for raw_variant in cast(list[object], raw_variants_obj):
                variant = _coerce_variant(raw_variant)
                if variant is None:
                    continue
                variants.append(variant)

            if variants:
                registry[layout_type_obj] = variants

    if not registry:
        return {fallback.layout_type: [fallback]}, {fallback.id: fallback}, fallback

    default_variants = registry.get("body_text")
    if default_variants:
        default_variant = default_variants[0]
    else:
        default_variant = next(iter(registry.values()))[0]

    variant_by_id = {
        variant.id: variant
        for variant_list in registry.values()
        for variant in variant_list
    }

    return registry, variant_by_id, default_variant


VARIANTS, VARIANT_BY_ID, DEFAULT_VARIANT = _load_registry()

_CONTENT_BLOCK_RE = re.compile(r"(\.content\s*\{)(.*?)(\})", re.DOTALL)


@dataclass
class VariantState:
    history: list[str] = field(default_factory=list)
    dominant_history: list[str] = field(default_factory=list)

    def record(self, variant: LayoutVariant) -> None:
        self.history.append(variant.id)
        self.dominant_history.append(variant.dominant_element)

    @property
    def last_variant(self) -> LayoutVariant | None:
        if not self.history:
            return None
        return VARIANT_BY_ID.get(self.history[-1])

    @property
    def last_variant_key(self) -> str | None:
        last = self.last_variant
        if last is not None:
            return last.variant_key
        if not self.history:
            return None
        if "." not in self.history[-1]:
            return None
        return self.history[-1].split(".", 1)[1]

    @property
    def last_dominant(self) -> str | None:
        if not self.dominant_history:
            return None
        return self.dominant_history[-1]

    @property
    def last_density(self) -> str | None:
        last = self.last_variant
        if last is None:
            return None
        return last.content_density

    @property
    def last_split_ratio(self) -> str | None:
        last = self.last_variant
        if last is None:
            return None
        return last.split_ratio

    @property
    def consecutive_same_dominant(self) -> int:
        if not self.dominant_history:
            return 0

        count = 0
        target = self.dominant_history[-1]
        for dominant in reversed(self.dominant_history):
            if dominant != target:
                break
            count += 1
        return count

    @property
    def consecutive_same_density(self) -> int:
        if not self.history:
            return 0

        last = self.last_variant
        if last is None:
            return 0

        count = 0
        target = last.content_density
        for variant_id in reversed(self.history):
            variant = VARIANT_BY_ID.get(variant_id)
            if variant is None or variant.content_density != target:
                break
            count += 1
        return count


def get_variants(layout_type: str) -> list[LayoutVariant]:
    variants = VARIANTS.get(layout_type)
    if variants:
        return variants
    return [DEFAULT_VARIANT]


def get_variant(layout_type: str, variant_key: str) -> LayoutVariant:
    for variant in get_variants(layout_type):
        if variant.variant_key == variant_key:
            return variant
    raise KeyError(f"Unknown variant '{layout_type}.{variant_key}'")


def _content_hint_bonus(
    variant: LayoutVariant,
    content_hint: dict[str, object] | None,
) -> float:
    if not content_hint:
        return 0.0

    score = 0.0

    word_count = content_hint.get("word_count")
    if isinstance(word_count, int):
        if word_count >= 140:
            if variant.content_density == "dense":
                score += 1.25
            if variant.content_density == "sparse":
                score -= 1.25
        elif word_count <= 50:
            if variant.content_density == "sparse":
                score += 1.0
            if variant.content_density == "dense":
                score -= 0.75

    bullet_count = content_hint.get("bullet_count")
    if isinstance(bullet_count, int):
        if bullet_count >= 5 and variant.content_density == "dense":
            score += 0.75
        if bullet_count <= 3 and variant.content_density == "sparse":
            score += 0.5

    has_image = content_hint.get("has_image")
    if has_image is True and variant.dominant_element in {"image", "mixed"}:
        score += 0.75
    if has_image is False and variant.dominant_element == "image":
        score -= 1.0

    has_data = content_hint.get("has_data")
    if has_data is True and variant.dominant_element == "data":
        score += 0.75

    return score


def _score_variant(
    variant: LayoutVariant,
    state: VariantState,
    content_hint: dict[str, object] | None,
) -> float:
    score = 0.0

    if state.last_variant_key == variant.variant_key:
        score -= 4.0

    if (
        state.consecutive_same_dominant >= 2
        and state.last_dominant == variant.dominant_element
    ):
        score -= 5.0

    if state.consecutive_same_density >= 2 and state.last_density == variant.content_density:
        score -= 3.5

    if state.last_dominant is not None and variant.dominant_element != state.last_dominant:
        score += 2.0

    if state.last_split_ratio is not None and variant.split_ratio != state.last_split_ratio:
        score += 1.25

    score += _content_hint_bonus(variant, content_hint)
    return score


def select_variant(
    layout_type: str,
    state: VariantState,
    content_hint: dict[str, object] | None = None,
    force_variant: str | None = None,
) -> LayoutVariant:
    if force_variant is not None:
        selected = get_variant(layout_type, force_variant)
        state.record(selected)
        return selected

    variants = get_variants(layout_type)
    if len(variants) == 1:
        state.record(variants[0])
        return variants[0]

    best_variant = variants[0]
    best_score = float("-inf")

    for variant in variants:
        score = _score_variant(variant, state, content_hint)
        if score > best_score:
            best_score = score
            best_variant = variant

    state.record(best_variant)
    return best_variant


def _parse_css_properties(content_block: str) -> tuple[list[str], dict[str, str]]:
    order: list[str] = []
    values: dict[str, str] = {}

    for line in content_block.splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped or not stripped.endswith(";"):
            continue

        key, value = stripped[:-1].split(":", 1)
        key = key.strip()
        value = value.strip()

        if key not in values:
            order.append(key)
        values[key] = value

    return order, values


def apply_variant_css(base_css: str, variant: LayoutVariant) -> str:
    if not variant.css_overrides:
        return base_css

    match = _CONTENT_BLOCK_RE.search(base_css)
    if match is None:
        lines = [base_css.rstrip()]
        if lines[0]:
            lines.append("")
        lines.append(".content {")
        for key, value in variant.css_overrides.items():
            lines.append(f"  {key}: {value};")
        lines.append("}")
        return "\n".join(lines)

    opening, body, closing = match.groups()
    order, values = _parse_css_properties(body)

    for key, value in variant.css_overrides.items():
        if key not in values:
            order.append(key)
        values[key] = value

    merged_body = "\n".join(f"  {key}: {values[key]};" for key in order)
    replacement = f"{opening}\n{merged_body}\n{closing}"

    return base_css[: match.start()] + replacement + base_css[match.end() :]
