"""Integration: theme toggle propagates to all QPainter panels."""

import os
import sys
import tempfile
import unittest

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from src.services.data_loader import load_elements, load_nomenclature_data
from src.services.settings_service import SettingsService
from src.ui.context import AppContext
from src.ui.main_window import MainWindow
from src.ui.theme import DARK_THEME, LIGHT_THEME

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication(sys.argv)


class TestThemePropagation(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False, encoding="utf-8"
        )
        tmp.close()
        self.ini_path = tmp.name
        qs = QSettings(self.ini_path, QSettings.IniFormat)
        settings = SettingsService(qsettings=qs)
        context = AppContext.create(
            elements=load_elements(),
            nomenclature_data=load_nomenclature_data(),
            settings_service=settings,
        )
        self.window = MainWindow(context)

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        try:
            os.unlink(self.ini_path)
        except OSError:
            pass

    def _expected_theme(self):
        return LIGHT_THEME if self.window.current_theme == "light" else DARK_THEME

    def test_toggle_switches_current_theme(self):
        initial = self.window.current_theme
        self.window.toggle_theme()
        self.assertNotEqual(self.window.current_theme, initial)

    def test_toggle_propagates_to_orbital_panel(self):
        self.window.toggle_theme()
        self.assertIs(self.window.orbital_diagram_panel._theme, self._expected_theme())

    def test_toggle_propagates_to_lewis_panel(self):
        self.window.toggle_theme()
        self.assertIs(self.window.lewis_panel._theme, self._expected_theme())

    def test_toggle_propagates_to_solubility_panel(self):
        self.window.toggle_theme()
        self.assertIs(self.window.solubility_panel._theme, self._expected_theme())

    def test_toggle_persists_via_settings_service(self):
        self.window.toggle_theme()
        self.assertEqual(
            self.window.settings_service.get_theme(),
            self.window.current_theme,
        )


if __name__ == "__main__":
    unittest.main()
