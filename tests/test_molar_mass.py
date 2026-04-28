import unittest

from src.domain.molar_mass import (
    FormulaError,
    compute_molar_mass,
    compute_percent_composition,
    parse_formula,
)
from src.services.data_loader import load_elements

ELEMENTS = load_elements()


class TestParseFormula(unittest.TestCase):

    def test_parse_simple_formula(self):
        self.assertEqual(parse_formula("H2O"), {"H": 2, "O": 1})

    def test_parse_with_parentheses(self):
        self.assertEqual(parse_formula("Ca(OH)2"), {"Ca": 1, "O": 2, "H": 2})

    def test_parse_nested_parentheses(self):
        self.assertEqual(parse_formula("Mg3(PO4)2"), {"Mg": 3, "P": 2, "O": 8})

    def test_parse_single_element(self):
        self.assertEqual(parse_formula("Fe"), {"Fe": 1})

    def test_parse_complex_formula(self):
        self.assertEqual(parse_formula("Fe2(SO4)3"), {"Fe": 2, "S": 3, "O": 12})

    def test_parse_two_letter_symbols(self):
        self.assertEqual(parse_formula("NaCl"), {"Na": 1, "Cl": 1})

    def test_parse_implicit_count(self):
        result = parse_formula("NaCl")
        self.assertEqual(result["Na"], 1)
        self.assertEqual(result["Cl"], 1)


class TestMolarMass(unittest.TestCase):

    def test_molar_mass_water(self):
        atoms = parse_formula("H2O")
        mass = compute_molar_mass(atoms, ELEMENTS)
        self.assertAlmostEqual(mass, 18.015, delta=0.01)

    def test_molar_mass_nacl(self):
        atoms = parse_formula("NaCl")
        mass = compute_molar_mass(atoms, ELEMENTS)
        self.assertAlmostEqual(mass, 58.44, delta=0.01)


class TestPercentComposition(unittest.TestCase):

    def test_percent_composition_water(self):
        atoms = parse_formula("H2O")
        comp = compute_percent_composition(atoms, ELEMENTS)
        by_symbol = {c["symbol"]: c["percent"] for c in comp}
        self.assertAlmostEqual(by_symbol["H"], 11.19, delta=0.1)
        self.assertAlmostEqual(by_symbol["O"], 88.81, delta=0.1)


class TestFormulaErrors(unittest.TestCase):

    def test_invalid_formula_raises(self):
        with self.assertRaises(FormulaError):
            atoms = parse_formula("Xx2")
            compute_molar_mass(atoms, ELEMENTS)

    def test_empty_formula_raises(self):
        with self.assertRaises(FormulaError):
            parse_formula("")

    def test_case_sensitivity(self):
        # "na" should not be parsed as "Na" — lowercase-only is invalid
        with self.assertRaises(FormulaError):
            parse_formula("na")

    def test_three_letter_symbol_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("NaaCl")

    def test_lowercase_after_two_letter_symbol_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("Naa")


if __name__ == "__main__":
    unittest.main()
