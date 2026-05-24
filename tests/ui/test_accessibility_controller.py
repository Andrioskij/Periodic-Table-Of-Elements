"""Unit tests for AccessibilityController.

Two scopes (mirrors test_responsive_layout_controller.py's split):

- ``TestApplySpec`` exercises the static ``_apply_spec`` helper
  against a fake widget — pure Python, no Qt round-trip.

- ``TestAccessibilityIntegration`` boots a real MainWindow under
  offscreen Qt and asserts the controller did its job at startup:
  focus policies set, keyboard shortcuts bound, and
  ``refresh_control_accessibility`` populated accessibleName /
  accessibleDescription / toolTip.
"""

import os
import sys
import tempfile
import unittest

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication

from src.services.data_loader import load_elements, load_nomenclature_data
from src.services.settings_service import SettingsService
from src.ui.context import AppContext
from src.ui.controllers.accessibility_controller import AccessibilityController
from src.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication(sys.argv)


class _FakeWidget:
    """Captures accessibility setters so ``_apply_spec`` can be tested
    without spinning up a QWidget."""

    def __init__(self):
        self.name = None
        self.description = None
        self.tooltip = None

    def setAccessibleName(self, value):
        self.name = value

    def setAccessibleDescription(self, value):
        self.description = value

    def setToolTip(self, value):
        self.tooltip = value


class TestApplySpec(unittest.TestCase):
    def test_apply_spec_sets_all_three_fields(self):
        widget = _FakeWidget()
        AccessibilityController._apply_spec(
            widget,
            {"name": "Search", "description": "Type to filter", "tooltip": "Ctrl+F"},
        )
        self.assertEqual(widget.name, "Search")
        self.assertEqual(widget.description, "Type to filter")
        self.assertEqual(widget.tooltip, "Ctrl+F")


class TestAccessibilityIntegration(unittest.TestCase):
    """Real-MainWindow round-trip: asserts the controller wired the
    things it's supposed to wire at startup."""

    @classmethod
    def setUpClass(cls):
        # Same setup pattern as test_responsive_layout_controller.py:
        # build the heavy MainWindow once and reuse it across tests.
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

    def test_main_window_owns_accessibility_controller(self):
        self.assertIsInstance(
            self.window.accessibility_controller, AccessibilityController,
        )
        self.assertIs(self.window.accessibility_controller.window, self.window)

    def test_strong_focus_policy_on_audited_controls(self):
        # Every keyboard-actionable widget must get StrongFocus so
        # screen readers and Tab navigation reach it.
        for widget in (
            self.window.about_button,
            self.window.language_selector,
            self.window.search_input,
            self.window.compound_builder_panel,
            self.window.periodic_table_widget,
            self.window.right_column_widget,
            self.window.info_panel,
            self.window.orbital_diagram_panel,
            self.window.lewis_panel,
            self.window.molar_mass_panel,
            self.window.stoichiometry_panel,
        ):
            self.assertEqual(
                widget.focusPolicy(), Qt.StrongFocus,
                msg=f"{type(widget).__name__} did not get StrongFocus",
            )
        for button in self.window.trend_buttons.values():
            self.assertEqual(button.focusPolicy(), Qt.StrongFocus)
        for button in self.window.right_panel_buttons.values():
            self.assertEqual(button.focusPolicy(), Qt.StrongFocus)

    def test_keyboard_shortcuts_registered(self):
        # The controller binds Ctrl+F, Ctrl+R, Ctrl+1/2/3, Ctrl+L.
        bound = {sc.key().toString() for sc in self.window.findChildren(QShortcut)}
        for expected in ("Ctrl+F", "Ctrl+R", "Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+L"):
            self.assertIn(
                QKeySequence(expected).toString(), bound,
                msg=f"shortcut {expected} not registered",
            )

    def test_refresh_populates_accessible_name_on_about_button(self):
        # Startup refresh should have set an accessibleName on the
        # about button; exact wording is language-dependent but
        # must be non-empty.
        self.assertTrue(self.window.about_button.accessibleName())

    def test_refresh_repopulates_after_explicit_call(self):
        # Wipe the name then call the controller refresher; it must
        # be repopulated from current button texts.
        self.window.about_button.setAccessibleName("")
        self.window.accessibility_controller.refresh_control_accessibility()
        self.assertTrue(self.window.about_button.accessibleName())

    def test_focus_search_input_calls_set_focus_with_tab_reason(self):
        # Under offscreen Qt the application-wide focus widget tracking
        # is unreliable (no input dispatch), so we patch `setFocus` on
        # the search input and capture the reason instead of asserting
        # against `QApplication.focusWidget()`. Verifies the controller
        # invokes the right method with the documented reason —
        # Qt's actual focus delivery is its own concern.
        calls = []
        original = self.window.search_input.setFocus

        def capture(reason=Qt.OtherFocusReason):
            calls.append(reason)
            return original(reason)

        self.window.search_input.setFocus = capture
        try:
            self.window.accessibility_controller.focus_search_input()
        finally:
            self.window.search_input.setFocus = original
        self.assertEqual(calls, [Qt.TabFocusReason])


if __name__ == "__main__":
    unittest.main()
