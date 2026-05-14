"""Parse chemical formulas and compute molar masses and percent composition.

FormulaError codes (used by the UI to look up localized messages):
- ``empty``: formula is empty / whitespace-only.
- ``hydrate_malformed``: hydrate notation has an empty segment. Params: ``formula``.
- ``hydrate_no_formula``: hydrate multiplier without trailing formula. Params: ``formula``.
- ``unmatched_close``: unmatched closing parenthesis. Params: ``position``.
- ``unexpected_char``: unexpected character at position. Params: ``char``, ``position``, ``formula``.
- ``unmatched_open``: unmatched opening parenthesis.
- ``no_elements``: formula parsed without producing any element. Params: ``formula``.
- ``unknown_symbol``: element symbol not in dataset. Params: ``symbol``.
- ``empirical_empty``: empirical-formula composition received no rows.
- ``invalid_amount``: empirical-formula row has a non-positive amount. Params: ``symbol``.
"""


class FormulaError(ValueError):
    """Raised when a chemical formula cannot be parsed or contains unknown symbols.

    Carries an optional ``code`` and ``params`` dict so the UI layer can map
    them to a localized message via :func:`src.ui.error_format.format_formula_error`.
    The English ``message`` remains the fallback when no translation is available.
    """

    def __init__(self, message: str, *, code: str | None = None, params: dict | None = None):
        super().__init__(message)
        self.code = code
        self.params = params or {}


def parse_formula(formula: str) -> dict[str, int]:
    """Parse a chemical formula and return {symbol: atom_count}.

    Handles simple formulas (H2O), parentheses with multipliers Ca(OH)2,
    nested parentheses Mg3(PO4)2, implicit count of 1, and crystalline
    hydrate notation using `·` (U+00B7) or `.` as the separator
    (e.g. CuSO4·5H2O, Na2CO3.10H2O).

    Raises FormulaError on empty input, invalid characters, malformed
    parentheses, or malformed hydrate notation.
    """
    if not formula or not formula.strip():
        raise FormulaError("Empty formula", code="empty")

    formula = formula.strip()

    if "·" in formula or "." in formula:
        return _parse_hydrate(formula)

    return _parse_simple(formula)


def _parse_hydrate(formula: str) -> dict[str, int]:
    """Parse a hydrate-notation formula like CuSO4·5H2O.

    The first segment must be a plain formula; subsequent segments may carry
    an optional integer multiplier prefix (e.g. `5H2O`).
    """
    normalized = formula.replace("·", ".")
    parts = [p.strip() for p in normalized.split(".")]
    if any(not p for p in parts):
        raise FormulaError(
            f"Malformed hydrate notation in '{formula}'",
            code="hydrate_malformed",
            params={"formula": formula},
        )

    merged: dict[str, int] = {}
    for idx, part in enumerate(parts):
        multiplier = 1
        sub = part
        if idx > 0:
            k = 0
            while k < len(sub) and sub[k].isdigit():
                k += 1
            if k > 0:
                multiplier = int(sub[:k])
                sub = sub[k:]
                if not sub:
                    raise FormulaError(
                        f"Hydrate multiplier without formula in '{formula}'",
                        code="hydrate_no_formula",
                        params={"formula": formula},
                    )
        atoms = _parse_simple(sub)
        for symbol, count in atoms.items():
            merged[symbol] = merged.get(symbol, 0) + count * multiplier

    return merged


