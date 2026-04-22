import math
import re

OXIDATION_PATTERN = re.compile(r"[+-]?\d+")


def parse_oxidation_states(oxidation_data):
    """Extract and sort the non-zero oxidation states of an element.

    Accepts either a list of integers or a comma-separated string
    (as stored in the dataset). Returns positive values first, then
    negative values, both sorted by ascending absolute value.
    """
    states = []
    if oxidation_data is None:
        return states

    if isinstance(oxidation_data, list):
        raw_items = oxidation_data
    else:
        raw_items = OXIDATION_PATTERN.findall(str(oxidation_data))

    for item in raw_items:
        try:
            value = int(item)
        except (TypeError, ValueError):
            continue
        if value != 0 and value not in states:
            states.append(value)

    positive_states = sorted([value for value in states if value > 0])
    negative_states = sorted([value for value in states if value < 0], key=lambda value: abs(value))
    return positive_states + negative_states


def format_formula_part(symbol, count):
    """Format a single part of a chemical formula (e.g. 'Na' or 'O2').

    Omits the subscript when count is 1, following standard chemical notation.
    """
    return symbol if count == 1 else f"{symbol}{count}"


def build_binary_formula(
    cation_symbol,
    cation_charge,
    anion_symbol,
    anion_charge,
    formatter=None,
):
    """Build the empirical formula for a binary ionic compound.

    Computes the simplest integer ratio of cation to anion using the
    greatest common divisor of their charges, then delegates the
    symbol+subscript rendering to the formatter function.
    """
    format_part = formatter or format_formula_part
    gcd_value = math.gcd(abs(cation_charge), abs(anion_charge))
    cation_count = abs(anion_charge) // gcd_value
    anion_count = abs(cation_charge) // gcd_value
    return (
        f"{format_part(cation_symbol, cation_count)}"
        f"{format_part(anion_symbol, anion_count)}"
    )
