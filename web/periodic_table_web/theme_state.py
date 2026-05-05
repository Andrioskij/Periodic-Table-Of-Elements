"""Reflex state for the active visual theme.

Mirrors :class:`TranslationState` in spirit — a single ``rx.LocalStorage``
field for cross-session persistence, plus a ``colors`` computed var that
returns the entire palette dict for the active theme. Views index it as
``ThemeState.colors["background"]`` so the page restyles instantly when
the user toggles dark/light.

A separate module (rather than ``state.py`` or ``theme.py``) keeps
``state.py`` focused on table state and ``theme.py`` purely declarative,
and avoids the circular import that would otherwise appear because
electron_view / lewis_view both import the palette and are themselves
imported from state.py.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.theme import DARK_PALETTE, palette

VALID_THEMES: frozenset[str] = frozenset({"dark", "light"})


class ThemeState(rx.State):
    """Active dark/light theme + the palette dict that follows it."""

    theme: str = rx.LocalStorage("dark", name="ptw_theme")

    @rx.event
    def set_theme(self, value: str) -> None:
        if value in VALID_THEMES:
            self.theme = value

    @rx.event
    def toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"

    @rx.var(cache=True)
    def colors(self) -> dict[str, str]:
        """Palette dict for the active theme; views index by key."""
        return palette(self.theme) if self.theme in VALID_THEMES else DARK_PALETTE

    @rx.var(cache=True)
    def is_dark(self) -> bool:
        return self.theme == "dark"
