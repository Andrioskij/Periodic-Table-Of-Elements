"""Unit tests for InfoPanel and its _IsotopesSection subwidget.

`TestIsotopesSection` covers rendering of empty/valid/malformed isotope
data and the translate fallback. `TestInfoPanel` adds smoke coverage
for the top-level panel (init, set_prompt, set_numeric_ranges) that
previously had no direct tests.

A module-level QApplication singleton is required to instantiate
QWidget subclasses.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication, QLabel

from src.ui.panels.info_panel import InfoPanel, _IsotopesSection

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
        def tr(key):
            return {"no_isotope_data": "Nessun dato sugli isotopi"}.get(key, key)
        self.section.set_content(title="Isotopi", isotopes=[], translate=tr)
        label = self.section.isotopes_layout.itemAt(0).widget()
        self.assertEqual(label.text(), "Nessun dato sugli isotopi")
        self.assertEqual(self.section.title_label.text(), "Isotopi")

    def test_section_has_accessible_name_and_description(self):
        self.assertEqual(self.section.accessibleName(), "Isotopes Section")
        self.assertIn("isotopes", self.section.accessibleDescription().lower())


class TestInfoPanel(unittest.TestCase):
    """Smoke coverage for the top-level InfoPanel widget.

    The detailed behavior of nested sections (isotopes, industrial uses,
    metric visuals) is covered by dedicated tests; this class only
    verifies that the panel instantiates with a usable shell and that
    the public mutation methods do not crash.
    """

    def setUp(self):
        self.panel = InfoPanel("Select an element to see details.")

    def test_instantiation_sets_initial_prompt_text(self):
        self.assertEqual(
            self.panel.prompt_label.text(),
            "Select an element to see details.",
        )
        self.assertEqual(
            self.panel.info_label.text(),
            "Select an element to see details.",
        )

    def test_instantiation_has_accessible_name(self):
        self.assertEqual(self.panel.accessibleName(), "Info Panel")

    def test_set_prompt_updates_prompt_label(self):
        self.panel.set_prompt("fallback prompt", prompt_text="Seleziona un elemento")
        self.assertEqual(self.panel.prompt_label.text(), "Seleziona un elemento")

    def test_set_prompt_uses_first_arg_when_explicit_text_missing(self):
        self.panel.set_prompt("solo fallback")
        self.assertEqual(self.panel.prompt_label.text(), "solo fallback")

    def test_set_numeric_ranges_does_not_crash_with_empty_dict(self):
        # Just verifying the setter accepts the contract; metric rendering
        # is exercised in other tests when a real element is bound.
        self.panel.set_numeric_ranges({})
        self.assertEqual(self.panel.numeric_ranges, {})

    def test_set_numeric_ranges_overwrites_previous_values(self):
        self.panel.set_numeric_ranges({"electronegativity": (0.7, 4.0)})
        self.assertEqual(self.panel.numeric_ranges, {"electronegativity": (0.7, 4.0)})
        self.panel.set_numeric_ranges({"radius": (10.0, 300.0)})
        self.assertEqual(self.panel.numeric_ranges, {"radius": (10.0, 300.0)})


if __name__ == "__main__":
    unittest.main()
