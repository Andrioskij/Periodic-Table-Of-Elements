from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class CompoundBuilderPanel(QWidget):
    """Top-area panel where the user selects two elements and their oxidation states.

    Contains slot cards for element A and B with inline search fields,
    oxidation-state combo boxes, and action buttons to calculate the
    formula or reset the selection.
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("compoundBuilderPanel")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.builder_title_label = QLabel()
        self.builder_title_label.setObjectName("builderTitleLabel")
        self.builder_scope_label = QLabel()
        self.builder_scope_label.setObjectName("builderScopeLabel")
        self.builder_scope_label.setWordWrap(True)

        self.selection_summary_card = QWidget()
        self.selection_summary_card.setObjectName("builderSelectionCard")
        self.selection_summary_card.setAttribute(Qt.WA_StyledBackground, True)
        selection_summary_layout = QHBoxLayout()
        selection_summary_layout.setContentsMargins(6, 6, 6, 6)
        selection_summary_layout.setSpacing(4)
        self.current_selection_title_label = QLabel()
        self.current_selection_title_label.setObjectName("builderSelectionTitleLabel")
        self.current_selection_value_label = QLabel()
        self.current_selection_value_label.setObjectName("builderSelectionValueLabel")
        self.builder_guide_label = QLabel()
        self.builder_guide_label.setObjectName("builderGuideLabel")
        self.builder_guide_label.setWordWrap(True)
        self.builder_guide_label.hide()
        selection_summary_layout.addWidget(self.current_selection_title_label, 0)
        selection_summary_layout.addWidget(self.current_selection_value_label, 1)
        self.selection_summary_card.setLayout(selection_summary_layout)

        self.selector_cards_layout = QHBoxLayout()
        self.selector_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.selector_cards_layout.setSpacing(6)

        self.selector_a_widget = QWidget()
        self.selector_a_widget.setObjectName("builderSelectorCard")
        self.selector_a_widget.setAttribute(Qt.WA_StyledBackground, True)
        selector_a_layout = QVBoxLayout()
        selector_a_layout.setContentsMargins(6, 6, 6, 6)
        selector_a_layout.setSpacing(3)
        selector_a_header = QHBoxLayout()
        selector_a_header.setContentsMargins(0, 0, 0, 0)
        selector_a_header.setSpacing(6)
        self.selector_a_badge_label = QLabel("A")
        self.selector_a_badge_label.setObjectName("builderSlotBadgeLabel")
        self.selector_a_title_label = QLabel()
        self.selector_a_title_label.setObjectName("builderSlotTitleLabel")
        selector_a_header.addWidget(self.selector_a_badge_label, 0)
        selector_a_header.addWidget(self.selector_a_title_label, 1)
        self.selector_a_summary_label = QLabel()
        self.selector_a_summary_label.setObjectName("builderSelectorSummaryLabel")
        self.search_a_input = QLineEdit()
        self.search_a_input.setObjectName("builderSearchInput")
        self.search_a_input.setAccessibleName("Search element A")
        selector_a_header.addWidget(self.search_a_input, 1)
        self.a_oxidation_label = QLabel()
        self.a_oxidation_label.setObjectName("builderSelectorCaptionLabel")
        self.a_oxidation_combo = QComboBox()
        a_oxidation_row = QHBoxLayout()
        a_oxidation_row.setContentsMargins(0, 0, 0, 0)
        a_oxidation_row.setSpacing(6)
        a_oxidation_row.addWidget(self.a_oxidation_label)
        a_oxidation_row.addWidget(self.a_oxidation_combo)
        selector_a_layout.addLayout(selector_a_header)
        selector_a_layout.addWidget(self.selector_a_summary_label)
        selector_a_layout.addLayout(a_oxidation_row)
        self.selector_a_widget.setLayout(selector_a_layout)

        self.selector_b_widget = QWidget()
        self.selector_b_widget.setObjectName("builderSelectorCard")
        self.selector_b_widget.setAttribute(Qt.WA_StyledBackground, True)
        selector_b_layout = QVBoxLayout()
        selector_b_layout.setContentsMargins(6, 6, 6, 6)
        selector_b_layout.setSpacing(3)
        selector_b_header = QHBoxLayout()
        selector_b_header.setContentsMargins(0, 0, 0, 0)
        selector_b_header.setSpacing(6)
        self.selector_b_badge_label = QLabel("B")
        self.selector_b_badge_label.setObjectName("builderSlotBadgeLabel")
        self.selector_b_title_label = QLabel()
        self.selector_b_title_label.setObjectName("builderSlotTitleLabel")
        selector_b_header.addWidget(self.selector_b_badge_label, 0)
        selector_b_header.addWidget(self.selector_b_title_label, 1)
        self.selector_b_summary_label = QLabel()
        self.selector_b_summary_label.setObjectName("builderSelectorSummaryLabel")
        self.search_b_input = QLineEdit()
        self.search_b_input.setObjectName("builderSearchInput")
        self.search_b_input.setAccessibleName("Search element B")
        selector_b_header.addWidget(self.search_b_input, 1)
        self.b_oxidation_label = QLabel()
        self.b_oxidation_label.setObjectName("builderSelectorCaptionLabel")
        self.b_oxidation_combo = QComboBox()
        b_oxidation_row = QHBoxLayout()
        b_oxidation_row.setContentsMargins(0, 0, 0, 0)
        b_oxidation_row.setSpacing(6)
        b_oxidation_row.addWidget(self.b_oxidation_label)
        b_oxidation_row.addWidget(self.b_oxidation_combo)
        selector_b_layout.addLayout(selector_b_header)
        selector_b_layout.addWidget(self.selector_b_summary_label)
        selector_b_layout.addLayout(b_oxidation_row)
        self.selector_b_widget.setLayout(selector_b_layout)

        self.selector_cards_layout.addWidget(self.selector_a_widget)
        self.selector_cards_layout.addWidget(self.selector_b_widget)

        self.builder_actions_widget = QWidget()
        self.action_buttons_layout = QHBoxLayout()
        self.action_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.action_buttons_layout.setSpacing(6)
        self.build_button = QPushButton()
        self.build_button.setObjectName("builderButton")

        self.builder_reset_button = QPushButton()
        self.builder_reset_button.setObjectName("builderResetButton")

        self.builder_status_label = QLabel("")
        self.builder_status_label.setObjectName("builderStatusLabel")
        self.builder_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.builder_status_label.setMinimumWidth(0)
        self.builder_status_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.builder_status_label.setWordWrap(False)
        self.action_buttons_layout.addWidget(self.build_button)
        self.action_buttons_layout.addStretch(1)
        self.action_buttons_layout.addWidget(self.builder_reset_button)
        self.action_buttons_layout.addWidget(self.builder_status_label)
        self.builder_actions_widget.setLayout(self.action_buttons_layout)

        layout.addWidget(self.builder_title_label)
        layout.addWidget(self.builder_scope_label)
        layout.addWidget(self.selection_summary_card)
        layout.addLayout(self.selector_cards_layout)
        layout.addWidget(self.builder_actions_widget)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def apply_language(
        self,
        *,
        builder_title,
        scope_note,
        selection_title,
        selection_hint,
        selector_a_title,
        selector_b_title,
        search_placeholder_a,
        search_placeholder_b,
        oxidation_first,
        oxidation_second,
        calculate_formula,
        reset,
    ):
        self.builder_title_label.setText(builder_title)
        self.builder_scope_label.setText(scope_note)
        self.current_selection_title_label.setText(f"{selection_title}:")
        self.builder_guide_label.setText(selection_hint)
        self.selector_a_title_label.setText(selector_a_title)
        self.selector_b_title_label.setText(selector_b_title)
        self.search_a_input.setPlaceholderText(search_placeholder_a)
        self.search_b_input.setPlaceholderText(search_placeholder_b)
        self.a_oxidation_label.setText(oxidation_first)
        self.b_oxidation_label.setText(oxidation_second)
        self.build_button.setText(calculate_formula)
        self.builder_reset_button.setText(reset)

    def set_current_selection_text(self, text):
        self.current_selection_value_label.setText(text)

    def set_selector_texts(self, first_text, second_text):
        self.selector_a_summary_label.setText(first_text)
        self.selector_b_summary_label.setText(second_text)

    def set_status_text(self, text):
        self.builder_status_label.setText(text)
        self.builder_status_label.setToolTip(text)


class CompoundPanel(QWidget):
    """Right-side panel that displays the calculated compound formula and nomenclature.

    Shows the result of the compound builder: binary formula, IUPAC
    Stock name, traditional name, and any common compounds for the
    selected element pair.
    """

    def __init__(self, title_text, prompt_text, scope_note_text=""):
        super().__init__()
        self.setObjectName("compoundPanel")
        self.setFocusPolicy(Qt.StrongFocus)

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("compoundTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Compound panel title")

        self.scope_label = QLabel(scope_note_text)
        self.scope_label.setObjectName("compoundScopeLabel")
        self.scope_label.setWordWrap(True)
        self.scope_label.setAccessibleName("Compound panel scope")

        self.result_label = QLabel(prompt_text)
        self.result_label.setObjectName("compoundResultLabel")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setWordWrap(True)
        self.result_label.setAccessibleName("Compound panel result")
        self.result_label.setAccessibleDescription("Shows calculated formula and nomenclature.")
        self.result_label.setObjectName("compoundResultLabel")
        self.result_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.result_label.setWordWrap(True)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setAccessibleName("Compound Panel")
        self.setAccessibleDescription("Displays mixture formula and nomenclature details.")

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.scope_label)
        card_layout.addWidget(self.result_label)
        self.card_widget.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

    def set_title(self, text):
        self.title_label.setText(text)

    def set_prompt(self, text):
        self.result_label.setText(text)

    def set_scope_note(self, text):
        self.scope_label.setText(text)

    def set_result_text(self, text):
        self.result_label.setText(text)
