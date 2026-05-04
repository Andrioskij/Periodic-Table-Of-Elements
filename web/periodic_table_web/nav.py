"""Top-of-page navigation shared by ``/`` (table) and ``/tools``.

Two `rx.link` items rendered as anchor tags so Reflex's router takes
care of client-side navigation without a full page reload.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.theme import DARK_FOREGROUND, DARK_PANEL

_ACTIVE_BG = "#4e79a7"
_INACTIVE_BG = DARK_PANEL
_LABEL_COLOR = DARK_FOREGROUND

_LINKS: list[tuple[str, str, str]] = [
    ("home", "/", "Periodic Table"),
    ("tools", "/tools", "Tools"),
]


def _link(active: str, key: str, href: str, label: str) -> rx.Component:
    is_active = key == active
    return rx.link(
        label,
        href=href,
        background=_ACTIVE_BG if is_active else _INACTIVE_BG,
        color=_LABEL_COLOR,
        padding="6px 14px",
        border_radius="6px",
        font_size="0.85rem",
        font_weight="600" if is_active else "400",
        text_decoration="none",
    )


def header(active: str) -> rx.Component:
    """Render the navigation strip with one of the routes highlighted.

    ``active`` is "home" on the table page and "tools" on the tools
    page — pages pass it explicitly so this helper stays a pure
    function with no router subscription.
    """
    return rx.hstack(
        *[_link(active, key, href, label) for key, href, label in _LINKS],
        spacing="2",
        margin_bottom="1.25rem",
    )
