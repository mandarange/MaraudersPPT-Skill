from __future__ import annotations

from copy import deepcopy

from .tokens import TokenMap


THEMES: dict[str, TokenMap] = {
    "consulting_minimal": {
        "meta": {
            "name": "Consulting Minimal",
            "description": "McKinsey/BCG corporate aesthetic. Navy + Helvetica.",
        },
        "color": {
            "semantic": {
                "bg": "#FFFFFF",
                "surface": "#F8F9FA",
                "text": "#1A1A2E",
                "text_secondary": "#4A4A5A",
                "text_muted": "#6B7280",
                "accent": "#003087",
                "accent_subtle": "#EEF3FF",
                "border": "#E5E7EB",
                "border_light": "#F3F4F6",
                "divider": "#E5E7EB",
            },
            "component": {
                "kpi_value": "#1A1A2E",
                "kpi_label": "#4A4A5A",
                "kpi_delta": "#6B7280",
                "kpi_accent_border": "#003087",
                "bar_fill_default": "#C8CED8",
                "bar_fill_max": "#1A1A2E",
                "bar_fill_accent": "#003087",
                "bar_track": "#EEF1F5",
                "bar_label": "#4A4A5A",
                "bar_value": "#1A1A2E",
                "donut_legend": "#4A4A5A",
                "compare_left_bg": "#F8F9FA",
                "compare_right_bg": "#FFFFFF",
                "compare_divider_text": "#C9CDD5",
                "compare_divider_line": "#E5E7EB",
                "compare_bullet_default": "#C9CDD5",
                "compare_bullet_accent": "#003087",
            },
        },
        "typography": {
            "font_stack": {
                "primary": "'Helvetica Neue', Arial, 'Pretendard', sans-serif",
                "display": "'Helvetica Neue', Arial, 'Pretendard', sans-serif",
            },
        },
    },
    "modern_editorial": {
        "meta": {
            "name": "Modern Editorial",
            "description": "Magazine-inspired layout system. Editorial red with serif display.",
        },
        "color": {
            "semantic": {
                "bg": "#FFFEFB",
                "surface": "#F9F4F3",
                "text": "#1F1A1A",
                "text_secondary": "#5A4E4E",
                "text_muted": "#7B7070",
                "accent": "#C41E3A",
                "accent_subtle": "#FCEEF1",
                "border": "#E8DFDD",
                "border_light": "#F3ECEA",
                "divider": "#E8DFDD",
            },
            "component": {
                "kpi_value": "#1F1A1A",
                "kpi_label": "#5A4E4E",
                "kpi_delta": "#7B7070",
                "kpi_accent_border": "#C41E3A",
                "bar_fill_default": "#D8CDCC",
                "bar_fill_max": "#1F1A1A",
                "bar_fill_accent": "#C41E3A",
                "bar_track": "#F3ECEA",
                "bar_label": "#5A4E4E",
                "bar_value": "#1F1A1A",
                "donut_legend": "#5A4E4E",
                "compare_left_bg": "#F9F4F3",
                "compare_right_bg": "#FFFEFB",
                "compare_divider_text": "#D5C8C6",
                "compare_divider_line": "#E8DFDD",
                "compare_bullet_default": "#D5C8C6",
                "compare_bullet_accent": "#C41E3A",
            },
        },
        "typography": {
            "font_stack": {
                "primary": "'Pretendard', 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif",
                "display": "'Iowan Old Style', 'Times New Roman', 'Noto Serif KR', serif",
            },
        },
    },
    "product_pitch": {
        "meta": {
            "name": "Product Pitch",
            "description": "High-contrast product narrative. Cobalt accent with tight typography.",
        },
        "color": {
            "semantic": {
                "bg": "#FFFFFF",
                "surface": "#F5F7FC",
                "text": "#111827",
                "text_secondary": "#374151",
                "text_muted": "#6B7280",
                "accent": "#1B4FD8",
                "accent_subtle": "#EEF3FF",
                "border": "#DDE3F0",
                "border_light": "#EEF2F8",
                "divider": "#DDE3F0",
            },
            "component": {
                "kpi_value": "#111827",
                "kpi_label": "#374151",
                "kpi_delta": "#6B7280",
                "kpi_accent_border": "#1B4FD8",
                "bar_fill_default": "#CAD4EA",
                "bar_fill_max": "#111827",
                "bar_fill_accent": "#1B4FD8",
                "bar_track": "#EEF2F8",
                "bar_label": "#374151",
                "bar_value": "#111827",
                "donut_legend": "#374151",
                "compare_left_bg": "#F5F7FC",
                "compare_right_bg": "#FFFFFF",
                "compare_divider_text": "#C7D0E5",
                "compare_divider_line": "#DDE3F0",
                "compare_bullet_default": "#C7D0E5",
                "compare_bullet_accent": "#1B4FD8",
            },
        },
        "typography": {
            "font_stack": {
                "primary": "'Pretendard', 'Segoe UI', Arial, sans-serif",
                "display": "'Space Grotesk', 'Pretendard', 'Segoe UI', sans-serif",
            },
        },
    },
    "dark_executive": {
        "meta": {
            "name": "Dark Executive",
            "description": "Executive dark mode for projection rooms. Muted steel accent.",
        },
        "color": {
            "semantic": {
                "bg": "#0C0C0C",
                "surface": "#151515",
                "text": "#F2F2F2",
                "text_secondary": "#D1D5DB",
                "text_muted": "#9CA3AF",
                "accent": "#8A94A6",
                "accent_subtle": "#1B1E24",
                "border": "#2B2F36",
                "border_light": "#3A3F47",
                "divider": "#2B2F36",
            },
            "component": {
                "kpi_value": "#F2F2F2",
                "kpi_label": "#D1D5DB",
                "kpi_delta": "#9CA3AF",
                "kpi_accent_border": "#8A94A6",
                "bar_fill_default": "#4B5563",
                "bar_fill_max": "#F2F2F2",
                "bar_fill_accent": "#8A94A6",
                "bar_track": "#242831",
                "bar_label": "#D1D5DB",
                "bar_value": "#F2F2F2",
                "donut_legend": "#D1D5DB",
                "compare_left_bg": "#151515",
                "compare_right_bg": "#111111",
                "compare_divider_text": "#4B5563",
                "compare_divider_line": "#2B2F36",
                "compare_bullet_default": "#4B5563",
                "compare_bullet_accent": "#8A94A6",
            },
        },
        "typography": {
            "font_stack": {
                "primary": "'Avenir Next', 'Pretendard', Arial, sans-serif",
                "display": "'Avenir Next', 'Pretendard', Arial, sans-serif",
            },
        },
    },
    "academic_clean": {
        "meta": {
            "name": "Academic Clean",
            "description": "Scholarly report tone. Warm paper background with burgundy accent.",
        },
        "color": {
            "semantic": {
                "bg": "#FFFEF7",
                "surface": "#F8F5EE",
                "text": "#2B211B",
                "text_secondary": "#5B4A3F",
                "text_muted": "#7A6C63",
                "accent": "#8B0000",
                "accent_subtle": "#F9ECEC",
                "border": "#E5DDD1",
                "border_light": "#F2ECE3",
                "divider": "#DDD3C4",
            },
            "component": {
                "kpi_value": "#2B211B",
                "kpi_label": "#5B4A3F",
                "kpi_delta": "#7A6C63",
                "kpi_accent_border": "#8B0000",
                "bar_fill_default": "#D6CEC0",
                "bar_fill_max": "#2B211B",
                "bar_fill_accent": "#8B0000",
                "bar_track": "#F2ECE3",
                "bar_label": "#5B4A3F",
                "bar_value": "#2B211B",
                "donut_legend": "#5B4A3F",
                "compare_left_bg": "#F8F5EE",
                "compare_right_bg": "#FFFEF7",
                "compare_divider_text": "#CDC2B0",
                "compare_divider_line": "#DDD3C4",
                "compare_bullet_default": "#CDC2B0",
                "compare_bullet_accent": "#8B0000",
            },
        },
        "typography": {
            "font_stack": {
                "primary": "'Source Serif 4', 'Times New Roman', 'Noto Serif KR', serif",
                "display": "'Source Serif 4', 'Times New Roman', 'Noto Serif KR', serif",
            },
        },
    },
}

LEGACY_DEFAULT = "consulting_minimal"


def get_theme(name: str) -> TokenMap:
    """Return theme override dict. Raises KeyError for unknown themes."""
    if name not in THEMES:
        raise KeyError(f"Unknown theme: {name}")
    return deepcopy(THEMES[name])


def list_themes() -> list[str]:
    """Return available theme names."""
    return list(THEMES.keys())
