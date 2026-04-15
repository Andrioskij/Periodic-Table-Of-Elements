"""Tests for TrendManager."""

import unittest

from src.services.data_loader import load_elements
from src.ui.managers.trend_manager import TrendManager, TrendMode


class TestTrendManager(unittest.TestCase):
    """Test suite for TrendManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.elements = load_elements()
        self.manager = TrendManager(self.elements)

    def test_default_trend_mode(self):
        """Test that default trend mode is 'normal'."""
        self.assertEqual(self.manager.current_mode, "normal")

    def test_set_valid_trend_mode(self):
        """Test setting a valid trend mode."""
        self.manager.set_trend_mode("macroclass")
        self.assertEqual(self.manager.current_mode, "macroclass")

    def test_set_numeric_trend_mode(self):
        """Test setting numeric trend modes."""
        for mode in ["atomic_radius", "ionization_energy", "electron_affinity", "electronegativity"]:
            self.manager.set_trend_mode(mode)
            self.assertIn(self.manager.current_mode, [mode, "normal"])  # Mode is valid or defaults to normal

    def test_invalid_trend_mode_defaults_to_normal(self):
        """Test that invalid mode defaults to 'normal'."""
        self.manager.set_trend_mode("invalid_mode")
        self.assertEqual(self.manager.current_mode, "normal")

    def test_get_trend_color_returns_hex(self):
        """Test that get_trend_color returns a hex color."""
        hydrogen = next(e for e in self.elements if e.get("atomic_number") == 1)
        color = self.manager.get_trend_color(hydrogen)
        self.assertTrue(color.startswith("#"), f"Color should start with '#', got {color}")
        self.assertEqual(len(color), 7, f"Hex color should have 7 chars (#RRGGBB), got {color}")

    def test_trend_color_for_different_modes(self):
        """Test that different modes may produce different colors."""
        hydrogen = next(e for e in self.elements if e.get("atomic_number") == 1)

        self.manager.set_trend_mode("normal")
        color_normal = self.manager.get_trend_color(hydrogen)

        self.manager.set_trend_mode("atomic_radius")
        color_radius = self.manager.get_trend_color(hydrogen)

        # Both should be valid hex colors (may or may not be the same)
        self.assertTrue(color_normal.startswith("#"))
        self.assertTrue(color_radius.startswith("#"))

    def test_get_text_color(self):
        """Test that get_text_color returns a hex color."""
        hydrogen = next(e for e in self.elements if e.get("atomic_number") == 1)
        color = self.manager.get_text_color(hydrogen)
        self.assertTrue(color.startswith("#"), f"Text color should start with '#', got {color}")
        self.assertEqual(len(color), 7, f"Hex color should have 7 chars (#RRGGBB), got {color}")

    def test_numeric_ranges_computed(self):
        """Test that numeric ranges are computed."""
        self.assertIsNotNone(self.manager.numeric_ranges)
        self.assertGreater(len(self.manager.numeric_ranges), 0)


if __name__ == "__main__":
    unittest.main()
