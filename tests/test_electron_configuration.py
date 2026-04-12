import unittest

from src.domain.electron_configuration import (
    configuration_to_map,
    expand_configuration,
    fill_boxes,
)


class TestExpandConfiguration(unittest.TestCase):

    def test_empty_returns_empty(self):
        self.assertEqual(expand_configuration(""), [])
        self.assertEqual(expand_configuration(None), [])

    def test_no_core_abbreviation(self):
        tokens = expand_configuration("1s2 2s2 2p6")
        self.assertEqual(tokens, ["1s2", "2s2", "2p6"])

    def test_expands_helium_core(self):
        tokens = expand_configuration("[He] 2s1")
        self.assertEqual(tokens, ["1s2", "2s1"])

    def test_expands_argon_core(self):
        tokens = expand_configuration("[Ar] 4s1")
        self.assertIn("3p6", tokens)
        self.assertEqual(tokens[-1], "4s1")

    def test_expands_xenon_core(self):
        tokens = expand_configuration("[Xe] 6s2")
        self.assertIn("5p6", tokens)
        self.assertEqual(tokens[-1], "6s2")


class TestConfigurationToMap(unittest.TestCase):

    def test_hydrogen(self):
        result = configuration_to_map("1s1")
        self.assertEqual(result, {"1s": 1})

    def test_oxygen(self):
        result = configuration_to_map("[He] 2s2 2p4")
        self.assertEqual(result["1s"], 2)
        self.assertEqual(result["2s"], 2)
        self.assertEqual(result["2p"], 4)

    def test_iron(self):
        result = configuration_to_map("[Ar] 3d6 4s2")
        self.assertEqual(result["3d"], 6)
        self.assertEqual(result["4s"], 2)
        self.assertIn("3p", result)


class TestFillBoxes(unittest.TestCase):

    def test_single_electron_in_s(self):
        self.assertEqual(fill_boxes(1, 1), [1])

    def test_full_s_orbital(self):
        self.assertEqual(fill_boxes(2, 1), [2])

    def test_hund_rule_three_in_p(self):
        # 3 electrons in 3 p-boxes: one each (Hund's rule)
        self.assertEqual(fill_boxes(3, 3), [1, 1, 1])

    def test_four_in_p(self):
        # 4 electrons: first pass fills [1,1,1], second pass adds to first
        self.assertEqual(fill_boxes(4, 3), [2, 1, 1])

    def test_full_p_orbital(self):
        self.assertEqual(fill_boxes(6, 3), [2, 2, 2])

    def test_hund_rule_five_in_d(self):
        # 5 electrons in 5 d-boxes: one each (half-filled)
        self.assertEqual(fill_boxes(5, 5), [1, 1, 1, 1, 1])

    def test_full_d_orbital(self):
        self.assertEqual(fill_boxes(10, 5), [2, 2, 2, 2, 2])

    def test_zero_electrons(self):
        self.assertEqual(fill_boxes(0, 3), [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
