"""Responsive layout policy application, extracted from MainWindow.

Owns the logic that takes a `ResponsiveLayoutPolicy` (computed from
the current window width by `src.ui.layout_policy.compute_responsive_layout`)
and applies it to MainWindow's widget tree: layout direction,
alignment, search/builder/right-column widths, periodic-table cell
metrics, and the trend status label visibility.

Takes a reference to the MainWindow (called `window`) and reaches
into its widget tree to read sizes and write layout decisions. The
"view holder" pattern keeps the controller's surface tiny (single
public method `apply()`) while making the ~80 LOC of layout math
discoverable in a focused file outside the 1500+ LOC orchestrator.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout

from src.ui.layout_policy import (
    HORIZONTAL,
    UNBOUNDED_MAX_WIDTH,
    VERTICAL,
    compute_responsive_layout,
)

_DIRECTION_MAP = {
    HORIZONTAL: QBoxLayout.LeftToRight,
    VERTICAL: QBoxLayout.TopToBottom,
}


class ResponsiveLayoutController:
    """Compute the responsive policy for the current window width and apply it."""

    def __init__(self, window):
        self.window = window

    def apply(self):
        """Recompute and apply the responsive layout policy."""
        w = self.window
        policy = compute_responsive_layout(w.width())

        w.top_controls_layout.setDirection(_DIRECTION_MAP[policy.top_controls_direction])
        w.content_layout.setDirection(_DIRECTION_MAP[policy.content_direction])
        w.top_controls_layout.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
            if policy.top_controls_direction == HORIZONTAL
            else Qt.AlignTop
        )

        viewport_width = max(w.width(), w.main_scroll_area.viewport().width())
        available_top_width = max(
            0,
            viewport_width
            - w.main_layout.contentsMargins().left()
            - w.main_layout.contentsMargins().right(),
        )
        top_spacing = w.top_controls_layout.spacing()
        if policy.top_controls_direction == HORIZONTAL:
            horizontal_top_width = max(0, available_top_width - top_spacing)
            search_width = min(
                policy.search_max_width,
                max(430, int(horizontal_top_width * 0.34)),
            )
            w.search_widget.setMinimumWidth(search_width)
            w.search_widget.setMaximumWidth(search_width)
        else:
            w.search_widget.setMinimumWidth(0)
            w.search_widget.setMaximumWidth(policy.search_max_width)

        w.builder_widget.setMaximumWidth(UNBOUNDED_MAX_WIDTH)
        w.right_column_widget.setMaximumWidth(policy.right_column_max_width)
        self._sync_trend_status_visibility(policy.mode)

        # Update the window's metric attrs (consumed by orbital diagram, etc.).
        w.cell_size = policy.cell_size
        w.side_width = policy.side_width
        w.header_height = policy.header_height
        w.grid_h_spacing = policy.grid_h_spacing
        w.grid_v_spacing = policy.grid_v_spacing
        w.element_font_size = policy.element_font_size

        w.periodic_table_widget.update_metrics(
            cell_size=policy.cell_size,
            header_height=policy.header_height,
            side_width=policy.side_width,
            grid_h_spacing=policy.grid_h_spacing,
            grid_v_spacing=policy.grid_v_spacing,
            element_font_size=policy.element_font_size,
        )
        self._sync_compact_section_heights()
        self._sync_right_column_height(policy.content_direction)

        w.content_widget.adjustSize()

    def _sync_right_column_height(self, content_direction):
        """Constrain the right column height to match the table when in horizontal layout."""
        w = self.window
        if content_direction == HORIZONTAL:
            table_height = w.periodic_table_widget.sizeHint().height()
            buttons_height = w.right_panel_buttons_widget.sizeHint().height()
            spacing = w.right_column_widget.layout().spacing()
            panel_height = max(0, table_height - buttons_height - spacing)
            w.right_column_widget.setMaximumHeight(table_height)
            w.right_panel_container.setMaximumHeight(panel_height)
            return

        w.right_column_widget.setMaximumHeight(UNBOUNDED_MAX_WIDTH)
        w.right_panel_container.setMaximumHeight(UNBOUNDED_MAX_WIDTH)

    @staticmethod
    def _sync_height_for_width_widget(widget):
        """Set a widget's fixed height from its heightForWidth hint (used for flow-layout sections)."""
        if widget is None:
            return

        if widget.hasHeightForWidth() and widget.width() > 0:
            height = widget.heightForWidth(widget.width())
        else:
            height = widget.sizeHint().height()

        if height > 0:
            widget.setFixedHeight(height)

    def _sync_compact_section_heights(self):
        """Recalculate fixed heights for the trend container and panel buttons."""
        self._sync_height_for_width_widget(self.window.trend_container)
        self._sync_height_for_width_widget(self.window.right_panel_buttons_widget)

    def _sync_trend_status_visibility(self, mode):
        """Hide the trend status label on wide/medium layouts where space is tight."""
        self.window.trend_status_label.setVisible(mode not in {"wide", "medium"})
