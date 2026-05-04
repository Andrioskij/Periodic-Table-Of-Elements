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

from periodic_table_web.nav import header
from periodic_table_web.theme import DARK_BACKGROUND, DARK_FOREGROUND, DARK_PANEL
from periodic_table_web.tools.compound_builder_view import compound_builder_view
from periodic_table_web.tools.molar_mass_view import molar_mass_view
from periodic_table_web.tools.state import ToolsState

_TAB_BUTTONS: list[tuple[str, str]] = [
    ("molar", "Molar Mass"),
    ("stoich", "Stoichiometry"),
    ("builder", "Compound Builder"),
    ("solubility", "Solubility"),
]
_TAB_ACTIVE_BG = "#4e79a7"
_TAB_INACTIVE_BG = "#1f1f2e"


def _placeholder(label: str) -> rx.Component:
    return rx.center(
        rx.text(
            f"{label} — coming up in this batch.",
            color="#9a9aa8",
            font_size="0.95rem",
        ),
        min_height="240px",
        width="100%",
    )


def _tab_button(tool: str, label: str) -> rx.Component:
    is_active = ToolsState.active_tool == tool
    return rx.button(
        label,
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
        *[_tab_button(tool, label) for tool, label in _TAB_BUTTONS],
        spacing="2",
        width="100%",
        margin_bottom="1rem",
    )


def _tab_content() -> rx.Component:
    return rx.match(
        ToolsState.active_tool,
        ("molar", molar_mass_view()),
        ("stoich", _placeholder("Stoichiometry")),
        ("builder", compound_builder_view()),
        ("solubility", _placeholder("Solubility")),
        molar_mass_view(),
    )


def tools_page() -> rx.Component:
    """Render the ``/tools`` page: nav header + tab strip + tool body."""
    return rx.box(
        rx.vstack(
            header("tools"),
            rx.heading(
                "Tools",
                size="6",
                color=DARK_FOREGROUND,
                margin_bottom="0.25rem",
            ),
            rx.text(
                "Calculators and lookups built on the same domain logic as the desktop app.",
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
