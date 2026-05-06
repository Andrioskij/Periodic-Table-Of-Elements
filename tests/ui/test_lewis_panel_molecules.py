"""Smoke tests for the LewisPanel molecule-input flow."""

import sys

import pytest
from PySide6.QtWidgets import QApplication

from src.ui.panels.lewis_panel import LewisPanel

_TRANSLATIONS = {
    "lewis_title": "Lewis diagram",
    "lewis_prompt": "Select an element.",
    "lewis_not_applicable": "Not applicable.",
    "lewis_valence_electrons": "Valence electrons: {count}",
    "lewis_not_in_library": "Lewis structure not in library.",
}


def _translate(key, **kwargs):
    template = _TRANSLATIONS.get(key, key)
    return template.format(**kwargs) if kwargs else template


def _format_value(value, **_kwargs):
    return "" if value is None else str(value)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def panel(qapp):
    elements = [
        {"symbol": "Na", "group": 1, "category": "alkali metal"},
        {"symbol": "O", "group": 16, "category": "nonmetal"},
        {"symbol": "Fe", "group": 8, "category": "transition metal"},
    ]
    p = LewisPanel("Lewis diagram", "Select an element.", elements=elements)
    p.set_translator(_translate, _format_value)
    p.apply_language(
        title=_translate("lewis_title"),
        prompt=_translate("lewis_prompt"),
        input_placeholder="formula...",
        show_button_text="Show",
        not_in_library_text=_translate("lewis_not_in_library"),
    )
    return p


def test_panel_renders_h2o_via_input(panel):
    panel.formula_input.setText("H2O")
    panel.show_molecule_button.click()

    pixmap = panel.diagram_label.pixmap()
    assert pixmap is not None
    assert not pixmap.isNull()
    assert panel._last_render == ("molecule", "H2O")


def test_panel_renders_h2o_case_insensitive(panel):
    panel.formula_input.setText("h2o")
    panel.show_molecule_button.click()

    assert panel._last_render == ("molecule", "H2O")


def test_panel_falls_back_to_element_for_single_symbol(panel):
    panel.formula_input.setText("Na")
    panel.show_molecule_button.click()

    pixmap = panel.diagram_label.pixmap()
    assert pixmap is not None
    assert not pixmap.isNull()
    # Single-element rendering stores ("element", symbol, valence).
    assert panel._last_render is not None
    assert panel._last_render[0] == "element"
    assert panel._last_render[1] == "Na"


def test_panel_shows_not_in_library_message(panel):
    panel.formula_input.setText("XYZ123")
    panel.show_molecule_button.click()

    assert panel._last_render is None
    assert panel.diagram_label.text() == _translate("lewis_not_in_library")
    assert panel.diagram_label.pixmap().isNull()


def test_panel_handles_empty_input(panel):
    # Render H2O first so we can verify empty-input is a no-op.
    panel.formula_input.setText("H2O")
    panel.show_molecule_button.click()
    panel.formula_input.setText("   ")
    panel.show_molecule_button.click()

    assert panel._last_render == ("molecule", "H2O")


def test_apply_theme_redraws_molecule(panel):
    panel.formula_input.setText("CO2")
    panel.show_molecule_button.click()
    pixmap_dark = panel.diagram_label.pixmap()
    assert not pixmap_dark.isNull()

    panel.apply_theme("light")
    pixmap_light = panel.diagram_label.pixmap()
    assert not pixmap_light.isNull()
    assert panel._last_render == ("molecule", "CO2")
