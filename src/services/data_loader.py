"""Centralized dataset paths and JSON loaders for the application."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REFERENCE_DATA_DIR = DATA_DIR / "reference"
ELEMENTS_DATA_PATH = RAW_DATA_DIR / "elements.json"
NOMENCLATURE_DATA_PATH = REFERENCE_DATA_DIR / "nomenclature_data.json"


def resolve_data_path(*parts):
    """Resolve a path under the repository data directory."""
    return DATA_DIR.joinpath(*parts)


def load_json_file(path, *, allow_missing=False, default=None):
    """Read and parse a JSON file from disk.

    Wraps the standard open-and-parse flow with clear error messages
    for missing files and malformed JSON. When allow_missing is True,
    silently returns a default value instead of raising on absent files.
    """
    dataset_path = Path(path)
    if allow_missing and not dataset_path.exists():
        return {} if default is None else default

    try:
        with dataset_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Required dataset not found: {dataset_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON dataset: {dataset_path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to read dataset file: {dataset_path}") from exc


def load_elements():
    """Load the full periodic-table dataset from data/raw/elements.json.

    Returns a list of dictionaries, one per element, containing all
    properties needed by the UI and domain layers.
    """
    return load_json_file(ELEMENTS_DATA_PATH)


def load_nomenclature_data():
    """Load the nomenclature reference dataset used by the compound builder.

    Returns an empty dictionary when the file is absent, allowing the
    app to start without nomenclature features.
    """
    return load_json_file(NOMENCLATURE_DATA_PATH, allow_missing=True, default={})


__all__ = [
    "DATA_DIR",
    "ELEMENTS_DATA_PATH",
    "NOMENCLATURE_DATA_PATH",
    "PROCESSED_DATA_DIR",
    "PROJECT_ROOT",
    "RAW_DATA_DIR",
    "REFERENCE_DATA_DIR",
    "load_elements",
    "load_json_file",
    "load_nomenclature_data",
    "resolve_data_path",
]
