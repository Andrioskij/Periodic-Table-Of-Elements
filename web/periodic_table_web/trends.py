"""Color computation for the periodic-table trend overlays.

The browser version mirrors the desktop trend behavior: each numeric
trend gets a two-color gradient driven by min/max across the dataset.
Categorical and metallic/nonmetallic modes use fixed swatches.

Pure Python — no numpy, no Reflex imports — so the helpers are easy to
unit-test and import from both the State layer and ad-hoc scripts.
"""

from __future__ import annotations

from collections.abc import Iterable

from periodic_table_web.theme import (
    DEFAULT_CATEGORY_COLOR,
    category_color,
)

NULL_TREND_COLOR = "#3a3a4a"

GRADIENT_ENDPOINTS: dict[str, tuple[str, str]] = {
    "radius": ("#1f3b73", "#9ec5fe"),
    "ionization": ("#1c7c54", "#e3431a"),
    "electron_affinity": ("#1c4f7c", "#f0b619"),
    "electronegativity": ("#2359a8", "#ffd60a"),
}

NUMERIC_TREND_FIELDS: dict[str, str] = {
    "radius": "atomic_radius",
    "ionization": "ionization_energy",
    "electron_affinity": "electron_affinity",
    "electronegativity": "electronegativity",
}

METAL_CATEGORIES = frozenset(
    {
        "alkali metal",
        "alkaline earth metal",
        "transition metal",
        "post-transition metal",
        "lanthanide",
        "lanthanoid",
        "actinide",
        "actinoid",
    }
)
METALLIC_COLOR = "#56CCF2"
NONMETALLIC_COLOR = "#FFD60A"
METALLOID_COLOR = "#B07AA1"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    h = color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lerp_color(c1: str, c2: str, t: float) -> str:
    """Blend two hex colors linearly (t=0 → c1, t=1 → c2)."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def compute_ranges(elements: Iterable[dict]) -> dict[str, tuple[float, float]]:
    """Return (min, max) per numeric trend field, ignoring None values."""
    ranges: dict[str, tuple[float, float]] = {}
    elements = list(elements)
    for mode, field in NUMERIC_TREND_FIELDS.items():
        values = [e[field] for e in elements if e.get(field) is not None]
        if values:
            ranges[mode] = (min(values), max(values))
    return ranges


def _metal_color(category: str | None) -> str:
    if not category:
        return NULL_TREND_COLOR
    cat = category.lower()
    if cat == "metalloid":
        return METALLOID_COLOR
    return METALLIC_COLOR if cat in METAL_CATEGORIES else NONMETALLIC_COLOR


def _nonmetal_color(category: str | None) -> str:
    if not category:
        return NULL_TREND_COLOR
    cat = category.lower()
    if cat == "metalloid":
        return METALLOID_COLOR
    return NONMETALLIC_COLOR if cat in METAL_CATEGORIES else METALLIC_COLOR


def trend_color(
    element: dict,
    mode: str,
    ranges: dict[str, tuple[float, float]] | None = None,
) -> str:
    """Background color for an element cell under the given trend mode."""
    if mode == "category" or mode is None:
        return category_color(element.get("category"))
    if mode == "metallic":
        return _metal_color(element.get("category"))
    if mode == "nonmetallic":
        return _nonmetal_color(element.get("category"))

    field = NUMERIC_TREND_FIELDS.get(mode)
    if field is None:
        return DEFAULT_CATEGORY_COLOR

    value = element.get(field)
    if value is None:
        return NULL_TREND_COLOR

    bounds = (ranges or {}).get(mode)
    if bounds is None or bounds[0] == bounds[1]:
        return lerp_color(*GRADIENT_ENDPOINTS[mode], 0.5)

    lo, hi = bounds
    t = (float(value) - lo) / (hi - lo)
    return lerp_color(*GRADIENT_ENDPOINTS[mode], t)
