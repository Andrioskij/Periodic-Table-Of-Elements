"""Smoke tests for LewisPanel instantiation and translatable-text API.

The pre-existing `test_lewis_panel_molecules.py` covers the
molecule-library logic against the lewis library, but the panel
widget itself (init, set_prompt, apply_language) had no smoke
coverage. This file fills that gap.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.panels.lewis_panel import LewisPanel

_app = QApplication.instance() or QApplication(sys.argv)


class TestLewisPanel(unittest.TestCase):
    def setUp(self):
        self.panel = LewisPanel("Lewis Diagram", "Select an element to see its Lewis dot diagram.")

    def test_instantiation_sets_initial_title_and_prompt(self):
        self.assertEqual(self.panel.title_label.text(), "Lewis Diagram")
        self.assertEqual(
            self.panel.diagram_label.text(),
            "Select an element to see its Lewis dot diagram.",
        )

    def test_set_prompt_updates_title_and_diagram_prompt(self):
        self.panel.set_prompt("Diagramma di Lewis", "Seleziona un elemento.")
        self.assertEqual(self.panel.title_label.text(), "Diagramma di Lewis")
        self.assertEqual(self.panel.diagram_label.text(), "Seleziona un elemento.")

    def test_apply_language_updates_title_and_placeholder(self):
        self.panel.apply_language(
            title="Diagramma di Lewis",
            prompt="Seleziona un elemento.",
            input_placeholder="Inserisci formula molecola (es. H2O)",
            show_button_text="Mostra",
            not_in_library_text="Struttura non disponibile nella libreria.",
        )
        self.assertEqual(self.panel.title_label.text(), "Diagramma di Lewis")
        self.assertEqual(
            self.panel.formula_input.placeholderText(),
            "Inserisci formula molecola (es. H2O)",
        )
        self.assertEqual(self.panel.show_molecule_button.text(), "Mostra")


if __name__ == "__main__":
    unittest.main()
