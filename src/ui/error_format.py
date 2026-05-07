"""Localize parser error messages from the domain layer.

Domain exceptions (:class:`FormulaError`, :class:`EquationError`) carry an
optional ``code`` and ``params`` dict. This module maps codes to localization
keys and formats them with the translator callable supplied by the UI. The
English message on the exception remains the fallback when a code is missing
or unknown so users never see an empty error in production.
"""

from src.domain.molar_mass import FormulaError
from src.domain.stoichiometry import EquationError

_FORMULA_ERROR_KEYS: dict[str, str] = {
    "empty": "formula_error_empty",
    "hydrate_malformed": "formula_error_hydrate_malformed",
    "hydrate_no_formula": "formula_error_hydrate_no_formula",
    "unmatched_close": "formula_error_unmatched_close",
    "unmatched_open": "formula_error_unmatched_open",
    "unexpected_char": "formula_error_unexpected_char",
    "no_elements": "formula_error_no_elements",
    "unknown_symbol": "formula_error_unknown_symbol",
}

_EQUATION_ERROR_KEYS: dict[str, str] = {
    "empty": "equation_error_empty",
    "no_separator": "equation_error_no_separator",
    "one_separator": "equation_error_one_separator",
    "both_sides": "equation_error_both_sides",
    "invalid_compound": "equation_error_invalid_compound",
    "cannot_balance": "equation_error_cannot_balance",
    "under_determined": "equation_error_under_determined",
    "zero_coefficient": "equation_error_zero_coefficient",
    "compound_not_found": "equation_error_compound_not_found",
}


def _format(exc, translate, code_to_key):
    """Look up the localized message for ``exc``, else fall back to its text."""
    code = getattr(exc, "code", None)
    key = code_to_key.get(code) if code else None
    if key is None or translate is None:
        return str(exc)
    params = getattr(exc, "params", None) or {}
    try:
        translated = translate(key, **params)
    except Exception:
        return str(exc)
    if not translated or translated == key:
        return str(exc)
    return translated


def format_formula_error(exc: FormulaError, translate) -> str:
    """Return a localized message for a :class:`FormulaError`."""
    return _format(exc, translate, _FORMULA_ERROR_KEYS)


def format_equation_error(exc: EquationError, translate) -> str:
    """Return a localized message for an :class:`EquationError`.

    When the equation error wraps a :class:`FormulaError` (compound failed to
    parse), the inner formula error is localized first and substituted into
    the ``detail`` parameter so the whole chain is presented in the user's
    language rather than mixing English with the localized prefix.
    """
    if isinstance(exc, FormulaError):
        return format_formula_error(exc, translate)
    cause = exc.__cause__
    if (
        getattr(exc, "code", None) == "invalid_compound"
        and isinstance(cause, FormulaError)
        and translate is not None
    ):
        localized_detail = format_formula_error(cause, translate)
        params = dict(getattr(exc, "params", None) or {})
        params["detail"] = localized_detail
        try:
            translated = translate(_EQUATION_ERROR_KEYS["invalid_compound"], **params)
        except Exception:
            return str(exc)
        if translated and translated != _EQUATION_ERROR_KEYS["invalid_compound"]:
            return translated
    return _format(exc, translate, _EQUATION_ERROR_KEYS)
