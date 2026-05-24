"""Focus + shortcut + accessibility configuration, extracted from MainWindow.

View-holder controller (mirrors ``ResponsiveLayoutController``): a
single ``window`` reference; the methods reach into the widget tree
through it. Owns three responsibilities pulled out of MainWindow:

- ``configure_focus_and_shortcuts()`` — runs once at startup right
  after the layout is assembled. Pins focus policies on every
  interactive widget, walks the tab-order graph (about → language →
  search → trend buttons → right-panel buttons → table → builder),
  and binds the four window-level keyboard shortcuts (Ctrl+F /
  Ctrl+R focus the search input; Ctrl+1/2/3 switch the right panel
  tab; Ctrl+L resets the compound builder).

- ``refresh_control_accessibility()`` — re-applies localized
  accessible-name / description / tooltip strings to every control
  after a language change. Reads the current button labels and feeds
  ``build_accessibility_specs`` to derive the metadata.

- ``focus_search_input()`` — the search-focus shortcut handler.

What stays on MainWindow:

- ``eventFilter(obj, event)`` — a Qt-overridden method that has to
  live on the QObject that's installed as the filter. The buttons
  receive ``installEventFilter(self.window)`` inside the controller
  so MainWindow remains the filter target.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from src.ui.main_window_language import build_accessibility_specs


def _safe_set_tab_order(window, first, second):
    """Set tab order between two widgets, swallowing the cross-window
    edge case where Qt logs a warning.

    Returns silently when either widget is None, or when they don't
    share a window (which Qt rejects with a runtime warning otherwise).
    """
    if first is None or second is None:
        return
    try:
        if first.window() is second.window():
            window.setTabOrder(first, second)
    except Exception:
        pass


class AccessibilityController:
    """Focus + shortcut + a11y wiring for MainWindow's interactive controls."""

    def __init__(self, window):
        self.window = window

    def configure_focus_and_shortcuts(self):
        """Configure focus policies, tab order, keyboard shortcuts, and event filters."""
        window = self.window

        # Global focus policies — every keyboard-actionable widget gets
        # StrongFocus so it's reachable via Tab and from screen readers.
        window.setFocusPolicy(Qt.StrongFocus)
        window.about_button.setFocusPolicy(Qt.StrongFocus)
        window.language_selector.setFocusPolicy(Qt.StrongFocus)
        window.search_input.setFocusPolicy(Qt.StrongFocus)
        window.compound_builder_panel.setFocusPolicy(Qt.StrongFocus)
        window.periodic_table_widget.setFocusPolicy(Qt.StrongFocus)
        window.right_column_widget.setFocusPolicy(Qt.StrongFocus)

        # Trend buttons and panel buttons need an event filter so a
        # FocusIn (keyboard tab into them) activates the corresponding
        # mode — see MainWindow.eventFilter. The filter receiver MUST
        # be the window (Qt routes filter calls to the QObject that
        # was passed to installEventFilter), so the controller installs
        # ``window`` as the target rather than itself.
        for _mode, button in window.trend_buttons.items():
            button.setFocusPolicy(Qt.StrongFocus)
            button.installEventFilter(window)

        for _mode, button in window.right_panel_buttons.items():
            button.setFocusPolicy(Qt.StrongFocus)
            button.installEventFilter(window)

        # Right-panel component accessibility — gives screen readers a
        # consistent focus target on every tab.
        window.info_panel.setFocusPolicy(Qt.StrongFocus)
        window.orbital_diagram_panel.setFocusPolicy(Qt.StrongFocus)
        window.lewis_panel.setFocusPolicy(Qt.StrongFocus)
        window.molar_mass_panel.setFocusPolicy(Qt.StrongFocus)
        window.stoichiometry_panel.setFocusPolicy(Qt.StrongFocus)

        # Tab order: about → language → search → trends → panels → table → builder
        _safe_set_tab_order(window, window.about_button, window.language_selector)
        _safe_set_tab_order(window, window.language_selector, window.search_input)

        trend_keys = list(window.trend_buttons.keys())
        if trend_keys:
            first_trend = window.trend_buttons[trend_keys[0]]
            _safe_set_tab_order(window, window.search_input, first_trend)
            previous = first_trend
            for key in trend_keys[1:]:
                current = window.trend_buttons[key]
                _safe_set_tab_order(window, previous, current)
                previous = current

            right_keys = list(window.right_panel_buttons.keys())
            if right_keys:
                first_right_panel = window.right_panel_buttons[right_keys[0]]
                _safe_set_tab_order(window, previous, first_right_panel)
                previous_right = first_right_panel
                for key in right_keys[1:]:
                    current = window.right_panel_buttons[key]
                    _safe_set_tab_order(window, previous_right, current)
                    previous_right = current

                _safe_set_tab_order(window, previous_right, window.periodic_table_widget)

        _safe_set_tab_order(window, window.periodic_table_widget, window.compound_builder_panel)

        # Keyboard shortcuts — declared with window as parent so they
        # live for the window's lifetime and inherit its activation
        # scope (Qt only fires them when the window is active).
        QShortcut(QKeySequence("Ctrl+F"), window, activated=self.focus_search_input)
        QShortcut(QKeySequence("Ctrl+R"), window, activated=self.focus_search_input)
        QShortcut(
            QKeySequence("Ctrl+1"), window,
            activated=lambda: window.set_right_panel_mode("info"),
        )
        QShortcut(
            QKeySequence("Ctrl+2"), window,
            activated=lambda: window.set_right_panel_mode("diagram"),
        )
        QShortcut(
            QKeySequence("Ctrl+3"), window,
            activated=lambda: window.set_right_panel_mode("lewis"),
        )
        QShortcut(QKeySequence("Ctrl+L"), window, activated=window.reset_builder)

    def focus_search_input(self):
        """Move keyboard focus to the search input field."""
        self.window.search_input.setFocus(Qt.TabFocusReason)

    def refresh_control_accessibility(self):
        """Rebuild and apply accessible names / descriptions / tooltips for all interactive controls.

        Triggered after every language change so screen-reader users
        get the updated labels without having to reload the window.
        """
        window = self.window
        specs = build_accessibility_specs(
            about_text=window.about_button.text(),
            search_placeholder=window.search_input.placeholderText(),
            search_button_text=window.search_button.text(),
            build_button_text=window.build_button.text(),
            reset_button_text=window.builder_reset_button.text(),
            trend_button_texts={
                mode: button.text()
                for mode, button in getattr(window, "trend_buttons", {}).items()
            },
            right_panel_button_texts={
                mode: button.text()
                for mode, button in getattr(window, "right_panel_buttons", {}).items()
            },
        )

        self._apply_spec(window.about_button, specs["about_button"])
        self._apply_spec(window.search_input, specs["search_input"])
        self._apply_spec(window.search_button, specs["search_button"])
        self._apply_spec(window.build_button, specs["build_button"])
        self._apply_spec(window.builder_reset_button, specs["builder_reset_button"])

        for mode, button in getattr(window, "trend_buttons", {}).items():
            self._apply_spec(button, specs["trend_buttons"][mode])

        for mode, button in getattr(window, "right_panel_buttons", {}).items():
            self._apply_spec(button, specs["right_panel_buttons"][mode])

    @staticmethod
    def _apply_spec(widget, spec):
        """Apply a single accessibility spec dict to a widget."""
        widget.setAccessibleName(spec["name"])
        widget.setAccessibleDescription(spec["description"])
        widget.setToolTip(spec["tooltip"])
