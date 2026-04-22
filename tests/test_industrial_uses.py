"""Tests for src.services.industrial_uses."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.services import industrial_uses
from src.services.industrial_uses import get_industrial_uses


class TestGetIndustrialUses(unittest.TestCase):
    def test_known_symbol_returns_list(self):
        result = get_industrial_uses("Fe")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_unknown_symbol_returns_empty_list(self):
        self.assertEqual(get_industrial_uses("Xx"), [])

    def test_empty_symbol_returns_empty_list(self):
        self.assertEqual(get_industrial_uses(""), [])

    def test_case_sensitive(self):
        # Symbol lookup is case-sensitive by design; "fe" should not match "Fe"
        self.assertEqual(get_industrial_uses("fe"), [])

    def test_returns_copy_not_reference(self):
        result = get_industrial_uses("Fe")
        result.append({"category": "fake", "use": "fake"})
        self.assertNotIn(
            {"category": "fake", "use": "fake"},
            get_industrial_uses("Fe"),
        )


class TestLoadIndustrialUses(unittest.TestCase):
    def test_file_not_found_returns_empty_dict(self):
        with patch.object(industrial_uses, "_DATA_PATH", Path("/nonexistent.json")):
            self.assertEqual(industrial_uses._load_industrial_uses(), {})

    def test_corrupted_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{not valid json")
            tmp_path = Path(f.name)
        try:
            with patch.object(industrial_uses, "_DATA_PATH", tmp_path):
                with self.assertRaises(json.JSONDecodeError):
                    industrial_uses._load_industrial_uses()
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
