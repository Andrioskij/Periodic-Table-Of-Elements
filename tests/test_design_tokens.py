"""Tests for src.config.design_tokens: schema, format, immutability, and consumer parity.

These tests guard the refactor that moved every visual constant of the
Qt frontend into a single canonical mapping, and they pin the contract
for the JSON export consumed by the upcoming web frontend.
"""

import re
import unittest
from types import MappingProxyType

from src.config.design_tokens import TOKENS

HEX6 = re.compile(r"^#[0-9a-fA-F]{6}$")
HEX6_OR_8 = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


class TestTokenSchema(unittest.TestCase):
    """Every expected top-level group must be present and non-empty."""

    EXPECTED_TOP_LEVEL = {
        "color",
        "font",
        "spacing",
        "radius",
        "border",
        "scale",
        "alpha",
        "interpolation",
        "luminance",
    }

    EXPECTED_COLOR_GROUPS = {
        "theme",
        "category",
        "macro_class",
        "trend",
        "button_border",
        "fallback",
        "text_on_color",
        "info_panel",
        "metric_progress",
    }

    EXPECTED_FONT_GROUPS = {"family", "size", "weight", "letter_spacing"}

    REQUIRED_THEME_KEYS = {
        "bg_primary", "bg_secondary", "bg_card", "bg_card_alt", "bg_input",
        "bg_inset", "bg_hero", "bg_button", "bg_button_hover",
        "bg_button_pressed", "bg_disabled", "bg_search_card",
        "text_primary", "text_secondary", "text_muted", "text_strong",
        "text_disabled", "text_on_accent",
        "border", "border_strong", "border_subtle", "border_search",
        "border_button", "border_disabled",
        "accent", "accent_hover", "accent_pressed",
        "selection_bg", "selection_text",
        "painter_bg", "painter_text", "painter_subtext", "painter_label",
        "painter_box_border", "painter_arrow_up", "painter_arrow_down",
        "painter_dot",
        "solubility_soluble", "solubility_insoluble", "solubility_slightly",
        "solubility_highlight",
    }

    REQUIRED_CATEGORY_KEYS = {
        "alkali_metal", "alkaline_earth_metal", "transition_metal",
        "post_transition_metal", "metalloid", "nonmetal", "halogen",
        "noble_gas", "lanthanide", "actinide",
    }

    def test_top_level_groups_present(self):
        self.assertEqual(self.EXPECTED_TOP_LEVEL, set(TOKENS.keys()))

    def test_color_groups_present(self):
        self.assertEqual(self.EXPECTED_COLOR_GROUPS, set(TOKENS["color"].keys()))

    def test_font_groups_present(self):
        self.assertEqual(self.EXPECTED_FONT_GROUPS, set(TOKENS["font"].keys()))

    def test_theme_palettes_have_required_keys(self):
        for theme_name in ("dark", "light"):
            with self.subTest(theme=theme_name):
                palette = TOKENS["color"]["theme"][theme_name]
                self.assertEqual(
                    self.REQUIRED_THEME_KEYS - set(palette.keys()), set()
                )

    def test_dark_and_light_theme_share_keys(self):
        self.assertEqual(
            set(TOKENS["color"]["theme"]["dark"].keys()),
            set(TOKENS["color"]["theme"]["light"].keys()),
        )

    def test_category_palettes_have_required_keys(self):
        for theme_name in ("dark", "light"):
            with self.subTest(theme=theme_name):
                palette = TOKENS["color"]["category"][theme_name]
                self.assertEqual(
                    self.REQUIRED_CATEGORY_KEYS - set(palette.keys()), set()
                )

    def test_dark_and_light_category_share_keys(self):
        self.assertEqual(
            set(TOKENS["color"]["category"]["dark"].keys()),
            set(TOKENS["color"]["category"]["light"].keys()),
        )

    def test_font_size_values_are_positive_int(self):
        sizes = TOKENS["font"]["size"]
        self.assertGreater(len(sizes), 0)
        for key, value in sizes.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, int)
                self.assertGreater(value, 0)

    def test_spacing_values_are_non_negative_int(self):
        for key, value in TOKENS["spacing"].items():
            with self.subTest(key=key):
                self.assertIsInstance(value, int)
                self.assertGreaterEqual(value, 0)

    def test_radius_values_are_non_negative_number(self):
        for key, value in TOKENS["radius"].items():
            with self.subTest(key=key):
                self.assertIsInstance(value, (int, float))
                self.assertGreaterEqual(value, 0)


