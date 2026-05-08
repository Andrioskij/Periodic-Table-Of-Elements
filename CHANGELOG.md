# Changelog

All notable changes to this project will be documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Web companion frontend served from `web/` and deployed to GitHub Pages. The browser UI re-uses the desktop's Python molar-mass logic via Pyodide and consumes the canonical design tokens for visual parity. V1 scope: periodic table grid, element info card, molar mass calculator, light/dark theme switcher, 7-language picker.
- `tools/export_design_tokens.py` and `tools/build_web.py` to assemble the web bundle on every deploy from `src/` as the single source of truth.
- `.github/workflows/deploy-web.yml` Pages deploy workflow.

## [1.3.0] - 2026-05-07

### Added
- Lewis panel now renders multi-atom diagrams for ~22 common molecules (H2O, CO2, NH3, CH4, O2, …) via formula input.

### Changed
- Parser error messages (molar mass, stoichiometry) are now localized in all 7 UI languages.
- Molar mass and stoichiometry panels avoid redundant parse/balance work when re-rendering or recomputing masses.

## [1.2.0] - 2026-04-29

### Added
- Cross-platform delivery: Windows, macOS, and Linux portable bundles published to GitHub releases. Per-OS zip naming (`...-win.zip`, `...-mac.zip`, `...-linux.zip`).
- `tools/build_unix.sh` build wrapper for macOS and Linux, mirroring `tools/build_windows.ps1` (PyInstaller, offscreen smoke launch, zip).
- Release workflow now runs a 3-OS matrix build and publishes all artifacts to a single GitHub release.

### Changed
- `get_release_bundle_name()` accepts an optional `os_suffix` argument so per-OS bundles can coexist on the same release.
- `PeriodicTableApp.spec` produces a `.app` bundle on macOS and skips the Windows-only `.ico` icon on macOS/Linux.

## [1.1.0] - 2026-04-29

### Added
- Crystalline hydrate notation support in the molar-mass parser, accepting `·` (U+00B7) or `.` as separator (e.g. `CuSO4·5H2O`, `Na2CO3·10H2O`, `Al2(SO4)3·18H2O`).
- Tag-triggered auto-release workflow (Windows portable bundle uploaded as release asset).
- Linux lint + test CI job running in parallel with the Windows build for faster feedback.
- Dependabot configuration for pip and GitHub Actions, weekly schedule.

## [1.0.1] - 2026-04-29

### Fixed
- Formula parser now reads at most one lowercase letter after an uppercase, so malformed symbols like `NaaCl` are rejected at parse time with a clear error.
- `build_binary_formula` rejects zero charges explicitly, preventing nonsensical output and a `ZeroDivisionError`.

### Changed
- Removed four decorative section banners in the solubility panel for visual consistency.
- Renamed packaging icon folder from `assets_/` to `assets/` so the dev environment also locates the icon.

### Quality
- Test suite expanded to 340 tests (3 new edge-case tests on the formula parser and compound builder).

## [1.0.0] - 2026-04-28

### Added
- Light theme with persistent user-selectable toggle.
- Industrial-use categories localized across 7 UI languages.
- Solubility matrix panel with rule descriptions and exception lookup.
- Compound builder for binary ionic compounds with Stock nomenclature.
- Stoichiometry equation balancer.

### Changed
- Localization files lazy-loaded on demand instead of at startup.
- Compound builder hardened with explicit error handling and O(1) element lookup.
- Reference-data loading distinguishes a missing file from a corrupted JSON payload.
- Stylesheet caching and a no-op theme-reapply guard reduce redundant repaints.
- Supplementary element data externalized to JSON; coverage expanded to 61 elements.

### Quality
- Test suite covers 337 tests (integration + unit).
- ruff lint baseline reduced to zero findings and enforced by Windows CI.
- Project configuration consolidated into pyproject.toml.

[Unreleased]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/releases/tag/v1.0.0
