import unittest

from src.ui.formatters import format_info_value, format_value


class TestFormatValue(unittest.TestCase):

    def test_none_returns_na(self):
        self.assertEqual(format_value(None), "n/a")

    def test_custom_na_text(self):
        self.assertEqual(format_value(None, na_text="N/D"), "N/D")

    def test_float_default_precision(self):
        self.assertEqual(format_value(3.14159), "3.142")

    def test_float_custom_precision(self):
        self.assertEqual(format_value(3.14159, decimals=1), "3.1")

    def test_integer_passthrough(self):
        self.assertEqual(format_value(42), "42")

    def test_string_passthrough(self):
        self.assertEqual(format_value("hello"), "hello")


class TestFormatInfoValue(unittest.TestCase):

    def test_none_returns_na(self):
        self.assertEqual(format_info_value("atomic_mass", None), "n/a")

    def test_electronegativity_no_unit(self):
        result = format_info_value("electronegativity", 2.20)
        self.assertNotIn("pm", result)

    def test_atomic_radius_has_pm_unit(self):
        result = format_info_value("atomic_radius", 152.0)
        self.assertIn("pm", result)

    def test_unknown_field_uses_generic(self):
        result = format_info_value("unknown_field", 3.14)
        self.assertEqual(result, "3.140")

    def test_ionization_energy_has_kj_unit(self):
        result = format_info_value("ionization_energy", 5.139)
        self.assertIn("kJ/mol", result)


if __name__ == "__main__":
    unittest.main()
