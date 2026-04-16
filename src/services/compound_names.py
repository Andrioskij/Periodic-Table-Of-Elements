"""
Compound naming and formatting module.

Handles IUPAC and traditional compound name formatting with language-specific
grammatical rules (Russian genitive, French elision). Provides utilities for
accent removal and language naming rules lookup.
"""

import unicodedata

__all__ = [
    "format_stock_compound_name",
    "format_traditional_compound_name",
    "RUSSIAN_GENITIVE_EXCEPTIONS",
]

RUSSIAN_GENITIVE_EXCEPTIONS = {
    "медь": "меди",
    "ртуть": "ртути",
}


def _first_letter_without_accents(text):
    """Extract first alphabetic character without accents from text."""
    normalized = unicodedata.normalize("NFKD", text or "")
    for char in normalized:
        if char.isalpha():
            return char.lower()
    return ""


def _needs_french_elision(word):
    """Check if word needs French elision ('d\'' instead of 'de ')."""
    return _first_letter_without_accents(word) in {"a", "e", "i", "o", "u", "y", "h"}


def _to_russian_genitive(name):
    """Convert Russian noun to genitive case for compound naming."""
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


def format_stock_compound_name(nomenclature_data, language_code, anion_name, cation_name, roman=None):
    """
    Format IUPAC (stock) compound name with language-specific rules.

    Args:
        nomenclature_data: Full nomenclature dataset (for language rules)
        language_code: Language code (e.g., 'en', 'ru', 'fr')
        anion_name: Anion name
        cation_name: Cation name (will be converted to genitive in Russian)
        roman: Roman numeral string for stock notation, or None

    Returns:
        Formatted compound name
    """
    # Import here to avoid circular dependency
    from . import localization_service

    code = language_code or "en"
    if code == "fr":
        connector = "d'" if _needs_french_elision(cation_name) else "de "
        suffix = f" ({roman})" if roman else ""
        return f"{anion_name} {connector}{cation_name}{suffix}"

    if code == "ru":
        cation_name = _to_russian_genitive(cation_name)

    rules = localization_service.get_language_naming_rules(nomenclature_data, language_code)
    key = "stock_roman" if roman else "stock_simple"
    template = rules.get(key, "{anion} of {cation}" if not roman else "{anion} of {cation} ({roman})")
    return template.format(anion=anion_name, cation=cation_name, roman=roman or "")


def format_traditional_compound_name(nomenclature_data, language_code, anion_name, epithet):
    """
    Format traditional compound name with language-specific templates.

    Args:
        nomenclature_data: Full nomenclature dataset (for language rules)
        language_code: Language code (e.g., 'en', 'it')
        anion_name: Anion name
        epithet: Traditional epithet (e.g., 'oxide', 'sulfate')

    Returns:
        Formatted compound name
    """
    # Import here to avoid circular dependency
    from . import localization_service

    rules = localization_service.get_language_naming_rules(nomenclature_data, language_code)
    template = rules.get("traditional", "{anion} {epithet}")
    return template.format(anion=anion_name, epithet=epithet)
