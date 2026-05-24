import unittest

from src.ui.formatters import (
    format_info_value,
    format_value,
    subscript_chemical_formula,
)


class TestFormatValue(unittest.TestCase):

    def test_none_returns_na(self):
        self.assertEqual(format_value(None), "n/a")

    def test_custom_na_text(self):
        self.assertEqual(format_value(None, na_text="N/D"), "N/D")

    def test_float_default_precision(self):
        self.assertEqual(format_value(3.14159), "3.142")

    def test_float_custom_precision(self):
        self.assertEqual(format_value(3.14159, decimals=1), "3.1")

    def test_integer_passthrough(self):
        self.assertEqual(format_value(42), "42")

    def test_string_passthrough(self):
        self.assertEqual(format_value("hello"), "hello")


class TestFormatInfoValue(unittest.TestCase):

    def test_none_returns_na(self):
        self.assertEqual(format_info_value("atomic_mass", None), "n/a")

    def test_electronegativity_no_unit(self):
        result = format_info_value("electronegativity", 2.20)
        self.assertNotIn("pm", result)

    def test_atomic_radius_has_pm_unit(self):
        result = format_info_value("atomic_radius", 152.0)
        self.assertIn("pm", result)

    def test_unknown_field_uses_generic(self):
        result = format_info_value("unknown_field", 3.14)
        self.assertEqual(result, "3.140")

    def test_ionization_energy_has_kj_unit(self):
        result = format_info_value("ionization_energy", 5.139)
        self.assertIn("kJ/mol", result)


class TestSubscriptChemicalFormula(unittest.TestCase):
    def test_simple_diatomic_subscript(self):
        self.assertEqual(subscript_chemical_formula("H2O"), "H₂O")

    def test_polyatomic_with_parens(self):
        self.assertEqual(subscript_chemical_formula("Fe2(SO4)3"), "Fe₂(SO₄)₃")

    def test_hydrate_count_stays_plain(self):
        # The ``5`` in 5H2O is a hydrate multiplier, preceded by U+00B7
        # (·) — not a letter or closing paren — so it must stay plain.
        # Only the 4 (after O) and the 2 (after H) become subscripts.
        self.assertEqual(
            subscript_chemical_formula("CuSO4·5H2O"), "CuSO₄·5H₂O",
        )

    def test_balanced_equation_keeps_leading_coefficients_plain(self):
        # In a stoichiometric coefficient + space + formula, the
        # leading integers stay plain (they're not subscripts) while
        # the in-formula counts get subscripted.
        self.assertEqual(
            subscript_chemical_formula("2 Fe + 3 O2 -> Fe2O3"),
            "2 Fe + 3 O₂ -> Fe₂O₃",
        )

    def test_multi_digit_subscripts(self):
        self.assertEqual(subscript_chemical_formula("C60"), "C₆₀")

    def test_single_atom_no_change(self):
        self.assertEqual(subscript_chemical_formula("Na"), "Na")

    def test_empty_string_returns_empty(self):
        self.assertEqual(subscript_chemical_formula(""), "")

    def test_none_returns_none(self):
        # Defensive — render-time callers may hand us None when the
        # underlying field is missing; the formatter must round-trip
        # it without raising.
        self.assertIsNone(subscript_chemical_formula(None))

    def test_lowercase_element_followed_by_digit(self):
        # The regex allows lowercase letters too because composed
        # symbols (Fe, Cl, Mg) end in lowercase and may be followed
        # by a digit (``Mg2`` if it ever appears in a non-canonical
        # formula).
        self.assertEqual(subscript_chemical_formula("Mg2"), "Mg₂")


if __name__ == "__main__":
    unittest.main()
