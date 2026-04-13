"""Tests for Lewis dot diagram domain logic."""

import unittest

from src.domain.lewis_diagram import distribute_dots, get_valence_electrons


class TestGetValenceElectrons(unittest.TestCase):
    """Verify valence electron counts for representative elements."""

    def test_valence_group_1(self):
        element = {"symbol": "Na", "group": 1, "category": "alkali metal"}
        self.assertEqual(get_valence_electrons(element), 1)

    def test_valence_group_2(self):
        element = {"symbol": "Mg", "group": 2, "category": "alkaline earth metal"}
        self.assertEqual(get_valence_electrons(element), 2)

    def test_valence_group_14(self):
        element = {"symbol": "C", "group": 14, "category": "nonmetal"}
        self.assertEqual(get_valence_electrons(element), 4)

    def test_valence_group_17(self):
        element = {"symbol": "Cl", "group": 17, "category": "halogen"}
        self.assertEqual(get_valence_electrons(element), 7)

    def test_valence_group_18(self):
        element = {"symbol": "Ne", "group": 18, "category": "noble gas"}
        self.assertEqual(get_valence_electrons(element), 8)

    def test_valence_helium(self):
        element = {"symbol": "He", "group": 18, "category": "noble gas"}
        self.assertEqual(get_valence_electrons(element), 2)

    def test_valence_transition_metal(self):
        element = {"symbol": "Fe", "group": 8, "category": "transition metal"}
        self.assertIsNone(get_valence_electrons(element))

    def test_valence_lanthanide(self):
        element = {"symbol": "La", "group": 3, "category": "lanthanide"}
        self.assertIsNone(get_valence_electrons(element))

    def test_valence_actinide_no_group(self):
        element = {"symbol": "U", "group": None, "category": "actinide"}
        self.assertIsNone(get_valence_electrons(element))

    def test_valence_group_13(self):
        element = {"symbol": "B", "group": 13, "category": "metalloid"}
        self.assertEqual(get_valence_electrons(element), 3)

    def test_valence_group_15(self):
        element = {"symbol": "N", "group": 15, "category": "nonmetal"}
        self.assertEqual(get_valence_electrons(element), 5)

    def test_valence_group_16(self):
        element = {"symbol": "O", "group": 16, "category": "nonmetal"}
        self.assertEqual(get_valence_electrons(element), 6)


class TestDistributeDots(unittest.TestCase):
    """Verify dot distribution for 1-8 valence electrons."""

    def test_distribute_1(self):
        self.assertEqual(
            distribute_dots(1),
            {"top": 1, "right": 0, "bottom": 0, "left": 0},
        )

    def test_distribute_2(self):
        self.assertEqual(
            distribute_dots(2),
            {"top": 1, "right": 1, "bottom": 0, "left": 0},
        )

    def test_distribute_3(self):
        self.assertEqual(
            distribute_dots(3),
            {"top": 1, "right": 1, "bottom": 1, "left": 0},
        )

    def test_distribute_4(self):
        self.assertEqual(
            distribute_dots(4),
            {"top": 1, "right": 1, "bottom": 1, "left": 1},
        )

    def test_distribute_5(self):
        self.assertEqual(
            distribute_dots(5),
            {"top": 2, "right": 1, "bottom": 1, "left": 1},
        )

    def test_distribute_6(self):
        self.assertEqual(
            distribute_dots(6),
            {"top": 2, "right": 2, "bottom": 1, "left": 1},
        )

    def test_distribute_7(self):
        self.assertEqual(
            distribute_dots(7),
            {"top": 2, "right": 2, "bottom": 2, "left": 1},
        )

    def test_distribute_8(self):
        self.assertEqual(
            distribute_dots(8),
            {"top": 2, "right": 2, "bottom": 2, "left": 2},
        )


if __name__ == "__main__":
    unittest.main()
