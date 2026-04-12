"""Minimal fatal-error handling and local diagnostic logging for the desktop app."""

import logging
import os
import sys
import tempfile
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from src.app_metadata import (
    APP_DISPLAY_NAME,
    APP_EXECUTABLE_NAME,
    APP_VENDOR,
    APP_VERSION,
    OPTIONAL_ICON_PATH,
)


LOG_FILE_NAME = f"{APP_EXECUTABLE_NAME}.log"
LOG_DIR_NAME = "logs"
LOG_MAX_BYTES = 512 * 1024
LOG_BACKUP_COUNT = 3
LOG_ROOT_ENV_VAR = "PERIODIC_TABLE_LOG_ROOT"
STARTUP_ERROR_MESSAGE = (
    f"{APP_DISPLAY_NAME} could not start because an unexpected problem occurred."
)
RUNTIME_ERROR_MESSAGE = (
    f"{APP_DISPLAY_NAME} encountered an unexpected problem and needs to close."
)
_APP_HANDLER_FLAG = "_periodic_table_app_file_handler"


def get_log_directory(root_dir=None):
    """Resolve the directory where application log files should be stored.

    Tries, in order: the explicit root_dir, the LOG_ROOT_ENV_VAR
    environment variable, LOCALAPPDATA, QStandardPaths, and finally
    falls back to ~/.local/share.
    """
    selected_root = root_dir or os.environ.get(LOG_ROOT_ENV_VAR)
    if selected_root is not None:
        return Path(selected_root) / APP_VENDOR / APP_EXECUTABLE_NAME / LOG_DIR_NAME

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_VENDOR / APP_EXECUTABLE_NAME / LOG_DIR_NAME

    location_type = getattr(QStandardPaths, "AppLocalDataLocation", QStandardPaths.AppDataLocation)
    standard_path = QStandardPaths.writableLocation(location_type)
    if standard_path:
        return Path(standard_path) / LOG_DIR_NAME

    return Path.home() / ".local" / "share" / APP_VENDOR / APP_EXECUTABLE_NAME / LOG_DIR_NAME


def get_log_file_path(root_dir=None):
    """Return the full path to the application log file."""
    return get_log_directory(root_dir) / LOG_FILE_NAME


def _get_log_file_candidates(log_path=None):
    if log_path is not None:
        return [Path(log_path)]

    candidates = [get_log_file_path()]
    temp_candidate = get_log_file_path(tempfile.gettempdir())
    cwd_candidate = get_log_file_path(Path.cwd() / ".runtime")

    for candidate in (temp_candidate, cwd_candidate):
        if candidate not in candidates:
            candidates.append(candidate)

    return candidates


def _iter_app_file_handlers():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if getattr(handler, _APP_HANDLER_FLAG, False):
            yield handler


def reset_logging_configuration():
    """Remove all application file handlers from the root logger. Used in tests."""
    root_logger = logging.getLogger()
    for handler in list(_iter_app_file_handlers()):
        root_logger.removeHandler(handler)
        handler.close()


