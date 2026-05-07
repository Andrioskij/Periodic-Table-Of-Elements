"""Theme color palettes for the dark and light UI modes.

Each palette exposes the same set of named tokens so that the QSS
template ``assets/styles/theme.qss`` and the QPainter-based widgets
can render in either mode by simply selecting a different mapping.

The palette dicts are derived from the canonical ``src.config.design_tokens.TOKENS``
structure at import time. Their object identity is stable so that callers
caching ``DARK_THEME`` / ``LIGHT_THEME`` references (e.g. QPainter panels)
remain identity-comparable across hot reloads of dependent modules.

Helpers ``relative_luminance`` and ``contrast_ratio`` implement the
WCAG 2.1 formulas and are used by tests to verify accessibility.
"""

from src.config.design_tokens import TOKENS

DARK_THEME = dict(TOKENS["color"]["theme"]["dark"])
LIGHT_THEME = dict(TOKENS["color"]["theme"]["light"])

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
