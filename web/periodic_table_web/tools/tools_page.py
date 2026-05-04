"""Top-level Reflex component for the ``/tools`` route.

Holds the four-tab strip and dispatches to each tool's view via
``rx.match``. Each tool view is a thin function imported from a
sibling module — this file stays the layout shell.

Until later commits land, the per-tool views render an empty
placeholder so the page boots cleanly with the navigation skeleton in
place.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.i18n import TranslationState
from periodic_table_web.nav import header
from periodic_table_web.theme import DARK_BACKGROUND, DARK_FOREGROUND, DARK_PANEL
from periodic_table_web.tools.compound_builder_view import compound_builder_view
from periodic_table_web.tools.molar_mass_view import molar_mass_view
from periodic_table_web.tools.solubility_view import solubility_view
from periodic_table_web.tools.state import ToolsState
from periodic_table_web.tools.stoichiometry_view import stoichiometry_view

_TAB_BUTTONS: list[tuple[str, str]] = [
    ("molar", "tools_tab_molar"),
    ("stoich", "tools_tab_stoich"),
    ("builder", "tools_tab_builder"),
    ("solubility", "tools_tab_solubility"),
]
_TAB_ACTIVE_BG = "#4e79a7"
_TAB_INACTIVE_BG = "#1f1f2e"


def _tab_button(tool: str, t_key: str) -> rx.Component:
    is_active = ToolsState.active_tool == tool
    return rx.button(
        TranslationState.t[t_key],
        on_click=ToolsState.set_active_tool(tool),
        background=rx.cond(is_active, _TAB_ACTIVE_BG, _TAB_INACTIVE_BG),
        color=DARK_FOREGROUND,
        border="none",
        border_radius="6px",
        padding="8px 14px",
        cursor="pointer",
        font_size="0.85rem",
        font_weight=rx.cond(is_active, "600", "400"),
        flex_grow="1",
    )


def _tab_bar() -> rx.Component:
    return rx.hstack(
        *[_tab_button(tool, t_key) for tool, t_key in _TAB_BUTTONS],
        spacing="2",
        width="100%",
        margin_bottom="1rem",
    )


def _tab_content() -> rx.Component:
    return rx.match(
        ToolsState.active_tool,
        ("molar", molar_mass_view()),
        ("stoich", stoichiometry_view()),
        ("builder", compound_builder_view()),
        ("solubility", solubility_view()),
        molar_mass_view(),
    )


def tools_page() -> rx.Component:
    """Render the ``/tools`` page: nav header + tab strip + tool body."""
    return rx.box(
        rx.vstack(
            header("tools"),
            rx.heading(
                TranslationState.t["tools_heading"],
                size="6",
                color=DARK_FOREGROUND,
                margin_bottom="0.25rem",
            ),
            rx.text(
                TranslationState.t["tools_subtitle"],
                font_size="0.85rem",
                color="#9a9aa8",
                margin_bottom="1rem",
            ),
            _tab_bar(),
            rx.box(
                _tab_content(),
                background=DARK_PANEL,
                border_radius="8px",
                padding="20px",
                width="100%",
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        background=DARK_BACKGROUND,
        min_height="100vh",
        padding="1.5rem 1rem 2rem",
        color=DARK_FOREGROUND,
        font_family="'Segoe UI', system-ui, -apple-system, sans-serif",
    )
