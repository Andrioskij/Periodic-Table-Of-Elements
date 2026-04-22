"""Balance chemical equations and compute stoichiometric masses."""

from sympy import Matrix, lcm

from src.domain.molar_mass import FormulaError, compute_molar_mass, parse_formula


class EquationError(ValueError):
    """Raised when a chemical equation cannot be parsed or balanced."""


_ARROW_SEPARATORS = ("->", "→", "=")


def parse_equation(equation: str) -> tuple[list[str], list[str]]:
    """Parse 'Fe + O2 -> Fe2O3' into (["Fe", "O2"], ["Fe2O3"]).

    Accepts '->', '→', or '=' as the separator between reactants and products.
    Raises EquationError on malformed input.
    """
    if not equation or not equation.strip():
        raise EquationError("Empty equation")

    equation = equation.strip()

    separator_used = None
    for sep in _ARROW_SEPARATORS:
        if sep in equation:
            separator_used = sep
            break

    if separator_used is None:
        raise EquationError(
            "No separator found. Use '->', '→', or '=' between reactants and products."
        )

    parts = equation.split(separator_used, 1)
    if len(parts) != 2:
        raise EquationError("Equation must have exactly one separator.")

    left, right = parts[0].strip(), parts[1].strip()
    if not left or not right:
        raise EquationError("Both sides of the equation must contain compounds.")

    reactants = [c.strip() for c in left.split("+") if c.strip()]
    products = [c.strip() for c in right.split("+") if c.strip()]

    if not reactants or not products:
        raise EquationError("Both sides of the equation must contain compounds.")

    return reactants, products


def build_composition_matrix(
    reactants: list[str], products: list[str]
) -> tuple[Matrix, list[str]]:
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
            raise EquationError(f"Invalid compound '{compound}': {exc}") from exc

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

    return Matrix(mat), elements


def balance_equation(equation: str) -> list[int]:
    """Balance the equation and return the minimal positive integer coefficients.

    Returns coefficients in order [reactants..., products...].
    Raises EquationError if balancing is impossible or ambiguous.
    """
    reactants, products = parse_equation(equation)
    mat, elements = build_composition_matrix(reactants, products)

    nullspace = mat.nullspace()

    if not nullspace:
        raise EquationError(
            "Cannot balance: elements differ between reactants and products."
        )

    if len(nullspace) > 1:
        raise EquationError(
            "Equation is under-determined (multiple independent solutions)."
        )

    solution = nullspace[0]

    # Find LCM of denominators to get integer coefficients
    from sympy import Rational
    denoms = []
    for val in solution:
        r = Rational(val).limit_denominator(10**6)
        denoms.append(r.q)

    scale = denoms[0]
    for d in denoms[1:]:
        scale = lcm(scale, d)

    coefficients = []
    for val in solution:
        coeff = val * scale
        int_coeff = int(abs(coeff))
        if int_coeff == 0:
            raise EquationError("Balancing produced a zero coefficient.")
        coefficients.append(int_coeff)

    # Reduce by GCD
    from math import gcd
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
) -> list[dict]:
    """Compute stoichiometric masses for every compound in the equation.

    If given_compound and given_mass_grams are provided, computes actual
    moles and masses based on those values. Otherwise shows the base
    molar ratios (1x coefficients).

    Returns: [{"compound": str, "coefficient": int, "molar_mass": float,
               "moles": float, "mass": float}, ...]
    """
    compounds = reactants + products
    n = len(compounds)

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
            raise EquationError(f"Compound '{given_compound}' not found in equation.")

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
