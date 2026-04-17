"""Unit tests for SolubilityPanel.

Exercises instantiation, apply_language() updates, and the cation/anion quick-check
(Na+/Cl- -> soluble, Ag+/Cl- -> insoluble) via the _on_check handler. The domain
lookup itself is already covered elsewhere; these tests confirm the panel wires
combo selections to verdict_label correctly.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.panels.solubility_panel import SolubilityPanel


_app = QApplication.instance() or QApplication(sys.argv)


# Localized strings used by apply_language tests.
_LANG_KWARGS = {
    "title": "Solubilita",
    "prompt": "Seleziona ioni",
    "cation_label": "Catione",
    "anion_label": "Anione",
    "check_text": "Verifica",
    "soluble_text": "Solubile",
    "insoluble_text": "Insolubile",
    "slightly_text": "Poco solubile",
    "rule_label": "Regola:",
    "exceptions_label": "Eccezioni:",
    "legend_title": "Legenda",
    "rule_alkali": "Alcali solubili",
    "rule_nitrate_acetate": "Nitrati e acetati solubili",
    "rule_halide": "Alogenuri solubili tranne Ag, Pb, Hg",
    "rule_sulfate": "Solfati solubili con eccezioni",
    "rule_hydroxide": "Idrossidi insolubili con eccezioni",
    "rule_carbonate_phosphate_sulfide": "Carbonati, fosfati, solfuri insolubili",
    "rule_default": "Nessuna regola specifica; assunto insolubile.",
}


class TestSolubilityPanel(unittest.TestCase):
    def setUp(self):
        self.panel = SolubilityPanel("Solubility", "Select ions and check.")

    def test_instantiation_populates_combos(self):
        self.assertEqual(self.panel.title_label.text(), "Solubility")
        self.assertGreater(self.panel.cation_combo.count(), 0)
        self.assertGreater(self.panel.anion_combo.count(), 0)

    def test_apply_language_updates_labels(self):
        self.panel.apply_language(**_LANG_KWARGS)
        self.assertEqual(self.panel.title_label.text(), "Solubilita")
        self.assertEqual(self.panel._prompt_text, "Seleziona ioni")
        self.assertEqual(self.panel.check_button.text(), "Verifica")
        self.assertEqual(self.panel._soluble_text, "Solubile")
        self.assertEqual(self.panel._insoluble_text, "Insolubile")

    def test_quick_check_sodium_chloride_soluble(self):
        self.panel.apply_language(**_LANG_KWARGS)
        self.panel.cation_combo.setCurrentText("Na\u207a")
        self.panel.anion_combo.setCurrentText("Cl\u207b")
        self.panel._on_check()
        self.assertIn("Solubile", self.panel.verdict_label.text())

    def test_quick_check_silver_chloride_insoluble(self):
        self.panel.apply_language(**_LANG_KWARGS)
        self.panel.cation_combo.setCurrentText("Ag\u207a")
        self.panel.anion_combo.setCurrentText("Cl\u207b")
        self.panel._on_check()
        self.assertIn("Insolubile", self.panel.verdict_label.text())

    def test_matrix_cells_accessibility_non_empty(self):
        entries = self.panel._matrix_cell_accessibility
        self.assertGreater(len(entries), 0)
        for entry in entries:
            self.assertTrue(entry)
        joined = " | ".join(entries)
        self.assertIn("Na\u207a", joined)
        self.assertIn("Cl\u207b", joined)
        self.assertIn("Na\u207a + Cl\u207b", joined)

    def test_matrix_description_includes_localized_verdict(self):
        self.panel.apply_language(**_LANG_KWARGS)
        entries = self.panel._matrix_cell_accessibility
        joined = " | ".join(entries)
        self.assertIn("Solubile", joined)
        description = self.panel.matrix_label.accessibleDescription()
        self.assertIn("Na\u207a", description)
        self.assertIn("Cl\u207b", description)


if __name__ == "__main__":
    unittest.main()
