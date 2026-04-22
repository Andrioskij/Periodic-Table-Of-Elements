"""Unit tests for MolarMassPanel.

Exercises instantiation, set_prompt(), and apply_language() — all against the
existing public API. We pass an empty element list since these tests do not
trigger molar-mass computation.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.panels.molar_mass_panel import MolarMassPanel

_app = QApplication.instance() or QApplication(sys.argv)


class TestMolarMassPanel(unittest.TestCase):
    def setUp(self):
        self.panel = MolarMassPanel("Molar Mass", "Enter a formula to compute.", elements=[])

    def test_instantiation_sets_initial_texts(self):
        self.assertEqual(self.panel.title_label.text(), "Molar Mass")
        self.assertEqual(self.panel.result_label.text(), "Enter a formula to compute.")
        self.assertEqual(self.panel._error_prefix, "Error")

    def test_set_prompt_updates_result_label(self):
        self.panel.set_prompt("fallback", prompt_text="Scrivi una formula")
        self.assertEqual(self.panel.result_label.text(), "Scrivi una formula")
        self.panel.set_prompt("solo fallback")
        self.assertEqual(self.panel.result_label.text(), "solo fallback")

    def test_apply_language_updates_all_labels(self):
        self.panel.apply_language(
            title="Massa molare",
            prompt="Inserisci una formula",
            button_text="Calcola",
            error_prefix="Errore",
        )
        self.assertEqual(self.panel.title_label.text(), "Massa molare")
        self.assertEqual(self.panel.result_label.text(), "Inserisci una formula")
        self.assertEqual(self.panel.calculate_button.text(), "Calcola")
        self.assertEqual(self.panel._error_prefix, "Errore")


if __name__ == "__main__":
    unittest.main()
