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


class TestHydratedCompounds(unittest.TestCase):

    def test_copper_sulfate_pentahydrate(self):
        self.assertEqual(
            parse_formula("CuSO4·5H2O"),
            {"Cu": 1, "S": 1, "O": 9, "H": 10},
        )

    def test_sodium_carbonate_decahydrate(self):
        self.assertEqual(
            parse_formula("Na2CO3·10H2O"),
            {"Na": 2, "C": 1, "O": 13, "H": 20},
        )

    def test_magnesium_sulfate_heptahydrate(self):
        self.assertEqual(
            parse_formula("MgSO4·7H2O"),
            {"Mg": 1, "S": 1, "O": 11, "H": 14},
        )

    def test_iron_chloride_hexahydrate(self):
        self.assertEqual(
            parse_formula("FeCl3·6H2O"),
            {"Fe": 1, "Cl": 3, "O": 6, "H": 12},
        )

    def test_alum_octadecahydrate(self):
        self.assertEqual(
            parse_formula("Al2(SO4)3·18H2O"),
            {"Al": 2, "S": 3, "O": 30, "H": 36},
        )

    def test_hydrate_without_explicit_multiplier(self):
        self.assertEqual(
            parse_formula("CaSO4·H2O"),
            {"Ca": 1, "S": 1, "O": 5, "H": 2},
        )

    def test_molar_mass_of_copper_sulfate_pentahydrate(self):
        atoms = parse_formula("CuSO4·5H2O")
        mass = compute_molar_mass(atoms, ELEMENTS)
        self.assertAlmostEqual(mass, 249.68, delta=0.05)

    def test_ascii_dot_equivalent_to_middle_dot(self):
        self.assertEqual(
            parse_formula("CuSO4.5H2O"),
            parse_formula("CuSO4·5H2O"),
        )

    def test_spaces_around_separator_are_tolerated(self):
        self.assertEqual(
            parse_formula("CuSO4 · 5H2O"),
            parse_formula("CuSO4·5H2O"),
        )

    def test_leading_separator_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("·H2O")

    def test_trailing_separator_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("CuSO4·")

    def test_double_separator_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("CuSO4··5H2O")

    def test_separator_only_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("·")

    def test_multiplier_without_formula_rejected(self):
        with self.assertRaises(FormulaError):
            parse_formula("CuSO4·5")


class TestFormulaErrorCodes(unittest.TestCase):
    """Each FormulaError raise site must carry a non-empty code and coherent params."""

    def _raises_with(self, fn, *, code: str, params: dict | None = None):
        with self.assertRaises(FormulaError) as ctx:
            fn()
        exc = ctx.exception
        self.assertEqual(exc.code, code)
        self.assertIsInstance(exc.params, dict)
        if params is not None:
            self.assertEqual(exc.params, params)

    def test_empty_formula_code(self):
        self._raises_with(lambda: parse_formula(""), code="empty", params={})

    def test_whitespace_only_code(self):
        self._raises_with(lambda: parse_formula("   "), code="empty", params={})

    def test_unmatched_close_carries_position(self):
        self._raises_with(
            lambda: parse_formula("H2O)"),
            code="unmatched_close",
            params={"position": 3},
        )

    def test_unmatched_open_code(self):
        self._raises_with(lambda: parse_formula("Ca(OH"), code="unmatched_open", params={})

    def test_unexpected_char_carries_context(self):
        with self.assertRaises(FormulaError) as ctx:
            parse_formula("H2@O")
        exc = ctx.exception
        self.assertEqual(exc.code, "unexpected_char")
        self.assertEqual(exc.params["char"], "@")
        self.assertEqual(exc.params["position"], 2)
        self.assertEqual(exc.params["formula"], "H2@O")

    def test_no_elements_carries_formula(self):
        # A bare digit produces a parse with no elements collected.
        with self.assertRaises(FormulaError) as ctx:
            parse_formula("()")
        exc = ctx.exception
        self.assertEqual(exc.code, "no_elements")
        self.assertEqual(exc.params, {"formula": "()"})

    def test_unknown_symbol_carries_symbol(self):
        with self.assertRaises(FormulaError) as ctx:
            compute_molar_mass({"Xx": 1}, ELEMENTS)
        exc = ctx.exception
        self.assertEqual(exc.code, "unknown_symbol")
        self.assertEqual(exc.params, {"symbol": "Xx"})

    def test_unknown_symbol_via_percent_composition(self):
        with self.assertRaises(FormulaError) as ctx:
            compute_percent_composition({"Yy": 1}, ELEMENTS)
        self.assertEqual(ctx.exception.code, "unknown_symbol")
        self.assertEqual(ctx.exception.params, {"symbol": "Yy"})

    def test_hydrate_malformed_carries_formula(self):
        with self.assertRaises(FormulaError) as ctx:
            parse_formula("CuSO4·")
        self.assertEqual(ctx.exception.code, "hydrate_malformed")
        self.assertEqual(ctx.exception.params, {"formula": "CuSO4·"})

    def test_hydrate_no_formula_carries_formula(self):
        with self.assertRaises(FormulaError) as ctx:
            parse_formula("CuSO4·5")
        self.assertEqual(ctx.exception.code, "hydrate_no_formula")
        self.assertEqual(ctx.exception.params, {"formula": "CuSO4·5"})


if __name__ == "__main__":
    unittest.main()
