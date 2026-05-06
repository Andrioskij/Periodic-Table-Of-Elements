"""Orbital diagram view for the right panel (Electron Configuration tab).

Reuses the desktop's pure-Python parsers (configuration_to_map,
fill_boxes) and exposes a Reflex component that renders the
orbital boxes with Hund-rule arrows for the selected element.

Noble-gas core handling: the original configuration string is shown
verbatim above the diagram (so [He]2s2 stays readable as "[He] 2s²"),
and the diagram itself uses the *expanded* shell list so every
subshell, including those hidden behind a noble-gas prefix, is
visible. This is the most pedagogically useful split — students see
where the core stops while still getting a full visual map.
"""

from __future__ import annotations

import reflex as rx
from pydantic import BaseModel

from periodic_table_web.i18n import TranslationState
from periodic_table_web.theme import MONO_FONT_FAMILY
from periodic_table_web.theme_state import ThemeState
from src.config.static_data import ORBITAL_BOX_COUNTS, VALID_SUBSHELLS
from src.domain.electron_configuration import configuration_to_map, fill_boxes

ARROW_UP = "↑"
ARROW_DOWN = "↓"
SUPERSCRIPTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

BOX_BORDER = "#5a5a72"
ARROW_UP_COLOR = "#9ec5fe"
ARROW_DOWN_COLOR = "#f7a8a8"
SHELL_LABEL_COLOR = "#9a9aa8"
BLOCK_LABEL_COLOR = "#cfcfdc"


def _format_block_label(level: int, subshell: str, electrons: int) -> str:
    return f"{level}{subshell}{str(electrons).translate(SUPERSCRIPTS)}"


class OrbitalBlock(BaseModel):
    """One subshell within a shell — labelled box group with Hund-filled arrows."""

    label: str
    boxes: list[int]


class ShellRow(BaseModel):
    """All occupied subshells for a single principal quantum number."""

    shell: int
    blocks: list[OrbitalBlock]


def compute_shell_rows(config_text: str | None) -> list[ShellRow]:
    """Build the data the orbital diagram component renders.

    Returns a list of rows, one per electron shell that has any
    occupied subshell. Each row carries:

    - ``shell``: the principal quantum number (1..7)
    - ``blocks``: list of OrbitalBlock(label, boxes), where ``boxes``
      is a list of 0/1/2 (arrows per orbital under Hund's rule).
    """
    if not config_text:
        return []

    occupancy = configuration_to_map(config_text)
    if not occupancy:
        return []

    rows: list[ShellRow] = []
    for level in range(1, 8):
        blocks: list[OrbitalBlock] = []
        for subshell in VALID_SUBSHELLS[level]:
            key = f"{level}{subshell}"
            electrons = occupancy.get(key)
            if not electrons:
                continue
            box_count = ORBITAL_BOX_COUNTS[subshell]
            boxes = fill_boxes(electrons, box_count)
            blocks.append(
                OrbitalBlock(
                    label=_format_block_label(level, subshell, electrons),
                    boxes=boxes,
                )
            )
        if blocks:
            rows.append(ShellRow(shell=level, blocks=blocks))
    return rows


def _arrow_pair(box) -> rx.Component:
    return rx.box(
        rx.cond(
            box >= 1,
            rx.text(
                ARROW_UP,
                color=ARROW_UP_COLOR,
                font_size="0.85rem",
                line_height="1",
                font_weight="700",
            ),
            rx.text(" ", font_size="0.85rem", line_height="1"),
        ),
        rx.cond(
            box == 2,
            rx.text(
                ARROW_DOWN,
                color=ARROW_DOWN_COLOR,
                font_size="0.85rem",
                line_height="1",
                font_weight="700",
            ),
            rx.text(" ", font_size="0.85rem", line_height="1"),
        ),
        display="flex",
        flex_direction="row",
        justify_content="center",
        align_items="center",
        gap="1px",
        width="28px",
        height="28px",
        border=f"1px solid {BOX_BORDER}",
        border_radius="3px",
        background="transparent",
        flex_shrink="0",
    )


def _block(block: OrbitalBlock) -> rx.Component:
    return rx.vstack(
        rx.text(
            block.label,
            font_family=MONO_FONT_FAMILY,
            font_size="0.78rem",
            color=BLOCK_LABEL_COLOR,
            line_height="1",
            margin_bottom="2px",
        ),
        rx.hstack(
            rx.foreach(block.boxes, _arrow_pair),
            spacing="1",
            align="center",
        ),
        spacing="0",
        align="start",
    )


def _shell_row(row: ShellRow) -> rx.Component:
    return rx.hstack(
        rx.text(
            row.shell,
            color=SHELL_LABEL_COLOR,
            font_size="0.75rem",
            font_weight="600",
            min_width="14px",
            text_align="right",
        ),
        rx.hstack(
            rx.foreach(row.blocks, _block),
            spacing="4",
            align="end",
            flex_wrap="wrap",
        ),
        spacing="3",
        align="end",
        width="100%",
    )


def electron_view(state, placeholder) -> rx.Component:
    """Right-panel content for the Electron Configuration tab.

    ``state`` is the TableState class, passed in to avoid an import
    cycle with periodic_table_web.py. ``placeholder`` is the shared
    "select an element" widget reused across all three tabs.
    """
    el = state.selected_element
    return rx.cond(
        state.has_selection,
        rx.vstack(
            rx.hstack(
                rx.text(
                    el["symbol"],
                    font_size="1.6rem",
                    font_weight="700",
                    color=ThemeState.colors["foreground"],
                    line_height="1",
                ),
                rx.text(
                    el["name"],
                    font_size="1rem",
                    color=ThemeState.colors["foreground"],
                    line_height="1",
                ),
                spacing="3",
                align="baseline",
                margin_bottom="0.25rem",
            ),
            rx.text(
                rx.fragment(
                    TranslationState.t["electron_configuration_label"],
                    " ",
                    el["electron_configuration"],
                ),
                font_family=MONO_FONT_FAMILY,
                font_size="0.8rem",
                color=BLOCK_LABEL_COLOR,
                margin_bottom="0.75rem",
            ),
            rx.vstack(
                rx.foreach(state.orbital_rows, _shell_row),
                spacing="3",
                align="stretch",
                width="100%",
            ),
            spacing="2",
            align="stretch",
            width="100%",
        ),
        placeholder,
    )