class TestColorFormat(unittest.TestCase):
    """Every hex color must be #RRGGBB or #RRGGBBAA — no rgb()/named colors."""

    def _iter_hex_strings(self, node):
        if isinstance(node, str):
            if node.startswith("#"):
                yield node
            return
        if isinstance(node, MappingProxyType) or isinstance(node, dict):
            for value in node.values():
                yield from self._iter_hex_strings(value)
            return
        if isinstance(node, (tuple, list)):
            for value in node:
                yield from self._iter_hex_strings(value)

    def test_all_hex_color_values_are_well_formed(self):
        seen_any = False
        for color_string in self._iter_hex_strings(TOKENS["color"]):
            seen_any = True
            with self.subTest(color=color_string):
                self.assertRegex(color_string, HEX6_OR_8)
        self.assertTrue(seen_any, "No hex color strings found in TOKENS['color']")

    def test_palette_colors_are_six_digit(self):
        for theme_name in ("dark", "light"):
            for key, color in TOKENS["color"]["theme"][theme_name].items():
                with self.subTest(theme=theme_name, key=key):
                    self.assertRegex(color, HEX6)

    def test_category_colors_are_six_digit(self):
        for theme_name in ("dark", "light"):
            for key, color in TOKENS["color"]["category"][theme_name].items():
                with self.subTest(theme=theme_name, key=key):
                    self.assertRegex(color, HEX6)

    def test_macro_class_colors_are_six_digit(self):
        for key, color in TOKENS["color"]["macro_class"].items():
            with self.subTest(key=key):
                self.assertRegex(color, HEX6)

    def test_label_background_rgba_is_quadruple(self):
        rgba = TOKENS["color"]["trend"]["label_background_rgba"]
        self.assertEqual(len(rgba), 4)
        for channel in rgba:
            self.assertIsInstance(channel, int)
            self.assertGreaterEqual(channel, 0)
            self.assertLessEqual(channel, 255)


class TestImmutability(unittest.TestCase):
    """Top-level groups should be immutable proxies so callers can't mutate them."""

    def test_top_level_is_proxy(self):
        self.assertIsInstance(TOKENS, MappingProxyType)

    def test_nested_groups_are_proxies(self):
        for key, value in TOKENS.items():
            with self.subTest(key=key):
                self.assertIsInstance(value, MappingProxyType)

    def test_cannot_mutate_top_level(self):
        with self.assertRaises(TypeError):
            TOKENS["color"] = {}  # type: ignore[index]

    def test_cannot_mutate_nested(self):
        with self.assertRaises(TypeError):
            TOKENS["color"]["theme"]["dark"]["bg_primary"] = "#000000"  # type: ignore[index]


class TestThemeRoundtrip(unittest.TestCase):
    """The legacy ``theme.py`` palettes must remain content-equal to TOKENS."""

    def test_dark_palette_matches_tokens(self):
        from src.ui.theme import DARK_THEME

        for key, value in TOKENS["color"]["theme"]["dark"].items():
            with self.subTest(key=key):
                self.assertEqual(DARK_THEME[key], value)

    def test_light_palette_matches_tokens(self):
        from src.ui.theme import LIGHT_THEME

        for key, value in TOKENS["color"]["theme"]["light"].items():
            with self.subTest(key=key):
                self.assertEqual(LIGHT_THEME[key], value)

    def test_get_theme_returns_canonical_object(self):
        from src.ui.theme import DARK_THEME, LIGHT_THEME, get_theme

        # Identity, not just equality — panels cache the dict reference.
        self.assertIs(get_theme("dark"), DARK_THEME)
        self.assertIs(get_theme("light"), LIGHT_THEME)


