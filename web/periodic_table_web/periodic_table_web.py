"""Reflex entry point for the browser version of the periodic table."""

import reflex as rx

from periodic_table_web.electron_view import electron_view
from periodic_table_web.i18n import TranslationState
from periodic_table_web.lewis_view import lewis_view
from periodic_table_web.nav import header as nav_header
from periodic_table_web.state import TableState
from periodic_table_web.theme import DARK_LABEL_MUTED
from periodic_table_web.theme_state import ThemeState
from periodic_table_web.tools import tools_page
from src.services.data_loader import load_elements

ELEMENTS = load_elements()
GRID_GAP_ROW = 8
TREND_BUTTONS: list[tuple[str, str]] = [
    ("category", "trend_default"),
    ("radius", "trend_radius"),
    ("ionization", "trend_ionization"),
    ("electron_affinity", "trend_electron_affinity"),
    ("electronegativity", "trend_electronegativity"),
    ("metallic", "trend_metallic"),
    ("nonmetallic", "trend_nonmetallic"),
]
RIGHT_PANEL_TABS: list[tuple[str, str]] = [
    ("info", "tab_info"),
    ("electron", "tab_electron_config"),
    ("lewis", "tab_lewis"),
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
            "2px solid " + ThemeState.colors["selection_border"],
            "1px solid " + ThemeState.colors["border"],
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
            placeholder=TranslationState.t["home_search_placeholder"],
            value=TableState.search_query,
            on_change=TableState.set_search,
            background=ThemeState.colors["input_bg"],
            color=ThemeState.colors["foreground"],
            border="1px solid " + ThemeState.colors["border"],
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
                color=ThemeState.colors["foreground"],
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


def _trend_button(mode: str, t_key: str) -> rx.Component:
    is_active = TableState.trend_mode == mode
    return rx.button(
        TranslationState.t[t_key],
        on_click=TableState.set_trend(mode),
        background=rx.cond(
            is_active,
            ThemeState.colors["accent_active"],
            ThemeState.colors["accent_inactive"],
        ),
        color=ThemeState.colors["foreground"],
        border="1px solid " + ThemeState.colors["border"],
        border_radius="6px",
        padding="4px 12px",
        cursor="pointer",
        font_size="0.8rem",
        font_weight=rx.cond(is_active, "600", "400"),
    )


def _trend_buttons() -> rx.Component:
    return rx.hstack(
        *[_trend_button(mode, t_key) for mode, t_key in TREND_BUTTONS],
        spacing="2",
        flex_wrap="wrap",
        margin_bottom="1rem",
    )


def _info_row(label, value) -> rx.Component:
    return rx.hstack(
        rx.text(
            label,
            color=ThemeState.colors["text_muted"],
            font_size="0.78rem",
            min_width="120px",
        ),
        rx.text(
            value,
            color=ThemeState.colors["foreground"],
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
                color=ThemeState.colors["foreground"],
            ),
            rx.vstack(
                rx.text(
                    el["atomic_number"],
                    color=ThemeState.colors["text_muted"],
                    font_size="0.85rem",
                    line_height="1",
                ),
                rx.text(
                    el["name"],
                    font_size="1.4rem",
                    font_weight="600",
                    color=ThemeState.colors["foreground"],
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
        _info_row(TranslationState.t["info_atomic_mass"], rx.fragment(el["atomic_mass"], " u")),
        _info_row(TranslationState.t["info_category"], el["category"]),
        _info_row(TranslationState.t["info_period"], el["period"]),
        _info_row(TranslationState.t["info_group"], _opt(el["group"])),
        _info_row(TranslationState.t["info_standard_state"], _opt(el["standard_state"])),
        _info_row(
            TranslationState.t["info_electron_config"],
            rx.text(
                el["electron_configuration"],
                font_family="'Cascadia Code', 'Consolas', monospace",
                font_size="0.8rem",
                color=ThemeState.colors["foreground"],
            ),
        ),
        _info_row(TranslationState.t["info_electronegativity"], _opt(el["electronegativity"])),
        _info_row(TranslationState.t["info_atomic_radius"], _opt(el["atomic_radius"], " pm")),
        _info_row(TranslationState.t["info_ionization_energy"], _opt(el["ionization_energy"], " eV")),
        _info_row(TranslationState.t["info_electron_affinity"], _opt(el["electron_affinity"], " eV")),
        _info_row(TranslationState.t["info_oxidation_states"], _opt(el["oxidation_states"])),
        _info_row(TranslationState.t["info_melting_point"], _opt(el["melting_point"], " K")),
        _info_row(TranslationState.t["info_boiling_point"], _opt(el["boiling_point"], " K")),
        _info_row(TranslationState.t["info_density"], _opt(el["density"], " g/cm³")),
        _info_row(TranslationState.t["info_discovered"], _opt(el["year_discovered"])),
        spacing="2",
        align="stretch",
        width="100%",
    )


def _info_placeholder() -> rx.Component:
    return rx.center(
        rx.text(
            TranslationState.t["home_select_prompt"],
            color=ThemeState.colors["text_muted"],
            font_size="0.9rem",
            text_align="center",
        ),
        height="100%",
        min_height="180px",
    )


def _info_tab_content() -> rx.Component:
    return rx.cond(
        TableState.has_selection,
        _info_card_content(),
        _info_placeholder(),
    )


def _tab_button(view: str, t_key: str) -> rx.Component:
    is_active = TableState.right_panel_view == view
    return rx.button(
        TranslationState.t[t_key],
        on_click=TableState.set_right_panel(view),
        background=rx.cond(
            is_active,
            ThemeState.colors["accent_active"],
            ThemeState.colors["accent_inactive"],
        ),
        color=ThemeState.colors["foreground"],
        border="none",
        border_radius="6px",
        padding="6px 10px",
        cursor="pointer",
        font_size="0.78rem",
        font_weight=rx.cond(is_active, "600", "400"),
        flex_grow="1",
    )


def _tab_bar() -> rx.Component:
    return rx.hstack(
        *[_tab_button(view, t_key) for view, t_key in RIGHT_PANEL_TABS],
        spacing="1",
        width="100%",
        margin_bottom="0.75rem",
    )


def _info_card() -> rx.Component:
    return rx.box(
        _tab_bar(),
        rx.match(
            TableState.right_panel_view,
            ("info", _info_tab_content()),
            ("electron", electron_view(TableState, _info_placeholder())),
            ("lewis", lewis_view(TableState, _info_placeholder())),
            _info_tab_content(),
        ),
        background=ThemeState.colors["panel"],
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
            nav_header("home"),
            rx.heading(
                TranslationState.t["home_heading"],
                size="6",
                color=ThemeState.colors["foreground"],
                margin_bottom="0.25rem",
            ),
            rx.text(
                TranslationState.t["home_subtitle"],
                font_size="0.85rem",
                color=ThemeState.colors["text_muted"],
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
        background=ThemeState.colors["background"],
        min_height="100vh",
        padding="1.5rem 1rem 2rem",
        color=ThemeState.colors["foreground"],
        font_family="'Segoe UI', system-ui, -apple-system, sans-serif",
    )


# Reflex 0.9.1's ``rx.theme(appearance=...)`` is read at app build time,
# not per-render — switching it dynamically would require a full reload.
# Keeping ``appearance="inherit"`` lets the Radix primitives follow the
# host CSS, while the visible colours (page bg, foreground, panel,
# accent) are driven entirely by ``ThemeState.colors`` on every box.
app = rx.App(
    theme=rx.theme(appearance="inherit", accent_color="iris"),
)
app.add_page(index, title="Periodic Table")
app.add_page(tools_page, route="/tools", title="Tools — Periodic Table")
