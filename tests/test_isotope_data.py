"""Tests for src.services.isotope_data."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.services import isotope_data
from src.services.isotope_data import get_isotopes


class TestGetIsotopes(unittest.TestCase):
    def test_known_symbol_returns_list(self):
        result = get_isotopes("H")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_unknown_symbol_returns_empty_list(self):
        self.assertEqual(get_isotopes("Xx"), [])

    def test_empty_symbol_returns_empty_list(self):
        self.assertEqual(get_isotopes(""), [])

    def test_case_sensitive(self):
        # Symbol lookup is case-sensitive by design; "h" should not match "H"
        self.assertEqual(get_isotopes("h"), [])

    def test_returns_copy_not_reference(self):
        result = get_isotopes("H")
        result.append({"mass_number": 999, "name": "Fake"})
        self.assertNotIn(
            {"mass_number": 999, "name": "Fake"},
            get_isotopes("H"),
        )


class TestLoadIsotopeData(unittest.TestCase):
    def test_file_not_found_returns_empty_dict(self):
        with patch.object(isotope_data, "_DATA_PATH", Path("/nonexistent.json")):
            self.assertEqual(isotope_data._load_isotope_data(), {})

    def test_corrupted_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{not valid json")
            tmp_path = Path(f.name)
        try:
            with patch.object(isotope_data, "_DATA_PATH", tmp_path):
                with self.assertRaises(json.JSONDecodeError):
                    isotope_data._load_isotope_data()
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
