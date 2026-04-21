"""Tests for theme persistence via SettingsService."""

import os
import tempfile
import unittest

from PySide6.QtCore import QSettings

from src.services.settings_service import (
    DEFAULT_THEME,
    VALID_THEMES,
    SettingsService,
)


class TestSettingsServiceTheme(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False, encoding="utf-8"
        )
        self._tmp.close()
        self.ini_path = self._tmp.name
        self.settings = QSettings(self.ini_path, QSettings.IniFormat)
        self.service = SettingsService(qsettings=self.settings)

    def tearDown(self):
        self.settings.sync()
        del self.settings
        try:
            os.unlink(self.ini_path)
        except OSError:
            pass

    def test_default_theme_is_dark(self):
        self.assertEqual(DEFAULT_THEME, "dark")
        self.assertEqual(self.service.get_theme(), "dark")

    def test_valid_themes_contains_dark_and_light(self):
        self.assertEqual(VALID_THEMES, {"dark", "light"})

    def test_set_theme_light_persists(self):
        self.service.set_theme("light")
        self.assertEqual(self.service.get_theme(), "light")

    def test_set_theme_dark_persists(self):
        self.service.set_theme("light")
        self.service.set_theme("dark")
        self.assertEqual(self.service.get_theme(), "dark")

    def test_set_theme_invalid_is_ignored(self):
        self.service.set_theme("light")
        self.service.set_theme("solarized")
        self.assertEqual(self.service.get_theme(), "light")

    def test_set_theme_none_is_ignored(self):
        self.service.set_theme("light")
        self.service.set_theme(None)
        self.assertEqual(self.service.get_theme(), "light")

    def test_persistence_across_instances(self):
        self.service.set_theme("light")
        fresh_settings = QSettings(self.ini_path, QSettings.IniFormat)
        fresh_service = SettingsService(qsettings=fresh_settings)
        self.assertEqual(fresh_service.get_theme(), "light")

    def test_corrupted_value_returns_default(self):
        self.settings.setValue("theme", "neon")
        self.settings.sync()
        self.assertEqual(self.service.get_theme(), DEFAULT_THEME)


if __name__ == "__main__":
    unittest.main()
