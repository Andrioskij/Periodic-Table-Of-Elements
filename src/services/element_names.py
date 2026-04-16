"""
Element naming and localization module.

Handles localized retrieval of element names, anion names, and support data
from the nomenclature dataset. Provides lookup functions for chemical element
nomenclature across multiple languages.
"""

__all__ = [
    "get_localized_element_name",
    "get_localized_anion_name",
    "get_support_entry",
    "get_localized_support_text",
]


def get_support_entry(nomenclature_data, symbol):
    """Get nomenclature entry for an element symbol."""
    return nomenclature_data.get("elements", {}).get(symbol, {})


def get_localized_support_text(entry, field_prefix, language_code):
    """
    Get localized support text from nomenclature entry.

    Args:
        entry: Element entry from nomenclature_data
        field_prefix: Base field name (e.g., 'name', 'traditional_name')
        language_code: Language code (e.g., 'en', 'it')

    Returns:
        Localized text or fallback to English, or None if not available
    """
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
    """
    Get localized name for an element.

    Args:
        element: Element dict with 'symbol' and 'name' keys
        nomenclature_data: Full nomenclature dataset
        language_code: Language code (e.g., 'en', 'it')

    Returns:
        Localized element name or fallback to English
    """
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"name_{code}"
    if field in entry:
        return entry[field]
    if "name_en" in entry:
        return entry["name_en"]
    return str(element.get("name", "element"))


def get_localized_anion_name(element, nomenclature_data, language_code):
    """
    Get localized anion name for an element.

    Args:
        element: Element dict with 'symbol' key
        nomenclature_data: Full nomenclature dataset
        language_code: Language code (e.g., 'en', 'it')

    Returns:
        Localized anion name or None if not available
    """
    entry = get_support_entry(nomenclature_data, element.get("symbol"))
    code = language_code or "en"
    field = f"anion_{code}"
    if field in entry:
        return entry[field]
    return entry.get("anion_en")
