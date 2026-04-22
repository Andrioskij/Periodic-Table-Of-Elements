"""Manager for binary compound builder operations."""

import logging
from dataclasses import dataclass, field

from src.domain.compound_builder import build_binary_formula

_logger = logging.getLogger(__name__)


@dataclass
class CompoundBuilderState:
    """Internal state for compound builder."""

    element_a_id: int | None = None
    element_a_oxidation: int | None = None
    element_b_id: int | None = None
    element_b_oxidation: int | None = None


@dataclass
class CompoundBuilderManager:
    """Manages state and operations for the binary compound builder.

    Maintains selections of two elements and their oxidation states,
    and provides methods to validate and build binary chemical formulas.
    """

    elements: list

    _state: CompoundBuilderState = field(default_factory=CompoundBuilderState)
    _element_index: dict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._element_index = {
            element["atomic_number"]: element for element in self.elements
        }

    def set_element_a(self, element_id: int, oxidation: int) -> bool:
        """Set the first element and its oxidation state.

        Args:
            element_id: Atomic number of the element
            oxidation: Oxidation state (positive or negative integer)

        Returns:
            True if valid, False otherwise
        """
        if not self._is_valid_element(element_id):
            return False
        if not self._is_valid_oxidation(oxidation):
            return False

        self._state.element_a_id = element_id
        self._state.element_a_oxidation = oxidation
        return True

    def set_element_b(self, element_id: int, oxidation: int) -> bool:
        """Set the second element and its oxidation state.

        Args:
            element_id: Atomic number of the element
            oxidation: Oxidation state (positive or negative integer)

        Returns:
            True if valid, False otherwise
        """
        if not self._is_valid_element(element_id):
            return False
        if not self._is_valid_oxidation(oxidation):
            return False

        self._state.element_b_id = element_id
        self._state.element_b_oxidation = oxidation
        return True

    def build_compound(self) -> str | None:
        """Build the chemical formula if state is valid.

        Returns:
            Formula string (e.g., 'NaCl') or None if incomplete/invalid
        """
        if not self._can_build():
            return None

        element_a = self._get_element(self._state.element_a_id)
        element_b = self._get_element(self._state.element_b_id)

        if not element_a or not element_b:
            return None

        symbol_a = element_a.get("symbol", "?")
        symbol_b = element_b.get("symbol", "?")

        try:
            formula = build_binary_formula(
                symbol_a,
                self._state.element_a_oxidation,
                symbol_b,
                self._state.element_b_oxidation,
            )
            return formula
        except (ValueError, ArithmeticError):
            _logger.exception(
                "build_binary_formula failed for %s/%s", symbol_a, symbol_b
            )
            return None

    def reset(self) -> None:
        """Clear all builder state."""
        self._state = CompoundBuilderState()

    def _can_build(self) -> bool:
        """Check if the builder is complete and valid for building."""
        # Must have both elements and oxidation states
        if None in {
            self._state.element_a_id,
            self._state.element_a_oxidation,
            self._state.element_b_id,
            self._state.element_b_oxidation,
        }:
            return False

        # Elements must be different
        if self._state.element_a_id == self._state.element_b_id:
            return False

        # Oxidation states must have opposite signs
        ox_a = self._state.element_a_oxidation
        ox_b = self._state.element_b_oxidation
        if (ox_a > 0 and ox_b > 0) or (ox_a < 0 and ox_b < 0):
            return False

        return True

    def _is_valid_element(self, element_id: int) -> bool:
        """Check if element ID is valid."""
        return self._get_element(element_id) is not None

    def _is_valid_oxidation(self, oxidation: int) -> bool:
        """Check if oxidation state is valid (non-zero integer)."""
        return isinstance(oxidation, int) and oxidation != 0

    def _get_element(self, element_id: int | None) -> dict | None:
        """Return the element record for the given atomic number, or None."""
        if element_id is None:
            return None
        return self._element_index.get(element_id)

    @property
    def state(self) -> CompoundBuilderState:
        """Return the current builder state."""
        return self._state
