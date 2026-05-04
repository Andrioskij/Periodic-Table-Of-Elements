"""Compound Builder tab content.

Single-pair binary ionic formula builder. Uses
``src.domain.compound_builder`` for the actual formula derivation
(criss-cross GCD); this module wires Reflex inputs to it and adds
validation for same-element / same-sign / no-charge selections.

Element pickers are filtered to those with at least one positive
oxidation state (cation list) and at least one negative oxidation
state (anion list). That keeps the dropdowns short and avoids
charge combinations that the desktop app's manager would also
reject.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.i18n import TranslationState
from periodic_table_web.theme import DARK_FOREGROUND
from src.domain.compound_builder import build_binary_formula, parse_oxidation_states
from src.services.data_loader import load_elements

_ELEMENTS = load_elements()
_LABEL_MUTED = "#9a9aa8"
_RESULT_BG = "#1f1f2e"
_ERROR_COLOR = "#f7a8a8"

# Pre-compute the dropdown lists at import time. Each entry is
# (symbol, "Symbol — Name") so the labels read naturally; we send the
# symbol as the form value and look up oxidation states by symbol.
_ELEMENT_OXIDATIONS: dict[str, list[int]] = {
    el["symbol"]: parse_oxidation_states(el.get("oxidation_states"))
    for el in _ELEMENTS
}


def _filter_options(positive: bool) -> list[str]:
    options: list[str] = []
    for el in _ELEMENTS:
        states = _ELEMENT_OXIDATIONS.get(el["symbol"], [])
        if any((s > 0) == positive for s in states):
            options.append(f"{el['symbol']} — {el['name']}")
    return options


_CATION_OPTIONS: list[str] = _filter_options(positive=True)
_ANION_OPTIONS: list[str] = _filter_options(positive=False)


def _option_to_symbol(option: str) -> str:
    return option.split(" — ")[0] if option else ""


def _charge_options(symbol: str, positive: bool) -> list[str]:
    states = _ELEMENT_OXIDATIONS.get(symbol, [])
    filtered = [s for s in states if (s > 0) == positive]
    return [(f"+{s}" if s > 0 else str(s)) for s in filtered]


def _coerce_charge(label: str) -> int:
    if not label:
        return 0
    return int(label.replace("+", ""))


class CompoundBuilderState(rx.State):
    """Picker selections (element + charge per side) for the binary builder."""

    cation_option: str = ""
    cation_charge_label: str = ""
    anion_option: str = ""
    anion_charge_label: str = ""

    @rx.event
    def set_cation_option(self, value: str) -> None:
        self.cation_option = value
        # Reset the charge selector when the element changes — the
        # previous charge may not exist on the new element.
        self.cation_charge_label = ""

    @rx.event
    def set_cation_charge(self, value: str) -> None:
        self.cation_charge_label = value

    @rx.event
    def set_anion_option(self, value: str) -> None:
        self.anion_option = value
        self.anion_charge_label = ""

    @rx.event
    def set_anion_charge(self, value: str) -> None:
        self.anion_charge_label = value

    @rx.var(cache=True)
    def cation_symbol(self) -> str:
        return _option_to_symbol(self.cation_option)

    @rx.var(cache=True)
    def anion_symbol(self) -> str:
        return _option_to_symbol(self.anion_option)

    @rx.var(cache=True)
    def cation_charge_choices(self) -> list[str]:
        return _charge_options(self.cation_symbol, positive=True)

    @rx.var(cache=True)
    def anion_charge_choices(self) -> list[str]:
        return _charge_options(self.anion_symbol, positive=False)

    @rx.var(cache=True)
    def has_full_selection(self) -> bool:
        return bool(
            self.cation_option
            and self.anion_option
            and self.cation_charge_label
            and self.anion_charge_label
        )

    @rx.var(cache=True)
    def error_key(self) -> str:
        """Return the translation key for the current error, or ``""``.

        Storing a key (not a localized string) lets the view look the
        message up against ``TranslationState.t`` so the language switch
        propagates instantly.
        """
        if not (self.cation_option and self.anion_option):
            return ""
        if self.cation_symbol == self.anion_symbol:
            return "builder_error_same_element"
        if not (self.cation_charge_label and self.anion_charge_label):
            return ""
        cation_charge = _coerce_charge(self.cation_charge_label)
        anion_charge = _coerce_charge(self.anion_charge_label)
        if cation_charge <= 0:
            return "builder_error_cation_positive"
        if anion_charge >= 0:
            return "builder_error_anion_negative"
        return ""

    @rx.var(cache=True)
    def formula(self) -> str:
        if not self.has_full_selection or self.error_key:
            return ""
        cation_charge = _coerce_charge(self.cation_charge_label)
        anion_charge = _coerce_charge(self.anion_charge_label)
        try:
            return build_binary_formula(
                self.cation_symbol,
                cation_charge,
                self.anion_symbol,
                anion_charge,
            )
        except ValueError:
            return ""


def _picker(label, options: list[str], value, on_change) -> rx.Component:
    return rx.vstack(
        rx.text(label, color=_LABEL_MUTED, font_size="0.78rem"),
        rx.select(
            options,
            value=value,
            on_change=on_change,
            placeholder=TranslationState.t["builder_select_placeholder"],
            color_scheme="iris",
            width="100%",
        ),
        spacing="1",
        align="stretch",
        flex_grow="1",
    )


def _charge_picker(label, choices, value, on_change) -> rx.Component:
    return rx.vstack(
        rx.text(label, color=_LABEL_MUTED, font_size="0.78rem"),
        rx.select(
            choices,
            value=value,
            on_change=on_change,
            placeholder=TranslationState.t["builder_charge_placeholder"],
            color_scheme="iris",
            width="100%",
        ),
        spacing="1",
        align="stretch",
        width="110px",
    )


def compound_builder_view() -> rx.Component:
    return rx.vstack(
        rx.text(
            TranslationState.t["builder_subtitle"],
            color=_LABEL_MUTED,
            font_size="0.85rem",
        ),
        rx.hstack(
            _picker(
                TranslationState.t["builder_cation_element"],
                _CATION_OPTIONS,
                CompoundBuilderState.cation_option,
                CompoundBuilderState.set_cation_option,
            ),
            _charge_picker(
                TranslationState.t["builder_charge"],
                CompoundBuilderState.cation_charge_choices,
                CompoundBuilderState.cation_charge_label,
                CompoundBuilderState.set_cation_charge,
            ),
            spacing="3",
            width="100%",
            max_width="540px",
        ),
        rx.hstack(
            _picker(
                TranslationState.t["builder_anion_element"],
                _ANION_OPTIONS,
                CompoundBuilderState.anion_option,
                CompoundBuilderState.set_anion_option,
            ),
            _charge_picker(
                TranslationState.t["builder_charge"],
                CompoundBuilderState.anion_charge_choices,
                CompoundBuilderState.anion_charge_label,
                CompoundBuilderState.set_anion_charge,
            ),
            spacing="3",
            width="100%",
            max_width="540px",
        ),
        rx.cond(
            CompoundBuilderState.error_key != "",
            rx.text(
                TranslationState.t[CompoundBuilderState.error_key],
                color=_ERROR_COLOR,
                font_size="0.85rem",
            ),
        ),
        rx.cond(
            CompoundBuilderState.formula != "",
            rx.vstack(
                rx.text(
                    TranslationState.t["builder_formula_label"],
                    color=_LABEL_MUTED,
                    font_size="0.78rem",
                    margin_top="0.5rem",
                ),
                rx.text(
                    CompoundBuilderState.formula,
                    color=DARK_FOREGROUND,
                    font_size="2rem",
                    font_weight="700",
                    font_family="'Cascadia Code', 'Consolas', monospace",
                    line_height="1.1",
                ),
                spacing="1",
                align="start",
            ),
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )
