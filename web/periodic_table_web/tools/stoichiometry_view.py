"""Stoichiometry tab content.

Wraps ``src.domain.stoichiometry`` for the browser: text input for
the equation, optional given-compound + given-mass override, and a
table that shows balanced coefficients alongside molar masses,
moles, and computed masses.
"""

from __future__ import annotations

import reflex as rx
from pydantic import BaseModel

from periodic_table_web.theme import DARK_FOREGROUND
from src.domain.molar_mass import FormulaError
from src.domain.stoichiometry import (
    EquationError,
    balance_equation,
    compute_stoichiometric_masses,
    format_balanced_equation,
    parse_equation,
)
from src.services.data_loader import load_elements

_ELEMENTS = load_elements()
_LABEL_MUTED = "#9a9aa8"
_RESULT_BG = "#1f1f2e"
_ERROR_COLOR = "#f7a8a8"


class StoichRow(BaseModel):
    """One compound entry in the balanced-equation results table."""

    compound: str
    coefficient: int
    molar_mass: float
    moles: float
    mass: float


class _BalanceResult(BaseModel):
    """Internal cache: parsed equation + computed coefficients + display string."""

    reactants: list[str] = []
    products: list[str] = []
    coefficients: list[int] = []
    balanced_text: str = ""
    error_message: str = ""

    @property
    def compounds(self) -> list[str]:
        return self.reactants + self.products


def _balance(equation: str) -> _BalanceResult:
    if not equation.strip():
        return _BalanceResult()
    try:
        reactants, products = parse_equation(equation)
        coefficients = balance_equation(equation)
        text = format_balanced_equation(reactants, products, coefficients)
    except (EquationError, FormulaError) as exc:
        return _BalanceResult(error_message=str(exc))
    return _BalanceResult(
        reactants=reactants,
        products=products,
        coefficients=coefficients,
        balanced_text=text,
    )


class StoichiometryState(rx.State):
    """Equation input and optional given-compound/mass overrides."""

    equation: str = ""
    given_compound: str = ""
    given_mass_text: str = ""

    @rx.event
    def set_equation(self, value: str) -> None:
        self.equation = value
        # If the equation changes the previous given_compound is likely
        # stale — clear it so the rendered select stays consistent.
        if self.given_compound and self.given_compound not in _balance(value).compounds:
            self.given_compound = ""

    @rx.event
    def set_given_compound(self, value: str) -> None:
        self.given_compound = value

    @rx.event
    def set_given_mass(self, value: str) -> None:
        self.given_mass_text = value

    @rx.var(cache=True)
    def has_input(self) -> bool:
        return bool(self.equation.strip())

    @rx.var(cache=True)
    def balanced_text(self) -> str:
        return _balance(self.equation).balanced_text

    @rx.var(cache=True)
    def error_message(self) -> str:
        return _balance(self.equation).error_message

    @rx.var(cache=True)
    def compound_options(self) -> list[str]:
        return _balance(self.equation).compounds

    @rx.var(cache=True)
    def rows(self) -> list[StoichRow]:
        result = _balance(self.equation)
        if result.error_message or not result.compounds:
            return []

        given_mass: float | None = None
        given_compound: str | None = None
        if self.given_compound and self.given_mass_text.strip():
            try:
                given_mass = float(self.given_mass_text.replace(",", "."))
                given_compound = self.given_compound
            except ValueError:
                given_mass = None
                given_compound = None
        try:
            raw = compute_stoichiometric_masses(
                result.reactants,
                result.products,
                result.coefficients,
                _ELEMENTS,
                given_compound=given_compound,
                given_mass_grams=given_mass,
            )
        except (EquationError, FormulaError):
            return []
        return [StoichRow(**row) for row in raw]


