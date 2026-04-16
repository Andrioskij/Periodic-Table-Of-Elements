"""Right-side panel for the stoichiometric equation balancer."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.domain.molar_mass import FormulaError
from src.domain.stoichiometry import (
    EquationError,
    balance_equation,
    compute_stoichiometric_masses,
    format_balanced_equation,
    parse_equation,
)


class StoichiometryPanel(QWidget):
    """Right-side panel that balances chemical equations and computes masses.

    The user enters an unbalanced equation (e.g. Fe + O2 -> Fe2O3),
    clicks Balance to get the balanced form, then optionally enters a
    mass for one compound to compute all stoichiometric quantities.
    """

    def __init__(self, title_text, prompt_text, elements):
        super().__init__()
        self.elements = elements
        self._current_reactants = []
        self._current_products = []
        self._current_coefficients = []
        self.setObjectName("stoichiometryPanel")
        self.setFocusPolicy(Qt.StrongFocus)

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("compoundTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Stoichiometry panel title")

        self.equation_input = QLineEdit()
        self.equation_input.setObjectName("molarMassInput")
        self.equation_input.setPlaceholderText("Fe + O2 -> Fe2O3")
        self.equation_input.setAccessibleName("Chemical equation input")

        self.balance_button = QPushButton()
        self.balance_button.setObjectName("builderButton")
        self.balance_button.setAccessibleName("Balance equation")
        self.balance_button.clicked.connect(self._on_balance)
        self.equation_input.returnPressed.connect(self._on_balance)

        eq_row = QHBoxLayout()
        eq_row.setContentsMargins(0, 0, 0, 0)
        eq_row.setSpacing(6)
        eq_row.addWidget(self.equation_input, 1)
        eq_row.addWidget(self.balance_button, 0)

        self.result_label = QLabel(prompt_text)
        self.result_label.setObjectName("compoundResultLabel")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setWordWrap(True)
        self.result_label.setAccessibleName("Balanced equation result")
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Mass calculation section
        self.mass_section = QWidget()
        self.mass_section.setVisible(False)

        self.compound_combo = QComboBox()
        self.compound_combo.setAccessibleName("Select compound")

        self.mass_input = QLineEdit()
        self.mass_input.setObjectName("molarMassInput")
        self.mass_input.setPlaceholderText("10.0")
        self.mass_input.setAccessibleName("Mass in grams")
        self.mass_input.setMaximumWidth(120)

        self.mass_unit_label = QLabel("g")
        self.mass_unit_label.setObjectName("compoundResultLabel")

        self.calc_mass_button = QPushButton()
        self.calc_mass_button.setObjectName("builderButton")
        self.calc_mass_button.setAccessibleName("Calculate masses")
        self.calc_mass_button.clicked.connect(self._on_calc_masses)
        self.mass_input.returnPressed.connect(self._on_calc_masses)

        mass_row = QHBoxLayout()
        mass_row.setContentsMargins(0, 0, 0, 0)
        mass_row.setSpacing(6)
        mass_row.addWidget(self.compound_combo, 1)
        mass_row.addWidget(self.mass_input, 0)
        mass_row.addWidget(self.mass_unit_label, 0)
        mass_row.addWidget(self.calc_mass_button, 0)

        mass_layout = QVBoxLayout()
        mass_layout.setContentsMargins(0, 6, 0, 0)
        mass_layout.setSpacing(4)
        self.mass_section_label = QLabel()
        self.mass_section_label.setObjectName("compoundResultLabel")
        self.mass_section_label.setWordWrap(True)
        mass_layout.addWidget(self.mass_section_label)
        mass_layout.addLayout(mass_row)
        self.mass_section.setLayout(mass_layout)

        self.mass_result_label = QLabel()
        self.mass_result_label.setObjectName("compoundResultLabel")
        self.mass_result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.mass_result_label.setWordWrap(True)
        self.mass_result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.mass_result_label.setVisible(False)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setAccessibleName("Stoichiometry Panel")
        self.setAccessibleDescription("Balances equations and calculates stoichiometric masses.")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addLayout(eq_row)
        card_layout.addWidget(self.result_label)
        card_layout.addWidget(self.mass_section)
        card_layout.addWidget(self.mass_result_label)
        self.card_widget.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

        self._balance_label = "Balance"
        self._calc_masses_label = "Calculate masses"
        self._mass_section_text = "Enter mass for a compound:"
        self._error_prefix = "Error"

    def set_title(self, text):
        """Update the panel title."""
        self.title_label.setText(text)

    def set_prompt(self, text, prompt_text=None):
        """Show a prompt message in the result area."""
        self.result_label.setText(prompt_text if prompt_text is not None else text)
        self.mass_section.setVisible(False)
        self.mass_result_label.setVisible(False)

    def apply_language(
        self, *, title, prompt, balance_text, calc_masses_text,
        mass_section_text, error_prefix
    ):
        """Apply localized strings to all visible labels."""
        self.set_title(title)
        self.set_prompt(prompt)
        self._balance_label = balance_text
        self.balance_button.setText(balance_text)
        self._calc_masses_label = calc_masses_text
        self.calc_mass_button.setText(calc_masses_text)
        self._mass_section_text = mass_section_text
        self.mass_section_label.setText(mass_section_text)
        self._error_prefix = error_prefix

    def _on_balance(self):
        """Parse and balance the equation, then show results."""
        equation = self.equation_input.text().strip()
        if not equation:
            return

        try:
            reactants, products = parse_equation(equation)
            coefficients = balance_equation(equation)
            balanced = format_balanced_equation(reactants, products, coefficients)
        except (EquationError, FormulaError, Exception) as exc:
            self.result_label.setText(f"<b>{self._error_prefix}:</b> {exc}")
            self.mass_section.setVisible(False)
            self.mass_result_label.setVisible(False)
            return

        self._current_reactants = reactants
        self._current_products = products
        self._current_coefficients = coefficients

        self.result_label.setText(f"<b>{balanced}</b>")

        # Populate compound combo
        self.compound_combo.clear()
        for compound in reactants + products:
            self.compound_combo.addItem(compound)

        self.mass_section_label.setText(self._mass_section_text)
        self.mass_section.setVisible(True)
        self.mass_result_label.setVisible(False)
        self.mass_input.clear()

    def _on_calc_masses(self):
        """Compute stoichiometric masses for the selected compound."""
        mass_text = self.mass_input.text().strip()
        if not mass_text:
            return

        try:
            mass_grams = float(mass_text)
        except ValueError:
            self.mass_result_label.setText(
                f"<b>{self._error_prefix}:</b> Invalid number."
            )
            self.mass_result_label.setVisible(True)
            return

        compound = self.compound_combo.currentText()
        if not compound:
            return

        try:
            result = compute_stoichiometric_masses(
                self._current_reactants,
                self._current_products,
                self._current_coefficients,
                self.elements,
                given_compound=compound,
                given_mass_grams=mass_grams,
            )
        except (EquationError, FormulaError, Exception) as exc:
            self.mass_result_label.setText(f"<b>{self._error_prefix}:</b> {exc}")
            self.mass_result_label.setVisible(True)
            return

        lines = ["<table style='margin-top:6px;'>"]
        lines.append(
            "<tr><th align='left'>Compound</th>"
            "<th align='right'>Coeff.</th>"
            "<th align='right'>M (g/mol)</th>"
            "<th align='right'>Moles</th>"
            "<th align='right'>Mass (g)</th></tr>"
        )
        for entry in result:
            lines.append(
                f"<tr><td>{entry['compound']}</td>"
                f"<td align='right'>{entry['coefficient']}</td>"
                f"<td align='right'>{entry['molar_mass']:.2f}</td>"
                f"<td align='right'>{entry['moles']:.4f}</td>"
                f"<td align='right'>{entry['mass']:.4f}</td></tr>"
            )
        lines.append("</table>")
        self.mass_result_label.setText("".join(lines))
        self.mass_result_label.setVisible(True)