def _parse_simple(formula: str) -> dict[str, int]:
    """Parse a non-hydrate formula segment with the stack-based algorithm."""
    stack: list[dict[str, int]] = [{}]
    i = 0
    n = len(formula)

    while i < n:
        ch = formula[i]

        if ch == '(':
            stack.append({})
            i += 1

        elif ch == ')':
            if len(stack) < 2:
                raise FormulaError(
                    f"Unmatched closing parenthesis at position {i}",
                    code="unmatched_close",
                    params={"position": i},
                )
            i += 1
            # Read the multiplier after ')'
            num_start = i
            while i < n and formula[i].isdigit():
                i += 1
            multiplier = int(formula[num_start:i]) if i > num_start else 1

            top = stack.pop()
            for symbol, count in top.items():
                stack[-1][symbol] = stack[-1].get(symbol, 0) + count * multiplier

        elif ch.isupper():
            # Read element symbol: uppercase followed by at most one lowercase
            symbol = ch
            i += 1
            if i < n and formula[i].islower():
                symbol += formula[i]
                i += 1
            # Read count
            num_start = i
            while i < n and formula[i].isdigit():
                i += 1
            count = int(formula[num_start:i]) if i > num_start else 1

            stack[-1][symbol] = stack[-1].get(symbol, 0) + count

        else:
            raise FormulaError(
                f"Unexpected character '{ch}' at position {i} in formula '{formula}'",
                code="unexpected_char",
                params={"char": ch, "position": i, "formula": formula},
            )

    if len(stack) != 1:
        raise FormulaError(
            "Unmatched opening parenthesis in formula",
            code="unmatched_open",
        )

    if not stack[0]:
        raise FormulaError(
            f"No elements found in formula '{formula}'",
            code="no_elements",
            params={"formula": formula},
        )

    return stack[0]


def _find_element_by_symbol(symbol: str, elements: list[dict]) -> dict | None:
    """Find an element record by its symbol (case-sensitive)."""
    for el in elements:
        if el.get("symbol") == symbol:
            return el
    return None


def compute_molar_mass(atom_counts: dict[str, int], elements: list[dict]) -> float:
    """Compute the molar mass in g/mol by summing atomic_mass * count.

    Raises FormulaError if a symbol is not found in the elements dataset.
    """
    total = 0.0
    for symbol, count in atom_counts.items():
        el = _find_element_by_symbol(symbol, elements)
        if el is None:
            raise FormulaError(
                f"Unknown element symbol: '{symbol}'",
                code="unknown_symbol",
                params={"symbol": symbol},
            )
        total += el["atomic_mass"] * count
    return total


def compute_percent_composition(
    atom_counts: dict[str, int],
    elements: list[dict],
    *,
    total_mass: float | None = None,
) -> list[dict]:
    """Return the percent composition of each element in the formula.

    Output: [{"symbol": str, "count": int, "mass": float, "percent": float}, ...]
    sorted by percent descending.

    Pass ``total_mass`` if it has already been computed for ``atom_counts`` to
    skip the redundant :func:`compute_molar_mass` call.
    """
    if total_mass is None:
        total_mass = compute_molar_mass(atom_counts, elements)
    result = []
    for symbol, count in atom_counts.items():
        el = _find_element_by_symbol(symbol, elements)
        if el is None:
            raise FormulaError(
                f"Unknown element symbol: '{symbol}'",
                code="unknown_symbol",
                params={"symbol": symbol},
            )
        mass = el["atomic_mass"] * count
        percent = (mass / total_mass) * 100.0 if total_mass > 0 else 0.0
        result.append({
            "symbol": symbol,
            "count": count,
            "mass": round(mass, 4),
            "percent": round(percent, 2),
        })
    result.sort(key=lambda x: x["percent"], reverse=True)
    return result


