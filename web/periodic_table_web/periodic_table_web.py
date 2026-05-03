"""Reflex entry point for the browser version of the periodic table."""

import reflex as rx

from periodic_table_web.state import TableState
from periodic_table_web.theme import (
    DARK_BACKGROUND,
    DARK_FOREGROUND,
    DARK_LABEL_MUTED,
    DARK_PANEL,
)
from src.services.data_loader import load_elements

ELEMENTS = load_elements()
GRID_GAP_ROW = 8
SELECTED_BORDER_COLOR = "#f5d442"
TREND_BUTTONS: list[tuple[str, str]] = [
    ("category", "Default"),
    ("radius", "Radius"),
    ("ionization", "Ionization"),
    ("electron_affinity", "Electron Affinity"),
    ("electronegativity", "Electronegativity"),
    ("metallic", "Metallic"),
    ("nonmetallic", "Nonmetallic"),
]


def _grid_row(display_row: int) -> int:
    """Insert a blank grid row between the main table and the f-block."""
    return display_row if display_row < GRID_GAP_ROW else display_row + 1


def _element_cell(element: dict) -> rx.Component:
    atomic_number = element["atomic_number"]
    is_selected = TableState.selected_atomic_number == atomic_number
    is_visible = TableState.filtered_atomic_numbers.contains(atomic_number)
    return rx.box(
        rx.text(
            str(atomic_number),
            font_size="0.65rem",
            color=DARK_LABEL_MUTED,
            line_height="1",
            text_align="left",
            width="100%",
        ),
        rx.text(
            element["symbol"],
            font_size="1.4rem",
            font_weight="700",
            color=DARK_LABEL_MUTED,
            line_height="1",
            text_align="center",
            margin_top="2px",
        ),
        rx.text(
            element["name"],
            font_size="0.55rem",
            color=DARK_LABEL_MUTED,
            line_height="1.1",
            text_align="center",
            white_space="nowrap",
            overflow="hidden",
            text_overflow="ellipsis",
            width="100%",
        ),
        background=TableState.color_map[atomic_number],
        border=rx.cond(
            is_selected,
            f"2px solid {SELECTED_BORDER_COLOR}",
            f"1px solid {DARK_PANEL}",
        ),
        opacity=rx.cond(is_visible, "1", "0.25"),
        cursor="pointer",
        border_radius="4px",
        padding="3px 4px 2px",
        display="flex",
        flex_direction="column",
        justify_content="space-between",
        align_items="center",
        height="64px",
        grid_column=str(element["display_column"]),
        grid_row=str(_grid_row(element["display_row"])),
        on_click=TableState.select_element(atomic_number),
        _hover={"filter": "brightness(1.15)"},
    )


def _grid() -> rx.Component:
    return rx.box(
        *[_element_cell(e) for e in ELEMENTS],
        display="grid",
        grid_template_columns="repeat(18, minmax(48px, 1fr))",
        grid_template_rows="repeat(7, auto) 18px repeat(2, auto)",
        gap="3px",
        width="100%",
        flex_grow="1",
        min_width="0",
    )


def _search_box() -> rx.Component:
    return rx.box(
        rx.input(
            placeholder="Search by name, symbol, or atomic number…",
            value=TableState.search_query,
            on_change=TableState.set_search,
            background=DARK_PANEL,
            color=DARK_FOREGROUND,
            border=f"1px solid {DARK_PANEL}",
            border_radius="6px",
            padding="6px 10px",
            width="100%",
            max_width="420px",
        ),
        rx.cond(
            TableState.search_query != "",
            rx.button(
                "✕",
                on_click=TableState.clear_search,
                background="transparent",
                color=DARK_FOREGROUND,
                border="none",
                cursor="pointer",
                font_size="0.9rem",
                padding="0 8px",
                margin_left="6px",
            ),
        ),
        display="flex",
        align_items="center",
        margin_bottom="0.75rem",
    )


def _trend_button(mode: str, label: str) -> rx.Component:
    is_active = TableState.trend_mode == mode
    return rx.button(
        label,
        on_click=TableState.set_trend(mode),
        background=rx.cond(is_active, "#4e79a7", DARK_PANEL),
        color=DARK_FOREGROUND,
        border=f"1px solid {DARK_PANEL}",
        border_radius="6px",
        padding="4px 12px",
        cursor="pointer",
        font_size="0.8rem",
        font_weight=rx.cond(is_active, "600", "400"),
    )


