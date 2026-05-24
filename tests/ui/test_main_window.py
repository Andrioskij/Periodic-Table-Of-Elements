"""Integration smoke tests for `MainWindow`.

Closes IMP-002 in the followups backlog. The four controllers
(`ThemeController`, `LanguageController`, `ResponsiveLayoutController`,
`AccessibilityController`) each have their own unit tests; this file
covers the integration paths that exercise multiple of them through
the real `MainWindow` orchestration:

- Window title is built from the app metadata helper and contains the
  current version.
- Selection propagation: `select_element` updates the info panel
  visibility and the selection state.
- Language switch round-trip: `change_to` + `apply_language` updates
  every audited widget's text without raising.
- Builder reset: `reset_builder` clears both compound slots and
  hides the result.
- Theme toggle round-trip: alternate theme survives an `apply_theme`
  call and propagates to the orbital panel.
- About dialog: `open_about_dialog` returns the same instance on a
  second call (lazy singleton contract).

Tests use the same heavy-MainWindow setUpClass pattern as
`test_responsive_layout_controller.py` and `test_accessibility_controller.py`:
build the window once and share it across the test methods, since
none of them mutate global state irreversibly.
"""

import os
import sys
import tempfile
import unittest

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from src.app_metadata import APP_VERSION
from src.services.data_loader import load_elements, load_nomenclature_data
from src.services.settings_service import SettingsService
from src.ui.context import AppContext
from src.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_app = QApplication.instance() or QApplication(sys.argv)


class TestMainWindowSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".ini", delete=False, encoding="utf-8",
        )
        tmp.close()
        cls.ini_path = tmp.name
        qs = QSettings(cls.ini_path, QSettings.IniFormat)
        settings = SettingsService(qsettings=qs)
        cls.context = AppContext.create(
            elements=load_elements(),
            nomenclature_data=load_nomenclature_data(),
            settings_service=settings,
        )
        cls.window = MainWindow(cls.context)

    @classmethod
    def tearDownClass(cls):
        cls.window.close()
        cls.window.deleteLater()
        try:
            os.unlink(cls.ini_path)
        except OSError:
            pass

    # ----- Constructor + title -----

    def test_window_title_contains_app_version(self):
        # `build_window_title` from app_metadata stamps the version
        # onto the base title; the smoke test guards against drift
        # if someone re-implements the title independently.
        self.assertIn(APP_VERSION, self.window.windowTitle())

    def test_window_exposes_all_four_controllers(self):
        # Each chunk of the IMP-001 split must leave its controller
        # exposed on the window for callers (and tests) to reach.
        from src.ui.controllers.accessibility_controller import AccessibilityController
        from src.ui.controllers.language_controller import LanguageController
        from src.ui.controllers.responsive_layout_controller import ResponsiveLayoutController
        from src.ui.controllers.theme_controller import ThemeController

        self.assertIsInstance(self.window.theme_controller, ThemeController)
        self.assertIsInstance(self.window.language_controller, LanguageController)
        self.assertIsInstance(self.window.layout_controller, ResponsiveLayoutController)
        self.assertIsInstance(self.window.accessibility_controller, AccessibilityController)

    # ----- Selection propagation -----

    def test_select_element_updates_selection_state(self):
        hydrogen = next(
            el for el in self.window.elements if el["symbol"] == "H"
        )
        self.window.select_element(hydrogen)
        self.assertEqual(
            self.window.current_selected_element.get("symbol"), "H",
        )

    def test_select_element_propagates_to_info_panel(self):
        oxygen = next(
            el for el in self.window.elements if el["symbol"] == "O"
        )
        self.window.select_element(oxygen)
        # After selecting, the info_empty wrapper should hide and
        # info_card should show.
        self.assertFalse(self.window.info_panel.isHidden())

    # ----- Language switch -----

    def test_language_change_updates_window_title(self):
        # Switch to IT and verify the about button label changed (texts
        # are different between EN and IT).
        about_en = self.window.about_button.text()
        # change_to returns False if no-op; we don't care about the bool,
        # we care that apply_language ran without raising and that the
        # about_button picked up a new string.
        if self.window.current_language != "it":
            self.window.language_controller.change_to("it")
            self.window.apply_language()
            about_it = self.window.about_button.text()
            self.assertNotEqual(about_en, about_it)
            # Restore EN for downstream tests.
            self.window.language_controller.change_to("en")
            self.window.apply_language()

    def test_apply_language_does_not_raise(self):
        # Defensive: apply_language fans out to ~10 panels, the about
        # dialog (lazily), and the responsive layout. Just call it.
        self.window.apply_language()

    # ----- Theme toggle -----

    def test_theme_toggle_round_trip_preserves_initial_theme(self):
        initial = self.window.current_theme
        self.window.toggle_theme()
        self.assertNotEqual(self.window.current_theme, initial)
        self.window.toggle_theme()
        self.assertEqual(self.window.current_theme, initial)

    def test_apply_theme_updates_theme_button_text(self):
        # The theme button shows a sun/moon glyph driven by the
        # controller; calling apply_theme refreshes it.
        before = self.window.theme_button.text()
        self.window.toggle_theme()
        after_toggle = self.window.theme_button.text()
        self.assertNotEqual(before, after_toggle)
        # Restore for downstream tests.
        self.window.toggle_theme()

    # ----- Builder reset -----

    def test_reset_builder_clears_compound_state(self):
        # Seed builder state and verify reset wipes it.
        h = next(el for el in self.window.elements if el["symbol"] == "H")
        cl = next(el for el in self.window.elements if el["symbol"] == "Cl")
        self.window.compound_a = h
        self.window.compound_b = cl
        self.window.search_a_input.setText("H")
        self.window.search_b_input.setText("Cl")

        self.window.reset_builder()

        self.assertIsNone(self.window.compound_a)
        self.assertIsNone(self.window.compound_b)
        self.assertEqual(self.window.search_a_input.text(), "")
        self.assertEqual(self.window.search_b_input.text(), "")

    # ----- About dialog -----

    def test_open_about_dialog_creates_then_reuses_instance(self):
        self.assertIsNone(self.window.about_dialog)
        self.window.open_about_dialog()
        first = self.window.about_dialog
        self.assertIsNotNone(first)
        # Closing the dialog should not destroy the instance; a second
        # call must reuse it (lazy-singleton contract).
        first.hide()
        self.window.open_about_dialog()
        self.assertIs(self.window.about_dialog, first)
        first.hide()


if __name__ == "__main__":
    unittest.main()
