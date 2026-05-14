"""Smoke tests for the Python module the web frontend loads via Pyodide.

These run under regular CPython, importing ``src.domain.molar_mass`` the
same way Pyodide will after ``tools/build_web.py`` copies it into
``web/python/``. They guard against silent drift in the parser surface
or its dataset contract that would only otherwise show up in the
browser at runtime.
"""

import json
from pathlib import Path

from src.config.static_data import ORBITAL_BOX_COUNTS, VALID_SUBSHELLS
from src.domain.compound_builder import (
    build_binary_formula,
    parse_oxidation_states,
)
from src.domain.electron_configuration import configuration_to_map, fill_boxes
from src.domain.lewis_diagram import (
    distribute_dots,
    get_valence_electrons,
    lookup_molecule,
)
from src.domain.molar_mass import (
    FormulaError,
    compute_molar_mass,
    compute_percent_composition,
    empirical_formula_from_composition,
    parse_formula,
)
from src.domain.solubility import (
    get_solubility,
    get_solubility_rule,
)
from src.domain.stoichiometry import (
    balance_equation,
    compute_limiting_reagent,
    compute_stoichiometric_masses,
    parse_equation,
)


def _load_elements():
    path = Path(__file__).resolve().parents[2] / "data" / "raw" / "elements.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_parse_water_and_compute_molar_mass():
    elements = _load_elements()
    atoms = parse_formula("H2O")
    assert atoms == {"H": 2, "O": 1}
    mass = compute_molar_mass(atoms, elements)
    assert abs(mass - 18.015) < 0.05


def test_parse_hydrate_notation():
    elements = _load_elements()
    atoms = parse_formula("CuSO4·5H2O")
    mass = compute_molar_mass(atoms, elements)
    assert abs(mass - 249.685) < 0.5


def test_compute_percent_composition_water():
    elements = _load_elements()
    atoms = parse_formula("H2O")
    composition = compute_percent_composition(atoms, elements)
    by_symbol = {row["symbol"]: row for row in composition}
    assert "H" in by_symbol and "O" in by_symbol
    assert abs(by_symbol["O"]["percent"] - 88.81) < 0.5
    assert abs(by_symbol["H"]["percent"] - 11.19) < 0.5
    assert composition[0]["percent"] >= composition[-1]["percent"]


def test_electron_configuration_parses_and_fills_boxes_for_oxygen():
    # Oxygen: 1s2 2s2 2p4 — Hund's rule places 2 paired in 2p[0] then unpaired
    # singletons in 2p[1] and 2p[2]; this is the layout the orbital diagram shows.
    occupancy = configuration_to_map("1s2 2s2 2p4")
    assert occupancy == {"1s": 2, "2s": 2, "2p": 4}
    assert fill_boxes(4, ORBITAL_BOX_COUNTS["p"]) == [2, 1, 1]


def test_electron_configuration_expands_noble_gas_core():
    # Iron: [Ar]3d6 4s2 should expand into the full 1s..4s sequence.
    occupancy = configuration_to_map("[Ar]3d6 4s2")
    assert occupancy.get("3s") == 2
    assert occupancy.get("3p") == 6
    assert occupancy.get("3d") == 6
    assert occupancy.get("4s") == 2
    assert "p" in VALID_SUBSHELLS[2]


def test_unknown_symbol_raises_with_code():
    elements = _load_elements()
    atoms = parse_formula("Xx2")
    try:
        compute_molar_mass(atoms, elements)
    except FormulaError as exc:
        assert exc.code == "unknown_symbol"
        assert exc.params.get("symbol") == "Xx"
    else:
        raise AssertionError("Expected FormulaError for unknown symbol")


def test_balance_equation_iron_oxide():
    assert balance_equation("Fe + O2 -> Fe2O3") == [4, 3, 2]


def test_balance_equation_combustion():
    assert balance_equation("C3H8 + O2 -> CO2 + H2O") == [1, 5, 3, 4]


def test_stoichiometric_masses_water_from_hydrogen():
    elements = _load_elements()
    reactants, products = parse_equation("H2 + O2 -> H2O")
    coeffs = balance_equation("H2 + O2 -> H2O")
    rows = compute_stoichiometric_masses(
        reactants, products, coeffs, elements,
        given_compound="H2", given_mass_grams=2.0,
    )
    h2o = next(row for row in rows if row["compound"] == "H2O")
    assert abs(h2o["mass"] - 18.015) < 0.5


def test_compute_limiting_reagent_water_synthesis():
    elements = _load_elements()
    result = compute_limiting_reagent(
        ["H2", "O2"], ["H2O"], [2, 1, 2], elements,
        {"H2": 4.0, "O2": 16.0},
    )
    assert result["limiting"] == "O2"
    h2o = result["yields"][0]
    assert h2o["compound"] == "H2O"
    assert abs(h2o["theoretical_mass_g"] - 18.015) < 0.1


def test_lewis_valence_electrons_oxygen():
    elements = _load_elements()
    oxygen = next(el for el in elements if el["symbol"] == "O")
    assert get_valence_electrons(oxygen) == 6


def test_lewis_distribute_dots_oxygen():
    # Oxygen: first pass fills top, right, bottom, left with 1 electron each
    # (that's the 4 unpaired); then the remaining 2 valence electrons pair the
    # top and right positions, leaving bottom + left as singletons.
    placements = distribute_dots(6)
    assert placements["top"] == 2
    assert placements["right"] == 2
    assert placements["bottom"] == 1
    assert placements["left"] == 1


def test_lewis_lookup_water_molecule():
    diagram = lookup_molecule("H2O")
    assert diagram is not None
    assert diagram.formula == "H2O"
    assert len(diagram.atoms) == 3
    assert any(bond.order == 1 for bond in diagram.bonds)


def test_lewis_lookup_is_case_insensitive():
    assert lookup_molecule("h2o") is not None
    assert lookup_molecule("XXNotAMolecule") is None


def test_solubility_smoke():
    assert get_solubility("Na⁺", "Cl⁻") == "soluble"
    assert get_solubility("Ag⁺", "Cl⁻") == "insoluble"
    rule = get_solubility_rule("Ag⁺", "Cl⁻")
    assert rule is not None
    assert rule["id"] == "halides"


def test_compound_builder_smoke():
    assert parse_oxidation_states("+1, -1") == [1, -1]
    assert build_binary_formula("Na", 1, "Cl", -1) == "NaCl"
    assert build_binary_formula("Al", 3, "O", -2) == "Al2O3"


def test_empirical_formula_glucose_smoke():
    elements = _load_elements()
    result = empirical_formula_from_composition(
        [
            {"symbol": "C", "amount": 40.0},
            {"symbol": "H", "amount": 6.7},
            {"symbol": "O", "amount": 53.3},
        ],
        elements,
        total_molar_mass=180.0,
    )
    assert result["empirical"] == "CH2O"
    assert result["molecular"] == "C6H12O6"
