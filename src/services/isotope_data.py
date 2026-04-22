"""
Isotope data module.

Provides information about common stable and long-lived isotopes for all elements.
Data is loaded from data/reference/isotopes.json and includes mass number,
natural abundance (for stable isotopes), and half-life for radioactive isotopes.
"""

import json
import logging
from pathlib import Path

__all__ = ["get_isotopes", "ISOTOPE_DATA"]

_logger = logging.getLogger(__name__)

_DATA_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "reference"
    / "isotopes.json"
)


def _load_isotope_data():
    try:
        with open(_DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        _logger.warning("Isotope data file not found at %s", _DATA_PATH)
        return {}
    except json.JSONDecodeError:
        _logger.exception("Corrupted isotope JSON at %s", _DATA_PATH)
        raise


# Isotope data: symbol -> list of {"mass_number": int, "abundance": float|None,
# "half_life": str|None, "name": str}
# For stable isotopes: abundance is provided (in %)
# For radioactive isotopes: half_life is provided (e.g., "12.3 years", "8.02 days")
ISOTOPE_DATA = _load_isotope_data()


def get_isotopes(symbol):
    """
    Get list of common isotopes for an element.

    Args:
        symbol: Chemical symbol (e.g., 'H', 'C', 'U')

    Returns:
        List of isotope dicts with keys: mass_number, abundance (or None),
        half_life (or None), name. Empty list if element not found.
    """
    return list(ISOTOPE_DATA.get(symbol, []))
