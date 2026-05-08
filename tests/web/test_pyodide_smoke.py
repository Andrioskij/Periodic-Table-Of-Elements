"""Smoke tests for the Python module the web frontend loads via Pyodide.

These run under regular CPython, importing ``src.domain.molar_mass`` the
same way Pyodide will after ``tools/build_web.py`` copies it into
``web/python/``. They guard against silent drift in the parser surface
or its dataset contract that would only otherwise show up in the
browser at runtime.
"""

import json
from pathlib import Path

from src.domain.molar_mass import (
    FormulaError,
    compute_molar_mass,
    compute_percent_composition,
    parse_formula,
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
