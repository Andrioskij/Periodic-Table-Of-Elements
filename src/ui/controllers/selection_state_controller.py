"""Element-selection orchestration, extracted from MainWindow.

Owns the "select an element" surface: programmatic selection, applying
the selection to the underlying ``SelectionState`` dataclass, syncing
the header label from the periodic-table widget, highlighting the
solubility panel, and fanning out to the info / diagram / Lewis
right-panel refreshes.

Small but coherent extraction: MainWindow keeps the
``current_selected_element`` / ``selected_button`` properties on
``selection_state`` (they're read from many sites), and the periodic
table's ``on_element_selected`` callback stays as a 1-line MainWindow
delegation so the layout wiring is unchanged.
"""


class SelectionStateController:
    """View-holder controller for element-selection orchestration.

    Bound to ``SelectionState`` plus the periodic-table widget, the
    solubility panel, and a callable that refreshes the
    info/diagram/lewis right-panel pages.
    """

    def __init__(
        self,
        *,
        selection_state,
        periodic_table_widget,
        solubility_panel,
        refresh_panel_modes,
    ):
        self.selection_state = selection_state
        self.periodic_table_widget = periodic_table_widget
        self.solubility_panel = solubility_panel
        self.refresh_panel_modes = refresh_panel_modes

    @property
    def current_element(self):
        """Return the currently selected element dict (or None)."""
        return self.selection_state.element

    def activate_element(self, element):
        """Programmatically select an element (convenience entry point)."""
        self.select_element(element)

    def select_element(self, element):
        """Select an element in the table widget and apply it as active."""
        self.periodic_table_widget.select_element(element)
        self.apply_selected_element(element)

    def apply_selected_element(self, element):
        """Store the selection, refresh the header, and refresh info/diagram/lewis panels."""
        self.selection_state.element = element
        self.refresh_selection_header()
        self.refresh_panel_modes(("info", "diagram", "lewis"))
        symbol = element.get("symbol", "") if element else ""
        if symbol:
            self.solubility_panel.highlight_element(symbol)
        else:
            self.solubility_panel.clear_highlight()

    def refresh_selection_header(self):
        """Sync the selection state from the table widget and refresh the header label."""
        self.selection_state.selected_button = self.periodic_table_widget.selected_button
        self.periodic_table_widget.refresh_selected_element_name()
