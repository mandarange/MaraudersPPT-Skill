from __future__ import annotations

from .tokens import TOKENS, TokenMap


def _kebab_case(value: str) -> str:
    return value.replace("_", "-")


def _path_to_var_name(path_parts: tuple[str, ...]) -> str:
    if len(path_parts) >= 3 and path_parts[0] == "color" and path_parts[1] == "semantic":
        return f"--color-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 3 and path_parts[0] == "color" and path_parts[1] == "component":
        return f"--{_kebab_case(path_parts[2])}-color"

    if len(path_parts) >= 3 and path_parts[0] == "typography" and path_parts[1] == "font_stack":
        return f"--font-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 3 and path_parts[0] == "typography" and path_parts[1] == "scale":
        return f"--text-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 3 and path_parts[0] == "typography" and path_parts[1] == "weight":
        return f"--font-weight-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 3 and path_parts[0] == "typography" and path_parts[1] == "tracking":
        return f"--letter-spacing-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 3 and path_parts[0] == "typography" and path_parts[1] == "leading":
        return f"--line-height-{_kebab_case(path_parts[2])}"

    if len(path_parts) >= 2 and path_parts[0] == "layout":
        return f"--layout-{_kebab_case(path_parts[1])}"

    if len(path_parts) >= 2 and path_parts[0] == "component":
        return f"--component-{_kebab_case(path_parts[1])}"

    if len(path_parts) >= 2 and path_parts[0] == "editorial":
        return f"--editorial-{_kebab_case(path_parts[1])}"

    return "--" + "-".join(_kebab_case(part) for part in path_parts)


def _collect_token_vars(
    node: TokenMap,
    prefix: tuple[str, ...] = (),
) -> dict[str, str]:
    token_to_var: dict[str, str] = {}
    for key, value in node.items():
        next_prefix = prefix + (key,)
        if len(next_prefix) >= 2 and next_prefix[0] == "color" and next_prefix[1] == "primitive":
            if isinstance(value, dict):
                token_to_var.update(_collect_token_vars(value, next_prefix))
            continue

        if isinstance(value, dict):
            token_to_var.update(_collect_token_vars(value, next_prefix))
            continue

        token_path = ".".join(next_prefix)
        token_to_var[token_path] = _path_to_var_name(next_prefix)

    return token_to_var


TOKEN_TO_VAR = _collect_token_vars(TOKENS)


def get_var_name(token_path: str) -> str:
    if token_path not in TOKEN_TO_VAR:
        raise KeyError(f"Unknown token path: {token_path}")
    return TOKEN_TO_VAR[token_path]


def css_var(token_path: str, fallback: str | None = None) -> str:
    var_name = get_var_name(token_path)
    if fallback is None:
        return f"var({var_name})"
    return f"var({var_name}, {fallback})"
