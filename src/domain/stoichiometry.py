"""Balance chemical equations and compute stoichiometric masses.

EquationError codes (used by the UI to look up localized messages):
- ``empty``: equation is empty / whitespace-only.
- ``no_separator``: no recognized separator (``->``, ``→``, ``=``) found.
- ``one_separator``: equation does not split cleanly on a single separator.
- ``both_sides``: at least one side has no compounds.
- ``invalid_compound``: a compound failed to parse. Params: ``compound``, ``detail``.
- ``cannot_balance``: composition matrix has no nullspace.
- ``under_determined``: nullspace has multiple independent solutions.
- ``zero_coefficient``: balancing produced a zero coefficient.
- ``compound_not_found``: requested compound is not part of the equation. Params: ``compound``.
"""

from fractions import Fraction
from math import gcd, lcm

from src.domain.molar_mass import FormulaError, compute_molar_mass, parse_formula


class EquationError(ValueError):
    """Raised when a chemical equation cannot be parsed or balanced.

    Carries an optional ``code`` and ``params`` dict so the UI layer can map
    them to a localized message via :func:`src.ui.error_format.format_equation_error`.
    The English ``message`` remains the fallback when no translation is available.
    """

    def __init__(self, message: str, *, code: str | None = None, params: dict | None = None):
        super().__init__(message)
        self.code = code
        self.params = params or {}


_ARROW_SEPARATORS = ("->", "→", "=")


def parse_equation(equation: str) -> tuple[list[str], list[str]]:
    """Parse 'Fe + O2 -> Fe2O3' into (["Fe", "O2"], ["Fe2O3"]).

    Accepts '->', '→', or '=' as the separator between reactants and products.
    Raises EquationError on malformed input.
    """
    if not equation or not equation.strip():
        raise EquationError("Empty equation", code="empty")

    equation = equation.strip()

    separator_used = None
    for sep in _ARROW_SEPARATORS:
        if sep in equation:
            separator_used = sep
            break

    if separator_used is None:
        raise EquationError(
            "No separator found. Use '->', '→', or '=' between reactants and products.",
            code="no_separator",
        )

    parts = equation.split(separator_used, 1)
    if len(parts) != 2:
        raise EquationError(
            "Equation must have exactly one separator.",
            code="one_separator",
        )

    left, right = parts[0].strip(), parts[1].strip()
    if not left or not right:
        raise EquationError(
            "Both sides of the equation must contain compounds.",
            code="both_sides",
        )

    reactants = [c.strip() for c in left.split("+") if c.strip()]
    products = [c.strip() for c in right.split("+") if c.strip()]

    if not reactants or not products:
        raise EquationError(
            "Both sides of the equation must contain compounds.",
            code="both_sides",
        )

    return reactants, products


def build_composition_matrix(
    reactants: list[str], products: list[str]
) -> tuple[list[list[int]], list[str]]:
    """Build the composition matrix for balancing.

    Columns = compounds (reactants then products).
    Rows = elements.
    Values = +count for reactants, -count for products.

    Returns (matrix, sorted_element_list).
    """
    compounds = reactants + products
    all_atoms = []
    for compound in compounds:
        try:
            all_atoms.append(parse_formula(compound))
        except FormulaError as exc:
            raise EquationError(
                f"Invalid compound '{compound}': {exc}",
                code="invalid_compound",
                params={"compound": compound, "detail": str(exc)},
            ) from exc

    elements = sorted(
        set().union(*(atoms.keys() for atoms in all_atoms))
    )

    n_reactants = len(reactants)

    mat = []
    for el in elements:
        row = []
        for j, atoms in enumerate(all_atoms):
            count = atoms.get(el, 0)
            if j >= n_reactants:
                count = -count
            row.append(count)
        mat.append(row)

    return mat, elements


def _rref(matrix: list[list[Fraction]]) -> None:
    """Reduce ``matrix`` to reduced row-echelon form in place."""
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows:
            break
        sel = next(
            (r for r in range(pivot_row, rows) if matrix[r][col] != 0),
            None,
        )
        if sel is None:
            continue
        matrix[pivot_row], matrix[sel] = matrix[sel], matrix[pivot_row]
        pivot = matrix[pivot_row][col]
        matrix[pivot_row] = [v / pivot for v in matrix[pivot_row]]
        for r in range(rows):
            if r != pivot_row and matrix[r][col] != 0:
                factor = matrix[r][col]
                matrix[r] = [
                    v - factor * matrix[pivot_row][i]
                    for i, v in enumerate(matrix[r])
                ]
        pivot_row += 1


