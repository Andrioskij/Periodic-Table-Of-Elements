"""Theme state + presentation logic, extracted from MainWindow.

Owns the active theme name (`"dark"` or `"light"`), the toggle math
that flips between them, the persist-via-SettingsService side effect,
and the two presentation helpers that compute the theme toggle
button's icon character and tooltip.

Does NOT own `apply_theme()` itself — that orchestration (setStyleSheet,
panel notifications, periodic-table refresh) stays on MainWindow because
it touches many sibling widgets. The controller exposes a small,
testable surface; MainWindow consumes it.
"""

from dataclasses import dataclass
from types import MappingProxyType

VALID_THEMES = ("dark", "light")
_BUTTON_ICONS = MappingProxyType({"dark": "☼", "light": "☽"})


@dataclass
class ThemeController:
    """Owns the active theme name and the toggle + button-presentation logic."""

    current_theme: str
    settings_service: object

    def toggle_and_persist(self) -> str:
        """Flip dark <-> light, persist via the settings service, return the new theme."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.settings_service.set_theme(self.current_theme)
        return self.current_theme

    def button_text(self) -> str:
        """Return the single-character icon shown on the theme toggle button."""
        return _BUTTON_ICONS[self.current_theme]

    def button_tooltip(self) -> str:
        """Return the tooltip describing what toggling does from the current theme."""
        target = "light" if self.current_theme == "dark" else "dark"
        return f"Switch to {target} theme"
