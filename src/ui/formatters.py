import re
from dataclasses import dataclass

EV_TO_KJ_PER_MOL = 96.48533212331002

# Unicode subscript digits, indexed 0–9 so the lookup is a constant-time
# string slice (``_SUBSCRIPT_DIGITS[int(d)]``) instead of a per-digit
# function call. Mirrors the JS ``SUBSCRIPT_DIGITS`` constant used by
# the web companion's ``formatChemicalFormula`` so desktop and web
# render the same glyphs.
_SUBSCRIPT_DIGITS = "₀₁₂₃₄₅₆₇₈₉"
_FORMULA_DIGIT_PATTERN = re.compile(r"([A-Za-z\)])(\d+)")


@dataclass(frozen=True)
class MeasurementFieldFormat:
    unit: str
    decimals: int = 3
    trim_trailing_zeroes: bool = True
    scale: float = 1.0


MEASUREMENT_FIELD_FORMATS = {
    "atomic_mass": MeasurementFieldFormat(unit="kg/mol", decimals=7, scale=0.001),
    "atomic_radius": MeasurementFieldFormat(unit="pm", decimals=0),
    "ionization_energy": MeasurementFieldFormat(unit="kJ/mol", decimals=1, scale=EV_TO_KJ_PER_MOL),
    "electron_affinity": MeasurementFieldFormat(unit="kJ/mol", decimals=1, scale=EV_TO_KJ_PER_MOL),
    "melting_point": MeasurementFieldFormat(unit="K", decimals=3),
    "boiling_point": MeasurementFieldFormat(unit="K", decimals=3),
    "density": MeasurementFieldFormat(unit="kg/m^3", decimals=5, scale=1000.0),
    "electronegativity": MeasurementFieldFormat(unit="", decimals=2),
}


def format_value(value, decimals=3, na_text="n/a"):
    """Convert a scalar value to its display string.

    Formats floats to the requested decimal precision and returns
    the na_text placeholder for None values.
    """
    if value is None:
        return na_text

    if isinstance(value, float):
        return f"{value:.{decimals}f}"

    return str(value)


def format_info_value(field_name, value, *, na_text="n/a"):
    """Format an element property for display in the info panel.

    Applies the field-specific unit conversion and decimal precision
    defined in MEASUREMENT_FIELD_FORMATS, then appends the unit suffix.
    Falls back to generic formatting for fields without a format entry.
    """
    if value is None:
        return na_text

    field_format = MEASUREMENT_FIELD_FORMATS.get(field_name)
    if field_format is None:
        return format_value(value, na_text=na_text)

    base_value = _format_numeric_value(
        value * field_format.scale,
        decimals=field_format.decimals,
        trim_trailing_zeroes=field_format.trim_trailing_zeroes,
        na_text=na_text,
    )

    if not field_format.unit:
        return base_value

    return f"{base_value} {field_format.unit}"


def _format_numeric_value(value, *, decimals, trim_trailing_zeroes, na_text):
    """Format a numeric value with optional trailing-zero removal."""
    text = format_value(value, decimals=decimals, na_text=na_text)
    if not trim_trailing_zeroes:
        return text
    return _trim_trailing_zeroes(text)


def _trim_trailing_zeroes(text):
    """Strip unnecessary trailing zeros and lone decimal points from a numeric string."""
    if "." not in text:
        return text

    trimmed = text.rstrip("0").rstrip(".")
    return "0" if trimmed in {"", "-0"} else trimmed


def subscript_chemical_formula(text):
    """Convert each digit run that follows a letter or closing paren to
    Unicode subscript characters, leaving stand-alone numbers untouched.

    Display-time only — the underlying domain objects keep storing
    plain ASCII (``"Fe2O3"``, ``"H2O"``, ``"Ca(OH)2"``) so parsers and
    formula-comparison logic don't have to grow a Unicode awareness.

    Examples:

    >>> subscript_chemical_formula("H2O")
    'H₂O'
    >>> subscript_chemical_formula("Fe2(SO4)3")
    'Fe₂(SO₄)₃'
    >>> subscript_chemical_formula("CuSO4·5H2O")
    'CuSO₄·5H₂O'
    >>> subscript_chemical_formula("2 Fe + 3 O2 -> Fe2O3")
    '2 Fe + 3 O₂ -> Fe₂O₃'

    Standalone leading numbers (stoichiometric coefficients separated
    from the element by a space) stay plain; hydrate counts like the
    ``5`` in ``CuSO4·5H2O`` also stay plain because they're preceded
    by ``·`` (or ``.``), not a letter or closing paren.
    """
    if not text:
        return text

    def _replace(match):
        prefix, digits = match.group(1), match.group(2)
        subbed = "".join(_SUBSCRIPT_DIGITS[int(d)] for d in digits)
        return prefix + subbed

    return _FORMULA_DIGIT_PATTERN.sub(_replace, text)
