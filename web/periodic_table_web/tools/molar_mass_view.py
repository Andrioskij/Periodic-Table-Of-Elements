"""Molar Mass tab content.

Reuses ``src.domain.molar_mass`` for parsing and computation; this
module only adds the Reflex glue (input handler + computed vars +
component tree) and a pydantic row model so the percent-composition
table can render through ``rx.foreach``.
"""

from __future__ import annotations

import reflex as rx
from pydantic import BaseModel

from periodic_table_web.i18n import TranslationState
from periodic_table_web.theme import MONO_FONT_FAMILY
from periodic_table_web.theme_state import ThemeState
from src.domain.molar_mass import (
    FormulaError,
    compute_molar_mass,
    compute_percent_composition,
    parse_formula,
)
from src.services.data_loader import load_elements

_ELEMENTS = load_elements()


class CompositionRow(BaseModel):
    """One element's contribution to a compound's molar mass."""

    symbol: str
    count: int
    mass: float
    percent: float


class MolarMassState(rx.State):
    """Formula input + cached parse / computation results."""

    formula: str = ""
    show_composition: bool = False

    @rx.event
    def set_formula(self, value: str) -> None:
        self.formula = value

    @rx.event
    def toggle_composition(self, value: bool) -> None:
        self.show_composition = value

    @rx.var(cache=True)
    def has_input(self) -> bool:
        return bool(self.formula.strip())

    @rx.var(cache=True)
    def molar_mass_value(self) -> float:
        if not self.has_input:
            return 0.0
        try:
            atoms = parse_formula(self.formula)
            return round(compute_molar_mass(atoms, _ELEMENTS), 4)
        except FormulaError:
            return 0.0

    @rx.var(cache=True)
    def error_message(self) -> str:
        if not self.has_input:
            return ""
        try:
            atoms = parse_formula(self.formula)
            compute_molar_mass(atoms, _ELEMENTS)
        except FormulaError as exc:
            return str(exc)
        return ""

    @rx.var(cache=True)
    def composition_rows(self) -> list[CompositionRow]:
        if not self.has_input:
            return []
        try:
            atoms = parse_formula(self.formula)
            rows = compute_percent_composition(atoms, _ELEMENTS)
        except FormulaError:
            return []
        return [CompositionRow(**row) for row in rows]


def _composition_row(row: CompositionRow) -> rx.Component:
    return rx.hstack(
        rx.text(row.symbol, color=ThemeState.colors["foreground"], font_weight="600", width="48px"),
        rx.text(row.count, color=ThemeState.colors["foreground"], width="48px"),
        rx.text(
            rx.fragment(row.mass, " u"),
            color=ThemeState.colors["foreground"],
            font_family=MONO_FONT_FAMILY,
            font_size="0.85rem",
            width="120px",
        ),
        rx.text(
            rx.fragment(row.percent, " %"),
            color=ThemeState.colors["foreground"],
            font_family=MONO_FONT_FAMILY,
            font_size="0.85rem",
            text_align="right",
            flex_grow="1",
        ),
        spacing="3",
        width="100%",
        padding_y="4px",
        border_bottom="1px solid " + ThemeState.colors["border"],
    )


def _composition_table() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(TranslationState.t["molar_col_symbol"], color=ThemeState.colors["text_muted"], font_size="0.78rem", width="48px",),
            rx.text(TranslationState.t["molar_col_count"], color=ThemeState.colors["text_muted"], font_size="0.78rem", width="48px",),
            rx.text(TranslationState.t["molar_col_mass"], color=ThemeState.colors["text_muted"], font_size="0.78rem", width="120px"),
            rx.text(TranslationState.t["molar_col_percent"], color=ThemeState.colors["text_muted"], font_size="0.78rem", text_align="right", flex_grow="1"),
            spacing="3",
            width="100%",
            padding_y="4px",
            border_bottom="1px solid " + ThemeState.colors["border"],
        ),
        rx.foreach(MolarMassState.composition_rows, _composition_row),
        spacing="0",
        width="100%",
        margin_top="0.75rem",
    )


def molar_mass_view() -> rx.Component:
    return rx.vstack(
        rx.text(
            TranslationState.t["molar_subtitle"],
            color=ThemeState.colors["text_muted"],
            font_size="0.85rem",
        ),
        rx.input(
            placeholder=TranslationState.t["molar_placeholder"],
            value=MolarMassState.formula,
            on_change=MolarMassState.set_formula,
            background=ThemeState.colors["input_bg"],
            color=ThemeState.colors["foreground"],
            border="1px solid " + ThemeState.colors["border"],
            border_radius="6px",
            padding="8px 12px",
            font_family=MONO_FONT_FAMILY,
            width="100%",
            max_width="540px",
        ),
        rx.cond(
            MolarMassState.has_input,
            rx.cond(
                MolarMassState.error_message != "",
                rx.text(
                    MolarMassState.error_message,
                    color=ThemeState.colors["error"],
                    font_size="0.85rem",
                    margin_top="0.5rem",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            MolarMassState.molar_mass_value,
                            color=ThemeState.colors["foreground"],
                            font_size="2rem",
                            font_weight="700",
                            line_height="1.1",
                            font_family=MONO_FONT_FAMILY,
                        ),
                        rx.text(
                            "g/mol",
                            color=ThemeState.colors["text_muted"],
                            font_size="1rem",
                        ),
                        spacing="2",
                        align="baseline",
                        margin_top="0.5rem",
                    ),
                    rx.hstack(
                        rx.checkbox(
                            TranslationState.t["molar_show_composition"],
                            checked=MolarMassState.show_composition,
                            on_change=MolarMassState.toggle_composition,
                            color_scheme="iris",
                        ),
                        spacing="2",
                        margin_top="0.5rem",
                    ),
                    rx.cond(
                        MolarMassState.show_composition,
                        _composition_table(),
                    ),
                    spacing="2",
                    align="stretch",
                    width="100%",
                ),
            ),
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )
