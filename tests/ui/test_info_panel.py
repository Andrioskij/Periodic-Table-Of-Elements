"""Unit tests for the _IsotopesSection widget in info_panel.

Covers rendering of empty/valid/malformed isotope data and the translate fallback.
A module-level QApplication singleton is required to instantiate QWidget subclasses.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication, QLabel

from src.ui.panels.info_panel import _IsotopesSection

_app = QApplication.instance() or QApplication(sys.argv)


class TestIsotopesSection(unittest.TestCase):
    def setUp(self):
        self.section = _IsotopesSection()

    def test_empty_isotopes_shows_fallback_label(self):
        self.section.set_content(title="Isotopes", isotopes=[])
        self.assertEqual(self.section.isotopes_layout.count(), 1)
        label = self.section.isotopes_layout.itemAt(0).widget()
        self.assertIsInstance(label, QLabel)
        self.assertEqual(label.text(), "No isotope data available")

    def test_valid_isotope_with_abundance(self):
        data = [{"mass_number": 1, "abundance": 99.9885, "half_life": None, "name": "Protium"}]
        self.section.set_content(title="Isotopes", isotopes=data)
        self.assertEqual(self.section.isotopes_layout.count(), 1)
        text = self.section.isotopes_layout.itemAt(0).widget().text()
        self.assertIn("Protium", text)
        self.assertIn("mass 1", text)
        self.assertIn("99.99", text)

    def test_valid_isotope_with_half_life(self):
        data = [{"mass_number": 3, "abundance": None, "half_life": "12.3 years", "name": "Tritium"}]
        self.section.set_content(title="Isotopes", isotopes=data)
        self.assertEqual(self.section.isotopes_layout.count(), 1)
        text = self.section.isotopes_layout.itemAt(0).widget().text()
        self.assertIn("Tritium", text)
        self.assertIn("12.3 years", text)

    def test_malformed_data_does_not_crash(self):
        data = [{"unexpected_key": "value"}]
        self.section.set_content(title="Isotopes", isotopes=data)
        self.assertEqual(self.section.isotopes_layout.count(), 1)
        text = self.section.isotopes_layout.itemAt(0).widget().text()
        self.assertIn("Isotope-?", text)

    def test_translate_fallback_used_for_empty(self):
        tr = lambda key: {"no_isotope_data": "Nessun dato sugli isotopi"}.get(key, key)
        self.section.set_content(title="Isotopi", isotopes=[], translate=tr)
        label = self.section.isotopes_layout.itemAt(0).widget()
        self.assertEqual(label.text(), "Nessun dato sugli isotopi")
        self.assertEqual(self.section.title_label.text(), "Isotopi")

    def test_section_has_accessible_name_and_description(self):
        self.assertEqual(self.section.accessibleName(), "Isotopes Section")
        self.assertIn("isotopes", self.section.accessibleDescription().lower())


if __name__ == "__main__":
    unittest.main()
