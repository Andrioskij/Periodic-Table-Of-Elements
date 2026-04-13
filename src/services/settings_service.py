"""Persistent user preferences backed by QSettings (INI format)."""

from PySide6.QtCore import QSettings

from src.app_metadata import APP_EXECUTABLE_NAME, APP_VENDOR
from src.config.static_data import NUMERIC_TREND_PROPERTIES
from src.services.localization_service import LANGUAGE_OPTIONS

DEFAULT_LANGUAGE = "en"
DEFAULT_RIGHT_PANEL_MODE = "info"
DEFAULT_TREND_MODE = "normal"
DEFAULT_WINDOW_STATE = "normal"

VALID_RIGHT_PANEL_MODES = {"info", "diagram", "compound", "lewis"}
VALID_TOOL_AREA_MODES = {"compounds", "molar", "stoichiometry", "solubility"}
VALID_TREND_MODES = set(list(NUMERIC_TREND_PROPERTIES.keys()) + ["normal", "macroclass", "metallic", "nonmetallic"])
VALID_LANGUAGES = {code for code, _ in LANGUAGE_OPTIONS}
VALID_WINDOW_STATES = {"normal", "maximized"}


class SettingsService:
    """Read and write user preferences to a platform-appropriate INI file.

    Wraps QSettings to provide validated getters and setters for every
    preference the application supports (language, panel mode, trend
    mode, window geometry and state).
    """

    def __init__(self, qsettings=None, ini_file_path=None):
        """Initialize the settings back-end.

        Accepts an existing QSettings instance for testing, a custom
        INI file path, or falls back to the standard user-scope location.
        """
        if qsettings is not None:
            self.settings = qsettings
        elif ini_file_path:
            self.settings = QSettings(ini_file_path, QSettings.IniFormat)
        else:
            self.settings = QSettings(
                QSettings.IniFormat,
                QSettings.UserScope,
                APP_VENDOR,
                APP_EXECUTABLE_NAME,
            )

    def _clean_string(self, value):
        """Coerce a QSettings value to a plain Python string.

        QSettings may return bytes on some platforms; this helper
        decodes them safely and always returns str or None.
        """
        if value is None:
            return None
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                value = str(value)
        return str(value)

    def get_language(self):
        """Return the stored UI language code, defaulting to English."""
        raw = self.settings.value("language", DEFAULT_LANGUAGE)
        value = self._clean_string(raw)
        return value if value in VALID_LANGUAGES else DEFAULT_LANGUAGE

    def set_language(self, language_code):
        """Persist a new UI language choice after validation."""
        language_code = self._clean_string(language_code)
        if language_code not in VALID_LANGUAGES:
            return
        self.settings.setValue("language", language_code)
        self.settings.sync()

    def get_right_panel_mode(self):
        """Return which right-side panel is active (info, diagram, or compound)."""
        raw = self.settings.value("right_panel_mode", DEFAULT_RIGHT_PANEL_MODE)
        value = self._clean_string(raw)
        return value if value in VALID_RIGHT_PANEL_MODES else DEFAULT_RIGHT_PANEL_MODE

    def set_right_panel_mode(self, mode):
        """Persist the active right-panel mode after validation."""
        mode = self._clean_string(mode)
        if mode not in VALID_RIGHT_PANEL_MODES:
            return
        self.settings.setValue("right_panel_mode", mode)
        self.settings.sync()

    def get_trend_mode(self):
        """Return the current trend-overlay visualization mode."""
        raw = self.settings.value("trend_mode", DEFAULT_TREND_MODE)
        value = self._clean_string(raw)
        return value if value in VALID_TREND_MODES else DEFAULT_TREND_MODE

    def set_trend_mode(self, mode):
        """Persist a new trend-overlay mode after validation."""
        mode = self._clean_string(mode)
        if mode not in VALID_TREND_MODES:
            return
        self.settings.setValue("trend_mode", mode)
        self.settings.sync()

    def get_window_geometry(self):
        """Retrieve the saved window position and size.

        Returns a dict with x, y, width, height keys, or None when
        the stored values are incomplete or invalid (non-positive size).
        """
        x = self._clean_int(self.settings.value("window_x", None))
        y = self._clean_int(self.settings.value("window_y", None))
        width = self._clean_int(self.settings.value("window_width", None))
        height = self._clean_int(self.settings.value("window_height", None))

        if None in {x, y, width, height}:
            return None

        if width <= 0 or height <= 0:
            return None

        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }

    def set_window_geometry(self, geometry):
        """Persist the current window position and size.

        Silently ignores the call if geometry is not a valid dict
        or any coordinate cannot be parsed to an integer.
        """
        if not isinstance(geometry, dict):
            return

        x = self._clean_int(geometry.get("x"))
        y = self._clean_int(geometry.get("y"))
        width = self._clean_int(geometry.get("width"))
        height = self._clean_int(geometry.get("height"))

        if None in {x, y, width, height}:
            return

        self.settings.setValue("window_x", x)
        self.settings.setValue("window_y", y)
        self.settings.setValue("window_width", width)
        self.settings.setValue("window_height", height)
        self.settings.sync()

    def get_window_state(self):
        """Return the saved window state ('normal' or 'maximized')."""
        raw = self.settings.value("window_state", DEFAULT_WINDOW_STATE)
        value = self._clean_string(raw)
        return value if value in VALID_WINDOW_STATES else DEFAULT_WINDOW_STATE

    def set_window_state(self, state):
        """Persist the current window state after validation."""
        state = self._clean_string(state)
        if state not in VALID_WINDOW_STATES:
            return
        self.settings.setValue("window_state", state)
        self.settings.sync()

    def _clean_int(self, value):
        """Safely coerce a QSettings value to int, returning None on failure."""
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def clear(self):
        """Remove all stored preferences and flush to disk."""
        self.settings.clear()
        self.settings.sync()
