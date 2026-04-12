from dataclasses import dataclass


EV_TO_KJ_PER_MOL = 96.48533212331002


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
