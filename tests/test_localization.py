import unittest

from src.services.localization_service import (
    ALL_LANGUAGE_OPTIONS,
    UI_TEXTS,
    tr,
)


class TestTranslation(unittest.TestCase):

    def test_english_title(self):
        self.assertEqual(tr("en", "title"), "PERIODIC TABLE")

    def test_missing_key_returns_key(self):
        result = tr("en", "nonexistent_key_xyz")
        self.assertEqual(result, "nonexistent_key_xyz")

    def test_substitution(self):
        result = tr("en", "search_found", name="Iron", symbol="Fe")
        self.assertIn("Iron", result)
        self.assertIn("Fe", result)

    def test_all_languages_have_title(self):
        for code, _ in ALL_LANGUAGE_OPTIONS:
            if code in UI_TEXTS:
                self.assertIn("title", UI_TEXTS[code])


class TestLanguageOptions(unittest.TestCase):

    def test_english_is_first(self):
        self.assertEqual(ALL_LANGUAGE_OPTIONS[0][0], "en")

    def test_seven_languages(self):
        self.assertEqual(len(ALL_LANGUAGE_OPTIONS), 7)

    def test_each_option_has_code_and_label(self):
        for code, label in ALL_LANGUAGE_OPTIONS:
            self.assertIsInstance(code, str)
            self.assertIsInstance(label, str)
            self.assertGreater(len(code), 0)


class TestUITextsCompleteness(unittest.TestCase):

    def test_english_has_core_keys(self):
        en = UI_TEXTS["en"]
        core_keys = [
            "title", "search_placeholder", "search_button",
            "formula_label", "stock_name", "traditional_name",
            "info_prompt", "diagram_prompt", "compound_prompt",
        ]
        for key in core_keys:
            self.assertIn(key, en, f"Missing English key: {key}")

    def test_all_languages_cover_english_keys(self):
        en_keys = set(UI_TEXTS["en"].keys())
        for code, _ in ALL_LANGUAGE_OPTIONS:
            if code == "en" or code not in UI_TEXTS:
                continue
            lang_keys = set(UI_TEXTS[code].keys())
            missing = en_keys - lang_keys
            self.assertEqual(missing, set(), f"{code} is missing keys: {missing}")


if __name__ == "__main__":
    unittest.main()
