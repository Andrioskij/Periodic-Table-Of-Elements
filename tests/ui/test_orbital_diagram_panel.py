"""Unit tests for OrbitalDiagramPanel.

`TestOrbitalDiagramAccessibility` covers the original a11y contract
(`diagram_label.accessibleName` is updated with the localized config
or the "not available" fallback). `TestOrbitalDiagramPanelLifecycle`
adds smoke coverage for instantiation, `set_prompt`, `apply_theme`,
and the pixmap rendering happy/fallback paths.

A module-level QApplication singleton is required to instantiate
QWidget subclasses under offscreen Qt.
"""

import sys
import unittest

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

from src.ui.panels.orbital_diagram_panel import OrbitalDiagramPanel

_app = QApplication.instance() or QApplication(sys.argv)


def _translate(key, **kwargs):
    templates = {
        "diagram_title_symbol": "Diagram: {symbol}",
        "diagram_not_available": "Diagram not available",
        "diagram_accessible_name": "Orbital diagram for {symbol}: {config}",
    }
    template = templates.get(key, key)
    return template.format(**kwargs) if kwargs else template


class TestOrbitalDiagramAccessibility(unittest.TestCase):
    def setUp(self):
        self.panel = OrbitalDiagramPanel("Orbital diagram", "Select an element.")

    def test_accessible_name_includes_symbol_and_config(self):
        element = {"symbol": "H", "electron_configuration": "1s1"}
        self.panel.show_orbital_diagram(
            element, translate=_translate, cell_size=60, format_value=str,
        )
        accessible_name = self.panel.diagram_label.accessibleName()
        self.assertIn("H", accessible_name)
        self.assertIn("1s1", accessible_name)

    def test_accessible_name_falls_back_when_config_missing(self):
        element = {"symbol": "X", "electron_configuration": None}
        self.panel.show_orbital_diagram(
            element, translate=_translate, cell_size=60, format_value=str,
        )
        self.assertEqual(
            self.panel.diagram_label.accessibleName(),
            "Diagram not available",
        )


class TestOrbitalDiagramPanelLifecycle(unittest.TestCase):
    """Smoke coverage for instantiation, set_prompt, apply_theme, and the
    pixmap render path. The detailed accessibility behavior is covered
    by `TestOrbitalDiagramAccessibility` above."""

    def setUp(self):
        self.panel = OrbitalDiagramPanel(
            "Electron configuration",
            "Select an element to display the orbital diagram.",
        )

    def test_instantiation_sets_initial_title_and_prompt(self):
        self.assertEqual(self.panel.title_label.text(), "Electron configuration")
        self.assertEqual(
            self.panel.diagram_label.text(),
            "Select an element to display the orbital diagram.",
        )
        self.assertIsNone(self.panel._last_render)

    def test_instantiation_has_accessible_names(self):
        self.assertEqual(self.panel.accessibleName(), "Orbital Diagram Panel")
        self.assertEqual(self.panel.title_label.accessibleName(), "Orbital diagram title")
        self.assertEqual(self.panel.diagram_label.accessibleName(), "Orbital diagram prompt")

    def test_set_prompt_updates_title_clears_pixmap_and_resets_last_render(self):
        # Seed _last_render so we can confirm set_prompt clears it.
        self.panel._last_render = ("1s1", "H", 50)
        self.panel.set_prompt("Configurazione elettronica", "Seleziona un elemento.")
        self.assertEqual(self.panel.title_label.text(), "Configurazione elettronica")
        self.assertEqual(self.panel.diagram_label.text(), "Seleziona un elemento.")
        self.assertTrue(self.panel.diagram_label.pixmap().isNull())
        self.assertIsNone(self.panel._last_render)

    def test_apply_theme_no_op_when_same_theme(self):
        original_theme = self.panel._theme
        self.panel.apply_theme("dark")
        self.assertIs(self.panel._theme, original_theme)

    def test_apply_theme_switches_palette_without_last_render(self):
        self.panel.apply_theme("light")
        self.assertIsNotNone(self.panel._theme)
        # No prior render → no pixmap should appear from the theme switch.
        self.assertTrue(self.panel.diagram_label.pixmap().isNull())

    def test_show_orbital_diagram_renders_pixmap_for_hydrogen(self):
        hydrogen = {"symbol": "H", "electron_configuration": "1s1"}
        self.panel.show_orbital_diagram(
            hydrogen, translate=_translate, cell_size=50, format_value=str,
        )
        self.assertIsInstance(self.panel.diagram_label.pixmap(), QPixmap)
        self.assertFalse(self.panel.diagram_label.pixmap().isNull())
        self.assertEqual(self.panel.diagram_label.text(), "")
        self.assertEqual(self.panel._last_render, ("1s1", "H", 50))

    def test_show_orbital_diagram_falls_back_when_configuration_missing(self):
        ghost = {"symbol": "??", "electron_configuration": None}
        self.panel.show_orbital_diagram(
            ghost, translate=_translate, cell_size=50, format_value=str,
        )
        self.assertTrue(self.panel.diagram_label.pixmap().isNull())
        self.assertEqual(self.panel.diagram_label.text(), "Diagram not available")
        self.assertIsNone(self.panel._last_render)

    def test_apply_theme_redraws_after_prior_render(self):
        hydrogen = {"symbol": "H", "electron_configuration": "1s1"}
        self.panel.show_orbital_diagram(
            hydrogen, translate=_translate, cell_size=50, format_value=str,
        )
        # Switch theme; redraw path should keep a non-null pixmap.
        self.panel.apply_theme("light")
        self.assertFalse(self.panel.diagram_label.pixmap().isNull())


if __name__ == "__main__":
    unittest.main()
