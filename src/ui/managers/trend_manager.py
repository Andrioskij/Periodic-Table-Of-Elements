"""Manager for trend visualization mode and color calculations."""

from dataclasses import dataclass
from enum import Enum

from src.config.static_data import NUMERIC_TREND_PROPERTIES
from src.domain.trends import (
    compute_numeric_ranges,
    get_macro_class,
    get_macro_class_color,
)
from src.ui.styles import get_current_button_colors


class TrendMode(str, Enum):
    """Enumeration of available trend visualization modes."""

    NORMAL = "normal"
    MACROCLASS = "macroclass"
    RADIUS = "atomic_radius"
    IONIZATION = "ionization_energy"
    AFFINITY = "electron_affinity"
    ELECTRONEGATIVITY = "electronegativity"
    METALLIC = "metallic"
    NONMETALLIC = "nonmetallic"


@dataclass
class TrendManager:
    """Manages trend visualization mode and color calculations for elements.

    Maintains the current trend mode and provides methods to compute
    colors for elements based on the active trend visualization.
    """

    elements: list

    _current_mode: str = "normal"
    _numeric_ranges: dict = None

    def __post_init__(self):
        """Initialize numeric ranges after dataclass creation."""
        if self._numeric_ranges is None:
            self._numeric_ranges = compute_numeric_ranges(self.elements)

    def set_trend_mode(self, mode: str) -> None:
        """Set the active trend visualization mode.

        Args:
            mode: Mode name (e.g., 'normal', 'macroclass', 'ionization_energy')
        """
        # Validate mode exists
        valid_modes = list(NUMERIC_TREND_PROPERTIES.keys()) + [
            "normal", "macroclass", "metallic", "nonmetallic"
        ]
        if mode in valid_modes:
            self._current_mode = mode
        else:
            self._current_mode = "normal"

    def get_trend_color(self, element: dict) -> str:
        """Get the background color for an element based on current trend mode.

        Args:
            element: Element record dictionary

        Returns:
            Hex color string (e.g., '#FF0000')
        """
        background_color, _ = get_current_button_colors(
            element,
            trend_mode=self._current_mode,
            numeric_ranges=self._numeric_ranges,
            get_macro_class=get_macro_class,
            get_macro_class_color=get_macro_class_color,
        )
        return background_color

    def get_text_color(self, element: dict) -> str:
        """Get the text color for an element based on current trend mode.

        Args:
            element: Element record dictionary

        Returns:
            Hex color string (e.g., '#FFFFFF' or '#111111')
        """
        _, text_color = get_current_button_colors(
            element,
            trend_mode=self._current_mode,
            numeric_ranges=self._numeric_ranges,
            get_macro_class=get_macro_class,
            get_macro_class_color=get_macro_class_color,
        )
        return text_color

    @property
    def current_mode(self) -> str:
        """Return the current trend visualization mode."""
        return self._current_mode

    @property
    def numeric_ranges(self) -> dict:
        """Return the computed numeric ranges for trend properties."""
        return self._numeric_ranges
