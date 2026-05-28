"""Unit tests for CompoundController.

Pure-Python: real ``CompoundBuilderManager`` + ``SelectionState`` +
``NomenclatureController`` (which is also Qt-free), and fake widgets
that record their inputs/outputs in plain attributes. Exercises the
orchestration the controller owns: status text composition, selector
labels, search-slot handlers, reset, and the result-text dispatch
into ``compose_compound_result_text``.
"""

import json
import unittest
from pathlib import Path

from src.ui.controllers.compound_controller import CompoundController
from src.ui.controllers.nomenclature_controller import NomenclatureController
from src.ui.managers.compound_builder_manager import CompoundBuilderManager
from src.ui.state import SelectionState

# ----- Fakes -----

class _FakeLanguageController:
    def __init__(self, code="en"):
        self.current_language = code


class _FakeLineEdit:
    """Mimics QLineEdit.text/setText/setToolTip/setAccessibleDescription."""

    def __init__(self, text=""):
        self._text = text
        self.tooltip = ""
        self.accessible_description = ""

    def text(self):
        return self._text

    def setText(self, value):
        self._text = value

    def setToolTip(self, value):
        self.tooltip = value

    def setAccessibleDescription(self, value):
        self.accessible_description = value


class _FakeCombo:
    """Mimics the slice of QComboBox the controller touches."""

    def __init__(self):
        self.items = []
        self._current_index = -1
        self.enabled = True
        self._signals_blocked = False

    def blockSignals(self, value):
        self._signals_blocked = value

    def clear(self):
        self.items = []
        self._current_index = -1

    def addItem(self, label, data):
        self.items.append((label, data))
        if self._current_index == -1:
            self._current_index = 0

    def setEnabled(self, value):
        self.enabled = value

    def currentData(self):
        if 0 <= self._current_index < len(self.items):
            return self.items[self._current_index][1]
        return None

    def set_current_index(self, idx):
        self._current_index = idx


class _FakeLabel:
    def __init__(self, text=""):
        self._text = text
        self.tooltip = ""

    def text(self):
        return self._text

    def setText(self, value):
        self._text = value

    def setToolTip(self, value):
        self.tooltip = value


class _FakePanel:
    """Mimics ``CompoundBuilderPanel`` slice used by the controller."""

    def __init__(self):
        self.status_text = ""
        self.result_text = ""
        self.selector_a_text = ""
        self.selector_b_text = ""
        self.selector_a_summary_label = _FakeLabel()
        self.selector_b_summary_label = _FakeLabel()

    def set_status_text(self, value):
        self.status_text = value

    def set_result_text(self, value):
        self.result_text = value

    def set_selector_texts(self, first, second):
        self.selector_a_text = first
        self.selector_b_text = second
        self.selector_a_summary_label.setText(first)
        self.selector_b_summary_label.setText(second)


# ----- Helpers -----

def _load_nomenclature_data():
    path = Path(__file__).resolve().parents[2] / "data" / "reference" / "nomenclature_data.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_elements_data():
    path = Path(__file__).resolve().parents[2] / "data" / "raw" / "elements.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _translate_passthrough(key, **kwargs):
    """Translate keys into deterministic, inspectable strings (no I/O)."""
    if not kwargs:
        return f"[{key}]"
    parts = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    return f"[{key}|{parts}]"


def _format_oxidation_state(value):
    return "[traditional_na]" if value is None else f"{value:+d}"


def _populate_oxidation_combo(combo, element):
    combo.blockSignals(True)
    combo.clear()
    if element is None:
        combo.addItem("[traditional_na]", None)
        combo.setEnabled(False)
        combo.blockSignals(False)
        return
    raw = element.get("oxidation_states") or ""
    states = sorted(
        int(token.strip()) for token in raw.split(",") if token.strip()
    )
    if not states:
        combo.addItem("[traditional_na]", None)
    else:
        for state in states:
            combo.addItem(_format_oxidation_state(state), state)
    combo.setEnabled(bool(states))
    combo.blockSignals(False)


# ----- Tests -----

