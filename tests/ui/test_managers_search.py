"""Tests for SearchManager."""

import unittest

from src.services.data_loader import load_elements
from src.ui.managers.search_manager import SearchManager


class TestSearchManager(unittest.TestCase):
    """Test suite for SearchManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.elements = load_elements()
        self.manager = SearchManager(self.elements)

    def test_search_by_name(self):
        """Test searching elements by name."""
        matches = self.manager.search("hydro")
        self.assertIn(1, matches, "Should find Hydrogen by partial name 'hydro'")

    def test_search_by_symbol(self):
        """Test searching elements by symbol."""
        matches = self.manager.search("H")
        self.assertIn(1, matches, "Should find H (Hydrogen)")

    def test_search_by_atomic_number(self):
        """Test searching elements by atomic number."""
        matches = self.manager.search("1")
        self.assertIn(1, matches, "Should find element 1")

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        matches_lower = self.manager.search("carbon")
        matches_upper = self.manager.search("CARBON")
        self.assertEqual(matches_lower, matches_upper, "Search should be case-insensitive")
        self.assertIn(6, matches_lower, "Should find Carbon")

    def test_empty_search_returns_no_matches(self):
        """Test that empty search clears matches."""
        self.manager.search("H")  # Set up some matches
        self.manager.search("")   # Clear with empty query
        self.assertEqual(len(self.manager.matches), 0, "Empty search should clear matches")

    def test_clear_search(self):
        """Test clearing search."""
        self.manager.search("hydro")
        self.assertTrue(len(self.manager.matches) > 0, "Should have matches")
        self.manager.clear_search()
        self.assertEqual(len(self.manager.matches), 0, "Clear should remove all matches")
        self.assertEqual(self.manager.current_query, "", "Query should be empty after clear")

    def test_multiple_results(self):
        """Test search returning multiple results."""
        matches = self.manager.search("ine")  # Should match multiple elements
        self.assertGreater(len(matches), 1, "Should find multiple elements with 'ine'")


if __name__ == "__main__":
    unittest.main()
