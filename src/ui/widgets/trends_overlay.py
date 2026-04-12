import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from src.ui.styles import TREND_OVERLAY_LABEL_BACKGROUND_RGBA, get_trend_overlay_color


class TrendsOverlay(QWidget):
    """Transparent overlay that draws directional trend arrows on the periodic table.

    Paints a diagonal arrow with a label box indicating the direction
    of metallic or nonmetallic character increase across the table.
    """

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName("trendsOverlay_inactive")
        self.setAccessibleName("Trend overlay")
        self.mode = None
        self.metallic_text = "Metallic character \u2199"
        self.nonmetallic_text = "Nonmetallic character \u2197"
        self._apply_accessibility_metadata()

    def set_mode(self, mode):
        self.mode = mode
        self._apply_accessibility_metadata()
        self.update()

    def set_texts(self, metallic_text, nonmetallic_text):
        self.metallic_text = metallic_text
        self.nonmetallic_text = nonmetallic_text
        self._apply_accessibility_metadata()
        self.update()

    def _apply_accessibility_metadata(self):
        if self.mode == "metallic":
            self.setObjectName("trendsOverlay_metallic")
            self.setAccessibleDescription(f"Trend overlay active: {self.metallic_text}")
        elif self.mode == "nonmetallic":
            self.setObjectName("trendsOverlay_nonmetallic")
            self.setAccessibleDescription(f"Trend overlay active: {self.nonmetallic_text}")
        else:
            self.setObjectName("trendsOverlay_inactive")
            self.setAccessibleDescription("Trend overlay hidden.")

    def draw_arrow(self, painter, start, end, color):
        pen = QPen(color, 4)
        painter.setPen(pen)
        painter.drawLine(start, end)

        angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        arrow_size = 12

        p1 = QPointF(
            end.x() - arrow_size * math.cos(angle - math.pi / 6),
            end.y() - arrow_size * math.sin(angle - math.pi / 6),
        )
        p2 = QPointF(
            end.x() - arrow_size * math.cos(angle + math.pi / 6),
            end.y() - arrow_size * math.sin(angle + math.pi / 6),
        )

        painter.drawLine(end, p1)
        painter.drawLine(end, p2)

    def draw_label_box(self, painter, rect, title_lines, color):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(*TREND_OVERLAY_LABEL_BACKGROUND_RGBA))
        painter.drawRoundedRect(rect, 10, 10)

        painter.setPen(color)
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))

        x = rect.x() + 10
        y = rect.y() + 20
        line_height = 16

        for line in title_lines:
            painter.drawText(x, y, line)
            y += line_height

    def paintEvent(self, event):
        if self.mode is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        if self.mode == "metallic":
            color = QColor(get_trend_overlay_color("metallic"))
            start = QPointF(width * 0.60, height * 0.42)
            end = QPointF(width * 0.18, height * 0.82)
            self.draw_arrow(painter, start, end, color)
            rect = QRectF(width * 0.02, height * 0.72, width * 0.30, height * 0.10)
            self.draw_label_box(painter, rect, [self.metallic_text], color)
        elif self.mode == "nonmetallic":
            color = QColor(get_trend_overlay_color("nonmetallic"))
            start = QPointF(width * 0.28, height * 0.68)
            end = QPointF(width * 0.84, height * 0.16)
            self.draw_arrow(painter, start, end, color)
            rect = QRectF(width * 0.60, height * 0.04, width * 0.34, height * 0.10)
            self.draw_label_box(painter, rect, [self.nonmetallic_text], color)
