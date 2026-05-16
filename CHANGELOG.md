# Changelog

All notable changes to this project will be documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New "Metalloid" trend overlay button (desktop + web) that emphasises only the metalloid band (B, Si, Ge, As, Sb, Te, Po) and dims the rest of the table to the UI fallback. Adds the `trend_button_metalloid`, `metalloid_arrow`, and `current_view_metalloid` keys across all 7 UI languages.

### Changed
- "Metallic" / "Nonmetallic" / "Metalloid" trend overlays are now mutually exclusive bands: each mode keeps the categorical palette only for elements in its own macro-class and dims the rest. Previously both directional modes produced the same palette as "Normal" on desktop and a symmetric 2-color lerp on web, so toggling between them changed only the arrow/label. Affects `src/ui/styles.py`, `src/ui/widgets/trends_overlay.py`, and `web/app.js`.

### Removed
- "Affinity" trend overlay button (desktop + web). Electron affinity is still shown in the info panel; only the redundant trend visualisation was retired to make room for the new exclusive band buttons.

## [1.4.1] - 2026-05-15

### Fixed
- Web companion header now displays the correct app version. `web/app.js` had its own hardcoded `APP_VERSION` constant and silently stayed at `1.3.0` through the `1.4.0` release; the value is now generated into `web/version.js` by `tools/build_web.py` from `src.app_metadata.APP_VERSION`, so future tags propagate automatically.

## [1.4.0] - 2026-05-15

### Added
- Web companion frontend served from `web/` and deployed to GitHub Pages. The browser UI re-uses the desktop's Python logic via Pyodide and consumes the canonical design tokens for visual parity.
- Web Calculators modal grouping all chemistry tools behind a single launcher: molar mass, stoichiometry (with limiting-reagent + theoretical yield), concentration/dilution, gas laws, pH/pOH, and empirical/molecular formula.
- Web Lewis structures tab (multi-atom diagrams for ~22 common molecules via formula input).
- Web compound builder tab (binary ionic compounds with Stock nomenclature).
- Web solubility checker tab.
- Web electron-configuration tab with an SVG orbital diagram.
- Web search box (name / symbol / atomic number) over the periodic table.
- Web trend overlays on the periodic table (atomic radius, ionization energy, electronegativity, etc.).
- Limiting-reagent + theoretical yield support in `src.domain.stoichiometry` (also surfaced in the desktop stoichiometry panel).
- `tools/export_design_tokens.py` and `tools/build_web.py` to assemble the web bundle on every deploy from `src/` as the single source of truth.
- `.github/workflows/deploy-web.yml` Pages deploy workflow.

### Changed
- Design tokens extracted to a shared config module so desktop and web read the same palette/spacing source.
- Web periodic table auto-fits the viewport width and the layout chrome matches the desktop app.
- Stoichiometry domain no longer depends on `sympy`; the balancer uses an internal rational solver, shrinking the Pyodide bundle and the desktop install footprint.

### Fixed
- Web: `[hidden]` attribute now wins against author display rules, so hidden tabs stay hidden.

### Quality
- Test suite: 498 tests, ruff clean.
- Three trailing magic numbers in the web layout tokenised against the shared design tokens.

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

[Unreleased]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.1...HEAD
[1.4.1]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/releases/tag/v1.0.0
