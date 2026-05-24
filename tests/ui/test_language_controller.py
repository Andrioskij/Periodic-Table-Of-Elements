"""Unit tests for LanguageController.

Pure-Python tests using fakes for `SettingsService`, `LanguageState`,
and the `QComboBox` interface the controller needs (`findData`,
`currentIndex`, `setCurrentIndex`, `blockSignals`). Exercises:

- ``load_from_settings``: pulls + ignores falsy
- ``sync_selector``: snaps the combo without re-emitting signals
- ``change_to``: persists only when the value actually changed
"""

import unittest

from src.ui.controllers.language_controller import LanguageController


class _FakeState:
    def __init__(self, code="en"):
        self.code = code


class _FakeSettings:
    def __init__(self, language="en"):
        self._language = language
        self.set_calls = []

    def get_language(self):
        return self._language

    def set_language(self, code):
        self._language = code
        self.set_calls.append(code)


class _FakeSelector:
    """Mimics the QComboBox surface the controller touches."""

    def __init__(self, entries, current_index=0):
        # entries: list of (label, data) tuples
        self._entries = list(entries)
        self._index = current_index
        self.signals_blocked = False
        self.block_history = []

    def findData(self, data):
        for i, (_label, entry_data) in enumerate(self._entries):
            if entry_data == data:
                return i
        return -1

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        self._index = index

    def blockSignals(self, value):
        self.signals_blocked = value
        self.block_history.append(value)


def _make_controller(*, state_code="en", settings_lang="it",
                     entries=None, current_index=0):
    entries = entries or [("English", "en"), ("Italiano", "it"), ("Espanol", "es")]
    return LanguageController(
        language_state=_FakeState(state_code),
        settings_service=_FakeSettings(settings_lang),
        language_selector=_FakeSelector(entries, current_index),
    )


class TestLoadFromSettings(unittest.TestCase):
    def test_persisted_language_overrides_state_default(self):
        controller = _make_controller(state_code="en", settings_lang="it")
        controller.load_from_settings()
        self.assertEqual(controller.current_language, "it")

    def test_empty_persisted_language_is_ignored(self):
        controller = _make_controller(state_code="en", settings_lang="")
        controller.load_from_settings()
        # Falsy code must NOT overwrite the existing state — the user's
        # earlier choice (or LanguageState default) wins.
        self.assertEqual(controller.current_language, "en")

    def test_none_persisted_language_is_ignored(self):
        controller = _make_controller(state_code="en", settings_lang=None)
        controller.load_from_settings()
        self.assertEqual(controller.current_language, "en")


class TestSyncSelector(unittest.TestCase):
    def test_sync_snaps_combo_to_current_language(self):
        controller = _make_controller(state_code="it", current_index=0)
        controller.sync_selector()
        self.assertEqual(controller.language_selector.currentIndex(), 1)

    def test_sync_blocks_signals_around_index_swap(self):
        controller = _make_controller(state_code="it", current_index=0)
        controller.sync_selector()
        # The combo's block_history must contain a True THEN a False —
        # the controller must NOT leave the selector in a permanent
        # signal-blocked state.
        self.assertEqual(
            controller.language_selector.block_history, [True, False],
        )

    def test_sync_noop_when_combo_already_on_current_language(self):
        controller = _make_controller(state_code="en", current_index=0)
        controller.sync_selector()
        # No signal-block calls when there's nothing to do.
        self.assertEqual(controller.language_selector.block_history, [])

    def test_sync_handles_unknown_language_gracefully(self):
        controller = _make_controller(state_code="zh", current_index=0)
        # No "zh" entry in the default selector; findData returns -1
        # and the method must just no-op.
        controller.sync_selector()
        self.assertEqual(controller.language_selector.currentIndex(), 0)
        self.assertEqual(controller.language_selector.block_history, [])


class TestChangeTo(unittest.TestCase):
    def test_change_to_new_code_persists_and_returns_true(self):
        controller = _make_controller(state_code="en", settings_lang="en")
        changed = controller.change_to("it")
        self.assertTrue(changed)
        self.assertEqual(controller.current_language, "it")
        self.assertEqual(controller.settings_service.set_calls, ["it"])

    def test_change_to_same_code_is_noop(self):
        controller = _make_controller(state_code="en", settings_lang="en")
        changed = controller.change_to("en")
        self.assertFalse(changed)
        self.assertEqual(controller.settings_service.set_calls, [])

    def test_change_to_empty_string_is_noop(self):
        controller = _make_controller(state_code="en", settings_lang="en")
        changed = controller.change_to("")
        self.assertFalse(changed)
        self.assertEqual(controller.settings_service.set_calls, [])

    def test_change_to_none_is_noop(self):
        controller = _make_controller(state_code="en", settings_lang="en")
        changed = controller.change_to(None)
        self.assertFalse(changed)
        self.assertEqual(controller.settings_service.set_calls, [])


if __name__ == "__main__":
    unittest.main()
