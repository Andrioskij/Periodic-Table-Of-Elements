"""Unit tests for SelectionStateController.

Pure-Python tests using the real ``SelectionState`` dataclass and
fake periodic-table + solubility-panel objects that record their
interactions in plain attributes. Asserts: header sync mirrors the
table widget's button, panel-refresh fan-out fires with the right
modes, and solubility highlighting is set/cleared based on the
selected element's symbol.
"""

import unittest

from src.ui.controllers.selection_state_controller import (
    SelectionStateController,
)
from src.ui.state import SelectionState


class _FakePeriodicTableWidget:
    def __init__(self):
        self.selected_button = None
        self.selected_element = None
        self.refresh_calls = 0

    def select_element(self, element):
        self.selected_element = element
        # Simulate the widget bumping its own selected_button on select.
        self.selected_button = f"button-for-{element['symbol']}" if element else None

    def refresh_selected_element_name(self):
        self.refresh_calls += 1


class _FakeSolubilityPanel:
    def __init__(self):
        self.highlighted = None
        self.cleared = 0

    def highlight_element(self, symbol):
        self.highlighted = symbol

    def clear_highlight(self):
        self.highlighted = None
        self.cleared += 1


class _RefreshPanelModesSpy:
    def __init__(self):
        self.calls = []

    def __call__(self, modes):
        self.calls.append(tuple(modes))


def _make_controller():
    state = SelectionState()
    table = _FakePeriodicTableWidget()
    panel = _FakeSolubilityPanel()
    refresh = _RefreshPanelModesSpy()
    controller = SelectionStateController(
        selection_state=state,
        periodic_table_widget=table,
        solubility_panel=panel,
        refresh_panel_modes=refresh,
    )
    return controller, state, table, panel, refresh


class TestSelectionStateController(unittest.TestCase):
    def test_apply_selected_element_stores_element_and_refreshes_panels(self):
        controller, state, table, panel, refresh = _make_controller()
        element = {"symbol": "Na", "atomic_number": 11}
        table.selected_button = "button-Na"

        controller.apply_selected_element(element)

        self.assertEqual(state.element, element)
        # Header sync read the table's current selected_button.
        self.assertEqual(state.selected_button, "button-Na")
        self.assertEqual(table.refresh_calls, 1)
        # Right-panel fan-out fired exactly once with the canonical modes.
        self.assertEqual(refresh.calls, [("info", "diagram", "lewis")])
        # Solubility highlighted to the new element's symbol.
        self.assertEqual(panel.highlighted, "Na")

    def test_apply_selected_element_none_clears_solubility(self):
        controller, state, _, panel, _ = _make_controller()
        # Seed an existing highlight to assert it gets cleared.
        panel.highlight_element("Cl")

        controller.apply_selected_element(None)

        self.assertIsNone(state.element)
        self.assertIsNone(panel.highlighted)
        self.assertEqual(panel.cleared, 1)

    def test_apply_selected_element_empty_symbol_clears_solubility(self):
        controller, _, _, panel, _ = _make_controller()
        # Symbol absent → treated like "no element" for solubility purposes.
        controller.apply_selected_element({"atomic_number": 0})
        self.assertIsNone(panel.highlighted)
        self.assertEqual(panel.cleared, 1)

    def test_select_element_drives_table_widget_then_applies(self):
        controller, state, table, panel, refresh = _make_controller()
        element = {"symbol": "Cl", "atomic_number": 17}

        controller.select_element(element)

        # Table widget was driven to select the element first.
        self.assertEqual(table.selected_element, element)
        # ...and apply ran afterwards (state populated, refresh fired).
        self.assertEqual(state.element, element)
        self.assertEqual(panel.highlighted, "Cl")
        self.assertEqual(len(refresh.calls), 1)

    def test_activate_element_is_alias_for_select_element(self):
        controller, state, table, _, _ = _make_controller()
        element = {"symbol": "O", "atomic_number": 8}

        controller.activate_element(element)

        self.assertEqual(table.selected_element, element)
        self.assertEqual(state.element, element)

    def test_refresh_selection_header_syncs_button_and_calls_widget(self):
        controller, state, table, _, _ = _make_controller()
        table.selected_button = "button-Fe"

        controller.refresh_selection_header()

        self.assertEqual(state.selected_button, "button-Fe")
        self.assertEqual(table.refresh_calls, 1)

    def test_current_element_proxies_to_selection_state(self):
        controller, state, _, _, _ = _make_controller()
        self.assertIsNone(controller.current_element)
        element = {"symbol": "He", "atomic_number": 2}
        state.element = element
        self.assertIs(controller.current_element, element)


if __name__ == "__main__":
    unittest.main()
