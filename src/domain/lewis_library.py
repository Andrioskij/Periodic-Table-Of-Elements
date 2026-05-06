"""Hardcoded library of Lewis structures for ~22 common small molecules.

Why a hardcoded library and not an inference engine?
    Drawing arbitrary Lewis structures requires resonance handling,
    expanded-octet support, and formal-charge minimisation. Each of
    these is a sub-project on its own and well outside the scope of
    this app. A static table covers the 90% pedagogical case (water,
    ammonia, methane, the diatomics) with deterministic, correct
    geometry, and is trivial to extend.

Coordinate convention
    All coordinates are dimensionless and live in the box
    ``x, y in [-1.0, 1.0]`` with the molecule centred at the origin.
    The Y axis follows the chemistry convention (up is positive); the
    UI layer flips it when projecting onto a Qt pixmap.

    Approximate placements per geometry:
        - linear (CO2, BeF2, HCN): atoms on the X axis with y=0,
          inter-atom distance ~0.6.
        - bent ~104° (H2O, H2S, SO2, O3): central atom at (0, 0),
          flanking atoms at (±0.5, -0.4).
        - trigonal (NH3, BF3, SO3): central atom at (0, 0), three
          peripherals at (0, 0.6), (0.52, -0.3), (-0.52, -0.3).
        - tetrahedral (CH4, CCl4, NH4+): central atom at (0, 0), four
          peripherals at (±0.5, ±0.5) — a flat 2D approximation of a
          tetrahedron suitable for pedagogical Lewis sketches.

How to add a new molecule
    Append an entry to ``MOLECULE_LIBRARY`` keyed by canonical formula.

        # Example: hydrogen peroxide H2O2 (skewed trans-planar)
        # "H2O2": MoleculeDiagram(
        #     formula="H2O2",
        #     name="Hydrogen peroxide",
        #     atoms=[
        #         LewisAtom("H", -0.85, 0.30),
        #         LewisAtom("O", -0.30, 0.00, lone_pairs=2),
        #         LewisAtom("O",  0.30, 0.00, lone_pairs=2),
        #         LewisAtom("H",  0.85, -0.30),
        #     ],
        #     bonds=[
        #         LewisBond(0, 1, order=1),
        #         LewisBond(1, 2, order=1),
        #         LewisBond(2, 3, order=1),
        #     ],
        # ),

    Lookup by ``lookup_molecule`` is case-insensitive, so the canonical
    key should follow standard chemistry casing (``"H2O"``, ``"CO2"``,
    ``"NH4+"``).
"""

from __future__ import annotations

from src.domain.lewis_diagram import LewisAtom, LewisBond, MoleculeDiagram

# --- Diatomic homonuclear ---------------------------------------------------

