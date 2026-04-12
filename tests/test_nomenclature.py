import unittest

from src.domain.nomenclature import (
    build_stock_name,
    build_traditional_name,
    int_to_roman,
)


class TestIntToRoman(unittest.TestCase):

    def test_basic_values(self):
        self.assertEqual(int_to_roman(1), "I")
        self.assertEqual(int_to_roman(2), "II")
        self.assertEqual(int_to_roman(3), "III")
        self.assertEqual(int_to_roman(4), "IV")
        self.assertEqual(int_to_roman(5), "V")
        self.assertEqual(int_to_roman(7), "VII")

    def test_none_returns_empty(self):
        self.assertEqual(int_to_roman(None), "")

    def test_zero_returns_empty(self):
        self.assertEqual(int_to_roman(0), "")

    def test_negative_returns_empty(self):
        self.assertEqual(int_to_roman(-3), "")

    def test_larger_values(self):
        self.assertEqual(int_to_roman(9), "IX")
        self.assertEqual(int_to_roman(14), "XIV")
        self.assertEqual(int_to_roman(40), "XL")


class TestBuildStockName(unittest.TestCase):

    def _make_formatter(self):
        def fmt(anion, cation, roman=None):
            if roman:
                return f"{cation}({roman}) {anion}"
            return f"{cation} {anion}"
        return fmt

    def test_single_oxidation_no_roman(self):
        result = build_stock_name(
            anion_name="chloride",
            cation_name="sodium",
            cation_charge=1,
            oxidation_states=[1],
            traditional_na="n/a",
            format_stock_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "sodium chloride")

    def test_multiple_oxidation_adds_roman(self):
        result = build_stock_name(
            anion_name="chloride",
            cation_name="iron",
            cation_charge=3,
            oxidation_states=[2, 3],
            traditional_na="n/a",
            format_stock_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "iron(III) chloride")

    def test_none_anion_returns_na(self):
        result = build_stock_name(
            anion_name=None,
            cation_name="iron",
            cation_charge=3,
            oxidation_states=[2, 3],
            traditional_na="n/a",
            format_stock_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "n/a")


class TestBuildTraditionalName(unittest.TestCase):

    def _make_formatter(self):
        def fmt(anion, epithet):
            return f"{epithet} {anion}"
        return fmt

    def test_low_oxidation_state(self):
        result = build_traditional_name(
            anion_name="chloride",
            cation_charge=2,
            oxidation_states=[2, 3],
            low_name="ferrous",
            high_name="ferric",
            traditional_na="n/a",
            format_traditional_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "ferrous chloride")

    def test_high_oxidation_state(self):
        result = build_traditional_name(
            anion_name="chloride",
            cation_charge=3,
            oxidation_states=[2, 3],
            low_name="ferrous",
            high_name="ferric",
            traditional_na="n/a",
            format_traditional_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "ferric chloride")

    def test_single_state_returns_na(self):
        result = build_traditional_name(
            anion_name="chloride",
            cation_charge=1,
            oxidation_states=[1],
            low_name="",
            high_name="",
            traditional_na="n/a",
            format_traditional_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "n/a")

    def test_none_anion_returns_na(self):
        result = build_traditional_name(
            anion_name=None,
            cation_charge=2,
            oxidation_states=[2, 3],
            low_name="ferrous",
            high_name="ferric",
            traditional_na="n/a",
            format_traditional_compound_name=self._make_formatter(),
        )
        self.assertEqual(result, "n/a")


if __name__ == "__main__":
    unittest.main()
