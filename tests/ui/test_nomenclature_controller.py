"""Unit tests for NomenclatureController.

Pure-Python tests using a real `nomenclature_data.json` payload and
a fake `language_controller` that just exposes a mutable
``current_language``. Exercises the wrappers' wiring (right data /
language flowing through to the underlying module-level helpers)
without any Qt dependency.
"""

import json
import unittest
from pathlib import Path

from src.ui.controllers.nomenclature_controller import NomenclatureController


class _FakeLanguageController:
    """Mimics the LanguageController surface NomenclatureController reads."""

    def __init__(self, code="en"):
        self.current_language = code


def _load_nomenclature_data():
    path = Path(__file__).resolve().parents[2] / "data" / "reference" / "nomenclature_data.json"
    return json.loads(path.read_text(encoding="utf-8"))


class TestNomenclatureControllerLookups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _load_nomenclature_data()

    def setUp(self):
        self.lang = _FakeLanguageController("en")
        self.controller = NomenclatureController(self.data, self.lang)

    def test_current_language_proxies_to_language_controller(self):
        self.assertEqual(self.controller.current_language, "en")
        self.lang.current_language = "it"
        self.assertEqual(self.controller.current_language, "it")

    def test_get_localized_element_name_en(self):
        sodium = {"symbol": "Na", "name": "Sodium"}
        self.assertEqual(
            self.controller.get_localized_element_name(sodium), "sodium",
        )

    def test_get_localized_element_name_it(self):
        self.lang.current_language = "it"
        sodium = {"symbol": "Na", "name": "Sodium"}
        self.assertEqual(
            self.controller.get_localized_element_name(sodium), "sodio",
        )

    def test_get_localized_anion_name_en(self):
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        self.assertEqual(
            self.controller.get_localized_anion_name(chlorine), "chloride",
        )

    def test_get_localized_anion_name_it(self):
        self.lang.current_language = "it"
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        self.assertEqual(
            self.controller.get_localized_anion_name(chlorine), "cloruro",
        )


class TestNomenclatureControllerFormatters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _load_nomenclature_data()

    def setUp(self):
        self.lang = _FakeLanguageController("en")
        self.controller = NomenclatureController(self.data, self.lang)

    def test_int_to_roman(self):
        self.assertEqual(self.controller.int_to_roman(3), "III")
        self.assertEqual(self.controller.int_to_roman(4), "IV")
        self.assertEqual(self.controller.int_to_roman(0), "")

    def test_format_formula_part_singleton_drops_subscript(self):
        # `Na1` collapses to `Na`; `O2` keeps the `2`.
        self.assertEqual(self.controller.format_formula_part("Na", 1), "Na")
        self.assertEqual(self.controller.format_formula_part("O", 2), "O2")

    def test_build_binary_formula_sodium_chloride(self):
        # NaCl is the canonical 1:1 ionic binary; charges +1/-1, GCD=1.
        formula = self.controller.build_binary_formula("Na", 1, "Cl", -1)
        self.assertEqual(formula, "NaCl")

    def test_build_binary_formula_aluminium_oxide(self):
        # Al(III) + O(-II) → Al2O3 via GCD reduction.
        formula = self.controller.build_binary_formula("Al", 3, "O", -2)
        self.assertEqual(formula, "Al2O3")

    def test_format_stock_compound_name_en(self):
        # English naming pattern is "{cation} {anion}".
        name = self.controller.format_stock_compound_name(
            anion_name="chloride", cation_name="sodium",
        )
        self.assertEqual(name, "sodium chloride")

    def test_format_stock_compound_name_it_uses_di_pattern(self):
        # Italian pattern is "{anion} di {cation}".
        self.lang.current_language = "it"
        name = self.controller.format_stock_compound_name(
            anion_name="cloruro", cation_name="sodio",
        )
        self.assertEqual(name, "cloruro di sodio")

    def test_format_stock_compound_name_with_roman(self):
        # Multi-state cation: include roman numeral marker.
        name = self.controller.format_stock_compound_name(
            anion_name="chloride", cation_name="iron", roman="III",
        )
        self.assertEqual(name, "iron(III) chloride")

    def test_format_stock_compound_name_it_with_roman_has_no_space(self):
        # Italian convention from the curated common-compounds dataset:
        # "ossido di ferro(III)" - no space between cation name and "(III)".
        self.lang.current_language = "it"
        name = self.controller.format_stock_compound_name(
            anion_name="ossido", cation_name="ferro", roman="III",
        )
        self.assertEqual(name, "ossido di ferro(III)")


class TestNomenclatureControllerCommonCompounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = _load_nomenclature_data()

    def setUp(self):
        self.lang = _FakeLanguageController("en")
        self.controller = NomenclatureController(self.data, self.lang)

    def test_common_compounds_returns_empty_when_either_missing(self):
        h = {"symbol": "H", "atomic_number": 1}
        self.assertEqual(
            self.controller.get_common_compounds_for_pair(h, None), [],
        )
        self.assertEqual(
            self.controller.get_common_compounds_for_pair(None, h), [],
        )
        self.assertEqual(
            self.controller.get_common_compounds_for_pair(None, None), [],
        )

    def test_compound_pair_key_is_symmetric_after_sort(self):
        # Key generation is deterministic; same pair should map to one key
        # regardless of which side was passed first.
        key_ab = self.controller.get_compound_pair_key("Na", "Cl")
        key_ba = self.controller.get_compound_pair_key("Cl", "Na")
        self.assertEqual(key_ab, key_ba)


class TestNomenclatureControllerBuildNames(unittest.TestCase):
    """End-to-end builds that thread the language + dataset through
    multiple wrappers — the high-value integration the controller is
    meant to enable as a single testable surface."""

    @classmethod
    def setUpClass(cls):
        cls.data = _load_nomenclature_data()

    def setUp(self):
        self.lang = _FakeLanguageController("en")
        self.controller = NomenclatureController(self.data, self.lang)

    def test_build_stock_name_single_state_cation(self):
        # Na has a single +1 state → no roman numeral.
        sodium = {"symbol": "Na", "name": "Sodium",
                  "oxidation_states": "+1"}
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        self.assertEqual(
            self.controller.build_stock_name(sodium, 1, chlorine),
            "sodium chloride",
        )

    def test_build_stock_name_multi_state_cation_emits_roman(self):
        # Fe has +2/+3 → roman numeral must appear.
        iron = {"symbol": "Fe", "name": "Iron",
                "oxidation_states": "+2, +3"}
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        name = self.controller.build_stock_name(iron, 3, chlorine)
        self.assertEqual(name, "iron(III) chloride")

    def test_build_traditional_name_returns_na_for_single_state_cation(self):
        # Na with only +1 has no -ous/-ic distinction → NA fallback.
        sodium = {"symbol": "Na", "name": "Sodium",
                  "oxidation_states": "+1"}
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        # The localized traditional_na string itself isn't asserted
        # here; the contract is that the helper returns it (truthy
        # placeholder, not the actual traditional epithet).
        name = self.controller.build_traditional_name(sodium, 1, chlorine)
        self.assertTrue(name)
        self.assertNotIn("chloride", name.lower())

    def test_build_traditional_name_uses_ic_suffix_for_higher_state(self):
        # Fe at +3 (the higher of +2/+3) → "ferric" in EN.
        iron = {"symbol": "Fe", "name": "Iron",
                "oxidation_states": "+2, +3"}
        chlorine = {"symbol": "Cl", "name": "Chlorine"}
        name = self.controller.build_traditional_name(iron, 3, chlorine)
        self.assertIn("ferric", name.lower())


if __name__ == "__main__":
    unittest.main()
