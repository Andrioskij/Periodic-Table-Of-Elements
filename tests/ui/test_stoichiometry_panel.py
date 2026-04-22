"""Unit tests for StoichiometryPanel.

Exercises instantiation, set_prompt() (which should also hide the mass section
and any previous mass result), and apply_language() against the existing public
API. An empty element list is safe because these tests do not trigger equation
balancing or mass computation.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.panels.stoichiometry_panel import StoichiometryPanel

_app = QApplication.instance() or QApplication(sys.argv)


class TestStoichiometryPanel(unittest.TestCase):
    def setUp(self):
        self.panel = StoichiometryPanel(
            "Stoichiometry",
            "Enter an unbalanced equation.",
            elements=[],
        )

    def test_instantiation_sets_initial_texts(self):
        self.assertEqual(self.panel.title_label.text(), "Stoichiometry")
        self.assertEqual(self.panel.result_label.text(), "Enter an unbalanced equation.")
        self.assertFalse(self.panel.mass_section.isVisible())
        self.assertFalse(self.panel.mass_result_label.isVisible())
        self.assertEqual(self.panel._error_prefix, "Error")

    def test_set_prompt_updates_label_and_hides_sections(self):
        # Force visible first to verify set_prompt hides them.
        self.panel.mass_section.setVisible(True)
        self.panel.mass_result_label.setVisible(True)
        self.panel.set_prompt("fallback", prompt_text="Prompt IT")
        self.assertEqual(self.panel.result_label.text(), "Prompt IT")
        self.assertFalse(self.panel.mass_section.isVisible())
        self.assertFalse(self.panel.mass_result_label.isVisible())

    def test_apply_language_updates_all_labels(self):
        self.panel.apply_language(
            title="Stechiometria",
            prompt="Inserisci equazione",
            balance_text="Bilancia",
            calc_masses_text="Calcola masse",
            mass_section_text="Inserisci massa:",
            error_prefix="Errore",
        )
        self.assertEqual(self.panel.title_label.text(), "Stechiometria")
        self.assertEqual(self.panel.result_label.text(), "Inserisci equazione")
        self.assertEqual(self.panel.balance_button.text(), "Bilancia")
        self.assertEqual(self.panel.calc_mass_button.text(), "Calcola masse")
        self.assertEqual(self.panel._mass_section_text, "Inserisci massa:")
        self.assertEqual(self.panel._error_prefix, "Errore")


if __name__ == "__main__":
    unittest.main()
