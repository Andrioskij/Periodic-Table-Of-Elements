import json
import os
import tempfile
import unittest

from src.services.data_loader import (
    ELEMENTS_DATA_PATH,
    NOMENCLATURE_DATA_PATH,
    load_elements,
    load_json_file,
    load_nomenclature_data,
)


class TestLoadJsonFile(unittest.TestCase):

    def test_loads_valid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"key": "value"}, f)
            path = f.name
        try:
            result = load_json_file(path)
            self.assertEqual(result, {"key": "value"})
        finally:
            os.unlink(path)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_json_file("/nonexistent/path.json")

    def test_allow_missing_returns_default(self):
        result = load_json_file("/nonexistent/path.json", allow_missing=True)
        self.assertEqual(result, {})

    def test_allow_missing_custom_default(self):
        result = load_json_file("/nonexistent/path.json", allow_missing=True, default=[])
        self.assertEqual(result, [])

    def test_invalid_json_raises_value_error(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            path = f.name
        try:
            with self.assertRaises(ValueError):
                load_json_file(path)
        finally:
            os.unlink(path)


class TestLoadElements(unittest.TestCase):

    def test_returns_list(self):
        elements = load_elements()
        self.assertIsInstance(elements, list)

    def test_has_118_elements(self):
        elements = load_elements()
        self.assertEqual(len(elements), 118)

    def test_first_element_is_hydrogen(self):
        elements = load_elements()
        self.assertEqual(elements[0]["symbol"], "H")
        self.assertEqual(elements[0]["atomic_number"], 1)

    def test_elements_have_required_fields(self):
        elements = load_elements()
        required = {"atomic_number", "symbol", "name", "period", "group"}
        for el in elements:
            for field in required:
                self.assertIn(field, el, f"{el.get('symbol', '?')} missing '{field}'")

    def test_atomic_numbers_are_unique(self):
        elements = load_elements()
        numbers = [el["atomic_number"] for el in elements]
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_data_file_exists(self):
        self.assertTrue(ELEMENTS_DATA_PATH.exists())


class TestLoadNomenclatureData(unittest.TestCase):

    def test_returns_dict(self):
        data = load_nomenclature_data()
        self.assertIsInstance(data, dict)

    def test_has_elements_section(self):
        data = load_nomenclature_data()
        if data:
            self.assertIn("elements", data)

    def test_data_file_exists(self):
        self.assertTrue(NOMENCLATURE_DATA_PATH.exists())


if __name__ == "__main__":
    unittest.main()