def _stoich_row(row: StoichRow) -> rx.Component:
    return rx.hstack(
        rx.text(row.compound, color=DARK_FOREGROUND, font_weight="600", min_width="120px"),
        rx.text(row.coefficient, color=DARK_FOREGROUND, width="60px"),
        rx.text(
            rx.fragment(row.molar_mass, " g/mol"),
            color=DARK_FOREGROUND,
            font_family="'Cascadia Code', 'Consolas', monospace",
            font_size="0.85rem",
            width="140px",
        ),
        rx.text(
            row.moles,
            color=DARK_FOREGROUND,
            font_family="'Cascadia Code', 'Consolas', monospace",
            font_size="0.85rem",
            width="100px",
        ),
        rx.text(
            rx.fragment(row.mass, " g"),
            color=DARK_FOREGROUND,
            font_family="'Cascadia Code', 'Consolas', monospace",
            font_size="0.85rem",
            text_align="right",
            flex_grow="1",
        ),
        spacing="3",
        width="100%",
        padding_y="4px",
        border_bottom="1px solid #2a2a3a",
    )


def _stoich_table() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text("Compound", color=_LABEL_MUTED, font_size="0.78rem", min_width="120px"),
            rx.text("Coeff.", color=_LABEL_MUTED, font_size="0.78rem", width="60px"),
            rx.text("Molar mass", color=_LABEL_MUTED, font_size="0.78rem", width="140px"),
            rx.text("Moles", color=_LABEL_MUTED, font_size="0.78rem", width="100px"),
            rx.text("Mass", color=_LABEL_MUTED, font_size="0.78rem", text_align="right", flex_grow="1"),
            spacing="3",
            width="100%",
            padding_y="4px",
            border_bottom="1px solid #2a2a3a",
        ),
        rx.foreach(StoichiometryState.rows, _stoich_row),
        spacing="0",
        width="100%",
        margin_top="0.75rem",
    )


def stoichiometry_view() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Enter a chemical equation. Use '->' (or '=' / '→') to separate reactants and products.",
            color=_LABEL_MUTED,
            font_size="0.85rem",
        ),
        rx.input(
            placeholder="e.g. H2 + O2 -> H2O",
            value=StoichiometryState.equation,
            on_change=StoichiometryState.set_equation,
            background=_RESULT_BG,
            color=DARK_FOREGROUND,
            border="1px solid #2a2a3a",
            border_radius="6px",
            padding="8px 12px",
            font_family="'Cascadia Code', 'Consolas', monospace",
            width="100%",
            max_width="540px",
        ),
        rx.cond(
            StoichiometryState.has_input,
            rx.cond(
                StoichiometryState.error_message != "",
                rx.text(
                    StoichiometryState.error_message,
                    color=_ERROR_COLOR,
                    font_size="0.85rem",
                    margin_top="0.5rem",
                ),
                rx.vstack(
                    rx.text(
                        StoichiometryState.balanced_text,
                        color=DARK_FOREGROUND,
                        font_family="'Cascadia Code', 'Consolas', monospace",
                        font_size="1.1rem",
                        font_weight="600",
                        margin_top="0.5rem",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Given compound", color=_LABEL_MUTED, font_size="0.78rem"),
                            rx.select(
                                StoichiometryState.compound_options,
                                value=StoichiometryState.given_compound,
                                on_change=StoichiometryState.set_given_compound,
                                placeholder="Optional — pick one",
                                color_scheme="iris",
                                width="100%",
                            ),
                            spacing="1",
                            align="stretch",
                            flex_grow="1",
                        ),
                        rx.vstack(
                            rx.text("Mass (g)", color=_LABEL_MUTED, font_size="0.78rem"),
                            rx.input(
                                placeholder="e.g. 18",
                                value=StoichiometryState.given_mass_text,
                                on_change=StoichiometryState.set_given_mass,
                                background=_RESULT_BG,
                                color=DARK_FOREGROUND,
                                border="1px solid #2a2a3a",
                                border_radius="6px",
                                padding="6px 10px",
                                width="120px",
                            ),
                            spacing="1",
                            align="stretch",
                        ),
                        spacing="3",
                        width="100%",
                        max_width="540px",
                        margin_top="0.5rem",
                    ),
                    _stoich_table(),
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
