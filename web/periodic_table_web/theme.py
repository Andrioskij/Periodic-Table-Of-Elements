"""Visual constants for the browser version.

Palette mirrors the desktop app (src.ui.styles) so the two stay
visually consistent. Kept separate from the desktop module because the
Reflex runtime cannot import PySide6.
"""

DARK_BACKGROUND = "#1e1e2e"
DARK_FOREGROUND = "#e6e6e6"
DARK_BORDER = "#2a2a3a"
DARK_PANEL = "#262638"
DARK_LABEL_MUTED = "#161620"

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
