"""Solubility rules and matrix for common ionic compounds.

Pure domain logic — no Qt dependencies.
"""

CATIONS = (
    "Li\u207a", "Na\u207a", "K\u207a", "NH\u2084\u207a",
    "Mg\u00b2\u207a", "Ca\u00b2\u207a", "Ba\u00b2\u207a",
    "Fe\u00b2\u207a", "Fe\u00b3\u207a", "Cu\u00b2\u207a",
    "Zn\u00b2\u207a", "Ag\u207a", "Pb\u00b2\u207a", "Al\u00b3\u207a",
)

ANIONS = (
    "Cl\u207b", "Br\u207b", "I\u207b", "NO\u2083\u207b",
    "SO\u2084\u00b2\u207b", "OH\u207b", "CO\u2083\u00b2\u207b",
    "PO\u2084\u00b3\u207b", "S\u00b2\u207b", "CH\u2083COO\u207b",
)

ALKALI_AMMONIUM = {"Li\u207a", "Na\u207a", "K\u207a", "NH\u2084\u207a"}

SOLUBILITY_RULES = [
    {
        "id": "alkali_ammonium",
        "applies_to": "cation",
        "ions": ALKALI_AMMONIUM,
        "result": "soluble",
        "exceptions": {},
    },
    {
        "id": "nitrate_acetate",
        "applies_to": "anion",
        "ions": {"NO\u2083\u207b", "CH\u2083COO\u207b"},
        "result": "soluble",
        "exceptions": {},
    },
    {
        "id": "halides",
        "applies_to": "anion",
        "ions": {"Cl\u207b", "Br\u207b", "I\u207b"},
        "result": "soluble",
        "exceptions": {
            "Ag\u207a": "insoluble",
            "Pb\u00b2\u207a": "insoluble",
        },
    },
    {
        "id": "sulfates",
        "applies_to": "anion",
        "ions": {"SO\u2084\u00b2\u207b"},
        "result": "soluble",
        "exceptions": {
            "Ba\u00b2\u207a": "insoluble",
            "Pb\u00b2\u207a": "insoluble",
            "Ca\u00b2\u207a": "slightly_soluble",
            "Ag\u207a": "slightly_soluble",
        },
    },
    {
        "id": "hydroxides",
        "applies_to": "anion",
        "ions": {"OH\u207b"},
        "result": "insoluble",
        "exceptions": {
            "Li\u207a": "soluble",
            "Na\u207a": "soluble",
            "K\u207a": "soluble",
            "NH\u2084\u207a": "soluble",
            "Ba\u00b2\u207a": "soluble",
            "Ca\u00b2\u207a": "slightly_soluble",
        },
    },
    {
        "id": "carbonate_phosphate_sulfide",
        "applies_to": "anion",
        "ions": {"CO\u2083\u00b2\u207b", "PO\u2084\u00b3\u207b", "S\u00b2\u207b"},
        "result": "insoluble",
        "exceptions": {
            "Li\u207a": "soluble",
            "Na\u207a": "soluble",
            "K\u207a": "soluble",
            "NH\u2084\u207a": "soluble",
        },
    },
]

ELEMENT_TO_CATIONS = {
    "Li": ["Li\u207a"],
    "Na": ["Na\u207a"],
    "K": ["K\u207a"],
    "Mg": ["Mg\u00b2\u207a"],
    "Ca": ["Ca\u00b2\u207a"],
    "Ba": ["Ba\u00b2\u207a"],
    "Fe": ["Fe\u00b2\u207a", "Fe\u00b3\u207a"],
    "Cu": ["Cu\u00b2\u207a"],
    "Zn": ["Zn\u00b2\u207a"],
    "Ag": ["Ag\u207a"],
    "Pb": ["Pb\u00b2\u207a"],
    "Al": ["Al\u00b3\u207a"],
}


def get_solubility(cation, anion):
    """Return 'soluble', 'insoluble', or 'slightly_soluble' for a cation-anion pair.

    Rules are applied in priority order; the first matching rule determines the result.
    If no rule matches, the default is 'insoluble'.
    """
    for rule in SOLUBILITY_RULES:
        if rule["applies_to"] == "cation" and cation in rule["ions"]:
            opposite = anion
            return rule["exceptions"].get(opposite, rule["result"])
        if rule["applies_to"] == "anion" and anion in rule["ions"]:
            opposite = cation
            return rule["exceptions"].get(opposite, rule["result"])
    return "insoluble"


def get_solubility_rule(cation, anion):
    """Return the rule dict that applies to a cation-anion pair, or None.

    Returns None when no specific rule matches (default insoluble).
    """
    for rule in SOLUBILITY_RULES:
        if rule["applies_to"] == "cation" and cation in rule["ions"]:
            return rule
        if rule["applies_to"] == "anion" and anion in rule["ions"]:
            return rule
    return None


def get_solubility_matrix():
    """Generate the full CATIONS x ANIONS solubility matrix.

    Returns a list of lists where matrix[i][j] is the solubility verdict
    for CATIONS[i] and ANIONS[j].
    """
    return [
        [get_solubility(cation, anion) for anion in ANIONS]
        for cation in CATIONS
    ]


def get_cations_for_element(symbol):
    """Return the cations corresponding to an element symbol, or an empty list."""
    return ELEMENT_TO_CATIONS.get(symbol, [])
