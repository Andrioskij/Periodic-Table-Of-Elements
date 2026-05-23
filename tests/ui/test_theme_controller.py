"""Unit tests for ThemeController.

Pure-Python tests (no Qt), exercising the toggle math, persistence
side effect, and the two presentation helpers that compute the
theme toggle button's icon and tooltip. Complements
test_theme_integration.py, which covers the wider round-trip via
the real MainWindow.
"""

import unittest

from src.ui.controllers.theme_controller import VALID_THEMES, ThemeController


class _FakeSettings:
    """Minimal duck-typed stand-in for SettingsService — records the last set."""

    def __init__(self):
        self.last_set = None

    def set_theme(self, value):
        self.last_set = value


class TestThemeController(unittest.TestCase):
    def setUp(self):
        self.settings = _FakeSettings()
        self.controller = ThemeController("dark", self.settings)

    def test_initial_state_matches_constructor_argument(self):
        self.assertEqual(self.controller.current_theme, "dark")

    def test_toggle_dark_to_light(self):
        new_theme = self.controller.toggle_and_persist()
        self.assertEqual(new_theme, "light")
        self.assertEqual(self.controller.current_theme, "light")

    def test_toggle_light_to_dark(self):
        light_controller = ThemeController("light", self.settings)
        new_theme = light_controller.toggle_and_persist()
        self.assertEqual(new_theme, "dark")
        self.assertEqual(light_controller.current_theme, "dark")

    def test_toggle_persists_via_settings_service(self):
        self.controller.toggle_and_persist()
        self.assertEqual(self.settings.last_set, "light")
        self.controller.toggle_and_persist()
        self.assertEqual(self.settings.last_set, "dark")

    def test_button_text_returns_distinct_icons_per_theme(self):
        self.assertNotEqual(
            ThemeController("dark", self.settings).button_text(),
            ThemeController("light", self.settings).button_text(),
        )

    def test_button_text_uses_sun_for_dark_moon_for_light(self):
        # Unicode escapes mirror the pre-refactor literals at MainWindow:601-608.
        self.assertEqual(ThemeController("dark", self.settings).button_text(), "☼")
        self.assertEqual(ThemeController("light", self.settings).button_text(), "☽")

    def test_button_tooltip_describes_target_theme(self):
        self.assertEqual(
            ThemeController("dark", self.settings).button_tooltip(),
            "Switch to light theme",
        )
        self.assertEqual(
            ThemeController("light", self.settings).button_tooltip(),
            "Switch to dark theme",
        )

    def test_valid_themes_constant_exposes_both_names(self):
        self.assertEqual(set(VALID_THEMES), {"dark", "light"})


if __name__ == "__main__":
    unittest.main()
