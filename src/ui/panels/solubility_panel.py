"""Tool-area panel for ionic compound solubility lookup and matrix display.

Provides a quick-check section (two ComboBoxes + Check button) and a
QPainter-rendered solubility matrix with highlight for the selected element.
"""

import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.domain.solubility import (
    ANIONS,
    CATIONS,
    get_cations_for_element,
    get_solubility,
    get_solubility_matrix,
    get_solubility_rule,
)
from src.ui.theme import get_theme

# Cell and layout constants
_CELL_W = 36
_CELL_H = 24
_GAP = 1
_HEADER_FONT_SIZE = 8
_CELL_FONT_SIZE = 8
_ANION_ROTATE_DEG = -60

_VERDICT_SYMBOL = {
    "soluble": "S",
    "insoluble": "I",
    "slightly_soluble": "~",
}


def _verdict_color(theme, verdict):
    """Return the theme-specific background color for a verdict category."""
    return theme["solubility_soluble"] if verdict == "soluble" else (
        theme["solubility_insoluble"] if verdict == "insoluble"
        else theme["solubility_slightly"]
    )

_RULE_TEXT_KEY = {
    "alkali_ammonium": "solubility_rule_alkali",
    "nitrate_acetate": "solubility_rule_nitrate_acetate",
    "halides": "solubility_rule_halide",
    "sulfates": "solubility_rule_sulfate",
    "hydroxides": "solubility_rule_hydroxide",
    "carbonate_phosphate_sulfide": "solubility_rule_carbonate_phosphate_sulfide",
}


