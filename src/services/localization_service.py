import json
import os
import unicodedata
from pathlib import Path


ALL_LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("it", "Italiano"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("zh", "中文（简体）"),
    ("ru", "Русский"),
]

VISIBLE_LANGUAGE_CODES = tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)

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

LANGUAGE_OPTIONS = [
    (code, label)
    for code, label in ALL_LANGUAGE_OPTIONS
    if code in VISIBLE_LANGUAGE_CODES
]

# Global data structures - loaded from JSON
UI_TEXTS = {}
LOCALIZED_CATEGORY_TEXTS = {}
LOCALIZED_STANDARD_STATE_TEXTS = {}
LOCALIZED_MACRO_CLASS_TEXTS = {}

RUSSIAN_GENITIVE_EXCEPTIONS = {
    "медь": "меди",
    "ртуть": "ртути",
}


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
    return language_code or "en"


def _get_localized_lookup_text(lookup, key, language_code, traditional_na="n/a"):
    code = _normalize_language_code(language_code)
    _ensure_language_loaded(code)

    localized_map = lookup.get(code, {})
    if key in localized_map:
        return localized_map[key]

    # Fallback to English
    _ensure_language_loaded("en")
    en_map = lookup.get("en", {})
    return en_map.get(key, key)


def _first_letter_without_accents(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    for char in normalized:
        if char.isalpha():
            return char.lower()
    return ""


def _needs_french_elision(word):
    return _first_letter_without_accents(word) in {"a", "e", "i", "o", "u", "y", "h"}


def _to_russian_genitive(name):
    word = (name or "").strip()
    if not word:
        return word

    if word in RUSSIAN_GENITIVE_EXCEPTIONS:
        return RUSSIAN_GENITIVE_EXCEPTIONS[word]

    if word.endswith("ий"):
        return f"{word[:-2]}ия"
    if word.endswith("й"):
        return f"{word[:-1]}я"
    if word.endswith("ь"):
        return f"{word[:-1]}и"
    if word.endswith("я"):
        return f"{word[:-1]}и"
    if word.endswith("а"):
        return (
            f"{word[:-1]}и"
            if word[-2:-1] in {"г", "к", "х", "ж", "ч", "ш", "щ", "ц"}
            else f"{word[:-1]}ы"
        )
    if word.endswith("о"):
        return f"{word[:-1]}а"
    return f"{word}а"


def tr(language_code, key, **kwargs):
    """Translate key for the given language code."""
    code = language_code or "en"
    _ensure_language_loaded(code)
    _ensure_language_loaded("en")

    lang = UI_TEXTS.get(code, {})
    fallback = UI_TEXTS.get("en", {})
    text = lang.get(key, fallback.get(key, key))
    return text.format(**kwargs) if kwargs else text


def get_all_language_codes():
    return tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)


def get_visible_language_codes():
    return tuple(code for code, _ in LANGUAGE_OPTIONS)


def audit_language_readiness(nomenclature_data, language_code):
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


def get_support_entry(nomenclature_data, symbol):
    return nomenclature_data.get("elements", {}).get(symbol, {})


def get_language_naming_rules(nomenclature_data, language_code=None):
    meta = nomenclature_data.get("meta", {})
    patterns = meta.get("naming_patterns", {})
    fallback_code = meta.get("fallback_language", "en")
    code = language_code or fallback_code
    return patterns.get(code, patterns.get(fallback_code, {}))


def get_localized_support_text(entry, field_prefix, language_code):
    code = language_code or "en"
    localized_field = f"{field_prefix}_{code}"
    fallback_field = f"{field_prefix}_en"
    localized_value = entry.get(localized_field)
    if localized_value:
        return localized_value

    if field_prefix.startswith("traditional_") and code not in {"en", "it"}:
        return None

    return entry.get(fallback_field)


def get_localized_element_name(element, nomenclature_data, language_code):
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"name_{code}"
    if field in entry:
        return entry[field]
    if "name_en" in entry:
        return entry["name_en"]
    return str(element.get("name", "element"))


def get_localized_anion_name(element, nomenclature_data, language_code):
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"anion_{code}"
    if field in entry:
        return entry[field]
    return entry.get("anion_en")


def get_localized_category_text(category, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_CATEGORY_TEXTS,
        category,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_standard_state_text(standard_state, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_STANDARD_STATE_TEXTS,
        standard_state,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_macro_class_text(macro_class, language_code, traditional_na="n/a"):
    return _get_localized_lookup_text(
        LOCALIZED_MACRO_CLASS_TEXTS,
        macro_class,
        language_code,
        traditional_na=traditional_na,
    )


def format_stock_compound_name(nomenclature_data, language_code, anion_name, cation_name, roman=None):
    code = _normalize_language_code(language_code)
    if code == "fr":
        connector = "d'" if _needs_french_elision(cation_name) else "de "
        suffix = f" ({roman})" if roman else ""
        return f"{anion_name} {connector}{cation_name}{suffix}"

    if code == "ru":
        cation_name = _to_russian_genitive(cation_name)

    rules = get_language_naming_rules(nomenclature_data, language_code)
    key = "stock_roman" if roman else "stock_simple"
    template = rules.get(key, "{anion} of {cation}" if not roman else "{anion} of {cation} ({roman})")
    return template.format(anion=anion_name, cation=cation_name, roman=roman or "")


def format_traditional_compound_name(nomenclature_data, language_code, anion_name, epithet):
    rules = get_language_naming_rules(nomenclature_data, language_code)
    template = rules.get("traditional", "{anion} {epithet}")
    return template.format(anion=anion_name, epithet=epithet)


# Load all languages at module import time
try:
    _load_all_languages()
except FileNotFoundError as e:
    print(f"Warning: Could not load localization files: {e}")
