"""Right-side panel that renders a Lewis dot diagram for the selected element.

Shows the element symbol centred with valence electrons drawn as dots
on four sides (top, right, bottom, left), following standard convention.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.domain.lewis_diagram import distribute_dots, get_valence_electrons
from src.ui.theme import get_theme


class LewisPanel(QWidget):
    """Right-side panel displaying a Lewis dot diagram for a selected element."""

    def __init__(self, title_text, prompt_text):
        super().__init__()
        self.setObjectName("lewisPanel")
        self.setFocusPolicy(Qt.StrongFocus)
        self._theme = get_theme("dark")
        self._last_render = None

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("diagramTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Lewis diagram title")

        self.diagram_label = QLabel(prompt_text)
        self.diagram_label.setAccessibleName("Lewis diagram display")
        self.diagram_label.setAccessibleDescription("Displays Lewis dot diagram or instructions.")
        self.diagram_label.setObjectName("diagramBoxLabel")
        self.diagram_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.diagram_label.setWordWrap(True)
        self.diagram_label.setMinimumHeight(260)

        self.valence_label = QLabel("")
        self.valence_label.setObjectName("lewisValenceLabel")
        self.valence_label.setAlignment(Qt.AlignCenter)
        self.valence_label.setWordWrap(True)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.diagram_label)
        card_layout.addWidget(self.valence_label)
        self.card_widget.setLayout(card_layout)

        self.setAccessibleName("Lewis Diagram Panel")
        self.setAccessibleDescription("Contains Lewis dot diagram for the selected element.")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

    def set_prompt(self, title_text, prompt_text):
        """Show a text prompt instead of a diagram."""
        self.title_label.setText(title_text)
        self.diagram_label.setPixmap(QPixmap())
        self.diagram_label.setText(prompt_text)
        self.valence_label.setText("")
        self._last_render = None

    def apply_theme(self, theme_name):
        """Switch the painter palette and redraw the last diagram, if any."""
        self._theme = get_theme(theme_name)
        if self._last_render is None:
            return
        symbol, valence = self._last_render
        pixmap = self._create_lewis_pixmap(symbol, valence)
        self.diagram_label.setPixmap(pixmap)

    def show_lewis_diagram(self, element, *, translate, format_value):
        """Generate and display the Lewis dot diagram for the given element."""
        symbol = format_value(element.get("symbol"))
        self.title_label.setText(translate("lewis_title"))

        valence = get_valence_electrons(element)
        if valence is None:
            self.diagram_label.setPixmap(QPixmap())
            self.diagram_label.setText(translate("lewis_not_applicable"))
            self.valence_label.setText("")
            self._last_render = None
            return

        pixmap = self._create_lewis_pixmap(symbol, valence)
        self.diagram_label.setText("")
        self.diagram_label.setPixmap(pixmap)
        self.valence_label.setText(
            translate("lewis_valence_electrons", count=valence)
        )
        self._last_render = (symbol, valence)

    def _create_lewis_pixmap(self, symbol, valence_electrons):
        """Render the Lewis dot diagram as a QPixmap image."""
        theme = self._theme
        size = 240
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(theme["painter_bg"]))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw element symbol at center
        symbol_font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(symbol_font)
        painter.setPen(QColor(theme["painter_text"]))
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(symbol)
        text_height = fm.height()
        cx = size // 2
        cy = size // 2
        painter.drawText(
            cx - text_width // 2,
            cy + fm.ascent() // 2 - 2,
            symbol,
        )

        # Dot positions and distribution
        dots = distribute_dots(valence_electrons)
        dot_radius = 5
        dot_color = QColor(theme["painter_dot"])
        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)

        # Spacing between paired dots
        pair_gap = 12

        # Boundaries around the symbol
        sym_left = cx - text_width // 2 - 8
        sym_right = cx + text_width // 2 + 8
        sym_top = cy - text_height // 2 + 4
        sym_bottom = cy + text_height // 2 - 4

        # Top dots: centred above symbol
        count = dots["top"]
        top_y = sym_top - 16
        if count == 1:
            painter.drawEllipse(cx - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(cx - pair_gap // 2 - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(cx + pair_gap // 2 - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)

        # Bottom dots: centred below symbol
        count = dots["bottom"]
        bottom_y = sym_bottom + 16
        if count == 1:
            painter.drawEllipse(cx - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(cx - pair_gap // 2 - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(cx + pair_gap // 2 - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)

        # Right dots: centred right of symbol
        count = dots["right"]
        right_x = sym_right + 16
        if count == 1:
            painter.drawEllipse(right_x - dot_radius, cy - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(right_x - dot_radius, cy - pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(right_x - dot_radius, cy + pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)

        # Left dots: centred left of symbol
        count = dots["left"]
        left_x = sym_left - 16
        if count == 1:
            painter.drawEllipse(left_x - dot_radius, cy - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(left_x - dot_radius, cy - pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(left_x - dot_radius, cy + pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)

        painter.end()
        return pixmap

    def apply_language(self, *, title, prompt):
        """Update translatable texts when the UI language changes."""
        self.title_label.setText(title)
        if not self.diagram_label.pixmap() or self.diagram_label.pixmap().isNull():
            self.diagram_label.setText(prompt)
