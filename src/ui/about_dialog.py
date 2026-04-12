from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app_metadata import APP_DISPLAY_NAME, APP_VERSION


class AboutDialog(QDialog):
    def __init__(self, *, translate, parent=None):
        super().__init__(parent)
        self._translate = translate

        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(460)
        self.resize(540, 420)

        if parent is not None:
            self.setWindowIcon(parent.windowIcon())

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.summary_card = QWidget()
        self.summary_card.setObjectName("sidePanelCard")
        self.summary_card.setAttribute(Qt.WA_StyledBackground, True)
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(6)

        self.app_name_label = QLabel(APP_DISPLAY_NAME)
        self.app_name_label.setObjectName("builderTitleLabel")
        self.version_label = QLabel()
        self.version_label.setObjectName("infoFooterLabel")
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)

        summary_layout.addWidget(self.app_name_label)
        summary_layout.addWidget(self.version_label)
        summary_layout.addWidget(self.description_label)
        self.summary_card.setLayout(summary_layout)

        self.help_card, self.help_title_label, self.help_body_label = self._build_section_card()
        self.limits_card, self.limits_title_label, self.limits_body_label = self._build_section_card()

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.addStretch()

        self.close_button = QPushButton()
        self.close_button.setObjectName("panelMiniButton")
        self.close_button.clicked.connect(self.accept)
        button_row.addWidget(self.close_button)

        layout.addWidget(self.summary_card)
        layout.addWidget(self.help_card)
        layout.addWidget(self.limits_card)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.apply_language()

    def _build_section_card(self):
        card = QWidget()
        card.setObjectName("sidePanelCard")
        card.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title_label = QLabel()
        title_label.setObjectName("compoundTitleLabel")

        body_label = QLabel()
        body_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        body_label.setWordWrap(True)
        body_label.setTextFormat(Qt.PlainText)

        layout.addWidget(title_label)
        layout.addWidget(body_label)
        card.setLayout(layout)

        return card, title_label, body_label

    def apply_language(self):
        self.setWindowTitle(self._translate("about_dialog_title", app_name=APP_DISPLAY_NAME))
        self.version_label.setText(self._translate("about_version", version=APP_VERSION))
        self.description_label.setText(self._translate("about_description"))
        self.help_title_label.setText(self._translate("quick_help_title"))
        self.help_body_label.setText(self._translate("quick_help_body"))
        self.limits_title_label.setText(self._translate("current_limits_title"))
        self.limits_body_label.setText(self._translate("current_limits_body"))
        self.close_button.setText(self._translate("close_dialog"))
