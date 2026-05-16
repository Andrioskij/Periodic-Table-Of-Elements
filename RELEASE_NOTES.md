# Release notes

## 1.4.2 "Chemistry Tool"

Added
- New "Metalloid" trend overlay button (desktop + web) emphasising only the metalloid band (B, Si, Ge, As, Sb, Te, Po). Localised in all 7 UI languages.

Changed
- "Metallic" / "Nonmetallic" / "Metalloid" trend overlays are now mutually exclusive: each mode keeps the categorical palette only for elements in its own macro-class and dims the rest. Previously toggling between Metallic and Nonmetallic changed only the arrow/label.

Removed
- "Affinity" trend overlay button. Electron affinity is still shown in the info panel; only the redundant band-style visualisation was retired.

## 1.4.1 "Chemistry Tool"

Fixes
- Web companion header now displays the correct app version. `web/app.js` had its own hardcoded `APP_VERSION` constant and silently stayed at `1.3.0` through the `1.4.0` release; the value is now generated into `web/version.js` by `tools/build_web.py` from `src.app_metadata.APP_VERSION`, so future tags propagate automatically.

## 1.4.0 "Chemistry Tool"

Highlights
- Web companion now exposes the full chemistry toolkit in the browser: a single Calculators modal groups molar mass, stoichiometry (with limiting-reagent + theoretical yield), concentration/dilution, gas laws, pH/pOH, and empirical/molecular formula.
- Dedicated web tabs for Lewis structures (multi-atom diagrams for ~22 molecules), compound builder (binary ionic with Stock nomenclature), solubility checker, electron configuration (with SVG orbital diagram), and periodic-table trend overlays (atomic radius, ionization energy, electronegativity, …).
- Search box over the periodic table (name / symbol / atomic number).
- Limiting-reagent + theoretical yield support in the desktop stoichiometry panel.

Changed
- Design tokens extracted to a shared config module: desktop and web read the same palette/spacing source, with web auto-fitting the viewport and matching the desktop chrome.
- `src.domain.stoichiometry` no longer depends on `sympy`; the balancer uses an internal rational solver, shrinking the Pyodide bundle and the desktop install footprint.

Fixed
- Web: `[hidden]` attribute now wins against author display rules, so hidden tabs stay hidden.

Quality
- Test suite: 498 tests, ruff clean.

## 1.3.0 "Chemistry Tool"

Highlights
- Lewis panel now renders multi-atom diagrams for ~22 common molecules (H2O, CO2, NH3, CH4, O2, …) via formula input.
- Parser error messages from the molar mass and stoichiometry tools are now localized in all 7 UI languages (en, it, es, fr, de, zh, ru).
- Molar mass and stoichiometry panels avoid redundant parse/balance work when re-rendering or recomputing masses.

Quality
- Test suite: 426 tests, ruff clean.

## 1.2.0 "Chemistry Tool"

Highlights
- Cross-platform delivery: Windows, macOS, and Linux portable bundles are now published to GitHub releases. Each release ships three zips named `...-win.zip`, `...-mac.zip`, and `...-linux.zip`.
- New `tools/build_unix.sh` build wrapper for macOS and Linux, mirroring the existing `tools/build_windows.ps1` (PyInstaller, offscreen smoke launch, zip).
- Release workflow now runs a 3-OS matrix build and publishes all artifacts to a single GitHub release.

## 1.1.0 "Chemistry Tool"

Highlights
- Molar-mass parser now accepts crystalline hydrate notation with `·` (U+00B7) or `.` as separator (e.g. `CuSO4·5H2O`, `Na2CO3·10H2O`).

## 1.0.1 "Chemistry Tool"

Fixes
- Formula parser now reads at most one lowercase letter after an uppercase, so malformed symbols like `NaaCl` are rejected at parse time with a clear error.
- `build_binary_formula` rejects zero charges explicitly, preventing nonsensical output and a `ZeroDivisionError`.
- Removed four decorative section banners in the solubility panel for visual consistency with the rest of the UI.

Quality
- Test suite expanded to 340 tests (3 new edge-case tests on the formula parser and compound builder).

## 1.0.0 "Chemistry Tool"

Highlights
- Light theme with a persistent user-selectable toggle (f241d9a).
- Localization files now lazy-loaded on demand instead of at startup (5d42c96).
- Compound builder hardened with explicit error handling and O(1) element lookup (4cda034).
- Reference-data loading distinguishes a missing file from a corrupted JSON payload (655aca6).
- Stylesheet caching and a no-op theme-reapply guard reduce redundant repaints (eaed084).
- Industrial-use categories localized across 7 UI languages (13d68a5).
- Accessibility improvements across the isotope and uses sections, the orbital diagram, and the solubility matrix (786a442).
- Supplementary element data externalized to JSON; coverage expanded to 61 elements (ab1dd71).

Quality
- Test suite expanded and now covers 337 tests (integration + unit).
- ruff lint baseline reduced to zero findings and enforced by a Windows CI gate (529ed47, d2d4b2b).
- Project configuration consolidated into pyproject.toml with ruff and pytest defaults (e37b9fc).