class _ControllerFixture:
    """Build a fully-wired CompoundController for the tests.

    Exposed as a mixin via ``self.make_controller()`` so each test
    method can drop in with a clean slate.
    """

    @classmethod
    def setUpClass(cls):
        cls.nomenclature_data = _load_nomenclature_data()
        cls.elements = _load_elements_data()
        cls.element_by_symbol = {e["symbol"]: e for e in cls.elements}

    def make_controller(self, language="en", ranked_matches=None):
        selection = SelectionState()
        manager = CompoundBuilderManager(elements=self.elements)
        lang = _FakeLanguageController(language)
        nomenclature = NomenclatureController(
            nomenclature_data=self.nomenclature_data,
            language_controller=lang,
        )
        panel = _FakePanel()
        search_a = _FakeLineEdit()
        search_b = _FakeLineEdit()
        combo_a = _FakeCombo()
        combo_b = _FakeCombo()

        # ranked_matches: dict[query -> list[element]] or callable
        if ranked_matches is None:
            ranked_matches = {}
        if isinstance(ranked_matches, dict):
            def get_ranked_matches(query, limit=6, _table=ranked_matches):
                return _table.get(query, [])[:limit]
        else:
            get_ranked_matches = ranked_matches

        controller = CompoundController(
            builder_manager=manager,
            selection_state=selection,
            nomenclature_controller=nomenclature,
            compound_builder_panel=panel,
            search_a_input=search_a,
            search_b_input=search_b,
            a_oxidation_combo=combo_a,
            b_oxidation_combo=combo_b,
            translate=_translate_passthrough,
            format_oxidation_state=_format_oxidation_state,
            populate_oxidation_combo=_populate_oxidation_combo,
            get_ranked_matches=get_ranked_matches,
        )
        return controller, {
            "selection": selection,
            "manager": manager,
            "panel": panel,
            "search_a": search_a,
            "search_b": search_b,
            "combo_a": combo_a,
            "combo_b": combo_b,
            "lang": lang,
        }


class TestCompoundControllerStateSync(_ControllerFixture, unittest.TestCase):
    def test_sync_state_pushes_oxidations_into_manager(self):
        controller, refs = self.make_controller()
        sodium = self.element_by_symbol["Na"]
        chlorine = self.element_by_symbol["Cl"]
        controller.compound_a = sodium
        controller.compound_b = chlorine
        # Combos must already be populated to expose a currentData.
        _populate_oxidation_combo(refs["combo_a"], sodium)
        _populate_oxidation_combo(refs["combo_b"], chlorine)

        controller.sync_state_from_controls()

        # Defaults: combo selects the first state.
        state = refs["manager"].state
        self.assertEqual(state.element_a_id, sodium["atomic_number"])
        self.assertEqual(state.element_b_id, chlorine["atomic_number"])
        self.assertIsNotNone(state.element_a_oxidation)
        self.assertIsNotNone(state.element_b_oxidation)

    def test_sync_state_noop_when_no_elements_selected(self):
        controller, refs = self.make_controller()
        controller.sync_state_from_controls()
        # Manager untouched.
        self.assertIsNone(refs["manager"].state.element_a_id)
        self.assertIsNone(refs["manager"].state.element_b_id)


class TestCompoundControllerPanelRefresh(_ControllerFixture, unittest.TestCase):
    def test_refresh_builder_status_uses_placeholder_when_empty(self):
        controller, refs = self.make_controller()
        controller.refresh_builder_status()
        # Status text formatted via translate("builder_status", a=..., b=...).
        self.assertIn("[not_selected]", refs["panel"].status_text)
        self.assertIn("[builder_status", refs["panel"].status_text)

    def test_refresh_builder_status_shows_symbol_plus_oxidation(self):
        controller, refs = self.make_controller()
        sodium = self.element_by_symbol["Na"]
        controller.compound_a = sodium
        refs["manager"].set_element_a(sodium["atomic_number"], 1)

        controller.refresh_builder_status()

        self.assertIn("Na +1", refs["panel"].status_text)

    def test_refresh_builder_selector_texts_uses_localized_name(self):
        controller, refs = self.make_controller(language="it")
        sodium = self.element_by_symbol["Na"]
        controller.compound_a = sodium

        controller.refresh_builder_selector_texts()

        # Italian localization for Sodium is "sodio".
        self.assertIn("sodio", refs["panel"].selector_a_text)
        self.assertIn("Na", refs["panel"].selector_a_text)
        # Slot B still placeholder.
        self.assertEqual(refs["panel"].selector_b_text, "[second_element]")

    def test_refresh_builder_action_accessibility_mirrors_selector_text(self):
        controller, refs = self.make_controller()
        controller.refresh_builder_selector_texts()
        controller.refresh_builder_action_accessibility()
        self.assertEqual(
            refs["search_a"].tooltip,
            refs["panel"].selector_a_summary_label.text(),
        )
        self.assertEqual(
            refs["search_a"].accessible_description,
            refs["panel"].selector_a_summary_label.text(),
        )

    def test_refresh_compound_panel_no_text_when_no_pair(self):
        controller, refs = self.make_controller()
        controller.refresh_compound_panel()
        self.assertEqual(refs["panel"].result_text, "")

    def test_refresh_compound_panel_shows_pair_ready_prompt(self):
        controller, refs = self.make_controller()
        controller.compound_a = self.element_by_symbol["Na"]
        controller.compound_b = self.element_by_symbol["Cl"]

        controller.refresh_compound_panel(rebuild=False)

        # Has the prompt; common-compounds preview may or may not be appended
        # depending on dataset content.
        self.assertIn("[pair_ready_prompt]", refs["panel"].result_text)

    def test_refresh_compound_panel_rebuild_emits_result_text(self):
        controller, refs = self.make_controller()
        sodium = self.element_by_symbol["Na"]
        chlorine = self.element_by_symbol["Cl"]
        controller.compound_a = sodium
        controller.compound_b = chlorine
        _populate_oxidation_combo(refs["combo_a"], sodium)
        _populate_oxidation_combo(refs["combo_b"], chlorine)

        controller.refresh_compound_panel(rebuild=True)

        # Result text is non-empty when a valid pair is selected.
        self.assertNotEqual(refs["panel"].result_text, "")


