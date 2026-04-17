"""
Core localization service module.

Central hub for managing multi-language UI text, loading language data from JSON,
and providing translation functionality. Delegates specialized tasks to:
- element_names: Element nomenclature lookups
- compound_names: Compound naming with language-specific rules
- ui_localization: UI text lookups for categories, states, classes
"""

import json
import logging
from pathlib import Path

_logger = logging.getLogger(__name__)

# Import from specialized modules for re-export
from .element_names import (
    get_localized_element_name,
    get_localized_anion_name,
    get_support_entry,
    get_localized_support_text,
)
from .compound_names import (
    format_stock_compound_name,
    format_traditional_compound_name,
    RUSSIAN_GENITIVE_EXCEPTIONS,
)
from .ui_localization import (
    get_localized_category_text,
    get_localized_standard_state_text,
    get_localized_macro_class_text,
)

# Language configuration constants are defined in src/config/languages.py to
# avoid potential circular imports between settings_service and this module.
# They are re-exported here for backward compatibility (see __all__ below).
from src.config.languages import (
    ALL_LANGUAGE_OPTIONS,
    VISIBLE_LANGUAGE_CODES,
    LANGUAGE_OPTIONS,
)

LANGUAGE_READINESS_REQUIRED_TEXT_KEYS = (
    "about_button",
    "about_description",
    "about_dialog_title",
    "about_version",
    "atomic_mass",
    "atomic_number",
    "atomic_radius",
    "boiling_point",
    "builder_scope_note",
    "builder_selection_current",
    "builder_selection_empty",
    "builder_selection_hint",
    "builder_selection_title",
    "builder_status",
    "builder_slot_a_title",
    "builder_slot_b_title",
    "builder_title",
    "builder_search_placeholder_a",
    "builder_search_placeholder_b",
    "calculate_formula",
    "category",
    "close_dialog",
    "common_compounds",
    "compound_prompt",
    "compound_scope_note",
    "current_limits_body",
    "current_limits_title",
    "current_view_macro",
    "current_view_metallic",
    "current_view_metric",
    "current_view_nonmetallic",
    "current_view_normal",
    "density",
    "diagram_accessible_name",
    "diagram_not_available",
    "diagram_prompt",
    "diagram_switch_prompt",
    "diagram_title",
    "diagram_title_symbol",
    "electron_affinity",
    "electronegativity",
    "first_element",
    "first_selected",
    "formula_label",
    "formula_title",
    "group",
    "info_prompt",
    "info_section_chemical_properties",
    "info_section_identity",
    "info_section_physical_properties",
    "ionization_energy",
    "lewis_not_applicable",
    "lewis_prompt",
    "lewis_switch_prompt",
    "lewis_title",
    "lewis_valence_electrons",
    "macro_class",
    "melting_point",
    "metallic_arrow",
    "molar_calculate",
    "molar_error",
    "molar_prompt",
    "molar_title",
    "more_info",
    "must_select_ab",
    "name",
    "no_common_compounds",
    "nonmetallic_arrow",
    "not_selected",
    "opposite_sign",
    "oxidation_first",
    "oxidation_second",
    "oxidation_states",
    "pair_ready_prompt",
    "period",
    "quick_help_body",
    "quick_help_title",
    "reset",
    "right_diagram",
    "right_info",
    "right_lewis",
    "right_molar",
    "right_stoichiometry",
    "same_element",
    "scientific_data_partial_note",
    "scientific_data_partial_note_more",
    "search_button",
    "search_found",
    "search_helper",
    "search_not_found",
    "search_placeholder",
    "search_title",
    "second_element",
    "second_selected",
    "select_oxidation",
    "selected_none",
    "standard_state",
    "stoichiometry_balance",
    "stoichiometry_calc_masses",
    "stoichiometry_error",
    "stoichiometry_mass_section",
    "stoichiometry_prompt",
    "stoichiometry_title",
    "stock_name",
    "symbol",
    "title",
    "tool_nomenclature",
    "tool_molar",
    "tool_stoichiometry",
    "tool_solubility",
    "solubility_anion_label",
    "solubility_cation_label",
    "solubility_check",
    "solubility_exceptions_label",
    "solubility_insoluble",
    "solubility_legend_title",
    "solubility_prompt",
    "solubility_rule_alkali",
    "solubility_rule_carbonate_phosphate_sulfide",
    "solubility_rule_default",
    "solubility_rule_halide",
    "solubility_rule_hydroxide",
    "solubility_rule_label",
    "solubility_rule_nitrate_acetate",
    "solubility_rule_sulfate",
    "solubility_slightly_soluble",
    "solubility_soluble",
    "solubility_title",
    "compound_type",
    "acid_name_label",
    "hydracid",
    "basic_oxide",
    "acidic_oxide",
    "binary_salt",
    "traditional_na",
    "traditional_name",
    "transition_metals",
    "trend_button_macroclass",
    "trend_button_radius",
    "trend_button_ionization",
    "trend_button_affinity",
    "trend_button_electronegativity",
    "trend_button_metallic",
    "trend_button_nonmetallic",
    "trend_button_normal",
    "year_discovered",
)