def empirical_formula_from_composition(
    rows: list[dict],
    elements: list[dict],
    *,
    total_molar_mass: float | None = None,
    tolerance: float = 0.05,
    max_multiplier: int = 6,
) -> dict:
    """Derive an empirical (and optionally molecular) formula from composition.

    ``rows`` is a list of ``{"symbol": "C", "amount": 40.0}`` entries. The
    ``amount`` is the mass fraction (a percentage like 40.0) or the mass in
    grams of that element in a 100-g basis — both interpretations give the
    same ratio, so the caller can pick whichever is convenient.

    The algorithm divides the moles of each element by the smallest, then
    multiplies the resulting ratios by 2, 3, … up to ``max_multiplier`` until
    every value is within ``tolerance`` of an integer.

    Returns::

        {
            "empirical": "CH2O",
            "empirical_atoms": {"C": 1, "H": 2, "O": 1},
            "empirical_mass": 30.026,
            "molecular": "C6H12O6" | None,
            "molecular_atoms": {"C": 6, "H": 12, "O": 6} | None,
            "multiplier": int | None,
        }

    Raises ``FormulaError(code="empirical_empty")`` if ``rows`` is empty and
    ``FormulaError(code="unknown_symbol")`` if a symbol is not in ``elements``
    and ``FormulaError(code="invalid_amount")`` if any amount is non-positive.
    """
    if not rows:
        raise FormulaError(
            "Empirical-formula composition is empty.",
            code="empirical_empty",
            params={},
        )

    moles: list[tuple[str, float]] = []
    for row in rows:
        symbol = row.get("symbol")
        amount = row.get("amount")
        if not symbol:
            raise FormulaError(
                "Empirical-formula row is missing a symbol.",
                code="invalid_amount",
                params={"symbol": ""},
            )
        if amount is None or amount <= 0:
            raise FormulaError(
                f"Empirical-formula row '{symbol}' must have a positive amount.",
                code="invalid_amount",
                params={"symbol": symbol},
            )
        el = _find_element_by_symbol(symbol, elements)
        if el is None:
            raise FormulaError(
                f"Unknown element symbol: '{symbol}'",
                code="unknown_symbol",
                params={"symbol": symbol},
            )
        moles.append((symbol, amount / el["atomic_mass"]))

    smallest = min(m for _, m in moles)
    base_ratios = [(sym, value / smallest) for sym, value in moles]

    def _all_near_integer(ratios: list[float]) -> bool:
        return all(abs(r - round(r)) <= tolerance for r in ratios)

    integer_counts: list[int] = []
    for mult in range(1, max_multiplier + 1):
        scaled = [value * mult for _, value in base_ratios]
        if _all_near_integer(scaled):
            integer_counts = [max(1, round(v)) for v in scaled]
            break

    if not integer_counts:
        # Fall back to the original (mult=1) integer rounding even if the
        # values are not crisp; this still gives the student a reasonable
        # first answer.
        integer_counts = [max(1, round(value)) for _, value in base_ratios]

    # Reduce by GCD so the result is the simplest whole-number ratio.
    from math import gcd

    if integer_counts:
        g = integer_counts[0]
        for count in integer_counts[1:]:
            g = gcd(g, count)
        if g > 1:
            integer_counts = [count // g for count in integer_counts]

    empirical_atoms = {
        sym: count
        for (sym, _), count in zip(base_ratios, integer_counts, strict=True)
    }
    empirical_str = _format_formula_string(empirical_atoms)
    empirical_mass = compute_molar_mass(empirical_atoms, elements)

    molecular_str = None
    molecular_atoms = None
    molecular_multiplier = None
    if total_molar_mass is not None and total_molar_mass > 0 and empirical_mass > 0:
        molecular_multiplier = max(1, round(total_molar_mass / empirical_mass))
        if molecular_multiplier > 1:
            molecular_atoms = {
                sym: count * molecular_multiplier
                for sym, count in empirical_atoms.items()
            }
            molecular_str = _format_formula_string(molecular_atoms)
        else:
            molecular_atoms = dict(empirical_atoms)
            molecular_str = empirical_str

    return {
        "empirical": empirical_str,
        "empirical_atoms": empirical_atoms,
        "empirical_mass": round(empirical_mass, 4),
        "molecular": molecular_str,
        "molecular_atoms": molecular_atoms,
        "multiplier": molecular_multiplier,
    }


def _format_formula_string(atoms: dict[str, int]) -> str:
    """Render an {symbol: count} mapping as a Hill-system formula string.

    Carbon comes first, then hydrogen, then the rest alphabetically — the
    convention used by IUPAC for organic compounds. Counts of 1 are omitted.
    """
    keys = list(atoms.keys())
    ordered: list[str] = []
    if "C" in keys:
        ordered.append("C")
        if "H" in keys:
            ordered.append("H")
        for k in sorted(set(keys) - {"C", "H"}):
            ordered.append(k)
    else:
        ordered = sorted(keys)
    parts = []
    for sym in ordered:
        count = atoms[sym]
        parts.append(f"{sym}{count}" if count > 1 else sym)
    return "".join(parts)
