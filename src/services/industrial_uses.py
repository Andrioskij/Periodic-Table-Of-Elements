"""
Industrial uses data module.

Provides common industrial and commercial applications for all elements.
Data is loaded from data/reference/industrial_uses.json and is organized
by use category and relevance.
"""

import json
import logging
from pathlib import Path

__all__ = ["get_industrial_uses", "INDUSTRIAL_USES"]

_logger = logging.getLogger(__name__)

_DATA_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "reference"
    / "industrial_uses.json"
)


def _load_industrial_uses():
    try:
        with open(_DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        _logger.warning("Industrial uses data file not found at %s", _DATA_PATH)
        return {}
    except json.JSONDecodeError:
        _logger.exception("Corrupted industrial uses JSON at %s", _DATA_PATH)
        raise


# Industrial uses data: symbol -> list of {"category": str, "use": str}
INDUSTRIAL_USES = _load_industrial_uses()


def get_industrial_uses(symbol):
    """
    Get list of industrial and commercial uses for an element.

    Args:
        symbol: Chemical symbol (e.g., 'Fe', 'Cu', 'Al')

    Returns:
        List of use dicts with keys: category, use. Empty list if element not found.
    """
    return list(INDUSTRIAL_USES.get(symbol, []))
