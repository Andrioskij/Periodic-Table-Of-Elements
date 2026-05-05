"""Lewis dot diagram view for the right panel (Lewis tab).

Reuses ``src.domain.lewis_diagram`` for main-group elements and
falls back to an outer s+p shell count for transition metals so the
view still shows *something* useful for d-block selections (the
desktop app shows "not applicable" — the browser is friendlier).

Single atoms only — multi-atom molecules are out of scope for this
batch and are tracked for a later iteration.
"""

from __future__ import annotations

import reflex as rx
from pydantic import BaseModel, Field

from periodic_table_web.i18n import TranslationState
from periodic_table_web.theme_state import ThemeState
from src.domain.electron_configuration import configuration_to_map
from src.domain.lewis_diagram import distribute_dots, get_valence_electrons

# Dot colour stays fixed: yellow reads against both panel backgrounds.
DOT_COLOR = "#f5d442"

SVG_SIZE = 200
CENTER = SVG_SIZE / 2
DOT_RADIUS = 5
SYMBOL_HALF_WIDTH = 28
SYMBOL_HALF_HEIGHT = 22
DOT_OFFSET = 16
PAIR_GAP = 12


def _outer_sp_electrons(config_text: str | None) -> int:
    """Sum of s and p electrons in the highest occupied shell.

    Used as a Lewis-style approximation for transition metals where
    the standard group-based formula does not apply.
    """
    if not config_text:
        return 0
    occupancy = configuration_to_map(config_text)
    if not occupancy:
        return 0
    sp_levels = [
        int(key[0]) for key in occupancy if key[1] in ("s", "p")
    ]
    if not sp_levels:
        return 0
    outer = max(sp_levels)
    return occupancy.get(f"{outer}s", 0) + occupancy.get(f"{outer}p", 0)


