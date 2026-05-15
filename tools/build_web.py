"""Assemble the static ``web/`` artifact for the Pyodide-based frontend.

The ``web/`` directory holds tracked sources (``index.html``, ``style.css``,
``app.js``, ``i18n.js``) plus four generated artifacts regenerated on every
deploy from the desktop sources of truth:

- ``web/python/``            — Python modules loaded by Pyodide.
- ``web/data/``              — element dataset and localization snapshots.
- ``web/design_tokens.json`` — JSON projection of ``TOKENS``.
- ``web/version.js``         — ES module re-exporting ``APP_VERSION`` from
  ``src.app_metadata`` so the browser header label tracks the desktop tag.

Keeping these copies generated (and gitignored) prevents drift between the
desktop and web payloads. The deploy workflow runs this script before
uploading the Pages artifact; tests call ``build_web()`` against a tmp dir.

CLI usage::

    python tools/build_web.py            # populate ./web/
    python tools/build_web.py -o out/web # populate an alternate root
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.app_metadata import APP_VERSION  # noqa: E402
from tools.export_design_tokens import export_tokens  # noqa: E402

DOMAIN_MODULES = (
    "molar_mass.py",
    "electron_configuration.py",
    "stoichiometry.py",
    "lewis_diagram.py",
    "lewis_library.py",
    "compound_builder.py",
    "solubility.py",
    "trends.py",
)
CONFIG_MODULES = ("static_data.py", "design_tokens.py")
LOCALIZATION_FILES = (
    "en.json",
    "it.json",
    "es.json",
    "fr.json",
    "de.json",
    "zh.json",
    "ru.json",
)


def _copy_python_modules(dest_python: Path) -> list[Path]:
    """Copy the V1-required domain modules into ``dest_python``.

    Domain modules sit at the package root so the browser can ``import
    molar_mass`` directly. The same modules are also mirrored under
    ``src/domain/`` (with an empty ``__init__`` marker) so cross-module
    imports like ``from src.domain.molar_mass import ...`` inside
    ``stoichiometry.py`` resolve the same way they do on the desktop.
    Configuration modules are mirrored under ``src/config/`` for the
    matching reason — ``from src.config.static_data import CORE_CONFIGS``
    keeps working unmodified inside Pyodide.
    """
    dest_python.mkdir(parents=True, exist_ok=True)
    written = []
    for name in DOMAIN_MODULES:
        src = REPO_ROOT / "src" / "domain" / name
        if not src.exists():
            raise FileNotFoundError(f"Expected domain module not found: {src}")
        target = dest_python / name
        shutil.copyfile(src, target)
        written.append(target)

    src_pkg = dest_python / "src"
    src_pkg.mkdir(parents=True, exist_ok=True)
    src_pkg_init = src_pkg / "__init__.py"
    src_pkg_init.write_text("", encoding="utf-8")
    written.append(src_pkg_init)

    domain_pkg = src_pkg / "domain"
    domain_pkg.mkdir(parents=True, exist_ok=True)
    domain_pkg_init = domain_pkg / "__init__.py"
    domain_pkg_init.write_text("", encoding="utf-8")
    written.append(domain_pkg_init)
    for name in DOMAIN_MODULES:
        src = REPO_ROOT / "src" / "domain" / name
        target = domain_pkg / name
        shutil.copyfile(src, target)
        written.append(target)

    config_pkg = src_pkg / "config"
    config_pkg.mkdir(parents=True, exist_ok=True)
    config_pkg_init = config_pkg / "__init__.py"
    config_pkg_init.write_text("", encoding="utf-8")
    written.append(config_pkg_init)

    for name in CONFIG_MODULES:
        src = REPO_ROOT / "src" / "config" / name
        if not src.exists():
            raise FileNotFoundError(f"Expected config module not found: {src}")
        target = config_pkg / name
        shutil.copyfile(src, target)
        written.append(target)

    return written


def _copy_data(dest_data: Path) -> list[Path]:
    """Copy elements.json and the localization JSONs into ``dest_data``."""
    dest_data.mkdir(parents=True, exist_ok=True)
    written = []

    elements_src = REPO_ROOT / "data" / "raw" / "elements.json"
    if not elements_src.exists():
        raise FileNotFoundError(f"Elements dataset not found: {elements_src}")
    elements_dst = dest_data / "elements.json"
    shutil.copyfile(elements_src, elements_dst)
    written.append(elements_dst)

    loc_dst = dest_data / "localization"
    loc_dst.mkdir(parents=True, exist_ok=True)
    for name in LOCALIZATION_FILES:
        src = REPO_ROOT / "data" / "localization" / name
        if not src.exists():
            raise FileNotFoundError(f"Localization file not found: {src}")
        target = loc_dst / name
        shutil.copyfile(src, target)
        written.append(target)

    return written


def _write_version(dest_root: Path) -> Path:
    """Generate ``version.js`` re-exporting the desktop ``APP_VERSION``.

    ``web/app.js`` imports ``APP_VERSION`` from this module so the version
    label in the browser header automatically tracks
    ``src.app_metadata.APP_VERSION``. Regenerating it on every deploy keeps
    the Pages site in sync with whatever tag the release workflow shipped.
    """
    target = dest_root / "version.js"
    target.write_text(
        f'export const APP_VERSION = "{APP_VERSION}";\n',
        encoding="utf-8",
    )
    return target


def build_web(dest_root: Path) -> dict[str, list[Path]]:
    """Populate ``dest_root`` with the generated portions of the web bundle.

    ``dest_root`` is the ``web/`` directory itself; its tracked sources
    (``index.html`` etc.) are left untouched. Returns a dict mapping each
    generated section to the paths it produced — useful for tests.
    """
    dest_root = Path(dest_root)
    dest_root.mkdir(parents=True, exist_ok=True)

    python_paths = _copy_python_modules(dest_root / "python")
    data_paths = _copy_data(dest_root / "data")
    tokens_path = export_tokens(dest_root / "design_tokens.json")
    version_path = _write_version(dest_root)

    return {
        "python": python_paths,
        "data": data_paths,
        "tokens": [tokens_path],
        "version": [version_path],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=REPO_ROOT / "web",
        help="Destination web/ root (default: ./web)",
    )
    args = parser.parse_args(argv)
    written = build_web(args.output)
    total = sum(len(paths) for paths in written.values())
    print(f"Built {total} files into {args.output}")
    for section, paths in written.items():
        print(f"  {section}: {len(paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
