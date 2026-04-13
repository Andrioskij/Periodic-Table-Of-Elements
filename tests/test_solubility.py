"""Tests for src.domain.solubility module."""

import unittest

from src.domain.solubility import (
    ANIONS,
    CATIONS,
    get_cations_for_element,
    get_solubility,
    get_solubility_matrix,
    get_solubility_rule,
)


class TestSolubility(unittest.TestCase):
    """Test solubility verdicts for known compounds."""

    def test_nacl_soluble(self):
        self.assertEqual(get_solubility("Na\u207a", "Cl\u207b"), "soluble")

    def test_agcl_insoluble(self):
        self.assertEqual(get_solubility("Ag\u207a", "Cl\u207b"), "insoluble")

    def test_baso4_insoluble(self):
        self.assertEqual(get_solubility("Ba\u00b2\u207a", "SO\u2084\u00b2\u207b"), "insoluble")

    def test_caso4_slightly(self):
        self.assertEqual(get_solubility("Ca\u00b2\u207a", "SO\u2084\u00b2\u207b"), "slightly_soluble")

    def test_naoh_soluble(self):
        self.assertEqual(get_solubility("Na\u207a", "OH\u207b"), "soluble")

    def test_feoh3_insoluble(self):
        self.assertEqual(get_solubility("Fe\u00b3\u207a", "OH\u207b"), "insoluble")

    def test_caco3_insoluble(self):
        self.assertEqual(get_solubility("Ca\u00b2\u207a", "CO\u2083\u00b2\u207b"), "insoluble")

    def test_na2co3_soluble(self):
        self.assertEqual(get_solubility("Na\u207a", "CO\u2083\u00b2\u207b"), "soluble")

    def test_kno3_soluble(self):
        self.assertEqual(get_solubility("K\u207a", "NO\u2083\u207b"), "soluble")

    def test_pbcl2_insoluble(self):
        self.assertEqual(get_solubility("Pb\u00b2\u207a", "Cl\u207b"), "insoluble")

    def test_caoh2_slightly(self):
        self.assertEqual(get_solubility("Ca\u00b2\u207a", "OH\u207b"), "slightly_soluble")


class TestSolubilityRule(unittest.TestCase):
    """Test that the correct rule is returned."""

    def test_rule_nacl_is_alkali(self):
        rule = get_solubility_rule("Na\u207a", "Cl\u207b")
        self.assertIsNotNone(rule)
        self.assertEqual(rule["id"], "alkali_ammonium")

    def test_rule_agcl_is_halide(self):
        rule = get_solubility_rule("Ag\u207a", "Cl\u207b")
        self.assertIsNotNone(rule)
        self.assertEqual(rule["id"], "halides")

    def test_rule_baso4_is_sulfate(self):
        rule = get_solubility_rule("Ba\u00b2\u207a", "SO\u2084\u00b2\u207b")
        self.assertIsNotNone(rule)
        self.assertEqual(rule["id"], "sulfates")


class TestSolubilityMatrix(unittest.TestCase):
    """Test the generated solubility matrix."""

    def test_matrix_dimensions(self):
        matrix = get_solubility_matrix()
        self.assertEqual(len(matrix), len(CATIONS))
        for row in matrix:
            self.assertEqual(len(row), len(ANIONS))

    def test_matrix_all_valid_values(self):
        valid = {"soluble", "insoluble", "slightly_soluble"}
        matrix = get_solubility_matrix()
        for row in matrix:
            for cell in row:
                self.assertIn(cell, valid)


class TestElementMapping(unittest.TestCase):
    """Test element-to-cation mapping."""

    def test_na_maps_to_cation(self):
        self.assertEqual(get_cations_for_element("Na"), ["Na\u207a"])

    def test_fe_maps_to_two_cations(self):
        self.assertEqual(get_cations_for_element("Fe"), ["Fe\u00b2\u207a", "Fe\u00b3\u207a"])

    def test_he_maps_to_nothing(self):
        self.assertEqual(get_cations_for_element("He"), [])


if __name__ == "__main__":
    unittest.main()