def _trend_buttons() -> rx.Component:
    return rx.hstack(
        *[_trend_button(mode, label) for mode, label in TREND_BUTTONS],
        spacing="2",
        flex_wrap="wrap",
        margin_bottom="1rem",
    )


def _info_row(label: str, value) -> rx.Component:
    return rx.hstack(
        rx.text(label, color="#9a9aa8", font_size="0.78rem", min_width="120px"),
        rx.text(
            value,
            color=DARK_FOREGROUND,
            font_size="0.85rem",
            text_align="right",
            flex_grow="1",
        ),
        justify="between",
        width="100%",
        spacing="2",
    )


def _opt(value, suffix: str = "") -> rx.Component:
    return rx.cond(value != None, rx.fragment(value, suffix), "—")  # noqa: E711


def _info_card_content() -> rx.Component:
    el = TableState.selected_element
    return rx.vstack(
        rx.hstack(
            rx.text(
                el["symbol"],
                font_size="3rem",
                font_weight="700",
                line_height="1",
                color=DARK_FOREGROUND,
            ),
            rx.vstack(
                rx.text(
                    el["atomic_number"],
                    color="#9a9aa8",
                    font_size="0.85rem",
                    line_height="1",
                ),
                rx.text(
                    el["name"],
                    font_size="1.4rem",
                    font_weight="600",
                    color=DARK_FOREGROUND,
                    line_height="1.1",
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            align="center",
            width="100%",
            margin_bottom="0.5rem",
        ),
        rx.divider(color_scheme="gray"),
        _info_row("Atomic mass", rx.fragment(el["atomic_mass"], " u")),
        _info_row("Category", el["category"]),
        _info_row("Period", el["period"]),
        _info_row("Group", _opt(el["group"])),
        _info_row("Standard state", _opt(el["standard_state"])),
        _info_row(
            "Electron config.",
            rx.text(
                el["electron_configuration"],
                font_family="'Cascadia Code', 'Consolas', monospace",
                font_size="0.8rem",
                color=DARK_FOREGROUND,
            ),
        ),
        _info_row("Electronegativity", _opt(el["electronegativity"])),
        _info_row("Atomic radius", _opt(el["atomic_radius"], " pm")),
        _info_row("Ionization energy", _opt(el["ionization_energy"], " eV")),
        _info_row("Electron affinity", _opt(el["electron_affinity"], " eV")),
        _info_row("Oxidation states", _opt(el["oxidation_states"])),
        _info_row("Melting point", _opt(el["melting_point"], " K")),
        _info_row("Boiling point", _opt(el["boiling_point"], " K")),
        _info_row("Density", _opt(el["density"], " g/cm³")),
        _info_row("Discovered", _opt(el["year_discovered"])),
        spacing="2",
        align="stretch",
        width="100%",
    )


def _info_placeholder() -> rx.Component:
    return rx.center(
        rx.text(
            "Select an element to see its details.",
            color="#9a9aa8",
            font_size="0.9rem",
            text_align="center",
        ),
        height="100%",
        min_height="180px",
    )


def _info_card() -> rx.Component:
    return rx.box(
        rx.cond(
            TableState.has_selection,
            _info_card_content(),
            _info_placeholder(),
        ),
        background=DARK_PANEL,
        border_radius="8px",
        padding="16px",
        width={"base": "100%", "lg": "360px"},
        flex_shrink="0",
        max_height={"base": "none", "lg": "calc(100vh - 9rem)"},
        overflow_y="auto",
    )


def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Periodic Table of Elements",
                size="6",
                color=DARK_FOREGROUND,
                margin_bottom="0.25rem",
            ),
            rx.text(
                "Click an element for details · search by name, symbol, or atomic number · switch trend view above the table.",
                font_size="0.85rem",
                color="#9a9aa8",
                margin_bottom="1.25rem",
            ),
            _search_box(),
            _trend_buttons(),
            rx.flex(
                _grid(),
                _info_card(),
                direction={"base": "column", "lg": "row"},
                gap="1.5rem",
                width="100%",
                align="stretch",
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


app = rx.App(
    theme=rx.theme(appearance="dark", accent_color="iris"),
)
app.add_page(index, title="Periodic Table")
