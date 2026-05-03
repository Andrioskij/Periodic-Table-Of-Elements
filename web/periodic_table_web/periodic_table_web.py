"""Reflex entry point for the browser version of the periodic table."""

import reflex as rx

from periodic_table_web.theme import (
    DARK_BACKGROUND,
    DARK_FOREGROUND,
    DARK_LABEL_MUTED,
    DARK_PANEL,
    category_color,
)
from src.services.data_loader import load_elements

ELEMENTS = load_elements()
GRID_GAP_ROW = 8


def _grid_row(display_row: int) -> int:
    """Insert a blank grid row between the main table and the f-block."""
    return display_row if display_row < GRID_GAP_ROW else display_row + 1


def _element_cell(element: dict) -> rx.Component:
    color = category_color(element.get("category"))
    return rx.box(
        rx.text(
            str(element["atomic_number"]),
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
        background=color,
        border=f"1px solid {DARK_PANEL}",
        border_radius="4px",
        padding="4px 4px 3px",
        display="flex",
        flex_direction="column",
        justify_content="space-between",
        align_items="center",
        height="64px",
        grid_column=str(element["display_column"]),
        grid_row=str(_grid_row(element["display_row"])),
    )


def _grid() -> rx.Component:
    return rx.box(
        *[_element_cell(e) for e in ELEMENTS],
        display="grid",
        grid_template_columns="repeat(18, minmax(54px, 1fr))",
        grid_template_rows="repeat(7, auto) 18px repeat(2, auto)",
        gap="3px",
        width="100%",
        max_width="1280px",
        margin="0 auto",
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
                "Browser preview — static render (Batch 6 foundation)",
                font_size="0.85rem",
                color="#9a9aa8",
                margin_bottom="1.25rem",
            ),
            _grid(),
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
