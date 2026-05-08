"""Tests for tools/build_web.py: the web bundle assembler.

These tests run ``build_web`` against a tmp directory and assert that
the generated tree matches the contract the deploy workflow relies on
(the V1 web frontend expects molar_mass.py under python/, the elements
dataset and 7 localizations under data/, and design_tokens.json at the
root with a schema mirroring src.config.design_tokens).
"""

import json

from tools import build_web as build_web_module
from tools.build_web import LOCALIZATION_FILES, build_web


def test_build_web_populates_python_data_and_tokens(tmp_path):
    dest = tmp_path / "web_out"
    written = build_web(dest)

    assert (dest / "python" / "molar_mass.py").is_file()
    assert (dest / "python" / "electron_configuration.py").is_file()
    assert any("molar_mass.py" in str(path) for path in written["python"])
    assert any("electron_configuration.py" in str(path) for path in written["python"])

    # Config package mirror so Pyodide can resolve "from src.config.static_data".
    assert (dest / "python" / "src" / "__init__.py").is_file()
    assert (dest / "python" / "src" / "config" / "__init__.py").is_file()
    assert (dest / "python" / "src" / "config" / "static_data.py").is_file()

    assert (dest / "data" / "elements.json").is_file()
    elements = json.loads((dest / "data" / "elements.json").read_text(encoding="utf-8"))
    assert isinstance(elements, list) and len(elements) == 118

    loc_dir = dest / "data" / "localization"
    for name in LOCALIZATION_FILES:
        path = loc_dir / name
        assert path.is_file(), f"missing localization file: {name}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert "ui_texts" in payload, f"{name} missing ui_texts"

    tokens_path = dest / "design_tokens.json"
    assert tokens_path.is_file()
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    for top_level in ("color", "font", "spacing", "radius", "border"):
        assert top_level in tokens, f"missing top-level key: {top_level}"
    assert "dark" in tokens["color"]["theme"]
    assert "light" in tokens["color"]["theme"]
    assert "dark" in tokens["color"]["category"]
    assert "light" in tokens["color"]["category"]


def test_build_web_bundled_static_data_matches_source(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    bundled = (dest / "python" / "src" / "config" / "static_data.py").read_text(
        encoding="utf-8",
    )
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "src" / "config" / "static_data.py"
    ).read_text(encoding="utf-8")
    assert bundled == source, (
        "The web bundle must ship a byte-identical copy of src/config/static_data.py "
        "so the desktop and the browser share one source of truth for orbital "
        "constants."
    )


def test_build_web_idempotent(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    first_tokens = (dest / "design_tokens.json").read_text(encoding="utf-8")
    first_module = (dest / "python" / "molar_mass.py").read_text(encoding="utf-8")

    build_web(dest)
    second_tokens = (dest / "design_tokens.json").read_text(encoding="utf-8")
    second_module = (dest / "python" / "molar_mass.py").read_text(encoding="utf-8")

    assert first_tokens == second_tokens
    assert first_module == second_module


def test_build_web_localization_set_matches_languages_config():
    from src.config.languages import ALL_LANGUAGE_OPTIONS

    expected = {f"{code}.json" for code, _ in ALL_LANGUAGE_OPTIONS}
    assert set(LOCALIZATION_FILES) == expected, (
        "LOCALIZATION_FILES must mirror src.config.languages.ALL_LANGUAGE_OPTIONS so the web "
        "deploy ships the same languages the desktop offers."
    )


def test_build_web_module_exposes_build_function():
    assert callable(build_web_module.build_web)


def test_web_app_js_includes_search_match_scorer():
    from pathlib import Path

    app_js = (
        Path(__file__).resolve().parents[2] / "web" / "app.js"
    ).read_text(encoding="utf-8")
    assert "computeMatchScore" in app_js, (
        "web/app.js must keep the search scorer; if you renamed it, update "
        "this drift test to match."
    )
