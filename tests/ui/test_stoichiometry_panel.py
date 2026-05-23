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

    def test_help_button_hidden_without_help_body(self):
        self.panel.apply_language(
            title="t", prompt="p", balance_text="b", calc_masses_text="cm",
            mass_section_text="ms", error_prefix="e",
        )
        self.assertFalse(self.panel.help_button.isVisibleTo(self.panel))

    def test_help_button_visible_when_help_body_provided(self):
        self.panel.apply_language(
            title="t", prompt="p", balance_text="b", calc_masses_text="cm",
            mass_section_text="ms", error_prefix="e",
            help_body="Bilancia un'equazione.\n\nEsempio: `Fe + O2 -> Fe2O3`.",
            help_close_text="Chiudi",
        )
        self.assertTrue(self.panel.help_button.isVisibleTo(self.panel))
        self.assertIn("Fe2O3", self.panel._help_body)

    def test_example_button_visibility_round_trip(self):
        self.panel.apply_language(
            title="t", prompt="p", balance_text="b", calc_masses_text="cm",
            mass_section_text="ms", error_prefix="e",
        )
        self.assertFalse(self.panel.example_button.isVisibleTo(self.panel))
        self.panel.apply_language(
            title="t", prompt="p", balance_text="b", calc_masses_text="cm",
            mass_section_text="ms", error_prefix="e",
            example_text="Prova un esempio",
        )
        self.assertTrue(self.panel.example_button.isVisibleTo(self.panel))

    def test_example_click_fills_equation_input(self):
        self.panel.apply_language(
            title="t", prompt="p", balance_text="b", calc_masses_text="cm",
            mass_section_text="ms", error_prefix="e",
            example_text="Prova",
        )
        self.panel.example_button.click()
        self.assertEqual(self.panel.equation_input.text(), "Fe + O2 -> Fe2O3")


if __name__ == "__main__":
    unittest.main()
