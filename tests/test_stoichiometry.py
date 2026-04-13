import unittest

from src.domain.stoichiometry import (
    EquationError,
    balance_equation,
    compute_stoichiometric_masses,
    format_balanced_equation,
    parse_equation,
)
from src.services.data_loader import load_elements

ELEMENTS = load_elements()


class TestParseEquation(unittest.TestCase):

    def test_parse_equation_arrow(self):
        r, p = parse_equation("H2 + O2 -> H2O")
        self.assertEqual(r, ["H2", "O2"])
        self.assertEqual(p, ["H2O"])

    def test_parse_equation_equals(self):
        r, p = parse_equation("H2 + O2 = H2O")
        self.assertEqual(r, ["H2", "O2"])
        self.assertEqual(p, ["H2O"])

    def test_parse_equation_unicode_arrow(self):
        r, p = parse_equation("H2 + O2 → H2O")
        self.assertEqual(r, ["H2", "O2"])
        self.assertEqual(p, ["H2O"])


class TestBalanceEquation(unittest.TestCase):

    def test_balance_simple(self):
        coeffs = balance_equation("H2 + O2 -> H2O")
        self.assertEqual(coeffs, [2, 1, 2])

    def test_balance_iron_oxide(self):
        coeffs = balance_equation("Fe + O2 -> Fe2O3")
        self.assertEqual(coeffs, [4, 3, 2])

    def test_balance_already_balanced(self):
        coeffs = balance_equation("H2 + Cl2 -> HCl")
        self.assertEqual(coeffs, [1, 1, 2])

    def test_balance_combustion(self):
        coeffs = balance_equation("C3H8 + O2 -> CO2 + H2O")
        self.assertEqual(coeffs, [1, 5, 3, 4])


class TestFormatBalanced(unittest.TestCase):

    def test_format_balanced(self):
        result = format_balanced_equation(["Fe", "O2"], ["Fe2O3"], [4, 3, 2])
        self.assertEqual(result, "4Fe + 3O2 → 2Fe2O3")

    def test_format_omits_coefficient_one(self):
        result = format_balanced_equation(["C3H8", "O2"], ["CO2", "H2O"], [1, 5, 3, 4])
        self.assertIn("C3H8", result)
        self.assertNotIn("1C3H8", result)


class TestStoichiometricMasses(unittest.TestCase):

    def test_stoichiometric_masses(self):
        # 4Fe + 3O2 -> 2Fe2O3, given 10g of Fe
        result = compute_stoichiometric_masses(
            ["Fe", "O2"], ["Fe2O3"], [4, 3, 2],
            ELEMENTS,
            given_compound="Fe",
            given_mass_grams=10.0,
        )
        fe_entry = next(r for r in result if r["compound"] == "Fe")
        self.assertAlmostEqual(fe_entry["mass"], 10.0, delta=0.01)

        o2_entry = next(r for r in result if r["compound"] == "O2")
        # 10g Fe = 0.1791 mol, ratio 3/4 -> 0.1343 mol O2 -> 4.297g
        self.assertAlmostEqual(o2_entry["mass"], 4.297, delta=0.1)

        fe2o3_entry = next(r for r in result if r["compound"] == "Fe2O3")
        # ratio 2/4 -> 0.0895 mol -> 14.30g
        self.assertAlmostEqual(fe2o3_entry["mass"], 14.30, delta=0.1)


class TestEquationErrors(unittest.TestCase):

    def test_invalid_equation_raises(self):
        with self.assertRaises(EquationError):
            parse_equation("-> O2")

    def test_empty_equation_raises(self):
        with self.assertRaises(EquationError):
            parse_equation("")

    def test_no_separator_raises(self):
        with self.assertRaises(EquationError):
            parse_equation("Fe O2")


if __name__ == "__main__":
    unittest.main()
