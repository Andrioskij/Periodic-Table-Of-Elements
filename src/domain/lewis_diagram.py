"""Pure-logic functions for Lewis dot diagram computation.

Determines valence electron count from an element's group and
distributes dots across four positions (top, right, bottom, left)
following a simplified Hund's rule convention.
"""

_POSITIONS = ("top", "right", "bottom", "left")


def get_valence_electrons(element: dict) -> int | None:
    """Return the number of valence electrons for a main-group element.

    Uses the element's periodic-table group number.  Returns None for
    transition metals (groups 3-12), lanthanides, and actinides, where
    Lewis dot diagrams are not conventionally drawn.
    """
    category = (element.get("category") or "").lower()
    if category in ("lanthanide", "actinide"):
        return None

    group = element.get("group")
    if group is None:
        return None

    if 3 <= group <= 12:
        return None

    # Helium exception: group 18 but only 2 valence electrons
    if group == 18:
        symbol = element.get("symbol", "")
        if symbol == "He":
            return 2
        return 8

    if group <= 2:
        return group

    # Groups 13-17
    return group - 10


def distribute_dots(valence_electrons: int) -> dict[str, int]:
    """Distribute valence electrons across four positions around a symbol.

    Fills one electron per position first (top → right → bottom → left),
    then pairs starting from top again.  Each position holds 0, 1, or 2.

    Returns ``{"top": n, "right": n, "bottom": n, "left": n}``.
    """
    result = {pos: 0 for pos in _POSITIONS}
    remaining = max(0, min(valence_electrons, 8))

    # First pass: one electron per position
    for pos in _POSITIONS:
        if remaining <= 0:
            break
        result[pos] = 1
        remaining -= 1

    # Second pass: pair up
    for pos in _POSITIONS:
        if remaining <= 0:
            break
        result[pos] = 2
        remaining -= 1

    return result
