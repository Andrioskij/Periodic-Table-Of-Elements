import unittest

from src.domain.trends import (
    compute_numeric_ranges,
    get_macro_class,
    get_macro_class_color,
)


class TestGetMacroClass(unittest.TestCase):

    def test_alkali_metal(self):
        self.assertEqual(get_macro_class("alkali metal"), "Metal")

    def test_transition_metal(self):
        self.assertEqual(get_macro_class("transition metal"), "Metal")

    def test_lanthanide(self):
        self.assertEqual(get_macro_class("lanthanide"), "Metal")

    def test_actinoid(self):
        self.assertEqual(get_macro_class("actinoid"), "Metal")

    def test_metalloid(self):
        self.assertEqual(get_macro_class("metalloid"), "Metalloid")

    def test_nonmetal(self):
        self.assertEqual(get_macro_class("nonmetal"), "Nonmetal")

    def test_halogen(self):
        self.assertEqual(get_macro_class("halogen"), "Nonmetal")

    def test_noble_gas(self):
        self.assertEqual(get_macro_class("noble gas"), "Nonmetal")

    def test_unknown_category(self):
        self.assertEqual(get_macro_class("unknown"), "n/a")

    def test_none_category(self):
        self.assertEqual(get_macro_class(None), "n/a")

    def test_custom_fallback(self):
        self.assertEqual(get_macro_class("unknown", traditional_na="N/D"), "N/D")


class TestGetMacroClassColor(unittest.TestCase):

    def test_metal_color(self):
        self.assertEqual(get_macro_class_color("Metal"), "#4E79A7")

    def test_nonmetal_color(self):
        self.assertEqual(get_macro_class_color("Nonmetal"), "#EDC948")

    def test_metalloid_color(self):
        self.assertEqual(get_macro_class_color("Metalloid"), "#B07AA1")

    def test_unknown_falls_back_to_grey(self):
        self.assertEqual(get_macro_class_color("Whatever"), "#7A7A7A")


class TestComputeNumericRanges(unittest.TestCase):

    def test_basic_range(self):
        elements = [
            {"electronegativity": 0.7, "atomic_radius": 200},
            {"electronegativity": 4.0, "atomic_radius": 50},
            {"electronegativity": 2.2, "atomic_radius": 120},
        ]
        props = {"electronegativity": ("Electronegativity", "electronegativity")}
        ranges = compute_numeric_ranges(elements, props)
        self.assertAlmostEqual(ranges["electronegativity"][0], 0.7)
        self.assertAlmostEqual(ranges["electronegativity"][1], 4.0)

    def test_skips_none_values(self):
        elements = [
            {"electronegativity": None},
            {"electronegativity": 3.0},
            {"electronegativity": 1.5},
        ]
        props = {"electronegativity": ("Electronegativity", "electronegativity")}
        ranges = compute_numeric_ranges(elements, props)
        self.assertAlmostEqual(ranges["electronegativity"][0], 1.5)
        self.assertAlmostEqual(ranges["electronegativity"][1], 3.0)

    def test_empty_values_default_range(self):
        elements = [{"electronegativity": None}]
        props = {"electronegativity": ("Electronegativity", "electronegativity")}
        ranges = compute_numeric_ranges(elements, props)
        self.assertEqual(ranges["electronegativity"], (0, 1))


if __name__ == "__main__":
    unittest.main()
