import os
from pathlib import Path
from src.config.static_data import NUMERIC_TREND_PROPERTIES


def _get_stylesheet_path():
    """Get path to the QSS stylesheet file."""
    base_dir = Path(__file__).parent.parent.parent  # Navigate to project root
    return base_dir / "assets" / "styles" / "default.qss"


def get_stylesheet():
    """Load stylesheet from external QSS file."""
    qss_path = _get_stylesheet_path()

    if not qss_path.exists():
        raise FileNotFoundError(f"Stylesheet file not found: {qss_path}")

    with open(qss_path, "r", encoding="utf-8") as f:
        return f.read()


DEFAULT_UI_COLOR = "#7A7A7A"
NUMERIC_TREND_START_COLOR = "#2359A8"
NUMERIC_TREND_END_COLOR = "#FFD60A"
TREND_OVERLAY_COLORS = {
    "metallic": "#56CCF2",
    "nonmetallic": "#FFD60A",
}
TREND_OVERLAY_LABEL_BACKGROUND_RGBA = (20, 20, 20, 180)
PERIODIC_TABLE_CATEGORY_COLORS = {
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
BUTTON_BORDER_COLORS = {
    "default": "#202020",
    "default_hover": "#FFFFFF",
    "focus": "#FFD60A",
    "search_match": "#FFD60A",
    "search_match_hover": "#FFF2A8",
    "pressed": "#000000",
    "selected": "#111111",
}


def interpolate_color(color1, color2, t):
    """Linearly blend two hex colors by factor t (0.0 = color1, 1.0 = color2).

    Used to generate the gradient on numeric trend overlays (e.g.
    electronegativity going from blue to yellow).
    """
    t = max(0.0, min(1.0, t))
    c1 = color1.lstrip("#")
    c2 = color2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgba(hex_color, alpha):
    """Convert a hex color string to a CSS rgba() expression with the given alpha."""
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return f"rgba(122, 122, 122, {max(0, min(255, alpha))})"

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {max(0, min(255, alpha))})"


def get_text_color(hex_color):
    """Choose black or white text for readability on the given background color.

    Uses the weighted luminance formula (ITU-R BT.601) to decide
    whether dark or light text provides better contrast.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
    return "#111111" if luminance > 160 else "#FFFFFF"


def get_category_color(category):
    """Return the hex color assigned to an element category (e.g. 'noble gas')."""
    category = (category or "").lower()
    return PERIODIC_TABLE_CATEGORY_COLORS.get(category, DEFAULT_UI_COLOR)


def get_trend_overlay_color(mode):
    """Return the arrow/label color for a directional trend overlay mode."""
    return TREND_OVERLAY_COLORS.get(mode, DEFAULT_UI_COLOR)


def get_current_button_colors(
    element,
    *,
    trend_mode,
    numeric_ranges,
    get_macro_class,
    get_macro_class_color,
):
    """Compute the (background, text) color pair for an element button.

    Selects the coloring strategy based on the active trend mode:
    category colors for 'normal', macro-class colors for 'macroclass',
    or a gradient-interpolated color for numeric trend properties.
    """
    if trend_mode == "normal" or trend_mode in {"metallic", "nonmetallic"}:
        background_color = get_category_color(element.get("category"))
        return background_color, get_text_color(background_color)

    if trend_mode == "macroclass":
        macro_class = get_macro_class(element.get("category"))
        background_color = get_macro_class_color(macro_class)
        return background_color, get_text_color(background_color)

    _, field_name = NUMERIC_TREND_PROPERTIES[trend_mode]
    value = element.get(field_name)

    if not isinstance(value, (int, float)):
        return DEFAULT_UI_COLOR, get_text_color(DEFAULT_UI_COLOR)

    minimum, maximum = numeric_ranges[trend_mode]
    t = 0.5 if maximum == minimum else (value - minimum) / (maximum - minimum)
    background_color = interpolate_color(NUMERIC_TREND_START_COLOR, NUMERIC_TREND_END_COLOR, t)
    return background_color, get_text_color(background_color)


def build_periodic_button_stylesheet(
    *,
    background_color,
    text_color,
    cell_size,
    element_font_size,
    search_match=False,
):
    """Generate the full Qt stylesheet for a single element button.

    Handles normal, hover, pressed, focused, checked, and search-match
    states. Border width and highlight color change when the element
    matches the current search query.
    """
    if search_match:
        normal_border_color = BUTTON_BORDER_COLORS["search_match"]
        normal_border_width = 3
        hover_border_color = BUTTON_BORDER_COLORS["search_match_hover"]
    else:
        normal_border_color = BUTTON_BORDER_COLORS["default"]
        normal_border_width = 1
        hover_border_color = BUTTON_BORDER_COLORS["default_hover"]

    return f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: {normal_border_width}px solid {normal_border_color};
                border-radius: {max(4, int(cell_size * 0.16))}px;
                padding: 2px;
                font-size: {element_font_size}px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                border: 2px solid {hover_border_color};
            }}

            QPushButton:pressed {{
                border: 2px solid {BUTTON_BORDER_COLORS["pressed"]};
            }}

            QPushButton:focus {{
                border: 3px solid {BUTTON_BORDER_COLORS["focus"]};
            }}

            QPushButton:checked {{
                border: 3px solid {BUTTON_BORDER_COLORS["selected"]};
            }}

            QPushButton:checked:focus {{
                border: 3px solid {BUTTON_BORDER_COLORS["focus"]};
            }}
        """