class LewisDots(BaseModel):
    """Per-side dot counts (0/1/2) around the element symbol."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0


class LewisData(BaseModel):
    """Everything the Lewis component renders for one selected element."""

    valence: int = 0
    dots: LewisDots = Field(default_factory=LewisDots)
    lone_pairs: int = 0
    unpaired: int = 0
    is_extended: bool = False
    applicable: bool = False


def compute_lewis_data(element: dict) -> LewisData:
    """Return the data the Lewis component needs for one element.

    Falls back to outer s+p electron count for transition metals and
    flags ``is_extended`` so the view can show a clarifying note.
    Returns a zeroed model when the element has no usable
    configuration.
    """
    if not element:
        return LewisData()

    valence = get_valence_electrons(element)
    is_extended = False
    if valence is None:
        valence = _outer_sp_electrons(element.get("electron_configuration"))
        is_extended = True

    dots_map = distribute_dots(valence)
    lone_pairs = sum(1 for v in dots_map.values() if v == 2)
    unpaired = sum(1 for v in dots_map.values() if v == 1)
    return LewisData(
        valence=valence,
        dots=LewisDots(**dots_map),
        lone_pairs=lone_pairs,
        unpaired=unpaired,
        is_extended=is_extended,
        applicable=valence > 0,
    )


def _dot(cx: float, cy: float) -> rx.Component:
    return rx.el.circle(
        cx=str(cx),
        cy=str(cy),
        r=str(DOT_RADIUS),
        fill=DOT_COLOR,
    )


def _lewis_svg(state) -> rx.Component:
    el = state.selected_element
    dots = state.lewis_data.dots

    top_y = CENTER - SYMBOL_HALF_HEIGHT - DOT_OFFSET
    bottom_y = CENTER + SYMBOL_HALF_HEIGHT + DOT_OFFSET
    left_x = CENTER - SYMBOL_HALF_WIDTH - DOT_OFFSET
    right_x = CENTER + SYMBOL_HALF_WIDTH + DOT_OFFSET

    top = rx.cond(
        dots.top == 1,
        _dot(CENTER, top_y),
        rx.cond(
            dots.top == 2,
            rx.fragment(
                _dot(CENTER - PAIR_GAP / 2, top_y),
                _dot(CENTER + PAIR_GAP / 2, top_y),
            ),
            rx.fragment(),
        ),
    )
    bottom = rx.cond(
        dots.bottom == 1,
        _dot(CENTER, bottom_y),
        rx.cond(
            dots.bottom == 2,
            rx.fragment(
                _dot(CENTER - PAIR_GAP / 2, bottom_y),
                _dot(CENTER + PAIR_GAP / 2, bottom_y),
            ),
            rx.fragment(),
        ),
    )
    left = rx.cond(
        dots.left == 1,
        _dot(left_x, CENTER),
        rx.cond(
            dots.left == 2,
            rx.fragment(
                _dot(left_x, CENTER - PAIR_GAP / 2),
                _dot(left_x, CENTER + PAIR_GAP / 2),
            ),
            rx.fragment(),
        ),
    )
    right = rx.cond(
        dots.right == 1,
        _dot(right_x, CENTER),
        rx.cond(
            dots.right == 2,
            rx.fragment(
                _dot(right_x, CENTER - PAIR_GAP / 2),
                _dot(right_x, CENTER + PAIR_GAP / 2),
            ),
            rx.fragment(),
        ),
    )

    return rx.el.svg(
        rx.el.text(
            el["symbol"],
            x=str(CENTER),
            y=str(CENTER),
            text_anchor="middle",
            dominant_baseline="central",
            font_size="36",
            font_weight="700",
            fill=ThemeState.colors["foreground"],
            font_family="'Segoe UI', system-ui, sans-serif",
        ),
        top,
        bottom,
        left,
        right,
        width=str(SVG_SIZE),
        height=str(SVG_SIZE),
        view_box=f"0 0 {SVG_SIZE} {SVG_SIZE}",
        style={"display": "block", "margin": "0 auto"},
    )


def _info_row(label, value) -> rx.Component:
    return rx.hstack(
        rx.text(label, color=ThemeState.colors["text_muted"], font_size="0.78rem"),
        rx.text(value, color=ThemeState.colors["foreground"], font_size="0.85rem"),
        justify="between",
        width="100%",
    )


def lewis_view(state, placeholder) -> rx.Component:
    """Right-panel content for the Lewis tab.

    ``state`` is TableState; ``placeholder`` is the shared "select an
    element" widget reused across all three tabs.
    """
    el = state.selected_element
    data = state.lewis_data
    return rx.cond(
        state.has_selection,
        rx.cond(
            data.applicable,
            rx.vstack(
                rx.text(
                    el["name"],
                    font_size="1rem",
                    font_weight="600",
                    color=ThemeState.colors["foreground"],
                    margin_bottom="0.25rem",
                ),
                _lewis_svg(state),
                rx.vstack(
                    _info_row(TranslationState.t["lewis_valence_electrons"], data.valence),
                    _info_row(TranslationState.t["lewis_lone_pairs"], data.lone_pairs),
                    _info_row(TranslationState.t["lewis_bonding"], data.unpaired),
                    spacing="1",
                    width="100%",
                    margin_top="0.5rem",
                ),
                rx.cond(
                    data.is_extended,
                    rx.text(
                        TranslationState.t["lewis_extended_octet_note"],
                        font_size="0.75rem",
                        color=ThemeState.colors["text_muted"],
                        font_style="italic",
                        margin_top="0.5rem",
                    ),
                ),
                spacing="2",
                align="stretch",
                width="100%",
            ),
            rx.center(
                rx.text(
                    TranslationState.t["lewis_not_applicable"],
                    color=ThemeState.colors["text_muted"],
                    font_size="0.85rem",
                    text_align="center",
                ),
                height="100%",
                min_height="180px",
            ),
        ),
        placeholder,
    )
