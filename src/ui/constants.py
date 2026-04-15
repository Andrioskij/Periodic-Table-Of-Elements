"""Centralized UI constants to eliminate hardcoded strings."""


class ObjectNames:
    """Qt object names used for CSS selectors and introspection."""

    # Main window
    TITLE_LABEL = "titleLabel"
    SEARCH_CARD = "searchCard"
    SEARCH_TITLE_LABEL = "searchTitleLabel"
    SEARCH_HELP_LABEL = "searchHelpLabel"
    SEARCH_INPUT = "searchInput"
    SEARCH_BUTTON = "searchButton"
    SEARCH_STATUS_LABEL = "searchStatusLabel"

    # Panels and buttons
    PANEL_MINI_BUTTON = "panelMiniButton"
    TREND_BUTTON = "trendButton"
    TREND_STATUS_LABEL = "trendStatusLabel"

    # Compound builder
    COMPOUND_BUILDER_PANEL = "compoundBuilderPanel"
    BUILDER_SELECTOR_CARD = "builderSelectorCard"
    BUILDER_SLOT_BADGE_LABEL = "builderSlotBadgeLabel"
    BUILDER_SLOT_TITLE_LABEL = "builderSlotTitleLabel"
    BUILDER_SELECTOR_SUMMARY_LABEL = "builderSelectorSummaryLabel"
    BUILDER_SEARCH_INPUT = "builderSearchInput"
    BUILDER_SELECTOR_CAPTION_LABEL = "builderSelectorCaptionLabel"
    BUILDER_STATUS_LABEL = "builderStatusLabel"
    BUILDER_BUTTON = "builderButton"
    BUILDER_RESET_BUTTON = "builderResetButton"

    # Info panel
    INFO_SECTION_CARD = "infoSectionCard"
    INFO_SECTION_TITLE = "infoSectionTitle"

    # Periodic table
    PERIODIC_TABLE_WIDGET = "periodicTableWidget"


class LocalizationKeys:
    """Localization keys used throughout the UI."""

    # General
    TITLE = "title"
    ABOUT_BUTTON = "about_button"
    ABOUT_DESCRIPTION = "about_description"
    ABOUT_DIALOG_TITLE = "about_dialog_title"
    ABOUT_VERSION = "about_version"

    # Search
    SEARCH_PLACEHOLDER = "search_placeholder"
    SEARCH_TITLE = "search_title"
    SEARCH_BUTTON = "search_button"

    # Compound builder
    BUILDER_TITLE = "builder_title"
    BUILDER_SCOPE_NOTE = "builder_scope_note"
    BUILDER_SELECTION_CURRENT = "builder_selection_current"
    BUILDER_SELECTION_EMPTY = "builder_selection_empty"
    BUILDER_SELECTION_HINT = "builder_selection_hint"
    BUILDER_SELECTION_TITLE = "builder_selection_title"
    BUILDER_STATUS = "builder_status"
    BUILDER_SLOT_A_TITLE = "builder_slot_a_title"
    BUILDER_SLOT_B_TITLE = "builder_slot_b_title"
    BUILDER_SEARCH_PLACEHOLDER_A = "builder_search_placeholder_a"
    BUILDER_SEARCH_PLACEHOLDER_B = "builder_search_placeholder_b"
    CALCULATE_FORMULA = "calculate_formula"

    # Info panel
    INFO_PROMPT = "info_prompt"

    # Panels
    MOLAR_TITLE = "molar_title"
    MOLAR_PROMPT = "molar_prompt"
    STOICHIOMETRY_TITLE = "stoichiometry_title"
    STOICHIOMETRY_PROMPT = "stoichiometry_prompt"
    DIAGRAM_TITLE = "diagram_title"
    DIAGRAM_PROMPT = "diagram_prompt"
    LEWIS_TITLE = "lewis_title"
    LEWIS_PROMPT = "lewis_prompt"
    SOLUBILITY_TITLE = "solubility_title"
    SOLUBILITY_PROMPT = "solubility_prompt"
    SOLUBILITY_LEGEND_TITLE = "solubility_legend_title"

    # Trends
    CURRENT_VIEW_NORMAL = "current_view_normal"
    CURRENT_VIEW_MACRO = "current_view_macro"
    CURRENT_VIEW_METRIC = "current_view_metric"
    CURRENT_VIEW_METALLIC = "current_view_metallic"
    CURRENT_VIEW_NONMETALLIC = "current_view_nonmetallic"

    # Element properties
    ATOMIC_NUMBER = "atomic_number"
    ATOMIC_MASS = "atomic_mass"
    ATOMIC_RADIUS = "atomic_radius"
    BOILING_POINT = "boiling_point"
    CATEGORY = "category"

    # Tools
    TOOL_COMPOUNDS = "tool_compounds"
    TOOL_MOLAR = "tool_molar"
    TOOL_STOICHIOMETRY = "tool_stoichiometry"
    TOOL_SOLUBILITY = "tool_solubility"

    # Common compounds
    COMMON_COMPOUNDS = "common_compounds"
    COMPOUND_PROMPT = "compound_prompt"
    COMPOUND_SCOPE_NOTE = "compound_scope_note"

    # Dialogs
    CLOSE_DIALOG = "close_dialog"
    CURRENT_LIMITS_BODY = "current_limits_body"
    CURRENT_LIMITS_TITLE = "current_limits_title"


class SettingKeys:
    """Keys for QSettings persistence."""

    LANGUAGE = "language"
    TREND_MODE = "trend_mode"
    WINDOW_GEOMETRY = "window_geometry"
    RIGHT_PANEL_MODE = "right_panel_mode"
    TOOL_AREA_MODE = "tool_area_mode"


__all__ = [
    "ObjectNames",
    "LocalizationKeys",
    "SettingKeys",
]
