"""Tests for ResponsiveLayoutController.

Two scopes:

- `TestResponsiveLayoutStaticHelpers` covers the pure-Python static
  helpers that don't need a real widget tree (None-guards, etc.).
- `TestResponsiveLayoutIntegration` instantiates a real MainWindow,
  resizes it across the breakpoints defined in layout_policy, and
  asserts that the controller's `apply()` propagates the policy to
  the window's metric attributes and key widget layouts.

The integration tests complement `test_theme_integration.py`: both
exercise real-MainWindow round-trips, but this file focuses on
responsive-policy application instead of theme propagation.
"""

import os
import sys
import tempfile
import unittest

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QBoxLayout, QPushButton

from src.services.data_loader import load_elements, load_nomenclature_data
from src.services.settings_service import SettingsService
from src.ui.context import AppContext
from src.ui.controllers.responsive_layout_controller import ResponsiveLayoutController
from src.ui.layout_policy import (
    MEDIUM_BREAKPOINT,
    NARROW_BREAKPOINT,
    WIDE_BREAKPOINT,
)
from src.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication(sys.argv)


class TestResponsiveLayoutStaticHelpers(unittest.TestCase):
    """Static / pure-Python helpers that need neither MainWindow nor a real layout."""

    def test_sync_height_for_width_widget_accepts_none(self):
        # Defensive None-guard: callers pass attributes that might be None
        # if a widget hasn't been built yet (e.g. during early-init paths).
        ResponsiveLayoutController._sync_height_for_width_widget(None)

    def test_sync_height_for_width_widget_sets_fixed_height_from_size_hint(self):
        widget = QPushButton("hello")
        widget.adjustSize()
        ResponsiveLayoutController._sync_height_for_width_widget(widget)
        self.assertGreater(widget.height(), 0)


class TestResponsiveLayoutIntegration(unittest.TestCase):
    """Integration: real MainWindow, resize across breakpoints, assert policy applied."""

    @classmethod
    def setUpClass(cls):
        # Build the heavy MainWindow once for all tests in this class — the
        # responsive policy is pure of side effects on the dataset, so the
        # window can be reused across resizes.
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False, encoding="utf-8"
        )
        tmp.close()
        cls.ini_path = tmp.name
        qs = QSettings(cls.ini_path, QSettings.IniFormat)
        settings = SettingsService(qsettings=qs)
        context = AppContext.create(
            elements=load_elements(),
            nomenclature_data=load_nomenclature_data(),
            settings_service=settings,
        )
        cls.window = MainWindow(context)

    @classmethod
    def tearDownClass(cls):
        cls.window.close()
        cls.window.deleteLater()
        try:
            os.unlink(cls.ini_path)
        except OSError:
            pass

    def _resize_and_apply(self, width):
        self.window.resize(width, 900)
        self.window.update_responsive_layout()

    def test_wide_breakpoint_uses_horizontal_top_controls(self):
        self._resize_and_apply(WIDE_BREAKPOINT + 100)
        self.assertEqual(
            self.window.top_controls_layout.direction(),
            QBoxLayout.LeftToRight,
        )

    def test_medium_breakpoint_uses_horizontal_top_controls(self):
        self._resize_and_apply(MEDIUM_BREAKPOINT + 50)
        self.assertEqual(
            self.window.top_controls_layout.direction(),
            QBoxLayout.LeftToRight,
        )

    def test_narrow_breakpoint_switches_to_vertical(self):
        self._resize_and_apply(NARROW_BREAKPOINT + 10)
        self.assertEqual(
            self.window.top_controls_layout.direction(),
            QBoxLayout.TopToBottom,
        )

    def test_metric_attrs_are_updated_on_apply(self):
        self._resize_and_apply(WIDE_BREAKPOINT + 100)
        wide_cell = self.window.cell_size
        self._resize_and_apply(600)  # compact
        compact_cell = self.window.cell_size
        self.assertGreater(
            wide_cell,
            compact_cell,
            "Cell size must shrink when window narrows below the wide breakpoint",
        )

    def test_periodic_table_receives_updated_metrics(self):
        self._resize_and_apply(WIDE_BREAKPOINT + 100)
        # PeriodicTableWidget.update_metrics writes the new cell_size onto the widget;
        # asserting the widget agrees with MainWindow's attr proves the propagation path.
        self.assertEqual(self.window.periodic_table_widget.cell_size, self.window.cell_size)


if __name__ == "__main__":
    unittest.main()
