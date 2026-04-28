import unittest

from src.domain.compound_builder import (
    build_binary_formula,
    format_formula_part,
    parse_oxidation_states,
)


class TestParseOxidationStates(unittest.TestCase):

    def test_returns_empty_for_none(self):
        self.assertEqual(parse_oxidation_states(None), [])

    def test_parses_list_of_ints(self):
        result = parse_oxidation_states([1, 2, 3, -1])
        self.assertEqual(result, [1, 2, 3, -1])

    def test_filters_zero(self):
        result = parse_oxidation_states([0, 2, -1])
        self.assertEqual(result, [2, -1])

    def test_parses_comma_separated_string(self):
        result = parse_oxidation_states("+1, +2, -1")
        self.assertEqual(result, [1, 2, -1])

    def test_removes_duplicates(self):
        result = parse_oxidation_states([3, 3, -2, -2])
        self.assertEqual(result, [3, -2])

    def test_sorts_positive_then_negative(self):
        result = parse_oxidation_states([-2, 3, -1, 1])
        self.assertEqual(result, [1, 3, -1, -2])


class TestFormatFormulaPart(unittest.TestCase):

    def test_count_one_omitted(self):
        self.assertEqual(format_formula_part("Na", 1), "Na")

    def test_count_shown_when_greater_than_one(self):
        self.assertEqual(format_formula_part("O", 2), "O2")

    def test_large_subscript(self):
        self.assertEqual(format_formula_part("H", 12), "H12")


class TestBuildBinaryFormula(unittest.TestCase):

    def test_nacl(self):
        result = build_binary_formula("Na", 1, "Cl", 1)
        self.assertEqual(result, "NaCl")

    def test_mgcl2(self):
        result = build_binary_formula("Mg", 2, "Cl", 1)
        self.assertEqual(result, "MgCl2")

    def test_al2o3(self):
        result = build_binary_formula("Al", 3, "O", 2)
        self.assertEqual(result, "Al2O3")

    def test_cao(self):
        result = build_binary_formula("Ca", 2, "O", 2)
        self.assertEqual(result, "CaO")

    def test_custom_formatter(self):
        def fmt(sym, cnt):
            return f"<sub>{sym}{cnt}</sub>"
        result = build_binary_formula("Fe", 3, "O", 2, formatter=fmt)
        self.assertIn("Fe", result)
        self.assertIn("O", result)

    def test_zero_charge_rejected(self):
        with self.assertRaises(ValueError):
            build_binary_formula("Na", 0, "Cl", 1)
        with self.assertRaises(ValueError):
            build_binary_formula("Na", 1, "Cl", 0)


if __name__ == "__main__":
    unittest.main()
