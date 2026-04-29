# Release notes

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
