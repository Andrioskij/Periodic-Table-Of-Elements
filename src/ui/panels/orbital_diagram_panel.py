from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.config.static_data import ORBITAL_BOX_COUNTS, VALID_SUBSHELLS
from src.domain.electron_configuration import configuration_to_map, fill_boxes
from src.ui.theme import get_theme


class OrbitalDiagramPanel(QWidget):
    """Right-side panel that renders an orbital box diagram for the selected element.

    Draws boxes for each subshell (s, p, d, f) with up/down arrows
    representing electron spin, following Hund's rule distribution.
    """

    def __init__(self, title_text, prompt_text):
        super().__init__()
        self.setObjectName("orbitalDiagramPanel")
        self.setFocusPolicy(Qt.StrongFocus)
        self._theme = get_theme("dark")
        self._last_render = None

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("diagramTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Orbital diagram title")

        self.diagram_label = QLabel(prompt_text)
        self.diagram_label.setAccessibleName("Orbital diagram prompt")
        self.diagram_label.setAccessibleDescription("Displays orbital diagram or instructions.")
        self.diagram_label.setObjectName("diagramBoxLabel")
        self.diagram_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.diagram_label.setWordWrap(True)
        self.diagram_label.setMinimumHeight(260)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.diagram_label)
        self.card_widget.setLayout(card_layout)

        self.setAccessibleName("Orbital Diagram Panel")
        self.setAccessibleDescription("Contains orbital diagram information for the selected element.")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

    def set_prompt(self, title_text, prompt_text):
        self.title_label.setText(title_text)
        self.diagram_label.setPixmap(QPixmap())
        self.diagram_label.setText(prompt_text)
        self._last_render = None

    def apply_theme(self, theme_name):
        """Switch the painter palette and redraw the last diagram, if any."""
        new_theme = get_theme(theme_name)
        if new_theme is self._theme:
            return
        self._theme = new_theme
        if self._last_render is None:
            return
        config_text, symbol, cell_size = self._last_render
        pixmap = self.create_orbital_diagram_pixmap(config_text, symbol, cell_size)
        if pixmap is not None:
            self.diagram_label.setPixmap(pixmap)

    def show_orbital_diagram(self, element, *, translate, cell_size, format_value):
        """Generate and display the orbital diagram for the given element.

        Falls back to a 'not available' message when the electron
        configuration cannot be parsed.
        """
        symbol = format_value(element.get("symbol"))
        config_text = element.get("electron_configuration")
        self.title_label.setText(translate("diagram_title_symbol", symbol=symbol))

        pixmap = self.create_orbital_diagram_pixmap(config_text, symbol, cell_size)
        if pixmap is None:
            self.diagram_label.setPixmap(QPixmap())
            self.diagram_label.setText(translate("diagram_not_available"))
            self.diagram_label.setAccessibleName(translate("diagram_not_available"))
            self._last_render = None
        else:
            self.diagram_label.setText("")
            self.diagram_label.setPixmap(pixmap)
            self.diagram_label.setAccessibleName(
                translate(
                    "diagram_accessible_name",
                    symbol=symbol,
                    config=config_text or "",
                )
            )
            self._last_render = (config_text, symbol, cell_size)

    def create_orbital_diagram_pixmap(self, config_text, symbol, cell_size):
        """Render the orbital box diagram as a QPixmap image.

        Parses the electron configuration, distributes electrons into
        boxes following Hund's rule, and draws the result as a grid of
        labeled boxes with up/down spin arrows.
        """
        occupancy_map = configuration_to_map(config_text)
        if not occupancy_map:
            return None

        box_width = max(8, int(cell_size * 0.24))
        box_height = max(12, int(cell_size * 0.34))
        box_gap = 2
        column_gap = max(10, int(cell_size * 0.22))
        row_gap = max(8, int(cell_size * 0.18))
        top_margin = 24
        left_margin = 16
        label_height = 12

        def block_width(subshell):
            box_count = ORBITAL_BOX_COUNTS[subshell]
            return (box_count * box_width) + ((box_count - 1) * box_gap)

        subshell_columns = ["s", "p", "d", "f"]
        column_x = {}
        current_x = left_margin + 18

        for subshell in subshell_columns:
            column_x[subshell] = current_x
            current_x += block_width(subshell) + column_gap

        total_width = current_x + 10
        total_height = top_margin + 7 * (label_height + box_height + row_gap) + 8

        theme = self._theme
        pixmap = QPixmap(total_width, total_height)
        pixmap.fill(QColor(theme["painter_bg"]))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(theme["painter_text"]))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(10, 16, symbol)

        for level in range(1, 8):
            y_base = top_margin + (level - 1) * (label_height + box_height + row_gap)
            painter.setPen(QColor(theme["painter_subtext"]))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(4, y_base + box_height + 1, str(level))

            for subshell in VALID_SUBSHELLS[level]:
                key = f"{level}{subshell}"
                if key not in occupancy_map:
                    continue

                electrons = occupancy_map[key]
                box_count = ORBITAL_BOX_COUNTS[subshell]
                boxes = fill_boxes(electrons, box_count)
                x_base = column_x[subshell]

                painter.setPen(QColor(theme["painter_label"]))
                painter.setFont(QFont("Segoe UI", 7))
                painter.drawText(x_base, y_base - 1, key)

                for index in range(box_count):
                    x = x_base + index * (box_width + box_gap)
                    y = y_base
                    painter.setPen(QPen(QColor(theme["painter_box_border"]), 1))
                    painter.drawRect(x, y, box_width, box_height)

                    if boxes[index] >= 1:
                        painter.setPen(QColor(theme["painter_arrow_up"]))
                        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                        painter.drawText(x + 1, y + box_height - 3, "\u2191")
                    if boxes[index] == 2:
                        painter.setPen(QColor(theme["painter_arrow_down"]))
                        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                        painter.drawText(x + box_width - 7, y + box_height - 3, "\u2193")

        painter.end()
        return pixmap
