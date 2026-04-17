"""Unit tests for OrbitalDiagramPanel accessibility hooks.

Exercises `show_orbital_diagram()` to verify that `diagram_label.accessibleName`
is updated with the localized configuration string (or the "not available"
fallback) after rendering.
"""

import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