# Global data structures - loaded from JSON
UI_TEXTS = {}
LOCALIZED_CATEGORY_TEXTS = {}
LOCALIZED_STANDARD_STATE_TEXTS = {}
LOCALIZED_MACRO_CLASS_TEXTS = {}


def _get_localization_data_dir():
    """Get path to localization data directory."""
    base_dir = Path(__file__).parent.parent.parent  # Navigate to project root
    return base_dir / "data" / "localization"


def _load_language_from_json(language_code):
    """Load language data from JSON file."""
    global UI_TEXTS, LOCALIZED_CATEGORY_TEXTS, LOCALIZED_STANDARD_STATE_TEXTS, LOCALIZED_MACRO_CLASS_TEXTS

    data_dir = _get_localization_data_dir()
    json_file = data_dir / f"{language_code}.json"

    if not json_file.exists():
        raise FileNotFoundError(f"Localization file not found: {json_file}")

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Update global dictionaries
    UI_TEXTS[language_code] = data.get("ui_texts", {})
    LOCALIZED_CATEGORY_TEXTS[language_code] = data.get("localized_category_texts", {})
    LOCALIZED_STANDARD_STATE_TEXTS[language_code] = data.get("localized_standard_state_texts", {})
    LOCALIZED_MACRO_CLASS_TEXTS[language_code] = data.get("localized_macro_class_texts", {})


def _ensure_language_loaded(language_code):
    """Ensure language data is loaded, load if needed."""
    if language_code not in UI_TEXTS:
        _load_language_from_json(language_code)


def _load_all_languages():
    """Load all available languages at startup."""
    for code, _ in ALL_LANGUAGE_OPTIONS:
        try:
            _load_language_from_json(code)
        except FileNotFoundError:
            # If a language file is missing, fallback to en
            if code != "en":
                continue
            raise


def _normalize_language_code(language_code):
    """Normalize language code with 'en' as default."""
    return language_code or "en"


def tr(language_code, key, **kwargs):
    """
    Translate key for the given language code.

    Args:
        language_code: Language code (e.g., 'en', 'it', 'ru')
        key: Text key to translate
        **kwargs: Format arguments for the translated string

    Returns:
        Translated text with format applied, or fallback to key name
    """
    code = language_code or "en"
    _ensure_language_loaded(code)
    _ensure_language_loaded("en")

    lang = UI_TEXTS.get(code, {})
    fallback = UI_TEXTS.get("en", {})
    text = lang.get(key, fallback.get(key, key))
    return text.format(**kwargs) if kwargs else text


def get_all_language_codes():
    """Get all available language codes (including disabled ones)."""
    return tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)


def get_visible_language_codes():
    """Get visible language codes for UI selection."""
    return tuple(code for code, _ in LANGUAGE_OPTIONS)


