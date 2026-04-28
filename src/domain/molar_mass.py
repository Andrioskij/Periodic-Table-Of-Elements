"""Parse chemical formulas and compute molar masses and percent composition."""


class FormulaError(ValueError):
    """Raised when a chemical formula cannot be parsed or contains unknown symbols."""


def parse_formula(formula: str) -> dict[str, int]:
    """Parse a chemical formula and return {symbol: atom_count}.

    Handles simple formulas (H2O), parentheses with multipliers Ca(OH)2,
    nested parentheses Mg3(PO4)2, and implicit count of 1.

    Raises FormulaError on empty input, invalid characters, or malformed
    parentheses.
    """
    if not formula or not formula.strip():
        raise FormulaError("Empty formula")

    formula = formula.strip()
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
                raise FormulaError(f"Unmatched closing parenthesis at position {i}")
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
                f"Unexpected character '{ch}' at position {i} in formula '{formula}'"
            )

    if len(stack) != 1:
        raise FormulaError("Unmatched opening parenthesis in formula")

    if not stack[0]:
        raise FormulaError(f"No elements found in formula '{formula}'")

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
            raise FormulaError(f"Unknown element symbol: '{symbol}'")
        total += el["atomic_mass"] * count
    return total


def compute_percent_composition(
    atom_counts: dict[str, int], elements: list[dict]
) -> list[dict]:
    """Return the percent composition of each element in the formula.

    Output: [{"symbol": str, "count": int, "mass": float, "percent": float}, ...]
    sorted by percent descending.
    """
    total_mass = compute_molar_mass(atom_counts, elements)
    result = []
    for symbol, count in atom_counts.items():
        el = _find_element_by_symbol(symbol, elements)
        if el is None:
            raise FormulaError(f"Unknown element symbol: '{symbol}'")
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
