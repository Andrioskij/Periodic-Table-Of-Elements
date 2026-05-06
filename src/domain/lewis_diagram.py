"""Pure-logic helpers for Lewis dot/structure diagrams.

This module covers two related concerns:

1. Single-atom Lewis dot diagrams. ``get_valence_electrons`` derives the
   valence count for a main-group element and ``distribute_dots`` lays
   those electrons out around the symbol following a simplified Hund's
   rule convention.
2. Multi-atom Lewis structures. ``LewisAtom``, ``LewisBond`` and
   ``MoleculeDiagram`` describe a small molecule as a graph of atoms
   plus bonds, and ``lookup_molecule`` resolves a user-supplied formula
   against the hardcoded library defined in
   ``src.domain.lewis_library``.

The module stays free of any Qt or filesystem dependencies so it can be
exercised by pure unit tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass(frozen=True)
class LewisAtom:
    """A single atom positioned in a Lewis structure diagram.

    Coordinates are dimensionless and conventionally live in the range
    ``[-1.0, 1.0]`` with the molecule centred at the origin and the Y
    axis pointing upward (chemistry convention, opposite to a Qt
    pixmap). The UI layer scales these to pixel coordinates and flips
    Y at render time.

    ``lone_pairs`` counts the number of non-bonding electron pairs
    drawn around the atom; ``formal_charge`` is the per-atom formal
    charge (positive or negative integer).
    """

    symbol: str
    x: float
    y: float
    lone_pairs: int = 0
    formal_charge: int = 0


@dataclass(frozen=True)
class LewisBond:
    """A bond between two atoms identified by their index in ``atoms``.

    ``order`` is 1 for a single bond, 2 for a double, 3 for a triple.
    """

    atom1: int
    atom2: int
    order: int = 1


@dataclass(frozen=True)
class MoleculeDiagram:
    """A complete Lewis structure: atoms, bonds, and an overall charge."""

    formula: str
    name: str
    atoms: list[LewisAtom] = field(default_factory=list)
    bonds: list[LewisBond] = field(default_factory=list)
    charge: int = 0


def lookup_molecule(formula: str) -> MoleculeDiagram | None:
    """Return the pre-built Lewis diagram for ``formula`` or ``None``.

    Matching is case-insensitive on the whole formula string, so users
    can type ``"h2o"`` and still find the canonical ``"H2O"`` entry.
    The returned ``MoleculeDiagram`` always carries the canonical
    formula casing as defined in ``src.domain.lewis_library``.

    Returns ``None`` for empty/whitespace input or for formulas that
    are not present in the library.
    """
    if not formula or not formula.strip():
        return None

    from src.domain.lewis_library import MOLECULE_LIBRARY

    key = formula.strip().lower()
    for canonical, diagram in MOLECULE_LIBRARY.items():
        if canonical.lower() == key:
            return diagram
    return None