def get_language_naming_rules(nomenclature_data, language_code=None):
    """
    Get compound naming rules for a language from nomenclature metadata.

    Args:
        nomenclature_data: Full nomenclature dataset
        language_code: Language code (uses fallback_language from metadata if None)

    Returns:
        Dictionary with naming patterns for the language
    """
    meta = nomenclature_data.get("meta", {})
    patterns = meta.get("naming_patterns", {})
    fallback_code = meta.get("fallback_language", "en")
    code = language_code or fallback_code
    return patterns.get(code, patterns.get(fallback_code, {}))


def audit_language_readiness(nomenclature_data, language_code):
    """
    Audit language readiness for UI display.

    Checks if language has all required UI strings, verified element names,
    and compound localizations in the dataset.

    Args:
        nomenclature_data: Full nomenclature dataset
        language_code: Language code to audit

    Returns:
        Dictionary with audit results and ready_for_ui flag
    """
    code = language_code or "en"
    _ensure_language_loaded(code)
    ui_texts = UI_TEXTS.get(code, {})
    meta = nomenclature_data.get("meta", {})
    elements = nomenclature_data.get("elements", {})
    common_compounds = nomenclature_data.get("common_compounds", {})
    supported_languages = set(meta.get("supported_languages", []))

    missing_ui_text_keys = sorted(
        key for key in LANGUAGE_READINESS_REQUIRED_TEXT_KEYS if key not in ui_texts
    )
    unverified_name_symbols = sorted(
        symbol
        for symbol, entry in elements.items()
        if code not in entry.get("verified_name_languages", [])
    )
    unverified_anion_symbols = sorted(
        symbol
        for symbol, entry in elements.items()
        if "anion_en" in entry and code not in entry.get("verified_anion_languages", [])
    )
    missing_common_compound_localizations = sorted(
        f"{pair_key}:{compound_entry.get('formula', '?')}"
        for pair_key, entries in common_compounds.items()
        for compound_entry in entries
        if not compound_entry.get(f"name_{code}")
    )

    ready_for_ui = (
        code in supported_languages
        and not missing_ui_text_keys
        and not unverified_name_symbols
        and not unverified_anion_symbols
        and not missing_common_compound_localizations
    )

    return {
        "language_code": code,
        "dataset_supported": code in supported_languages,
        "missing_ui_text_keys": missing_ui_text_keys,
        "unverified_name_symbols": unverified_name_symbols,
        "unverified_anion_symbols": unverified_anion_symbols,
        "missing_common_compound_localizations": missing_common_compound_localizations,
        "ready_for_ui": ready_for_ui,
    }


# Explicit public API
__all__ = [
    # Constants
    "ALL_LANGUAGE_OPTIONS",
    "VISIBLE_LANGUAGE_CODES",
    "LANGUAGE_OPTIONS",
    "LANGUAGE_READINESS_REQUIRED_TEXT_KEYS",
    "RUSSIAN_GENITIVE_EXCEPTIONS",
    # Global data
    "UI_TEXTS",
    "LOCALIZED_CATEGORY_TEXTS",
    "LOCALIZED_STANDARD_STATE_TEXTS",
    "LOCALIZED_MACRO_CLASS_TEXTS",
    # Core translation
    "tr",
    # Language code utilities
    "get_all_language_codes",
    "get_visible_language_codes",
    # Element naming (from element_names module)
    "get_localized_element_name",
    "get_localized_anion_name",
    "get_support_entry",
    "get_localized_support_text",
    # Compound naming (from compound_names module)
    "format_stock_compound_name",
    "format_traditional_compound_name",
    # UI localization (from ui_localization module)
    "get_localized_category_text",
    "get_localized_standard_state_text",
    "get_localized_macro_class_text",
    # Metadata and audit
    "get_language_naming_rules",
    "audit_language_readiness",
]

# Load only English (required fallback) at import time. Other languages are
# loaded on-demand via _ensure_language_loaded() when first requested.
try:
    _load_language_from_json("en")
except FileNotFoundError:
    _logger.error("Critical: English localization file not found")
    raise
