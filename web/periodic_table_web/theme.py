"""Visual constants for the browser version.

Two palettes (DARK + LIGHT) with the same keys, plus a ``palette()``
helper that picks one. The legacy ``DARK_*`` scalars are kept as
aliases so existing imports continue to work; ``ThemeState.colors``
is the runtime path that follows the user's toggle.

Palette values mirror the desktop app's ``DARK_THEME`` / ``LIGHT_THEME``
in :mod:`src.ui.theme`. Keys here are the web-facing names; the
``# desktop:`` comment next to each entry records which desktop token
the value is sourced from. Keep both halves in sync — the desktop is
the source of visual truth.

Typography: the web defaults to ``Segoe UI`` to match the desktop QSS
(``assets/styles/theme.qss``); :data:`UI_FONT_FAMILY` is the canonical
CSS stack. Element-cell metrics in :data:`CELL_METRICS` mirror the
desktop ``element_card`` proportions but render in CSS grid so the
layout stays elastic on narrow viewports.
"""

from typing import Final

UI_FONT_FAMILY: Final[str] = (
    "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
)
"""CSS font stack matching the desktop QSS ``font-family`` declaration."""

MONO_FONT_FAMILY: Final[str] = "'Cascadia Code', 'Consolas', monospace"
"""Monospace stack for electron configurations and code-like text."""

CELL_METRICS: Final[dict[str, str]] = {
    "height": "62px",  # desktop element_card cell ~58-64px tall
    "min_width": "48px",
    "atomic_number_size": "0.65rem",
    "symbol_size": "1.25rem",
    "name_size": "0.55rem",
    "border_radius": "6px",  # desktop QPushButton border-radius ~ cell_size * 0.16
    "padding": "3px 4px",
}
"""Element-cell sizing tokens mirrored from the desktop ``element_card``."""

DARK_PALETTE: Final[dict[str, str]] = {
    "background": "#1e1e1e",         # desktop: bg_primary
    "foreground": "#f2f2f2",         # desktop: text_primary
    "panel": "#23272f",              # desktop: bg_card
    "panel_inset": "#20252c",        # desktop: bg_inset
    "border": "#3c3c3c",             # desktop: border
    "accent_active": "#FFD60A",      # desktop: accent
    "accent_inactive": "#3f5261",    # desktop: bg_button
    "text_muted": "#bdbdbd",         # desktop: text_muted
    "cell_text": "#111111",          # desktop: text_on_accent (dark text on coloured cells)
    "selection_border": "#FFD60A",   # desktop: accent (also used as focus ring)
    "block_label": "#dfe7ef",        # desktop: text_strong
    "input_bg": "#252526",           # desktop: bg_input
    "error": "#ff5f5f",              # desktop: painter_arrow_down (red used in painter widgets)
    "divider": "#3c3c3c",            # desktop: border
}

LIGHT_PALETTE: Final[dict[str, str]] = {
    "background": "#fafafa",         # desktop: bg_primary
    "foreground": "#1a1d22",         # desktop: text_primary
    "panel": "#ffffff",              # desktop: bg_card
    "panel_inset": "#eef2f7",        # desktop: bg_inset
    "border": "#cfd4dc",             # desktop: border
    "accent_active": "#1565c0",      # desktop: accent
    "accent_inactive": "#d6dde6",    # desktop: bg_button
    "text_muted": "#5a6270",         # desktop: text_muted
    "cell_text": "#111111",          # desktop: text_on_accent fallback (dark text on coloured cells)
    "selection_border": "#1565c0",   # desktop: accent (focus ring on light theme)
    "block_label": "#1a1d22",        # desktop: text_strong
    "input_bg": "#ffffff",           # desktop: bg_input
    "error": "#c62828",              # desktop: painter_arrow_down
    "divider": "#cfd4dc",            # desktop: border
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


# Category swatches mirror ``src.ui.styles.PERIODIC_TABLE_CATEGORY_COLORS``
# for the dark theme and ``..._LIGHT`` for the light theme. The light
# variants use the same hue with reduced luminosity so contrast against
# a white background still meets WCAG AA — see desktop tests for the
# accessibility budget.
CATEGORY_COLORS: Final[dict[str, str]] = {
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

CATEGORY_COLORS_LIGHT: Final[dict[str, str]] = {
    "alkali metal": "#C46A12",
    "alkaline earth metal": "#9C8418",
    "transition metal": "#2E5380",
    "post-transition metal": "#1F7368",
    "metalloid": "#7F4F77",
    "nonmetal": "#A38B47",
    "halogen": "#C44099",
    "noble gas": "#1F8AB3",
    "lanthanide": "#9077A4",
    "lanthanoid": "#9077A4",
    "actinide": "#6E2DA0",
    "actinoid": "#6E2DA0",
}

DEFAULT_CATEGORY_COLOR: Final[str] = "#7A7A7A"


def category_color(category: str | None, theme: str = "dark") -> str:
    """Return the swatch for an element category, falling back to grey.

    ``theme`` selects the dark or light variant of the desktop palette.
    """
    if not category:
        return DEFAULT_CATEGORY_COLOR
    table = CATEGORY_COLORS_LIGHT if theme == "light" else CATEGORY_COLORS
    return table.get(category.lower(), DEFAULT_CATEGORY_COLOR)
