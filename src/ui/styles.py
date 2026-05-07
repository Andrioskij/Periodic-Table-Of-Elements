from pathlib import Path

from src.config.design_tokens import TOKENS
from src.config.static_data import NUMERIC_TREND_PROPERTIES
from src.ui.theme import get_theme

_STYLESHEET_CACHE: dict[str, str] = {}


def _get_stylesheet_path():
    """Get path to the QSS template file."""
    base_dir = Path(__file__).parent.parent.parent  # Navigate to project root
    return base_dir / "assets" / "styles" / "theme.qss"


_FONT_FAMILY_PLACEHOLDERS = {
    f"font_family_{key}": value
    for key, value in TOKENS["font"]["family"].items()
}
_FONT_SIZE_PLACEHOLDERS = {
    f"font_size_{key}": str(value)
    for key, value in TOKENS["font"]["size"].items()
}
_FONT_WEIGHT_PLACEHOLDERS = {
    f"font_weight_{key}": str(value)
    for key, value in TOKENS["font"]["weight"].items()
}
_LETTER_SPACING_PLACEHOLDERS = {
    f"letter_spacing_{key}": str(value)
    for key, value in TOKENS["font"]["letter_spacing"].items()
}
_SPACING_PLACEHOLDERS = {
    f"spacing_{key}": str(value)
    for key, value in TOKENS["spacing"].items()
}
_RADIUS_PLACEHOLDERS = {
    f"radius_{key}": str(value)
    for key, value in TOKENS["radius"].items()
}
_BORDER_PLACEHOLDERS = {
    f"border_{key}": str(value)
    for key, value in TOKENS["border"].items()
}
_SCALE_PLACEHOLDERS = {
    f"scale_{key}": str(value)
    for key, value in TOKENS["scale"].items()
}
_METRIC_TRACK_RGBA = TOKENS["color"]["metric_progress"]["track_rgba"]
_NUMERIC_PLACEHOLDERS = {
    **_FONT_FAMILY_PLACEHOLDERS,
    **_FONT_SIZE_PLACEHOLDERS,
    **_FONT_WEIGHT_PLACEHOLDERS,
    **_LETTER_SPACING_PLACEHOLDERS,
    **_SPACING_PLACEHOLDERS,
    **_RADIUS_PLACEHOLDERS,
    **_BORDER_PLACEHOLDERS,
    **_SCALE_PLACEHOLDERS,
    "metric_progress_track_rgba": (
        f"rgba({_METRIC_TRACK_RGBA[0]}, {_METRIC_TRACK_RGBA[1]}, "
        f"{_METRIC_TRACK_RGBA[2]}, {_METRIC_TRACK_RGBA[3]})"
    ),
}


def get_stylesheet(theme="dark"):
    """Load the QSS template and substitute theme placeholders.

    Results are cached per theme name; the template file is not
    expected to change at runtime, so the cache never expires.
    """
    if theme in _STYLESHEET_CACHE:
        return _STYLESHEET_CACHE[theme]

    qss_path = _get_stylesheet_path()
    if not qss_path.exists():
        raise FileNotFoundError(f"Stylesheet file not found: {qss_path}")

    template = qss_path.read_text(encoding="utf-8")
    palette = get_theme(theme)
    for key, value in palette.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    for key, value in _NUMERIC_PLACEHOLDERS.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    _STYLESHEET_CACHE[theme] = template
    return template


DEFAULT_UI_COLOR = TOKENS["color"]["fallback"]["ui"]
NUMERIC_TREND_START_COLOR = TOKENS["color"]["trend"]["numeric_gradient"]["start"]
NUMERIC_TREND_END_COLOR = TOKENS["color"]["trend"]["numeric_gradient"]["end"]
TREND_OVERLAY_COLORS = dict(TOKENS["color"]["trend"]["directional"])
TREND_OVERLAY_LABEL_BACKGROUND_RGBA = tuple(
    TOKENS["color"]["trend"]["label_background_rgba"]
)

