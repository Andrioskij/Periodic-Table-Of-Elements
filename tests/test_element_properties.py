"""Tests for src.services.element_properties aggregator."""

import unittest

from src.services.element_properties import get_element_full_info


class TestGetElementFullInfo(unittest.TestCase):
    def test_known_element_has_both_sections(self):
        info = get_element_full_info("H")
        self.assertIn("isotopes", info)
        self.assertIn("industrial_uses", info)
        self.assertIsInstance(info["isotopes"], list)
        self.assertIsInstance(info["industrial_uses"], list)

    def test_unknown_element_returns_empty_lists(self):
        info = get_element_full_info("Xx")
        self.assertEqual(info["isotopes"], [])
        self.assertEqual(info["industrial_uses"], [])


if __name__ == "__main__":
    unittest.main()