def _nullspace_basis(
    rref: list[list[Fraction]], n_cols: int
) -> list[list[Fraction]]:
    """Return a basis of the nullspace of an RREF matrix as column vectors."""
    pivot_cols: list[int] = []
    for row in rref:
        for c in range(n_cols):
            if row[c] != 0:
                pivot_cols.append(c)
                break
    free_cols = [c for c in range(n_cols) if c not in pivot_cols]
    basis: list[list[Fraction]] = []
    for free in free_cols:
        v = [Fraction(0)] * n_cols
        v[free] = Fraction(1)
        for i, pc in enumerate(pivot_cols):
            v[pc] = -rref[i][free]
        basis.append(v)
    return basis


def balance_equation(equation: str) -> list[int]:
    """Balance the equation and return the minimal positive integer coefficients.

    Returns coefficients in order [reactants..., products...].
    Raises EquationError if balancing is impossible or ambiguous.
    """
    reactants, products = parse_equation(equation)
    return balance_parsed(reactants, products)


def balance_parsed(reactants: list[str], products: list[str]) -> list[int]:
    """Balance an already-parsed equation.

    Same contract as :func:`balance_equation`, but skips the parse step so
    callers that already hold ``(reactants, products)`` (e.g. UI panels that
    parsed once for display) avoid a redundant parse.
    """
    mat, _elements = build_composition_matrix(reactants, products)

    n_cols = len(mat[0]) if mat else 0
    frac_mat = [[Fraction(v) for v in row] for row in mat]
    _rref(frac_mat)
    nullspace = _nullspace_basis(frac_mat, n_cols)

    if not nullspace:
        raise EquationError(
            "Cannot balance: elements differ between reactants and products.",
            code="cannot_balance",
        )

    if len(nullspace) > 1:
        raise EquationError(
            "Equation is under-determined (multiple independent solutions).",
            code="under_determined",
        )

    solution = nullspace[0]

    scale = 1
    for val in solution:
        scale = lcm(scale, val.denominator)

    coefficients = []
    for val in solution:
        int_coeff = abs(int(val * scale))
        if int_coeff == 0:
            raise EquationError(
                "Balancing produced a zero coefficient.",
                code="zero_coefficient",
            )
        coefficients.append(int_coeff)

    g = coefficients[0]
    for c in coefficients[1:]:
        g = gcd(g, c)
    coefficients = [c // g for c in coefficients]

    return coefficients


def format_balanced_equation(
    reactants: list[str], products: list[str], coefficients: list[int]
) -> str:
    """Format the balanced equation as a readable string.

    Omits coefficient 1. Uses '→' as the separator.
    """
    n_r = len(reactants)

    def _format_term(compound, coeff):
        if coeff == 1:
            return compound
        return f"{coeff}{compound}"

    left_parts = [
        _format_term(reactants[i], coefficients[i]) for i in range(n_r)
    ]
    right_parts = [
        _format_term(products[i], coefficients[n_r + i])
        for i in range(len(products))
    ]

    return " + ".join(left_parts) + " → " + " + ".join(right_parts)


def compute_stoichiometric_masses(
    reactants: list[str],
    products: list[str],
    coefficients: list[int],
    elements: list[dict],
    given_compound: str | None = None,
    given_mass_grams: float | None = None,
    *,
    molar_masses: list[float] | None = None,
) -> list[dict]:
    """Compute stoichiometric masses for every compound in the equation.

    If given_compound and given_mass_grams are provided, computes actual
    moles and masses based on those values. Otherwise shows the base
    molar ratios (1x coefficients).

    Pass ``molar_masses`` (one entry per compound, in ``reactants + products``
    order) to skip the per-call parse + :func:`compute_molar_mass` work when a
    caller has already computed them for the same equation.

    Returns: [{"compound": str, "coefficient": int, "molar_mass": float,
               "moles": float, "mass": float}, ...]
    """
    compounds = reactants + products
    n = len(compounds)

    if molar_masses is None:
        molar_masses = []
        for compound in compounds:
            atoms = parse_formula(compound)
            mm = compute_molar_mass(atoms, elements)
            molar_masses.append(mm)

    # Find the given compound index
    given_idx = None
    if given_compound is not None and given_mass_grams is not None:
        for i, c in enumerate(compounds):
            if c == given_compound:
                given_idx = i
                break
        if given_idx is None:
            raise EquationError(
                f"Compound '{given_compound}' not found in equation.",
                code="compound_not_found",
                params={"compound": given_compound},
            )

    result = []
    for i in range(n):
        coeff = coefficients[i]
        mm = molar_masses[i]

        if given_idx is not None:
            given_moles = given_mass_grams / molar_masses[given_idx]
            ratio = coeff / coefficients[given_idx]
            moles = given_moles * ratio
            mass = moles * mm
        else:
            moles = float(coeff)
            mass = coeff * mm

        result.append({
            "compound": compounds[i],
            "coefficient": coeff,
            "molar_mass": round(mm, 4),
            "moles": round(moles, 4),
            "mass": round(mass, 4),
        })

    return result