_CATEGORY_TOKEN_TO_PUBLIC_KEYS = {
    "alkali_metal": ("alkali metal",),
    "alkaline_earth_metal": ("alkaline earth metal",),
    "transition_metal": ("transition metal",),
    "post_transition_metal": ("post-transition metal",),
    "metalloid": ("metalloid",),
    "nonmetal": ("nonmetal",),
    "halogen": ("halogen",),
    "noble_gas": ("noble gas",),
    "lanthanide": ("lanthanide", "lanthanoid"),
    "actinide": ("actinide", "actinoid"),
}


def _build_category_lookup(theme_key):
    palette = {}
    for token_key, public_keys in _CATEGORY_TOKEN_TO_PUBLIC_KEYS.items():
        color = TOKENS["color"]["category"][theme_key][token_key]
        for public_key in public_keys:
            palette[public_key] = color
    return palette


PERIODIC_TABLE_CATEGORY_COLORS = _build_category_lookup("dark")
PERIODIC_TABLE_CATEGORY_COLORS_LIGHT = _build_category_lookup("light")
BUTTON_BORDER_COLORS = dict(TOKENS["color"]["button_border"])


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
    threshold = TOKENS["luminance"]["text_on_color_threshold"]
    return (
        TOKENS["color"]["text_on_color"]["dark"]
        if luminance > threshold
        else TOKENS["color"]["text_on_color"]["light"]
    )


def get_category_color(category, theme="dark"):
    """Return the hex color for an element category, tuned for the given theme.

    The light-theme variants use the same hue with reduced luminosity so
    contrast against a white background still meets WCAG AA.
    """
    category = (category or "").lower()
    palette = (
        PERIODIC_TABLE_CATEGORY_COLORS_LIGHT
        if theme == "light"
        else PERIODIC_TABLE_CATEGORY_COLORS
    )
    return palette.get(category, DEFAULT_UI_COLOR)


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
    theme="dark",
):
    """Compute the (background, text) color pair for an element button.

    Selects the coloring strategy based on the active trend mode:
    category colors for 'normal', macro-class colors for 'macroclass',
    or a gradient-interpolated color for numeric trend properties.
    The ``theme`` parameter selects the category palette tuned for
    either the dark or the light UI mode.
    """
    if trend_mode == "normal" or trend_mode in {"metallic", "nonmetallic"}:
        background_color = get_category_color(element.get("category"), theme=theme)
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
        normal_border_width = TOKENS["border"]["search_match_width"]
        hover_border_color = BUTTON_BORDER_COLORS["search_match_hover"]
    else:
        normal_border_color = BUTTON_BORDER_COLORS["default"]
        normal_border_width = TOKENS["border"]["default_width"]
        hover_border_color = BUTTON_BORDER_COLORS["default_hover"]

    return f"""
            QPushButton {{
                background-color: {background_color};
                color: {text_color};
                border: {normal_border_width}px solid {normal_border_color};
                border-radius: {max(TOKENS["radius"]["cell_min"], int(cell_size * TOKENS["radius"]["cell_ratio"]))}px;
                padding: 2px;
                font-size: {element_font_size}px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                border: {TOKENS["border"]["hover_width"]}px solid {hover_border_color};
            }}

            QPushButton:pressed {{
                border: {TOKENS["border"]["pressed_width"]}px solid {BUTTON_BORDER_COLORS["pressed"]};
            }}

            QPushButton:focus {{
                border: {TOKENS["border"]["focused_width"]}px solid {BUTTON_BORDER_COLORS["focus"]};
            }}

            QPushButton:checked {{
                border: {TOKENS["border"]["selected_width"]}px solid {BUTTON_BORDER_COLORS["selected"]};
            }}

            QPushButton:checked:focus {{
                border: {TOKENS["border"]["focused_width"]}px solid {BUTTON_BORDER_COLORS["focus"]};
            }}
        """
