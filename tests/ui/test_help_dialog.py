"""Unit tests for `HelpDialog` and the `format_help_body` helper.

Covers the plain-text → Qt rich-text conversion (paragraph splitting,
backtick → `<code>`, HTML escape) and the dialog's instantiation
contract: title in titlebar + body label, close button wired to accept.
"""

import sys
import unittest

from PySide6.QtWidgets import QApplication

from src.ui.help_dialog import HelpDialog, format_help_body

_app = QApplication.instance() or QApplication(sys.argv)


class TestFormatHelpBody(unittest.TestCase):
    def test_empty_input_returns_empty_string(self):
        self.assertEqual(format_help_body(""), "")
        self.assertEqual(format_help_body(None), "")

    def test_single_paragraph_wrapped_in_p(self):
        self.assertEqual(format_help_body("Hello world"), "<p>Hello world</p>")

    def test_double_newline_splits_into_paragraphs(self):
        result = format_help_body("First line.\n\nSecond line.")
        self.assertEqual(result, "<p>First line.</p><p>Second line.</p>")

    def test_blank_paragraphs_are_skipped(self):
        result = format_help_body("One.\n\n\n\nTwo.")
        self.assertEqual(result, "<p>One.</p><p>Two.</p>")

    def test_backtick_code_extracted_to_code_tag(self):
        result = format_help_body("Enter `H2O` to compute mass.")
        self.assertEqual(result, "<p>Enter <code>H2O</code> to compute mass.</p>")

    def test_html_special_chars_are_escaped(self):
        # The < and > would otherwise be parsed as broken tags by QLabel.
        result = format_help_body("Compare H<O and H>O.")
        self.assertEqual(result, "<p>Compare H&lt;O and H&gt;O.</p>")

    def test_ampersand_is_escaped(self):
        result = format_help_body("Acids & bases")
        self.assertEqual(result, "<p>Acids &amp; bases</p>")

    def test_code_with_special_chars_inside_is_escaped(self):
        # The <, >, & inside backticks should still be escaped (escape
        # happens before backtick extraction, so the contents of
        # <code>...</code> are the escaped string).
        result = format_help_body("Pattern: `a < b & c > d`.")
        self.assertEqual(
            result,
            "<p>Pattern: <code>a &lt; b &amp; c &gt; d</code>.</p>",
        )


class TestHelpDialog(unittest.TestCase):
    def setUp(self):
        self.dialog = HelpDialog(
            title="Molar mass",
            body_text="Computes the molar mass.\n\nEnter `H2O`.",
            close_button_text="Close",
        )

    def tearDown(self):
        self.dialog.deleteLater()

    def test_window_title_set_from_constructor(self):
        self.assertEqual(self.dialog.windowTitle(), "Molar mass")

    def test_title_label_renders_constructor_title(self):
        self.assertEqual(self.dialog.title_label.text(), "Molar mass")

    def test_body_label_contains_formatted_html(self):
        # Verify both paragraphs and the inline <code> made it through.
        body = self.dialog.body_label.text()
        self.assertIn("Computes the molar mass.", body)
        self.assertIn("<code>H2O</code>", body)

    def test_close_button_text_from_constructor(self):
        self.assertEqual(self.dialog.close_button.text(), "Close")

    def test_close_button_is_default(self):
        # ENTER closes the dialog out of the box.
        self.assertTrue(self.dialog.close_button.isDefault())

    def test_dialog_is_modal(self):
        self.assertTrue(self.dialog.isModal())

    def test_close_button_accepts_dialog(self):
        # The accept signal flips dialog result to Accepted; verify the
        # button is wired by clicking it and checking that result.
        self.dialog.close_button.click()
        from PySide6.QtWidgets import QDialog
        self.assertEqual(self.dialog.result(), QDialog.Accepted)


if __name__ == "__main__":
    unittest.main()
