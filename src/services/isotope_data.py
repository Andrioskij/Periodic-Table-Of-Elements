"""
Isotope data module.

Provides information about common stable and long-lived isotopes for all elements.
Data includes mass number, natural abundance (for stable isotopes), and half-life
for radioactive isotopes.
"""

__all__ = ["get_isotopes", "ISOTOPE_DATA"]

# Isotope data: symbol -> list of {"mass_number": int, "abundance": float (0-100) or None, "half_life": str}
# For stable isotopes: abundance is provided (in %)
# For radioactive isotopes: half_life is provided (e.g., "2.6M years" = million years, "87.4d" = days)
ISOTOPE_DATA = {
    "H": [
        {"mass_number": 1, "abundance": 99.9885, "half_life": None, "name": "Protium"},
        {"mass_number": 2, "abundance": 0.0115, "half_life": None, "name": "Deuterium"},
        {"mass_number": 3, "abundance": None, "half_life": "12.3 years", "name": "Tritium"},
    ],
    "C": [
        {"mass_number": 12, "abundance": 98.93, "half_life": None, "name": "Carbon-12"},
        {"mass_number": 13, "abundance": 1.07, "half_life": None, "name": "Carbon-13"},
        {"mass_number": 14, "abundance": None, "half_life": "5730 years", "name": "Carbon-14"},
    ],
    "N": [
        {"mass_number": 14, "abundance": 99.632, "half_life": None, "name": "Nitrogen-14"},
        {"mass_number": 15, "abundance": 0.368, "half_life": None, "name": "Nitrogen-15"},
    ],
    "O": [
        {"mass_number": 16, "abundance": 99.757, "half_life": None, "name": "Oxygen-16"},
        {"mass_number": 17, "abundance": 0.038, "half_life": None, "name": "Oxygen-17"},
        {"mass_number": 18, "abundance": 0.205, "half_life": None, "name": "Oxygen-18"},
    ],
    "S": [
        {"mass_number": 32, "abundance": 94.99, "half_life": None, "name": "Sulfur-32"},
        {"mass_number": 34, "abundance": 4.25, "half_life": None, "name": "Sulfur-34"},
        {"mass_number": 36, "abundance": 0.01, "half_life": None, "name": "Sulfur-36"},
    ],
    "Cl": [
        {"mass_number": 35, "abundance": 75.76, "half_life": None, "name": "Chlorine-35"},
        {"mass_number": 37, "abundance": 24.24, "half_life": None, "name": "Chlorine-37"},
    ],
    "Fe": [
        {"mass_number": 54, "abundance": 5.845, "half_life": None, "name": "Iron-54"},
        {"mass_number": 56, "abundance": 91.754, "half_life": None, "name": "Iron-56"},
        {"mass_number": 57, "abundance": 2.119, "half_life": None, "name": "Iron-57"},
        {"mass_number": 58, "abundance": 0.282, "half_life": None, "name": "Iron-58"},
    ],
    "Cu": [
        {"mass_number": 63, "abundance": 69.17, "half_life": None, "name": "Copper-63"},
        {"mass_number": 65, "abundance": 30.83, "half_life": None, "name": "Copper-65"},
    ],
    "Zn": [
        {"mass_number": 64, "abundance": 49.17, "half_life": None, "name": "Zinc-64"},
        {"mass_number": 66, "abundance": 27.73, "half_life": None, "name": "Zinc-66"},
        {"mass_number": 68, "abundance": 18.45, "half_life": None, "name": "Zinc-68"},
        {"mass_number": 70, "abundance": 0.61, "half_life": None, "name": "Zinc-70"},
    ],
    "Ag": [
        {"mass_number": 107, "abundance": 51.84, "half_life": None, "name": "Silver-107"},
        {"mass_number": 109, "abundance": 48.16, "half_life": None, "name": "Silver-109"},
    ],
    "I": [
        {"mass_number": 127, "abundance": 100.0, "half_life": None, "name": "Iodine-127"},
        {"mass_number": 131, "abundance": None, "half_life": "8.02 days", "name": "Iodine-131"},
    ],
    "U": [
        {"mass_number": 235, "abundance": 0.72, "half_life": "7.04e8 years", "name": "Uranium-235"},
        {"mass_number": 238, "abundance": 99.27, "half_life": "4.468e9 years", "name": "Uranium-238"},
    ],
    "Pu": [
        {"mass_number": 239, "abundance": None, "half_life": "24110 years", "name": "Plutonium-239"},
        {"mass_number": 244, "abundance": None, "half_life": "8.08e7 years", "name": "Plutonium-244"},
    ],
    "Co": [
        {"mass_number": 59, "abundance": 100.0, "half_life": None, "name": "Cobalt-59"},
        {"mass_number": 60, "abundance": None, "half_life": "5.27 years", "name": "Cobalt-60"},
    ],
    "K": [
        {"mass_number": 39, "abundance": 93.258, "half_life": None, "name": "Potassium-39"},
        {"mass_number": 40, "abundance": 0.0117, "half_life": "1.248e9 years", "name": "Potassium-40"},
        {"mass_number": 41, "abundance": 6.730, "half_life": None, "name": "Potassium-41"},
    ],
    "Na": [
        {"mass_number": 23, "abundance": 100.0, "half_life": None, "name": "Sodium-23"},
    ],
    "Mg": [
        {"mass_number": 24, "abundance": 78.99, "half_life": None, "name": "Magnesium-24"},
        {"mass_number": 25, "abundance": 10.0, "half_life": None, "name": "Magnesium-25"},
        {"mass_number": 26, "abundance": 11.01, "half_life": None, "name": "Magnesium-26"},
    ],
    "Al": [
        {"mass_number": 27, "abundance": 100.0, "half_life": None, "name": "Aluminium-27"},
    ],
    "Si": [
        {"mass_number": 28, "abundance": 92.223, "half_life": None, "name": "Silicon-28"},
        {"mass_number": 29, "abundance": 4.685, "half_life": None, "name": "Silicon-29"},
        {"mass_number": 30, "abundance": 3.092, "half_life": None, "name": "Silicon-30"},
    ],
    "P": [
        {"mass_number": 31, "abundance": 100.0, "half_life": None, "name": "Phosphorus-31"},
    ],
    "Ca": [
        {"mass_number": 40, "abundance": 96.941, "half_life": None, "name": "Calcium-40"},
        {"mass_number": 42, "abundance": 0.647, "half_life": None, "name": "Calcium-42"},
        {"mass_number": 48, "abundance": 0.187, "half_life": None, "name": "Calcium-48"},
    ],
    "He": [
        {"mass_number": 3, "abundance": 0.000134, "half_life": None, "name": "Helium-3"},
        {"mass_number": 4, "abundance": 99.999866, "half_life": None, "name": "Helium-4"},
    ],
    "Li": [
        {"mass_number": 6, "abundance": 7.59, "half_life": None, "name": "Lithium-6"},
        {"mass_number": 7, "abundance": 92.41, "half_life": None, "name": "Lithium-7"},
    ],
    "Be": [
        {"mass_number": 9, "abundance": 100.0, "half_life": None, "name": "Beryllium-9"},
    ],
    "B": [
        {"mass_number": 10, "abundance": 19.9, "half_life": None, "name": "Boron-10"},
        {"mass_number": 11, "abundance": 80.1, "half_life": None, "name": "Boron-11"},
    ],
    "F": [
        {"mass_number": 19, "abundance": 100.0, "half_life": None, "name": "Fluorine-19"},
    ],
    "Ne": [
        {"mass_number": 20, "abundance": 90.48, "half_life": None, "name": "Neon-20"},
        {"mass_number": 22, "abundance": 9.25, "half_life": None, "name": "Neon-22"},
    ],
    "Ar": [
        {"mass_number": 36, "abundance": 0.3365, "half_life": None, "name": "Argon-36"},
        {"mass_number": 38, "abundance": 0.0632, "half_life": None, "name": "Argon-38"},
        {"mass_number": 40, "abundance": 99.6035, "half_life": None, "name": "Argon-40"},
    ],
    "Cr": [
        {"mass_number": 50, "abundance": 4.345, "half_life": None, "name": "Chromium-50"},
        {"mass_number": 52, "abundance": 83.789, "half_life": None, "name": "Chromium-52"},
        {"mass_number": 53, "abundance": 9.501, "half_life": None, "name": "Chromium-53"},
        {"mass_number": 54, "abundance": 2.365, "half_life": None, "name": "Chromium-54"},
    ],
    "Ni": [
        {"mass_number": 58, "abundance": 68.077, "half_life": None, "name": "Nickel-58"},
        {"mass_number": 60, "abundance": 26.223, "half_life": None, "name": "Nickel-60"},
        {"mass_number": 62, "abundance": 3.634, "half_life": None, "name": "Nickel-62"},
    ],
    "Sn": [
        {"mass_number": 120, "abundance": 32.59, "half_life": None, "name": "Tin-120"},
        {"mass_number": 122, "abundance": 4.63, "half_life": None, "name": "Tin-122"},
        {"mass_number": 124, "abundance": 5.79, "half_life": None, "name": "Tin-124"},
    ],
    "Pb": [
        {"mass_number": 204, "abundance": 1.4, "half_life": None, "name": "Lead-204"},
        {"mass_number": 206, "abundance": 24.1, "half_life": None, "name": "Lead-206"},
        {"mass_number": 207, "abundance": 22.1, "half_life": None, "name": "Lead-207"},
        {"mass_number": 208, "abundance": 52.4, "half_life": None, "name": "Lead-208"},
    ],
    "Th": [
        {"mass_number": 232, "abundance": 100.0, "half_life": "1.4e10 years", "name": "Thorium-232"},
    ],
}


def get_isotopes(symbol):
    """
    Get list of common isotopes for an element.

    Args:
        symbol: Chemical symbol (e.g., 'H', 'C', 'U')

    Returns:
        List of isotope dicts with keys: mass_number, abundance (or None),
        half_life (or None), name. Empty list if element not found.
    """
    return ISOTOPE_DATA.get(symbol, [])
