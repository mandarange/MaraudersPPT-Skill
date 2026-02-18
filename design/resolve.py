from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy

from .tokens import TokenLeaf, TokenMap, TokenNode
from .vars import TOKEN_TO_VAR, get_var_name


class ThemeResolver:
    _base_tokens: TokenMap
    _theme_overrides: TokenMap

    def __init__(
        self,
        base_tokens: TokenMap,
        theme_overrides: TokenMap | None = None,
    ):
        self._base_tokens = deepcopy(base_tokens)
        self._theme_overrides = deepcopy(theme_overrides or {})

    def resolve(self) -> TokenMap:
        """Deep-merge theme overrides onto base tokens, return resolved dict."""
        resolved = deepcopy(self._base_tokens)
        self._deep_merge(resolved, self._theme_overrides)
        return resolved

    def to_css_vars(self) -> str:
        """Generate CSS custom properties block for :root injection."""
        resolved = self.resolve()
        flat_tokens = self._flatten_tokens(resolved)

        lines = [":root {"]
        for token_path in sorted(TOKEN_TO_VAR):
            if token_path not in flat_tokens:
                continue
            var_name = get_var_name(token_path)
            css_value = self._format_css_value(token_path, flat_tokens[token_path])
            lines.append(f"  {var_name}: {css_value};")
        lines.append("}")
        return "\n".join(lines)

    def to_inline_style_block(self) -> str:
        """Returns '<style>:root { ... }</style>' ready for HTML injection."""
        return f"<style>{self.to_css_vars()}</style>"

    @classmethod
    def _deep_merge(cls, base: TokenMap, overrides: Mapping[str, TokenNode]) -> None:
        for key, value in overrides.items():
            base_value = base.get(key)
            if isinstance(base_value, dict) and isinstance(value, dict):
                cls._deep_merge(base_value, value)
                continue
            base[key] = deepcopy(value)

    @classmethod
    def _flatten_tokens(
        cls,
        node: Mapping[str, TokenNode],
        prefix: tuple[str, ...] = (),
    ) -> dict[str, TokenLeaf]:
        flat: dict[str, TokenLeaf] = {}
        for key, value in node.items():
            next_prefix = prefix + (key,)
            if isinstance(value, dict):
                flat.update(cls._flatten_tokens(value, next_prefix))
                continue
            flat[".".join(next_prefix)] = value
        return flat

    @classmethod
    def _format_css_value(cls, token_path: str, value: TokenLeaf) -> str:
        if isinstance(value, (int, float)):
            return cls._format_numeric_value(token_path, value)
        return str(value)

    @classmethod
    def _format_numeric_value(cls, token_path: str, value: int | float) -> str:
        numeric = cls._stringify_number(value)
        if cls._uses_px(token_path):
            return f"{numeric}px"
        return numeric

    @staticmethod
    def _stringify_number(value: int | float) -> str:
        if isinstance(value, int):
            return str(value)
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        if text in {"", "-0"}:
            return "0"
        return text

    @staticmethod
    def _uses_px(token_path: str) -> bool:
        if token_path.startswith("typography.scale."):
            return True
        if token_path.startswith("typography.tracking."):
            return True
        if token_path.startswith("layout."):
            return True
        if token_path.startswith("component.") and token_path != "component.shadow":
            return True
        if token_path.startswith("editorial.") and token_path != "editorial.running_header_opacity":
            return True
        return False
