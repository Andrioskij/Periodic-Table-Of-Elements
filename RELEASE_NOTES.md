# Release notes

## 0.9.0 "Solubility Table"

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
