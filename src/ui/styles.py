from src.config.static_data import NUMERIC_TREND_PROPERTIES


APP_STYLESHEET = """
    QWidget {
        background-color: #1e1e1e;
        color: #f2f2f2;
        font-family: Segoe UI, Arial, sans-serif;
    }

    QLabel#titleLabel {
        font-size: 24px;
        font-weight: bold;
        padding-bottom: 2px;
    }

    QLabel#searchStatusLabel,
    QLabel#trendStatusLabel {
        font-size: 12px;
        color: #c8c8c8;
    }

    QLabel#builderStatusLabel {
        font-size: 11px;
        font-weight: bold;
        color: #d5dee8;
    }

    QLabel#builderScopeLabel,
    QLabel#compoundScopeLabel {
        font-size: 11px;
        color: #c8c8c8;
    }

    QWidget#searchCard {
        background-color: #27303a;
        border: 1px solid #4d5d6b;
        border-radius: 14px;
    }

    QWidget#compoundBuilderPanel {
        background-color: #23272f;
        border: 1px solid #404854;
        border-radius: 14px;
    }

    QWidget#builderSelectionCard,
    QWidget#builderSelectorCard {
        background-color: #20252c;
        border: 1px solid #404854;
        border-radius: 12px;
    }

    QLabel#searchTitleLabel {
        font-size: 16px;
        font-weight: bold;
    }

    QLabel#searchHelpLabel,
    QLabel#builderSelectionTitleLabel,
    QLabel#builderGuideLabel,
    QLabel#builderSelectorCaptionLabel {
        font-size: 11px;
        color: #c8c8c8;
    }

    QLabel#builderSelectionValueLabel,
    QLabel#builderSelectorSummaryLabel {
        font-size: 12px;
        font-weight: bold;
        color: #f2f2f2;
    }

    QLabel#builderSlotTitleLabel {
        font-size: 11px;
        font-weight: bold;
        color: #dfe7ef;
    }

    QLabel#builderSlotBadgeLabel {
        background-color: #FFD60A;
        color: #111111;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#infoLabel,
    QLabel#infoPromptLabel,
    QLabel#compoundResultLabel {
        background-color: #252526;
        border: 1px solid #3c3c3c;
        border-radius: 12px;
        padding: 12px;
        font-size: 13px;
    }

    QWidget#infoCard {
        background-color: #252526;
        border: 1px solid #3c3c3c;
        border-radius: 14px;
    }

    QWidget#infoHero {
        background-color: #27303a;
        border: 1px solid #44515b;
        border-radius: 12px;
    }

    QWidget#infoHeroAccentBar {
        background-color: #ffd60a;
        border-radius: 3px;
    }

    QWidget#infoHeroSymbolCard {
        background-color: #20252c;
        border: 1px solid #44515b;
        border-radius: 12px;
    }

    QWidget#infoSectionCard,
    QWidget#sidePanelCard {
        background-color: #23272f;
        border: 1px solid #404854;
        border-radius: 12px;
    }

    QLabel#infoSectionTitle {
        font-size: 11px;
        font-weight: bold;
        color: #d5dbe4;
        padding-top: 2px;
        letter-spacing: 0.4px;
    }

    QLabel#infoFieldLabel,
    QLabel#infoHeroCaptionLabel,
    QLabel#infoFooterLabel {
        font-size: 11px;
        color: #bdbdbd;
    }

    QLabel#infoFieldValue,
    QLabel#infoHeroValueLabel {
        font-size: 14px;
        font-weight: bold;
        color: #f2f2f2;
    }

    QLabel#infoHeroAtomicNumberLabel {
        font-size: 28px;
        font-weight: bold;
        color: #FFD60A;
    }

    QLabel#infoHeroSymbolLabel {
        font-size: 44px;
        font-weight: bold;
        color: #f2f2f2;
        min-width: 72px;
    }

    QLabel#infoHeroNameLabel {
        font-size: 24px;
        font-weight: bold;
        color: #f2f2f2;
    }

    QLabel#infoHeroBadgeLabel {
        font-size: 11px;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 11px;
    }

    QWidget#infoMetricVisualWidget {
        background: transparent;
    }

    QProgressBar#infoMetricProgressBar {
        background-color: rgba(122, 122, 122, 24);
        border: 1px solid #404854;
        border-radius: 4px;
    }

    QProgressBar#infoMetricProgressBar::chunk {
        background-color: #5f7384;
        border-radius: 4px;
    }

    QLabel#diagramTitleLabel,
    QLabel#compoundTitleLabel,
    QLabel#builderTitleLabel {
        font-size: 14px;
        font-weight: bold;
        padding-top: 2px;
    }

    QLabel#diagramBoxLabel {
        background-color: #20252c;
        border: 1px solid #404854;
        border-radius: 12px;
        padding: 10px;
    }

    QLabel#headerLabel {
        color: #d0d0d0;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#transitionBlockLabel {
        color: #d7e5f5;
        font-size: 14px;
        font-weight: bold;
        padding: 0px;
    }

    QLabel#sideLabel {
        color: #bdbdbd;
        font-size: 11px;
        font-weight: bold;
    }

    QLabel#seriesLabel {
        color: #bdbdbd;
        font-size: 10px;
        font-weight: bold;
    }

    QLineEdit,
    QComboBox {
        background-color: #252526;
        border: 1px solid #3c3c3c;
        border-radius: 8px;
        padding: 6px;
        font-size: 13px;
        color: #f2f2f2;
    }

    QComboBox {
        min-width: 88px;
    }

    QLineEdit#searchInput {
        min-height: 24px;
        font-size: 14px;
    }

    QLineEdit:focus,
    QComboBox:focus {
        border: 2px solid #FFD60A;
        padding: 5px;
    }

    QComboBox::drop-down {
        border: none;
        width: 24px;
    }

    QComboBox QAbstractItemView {
        background-color: #252526;
        color: #f2f2f2;
        border: 1px solid #3c3c3c;
        selection-background-color: #3f5261;
    }

    QPushButton#searchButton,
    QPushButton#trendButton,
    QPushButton#builderButton,
    QPushButton#builderResetButton,
    QPushButton#panelMiniButton {
        background-color: #3f5261;
        color: #ffffff;
        border: 1px solid #5f7384;
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: bold;
    }

    QPushButton#searchButton {
        background-color: #FFD60A;
        color: #111111;
        border: 1px solid #E0B800;
        padding: 6px 12px;
    }

    QPushButton#builderButton,
    QPushButton#builderResetButton {
        padding: 5px 9px;
        font-size: 11px;
    }

    QPushButton#searchButton:hover,
    QPushButton#trendButton:hover,
    QPushButton#builderButton:hover,
    QPushButton#builderResetButton:hover,
    QPushButton#panelMiniButton:hover {
        background-color: #4b6478;
    }

    QPushButton#searchButton:hover {
        background-color: #FFE27A;
    }

    QPushButton#searchButton:pressed,
    QPushButton#trendButton:pressed,
    QPushButton#builderButton:pressed,
    QPushButton#builderResetButton:pressed,
    QPushButton#panelMiniButton:pressed {
        background-color: #32424f;
    }

    QPushButton#searchButton:pressed {
        background-color: #E0B800;
    }

    QPushButton#trendButton:checked,
    QPushButton#panelMiniButton:checked {
        background-color: #FFD60A;
        color: #111111;
        border: 1px solid #E0B800;
    }

    QPushButton#panelMiniButton {
        padding: 5px 9px;
        font-size: 11px;
    }

    QPushButton#searchButton:focus,
    QPushButton#trendButton:focus,
    QPushButton#builderButton:focus,
    QPushButton#builderResetButton:focus,
    QPushButton#panelMiniButton:focus {
        border: 2px solid #FFD60A;
    }

    QPushButton:disabled,
    QComboBox:disabled {
        background-color: #2a2e33;
        color: #8f969e;
        border: 1px solid #434952;
    }

    QScrollArea#infoPanel:focus,
    QWidget#orbitalDiagramPanel:focus,
    QWidget#compoundPanel:focus,
    QWidget#periodicTableWidget:focus {
        border: 1px solid #FFD60A;
        border-radius: 12px;
    }

    QLabel#selectedElementNameLabel {
        font-size: 20px;
        font-weight: bold;
        color: #f2f2f2;
    }

    QListWidget {
        background-color: #252526;
        border: 1px solid #3c3c3c;
        border-radius: 8px;
        padding: 4px;
        font-size: 12px;
    }

    QListWidget::item {
        padding: 6px;
    }

    QListWidget::item:selected {
        background-color: #3f5261;
        color: #ffffff;
    }

    QScrollArea {
        border: none;
    }
"""


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
