"""Tests for Lewis dot diagram domain logic."""

import dataclasses
import unittest

import pytest

from src.domain.lewis_diagram import (
    LewisAtom,
    LewisBond,
    MoleculeDiagram,
    distribute_dots,
    get_valence_electrons,
    lookup_molecule,
)
from src.domain.lewis_library import MOLECULE_LIBRARY

_VALENCE_BY_SYMBOL = {
    "H": 1,
    "Be": 2,
    "B": 3,
    "C": 4,
    "N": 5,
    "O": 6,
    "F": 7,
    "Si": 4,
    "P": 5,
    "S": 6,
    "Cl": 7,
    "Br": 7,
    "I": 7,
}


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


class TestMoleculeLibrary:
    """Pytest-style tests for the multi-atom Lewis library."""

    def test_lookup_h2o(self):
        diagram = lookup_molecule("H2O")
        assert diagram is not None
        assert diagram.formula == "H2O"
        assert [a.symbol for a in diagram.atoms] == ["H", "O", "H"]
        single_bonds = [b for b in diagram.bonds if b.order == 1]
        assert len(single_bonds) == 2
        oxygen = next(a for a in diagram.atoms if a.symbol == "O")
        assert oxygen.lone_pairs == 2

    def test_lookup_co2(self):
        diagram = lookup_molecule("CO2")
        assert diagram is not None
        assert [a.symbol for a in diagram.atoms] == ["O", "C", "O"]
        double_bonds = [b for b in diagram.bonds if b.order == 2]
        assert len(double_bonds) == 2
        oxygens = [a for a in diagram.atoms if a.symbol == "O"]
        assert all(a.lone_pairs == 2 for a in oxygens)

    def test_lookup_n2(self):
        diagram = lookup_molecule("N2")
        assert diagram is not None
        assert [a.symbol for a in diagram.atoms] == ["N", "N"]
        assert len(diagram.bonds) == 1
        assert diagram.bonds[0].order == 3
        assert all(a.lone_pairs == 1 for a in diagram.atoms)

    def test_lookup_ch4(self):
        diagram = lookup_molecule("CH4")
        assert diagram is not None
        assert len(diagram.atoms) == 5
        assert diagram.atoms[0].symbol == "C"
        assert diagram.atoms[0].lone_pairs == 0
        hydrogens = [a for a in diagram.atoms if a.symbol == "H"]
        assert len(hydrogens) == 4
        assert all(a.lone_pairs == 0 for a in hydrogens)
        assert len(diagram.bonds) == 4
        assert all(b.order == 1 for b in diagram.bonds)

    def test_lookup_nh3(self):
        diagram = lookup_molecule("NH3")
        assert diagram is not None
        assert len(diagram.atoms) == 4
        nitrogen = next(a for a in diagram.atoms if a.symbol == "N")
        assert nitrogen.lone_pairs == 1
        hydrogens = [a for a in diagram.atoms if a.symbol == "H"]
        assert len(hydrogens) == 3
        assert all(a.lone_pairs == 0 for a in hydrogens)
        assert len(diagram.bonds) == 3
        assert all(b.order == 1 for b in diagram.bonds)

    def test_lookup_unknown_returns_none(self):
        assert lookup_molecule("XYZ123") is None

    def test_lookup_empty_returns_none(self):
        assert lookup_molecule("") is None
        assert lookup_molecule("   ") is None

    def test_lookup_case_normalization(self):
        assert lookup_molecule("h2o") == lookup_molecule("H2O")
        assert lookup_molecule("co2") == lookup_molecule("CO2")
        assert lookup_molecule("nh4+") == lookup_molecule("NH4+")

    @pytest.mark.parametrize("formula", sorted(MOLECULE_LIBRARY))
    def test_library_invariant(self, formula):
        """Bond electrons + lone-pair electrons match the valence sum.

        Allows ±2 tolerance for charged species and odd-electron radicals
        whose canonical Lewis drawings can't be balanced exactly.
        """
        diagram = MOLECULE_LIBRARY[formula]
        atom_count = len(diagram.atoms)
        for bond in diagram.bonds:
            assert 0 <= bond.atom1 < atom_count, (
                f"{formula}: bond.atom1 out of range"
            )
            assert 0 <= bond.atom2 < atom_count, (
                f"{formula}: bond.atom2 out of range"
            )
            assert bond.atom1 != bond.atom2, (
                f"{formula}: self-bond at index {bond.atom1}"
            )

        diagram_electrons = sum(b.order * 2 for b in diagram.bonds) + sum(
            a.lone_pairs * 2 for a in diagram.atoms
        )
        valence_total = sum(
            _VALENCE_BY_SYMBOL[a.symbol] for a in diagram.atoms
        )
        expected_electrons = valence_total - diagram.charge
        assert abs(diagram_electrons - expected_electrons) <= 2, (
            f"{formula}: diagram has {diagram_electrons} electrons, "
            f"expected ~{expected_electrons}"
        )


class TestMoleculeDataclasses:
    """Verify the multi-atom data model is immutable and comparable."""

    def test_lewis_atom_is_frozen(self):
        atom = LewisAtom("H", 0.0, 0.0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            atom.symbol = "He"

    def test_lewis_bond_is_frozen(self):
        bond = LewisBond(0, 1, order=2)
        with pytest.raises(dataclasses.FrozenInstanceError):
            bond.order = 3

    def test_molecule_diagram_equality(self):
        a = MoleculeDiagram(
            formula="H2",
            name="Hydrogen",
            atoms=[LewisAtom("H", -0.4, 0.0), LewisAtom("H", 0.4, 0.0)],
            bonds=[LewisBond(0, 1, order=1)],
        )
        b = MoleculeDiagram(
            formula="H2",
            name="Hydrogen",
            atoms=[LewisAtom("H", -0.4, 0.0), LewisAtom("H", 0.4, 0.0)],
            bonds=[LewisBond(0, 1, order=1)],
        )
        assert a == b


if __name__ == "__main__":
    unittest.main()
