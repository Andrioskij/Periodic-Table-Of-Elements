"""Shared modal that explains how a calculator works.

Used by `MolarMassPanel`, `StoichiometryPanel`, `CompoundBuilderPanel`
and `SolubilityPanel` — each anchors a "?" `QToolButton` next to its
title that opens this dialog with the panel-specific body text.

The body is plain text with `\\n\\n` paragraph breaks and backtick-
delimited inline code (matching the convention used by the web
`*_help_body` localization keys). `format_help_body()` converts it to
Qt rich text (`<p>` + `<code>`) for rendering in a `QLabel`.

Mirrors the web `#help-modal` introduced in PR #72 — same content
keys (`*_help_body`), same plain-text → paragraph rendering, same
visual idea (modal popup, title at top, scrollable body, close button).
"""

import html
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)


def format_help_body(text):
    """Convert plain-text help body into Qt rich text.

    Splits paragraphs on blank lines, wraps each in `<p>`, and replaces
    backtick-delimited inline `` `code` `` with `<code>` tags. HTML
    special chars are escaped before processing so a stray `<` in a
    translation can't break the layout (or smuggle markup).
    """
    if not text:
        return ""
    paragraphs = text.split("\n\n")
    rendered = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        escaped = html.escape(paragraph)
        with_code = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
        rendered.append(f"<p>{with_code}</p>")
    return "".join(rendered)


class HelpDialog(QDialog):
    """Modal popup that displays one calculator's help body.

    Constructed on-demand from the panel's stored `_help_title` and
    `_help_body` strings, so the dialog always reflects the current
    UI language without needing to retain a long-lived instance.
    """

    def __init__(self, *, title, body_text, close_button_text="Close", parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(440)
        self.resize(520, 380)
        self.setWindowTitle(title)
        self.setAccessibleName("Help Dialog")

        if parent is not None:
            self.setWindowIcon(parent.windowIcon())

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("compoundTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Help dialog title")

        self.body_label = QLabel(format_help_body(body_text))
        self.body_label.setTextFormat(Qt.RichText)
        self.body_label.setWordWrap(True)
        self.body_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body_label.setAccessibleName("Help dialog body")

        body_scroll = QScrollArea()
        body_scroll.setWidget(self.body_label)
        body_scroll.setWidgetResizable(True)
        body_scroll.setFrameShape(QFrame.NoFrame)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.addStretch(1)

        self.close_button = QPushButton(close_button_text)
        self.close_button.setObjectName("panelMiniButton")
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.accept)
        button_row.addWidget(self.close_button)

        layout.addWidget(self.title_label)
        layout.addWidget(body_scroll, 1)
        layout.addLayout(button_row)
        self.setLayout(layout)
