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

    If no compounds are available, returns a translated 'no common compounds'
    message. Otherwise, formats each compound as a bullet line with formula
    and localized name.
    """
    if not compounds:
        return translate("no_common_compounds")

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
):
    """Assemble the full compound-builder result text shown to the user.

    Validates the selected elements and oxidation states, then generates
    the binary formula along with IUPAC (Stock) and traditional names.
    Returns early with an appropriate message when the input is incomplete
    or invalid (same element, missing oxidation, same-sign charges).
    """
    if compound_a is None or compound_b is None:
        return translate("must_select_ab")

    if compound_a.get("atomic_number") == compound_b.get("atomic_number"):
        return translate("same_element") + "\n\n" + common_section

    if first_oxidation is None or second_oxidation is None:
        return translate("select_oxidation") + "\n\n" + common_section

    if first_oxidation * second_oxidation >= 0:
        return translate("opposite_sign") + "\n\n" + common_section

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

    return (
        f"{translate('formula_label')}: {formula}\n"
        f"{translate('stock_name')}: {stock_name}\n"
        f"{translate('traditional_name')}: {traditional_name or translate('traditional_na')}\n\n"
        f"{common_section}"
    )
