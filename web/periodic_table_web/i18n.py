"""Web-side localization layer.

Loads the 7 ``data/localization/web/{code}.json`` files at import time
and exposes ``TranslationState`` — a Reflex state whose ``t`` computed
var returns the entire translation dict for the active language. Views
look up strings with ``TranslationState.t["key"]`` instead of calling
a per-key event, which keeps the per-render Var graph small.

Persistence: ``language`` is a ``rx.LocalStorage`` field so the user's
choice survives a refresh. Default is ``"en"``.

Fallback: every language's dict is merged on top of the English dict
at load time, so any missing key in a non-English file silently falls
back to its English value when the view reads ``t[key]``.
"""

from __future__ import annotations

import json
from pathlib import Path

import reflex as rx

from src.config.languages import ALL_LANGUAGE_OPTIONS

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WEB_LOCALES_DIR = _REPO_ROOT / "data" / "localization" / "web"

LANGUAGE_CODES: tuple[str, ...] = tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)
LANGUAGE_LABELS: list[str] = [label for _, label in ALL_LANGUAGE_OPTIONS]
_LABEL_TO_CODE: dict[str, str] = {label: code for code, label in ALL_LANGUAGE_OPTIONS}
_CODE_TO_LABEL: dict[str, str] = {code: label for code, label in ALL_LANGUAGE_OPTIONS}


def _load_one(code: str) -> dict[str, str]:
    path = _WEB_LOCALES_DIR / f"{code}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


_EN = _load_one("en")
TRANSLATIONS: dict[str, dict[str, str]] = {
    code: {**_EN, **_load_one(code)} if code != "en" else dict(_EN)
    for code in LANGUAGE_CODES
}


def tr(code: str, key: str) -> str:
    """Lookup ``key`` for ``code``, falling back to English silently.

    Used by call sites that need a translation outside the Reflex render
    graph (currently none, but kept symmetric with the desktop's
    ``localization_service.tr`` so future helpers can reuse it).
    """
    bundle = TRANSLATIONS.get(code) or TRANSLATIONS["en"]
    return bundle.get(key) or _EN.get(key, key)


class TranslationState(rx.State):
    """Active language + translation bundle for the current session."""

    language: str = rx.LocalStorage("en", name="ptw_language")

    @rx.event
    def set_language(self, value: str) -> None:
        # ``value`` may arrive as either a language code or a native label
        # depending on which select widget fired the event. Normalize so
        # the rest of the app only deals with codes.
        if value in TRANSLATIONS:
            self.language = value
            return
        code = _LABEL_TO_CODE.get(value)
        if code:
            self.language = code

    @rx.var(cache=True)
    def t(self) -> dict[str, str]:
        """Translation dict for the active language; views index it by key."""
        return TRANSLATIONS.get(self.language, TRANSLATIONS["en"])

    @rx.var(cache=True)
    def language_label(self) -> str:
        """Native-name label of the active language (for the selector)."""
        return _CODE_TO_LABEL.get(self.language, _CODE_TO_LABEL["en"])
