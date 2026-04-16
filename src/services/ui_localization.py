"""
UI localization lookup module.

Handles localized text lookups for UI elements: categories, standard states,
and macro classes. Provides fallback-aware retrieval from pre-loaded localization
data dictionaries.
"""

__all__ = [
    "get_localized_category_text",
    "get_localized_standard_state_text",
    "get_localized_macro_class_text",
]


def _get_localized_lookup_text(lookup, key, language_code, traditional_na="n/a"):
    """
    Internal helper for localized lookups with fallback to English.

    Args:
        lookup: Dictionary keyed by language_code, containing {key -> text} maps
        key: Text key to look up
        language_code: Language code (e.g., 'en', 'it')
        traditional_na: Fallback text if not available

    Returns:
        Localized text, or English fallback, or key as-is
    """
    # Import here to avoid circular dependency
    from . import localization_service

    code = language_code or "en"
    localization_service._ensure_language_loaded(code)

    localized_map = lookup.get(code, {})
    if key in localized_map:
        return localized_map[key]

    # Fallback to English
    localization_service._ensure_language_loaded("en")
    en_map = lookup.get("en", {})
    return en_map.get(key, key)


def get_localized_category_text(category, language_code, traditional_na="n/a"):
    """
    Get localized text for element category.

    Args:
        category: Category key (e.g., 'metal', 'nonmetal')
        language_code: Language code (e.g., 'en', 'it')
        traditional_na: Fallback text (unused, kept for API compatibility)

    Returns:
        Localized category text
    """
    from . import localization_service

    return _get_localized_lookup_text(
        localization_service.LOCALIZED_CATEGORY_TEXTS,
        category,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_standard_state_text(standard_state, language_code, traditional_na="n/a"):
    """
    Get localized text for standard state.

    Args:
        standard_state: State key (e.g., 'gas', 'liquid', 'solid')
        language_code: Language code (e.g., 'en', 'it')
        traditional_na: Fallback text (unused, kept for API compatibility)

    Returns:
        Localized standard state text
    """
    from . import localization_service

    return _get_localized_lookup_text(
        localization_service.LOCALIZED_STANDARD_STATE_TEXTS,
        standard_state,
        language_code,
        traditional_na=traditional_na,
    )


def get_localized_macro_class_text(macro_class, language_code, traditional_na="n/a"):
    """
    Get localized text for macro class.

    Args:
        macro_class: Macro class key (e.g., 'alkali_metal', 'halogen')
        language_code: Language code (e.g., 'en', 'it')
        traditional_na: Fallback text (unused, kept for API compatibility)

    Returns:
        Localized macro class text
    """
    from . import localization_service

    return _get_localized_lookup_text(
        localization_service.LOCALIZED_MACRO_CLASS_TEXTS,
        macro_class,
        language_code,
        traditional_na=traditional_na,
    )
