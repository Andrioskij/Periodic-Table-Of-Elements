"""Language state + selector-sync logic, extracted from MainWindow.

Owns the three operations that wrap the active UI language:

- **`load_from_settings()`**: pulls the persisted code from the
  SettingsService into the `LanguageState`.
- **`sync_selector()`**: snaps the `QComboBox` so its current entry
  matches the active language, without emitting `currentIndexChanged`
  (which would otherwise loop back into `change_to`).
- **`change_to(code)`**: persists a new language to settings and
  reports whether the value actually changed, so the caller only
  triggers a full re-apply when needed.

Does NOT own `MainWindow.apply_language()` itself: that orchestration
re-applies localized text to ~10 panels, the periodic-table widget,
trend buttons, the about dialog and the responsive layout. Mirroring
the `ThemeController.apply_theme` split, the language *protocol* (read,
persist, sync) lives here; the *fan-out* stays on MainWindow.

`MainWindow.tr()` also stays where it is: it's called ~100 times across
the file (including from `_assemble_layout`, which runs *before* the
controller is constructed because the controller needs the already-
built `language_selector` widget). Routing `tr` through the controller
would either require a chicken-and-egg construction dance or a slower
two-stage init for negligible benefit.
"""

from dataclasses import dataclass


@dataclass
class LanguageController:
    """Façade over the language combo, persisted setting, and language
    state. Created once `_assemble_layout` has built the
    `language_selector` widget."""

    language_state: object
    settings_service: object
    language_selector: object

    @property
    def current_language(self) -> str:
        """Active UI language code (e.g. ``"en"``, ``"it"``)."""
        return self.language_state.code

    def load_from_settings(self) -> None:
        """Pull the persisted language code from settings into the state.

        Falsy codes are ignored so a missing or corrupt setting falls
        back to whatever default `LanguageState` initialised with — same
        guard the underlying `language_state.code` setter applies.
        """
        code = self.settings_service.get_language()
        if code:
            self.language_state.code = code

    def sync_selector(self) -> None:
        """Snap the language selector to the active language.

        Signals are blocked around the index swap so the call doesn't
        re-trigger `change_to` (which would persist the same code we
        just read). A no-op if the combo is already on the right entry.
        """
        index = self.language_selector.findData(self.current_language)
        if index >= 0 and index != self.language_selector.currentIndex():
            self.language_selector.blockSignals(True)
            self.language_selector.setCurrentIndex(index)
            self.language_selector.blockSignals(False)

    def change_to(self, code: str) -> bool:
        """Persist a new language code into the state + settings.

        Returns ``True`` if the code was applied (non-empty AND
        different from the current one) so the caller knows whether to
        trigger a UI re-apply. Returns ``False`` for no-op cases —
        falsy input or same-as-current — without writing to settings.
        """
        if not code or code == self.current_language:
            return False
        self.language_state.code = code
        self.settings_service.set_language(code)
        return True
