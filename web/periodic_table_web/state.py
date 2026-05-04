"""Reflex State for the browser version.

The State drives four concerns: which element is selected (info card),
the active search query (cell opacity), the active trend mode (cell
background color), and which view is shown in the right panel
(Info / Electron Config / Lewis). Computed vars produce a per-element
color map, a set of visible atomic numbers, and the parsed orbital /
Lewis data for the selected element so each cell can render with a
single Var dereference instead of a 119-way condition.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.electron_view import ShellRow, compute_shell_rows
from periodic_table_web.lewis_view import LewisData, compute_lewis_data
from periodic_table_web.trends import compute_ranges, trend_color
from src.services.data_loader import load_elements

VALID_TREND_MODES: frozenset[str] = frozenset(
    {
        "category",
        "radius",
        "ionization",
        "electron_affinity",
        "electronegativity",
        "metallic",
        "nonmetallic",
    }
)
VALID_RIGHT_PANEL_VIEWS: frozenset[str] = frozenset(
    {"info", "electron", "lewis"}
)

_ELEMENTS: list[dict] = load_elements()
_BY_ATOMIC_NUMBER: dict[int, dict] = {e["atomic_number"]: e for e in _ELEMENTS}
_TREND_RANGES = compute_ranges(_ELEMENTS)
_ALL_ATOMIC_NUMBERS: set[int] = {e["atomic_number"] for e in _ELEMENTS}


def _matches(query: str, element: dict) -> bool:
    return (
        query in element["symbol"].lower()
        or query in element["name"].lower()
        or query in str(element["atomic_number"])
    )


class TableState(rx.State):
    """Selection, search, and trend state for the periodic table view."""

    selected_atomic_number: int | None = None
    search_query: str = ""
    trend_mode: str = "category"
    right_panel_view: str = "info"

    @rx.event
    def select_element(self, atomic_number: int) -> None:
        self.selected_atomic_number = atomic_number

    @rx.event
    def clear_selection(self) -> None:
        self.selected_atomic_number = None

    @rx.event
    def set_search(self, value: str) -> None:
        self.search_query = value

    @rx.event
    def clear_search(self) -> None:
        self.search_query = ""

    @rx.event
    def set_trend(self, mode: str) -> None:
        if mode in VALID_TREND_MODES:
            self.trend_mode = mode

    @rx.event
    def set_right_panel(self, view: str) -> None:
        if view in VALID_RIGHT_PANEL_VIEWS:
            self.right_panel_view = view

    @rx.var(cache=True)
    def has_selection(self) -> bool:
        return self.selected_atomic_number is not None

    @rx.var(cache=True)
    def selected_element(self) -> dict:
        if self.selected_atomic_number is None:
            return {}
        return _BY_ATOMIC_NUMBER.get(self.selected_atomic_number, {})

    @rx.var(cache=True)
    def filtered_atomic_numbers(self) -> set[int]:
        query = self.search_query.strip().lower()
        if not query:
            return set(_ALL_ATOMIC_NUMBERS)
        return {e["atomic_number"] for e in _ELEMENTS if _matches(query, e)}

    @rx.var(cache=True)
    def color_map(self) -> dict[int, str]:
        mode = self.trend_mode
        return {
            e["atomic_number"]: trend_color(e, mode, ranges=_TREND_RANGES)
            for e in _ELEMENTS
        }

    @rx.var(cache=True)
    def orbital_rows(self) -> list[ShellRow]:
        if self.selected_atomic_number is None:
            return []
        element = _BY_ATOMIC_NUMBER.get(self.selected_atomic_number)
        if not element:
            return []
        return compute_shell_rows(element.get("electron_configuration"))

    @rx.var(cache=True)
    def lewis_data(self) -> LewisData:
        if self.selected_atomic_number is None:
            return compute_lewis_data({})
        element = _BY_ATOMIC_NUMBER.get(self.selected_atomic_number) or {}
        return compute_lewis_data(element)
