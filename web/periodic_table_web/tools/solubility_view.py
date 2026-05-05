"""Solubility matrix tab content.

Renders the static 14×10 cation/anion solubility table from
``src.domain.solubility``. Three discrete colors map onto the three
verdicts; nothing is highlighted by default. Optional select inputs
let the user dim everything except one row and/or column.
"""

from __future__ import annotations

import reflex as rx
from pydantic import BaseModel

from periodic_table_web.i18n import TranslationState
from periodic_table_web.theme_state import ThemeState
from src.domain.solubility import ANIONS, CATIONS, get_solubility_matrix

# Verdict colours (cell backgrounds) stay fixed across themes — they
# carry domain meaning (green=soluble / amber=slightly / red=insoluble)
# and read against both panel backgrounds.
_VERDICT_COLORS: dict[str, str] = {
    "soluble": "#3fa34d",
    "slightly_soluble": "#d9a13b",
    "insoluble": "#c14953",
}
# Map verdict keyword -> i18n translation key. The verdict itself stays
# inside the MatrixCell model so the view can index ``TranslationState.t``
# at render time and switch language without rebuilding the matrix.
_VERDICT_T_KEYS: dict[str, str] = {
    "soluble": "solubility_soluble",
    "slightly_soluble": "solubility_slightly_soluble",
    "insoluble": "solubility_insoluble",
}


class MatrixCell(BaseModel):
    """One cation/anion cell with its precomputed verdict + label key."""

    verdict: str
    label_key: str
    color: str
    cation: str
    anion: str


class MatrixRow(BaseModel):
    """A whole row keyed by cation, holding 10 cells (one per anion)."""

    cation: str
    cells: list[MatrixCell]


def _build_rows() -> list[MatrixRow]:
    raw = get_solubility_matrix()
    rows: list[MatrixRow] = []
    for i, cation in enumerate(CATIONS):
        cells = []
        for j, anion in enumerate(ANIONS):
            verdict = raw[i][j]
            cells.append(
                MatrixCell(
                    verdict=verdict,
                    label_key=_VERDICT_T_KEYS.get(verdict, ""),
                    color=_VERDICT_COLORS.get(verdict, "#7a7a8a"),
                    cation=cation,
                    anion=anion,
                )
            )
        rows.append(MatrixRow(cation=cation, cells=cells))
    return rows


_MATRIX_ROWS: list[MatrixRow] = _build_rows()
# "(All)" is the sentinel the highlight dropdowns emit when no row/column
# is filtered. The desktop's solubility dialog uses an analogous "any"
# sentinel; we keep this one in English because rx.select with a flat
# string list treats each entry as both value and label, so a translated
# label would also change the sentinel value the state compares against.
# Documented in the PR as a deliberate scope cut.
_CATION_OPTIONS: list[str] = ["(All)", *CATIONS]
_ANION_OPTIONS: list[str] = ["(All)", *ANIONS]


class SolubilityState(rx.State):
    """Highlight selectors — the matrix itself is static."""

    highlight_cation: str = "(All)"
    highlight_anion: str = "(All)"

    @rx.event
    def set_highlight_cation(self, value: str) -> None:
        self.highlight_cation = value

    @rx.event
    def set_highlight_anion(self, value: str) -> None:
        self.highlight_anion = value


def _cell(cell: MatrixCell) -> rx.Component:
    cation_match = SolubilityState.highlight_cation == "(All)"
    cation_match = cation_match | (SolubilityState.highlight_cation == cell.cation)
    anion_match = SolubilityState.highlight_anion == "(All)"
    anion_match = anion_match | (SolubilityState.highlight_anion == cell.anion)
    is_dim = ~(cation_match & anion_match)
    return rx.box(
        rx.text(
            TranslationState.t[cell.label_key],
            color="#ffffff",
            font_size="0.7rem",
            text_align="center",
            line_height="1",
        ),
        background=cell.color,
        opacity=rx.cond(is_dim, "0.25", "1"),
        padding="6px 4px",
        border_radius="4px",
        min_width="92px",
        min_height="32px",
        display="flex",
        align_items="center",
        justify_content="center",
    )


def _row(row: MatrixRow) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.text(
                row.cation,
                color=ThemeState.colors["foreground"],
                font_size="0.85rem",
                font_weight="600",
                text_align="right",
            ),
            min_width="80px",
            padding_right="6px",
            position="sticky",
            left="0",
            background=ThemeState.colors["panel"],
            z_index="1",
        ),
        *[_cell(cell) for cell in row.cells],
        spacing="1",
        width="max-content",
    )


def _header_row() -> rx.Component:
    return rx.hstack(
        rx.box(
            min_width="80px",
            padding_right="6px",
            position="sticky",
            left="0",
            background=ThemeState.colors["panel"],
            z_index="1",
        ),
        *[
            rx.box(
                rx.text(
                    anion,
                    color=ThemeState.colors["text_muted"],
                    font_size="0.78rem",
                    text_align="center",
                ),
                min_width="92px",
            )
            for anion in ANIONS
        ],
        spacing="1",
        width="max-content",
    )


def _legend_chip(verdict: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            background=_VERDICT_COLORS[verdict],
            width="14px",
            height="14px",
            border_radius="3px",
        ),
        rx.text(
            TranslationState.t[_VERDICT_T_KEYS[verdict]],
            color=ThemeState.colors["text_muted"],
            font_size="0.78rem",
        ),
        spacing="2",
        align="center",
    )


def solubility_view() -> rx.Component:
    return rx.vstack(
        rx.text(
            TranslationState.t["solubility_subtitle"],
            color=ThemeState.colors["text_muted"],
            font_size="0.85rem",
        ),
        rx.hstack(
            rx.vstack(
                rx.text(TranslationState.t["solubility_highlight_cation"], color=ThemeState.colors["text_muted"], font_size="0.78rem"),
                rx.select(
                    _CATION_OPTIONS,
                    value=SolubilityState.highlight_cation,
                    on_change=SolubilityState.set_highlight_cation,
                    color_scheme="iris",
                    width="180px",
                ),
                spacing="1",
                align="stretch",
            ),
            rx.vstack(
                rx.text(TranslationState.t["solubility_highlight_anion"], color=ThemeState.colors["text_muted"], font_size="0.78rem"),
                rx.select(
                    _ANION_OPTIONS,
                    value=SolubilityState.highlight_anion,
                    on_change=SolubilityState.set_highlight_anion,
                    color_scheme="iris",
                    width="180px",
                ),
                spacing="1",
                align="stretch",
            ),
            rx.hstack(
                _legend_chip("soluble"),
                _legend_chip("slightly_soluble"),
                _legend_chip("insoluble"),
                spacing="3",
                align="center",
                margin_left="auto",
                flex_wrap="wrap",
            ),
            spacing="3",
            align="end",
            width="100%",
            flex_wrap="wrap",
        ),
        rx.box(
            rx.vstack(
                _header_row(),
                *[_row(row) for row in _MATRIX_ROWS],
                spacing="1",
                align="start",
            ),
            overflow_x="auto",
            width="100%",
            margin_top="0.75rem",
        ),
        spacing="3",
        align="stretch",
        width="100%",
    )
