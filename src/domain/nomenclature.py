from src.domain.compound_builder import parse_oxidation_states


def int_to_roman(number):
    """Convert a positive integer to its Roman numeral representation.

    Used to express cation charges in IUPAC Stock nomenclature
    (e.g. Fe(III) for iron with +3 charge). Returns an empty string
    for None or non-positive values.
    """
    if number is None or number <= 0:
        return ""

    values = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    result = []
    remaining = number
    for value, symbol in values:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)


def _positive_oxidation_states(oxidation_states):
    """Filter an oxidation-state list to keep only positive values.

    Helper used by both Stock and traditional naming functions to
    determine whether the cation exhibits multiple oxidation states.
    """
    return [
        value
        for value in parse_oxidation_states(oxidation_states)
        if value > 0
    ]


def build_stock_name(
    *,
    anion_name,
    cation_name,
    cation_charge,
    oxidation_states,
    traditional_na,
    format_stock_compound_name,
):
    """Build the IUPAC Stock name for a binary compound.

    Appends a Roman-numeral charge indicator only when the cation has
    more than one possible positive oxidation state. Falls back to
    the 'not available' placeholder when the anion name is missing.
    """
    if anion_name is None:
        return traditional_na

    positive_states = _positive_oxidation_states(oxidation_states)

    if len(set(positive_states)) > 1:
        return format_stock_compound_name(
            anion_name,
            cation_name,
            int_to_roman(abs(cation_charge)),
        )

    return format_stock_compound_name(anion_name, cation_name)


def build_traditional_name(
    *,
    anion_name,
    cation_charge,
    oxidation_states,
    low_name,
    high_name,
    traditional_na,
    format_traditional_compound_name,
):
    """Build the traditional (pre-IUPAC) name for a binary compound.

    Uses the '-ous'/'-ic' suffix convention: the lower oxidation state
    gets low_name and the higher gets high_name. Returns the 'not
    available' placeholder when fewer than two positive states exist
    or the required name variant is missing.
    """
    if anion_name is None:
        return traditional_na

    positive_states = sorted(set(_positive_oxidation_states(oxidation_states)))

    if len(positive_states) < 2:
        return traditional_na

    if cation_charge == positive_states[0] and low_name:
        return format_traditional_compound_name(anion_name, low_name)
    if cation_charge == positive_states[-1] and high_name:
        return format_traditional_compound_name(anion_name, high_name)
    return traditional_na
