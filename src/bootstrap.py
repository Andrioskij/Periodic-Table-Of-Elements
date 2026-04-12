"""Minimal application bootstrap helpers shared by the public entry points."""

import logging
import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.app_metadata import (
    APP_DISPLAY_NAME,
    APP_EXECUTABLE_NAME,
    APP_ID,
    OPTIONAL_ICON_PATH,
    APP_VENDOR,
    APP_VERSION,
)
from src.error_handling import (
    STARTUP_ERROR_MESSAGE,
    configure_logging,
    install_exception_hooks,
    report_fatal_exception,
)
from src.services.data_loader import load_elements, load_nomenclature_data
from src.ui.main_window import MainWindow

STARTUP_SMOKE_EXIT_MS_ENV_VAR = "PERIODIC_TABLE_SMOKE_EXIT_MS"


def configure_application_metadata(app):
    """Apply display name, version, vendor, and icon to the QApplication instance."""
    app.setApplicationName(APP_EXECUTABLE_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_VENDOR)
    if OPTIONAL_ICON_PATH.exists():
        app_icon = QIcon(str(OPTIONAL_ICON_PATH))
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
    if hasattr(app, "setDesktopFileName"):
        app.setDesktopFileName(APP_ID)
    return app


def create_application(argv=None):
    """Create or reuse the QApplication singleton with full metadata applied."""
    existing_app = QApplication.instance()
    if existing_app is not None:
        return configure_application_metadata(existing_app)

    return configure_application_metadata(QApplication(sys.argv if argv is None else argv))


def load_application_data():
    """Load the elements dataset and nomenclature reference data from disk."""
    return load_elements(), load_nomenclature_data()


def create_main_window(elements=None, nomenclature_data=None):
    """Instantiate the MainWindow, loading data from disk if not provided."""
    if elements is None or nomenclature_data is None:
        loaded_elements, loaded_nomenclature_data = load_application_data()
        if elements is None:
            elements = loaded_elements
        if nomenclature_data is None:
            nomenclature_data = loaded_nomenclature_data

    return MainWindow(elements, nomenclature_data)


def get_startup_smoke_exit_delay_ms():
    """Read the optional smoke-test exit delay from the environment.

    Returns None when the variable is unset, allowing normal startup.
    Used by CI to verify the app launches without hanging.
    """
    configured_value = os.environ.get(STARTUP_SMOKE_EXIT_MS_ENV_VAR)
    if configured_value is None:
        return None

    configured_value = configured_value.strip()
    if not configured_value:
        return None

    try:
        exit_delay_ms = int(configured_value)
    except ValueError as exc:
        raise ValueError(
            f"{STARTUP_SMOKE_EXIT_MS_ENV_VAR} must be an integer number of milliseconds."
        ) from exc

    if exit_delay_ms < 0:
        raise ValueError(f"{STARTUP_SMOKE_EXIT_MS_ENV_VAR} must be greater than or equal to zero.")

    return exit_delay_ms


def install_startup_smoke_exit_timer(app):
    """Arm a one-shot timer that quits the app after the smoke-test delay, if configured."""
    exit_delay_ms = get_startup_smoke_exit_delay_ms()
    if exit_delay_ms is None:
        return None

    QTimer.singleShot(exit_delay_ms, app.quit)
    logging.getLogger(__name__).info(
        "Startup smoke exit timer armed for %s ms via %s.",
        exit_delay_ms,
        STARTUP_SMOKE_EXIT_MS_ENV_VAR,
    )
    return exit_delay_ms


def run(argv=None):
    """Full application lifecycle: configure logging, create the window, and run the event loop.

    Returns the Qt exit code (0 on success). Fatal exceptions are
    logged and shown in a dialog before returning 1.
    """
    log_path = configure_logging()
    install_exception_hooks(log_path)
    logger = logging.getLogger(__name__)
    logger.info("Starting %s %s", APP_EXECUTABLE_NAME, APP_VERSION)

    try:
        app = create_application(argv)
        window = create_main_window()
        window.show()
        install_startup_smoke_exit_timer(app)
        exit_code = app.exec()
        logger.info("Application exited with code %s", exit_code)
        return exit_code
    except Exception as exc:
        report_fatal_exception(
            exc,
            exc_info=(type(exc), exc, exc.__traceback__),
            user_message=STARTUP_ERROR_MESSAGE,
            log_path=log_path,
        )
        return 1


__all__ = [
    "MainWindow",
    "QApplication",
    "configure_application_metadata",
    "create_application",
    "create_main_window",
    "get_startup_smoke_exit_delay_ms",
    "install_startup_smoke_exit_timer",
    "load_application_data",
    "run",
    "STARTUP_SMOKE_EXIT_MS_ENV_VAR",
]
