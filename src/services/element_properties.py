"""
Element properties module.

Unified access to supplementary element data including isotopes and industrial uses.
Aggregates data from specialized modules for convenient lookup.
"""

from .industrial_uses import get_industrial_uses
from .isotope_data import get_isotopes

__all__ = [
    "get_isotopes",
    "get_industrial_uses",
    "get_element_full_info",
]


def get_element_full_info(symbol):
    """
    Get comprehensive supplementary data for an element.

    Args:
        symbol: Chemical symbol (e.g., 'Fe', 'Cu')

    Returns:
        Dictionary with keys:
        - isotopes: List of common isotopes
        - industrial_uses: List of industrial applications
    """
    return {
        "isotopes": get_isotopes(symbol),
        "industrial_uses": get_industrial_uses(symbol),
    }
