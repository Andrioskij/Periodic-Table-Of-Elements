"""Centralized application metadata for runtime, packaging, and release docs."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

APP_DISPLAY_NAME = "Periodic Table Of Elements"
APP_EXECUTABLE_NAME = "PeriodicTableApp"
APP_VENDOR = "T_P_python"
APP_ID = "t_p_python.periodic_table_app"
APP_VERSION = "1.0.1"
APP_RELEASE_NAME = "Chemistry Tool"
OPTIONAL_ICON_PATH = PROJECT_ROOT / "assets_" / "app.ico"


def get_release_display_name():
    """Return a human-readable version string like 'v1.0.0 "Chemistry Tool"'."""
    return f'v{APP_VERSION} "{APP_RELEASE_NAME}"'


def build_window_title(base_title):
    """Append the release version to a base title for the window title bar."""
    return f"{base_title} - {get_release_display_name()}"


def get_release_slug():
    """Return a URL/filename-safe version of the release name."""
    return APP_RELEASE_NAME.lower().replace(" ", "-")


def get_release_bundle_name():
    """Return the full bundle name used for packaged release artifacts."""
    return f"{APP_EXECUTABLE_NAME}-{APP_VERSION}-{get_release_slug()}"


def get_build_metadata():
    """Collect all build-time metadata into a single dictionary for diagnostics."""
    return {
        "app_id": APP_ID,
        "display_name": APP_DISPLAY_NAME,
        "executable_name": APP_EXECUTABLE_NAME,
        "icon_present": OPTIONAL_ICON_PATH.exists(),
        "optional_icon_path": str(OPTIONAL_ICON_PATH),
        "release_bundle_name": get_release_bundle_name(),
        "release_display_name": get_release_display_name(),
        "release_name": APP_RELEASE_NAME,
        "vendor": APP_VENDOR,
        "version": APP_VERSION,
    }


__all__ = [
    "APP_DISPLAY_NAME",
    "APP_EXECUTABLE_NAME",
    "APP_ID",
    "APP_RELEASE_NAME",
    "APP_VENDOR",
    "APP_VERSION",
    "OPTIONAL_ICON_PATH",
    "PROJECT_ROOT",
    "build_window_title",
    "get_build_metadata",
    "get_release_bundle_name",
    "get_release_display_name",
    "get_release_slug",
]
