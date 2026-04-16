"""Right-side panel for the molar mass calculator."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.domain.molar_mass import (
    FormulaError,
    compute_molar_mass,
    compute_percent_composition,
    parse_formula,
)


class MolarMassPanel(QWidget):
    """Right-side panel that computes molar mass and percent composition.

    The user enters a chemical formula (e.g. H2O, Ca(OH)2) and clicks
    Calculate to see the molar mass and element-by-element breakdown.
    """

    def __init__(self, title_text, prompt_text, elements):
        super().__init__()
        self.elements = elements
        self.setObjectName("molarMassPanel")
        self.setFocusPolicy(Qt.StrongFocus)

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("compoundTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Molar mass panel title")

        self.formula_input = QLineEdit()
        self.formula_input.setObjectName("molarMassInput")
        self.formula_input.setPlaceholderText("H2O, Ca(OH)2, Fe2(SO4)3...")
        self.formula_input.setAccessibleName("Chemical formula input")

        self.calculate_button = QPushButton()
        self.calculate_button.setObjectName("builderButton")
        self.calculate_button.setAccessibleName("Calculate molar mass")
        self.calculate_button.clicked.connect(self._on_calculate)
        self.formula_input.returnPressed.connect(self._on_calculate)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.setSpacing(6)
        input_row.addWidget(self.formula_input, 1)
        input_row.addWidget(self.calculate_button, 0)

        self.result_label = QLabel(prompt_text)
        self.result_label.setObjectName("compoundResultLabel")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setWordWrap(True)
        self.result_label.setAccessibleName("Molar mass result")
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setAccessibleName("Molar Mass Panel")
        self.setAccessibleDescription("Calculates molar mass and percent composition.")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addLayout(input_row)
        card_layout.addWidget(self.result_label)
        self.card_widget.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

        self._calculate_label_text = "Calculate"
        self._error_prefix = "Error"

    def set_title(self, text):
        """Update the panel title."""
        self.title_label.setText(text)

    def set_prompt(self, text, prompt_text=None):
        """Show a prompt message in the result area."""
        self.result_label.setText(prompt_text if prompt_text is not None else text)

    def set_button_text(self, text):
        """Update the calculate button label."""
        self._calculate_label_text = text
        self.calculate_button.setText(text)

    def set_error_prefix(self, text):
        """Set the localized prefix for error messages."""
        self._error_prefix = text

    def apply_language(self, *, title, prompt, button_text, error_prefix):
        """Apply localized strings to all visible labels."""
        self.set_title(title)
        self.set_prompt(prompt)
        self.set_button_text(button_text)
        self.set_error_prefix(error_prefix)

    def _on_calculate(self):
        """Parse the formula and display results."""
        formula = self.formula_input.text().strip()
        if not formula:
            return

        try:
            atom_counts = parse_formula(formula)
            total_mass = compute_molar_mass(atom_counts, self.elements)
            composition = compute_percent_composition(atom_counts, self.elements)
        except (FormulaError, Exception) as exc:
            self.result_label.setText(f"<b>{self._error_prefix}:</b> {exc}")
            return

        lines = [f"<b>{formula}</b>"]
        lines.append(f"<br>Molar mass: <b>{total_mass:.4f} g/mol</b><br>")
        lines.append("<table style='margin-top:6px;'>")
        lines.append(
            "<tr><th align='left'>Element</th>"
            "<th align='right'>Count</th>"
            "<th align='right'>Mass (g/mol)</th>"
            "<th align='right'>%</th></tr>"
        )
        for entry in composition:
            lines.append(
                f"<tr><td>{entry['symbol']}</td>"
                f"<td align='right'>{entry['count']}</td>"
                f"<td align='right'>{entry['mass']:.4f}</td>"
                f"<td align='right'>{entry['percent']:.2f}%</td></tr>"
            )
        lines.append("</table>")
        self.result_label.setText("".join(lines))
