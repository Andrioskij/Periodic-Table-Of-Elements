import unittest

from src.ui.compound_text import (
    compose_compound_result_text,
    format_common_compounds_section,
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


class TestFormatCommonCompoundsSection(unittest.TestCase):
    """The preview list of common compounds should subscript formula digits
    that follow a letter or closing paren — same rule as the main formula
    line. Regression coverage for the gap left by the original PR #86.
    """

    def _translate(self, key, **_kw):
        return {"common_compounds": "Common compounds"}.get(key, key)

    def _name(self, entry):
        return entry.get("name_en")

    def test_returns_empty_when_no_compounds(self):
        self.assertEqual(
            format_common_compounds_section(
                [], translate=self._translate, get_localized_name=self._name,
            ),
            "",
        )

    def test_subscripts_digits_after_letter(self):
        # Fe2O3 has two digit runs that follow letters; both must subscript.
        compounds = [{"formula": "Fe2O3", "name_en": "iron(III) oxide"}]
        section = format_common_compounds_section(
            compounds, translate=self._translate, get_localized_name=self._name,
        )
        self.assertIn("Fe₂O₃", section)
        self.assertNotIn("Fe2O3", section)

    def test_preserves_compounds_without_digits(self):
        compounds = [{"formula": "NaCl", "name_en": "sodium chloride"}]
        section = format_common_compounds_section(
            compounds, translate=self._translate, get_localized_name=self._name,
        )
        self.assertIn("NaCl", section)


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
