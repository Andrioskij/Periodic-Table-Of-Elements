"""Language configuration constants.

Shared by localization_service and settings_service to avoid circular imports.
"""

ALL_LANGUAGE_OPTIONS = [
    ("en", "English"),
    ("it", "Italiano"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("zh", "中文（简体）"),
    ("ru", "Русский"),
]

VISIBLE_LANGUAGE_CODES = tuple(code for code, _ in ALL_LANGUAGE_OPTIONS)

LANGUAGE_OPTIONS = [
    (code, label)
    for code, label in ALL_LANGUAGE_OPTIONS
    if code in VISIBLE_LANGUAGE_CODES
]

__all__ = [
    "ALL_LANGUAGE_OPTIONS",
    "VISIBLE_LANGUAGE_CODES",
    "LANGUAGE_OPTIONS",
]
