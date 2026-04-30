# CLAUDE.md

Operational notes for coding agents working on this repository. Keep it short
and accurate; do not turn it into a manual.

## Project overview

PySide6 desktop app for exploring the periodic table. The app combines element
data, quick property trends, electron configuration, compound nomenclature,
and a molar-mass calculator with crystalline hydrate notation
(e.g. `CuSO4·5H2O`). Cross-platform delivery: Windows / macOS / Linux portable
zips published to GitHub releases. No installer, no code signing.

## Architecture

- Public entry point: `python -m src.main` → re-exports + `src.bootstrap.run`.
- Real lifecycle lives in [`src/bootstrap.py`](src/bootstrap.py): logging,
  data loading, MainWindow, optional smoke-exit timer.
- Single source of truth for version / bundle name:
  [`src/app_metadata.py`](src/app_metadata.py).
- Layered layout under `src/`:
  - `src/config/` — static lookups, no I/O, no Qt.
  - `src/domain/` — pure logic (parsers, trends, nomenclature, solubility,
    stoichiometry, molar mass). Must not import from `src/ui/*`.
  - `src/services/` — JSON loaders, localization, settings, isotopes.
  - `src/ui/` — Qt widgets. `main_window.py` is the orchestrator;
    builders/managers/panels keep it sliceable.
- Right-side panels (info, electron config, molar mass, solubility,
  stoichiometry, lewis, compound, orbital diagram) live in
  [`src/ui/panels/`](src/ui/panels/).
- Read-only datasets in `data/raw/`, `data/reference/`, `data/localization/`.
- Tests in [`tests/`](tests/). UI tests under `tests/ui/` need
  `QT_QPA_PLATFORM=offscreen`.

## Build & test

Install the runtime / test set:

```bash
python -m pip install -r requirements-test.txt
```

Run the full suite (lint and tests must stay green):

```bash
python -m ruff check .
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q
```

Run the app locally:

```bash
python -m src.main
```

Build a portable bundle (PyInstaller via the shared `PeriodicTableApp.spec`,
both wrappers also run an offscreen smoke launch before zipping):

- Windows: `powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean`
- macOS / Linux: `bash tools/build_unix.sh --clean`

Outputs land under `dist/release/PeriodicTableApp-<version>-chemistry-tool-{win,mac,linux}.zip`.

## Release workflow

Releases are tag-driven. To cut `vX.Y.Z`:

1. Bump `APP_VERSION` in [`src/app_metadata.py`](src/app_metadata.py).
2. Add a `## [X.Y.Z] - YYYY-MM-DD` entry on top of
   [`CHANGELOG.md`](CHANGELOG.md) (Keep a Changelog format, with
   `[X.Y.Z]: ...compare/...` link at the bottom).
3. Add a `## X.Y.Z "<codename>"` section on top of
   [`RELEASE_NOTES.md`](RELEASE_NOTES.md). The first matching block is what
   `tools/extract_release_notes.py` ships to the GitHub release body.
4. Update the `Release target` line in [`README.md`](README.md) and the
   per-OS `docs/README_release_*.txt` if they reference a version.
5. Commit, tag `vX.Y.Z`, push tag.

The matrix workflow [`.github/workflows/release.yml`](.github/workflows/release.yml)
resolves metadata, builds on `windows-latest` / `macos-latest` /
`ubuntu-latest`, and publishes all three zips to a single GitHub release.
`workflow_dispatch` exposes `tag`, `source_ref`, and `upload` inputs for
re-running the build against a branch and (optionally) re-uploading assets to
an existing release — handy for validating workflow changes before tagging.

## Conventions

- Conventional Commits in English (`feat:` / `fix:` / `docs:` / `ci:` /
  `chore:` / `release:`), imperative mood, capital after the colon.
- **No AI attribution anywhere**: no `Co-Authored-By` lines for AI models,
  no "Generated with ..." footers, no AI mentions in commits, PR
  descriptions, code, or docs.
- Versioning is synchronized in three places — keep them in lockstep:
  `src/app_metadata.APP_VERSION`, `CHANGELOG.md`, `RELEASE_NOTES.md`
  (top section).
- Atomic commits per task — do not bundle unrelated changes.
- `domain/` and `config/` must not import `PySide6`.
- New user-visible strings go through `tr(key)` in
  `src.services.localization_service`. New keys must land in **all 7**
  localization JSONs (`en, it, es, fr, de, zh, ru`).
- Logging via `logging.getLogger(__name__)`. No `print()` in `src/`.
- Keep the test suite green. New Python logic ships with tests. Current
  baseline: 356 tests.

## File layout pointers

- [`src/app_metadata.py`](src/app_metadata.py) — version, bundle name,
  build metadata.
- [`src/bootstrap.py`](src/bootstrap.py) — application lifecycle, smoke
  exit timer (`PERIODIC_TABLE_SMOKE_EXIT_MS`).
- [`src/domain/molar_mass.py`](src/domain/molar_mass.py) — formula parser
  (parentheses, nested groups, hydrate `·` U+00B7 / `.` separator).
- [`tools/extract_release_notes.py`](tools/extract_release_notes.py) — used
  by the release workflow to ship the top section of `RELEASE_NOTES.md`.
- [`tools/build_windows.ps1`](tools/build_windows.ps1),
  [`tools/build_unix.sh`](tools/build_unix.sh) — packaging wrappers around
  `PeriodicTableApp.spec`.
- [`.github/workflows/release.yml`](.github/workflows/release.yml) —
  3-OS matrix release.
- [`.github/workflows/windows-ci.yml`](.github/workflows/windows-ci.yml) —
  PR / push CI: ruff + pytest on Linux, build on Windows.
- [`.github/dependabot.yml`](.github/dependabot.yml) — weekly pip and
  GitHub Actions updates.
- [`packaging/`](packaging/) — distro packaging recipes (Homebrew tap,
  AUR PKGBUILD) staged here for publication to their respective registries.
