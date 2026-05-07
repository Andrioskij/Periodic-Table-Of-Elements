"""Cover the UI-side translator helpers for parser errors."""

import unittest

from src.domain.molar_mass import FormulaError
from src.domain.stoichiometry import EquationError
from src.ui.error_format import format_equation_error, format_formula_error


def _fake_translator(table):
    """Build a translator that returns localized strings from a fixed mapping."""

    def translate(key, **kwargs):
        template = table.get(key)
        if template is None:
            return key
        return template.format(**kwargs) if kwargs else template

    return translate


class TestFormatFormulaError(unittest.TestCase):

    def test_localizes_known_code_with_params(self):
        translate = _fake_translator({
            "formula_error_unexpected_char": (
                "Carattere inatteso '{char}' alla posizione {position} "
                "nella formula '{formula}'."
            ),
        })
        exc = FormulaError(
            "boom",
            code="unexpected_char",
            params={"char": "@", "position": 2, "formula": "H2@O"},
        )
        result = format_formula_error(exc, translate)
        self.assertEqual(
            result,
            "Carattere inatteso '@' alla posizione 2 nella formula 'H2@O'.",
        )

    def test_falls_back_to_english_for_unknown_code(self):
        exc = FormulaError("Mysterious failure", code="something_new")
        translate = _fake_translator({})
        self.assertEqual(format_formula_error(exc, translate), "Mysterious failure")

    def test_falls_back_when_translator_is_none(self):
        exc = FormulaError("Empty formula", code="empty")
        self.assertEqual(format_formula_error(exc, None), "Empty formula")

    def test_falls_back_when_translation_missing(self):
        # Translator returns the key itself (the in-app fallback) — caller
        # should still get the English message rather than the raw key.
        translate = _fake_translator({})
        exc = FormulaError("Empty formula", code="empty")
        self.assertEqual(format_formula_error(exc, translate), "Empty formula")

    def test_handles_exception_without_code(self):
        exc = FormulaError("legacy message")
        translate = _fake_translator({"formula_error_empty": "ignored"})
        self.assertEqual(format_formula_error(exc, translate), "legacy message")


class TestFormatEquationError(unittest.TestCase):

    def test_localizes_invalid_compound_with_params(self):
        translate = _fake_translator({
            "equation_error_invalid_compound": "Composto non valido '{compound}': {detail}",
        })
        exc = EquationError(
            "Invalid compound 'Ca(': Unmatched opening parenthesis",
            code="invalid_compound",
            params={"compound": "Ca(", "detail": "Unmatched opening parenthesis"},
        )
        self.assertEqual(
            format_equation_error(exc, translate),
            "Composto non valido 'Ca(': Unmatched opening parenthesis",
        )

    def test_falls_back_to_english_for_unknown_code(self):
        exc = EquationError("oops", code="future_code")
        self.assertEqual(format_equation_error(exc, _fake_translator({})), "oops")

    def test_routes_formula_error_through_formula_mapping(self):
        # FormulaError is a subclass of EquationError? No — but the helper still
        # routes it to the formula-error mapping when a caller mistakenly
        # passes one. This guards against ordering bugs in panels' except clauses.
        translate = _fake_translator({
            "formula_error_empty": "Formula vuota.",
        })
        exc = FormulaError("Empty formula", code="empty")
        self.assertEqual(format_equation_error(exc, translate), "Formula vuota.")

    def test_invalid_compound_localizes_nested_formula_detail(self):
        translate = _fake_translator({
            "equation_error_invalid_compound": "Composto non valido '{compound}': {detail}",
            "formula_error_unmatched_open": "Parentesi aperta non chiusa nella formula.",
        })
        try:
            raise FormulaError(
                "Unmatched opening parenthesis in formula",
                code="unmatched_open",
            )
        except FormulaError as inner:
            try:
                raise EquationError(
                    "Invalid compound 'Ca(': Unmatched opening parenthesis in formula",
                    code="invalid_compound",
                    params={"compound": "Ca(", "detail": str(inner)},
                ) from inner
            except EquationError as outer:
                exc = outer
        result = format_equation_error(exc, translate)
        self.assertEqual(
            result,
            "Composto non valido 'Ca(': Parentesi aperta non chiusa nella formula.",
        )


if __name__ == "__main__":
    unittest.main()
