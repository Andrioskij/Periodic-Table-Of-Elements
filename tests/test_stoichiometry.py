import unittest

from src.domain.stoichiometry import (
    EquationError,
    balance_equation,
    balance_parsed,
    compute_limiting_reagent,
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


class TestEquationErrorCodes(unittest.TestCase):
    """Each EquationError raise site must carry a non-empty code and coherent params."""

    def test_empty_equation_code(self):
        with self.assertRaises(EquationError) as ctx:
            parse_equation("")
        self.assertEqual(ctx.exception.code, "empty")
        self.assertEqual(ctx.exception.params, {})

    def test_no_separator_code(self):
        with self.assertRaises(EquationError) as ctx:
            parse_equation("Fe O2")
        self.assertEqual(ctx.exception.code, "no_separator")

    def test_both_sides_code(self):
        with self.assertRaises(EquationError) as ctx:
            parse_equation("-> O2")
        self.assertEqual(ctx.exception.code, "both_sides")

    def test_invalid_compound_code_carries_compound_and_detail(self):
        # `Ca(` is malformed (unmatched open paren) — surfaces as invalid_compound
        # at the matrix-build step.
        with self.assertRaises(EquationError) as ctx:
            balance_equation("H2 + Ca( -> H2O")
        exc = ctx.exception
        self.assertEqual(exc.code, "invalid_compound")
        self.assertEqual(exc.params["compound"], "Ca(")
        self.assertTrue(exc.params["detail"])

    def test_cannot_balance_code(self):
        with self.assertRaises(EquationError) as ctx:
            balance_equation("H2 -> O2")
        self.assertEqual(ctx.exception.code, "cannot_balance")

    def test_compound_not_found_carries_compound(self):
        with self.assertRaises(EquationError) as ctx:
            compute_stoichiometric_masses(
                ["Fe", "O2"], ["Fe2O3"], [4, 3, 2],
                ELEMENTS,
                given_compound="Cu",
                given_mass_grams=10.0,
            )
        self.assertEqual(ctx.exception.code, "compound_not_found")
        self.assertEqual(ctx.exception.params, {"compound": "Cu"})


def test_balance_parsed_matches_balance_equation():
    expected = balance_equation("C3H8 + O2 -> CO2 + H2O")
    assert balance_parsed(["C3H8", "O2"], ["CO2", "H2O"]) == expected


def test_compute_stoichiometric_masses_accepts_precomputed_molar_masses():
    reactants, products = ["Fe", "O2"], ["Fe2O3"]
    coefficients = [4, 3, 2]

    baseline = compute_stoichiometric_masses(
        reactants, products, coefficients, ELEMENTS,
        given_compound="Fe",
        given_mass_grams=10.0,
    )

    cached_masses = [r["molar_mass"] for r in compute_stoichiometric_masses(
        reactants, products, coefficients, ELEMENTS,
    )]

    reused = compute_stoichiometric_masses(
        reactants, products, coefficients, ELEMENTS,
        given_compound="Fe",
        given_mass_grams=10.0,
        molar_masses=cached_masses,
    )

    assert reused == baseline


def test_compute_stoichiometric_masses_skips_parse_when_molar_masses_provided(
    monkeypatch,
):
    from src.domain import stoichiometry as stoich_mod

    calls = {"n": 0}

    def _spy(formula):
        calls["n"] += 1
        return {"_": 1}

    monkeypatch.setattr(stoich_mod, "parse_formula", _spy)
    compute_stoichiometric_masses(
        ["Fe", "O2"], ["Fe2O3"], [4, 3, 2], ELEMENTS,
        given_compound="Fe",
        given_mass_grams=10.0,
        molar_masses=[55.85, 32.0, 159.7],
    )
    assert calls["n"] == 0


def test_compute_limiting_reagent_h2_o2_water():
    """4 g H2 + 16 g O2 → limiting = O2, yield ≈ 18.0 g H2O, excess ≈ 2.0 g H2."""
    result = compute_limiting_reagent(
        ["H2", "O2"], ["H2O"], [2, 1, 2], ELEMENTS,
        {"H2": 4.0, "O2": 16.0},
    )
    assert result["limiting"] == "O2"
    assert len(result["yields"]) == 1
    assert result["yields"][0]["compound"] == "H2O"
    assert abs(result["yields"][0]["theoretical_mass_g"] - 18.015) < 0.05
    assert len(result["excess"]) == 1
    assert result["excess"][0]["compound"] == "H2"
    assert abs(result["excess"][0]["excess_g"] - 2.0) < 0.05


def test_compute_limiting_reagent_propane_combustion():
    """1.0 g C3H8 + 4.0 g O2 → ratio favors propane; limit on O2."""
    result = compute_limiting_reagent(
        ["C3H8", "O2"], ["CO2", "H2O"], [1, 5, 3, 4], ELEMENTS,
        {"C3H8": 1.0, "O2": 4.0},
    )
    # Per coefficient: C3H8 extent = (1.0/44.097)/1 ≈ 0.02268;
    #                  O2   extent = (4.0/31.998)/5 ≈ 0.02500.
    # So C3H8 is limiting.
    assert result["limiting"] == "C3H8"
    yields_by_compound = {row["compound"]: row for row in result["yields"]}
    assert yields_by_compound["CO2"]["theoretical_moles"] > 0
    assert yields_by_compound["H2O"]["theoretical_moles"] > 0


def test_compute_limiting_reagent_rejects_unknown_reactant_mass():
    with unittest.TestCase().assertRaises(EquationError) as ctx:
        compute_limiting_reagent(
            ["H2", "O2"], ["H2O"], [2, 1, 2], ELEMENTS,
            {"H2": 4.0, "O2": 16.0, "Cu": 5.0},
        )
    assert ctx.exception.code == "compound_not_found"


def test_compute_limiting_reagent_requires_positive_masses():
    with unittest.TestCase().assertRaises(EquationError) as ctx:
        compute_limiting_reagent(
            ["H2", "O2"], ["H2O"], [2, 1, 2], ELEMENTS,
            {"H2": 0.0, "O2": 16.0},
        )
    assert ctx.exception.code == "invalid_mass"


if __name__ == "__main__":
    unittest.main()
