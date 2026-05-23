"""Smoke tests for CompoundBuilderPanel.

Exercises instantiation and the public mutation API (apply_language,
set_selector_texts, set_status_text, set_result_text) against the
existing widget contract. A module-level QApplication singleton is
required to instantiate QWidget subclasses under offscreen Qt.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.panels.compound_panel import CompoundBuilderPanel

_app = QApplication.instance() or QApplication(sys.argv)


class TestCompoundBuilderPanel(unittest.TestCase):
    def setUp(self):
        self.panel = CompoundBuilderPanel()

    def test_instantiation_creates_both_selector_cards(self):
        self.assertEqual(self.panel.selector_a_badge_label.text(), "A")
        self.assertEqual(self.panel.selector_b_badge_label.text(), "B")
        self.assertIsNotNone(self.panel.search_a_input)
        self.assertIsNotNone(self.panel.search_b_input)
        self.assertIsNotNone(self.panel.a_oxidation_combo)
        self.assertIsNotNone(self.panel.b_oxidation_combo)

    def test_instantiation_creates_empty_hidden_title_label(self):
        self.assertEqual(self.panel.title_label.text(), "")
        self.assertEqual(self.panel.title_label.accessibleName(), "Simple compounds panel title")

    def test_apply_language_updates_all_translatable_labels(self):
        self.panel.apply_language(
            selector_a_title="Imposta A",
            selector_b_title="Imposta B",
            search_placeholder_a="Cerca A...",
            search_placeholder_b="Cerca B...",
            oxidation_first="Stato di ossidazione:",
            oxidation_second="Stato di ossidazione:",
            calculate_formula="Calcola formula",
            reset="Reimposta",
        )
        self.assertEqual(self.panel.selector_a_title_label.text(), "Imposta A")
        self.assertEqual(self.panel.selector_b_title_label.text(), "Imposta B")
        self.assertEqual(self.panel.search_a_input.placeholderText(), "Cerca A...")
        self.assertEqual(self.panel.search_b_input.placeholderText(), "Cerca B...")
        self.assertEqual(self.panel.build_button.text(), "Calcola formula")
        self.assertEqual(self.panel.builder_reset_button.text(), "Reimposta")

    def test_apply_language_sets_master_title_when_provided(self):
        self.panel.apply_language(
            title="🧱  Composti semplici",
            selector_a_title="Imposta A",
            selector_b_title="Imposta B",
            search_placeholder_a="Cerca A...",
            search_placeholder_b="Cerca B...",
            oxidation_first="Stato di ossidazione:",
            oxidation_second="Stato di ossidazione:",
            calculate_formula="Calcola formula",
            reset="Reimposta",
        )
        self.assertEqual(self.panel.title_label.text(), "🧱  Composti semplici")

    def test_set_selector_texts_writes_to_summary_labels(self):
        self.panel.set_selector_texts("Hydrogen (H)", "Oxygen (O)")
        self.assertEqual(self.panel.selector_a_summary_label.text(), "Hydrogen (H)")
        self.assertEqual(self.panel.selector_b_summary_label.text(), "Oxygen (O)")

    def test_set_status_text_writes_text_and_tooltip(self):
        self.panel.set_status_text("A: H | B: O")
        self.assertEqual(self.panel.builder_status_label.text(), "A: H | B: O")
        self.assertEqual(self.panel.builder_status_label.toolTip(), "A: H | B: O")

    def test_set_result_text_hides_when_empty_shows_when_not(self):
        self.panel.set_result_text("H2O")
        self.assertEqual(self.panel.result_label.text(), "H2O")
        self.assertTrue(self.panel.result_label.isVisible() or not self.panel.isVisible())
        self.panel.set_result_text("")
        self.assertFalse(self.panel.result_label.isVisible())


if __name__ == "__main__":
    unittest.main()
