"""Regression tests for lazy loading of localization files.

Bootstrap of `src.services.localization_service` loads only English; all other
languages are loaded on demand via `_ensure_language_loaded()`. These tests
verify that behavior by reloading the module in isolation for each test case.
"""

import importlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import src.services.localization_service as loc


def _reload_localization_service():
    """Re-execute the module body so module-level dicts reset to empty and the
    bootstrap runs fresh. Returns the reloaded module reference."""
    return importlib.reload(loc)


class TestLazyLoadingBootstrap(unittest.TestCase):
    """Only English should be loaded when the module is first imported."""

    def setUp(self):
        _reload_localization_service()

    def tearDown(self):
        _reload_localization_service()

    def test_only_english_loaded_after_import(self):
        self.assertEqual(set(loc.UI_TEXTS.keys()), {"en"})
        self.assertEqual(set(loc.LOCALIZED_CATEGORY_TEXTS.keys()), {"en"})
        self.assertEqual(set(loc.LOCALIZED_STANDARD_STATE_TEXTS.keys()), {"en"})
        self.assertEqual(set(loc.LOCALIZED_MACRO_CLASS_TEXTS.keys()), {"en"})

    def test_other_languages_not_loaded_at_startup(self):
        for code in ("it", "es", "fr", "de", "zh", "ru"):
            self.assertNotIn(
                code, loc.UI_TEXTS, f"{code!r} must not be loaded at startup"
            )


class TestLazyLoadingOnLookup(unittest.TestCase):
    """Lookup functions must trigger loading of the requested language."""

    def setUp(self):
        _reload_localization_service()

    def tearDown(self):
        _reload_localization_service()

    def test_tr_triggers_italian_load(self):
        self.assertNotIn("it", loc.UI_TEXTS)
        result = loc.tr("it", "title")
        self.assertIn("it", loc.UI_TEXTS)
        self.assertTrue(result)

    def test_get_localized_category_text_triggers_chinese_load(self):
        self.assertNotIn("zh", loc.LOCALIZED_CATEGORY_TEXTS)
        loc.get_localized_category_text("metal", "zh")
        self.assertIn("zh", loc.LOCALIZED_CATEGORY_TEXTS)

    def test_audit_language_readiness_triggers_load(self):
        self.assertNotIn("ru", loc.UI_TEXTS)
        loc.audit_language_readiness({"meta": {}, "elements": {}, "common_compounds": {}}, "ru")
        self.assertIn("ru", loc.UI_TEXTS)


class TestLazyLoadEquivalentToEagerLoad(unittest.TestCase):
    """Loading all seven languages one-by-one via `_ensure_language_loaded`
    must produce the same dictionaries as the legacy `_load_all_languages`."""

    def test_incremental_load_matches_eager_load(self):
        _reload_localization_service()
        loc._load_all_languages()
        eager_ui = dict(loc.UI_TEXTS)
        eager_cat = dict(loc.LOCALIZED_CATEGORY_TEXTS)
        eager_state = dict(loc.LOCALIZED_STANDARD_STATE_TEXTS)
        eager_macro = dict(loc.LOCALIZED_MACRO_CLASS_TEXTS)

        _reload_localization_service()
        for code, _label in loc.ALL_LANGUAGE_OPTIONS:
            loc._ensure_language_loaded(code)

        self.assertEqual(loc.UI_TEXTS, eager_ui)
        self.assertEqual(loc.LOCALIZED_CATEGORY_TEXTS, eager_cat)
        self.assertEqual(loc.LOCALIZED_STANDARD_STATE_TEXTS, eager_state)
        self.assertEqual(loc.LOCALIZED_MACRO_CLASS_TEXTS, eager_macro)


class TestMissingEnglishIsFatal(unittest.TestCase):
    """If `en.json` is missing, the initial load must raise FileNotFoundError.
    The module bootstrap wraps this same call and re-raises, so a missing
    English fallback fails the import fast."""

    def tearDown(self):
        _reload_localization_service()

    def test_missing_english_file_raises_filenotfound(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(loc, "_get_localization_data_dir", return_value=Path(tmpdir)):
                with self.assertRaises(FileNotFoundError):
                    loc._load_language_from_json("en")


if __name__ == "__main__":
    unittest.main()
