from src.config.static_data import NUMERIC_TREND_PROPERTIES


METAL_CATEGORIES = {
    "alkali metal",
    "alkaline earth metal",
    "transition metal",
    "post-transition metal",
    "lanthanide",
    "lanthanoid",
    "actinide",
    "actinoid",
}
SEMIMETAL_CATEGORIES = {"metalloid"}
NONMETAL_CATEGORIES = {"nonmetal", "halogen", "noble gas"}
MACRO_CLASS_COLORS = {
    "Metal": "#4E79A7",
    "Metalloid": "#B07AA1",
    "Nonmetal": "#EDC948",
}


def compute_numeric_ranges(elements, numeric_trend_properties=NUMERIC_TREND_PROPERTIES):
    """Calculate the min/max range for each numeric trend property.

    Iterates over all elements and collects valid numeric values for
    every trend mode (electronegativity, atomic radius, etc.).
    Returns a dictionary mapping each mode to a (min, max) tuple,
    used to normalize color scales in the trend overlay.
    """
    ranges = {}
    for mode, (_, field_name) in numeric_trend_properties.items():
        values = [
            element.get(field_name)
            for element in elements
            if isinstance(element.get(field_name), (int, float))
        ]
        ranges[mode] = (min(values), max(values)) if values else (0, 1)
    return ranges


def get_macro_class(category, traditional_na="n/a"):
    """Classify an element into a macro-level group: Metal, Metalloid, or Nonmetal.

    Maps the detailed PubChem category string (e.g. 'alkali metal',
    'halogen') to one of three broad classes. Returns the fallback
    placeholder for unknown or missing categories.
    """
    category = (category or "").lower()

    if category in METAL_CATEGORIES:
        return "Metal"
    if category in SEMIMETAL_CATEGORIES:
        return "Metalloid"
    if category in NONMETAL_CATEGORIES:
        return "Nonmetal"
    return traditional_na


def get_macro_class_color(macro_class):
    """Return the hex color code associated with a macro class.

    Used by the trend overlay to paint element buttons when the
    'macroclass' visualization mode is active. Defaults to grey
    for unrecognized classes.
    """
    return MACRO_CLASS_COLORS.get(macro_class, "#7A7A7A")
