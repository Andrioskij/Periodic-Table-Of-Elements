"""Tests for AppContext."""

import unittest

from src.services.data_loader import load_elements, load_nomenclature_data
from src.services.settings_service import SettingsService
from src.ui.context import AppContext


class TestAppContext(unittest.TestCase):
    """Test suite for AppContext."""

    def setUp(self):
        """Set up test fixtures."""
        self.elements = load_elements()
        self.nomenclature_data = load_nomenclature_data()
        self.settings_service = SettingsService()

    def test_app_context_creation(self):
        """Test creating AppContext with factory method."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        self.assertIsNotNone(context)

    def test_app_context_contains_all_managers(self):
        """Test that AppContext initializes all managers."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        self.assertIsNotNone(context.search_manager)
        self.assertIsNotNone(context.trend_manager)
        self.assertIsNotNone(context.compound_builder_manager)

    def test_app_context_preserves_data(self):
        """Test that AppContext preserves passed data."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        self.assertEqual(len(context.elements), len(self.elements))
        self.assertIsNotNone(context.nomenclature_data)
        self.assertIs(context.settings_service, self.settings_service)

    def test_app_context_elements_accessible_by_manager(self):
        """Test that managers can access elements through context."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        # Test SearchManager can search
        matches = context.search_manager.search("hydro")
        self.assertIn(1, matches, "SearchManager should find Hydrogen")

    def test_app_context_trend_manager_initialization(self):
        """Test that TrendManager is properly initialized."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        # Test TrendManager has numeric ranges
        self.assertIsNotNone(context.trend_manager.numeric_ranges)
        self.assertGreater(len(context.trend_manager.numeric_ranges), 0)

    def test_app_context_compound_builder_initialization(self):
        """Test that CompoundBuilderManager is properly initialized."""
        context = AppContext.create(
            elements=self.elements,
            nomenclature_data=self.nomenclature_data,
            settings_service=self.settings_service,
        )
        # Test CompoundBuilderManager can build compounds
        context.compound_builder_manager.set_element_a(11, 1)
        context.compound_builder_manager.set_element_b(17, -1)
        formula = context.compound_builder_manager.build_compound()
        self.assertEqual(formula, "NaCl")


if __name__ == "__main__":
    unittest.main()
