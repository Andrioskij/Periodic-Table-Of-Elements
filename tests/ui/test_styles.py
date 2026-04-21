"""Tests for src.ui.styles theme-aware loaders."""

import unittest

from src.ui.styles import (
    DEFAULT_UI_COLOR,
    PERIODIC_TABLE_CATEGORY_COLORS,
    PERIODIC_TABLE_CATEGORY_COLORS_LIGHT,
    get_category_color,
    get_stylesheet,
)


class TestGetStylesheet(unittest.TestCase):
    def test_dark_and_light_are_non_empty(self):
        dark = get_stylesheet("dark")
        light = get_stylesheet("light")
        self.assertGreater(len(dark), 0)
        self.assertGreater(len(light), 0)

    def test_dark_and_light_differ(self):
        self.assertNotEqual(get_stylesheet("dark"), get_stylesheet("light"))

    def test_no_unresolved_placeholders(self):
        for theme in ("dark", "light"):
            qss = get_stylesheet(theme)
            self.assertNotIn("{{", qss, msg=f"unresolved placeholder in {theme}")
            self.assertNotIn("}}", qss, msg=f"unresolved placeholder in {theme}")

    def test_default_theme_is_dark(self):
        self.assertEqual(get_stylesheet(), get_stylesheet("dark"))

    def test_unknown_theme_falls_back_to_dark(self):
        self.assertEqual(get_stylesheet("solarized"), get_stylesheet("dark"))


class TestGetCategoryColor(unittest.TestCase):
    def test_dark_vs_light_differ_for_known_category(self):
        self.assertNotEqual(
            get_category_color("noble gas", theme="dark"),
            get_category_color("noble gas", theme="light"),
        )

    def test_returns_hex(self):
        for theme in ("dark", "light"):
            for category in PERIODIC_TABLE_CATEGORY_COLORS:
                color = get_category_color(category, theme=theme)
                self.assertRegex(color, r"^#[0-9a-fA-F]{6}$")

    def test_unknown_category_returns_default(self):
        self.assertEqual(
            get_category_color("unobtainium", theme="dark"), DEFAULT_UI_COLOR
        )
        self.assertEqual(
            get_category_color("unobtainium", theme="light"), DEFAULT_UI_COLOR
        )

    def test_none_category_returns_default(self):
        self.assertEqual(get_category_color(None, theme="dark"), DEFAULT_UI_COLOR)

    def test_case_insensitive(self):
        self.assertEqual(
            get_category_color("Noble Gas", theme="dark"),
            get_category_color("noble gas", theme="dark"),
        )

    def test_light_palette_covers_all_dark_categories(self):
        self.assertEqual(
            set(PERIODIC_TABLE_CATEGORY_COLORS.keys()),
            set(PERIODIC_TABLE_CATEGORY_COLORS_LIGHT.keys()),
        )


if __name__ == "__main__":
    unittest.main()
