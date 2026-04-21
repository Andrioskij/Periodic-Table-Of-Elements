"""Tests for src.ui.theme: palette consistency, lookup, and WCAG contrast."""

import unittest

from src.ui.theme import (
    DARK_THEME,
    DEFAULT_THEME_NAME,
    LIGHT_THEME,
    VALID_THEME_NAMES,
    contrast_ratio,
    get_theme,
    relative_luminance,
)


class TestPaletteConsistency(unittest.TestCase):
    def test_dark_and_light_share_keys(self):
        self.assertEqual(set(DARK_THEME.keys()), set(LIGHT_THEME.keys()))

    def test_palettes_are_non_empty(self):
        self.assertGreater(len(DARK_THEME), 0)
        self.assertGreater(len(LIGHT_THEME), 0)

    def test_values_are_hex_colors(self):
        for name, palette in ("dark", DARK_THEME), ("light", LIGHT_THEME):
            for key, value in palette.items():
                self.assertRegex(
                    value,
                    r"^#[0-9a-fA-F]{6}$",
                    msg=f"{name}.{key} = {value!r} is not #RRGGBB",
                )

    def test_default_theme_name_is_valid(self):
        self.assertIn(DEFAULT_THEME_NAME, VALID_THEME_NAMES)


class TestGetTheme(unittest.TestCase):
    def test_dark_returns_dark_dict(self):
        self.assertEqual(get_theme("dark"), DARK_THEME)

    def test_light_returns_light_dict(self):
        self.assertEqual(get_theme("light"), LIGHT_THEME)

    def test_unknown_falls_back_to_dark(self):
        self.assertEqual(get_theme("solarized"), DARK_THEME)

    def test_default_is_dark(self):
        self.assertEqual(get_theme(), DARK_THEME)


class TestWcagHelpers(unittest.TestCase):
    def test_relative_luminance_black_is_zero(self):
        self.assertAlmostEqual(relative_luminance("#000000"), 0.0, places=6)

    def test_relative_luminance_white_is_one(self):
        self.assertAlmostEqual(relative_luminance("#ffffff"), 1.0, places=6)

    def test_contrast_ratio_black_white_is_21(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21.0, places=4)

    def test_contrast_ratio_is_symmetric(self):
        self.assertAlmostEqual(
            contrast_ratio("#1a1d22", "#ffffff"),
            contrast_ratio("#ffffff", "#1a1d22"),
            places=6,
        )

    def test_invalid_hex_raises(self):
        with self.assertRaises(ValueError):
            relative_luminance("#abc")


class TestWcagAACompliance(unittest.TestCase):
    """Verify bg/text pairs in both themes satisfy the WCAG AA 4.5:1 ratio."""

    PAIRS = [
        ("bg_primary", "text_primary"),
        ("bg_card", "text_primary"),
        ("bg_card_alt", "text_primary"),
        ("bg_input", "text_primary"),
        ("bg_hero", "text_primary"),
    ]

    def test_dark_theme_contrast(self):
        for bg_key, text_key in self.PAIRS:
            ratio = contrast_ratio(DARK_THEME[bg_key], DARK_THEME[text_key])
            self.assertGreaterEqual(
                ratio, 4.5,
                msg=f"dark ({bg_key}, {text_key}) ratio={ratio:.2f} < 4.5",
            )

    def test_light_theme_contrast(self):
        for bg_key, text_key in self.PAIRS:
            ratio = contrast_ratio(LIGHT_THEME[bg_key], LIGHT_THEME[text_key])
            self.assertGreaterEqual(
                ratio, 4.5,
                msg=f"light ({bg_key}, {text_key}) ratio={ratio:.2f} < 4.5",
            )


if __name__ == "__main__":
    unittest.main()
