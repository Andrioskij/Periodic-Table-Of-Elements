CORE_CONFIGS = {
    "[He]": ["1s2"],
    "[Ne]": ["1s2", "2s2", "2p6"],
    "[Ar]": ["1s2", "2s2", "2p6", "3s2", "3p6"],
    "[Kr]": ["1s2", "2s2", "2p6", "3s2", "3p6", "4s2", "3d10", "4p6"],
    "[Xe]": [
        "1s2", "2s2", "2p6",
        "3s2", "3p6",
        "4s2", "3d10", "4p6",
        "5s2", "4d10", "5p6",
    ],
    "[Rn]": [
        "1s2", "2s2", "2p6",
        "3s2", "3p6",
        "4s2", "3d10", "4p6",
        "5s2", "4d10", "5p6",
        "6s2", "4f14", "5d10", "6p6",
    ],
}

ORBITAL_BOX_COUNTS = {
    "s": 1,
    "p": 3,
    "d": 5,
    "f": 7,
}

VALID_SUBSHELLS = {
    1: ["s"],
    2: ["s", "p"],
    3: ["s", "p", "d"],
    4: ["s", "p", "d", "f"],
    5: ["s", "p", "d", "f"],
    6: ["s", "p", "d"],
    7: ["s", "p"],
}

NUMERIC_TREND_PROPERTIES = {
    "radius": ("Atomic radius", "atomic_radius"),
    "ionization": ("Ionization energy", "ionization_energy"),
    "affinity": ("Electron affinity", "electron_affinity"),
    "electronegativity": ("Electronegativity", "electronegativity"),
}
