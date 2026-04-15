"""Tests for CompoundBuilderManager."""

import unittest

from src.services.data_loader import load_elements
from src.ui.managers.compound_builder_manager import CompoundBuilderManager


class TestCompoundBuilderManager(unittest.TestCase):
    """Test suite for CompoundBuilderManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.elements = load_elements()
        self.manager = CompoundBuilderManager(self.elements)

    def test_initial_state_is_empty(self):
        """Test that initial state has no elements or oxidations set."""
        self.assertIsNone(self.manager.state.element_a_id)
        self.assertIsNone(self.manager.state.element_a_oxidation)
        self.assertIsNone(self.manager.state.element_b_id)
        self.assertIsNone(self.manager.state.element_b_oxidation)

    def test_set_element_a_valid(self):
        """Test setting first element with valid oxidation."""
        result = self.manager.set_element_a(11, 1)  # Na +1
        self.assertTrue(result)
        self.assertEqual(self.manager.state.element_a_id, 11)
        self.assertEqual(self.manager.state.element_a_oxidation, 1)

    def test_set_element_b_valid(self):
        """Test setting second element with valid oxidation."""
        result = self.manager.set_element_b(17, -1)  # Cl -1
        self.assertTrue(result)
        self.assertEqual(self.manager.state.element_b_id, 17)
        self.assertEqual(self.manager.state.element_b_oxidation, -1)

    def test_set_invalid_element_id(self):
        """Test that setting invalid element ID returns False."""
        result = self.manager.set_element_a(999, 1)  # Non-existent element
        self.assertFalse(result)
        self.assertIsNone(self.manager.state.element_a_id)

    def test_set_zero_oxidation_returns_false(self):
        """Test that zero oxidation is rejected."""
        result = self.manager.set_element_a(11, 0)
        self.assertFalse(result)
        self.assertIsNone(self.manager.state.element_a_oxidation)

    def test_build_compound_valid(self):
        """Test building a valid binary compound."""
        self.manager.set_element_a(11, 1)  # Na +1
        self.manager.set_element_b(17, -1)  # Cl -1
        formula = self.manager.build_compound()
        self.assertEqual(formula, "NaCl")

    def test_build_compound_incomplete_returns_none(self):
        """Test that incomplete builder returns None."""
        self.manager.set_element_a(11, 1)  # Only set first element
        formula = self.manager.build_compound()
        self.assertIsNone(formula)

    def test_build_compound_same_elements_returns_none(self):
        """Test that same element for both returns None."""
        self.manager.set_element_a(11, 1)
        self.manager.set_element_b(11, -1)  # Same element
        formula = self.manager.build_compound()
        self.assertIsNone(formula)

    def test_build_compound_same_sign_oxidations_returns_none(self):
        """Test that same-sign oxidations return None."""
        self.manager.set_element_a(11, 1)
        self.manager.set_element_b(19, 1)  # K +1 (same sign as Na)
        formula = self.manager.build_compound()
        self.assertIsNone(formula)

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        self.manager.set_element_a(11, 1)
        self.manager.set_element_b(17, -1)
        self.manager.reset()
        self.assertIsNone(self.manager.state.element_a_id)
        self.assertIsNone(self.manager.state.element_b_id)

    def test_multiple_oxidation_states(self):
        """Test compounds with different oxidation states."""
        test_cases = [
            (11, 1, 8, -2),    # Na+1, O-2 -> Na2O
            (12, 2, 8, -2),    # Mg+2, O-2 -> MgO
            (13, 3, 8, -2),    # Al+3, O-2 -> Al2O3
        ]
        for a_id, a_ox, b_id, b_ox in test_cases:
            self.manager.reset()
            self.manager.set_element_a(a_id, a_ox)
            self.manager.set_element_b(b_id, b_ox)
            formula = self.manager.build_compound()
            self.assertIsNotNone(formula, f"Failed for {a_id}({a_ox}) and {b_id}({b_ox})")


if __name__ == "__main__":
    unittest.main()
