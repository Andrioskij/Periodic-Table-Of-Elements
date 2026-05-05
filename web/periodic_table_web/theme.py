"""Visual constants for the browser version.

Two palettes (DARK + LIGHT) with the same keys, plus a ``palette()``
helper that picks one. The legacy ``DARK_*`` scalars are kept as
aliases so existing imports continue to work; ``ThemeState.colors``
is the runtime path that follows the user's toggle.

Palette colours mirror the desktop app's dark theme where
applicable. The light palette is web-only — the desktop app's
``src.ui.styles`` provides a Qt-styled light theme that cannot be
imported here (PySide6 dependency).
"""

from typing import Final

DARK_PALETTE: Final[dict[str, str]] = {
    "background": "#1e1e2e",
    "foreground": "#e6e6e6",
    "panel": "#262638",
    "panel_inset": "#1f1f2e",
    "border": "#2a2a3a",
    "accent_active": "#4e79a7",
    "accent_inactive": "#1f1f2e",
    "text_muted": "#9a9aa8",
    "cell_text": "#161620",
    "selection_border": "#f5d442",
    "block_label": "#cfcfdc",
    "input_bg": "#262638",
    "error": "#f7a8a8",
    "divider": "#2a2a3a",
}

LIGHT_PALETTE: Final[dict[str, str]] = {
    "background": "#f7f7fb",
    "foreground": "#1e1e2e",
    "panel": "#ffffff",
    "panel_inset": "#eceefa",
    "border": "#d4d4dc",
    "accent_active": "#4e79a7",
    "accent_inactive": "#e8e8ee",
    "text_muted": "#6a6a7a",
    "cell_text": "#161620",
    "selection_border": "#c19500",
    "block_label": "#4a4a5c",
    "input_bg": "#ffffff",
    "error": "#c14953",
    "divider": "#d4d4dc",
}

_PALETTES: Final[dict[str, dict[str, str]]] = {
    "dark": DARK_PALETTE,
    "light": LIGHT_PALETTE,
}


def palette(theme: str = "dark") -> dict[str, str]:
    """Return the colour map for ``theme``; falls back to dark on misses."""
    return _PALETTES.get(theme, DARK_PALETTE)


# Legacy scalar aliases — kept because several modules import these
# directly. New code should prefer ``ThemeState.colors[key]``.
DARK_BACKGROUND: Final[str] = DARK_PALETTE["background"]
DARK_FOREGROUND: Final[str] = DARK_PALETTE["foreground"]
DARK_BORDER: Final[str] = DARK_PALETTE["border"]
DARK_PANEL: Final[str] = DARK_PALETTE["panel"]
DARK_LABEL_MUTED: Final[str] = DARK_PALETTE["cell_text"]


CATEGORY_COLORS: dict[str, str] = {
    "alkali metal": "#F28E2B",
    "alkaline earth metal": "#EDC948",
    "transition metal": "#4E79A7",
    "post-transition metal": "#2A9D8F",
    "metalloid": "#B07AA1",
    "nonmetal": "#E9D8A6",
    "halogen": "#FF66C4",
    "noble gas": "#56CCF2",
    "lanthanide": "#CDB4DB",
    "lanthanoid": "#CDB4DB",
    "actinide": "#9D4EDD",
    "actinoid": "#9D4EDD",
}
DEFAULT_CATEGORY_COLOR = "#7A7A7A"


def category_color(category: str | None) -> str:
    """Return the swatch for an element category, falling back to grey."""
    if not category:
        return DEFAULT_CATEGORY_COLOR
    return CATEGORY_COLORS.get(category.lower(), DEFAULT_CATEGORY_COLOR)
