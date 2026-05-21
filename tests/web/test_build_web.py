"""Tests for tools/build_web.py: the web bundle assembler.

These tests run ``build_web`` against a tmp directory and assert that
the generated tree matches the contract the deploy workflow relies on
(the V1 web frontend expects molar_mass.py under python/, the elements
dataset and 7 localizations under data/, and design_tokens.json at the
root with a schema mirroring src.config.design_tokens).
"""

import json

from tools import build_web as build_web_module
from tools.build_web import HTML_LINKED_ICONS, ICON_FILES, LOCALIZATION_FILES, build_web


def test_build_web_populates_python_data_and_tokens(tmp_path):
    dest = tmp_path / "web_out"
    written = build_web(dest)

    assert (dest / "python" / "molar_mass.py").is_file()
    assert (dest / "python" / "electron_configuration.py").is_file()
    assert (dest / "python" / "stoichiometry.py").is_file()
    assert any("molar_mass.py" in str(path) for path in written["python"])
    assert any("electron_configuration.py" in str(path) for path in written["python"])
    assert any("stoichiometry.py" in str(path) for path in written["python"])

    # Config + domain package mirrors so Pyodide can resolve both
    # "from src.config.static_data" and the cross-module
    # "from src.domain.molar_mass" import inside stoichiometry.py.
    assert (dest / "python" / "src" / "__init__.py").is_file()
    assert (dest / "python" / "src" / "config" / "__init__.py").is_file()
    assert (dest / "python" / "src" / "config" / "static_data.py").is_file()
    assert (dest / "python" / "src" / "domain" / "__init__.py").is_file()
    assert (dest / "python" / "src" / "domain" / "molar_mass.py").is_file()
    assert (dest / "python" / "src" / "domain" / "stoichiometry.py").is_file()

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


def test_build_web_bundles_lewis_modules(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)

    assert (dest / "python" / "lewis_diagram.py").is_file()
    assert (dest / "python" / "lewis_library.py").is_file()
    # Both modules also live under the nested src.domain mirror so the
    # cross-module import from src.domain.lewis_library inside
    # lewis_diagram resolves the same way as on the desktop.
    assert (dest / "python" / "src" / "domain" / "lewis_diagram.py").is_file()
    assert (dest / "python" / "src" / "domain" / "lewis_library.py").is_file()


def test_build_web_bundled_compound_builder_matches_source(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "src" / "domain" / "compound_builder.py"
    ).read_text(encoding="utf-8")
    flat = (dest / "python" / "compound_builder.py").read_text(encoding="utf-8")
    nested = (
        dest / "python" / "src" / "domain" / "compound_builder.py"
    ).read_text(encoding="utf-8")
    assert flat == source
    assert nested == source


def test_build_web_bundled_trends_matches_source(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "src" / "domain" / "trends.py"
    ).read_text(encoding="utf-8")
    flat = (dest / "python" / "trends.py").read_text(encoding="utf-8")
    nested = (dest / "python" / "src" / "domain" / "trends.py").read_text(
        encoding="utf-8",
    )
    assert flat == source
    assert nested == source


def test_build_web_bundles_design_tokens_module(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    # The design_tokens.py module sits next to static_data.py under
    # src/config/ so trends.py can resolve its TOKENS import inside
    # Pyodide.
    assert (dest / "python" / "src" / "config" / "design_tokens.py").is_file()


def test_build_web_bundled_solubility_matches_source(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "src" / "domain" / "solubility.py"
    ).read_text(encoding="utf-8")
    flat = (dest / "python" / "solubility.py").read_text(encoding="utf-8")
    nested = (dest / "python" / "src" / "domain" / "solubility.py").read_text(
        encoding="utf-8",
    )
    assert flat == source
    assert nested == source


def test_build_web_bundled_stoichiometry_matches_source(tmp_path):
    dest = tmp_path / "web_out"
    build_web(dest)
    from pathlib import Path

    source_path = (
        Path(__file__).resolve().parents[2] / "src" / "domain" / "stoichiometry.py"
    )
    source = source_path.read_text(encoding="utf-8")

    flat = (dest / "python" / "stoichiometry.py").read_text(encoding="utf-8")
    nested = (
        dest / "python" / "src" / "domain" / "stoichiometry.py"
    ).read_text(encoding="utf-8")
    assert flat == source
    assert nested == source, (
        "The nested src/domain/stoichiometry.py mirror must stay byte-identical "
        "with the desktop source so the cross-module import inside the module "
        "(from src.domain.molar_mass import ...) resolves the same way in "
        "Pyodide as on the desktop."
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


def test_build_web_copies_favicon_assets(tmp_path):
    """Every desktop icon listed in ICON_FILES must land in web/icons/ byte-identical.

    The Pages tab and iOS home-screen install must show the same icon
    the .exe ships with; the canonical sources live under assets/ and
    the web bundle is a projection, not a fork.
    """
    from pathlib import Path

    dest = tmp_path / "web_out"
    written = build_web(dest)

    icons_dir = dest / "icons"
    assert icons_dir.is_dir()
    assets_dir = Path(__file__).resolve().parents[2] / "assets"

    for name in ICON_FILES:
        copied = icons_dir / name
        assert copied.is_file(), f"missing icon in web bundle: {name}"
        assert copied.read_bytes() == (assets_dir / name).read_bytes(), (
            f"web/icons/{name} must be byte-identical to assets/{name}"
        )
        assert copied in written["icons"]


def test_web_index_html_references_generated_icons():
    """Every icon in HTML_LINKED_ICONS must appear as a `<link>` href in index.html.

    Iterates the constant instead of hardcoding strings: dropping or
    renaming an entry in HTML_LINKED_ICONS without updating the HTML
    (or vice versa) now fails CI. The subset-of-ICON_FILES invariant
    asserted in build_web.py guarantees we never link an icon the
    build step doesn't emit.
    """
    from pathlib import Path

    index_html = (
        Path(__file__).resolve().parents[2] / "web" / "index.html"
    ).read_text(encoding="utf-8")
    for name in HTML_LINKED_ICONS:
        assert f'./icons/{name}"' in index_html, (
            f"web/index.html is missing a <link> href for {name}"
        )


def test_build_web_emits_version_module_matching_app_metadata(tmp_path):
    from src.app_metadata import APP_VERSION

    dest = tmp_path / "web_out"
    written = build_web(dest)

    version_path = dest / "version.js"
    assert version_path.is_file()
    assert version_path in written["version"]
    assert version_path.read_text(encoding="utf-8") == (
        f'export const APP_VERSION = "{APP_VERSION}";\n'
    )


def test_web_app_js_imports_version_from_generated_module():
    """Pin the import contract: app.js must take APP_VERSION from version.js.

    If this drifts (someone re-declares the constant inline), the deploy
    will silently ship a stale label again — same bug v1.4.1 was cut to
    fix.
    """
    from pathlib import Path

    app_js = (
        Path(__file__).resolve().parents[2] / "web" / "app.js"
    ).read_text(encoding="utf-8")
    assert 'from "./version.js"' in app_js, (
        "web/app.js must import APP_VERSION from the generated version.js "
        "so the Pages bundle tracks src.app_metadata.APP_VERSION."
    )
    assert "const APP_VERSION =" not in app_js, (
        "web/app.js must not redeclare APP_VERSION; it comes from version.js."
    )
