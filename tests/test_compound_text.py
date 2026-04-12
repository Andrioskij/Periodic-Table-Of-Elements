import unittest

from src.ui.compound_text import (
    compose_compound_result_text,
    get_compound_pair_key,
    get_localized_common_compound_name,
)


class TestGetCompoundPairKey(unittest.TestCase):

    def test_alphabetical_order(self):
        self.assertEqual(get_compound_pair_key("Na", "Cl"), "Cl|Na")

    def test_symmetric(self):
        self.assertEqual(
            get_compound_pair_key("O", "Fe"),
            get_compound_pair_key("Fe", "O"),
        )

    def test_same_element(self):
        self.assertEqual(get_compound_pair_key("H", "H"), "H|H")


class TestGetLocalizedCommonCompoundName(unittest.TestCase):

    def test_returns_localized_name(self):
        entry = {"formula": "NaCl", "name_en": "Sodium chloride", "name_it": "Cloruro di sodio"}
        self.assertEqual(get_localized_common_compound_name(entry, "it"), "Cloruro di sodio")

    def test_falls_back_to_english(self):
        entry = {"formula": "NaCl", "name_en": "Sodium chloride"}
        self.assertEqual(get_localized_common_compound_name(entry, "zh"), "Sodium chloride")

    def test_falls_back_to_formula(self):
        entry = {"formula": "NaCl"}
        self.assertEqual(get_localized_common_compound_name(entry, "en"), "NaCl")


class TestComposeCompoundResultText(unittest.TestCase):

    def _make_translate(self):
        texts = {
            "must_select_ab": "Select both A and B.",
            "same_element": "Same element selected.",
            "select_oxidation": "Select oxidation states.",
            "opposite_sign": "Opposite signs required.",
            "formula_label": "Formula",
            "stock_name": "Stock",
            "traditional_name": "Traditional",
            "traditional_na": "n/a",
        }
        return lambda key, **kw: texts.get(key, key)

    def test_missing_element_a(self):
        result = compose_compound_result_text(
            compound_a=None,
            compound_b={"atomic_number": 8, "symbol": "O"},
            first_oxidation=None,
            second_oxidation=None,
            common_section="",
            translate=self._make_translate(),
            build_binary_formula=None,
            build_stock_name=None,
            build_traditional_name=None,
        )
        self.assertIn("Select both A and B", result)

    def test_same_element(self):
        el = {"atomic_number": 11, "symbol": "Na"}
        result = compose_compound_result_text(
            compound_a=el,
            compound_b=el,
            first_oxidation=1,
            second_oxidation=-1,
            common_section="",
            translate=self._make_translate(),
            build_binary_formula=None,
            build_stock_name=None,
            build_traditional_name=None,
        )
        self.assertIn("Same element", result)

    def test_missing_oxidation(self):
        result = compose_compound_result_text(
            compound_a={"atomic_number": 11, "symbol": "Na"},
            compound_b={"atomic_number": 17, "symbol": "Cl"},
            first_oxidation=None,
            second_oxidation=-1,
            common_section="",
            translate=self._make_translate(),
            build_binary_formula=None,
            build_stock_name=None,
            build_traditional_name=None,
        )
        self.assertIn("Select oxidation", result)

    def test_same_sign_rejected(self):
        result = compose_compound_result_text(
            compound_a={"atomic_number": 11, "symbol": "Na"},
            compound_b={"atomic_number": 19, "symbol": "K"},
            first_oxidation=1,
            second_oxidation=1,
            common_section="",
            translate=self._make_translate(),
            build_binary_formula=None,
            build_stock_name=None,
            build_traditional_name=None,
        )
        self.assertIn("Opposite signs", result)

    def test_valid_compound_produces_formula(self):
        result = compose_compound_result_text(
            compound_a={"atomic_number": 11, "symbol": "Na"},
            compound_b={"atomic_number": 17, "symbol": "Cl"},
            first_oxidation=1,
            second_oxidation=-1,
            common_section="",
            translate=self._make_translate(),
            build_binary_formula=lambda c, cc, a, ac: "NaCl",
            build_stock_name=lambda cat, ch, an: "sodium chloride",
            build_traditional_name=lambda cat, ch, an: "n/a",
        )
        self.assertIn("NaCl", result)
        self.assertIn("sodium chloride", result)


if __name__ == "__main__":
    unittest.main()
