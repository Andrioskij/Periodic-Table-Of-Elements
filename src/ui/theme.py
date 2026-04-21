"""Theme color palettes for the dark and light UI modes.

Each palette exposes the same set of named tokens so that the QSS
template ``assets/styles/theme.qss`` and the QPainter-based widgets
can render in either mode by simply selecting a different mapping.

Helpers ``relative_luminance`` and ``contrast_ratio`` implement the
WCAG 2.1 formulas and are used by tests to verify accessibility.
"""

DARK_THEME = {
    # Stylesheet placeholders
    "bg_primary": "#1e1e1e",
    "bg_secondary": "#2b2b2b",
    "bg_card": "#23272f",
    "bg_card_alt": "#252526",
    "bg_input": "#252526",
    "bg_inset": "#20252c",
    "bg_hero": "#27303a",
    "bg_button": "#3f5261",
    "bg_button_hover": "#4b6478",
    "bg_button_pressed": "#32424f",
    "bg_disabled": "#2a2e33",
    "bg_search_card": "#27303a",
    "text_primary": "#f2f2f2",
    "text_secondary": "#c8c8c8",
    "text_muted": "#bdbdbd",
    "text_strong": "#dfe7ef",
    "text_disabled": "#8f969e",
    "text_on_accent": "#111111",
    "border": "#3c3c3c",
    "border_strong": "#404854",
    "border_subtle": "#44515b",
    "border_search": "#4d5d6b",
    "border_button": "#5f7384",
    "border_disabled": "#434952",
    "accent": "#FFD60A",
    "accent_hover": "#FFE27A",
    "accent_pressed": "#E0B800",
    "selection_bg": "#3f5261",
    "selection_text": "#ffffff",
    # QPainter-specific (orbital, lewis, solubility)
    "painter_bg": "#20252c",
    "painter_text": "#eef3f8",
    "painter_subtext": "#bec7d2",
    "painter_label": "#d5dde8",
    "painter_box_border": "#516071",
    "painter_arrow_up": "#4fa3ff",
    "painter_arrow_down": "#ff5f5f",
    "painter_dot": "#4fa3ff",
    "solubility_soluble": "#2d8a4e",
    "solubility_insoluble": "#c0392b",
    "solubility_slightly": "#d4a017",
    "solubility_highlight": "#4fa3ff",
}

LIGHT_THEME = {
    "bg_primary": "#fafafa",
    "bg_secondary": "#f0f2f5",
    "bg_card": "#ffffff",
    "bg_card_alt": "#f5f7fa",
    "bg_input": "#ffffff",
    "bg_inset": "#eef2f7",
    "bg_hero": "#e8eef6",
    "bg_button": "#d6dde6",
    "bg_button_hover": "#c5cdd9",
    "bg_button_pressed": "#b4bcc8",
    "bg_disabled": "#ececec",
    "bg_search_card": "#eef3fa",
    "text_primary": "#1a1d22",
    "text_secondary": "#3d4450",
    "text_muted": "#5a6270",
    "text_strong": "#1a1d22",
    "text_disabled": "#9aa1ad",
    "text_on_accent": "#1a1d22",
    "border": "#cfd4dc",
    "border_strong": "#b9c0c9",
    "border_subtle": "#cfd6e0",
    "border_search": "#a9b3c0",
    "border_button": "#9aa3b0",
    "border_disabled": "#d6d9de",
    "accent": "#1565c0",
    "accent_hover": "#1976d2",
    "accent_pressed": "#0d47a1",
    "selection_bg": "#bbdefb",
    "selection_text": "#0d47a1",
    "painter_bg": "#f5f7fa",
    "painter_text": "#1a1d22",
    "painter_subtext": "#3d4450",
    "painter_label": "#1a1d22",
    "painter_box_border": "#7d8794",
    "painter_arrow_up": "#1565c0",
    "painter_arrow_down": "#c62828",
    "painter_dot": "#1565c0",
    "solubility_soluble": "#1b5e20",
    "solubility_insoluble": "#b71c1c",
    "solubility_slightly": "#9a6b00",
    "solubility_highlight": "#1565c0",
}

VALID_THEME_NAMES = ("dark", "light")
DEFAULT_THEME_NAME = "dark"


def get_theme(name="dark"):
    """Return the palette dict for the requested theme name.

    Falls back to the dark palette for unknown names so callers can
    pass user-supplied values without extra validation.
    """
    return LIGHT_THEME if name == "light" else DARK_THEME


def relative_luminance(hex_color):
    """Compute the WCAG 2.1 relative luminance of an sRGB hex color."""
    color = hex_color.lstrip("#")
    if len(color) != 6:
        raise ValueError(f"Expected #RRGGBB hex color, got {hex_color!r}")
    channels = []
    for offset in (0, 2, 4):
        value = int(color[offset:offset + 2], 16) / 255.0
        if value <= 0.03928:
            channels.append(value / 12.92)
        else:
            channels.append(((value + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a, color_b):
    """Return the WCAG contrast ratio between two hex colors (1.0 - 21.0)."""
    la = relative_luminance(color_a)
    lb = relative_luminance(color_b)
    lighter, darker = (la, lb) if la >= lb else (lb, la)
    return (lighter + 0.05) / (darker + 0.05)


__all__ = [
    "DARK_THEME",
    "LIGHT_THEME",
    "VALID_THEME_NAMES",
    "DEFAULT_THEME_NAME",
    "get_theme",
    "relative_luminance",
    "contrast_ratio",
]
