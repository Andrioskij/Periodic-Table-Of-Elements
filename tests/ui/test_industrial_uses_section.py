"""Unit tests for the _IndustrialUsesSection widget in info_panel.

Verifies that category/use pairs render as two labels each (category in [brackets],
followed by the use text), that missing-category falls back to [General], that the
empty-list fallback renders a single translated label, and that a custom translate
callback is honored.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication, QLabel

from src.ui.panels.info_panel import _IndustrialUsesSection


_app = QApplication.instance() or QApplication(sys.argv)


class TestIndustrialUsesSection(unittest.TestCase):
    def setUp(self):
        self.section = _IndustrialUsesSection()

    def test_empty_uses_shows_fallback_label(self):
        self.section.set_content(title="Uses", uses=[])
        self.assertEqual(self.section.uses_layout.count(), 1)
        label = self.section.uses_layout.itemAt(0).widget()
        self.assertIsInstance(label, QLabel)
        self.assertEqual(label.text(), "No industrial use data available")

    def test_valid_uses_render_two_labels_per_entry(self):
        data = [
            {"category": "Chemical synthesis", "use": "Ammonia production"},
            {"category": "Energy", "use": "Rocket fuel"},
        ]
        self.section.set_content(title="Uses", uses=data)
        # 2 entries x 2 labels (category + use) = 4
        self.assertEqual(self.section.uses_layout.count(), 4)
        category_text = self.section.uses_layout.itemAt(0).widget().text()
        use_text = self.section.uses_layout.itemAt(1).widget().text()
        self.assertEqual(category_text, "[Chemical synthesis]")
        self.assertEqual(use_text, "Ammonia production")
        self.assertEqual(self.section.uses_layout.itemAt(2).widget().text(), "[Energy]")
        self.assertEqual(self.section.uses_layout.itemAt(3).widget().text(), "Rocket fuel")

    def test_missing_category_falls_back_to_general(self):
        data = [{"use": "Generic use without a category"}]
        self.section.set_content(title="Uses", uses=data)
        self.assertEqual(self.section.uses_layout.count(), 2)
        self.assertEqual(self.section.uses_layout.itemAt(0).widget().text(), "[General]")
        self.assertEqual(
            self.section.uses_layout.itemAt(1).widget().text(),
            "Generic use without a category",
        )

    def test_translate_fallback_used_for_empty(self):
        tr = lambda key: {"no_industrial_data": "Nessun dato industriale"}.get(key, key)
        self.section.set_content(title="Usi industriali", uses=[], translate=tr)
        label = self.section.uses_layout.itemAt(0).widget()
        self.assertEqual(label.text(), "Nessun dato industriale")
        self.assertEqual(self.section.title_label.text(), "Usi industriali")

    def test_category_translated_when_key_present(self):
        tr = lambda key: {
            "industrial_category_chemical_synthesis": "Sintesi chimica",
        }.get(key, key)
        data = [{"category": "Chemical synthesis", "use": "Ammonia production"}]
        self.section.set_content(title="Usi industriali", uses=data, translate=tr)
        self.assertEqual(self.section.uses_layout.count(), 2)
        self.assertEqual(
            self.section.uses_layout.itemAt(0).widget().text(),
            "[Sintesi chimica]",
        )
        self.assertEqual(
            self.section.uses_layout.itemAt(1).widget().text(),
            "Ammonia production",
        )

    def test_category_falls_back_when_translate_returns_key(self):
        tr = lambda key: key
        data = [{"category": "Chemical synthesis", "use": "Ammonia production"}]
        self.section.set_content(title="Industrial uses", uses=data, translate=tr)
        self.assertEqual(
            self.section.uses_layout.itemAt(0).widget().text(),
            "[Chemical synthesis]",
        )

    def test_unknown_category_falls_back_to_raw_value(self):
        tr = lambda key: {
            "industrial_category_energy": "Energia",
        }.get(key, key)
        data = [{"category": "Foo bar", "use": "Unmapped category"}]
        self.section.set_content(title="Usi industriali", uses=data, translate=tr)
        self.assertEqual(
            self.section.uses_layout.itemAt(0).widget().text(),
            "[Foo bar]",
        )

    def test_section_has_accessible_name_and_description(self):
        self.assertEqual(self.section.accessibleName(), "Industrial Uses Section")
        self.assertIn("industrial", self.section.accessibleDescription().lower())


if __name__ == "__main__":
    unittest.main()
