_METAL_CATEGORIES = {
    "alkali metal",
    "alkaline earth metal",
    "transition metal",
    "post-transition metal",
    "lanthanide",
    "lanthanoid",
    "actinide",
    "actinoid",
}


def _is_metal(category):
    return (category or "").lower() in _METAL_CATEGORIES


def classify_binary_compound(cation, anion, *, nomenclature_data, language_code):
    """Classify a binary compound and return (type_key, acid_name_or_None).

    type_key is one of: 'hydracid', 'basic_oxide', 'acidic_oxide', 'binary_salt'.
    acid_name is the localized hydracid name when the compound is a hydracid.
    Detects hydracids regardless of which element is assigned as cation/anion.
    """
    cation_symbol = cation.get("symbol")
    anion_symbol = anion.get("symbol")
    cation_category = cation.get("category", "")

    # Hydracid: one element is H, the other has a known hydracid entry
    hydracids = nomenclature_data.get("hydracids", {})
    if cation_symbol == "H":
        other_symbol = anion_symbol
    elif anion_symbol == "H":
        other_symbol = cation_symbol
    else:
        other_symbol = None

    if other_symbol is not None:
        entry = hydracids.get(other_symbol)
        if entry:
            field = f"name_{language_code}"
            acid_name = entry.get(field) or entry.get("name_en")
            return "hydracid", acid_name

    # Oxides
    if anion_symbol == "O":
        if _is_metal(cation_category):
            return "basic_oxide", None
        return "acidic_oxide", None

    # Default: binary salt
    return "binary_salt", None


def get_compound_pair_key(symbol_a, symbol_b):
    """Create a unique lookup key for a pair of element symbols.

    Sorts the two symbols alphabetically and joins them with a pipe
    separator, so that (Na, Cl) and (Cl, Na) produce the same key.
    """
    return "|".join(sorted([symbol_a, symbol_b]))


def get_common_compounds_for_pair(nomenclature_data, symbol_a, symbol_b):
    """Look up the list of well-known compounds formed by two elements.

    Searches the 'common_compounds' section of the nomenclature dataset
    using the canonical pair key. Returns an empty list when no entry exists.
    """
    pair_key = get_compound_pair_key(symbol_a, symbol_b)
    return nomenclature_data.get("common_compounds", {}).get(pair_key, [])


def get_localized_common_compound_name(compound_entry, language_code):
    """Return the compound name in the requested language.

    Falls back to the English name, then to the raw formula,
    ensuring a display string is always available.
    """
    field = f"name_{language_code}"
    return compound_entry.get(field) or compound_entry.get("name_en") or compound_entry.get("formula")


def format_common_compounds_section(compounds, *, translate, get_localized_name):
    """Build a human-readable text block listing common compounds.

    Returns an empty string when no compounds are available.
    Otherwise, formats each compound as a bullet line with formula
    and localized name.
    """
    if not compounds:
        return ""

    lines = [translate("common_compounds") + ":"]
    for entry in compounds:
        lines.append(f"- {entry.get('formula')}: {get_localized_name(entry)}")
    return "\n".join(lines)


def compose_compound_result_text(
    *,
    compound_a,
    compound_b,
    first_oxidation,
    second_oxidation,
    common_section,
    translate,
    build_binary_formula,
    build_stock_name,
    build_traditional_name,
    nomenclature_data=None,
    language_code="en",
):
    """Assemble the full compound-builder result text shown to the user.

    Validates the selected elements and oxidation states, then generates
    the binary formula along with IUPAC (Stock) and traditional names,
    plus acid/base classification when applicable.
    Returns early with an appropriate message when the input is incomplete
    or invalid (same element, missing oxidation, same-sign charges).
    """
    if compound_a is None or compound_b is None:
        return translate("must_select_ab")

    if compound_a.get("atomic_number") == compound_b.get("atomic_number"):
        return translate("same_element") + _append_section(common_section)

    if first_oxidation is None or second_oxidation is None:
        return translate("select_oxidation") + _append_section(common_section)

    if first_oxidation * second_oxidation >= 0:
        return translate("opposite_sign") + _append_section(common_section)

    if first_oxidation > 0 and second_oxidation < 0:
        cation = compound_a
        anion = compound_b
        cation_charge = first_oxidation
        anion_charge = second_oxidation
    else:
        cation = compound_b
        anion = compound_a
        cation_charge = second_oxidation
        anion_charge = first_oxidation

    formula = build_binary_formula(
        cation.get("symbol"),
        abs(cation_charge),
        anion.get("symbol"),
        abs(anion_charge),
    )
    stock_name = build_stock_name(cation, cation_charge, anion)
    traditional_name = build_traditional_name(cation, cation_charge, anion)

    lines = [
        f"{translate('formula_label')}: {formula}",
        f"{translate('stock_name')}: {stock_name}",
        f"{translate('traditional_name')}: {traditional_name or translate('traditional_na')}",
    ]

    if nomenclature_data is not None:
        type_key, acid_name = classify_binary_compound(
            cation, anion,
            nomenclature_data=nomenclature_data,
            language_code=language_code,
        )
        type_label = translate(type_key)
        lines.append(f"{translate('compound_type')}: {type_label}")
        if acid_name:
            lines.append(f"{translate('acid_name_label')}: {acid_name}")

    result = "\n".join(lines)
    return result + _append_section(common_section)


def _append_section(section):
    """Append a section with double-newline separator, or nothing if empty."""
    if section:
        return "\n\n" + section
    return ""