def configure_logging(log_path=None):
    """Set up rotating-file logging, trying multiple candidate paths.

    Returns the resolved path of the active log file on success.
    Raises OSError if no candidate path is writable.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    attempted_paths = []

    for candidate_path in _get_log_file_candidates(log_path):
        try:
            candidate_path.parent.mkdir(parents=True, exist_ok=True)
            resolved_target = candidate_path.resolve()

            for handler in list(_iter_app_file_handlers()):
                try:
                    current_path = Path(handler.baseFilename).resolve()
                except (AttributeError, OSError):
                    current_path = None

                if current_path == resolved_target:
                    return resolved_target

                root_logger.removeHandler(handler)
                handler.close()

            file_handler = RotatingFileHandler(
                resolved_target,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding="utf-8",
            )
            setattr(file_handler, _APP_HANDLER_FLAG, True)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
            )
            root_logger.addHandler(file_handler)
            logging.captureWarnings(True)
            logging.getLogger(__name__).info(
                "Logging initialized for %s %s at %s",
                APP_EXECUTABLE_NAME,
                APP_VERSION,
                resolved_target,
            )
            return resolved_target
        except OSError:
            attempted_paths.append(candidate_path)

    attempted_text = ", ".join(str(path) for path in attempted_paths)
    raise OSError(f"Unable to configure application logging. Attempted paths: {attempted_text}")


def build_exception_summary(exc_value):
    """Extract a short summary string from an exception for display in the error dialog."""
    message = str(exc_value).strip()
    if not message:
        return None

    if len(message) > 280:
        return message[:277] + "..."
    return message


def _ensure_message_box_application():
    app = QApplication.instance()
    created_app = False

    if app is None:
        app = QApplication([APP_EXECUTABLE_NAME])
        app.setApplicationName(APP_EXECUTABLE_NAME)
        app.setApplicationDisplayName(APP_DISPLAY_NAME)
        app.setOrganizationName(APP_VENDOR)
        created_app = True

        if OPTIONAL_ICON_PATH.exists():
            app_icon = QIcon(str(OPTIONAL_ICON_PATH))
            if not app_icon.isNull():
                app.setWindowIcon(app_icon)

    return app, created_app


def show_fatal_error_dialog(user_message, log_path, detail_message=None):
    """Display a blocking critical-error dialog with the log file path.

    Creates a temporary QApplication if one doesn't already exist,
    so the dialog can appear even during early startup failures.
    """
    try:
        app, created_app = _ensure_message_box_application()
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Critical)
        message_box.setWindowTitle(APP_DISPLAY_NAME)
        if app is not None and not app.windowIcon().isNull():
            message_box.setWindowIcon(app.windowIcon())
        message_box.setText(user_message)

        info_lines = []
        if detail_message:
            info_lines.append(detail_message)
        info_lines.append(f"A diagnostic log was saved to:\n{log_path}")
        info_lines.append("Please share this file if the problem keeps happening.")
        message_box.setInformativeText("\n\n".join(info_lines))
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec()

        if created_app:
            app.quit()
    except Exception:
        logging.getLogger(__name__).exception("Unable to display the fatal error dialog.")


def report_fatal_exception(
    exc_value,
    *,
    exc_info=None,
    user_message,
    log_path=None,
    show_dialog=True,
):
    """Log a fatal exception and optionally show an error dialog to the user.

    Ensures logging is configured, writes full traceback to the log,
    and presents a user-friendly dialog on the main thread.
    """
    resolved_log_path = configure_logging(log_path)
    exc_info = exc_info or (type(exc_value), exc_value, exc_value.__traceback__)

    logger = logging.getLogger(__name__)
    logger.critical("%s Log file: %s", user_message, resolved_log_path)
    logger.critical("Fatal exception details follow.", exc_info=exc_info)

    should_show_dialog = show_dialog and threading.current_thread() is threading.main_thread()
    if should_show_dialog:
        show_fatal_error_dialog(
            user_message,
            resolved_log_path,
            detail_message=build_exception_summary(exc_value),
        )

    return resolved_log_path


def install_exception_hooks(log_path=None):
    """Install global exception hooks for the main thread, worker threads, and unraisable errors.

    Ensures that any uncaught exception is logged and reported via
    report_fatal_exception, preventing silent failures.
    """
    resolved_log_path = configure_logging(log_path)

    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        if exc_type is not None and issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        report_fatal_exception(
            exc_value,
            exc_info=(exc_type, exc_value, exc_traceback),
            user_message=RUNTIME_ERROR_MESSAGE,
            log_path=resolved_log_path,
        )

    sys.excepthook = handle_unhandled_exception

    if hasattr(threading, "excepthook"):

        def handle_thread_exception(args):
            if args.exc_type is not None and issubclass(args.exc_type, KeyboardInterrupt):
                return

            report_fatal_exception(
                args.exc_value,
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
                user_message=RUNTIME_ERROR_MESSAGE,
                log_path=resolved_log_path,
                show_dialog=False,
            )

        threading.excepthook = handle_thread_exception

    if hasattr(sys, "unraisablehook"):

        def handle_unraisable_exception(unraisable):
            if unraisable.exc_type is None:
                return

            report_fatal_exception(
                unraisable.exc_value,
                exc_info=(unraisable.exc_type, unraisable.exc_value, unraisable.exc_traceback),
                user_message=RUNTIME_ERROR_MESSAGE,
                log_path=resolved_log_path,
                show_dialog=False,
            )

        sys.unraisablehook = handle_unraisable_exception

    return resolved_log_path


__all__ = [
    "LOG_FILE_NAME",
    "LOG_ROOT_ENV_VAR",
    "RUNTIME_ERROR_MESSAGE",
    "STARTUP_ERROR_MESSAGE",
    "build_exception_summary",
    "configure_logging",
    "get_log_directory",
    "get_log_file_path",
    "install_exception_hooks",
    "report_fatal_exception",
    "reset_logging_configuration",
    "show_fatal_error_dialog",
]
