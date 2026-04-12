import csv
import io
import json
import urllib.request
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def normalize_text(value):
    """
    Normalize text values read from the CSV.

    Parameters:
        value: value read from the CSV file, which can be a string, empty string, or None.

    Returns:
        None if the value is empty or unavailable, the cleaned string otherwise.
    """
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return None

    return value


def to_float(value):
    """
    Convert a numeric value read from the CSV to float.

    Parameters:
        value: numeric string, empty string, 'NaN', or None.

    Returns:
        A float if conversion is possible, None if the data is missing or not convertible.
    """
    value = normalize_text(value)

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def fetch_pubchem_rows():
    """
    Download the complete periodic table dataset from PubChem in CSV format.

    Parameters:
        None. Uses the official PubChem dataset URL internally.

    Returns:
        A list of CSV rows, each represented as a dictionary keyed by PubChem column names.
    """
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV"

    with urllib.request.urlopen(url) as response:
        csv_text = response.read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def build_display_position_lookup():
    """
    Build the visual position map for the periodic table layout.

    Parameters:
        None. Uses an explicit row-based representation of the table internally.

    Returns:
        A dictionary mapping atomic_number -> {"display_row": ..., "display_column": ...}.

    Note:
        Rows 1-7 represent the main table.
        Rows 8-9 represent lanthanides and actinides displayed below the main table.
    """
    rows = {
        1: [1] + [None] * 16 + [2],
        2: [3, 4] + [None] * 10 + [5, 6, 7, 8, 9, 10],
        3: [11, 12] + [None] * 10 + [13, 14, 15, 16, 17, 18],
        4: list(range(19, 37)),
        5: list(range(37, 55)),
        6: [55, 56, 57, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
        7: [87, 88, 89, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118],
        8: [None, None, None, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, None],
        9: [None, None, None, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, None],
    }

    lookup = {}

    for display_row, atomic_numbers in rows.items():
        for display_column, atomic_number in enumerate(atomic_numbers, start=1):
            if atomic_number is not None:
                lookup[atomic_number] = {
                    "display_row": display_row,
                    "display_column": display_column,
                }

    return lookup


def get_period(atomic_number):
    """
    Return the correct chemical period for an element.

    Parameters:
        atomic_number: the element's atomic number.

    Returns:
        An integer between 1 and 7 indicating the period.
    """
    if 1 <= atomic_number <= 2:
        return 1
    if 3 <= atomic_number <= 10:
        return 2
    if 11 <= atomic_number <= 18:
        return 3
    if 19 <= atomic_number <= 36:
        return 4
    if 37 <= atomic_number <= 54:
        return 5
    if 55 <= atomic_number <= 86:
        return 6
    if 87 <= atomic_number <= 118:
        return 7

    return None


def build_element(record, position_lookup):
    """
    Transform a PubChem CSV row into a final dictionary for elements.json.

    Parameters:
        record: a PubChem CSV row as a dictionary.
        position_lookup: dictionary with visual coordinates for the table layout.

    Returns:
        A Python dictionary ready to be saved into elements.json.
    """
    atomic_number = int(record["AtomicNumber"])
    position = position_lookup[atomic_number]

    # Chemical group:
    # - for the main table we use columns 1-18
    # - for the two separate rows (lanthanides/actinides) we leave None
    if position["display_row"] <= 7:
        group = position["display_column"]
    else:
        group = None

    category = normalize_text(record.get("GroupBlock"))
    if category is not None:
        category = category.lower()

    element = {
        "atomic_number": atomic_number,
        "symbol": normalize_text(record.get("Symbol")),
        "name": normalize_text(record.get("Name")),
        "atomic_mass": to_float(record.get("AtomicMass")),
        "cpk_hex_color": normalize_text(record.get("CPKHexColor")),
        "electron_configuration": normalize_text(record.get("ElectronConfiguration")),
        "electronegativity": to_float(record.get("Electronegativity")),
        "atomic_radius": to_float(record.get("AtomicRadius")),
        "ionization_energy": to_float(record.get("IonizationEnergy")),
        "electron_affinity": to_float(record.get("ElectronAffinity")),
        "oxidation_states": normalize_text(record.get("OxidationStates")),
        "standard_state": normalize_text(record.get("StandardState")),
        "melting_point": to_float(record.get("MeltingPoint")),
        "boiling_point": to_float(record.get("BoilingPoint")),
        "density": to_float(record.get("Density")),
        "category": category,
        "year_discovered": normalize_text(record.get("YearDiscovered")),
        "period": get_period(atomic_number),
        "group": group,
        "display_row": position["display_row"],
        "display_column": position["display_column"],
        "source": "PubChem PUG REST Periodic Table CSV",
        "source_checked": date.today().isoformat(),
    }

    return element


def main():
    """
    Generate the complete data/raw/elements.json file with all 118 elements.

    Parameters:
        Data is downloaded automatically from PubChem.
        Table structure is defined in code.

    Returns:
        Writes the final JSON file to data/raw/elements.json
        and prints a summary to the terminal.
    """
    output_path = DATA_RAW_DIR / "elements.json"

    rows = fetch_pubchem_rows()
    position_lookup = build_display_position_lookup()

    elements = []
    for record in rows:
        element = build_element(record, position_lookup)
        elements.append(element)

    elements.sort(key=lambda element: element["atomic_number"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(elements, file, ensure_ascii=False, indent=4)

    print("File generated successfully.")
    print(f"Path: {output_path}")
    print(f"Elements saved: {len(elements)}")


if __name__ == "__main__":
    main()
