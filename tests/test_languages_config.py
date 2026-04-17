import unittest

from src.config import languages as languages_config
from src.services import localization_service


class TestLanguagesConfigModule(unittest.TestCase):
    """The standalone config module must expose the three constants
    with the expected shapes and values."""

    def test_all_language_options_has_seven_entries(self):
        self.assertEqual(len(languages_config.ALL_LANGUAGE_OPTIONS), 7)

    def test_first_entry_is_english(self):
        self.assertEqual(languages_config.ALL_LANGUAGE_OPTIONS[0], ("en", "English"))

    def test_expected_codes_and_labels(self):
        expected = [
            ("en", "English"),
            ("it", "Italiano"),
            ("es", "Espa\u00f1ol"),
            ("fr", "Fran\u00e7ais"),
            ("de", "Deutsch"),
            ("zh", "\u4e2d\u6587\uff08\u7b80\u4f53\uff09"),
            ("ru", "\u0420\u0443\u0441\u0441\u043a\u0438\u0439"),
        ]
        self.assertEqual(languages_config.ALL_LANGUAGE_OPTIONS, expected)

    def test_visible_language_codes_is_tuple(self):
        self.assertIsInstance(languages_config.VISIBLE_LANGUAGE_CODES, tuple)
        self.assertEqual(
            languages_config.VISIBLE_LANGUAGE_CODES,
            tuple(code for code, _ in languages_config.ALL_LANGUAGE_OPTIONS),
        )

    def test_language_options_matches_visible_subset(self):
        filtered = [
            (code, label)
            for code, label in languages_config.ALL_LANGUAGE_OPTIONS
            if code in languages_config.VISIBLE_LANGUAGE_CODES
        ]
        self.assertEqual(languages_config.LANGUAGE_OPTIONS, filtered)

    def test_public_api_declared(self):
        self.assertEqual(
            set(languages_config.__all__),
            {"ALL_LANGUAGE_OPTIONS", "VISIBLE_LANGUAGE_CODES", "LANGUAGE_OPTIONS"},
        )


class TestLocalizationServiceReexport(unittest.TestCase):
    """Backward-compatible re-export: consumers that still import from
    localization_service must see the exact same objects as the new module."""

    def test_all_language_options_is_same_object(self):
        self.assertIs(
            localization_service.ALL_LANGUAGE_OPTIONS,
            languages_config.ALL_LANGUAGE_OPTIONS,
        )

    def test_visible_language_codes_is_same_object(self):
        self.assertIs(
            localization_service.VISIBLE_LANGUAGE_CODES,
            languages_config.VISIBLE_LANGUAGE_CODES,
        )

    def test_language_options_is_same_object(self):
        self.assertIs(
            localization_service.LANGUAGE_OPTIONS,
            languages_config.LANGUAGE_OPTIONS,
        )

    def test_constants_still_in_public_api(self):
        self.assertIn("ALL_LANGUAGE_OPTIONS", localization_service.__all__)
        self.assertIn("VISIBLE_LANGUAGE_CODES", localization_service.__all__)
        self.assertIn("LANGUAGE_OPTIONS", localization_service.__all__)


class TestSettingsServiceUsesConfigModule(unittest.TestCase):
    """settings_service must now depend on src.config.languages directly,
    not on the localization_service re-export."""

    def test_valid_languages_matches_config_codes(self):
        from src.services.settings_service import VALID_LANGUAGES

        self.assertEqual(
            VALID_LANGUAGES,
            {code for code, _ in languages_config.LANGUAGE_OPTIONS},
        )


if __name__ == "__main__":
    unittest.main()
