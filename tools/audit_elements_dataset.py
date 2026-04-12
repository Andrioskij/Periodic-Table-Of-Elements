"""CLI tool that audits elements.json for data quality issues.

Checks for missing required fields, duplicate entries, invalid electron
configurations, and missing nomenclature support. Outputs a cleaned
JSON file and a markdown audit report.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REQUIRED_FIELDS = [
    "atomic_number",
    "symbol",
    "name",
    "period",
    "group",
    "category",
    "electron_configuration",
    "display_row",
    "display_column",
]

CONFIG_TOKEN_RE = re.compile(r"(\[[A-Za-z]{1,2}\]|\d[spdf]\d+)")


def load_json(path: Path):
    """Read and parse a JSON file, returning the deserialized data."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_category(value):
    """Lowercase and strip whitespace from a category string.

    Returns None for missing values, ensuring consistent comparison
    across the dataset.
    """
    if value is None:
        return None
    return str(value).strip().lower()


def is_valid_configuration(config_text):
    """Check whether an electron configuration string contains parseable tokens.

    Returns True when at least one valid subshell token (e.g. '2p6')
    or noble-gas core abbreviation (e.g. '[Ar]') is found.
    """
    if not config_text:
        return False
    tokens = CONFIG_TOKEN_RE.findall(str(config_text))
    return bool(tokens)


def audit_elements(elements, nomenclature_symbols):
    """Run all quality checks on the elements dataset.

    Returns a report dictionary listing duplicates, missing fields,
    invalid configurations, display-position issues, and elements
    without nomenclature support.
    """
    report = {
        "element_count": len(elements),
        "missing_required_fields": [],
        "duplicate_atomic_numbers": [],
        "duplicate_symbols": [],
        "missing_nomenclature_support": [],
        "invalid_electron_configuration": [],
        "display_position_issues": [],
        "normalized_categories_preview": [],
    }

    atomic_numbers = [element.get("atomic_number") for element in elements]
    symbols = [element.get("symbol") for element in elements]

    report["duplicate_atomic_numbers"] = [
        value for value, count in Counter(atomic_numbers).items() if count > 1 and value is not None
    ]
    report["duplicate_symbols"] = [
        value for value, count in Counter(symbols).items() if count > 1 and value is not None
    ]

    for element in elements:
        symbol = element.get("symbol", "<missing symbol>")
        missing = [field for field in REQUIRED_FIELDS if field not in element]
        if missing:
            report["missing_required_fields"].append({"symbol": symbol, "fields": missing})

        if symbol not in nomenclature_symbols:
            report["missing_nomenclature_support"].append(symbol)

        if not is_valid_configuration(element.get("electron_configuration")):
            report["invalid_electron_configuration"].append(symbol)

        row = element.get("display_row")
        col = element.get("display_column")
        if not isinstance(row, int) or not isinstance(col, int):
            report["display_position_issues"].append(symbol)

        report["normalized_categories_preview"].append({
            "symbol": symbol,
            "original": element.get("category"),
            "normalized": normalize_category(element.get("category")),
        })

    report["missing_nomenclature_support"] = sorted(set(report["missing_nomenclature_support"]))
    report["normalized_categories_preview"] = report["normalized_categories_preview"][:15]
    return report


def get_default_output_paths(elements_path: Path):
    """Determine where to write the cleaned dataset and audit report.

    Places output in data/processed/ when the input comes from
    data/raw/, otherwise writes alongside the input file.
    """
    if elements_path.parent == DATA_RAW_DIR:
        return (
            DATA_PROCESSED_DIR / "elements_cleaned.json",
            DATA_PROCESSED_DIR / "elements_audit_report.md",
        )

    return (
        elements_path.with_name("elements_cleaned.json"),
        elements_path.with_name("elements_audit_report.md"),
    )


def write_cleaned_elements(elements, output_path: Path):
    """Write a normalized copy of the elements dataset to JSON.

    Sorts elements by atomic number and lowercases all category
    values for consistency.
    """
    cleaned = []
    for element in sorted(elements, key=lambda item: item.get("atomic_number", 0)):
        entry = dict(element)
        if "category" in entry:
            entry["category"] = normalize_category(entry.get("category"))
        cleaned.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(cleaned, handle, ensure_ascii=False, indent=2)


def write_report(report, output_path: Path):
    """Render the audit report as a markdown file.

    Summarizes duplicates, missing fields, nomenclature gaps,
    configuration issues, and a category normalization preview.
    """
    lines = [
        "# Elements dataset audit report",
        "",
        f"- Total elements: {report['element_count']}",
        f"- Duplicate atomic numbers: {report['duplicate_atomic_numbers'] or 'none'}",
        f"- Duplicate symbols: {report['duplicate_symbols'] or 'none'}",
        f"- Missing nomenclature support: {len(report['missing_nomenclature_support'])}",
        f"- Invalid electron configurations: {report['invalid_electron_configuration'] or 'none'}",
        f"- Display position issues: {report['display_position_issues'] or 'none'}",
        "",
        "## Missing required fields",
        "",
    ]

    if report["missing_required_fields"]:
        for item in report["missing_required_fields"]:
            lines.append(f"- {item['symbol']}: missing {', '.join(item['fields'])}")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Symbols missing nomenclature support",
        "",
    ]
    if report["missing_nomenclature_support"]:
        for symbol in report["missing_nomenclature_support"]:
            lines.append(f"- {symbol}")
    else:
        lines.append("- none")

    lines += [
        "",
        "## Category normalization preview",
        "",
    ]
    for item in report["normalized_categories_preview"]:
        lines.append(
            f"- {item['symbol']}: {item['original']} -> {item['normalized']}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    """Entry point: parse CLI arguments, run the audit, and write outputs."""
    if len(sys.argv) < 3:
        print("Usage: python tools/audit_elements_dataset.py <elements.json> <nomenclature_data.json>")
        raise SystemExit(1)

    elements_path = Path(sys.argv[1]).resolve()
    nomenclature_path = Path(sys.argv[2]).resolve()

    elements = load_json(elements_path)
    nomenclature = load_json(nomenclature_path)
    nomenclature_symbols = set(nomenclature.get("elements", {}).keys())

    report = audit_elements(elements, nomenclature_symbols)

    cleaned_path, report_path = get_default_output_paths(elements_path)

    write_cleaned_elements(elements, cleaned_path)
    write_report(report, report_path)

    print(f"Cleaned dataset written to: {cleaned_path}")
    print(f"Audit report written to: {report_path}")


if __name__ == "__main__":
    main()