class TestStylesRoundtrip(unittest.TestCase):
    """``styles.py`` constants must be derived from TOKENS without drift."""

    def test_default_ui_color_matches_fallback(self):
        from src.ui.styles import DEFAULT_UI_COLOR

        self.assertEqual(DEFAULT_UI_COLOR, TOKENS["color"]["fallback"]["ui"])

    def test_numeric_trend_endpoints_match(self):
        from src.ui.styles import NUMERIC_TREND_END_COLOR, NUMERIC_TREND_START_COLOR

        self.assertEqual(
            NUMERIC_TREND_START_COLOR,
            TOKENS["color"]["trend"]["numeric_gradient"]["start"],
        )
        self.assertEqual(
            NUMERIC_TREND_END_COLOR,
            TOKENS["color"]["trend"]["numeric_gradient"]["end"],
        )

    def test_trend_overlay_colors_match(self):
        from src.ui.styles import TREND_OVERLAY_COLORS

        self.assertEqual(
            TREND_OVERLAY_COLORS,
            dict(TOKENS["color"]["trend"]["directional"]),
        )

    def test_button_border_colors_match(self):
        from src.ui.styles import BUTTON_BORDER_COLORS

        self.assertEqual(
            BUTTON_BORDER_COLORS, dict(TOKENS["color"]["button_border"])
        )

    def test_category_lookup_uses_token_values(self):
        from src.ui.styles import (
            PERIODIC_TABLE_CATEGORY_COLORS,
            PERIODIC_TABLE_CATEGORY_COLORS_LIGHT,
        )

        self.assertEqual(
            PERIODIC_TABLE_CATEGORY_COLORS["alkali metal"],
            TOKENS["color"]["category"]["dark"]["alkali_metal"],
        )
        self.assertEqual(
            PERIODIC_TABLE_CATEGORY_COLORS_LIGHT["noble gas"],
            TOKENS["color"]["category"]["light"]["noble_gas"],
        )

    def test_lanthanoid_actinoid_aliases_share_color(self):
        from src.ui.styles import PERIODIC_TABLE_CATEGORY_COLORS

        self.assertEqual(
            PERIODIC_TABLE_CATEGORY_COLORS["lanthanide"],
            PERIODIC_TABLE_CATEGORY_COLORS["lanthanoid"],
        )
        self.assertEqual(
            PERIODIC_TABLE_CATEGORY_COLORS["actinide"],
            PERIODIC_TABLE_CATEGORY_COLORS["actinoid"],
        )


class TestStylesheetSubstitution(unittest.TestCase):
    """``get_stylesheet`` must resolve every placeholder and use token values."""

    def test_no_unresolved_placeholders(self):
        from src.ui.styles import get_stylesheet

        for theme in ("dark", "light"):
            qss = get_stylesheet(theme)
            with self.subTest(theme=theme):
                self.assertNotIn("{{", qss)
                self.assertNotIn("}}", qss)

    def test_dark_qss_includes_token_accent(self):
        from src.ui.styles import get_stylesheet

        accent = TOKENS["color"]["theme"]["dark"]["accent"]
        self.assertIn(accent, get_stylesheet("dark"))

    def test_qss_uses_token_font_family(self):
        from src.ui.styles import get_stylesheet

        family = TOKENS["font"]["family"]["sans"]
        self.assertIn(family, get_stylesheet("dark"))


class TestDomainTrendsRoundtrip(unittest.TestCase):
    """``domain.trends.MACRO_CLASS_COLORS`` must match TOKENS values."""

    def test_macro_class_colors_match(self):
        from src.domain.trends import MACRO_CLASS_COLORS

        self.assertEqual(
            MACRO_CLASS_COLORS["Metal"],
            TOKENS["color"]["macro_class"]["metal"],
        )
        self.assertEqual(
            MACRO_CLASS_COLORS["Metalloid"],
            TOKENS["color"]["macro_class"]["metalloid"],
        )
        self.assertEqual(
            MACRO_CLASS_COLORS["Nonmetal"],
            TOKENS["color"]["macro_class"]["nonmetal"],
        )

    def test_unknown_macro_class_falls_back_to_token(self):
        from src.domain.trends import get_macro_class_color

        self.assertEqual(
            get_macro_class_color("UnknownClass"),
            TOKENS["color"]["fallback"]["ui"],
        )


if __name__ == "__main__":
    unittest.main()