_H2 = MoleculeDiagram(
    formula="H2",
    name="Hydrogen",
    atoms=[
        LewisAtom("H", -0.4, 0.0),
        LewisAtom("H", 0.4, 0.0),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

_O2 = MoleculeDiagram(
    formula="O2",
    name="Oxygen",
    atoms=[
        LewisAtom("O", -0.4, 0.0, lone_pairs=2),
        LewisAtom("O", 0.4, 0.0, lone_pairs=2),
    ],
    bonds=[LewisBond(0, 1, order=2)],
)

_N2 = MoleculeDiagram(
    formula="N2",
    name="Nitrogen",
    atoms=[
        LewisAtom("N", -0.4, 0.0, lone_pairs=1),
        LewisAtom("N", 0.4, 0.0, lone_pairs=1),
    ],
    bonds=[LewisBond(0, 1, order=3)],
)

_F2 = MoleculeDiagram(
    formula="F2",
    name="Fluorine",
    atoms=[
        LewisAtom("F", -0.4, 0.0, lone_pairs=3),
        LewisAtom("F", 0.4, 0.0, lone_pairs=3),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

_Cl2 = MoleculeDiagram(
    formula="Cl2",
    name="Chlorine",
    atoms=[
        LewisAtom("Cl", -0.4, 0.0, lone_pairs=3),
        LewisAtom("Cl", 0.4, 0.0, lone_pairs=3),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

# --- Diatomic heteronuclear -------------------------------------------------

_HF = MoleculeDiagram(
    formula="HF",
    name="Hydrogen fluoride",
    atoms=[
        LewisAtom("H", -0.4, 0.0),
        LewisAtom("F", 0.4, 0.0, lone_pairs=3),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

_HCl = MoleculeDiagram(
    formula="HCl",
    name="Hydrogen chloride",
    atoms=[
        LewisAtom("H", -0.4, 0.0),
        LewisAtom("Cl", 0.4, 0.0, lone_pairs=3),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

_HBr = MoleculeDiagram(
    formula="HBr",
    name="Hydrogen bromide",
    atoms=[
        LewisAtom("H", -0.4, 0.0),
        LewisAtom("Br", 0.4, 0.0, lone_pairs=3),
    ],
    bonds=[LewisBond(0, 1, order=1)],
)

_CO = MoleculeDiagram(
    formula="CO",
    name="Carbon monoxide",
    atoms=[
        LewisAtom("C", -0.4, 0.0, lone_pairs=1, formal_charge=-1),
        LewisAtom("O", 0.4, 0.0, lone_pairs=1, formal_charge=1),
    ],
    bonds=[LewisBond(0, 1, order=3)],
)

_NO = MoleculeDiagram(
    formula="NO",
    name="Nitric oxide",
    atoms=[
        LewisAtom("N", -0.4, 0.0, lone_pairs=2),
        LewisAtom("O", 0.4, 0.0, lone_pairs=2),
    ],
    bonds=[LewisBond(0, 1, order=2)],
)

# --- Triatomic linear --------------------------------------------------------

_CO2 = MoleculeDiagram(
    formula="CO2",
    name="Carbon dioxide",
    atoms=[
        LewisAtom("O", -0.7, 0.0, lone_pairs=2),
        LewisAtom("C", 0.0, 0.0),
        LewisAtom("O", 0.7, 0.0, lone_pairs=2),
    ],
    bonds=[
        LewisBond(0, 1, order=2),
        LewisBond(1, 2, order=2),
    ],
)

_HCN = MoleculeDiagram(
    formula="HCN",
    name="Hydrogen cyanide",
    atoms=[
        LewisAtom("H", -0.7, 0.0),
        LewisAtom("C", 0.0, 0.0),
        LewisAtom("N", 0.7, 0.0, lone_pairs=1),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(1, 2, order=3),
    ],
)

_BeF2 = MoleculeDiagram(
    formula="BeF2",
    name="Beryllium fluoride",
    atoms=[
        LewisAtom("F", -0.7, 0.0, lone_pairs=3),
        LewisAtom("Be", 0.0, 0.0),
        LewisAtom("F", 0.7, 0.0, lone_pairs=3),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(1, 2, order=1),
    ],
)

# --- Triatomic bent ---------------------------------------------------------

_H2O = MoleculeDiagram(
    formula="H2O",
    name="Water",
    atoms=[
        LewisAtom("H", -0.5, -0.4),
        LewisAtom("O", 0.0, 0.0, lone_pairs=2),
        LewisAtom("H", 0.5, -0.4),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(1, 2, order=1),
    ],
)

_H2S = MoleculeDiagram(
    formula="H2S",
    name="Hydrogen sulfide",
    atoms=[
        LewisAtom("H", -0.5, -0.4),
        LewisAtom("S", 0.0, 0.0, lone_pairs=2),
        LewisAtom("H", 0.5, -0.4),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(1, 2, order=1),
    ],
)

_SO2 = MoleculeDiagram(
    formula="SO2",
    name="Sulfur dioxide",
    atoms=[
        LewisAtom("O", -0.5, -0.4, lone_pairs=2),
        LewisAtom("S", 0.0, 0.0, lone_pairs=1, formal_charge=1),
        LewisAtom("O", 0.5, -0.4, lone_pairs=3, formal_charge=-1),
    ],
    bonds=[
        LewisBond(0, 1, order=2),
        LewisBond(1, 2, order=1),
    ],
)

_O3 = MoleculeDiagram(
    formula="O3",
    name="Ozone",
    atoms=[
        LewisAtom("O", -0.5, -0.4, lone_pairs=2),
        LewisAtom("O", 0.0, 0.0, lone_pairs=1, formal_charge=1),
        LewisAtom("O", 0.5, -0.4, lone_pairs=3, formal_charge=-1),
    ],
    bonds=[
        LewisBond(0, 1, order=2),
        LewisBond(1, 2, order=1),
    ],
)

# --- Trigonal ---------------------------------------------------------------

_NH3 = MoleculeDiagram(
    formula="NH3",
    name="Ammonia",
    atoms=[
        LewisAtom("N", 0.0, 0.0, lone_pairs=1),
        LewisAtom("H", 0.0, 0.6),
        LewisAtom("H", 0.52, -0.3),
        LewisAtom("H", -0.52, -0.3),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(0, 2, order=1),
        LewisBond(0, 3, order=1),
    ],
)

_BF3 = MoleculeDiagram(
    formula="BF3",
    name="Boron trifluoride",
    atoms=[
        LewisAtom("B", 0.0, 0.0),
        LewisAtom("F", 0.0, 0.6, lone_pairs=3),
        LewisAtom("F", 0.52, -0.3, lone_pairs=3),
        LewisAtom("F", -0.52, -0.3, lone_pairs=3),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(0, 2, order=1),
        LewisBond(0, 3, order=1),
    ],
)

_SO3 = MoleculeDiagram(
    formula="SO3",
    name="Sulfur trioxide",
    atoms=[
        LewisAtom("S", 0.0, 0.0),
        LewisAtom("O", 0.0, 0.6, lone_pairs=2),
        LewisAtom("O", 0.52, -0.3, lone_pairs=2),
        LewisAtom("O", -0.52, -0.3, lone_pairs=2),
    ],
    bonds=[
        LewisBond(0, 1, order=2),
        LewisBond(0, 2, order=2),
        LewisBond(0, 3, order=2),
    ],
)

# --- Tetrahedral ------------------------------------------------------------

_CH4 = MoleculeDiagram(
    formula="CH4",
    name="Methane",
    atoms=[
        LewisAtom("C", 0.0, 0.0),
        LewisAtom("H", 0.5, 0.5),
        LewisAtom("H", -0.5, 0.5),
        LewisAtom("H", 0.5, -0.5),
        LewisAtom("H", -0.5, -0.5),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(0, 2, order=1),
        LewisBond(0, 3, order=1),
        LewisBond(0, 4, order=1),
    ],
)

_CCl4 = MoleculeDiagram(
    formula="CCl4",
    name="Carbon tetrachloride",
    atoms=[
        LewisAtom("C", 0.0, 0.0),
        LewisAtom("Cl", 0.5, 0.5, lone_pairs=3),
        LewisAtom("Cl", -0.5, 0.5, lone_pairs=3),
        LewisAtom("Cl", 0.5, -0.5, lone_pairs=3),
        LewisAtom("Cl", -0.5, -0.5, lone_pairs=3),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(0, 2, order=1),
        LewisBond(0, 3, order=1),
        LewisBond(0, 4, order=1),
    ],
)

_NH4_PLUS = MoleculeDiagram(
    formula="NH4+",
    name="Ammonium",
    atoms=[
        LewisAtom("N", 0.0, 0.0, formal_charge=1),
        LewisAtom("H", 0.5, 0.5),
        LewisAtom("H", -0.5, 0.5),
        LewisAtom("H", 0.5, -0.5),
        LewisAtom("H", -0.5, -0.5),
    ],
    bonds=[
        LewisBond(0, 1, order=1),
        LewisBond(0, 2, order=1),
        LewisBond(0, 3, order=1),
        LewisBond(0, 4, order=1),
    ],
    charge=1,
)


MOLECULE_LIBRARY: dict[str, MoleculeDiagram] = {
    # Diatomic homonuclear
    "H2": _H2,
    "O2": _O2,
    "N2": _N2,
    "F2": _F2,
    "Cl2": _Cl2,
    # Diatomic heteronuclear
    "HF": _HF,
    "HCl": _HCl,
    "HBr": _HBr,
    "CO": _CO,
    "NO": _NO,
    # Triatomic linear
    "CO2": _CO2,
    "HCN": _HCN,
    "BeF2": _BeF2,
    # Triatomic bent
    "H2O": _H2O,
    "H2S": _H2S,
    "SO2": _SO2,
    "O3": _O3,
    # Trigonal
    "NH3": _NH3,
    "BF3": _BF3,
    "SO3": _SO3,
    # Tetrahedral
    "CH4": _CH4,
    "CCl4": _CCl4,
    "NH4+": _NH4_PLUS,
}


__all__ = ["MOLECULE_LIBRARY"]