class SolubilityPanel(QWidget):
    """Tool-area panel displaying solubility lookup and matrix."""

    def __init__(self, title_text, prompt_text):
        super().__init__()
        self.setObjectName("solubilityPanel")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)
        self._theme = get_theme("dark")

        # --- Localized string storage ---
        self._soluble_text = "Soluble"
        self._insoluble_text = "Insoluble"
        self._slightly_text = "Slightly soluble"
        self._rule_label = "Rule:"
        self._exceptions_label = "Exceptions:"
        self._legend_title = "Legend"
        self._rule_texts = {}
        self._default_rule_text = "No specific rule applies; assumed insoluble."
        self._prompt_text = prompt_text

        # --- Title ---
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("compoundTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Solubility panel title")

        # --- Quick check section ---
        cation_label = QLabel("Cation")
        self._cation_label_widget = cation_label
        self.cation_combo = QComboBox()
        self.cation_combo.setObjectName("solubilityCationCombo")
        self.cation_combo.addItems(CATIONS)
        self.cation_combo.setAccessibleName("Cation selector")

        anion_label = QLabel("Anion")
        self._anion_label_widget = anion_label
        self.anion_combo = QComboBox()
        self.anion_combo.setObjectName("solubilityAnionCombo")
        self.anion_combo.addItems(ANIONS)
        self.anion_combo.setAccessibleName("Anion selector")

        self.check_button = QPushButton("Check")
        self.check_button.setObjectName("builderButton")
        self.check_button.setAccessibleName("Check solubility")
        self.check_button.clicked.connect(self._on_check)

        check_row = QHBoxLayout()
        check_row.setContentsMargins(0, 0, 0, 0)
        check_row.setSpacing(6)
        check_row.addWidget(cation_label)
        check_row.addWidget(self.cation_combo, 1)
        check_row.addWidget(anion_label)
        check_row.addWidget(self.anion_combo, 1)
        check_row.addWidget(self.check_button)

        # --- Verdict label ---
        self.verdict_label = QLabel(prompt_text)
        self.verdict_label.setObjectName("compoundResultLabel")
        self.verdict_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.verdict_label.setWordWrap(True)
        self.verdict_label.setAccessibleName("Solubility result")
        self.verdict_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # --- Matrix display ---
        self.matrix_label = QLabel()
        self.matrix_label.setAccessibleName("Solubility matrix")
        self.matrix_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setObjectName("solubilityScroll")
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.matrix_label)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        # --- Legend ---
        self.legend_widget = self._build_legend()

        # --- Card ---
        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addLayout(check_row)
        card_layout.addWidget(self.verdict_label)
        card_layout.addWidget(scroll, 1)
        card_layout.addWidget(self.legend_widget)
        self.card_widget.setLayout(card_layout)

        self.setAccessibleName("Solubility Panel")
        self.setAccessibleDescription("Solubility lookup and matrix display.")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

        # Initial render
        self._highlight_cations = []
        self._matrix_cell_accessibility = []
        self._render_matrix()

    def highlight_element(self, symbol):
        """Highlight matrix rows for the cations of the given element."""
        self._highlight_cations = get_cations_for_element(symbol)
        self._render_matrix()

    def clear_highlight(self):
        """Remove any row highlight from the matrix."""
        self._highlight_cations = []
        self._render_matrix()

    def apply_theme(self, theme_name):
        """Switch the painter palette and redraw the matrix and legend swatches."""
        new_theme = get_theme(theme_name)
        if new_theme is self._theme:
            return
        self._theme = new_theme
        self._refresh_legend_swatches()
        self._render_matrix()

    def apply_language(
        self,
        *,
        title,
        prompt,
        cation_label,
        anion_label,
        check_text,
        soluble_text,
        insoluble_text,
        slightly_text,
        rule_label,
        exceptions_label,
        legend_title,
        rule_alkali,
        rule_nitrate_acetate,
        rule_halide,
        rule_sulfate,
        rule_hydroxide,
        rule_carbonate_phosphate_sulfide,
        rule_default,
    ):
        """Update all translatable strings when the UI language changes."""
        self.title_label.setText(title)
        self._prompt_text = prompt
        self._cation_label_widget.setText(cation_label)
        self._anion_label_widget.setText(anion_label)
        self.check_button.setText(check_text)
        self._soluble_text = soluble_text
        self._insoluble_text = insoluble_text
        self._slightly_text = slightly_text
        self._rule_label = rule_label
        self._exceptions_label = exceptions_label
        self._legend_title = legend_title
        self._rule_texts = {
            "solubility_rule_alkali": rule_alkali,
            "solubility_rule_nitrate_acetate": rule_nitrate_acetate,
            "solubility_rule_halide": rule_halide,
            "solubility_rule_sulfate": rule_sulfate,
            "solubility_rule_hydroxide": rule_hydroxide,
            "solubility_rule_carbonate_phosphate_sulfide": rule_carbonate_phosphate_sulfide,
        }
        self._default_rule_text = rule_default

        # Update legend labels
        self._legend_title_label.setText(legend_title)
        self._legend_labels[0].setText(soluble_text)
        self._legend_labels[1].setText(insoluble_text)
        self._legend_labels[2].setText(slightly_text)

        # Refresh matrix so its accessibility description picks up the new verdict labels.
        self._render_matrix()

    def _on_check(self):
        """Look up solubility for the selected cation/anion pair."""
        cation = self.cation_combo.currentText()
        anion = self.anion_combo.currentText()
        verdict = get_solubility(cation, anion)
        rule = get_solubility_rule(cation, anion)

        verdict_text = {
            "soluble": self._soluble_text,
            "insoluble": self._insoluble_text,
            "slightly_soluble": self._slightly_text,
        }[verdict]
        color = _verdict_color(self._theme, verdict)

        lines = [
            f'<span style="color:{color}; font-size:14px;">\u25cf</span> '
            f'<b>{verdict_text}</b>'
        ]

        if rule:
            rule_key = _RULE_TEXT_KEY.get(rule["id"])
            rule_desc = self._rule_texts.get(rule_key, rule["id"])
            lines.append(f"<br><b>{self._rule_label}</b> {rule_desc}")
            if rule["exceptions"]:
                exc_items = ", ".join(
                    f"{ion}" for ion in sorted(rule["exceptions"])
                )
                lines.append(f"<br><b>{self._exceptions_label}</b> {exc_items}")
        else:
            lines.append(f"<br><b>{self._rule_label}</b> {self._default_rule_text}")

        self.verdict_label.setText("".join(lines))

    def _build_legend(self):
        """Build the legend row with title and three colored squares and labels."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._legend_title_label = QLabel(self._legend_title)
        self._legend_title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._legend_title_label)

        self._legend_labels = []
        self._legend_swatches = []
        texts = [self._soluble_text, self._insoluble_text, self._slightly_text]
        for text in texts:
            swatch = QLabel()
            swatch.setFixedSize(16, 12)
            self._legend_swatches.append(swatch)

            label = QLabel(text)
            self._legend_labels.append(label)

            layout.addWidget(swatch)
            layout.addWidget(label)

        self._refresh_legend_swatches()
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _refresh_legend_swatches(self):
        """Apply the current theme colors to the three legend swatches."""
        if not getattr(self, "_legend_swatches", None):
            return
        colors = [
            self._theme["solubility_soluble"],
            self._theme["solubility_insoluble"],
            self._theme["solubility_slightly"],
        ]
        for swatch, color in zip(self._legend_swatches, colors, strict=True):
            swatch.setStyleSheet(f"background-color: {color}; border-radius: 2px;")

    def _render_matrix(self):
        """Generate the solubility matrix as a QPixmap and display it."""
        matrix = get_solubility_matrix()
        header_font = QFont("Segoe UI", _HEADER_FONT_SIZE)
        cell_font = QFont("Segoe UI", _CELL_FONT_SIZE, QFont.Bold)

        # Measure row header width (longest cation)
        temp_pixmap = QPixmap(1, 1)
        temp_painter = QPainter(temp_pixmap)
        temp_painter.setFont(header_font)
        fm = temp_painter.fontMetrics()
        row_header_w = max(fm.horizontalAdvance(c) for c in CATIONS) + 8

        # Measure column header height (rotated anion text)
        max_anion_w = max(fm.horizontalAdvance(a) for a in ANIONS)
        angle_rad = math.radians(abs(_ANION_ROTATE_DEG))
        col_header_h = int(max_anion_w * math.sin(angle_rad) + fm.height() * math.cos(angle_rad)) + 8
        temp_painter.end()

        grid_w = len(ANIONS) * (_CELL_W + _GAP)
        grid_h = len(CATIONS) * (_CELL_H + _GAP)
        total_w = row_header_w + grid_w + 4
        total_h = col_header_h + grid_h + 4

        theme = self._theme
        pixmap = QPixmap(total_w, total_h)
        pixmap.fill(QColor(theme["painter_bg"]))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        highlight_set = set(self._highlight_cations)
        header_color = QColor(theme["painter_subtext"])
        text_color = QColor(theme["painter_text"])
        highlight_color = QColor(theme["solubility_highlight"])

        # --- Draw column headers (anions, rotated) ---
        painter.setFont(header_font)
        painter.setPen(header_color)
        for j, anion in enumerate(ANIONS):
            x = row_header_w + j * (_CELL_W + _GAP) + _CELL_W // 2
            y = col_header_h - 4
            painter.save()
            painter.translate(x, y)
            painter.rotate(_ANION_ROTATE_DEG)
            painter.drawText(0, 0, anion)
            painter.restore()

        # --- Draw row headers (cations) and cells ---
        for i, cation in enumerate(CATIONS):
            cy = col_header_h + i * (_CELL_H + _GAP)
            is_highlighted = cation in highlight_set

            # Row header
            painter.setFont(header_font)
            painter.setPen(header_color)
            painter.drawText(
                0, cy, row_header_w - 4, _CELL_H,
                Qt.AlignRight | Qt.AlignVCenter, cation,
            )

            # Cells
            for j, _anion in enumerate(ANIONS):
                cx = row_header_w + j * (_CELL_W + _GAP)
                verdict = matrix[i][j]
                cell_color = QColor(_verdict_color(theme, verdict))

                painter.setPen(Qt.NoPen)
                painter.setBrush(cell_color)
                painter.drawRect(cx, cy, _CELL_W, _CELL_H)

                # Cell symbol
                painter.setFont(cell_font)
                painter.setPen(text_color)
                painter.drawText(
                    cx, cy, _CELL_W, _CELL_H,
                    Qt.AlignCenter, _VERDICT_SYMBOL[verdict],
                )

            # Highlight border for row
            if is_highlighted:
                pen = QPen(highlight_color, 2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(
                    row_header_w - 1, cy - 1,
                    grid_w + 2, _CELL_H + 2,
                )

        painter.end()
        self.matrix_label.setPixmap(pixmap)

        verdict_label_map = {
            "soluble": self._soluble_text,
            "insoluble": self._insoluble_text,
            "slightly_soluble": self._slightly_text,
        }
        cell_entries = []
        for i, cation in enumerate(CATIONS):
            for j, anion in enumerate(ANIONS):
                verdict = matrix[i][j]
                result_text = verdict_label_map.get(verdict, verdict)
                cell_entries.append(f"{cation} + {anion}: {result_text}")
        self._matrix_cell_accessibility = cell_entries
        self.matrix_label.setAccessibleDescription("; ".join(cell_entries))