class TestCompoundControllerSlotHandlers(_ControllerFixture, unittest.TestCase):
    def test_on_search_element_a_assigns_match_and_refreshes(self):
        sodium = self.element_by_symbol["Na"]
        controller, refs = self.make_controller(
            ranked_matches={"sodium": [sodium]},
        )
        refs["search_a"].setText("sodium")

        controller.on_search_element_a()

        # Slot A is assigned.
        self.assertIs(controller.compound_a, sodium)
        # Search input is rewritten to show "<name> (<symbol>)".
        self.assertIn("Na", refs["search_a"].text())
        # Oxidation combo populated (at least one entry).
        self.assertTrue(refs["combo_a"].items)
        # Manager received the element + provisional charge 1.
        self.assertEqual(
            refs["manager"].state.element_a_id, sodium["atomic_number"],
        )

    def test_on_search_element_a_clears_input_when_no_match(self):
        controller, refs = self.make_controller(ranked_matches={})
        refs["search_a"].setText("zzz")

        controller.on_search_element_a()

        self.assertEqual(refs["search_a"].text(), "")
        self.assertIsNone(controller.compound_a)

    def test_on_search_element_a_noop_when_query_empty(self):
        controller, refs = self.make_controller()
        controller.on_search_element_a()
        self.assertIsNone(controller.compound_a)

    def test_on_search_element_b_assigns_with_negative_default_charge(self):
        chlorine = self.element_by_symbol["Cl"]
        controller, refs = self.make_controller(
            ranked_matches={"chlorine": [chlorine]},
        )
        refs["search_b"].setText("chlorine")

        controller.on_search_element_b()

        self.assertIs(controller.compound_b, chlorine)
        self.assertEqual(
            refs["manager"].state.element_b_id, chlorine["atomic_number"],
        )
        self.assertEqual(refs["manager"].state.element_b_oxidation, -1)


class TestCompoundControllerReset(_ControllerFixture, unittest.TestCase):
    def test_reset_clears_slots_inputs_combos_and_manager(self):
        sodium = self.element_by_symbol["Na"]
        chlorine = self.element_by_symbol["Cl"]
        controller, refs = self.make_controller(
            ranked_matches={"sodium": [sodium], "chlorine": [chlorine]},
        )
        refs["search_a"].setText("sodium")
        controller.on_search_element_a()
        refs["search_b"].setText("chlorine")
        controller.on_search_element_b()

        controller.reset()

        self.assertIsNone(controller.compound_a)
        self.assertIsNone(controller.compound_b)
        self.assertEqual(refs["search_a"].text(), "")
        self.assertEqual(refs["search_b"].text(), "")
        # Combos rebuilt with the single N/A placeholder.
        self.assertEqual(len(refs["combo_a"].items), 1)
        self.assertEqual(len(refs["combo_b"].items), 1)
        self.assertIsNone(refs["combo_a"].items[0][1])
        # Manager state cleared.
        self.assertIsNone(refs["manager"].state.element_a_id)
        self.assertIsNone(refs["manager"].state.element_b_id)


class TestCompoundControllerCommonCompounds(_ControllerFixture, unittest.TestCase):
    def test_format_common_compounds_section_empty_without_pair(self):
        controller, _ = self.make_controller()
        # No pair selected → preview helper returns falsy.
        self.assertFalse(controller.format_common_compounds_section())

    def test_get_common_compounds_for_current_pair_empty_without_pair(self):
        controller, _ = self.make_controller()
        self.assertEqual(
            controller.get_common_compounds_for_current_pair(), [],
        )


if __name__ == "__main__":
    unittest.main()
