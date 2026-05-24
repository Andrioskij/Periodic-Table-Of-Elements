# Changelog

All notable changes to this project will be documented here. Format based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.1] - 2026-05-23

A same-day patch on top of v1.5.0 that closes a real user-reported bug in the web Compound Builder and finally brings the web side to nomenclature parity with the desktop.

### Fixed
- **Web Compound Builder no longer errors with `"undefined" is not valid JSON`** when calculating a binary formula (#80). Root cause: `pyodide.runPython` returns the value of the last top-level *statement*, and a `try/except` is a compound statement, not an expression; a script whose last top-level statement is a `try/except` block returns `None` → `undefined` in JS → `JSON.parse(undefined)` is coerced to `JSON.parse("undefined")`, which V8 reports as the observed error. Rewrites all 6 calculator-bridge `runPython` scripts (`buildBinaryFormula`, `balanceEquation`, `computeStoichiometricMasses`, `computeEmpiricalFormula`, `computeLimitingReagent`, `computeMolarMass`) to build the payload inside the try/except branches and serialise it on a bare `json.dumps(payload)` last line, which Pyodide's CodeRunner extracts and evaluates. A comment block in `buildBinaryFormula` documents the gotcha so the pattern isn't reintroduced.

### Added
- **Web Compound Builder shows IUPAC Stock + traditional names** alongside the binary formula (#81), closing the long-standing desktop ↔ web parity gap. Examples: `NaCl` → "sodium chloride" / "cloruro di sodio"; `FeCl3` → "iron(III) chloride" / "ferric chloride" / "cloruro ferrico". `tools/build_web.py::_copy_data` now also copies `data/reference/nomenclature_data.json` (byte-identity test guards against drift); `web/app.js` ships an `intToRoman` helper and a `computeNomenclatureNames` function that follows the same Stock_simple / Stock_roman / traditional-suffix flow as the desktop's `build_stock_name` + `build_traditional_name`, entirely client-side (no Pyodide round-trip — the naming logic is template substitution + Roman numerals + suffix matching). Reuses existing `stock_name`/`traditional_name`/`traditional_na` localization keys — zero new translations.

### Refactor
- **`LanguageController` extracted from `MainWindow`** (#82, IMP-001 chunk #3). Mirrors the ThemeController + ResponsiveLayoutController extractions from chunks #1 and #2: pulls `sync_language_selector`, the body of `change_language`, and the first line of `load_preferences` into a dataclass façade with a small testable surface (`load_from_settings`, `sync_selector`, `change_to(code) -> bool`). `MainWindow.tr()` and `apply_language()` deliberately stay where they are because they're either called from `_assemble_layout` (before the controller can exist) or fan out to ~10 siblings. 11 new unit tests using pure-Python fakes — no Qt dependency.

## [1.5.0] - 2026-05-23

A "Calculator UX" release: the eight web calculators get help popups, pre-filled examples, polished tabs and result cards; the desktop pannelli get the same help popups and pre-filled examples; the side panels gain atom-glyph empty states; and the table grows two big new features — a multi-element comparison view and a first-visit guided tour.

### Added
- **Web Calculators help popups**. Each of the 8 calculators in the Calculators modal (Molar mass, Stoichiometry, Concentration, Gas laws, pH, Empirical, Builder, Solubility) grows a circular `?` button in the top-right corner that opens a small modal stacked above the Calculators modal explaining what the tool does, how to use it, and showing a worked example. Body content is plain text with `\n\n` paragraph splitting and backtick-delimited inline `code`; rendering is XSS-safe (textContent, never innerHTML). 8 new `*_help_body` localization keys × 7 langs.
- **Desktop Calculators help popups** (mirror of the web). `MolarMassPanel`, `StoichiometryPanel`, `CompoundBuilderPanel`, `SolubilityPanel` each grow a `?` `QToolButton` next to the title that opens a shared `HelpDialog` (`src/ui/help_dialog.py`) populated from the same `*_help_body` localization keys — zero new translations.
- **"Try example" button** in every calculator (web 8 + desktop 4). A soft, italic, ghost-styled secondary button that pre-fills the form with a typical, chemistry-meaningful example (`CuSO4·5H2O` for molar mass, `Fe + O2 -> Fe2O3` for stoichiometry, NaCl 5 g in 100 mL for concentration, gas at STP, pH 7.0, H/O for empirical, Na+1/Cl-1 for builder, Ag⁺/Cl⁻ for solubility). Synergy with the `?` popups — help explains *what*, example demonstrates *how*. Single new `example_button` localization key × 7 langs.
- **Atom-glyph empty state** on the 3 side panels (Info, Electron config, Lewis). Before an element is selected, each panel shows a small inline-SVG atom illustration (three rotated ellipses + a nucleus) above the existing "Select an element..." prompt so the panel reads as a deliberately-empty space waiting to be filled, not a blank rectangle. SVG uses `currentColor` so it inherits the muted text color and works in both themes without extra rules.
- **Element comparison view**. New "Compare" toggle in the topbar enters a multi-select mode that lets the user pick up to 3 elements from the table; their picks get an accent outline and the toggle button shows a count badge. Once 2+ are picked, a "View" button opens a comparison modal with a side-by-side table — 1 row per `INFO_FIELDS` property × 1 column per picked element, with category-tinted symbol badges in the header. Property labels reuse existing i18n keys (`atomic_number`, `category`, etc.) so the table body needs no new translations. 6 new `compare_*` localization keys × 7 langs.
- **First-visit onboarding tour**. New visitors are greeted by a 5-step tour (welcome → Calculators → Compare → Language → Theme) gated on `localStorage.pte_onboarded`. The tour dims the page with a single 9999px-spread `box-shadow` on a highlight rectangle (simpler than `clip-path`, works everywhere); on sub-600px viewports the popover docks to the viewport bottom-centre instead of trying to fit next to the highlight. Skip / ESC end the tour early and still set the flag so it never re-shows. 13 new `tour_*` localization keys × 7 langs.
- **Web Calculators tab icons + per-panel titles + accent result cards** (visual polish). Each of the 8 tabs gets a leading emoji (🧮 ⚖️ 💧 🌡️ 🧪 🔬 🧱 🌊); each panel grows an `<h3>` title; `.molar-result` and `.stoich-balanced` get an accent-yellow top border + subtle box-shadow so the output region reads as distinct from the form.
- **Desktop calculator panel title icons** mirroring the web tabs. New `CalculatorIcons` class in `src/ui/constants.py` (`MOLAR=🧮`, `STOICHIOMETRY=⚖️`, `BUILDER=🧱`, `SOLUBILITY=🌊`) is prepended to each panel's title at the `apply_language` call site. `CompoundBuilderPanel` gained the master title slot that finally consumes the existing `builder_title` localization key.
- **`OrbitalDiagramPanel` lifecycle smoke tests** (`tests/ui/test_orbital_diagram_panel.py`, 8 new tests). Covers instantiation, `set_prompt`, `apply_theme` (no-op + palette switch + redraw after prior render), `show_orbital_diagram` happy path + missing-config fallback. Closes the last "untested panel" backlog item.
- **`HelpDialog` unit tests** (`tests/ui/test_help_dialog.py`, 15 tests): 8 for `format_help_body` (paragraph split, backtick code extraction, HTML escape) + 7 for the dialog (title/body/close-button/modal/accept).
- **`ThemeController` and `ResponsiveLayoutController`** extracted from `MainWindow` (IMP-001 chunks #1 and #2). View-holder pattern: each controller takes a window ref and exposes a single public method (`toggle_and_persist` / `apply`). `MainWindow` shed ~95 LOC of responsive-layout helpers plus 5 theme-related methods.

### Changed
- **Web Calculators modal layout**. Tabs now lay out as a 4×2 grid (`display: grid; grid-template-columns: repeat(4, minmax(0, 1fr))`) so the longest labels can't overflow the card; modal max-width bumped from 720px to 920px. The old `≤720px` horizontal-scroll fallback is gone (no longer needed); below 720px the grid collapses to 2 columns. Fixes a real bug where "Simple compounds" overflowed and "Solubility" was hidden off-screen at desktop widths.

### Performance
- **Localization lookup memoization**. `_get_localized_lookup_text` and siblings in `src/services/ui_localization.py` are now wrapped in `functools.cache`, keyed on `(language, value)`. Per-element-render dict walks become O(1) after the first hit; the cache is bounded by the cardinality of the localized values (categories, standard states, etc.) so it never grows unboundedly.

### Refactor
- **`compute_numeric_ranges` duplication removed**. `MainWindow` was recomputing what `self.context.trend_manager.numeric_ranges` already had cached at AppContext init; the method is gone and call sites read the context value directly.

### CI / docs / tooling
- **`python -O -m pytest` step in Windows CI**. A second pytest pass under optimisation strips `assert` statements, so any `assert` accidentally used for input validation surfaces as a regression in CI instead of in production-under-`-O`.
- **Common pitfalls section in `CONTRIBUTING.md`**: the 7-JSON localization rule, the `-O` assert trap, the U+00B7 hydrate-separator convention, the panel-layer rule, and the `pyproject.toml` dynamic version.
- **`CuSO4·5H2O` hydrate example** added to the `molar_prompt` placeholder text across all 7 languages so the U+00B7 convention is discoverable without reading the docs.

### Documentation
- **Onboarding tour** is gated on `localStorage.pte_onboarded`; to re-see it open DevTools and run `localStorage.removeItem("pte_onboarded")`, then reload.

## [1.4.5] - 2026-05-21

### Added
- Browser tab favicon for the GitHub Pages web companion. `tools/build_web.py` now copies `assets/app.ico` and the matching PNG set (16/32/48/128/256) into a gitignored `web/icons/` directory at deploy time, and `web/index.html` references them via `<link rel="icon">` and `<link rel="apple-touch-icon">`. The Pages tab and the iOS home-screen install prompt now show the same icon the desktop `.exe` ships with instead of the default browser globe. `deploy-web.yml` triggers expanded to `assets/app*` so a future icon swap auto-redeploys.
- `border.selected_glow_blur = 8` design token, projected to `web/design_tokens.json` by the existing exporter for future cross-platform use.

### Changed
- Desktop periodic table now sources its grid spacing, cell padding, and element-button font size from `TOKENS` (`spacing.grid_gap_desktop`, `spacing.element_cell_padding_y_min`, `font.size.button_default`) instead of hardcoded literals in `MainWindow`, `PeriodicTableWidget`, and `styles.py`. Tuning a token now updates desktop and web simultaneously, closing the last three drift surfaces left after the v1.4.4 web-side parity pass.
- Selected periodic-table cell on desktop now shows a theme-aware accent halo (yellow `#FFD60A` on dark, blue `#1565c0` on light) via `QGraphicsDropShadowEffect`, mirroring the web `.element-cell.is-selected { box-shadow: 0 0 0 1px var(--color-accent) }` rule. The halo color tracks the active theme automatically on toggle.

## [1.4.4] - 2026-05-18

### Added
- `spacing.grid_gap_desktop = 4` design token, shared between desktop and web, so the periodic table grid gap is tunable from one place.

### Changed
- Web companion periodic table cells now mirror the desktop PySide6 look: 1:1 aspect ratio with the atomic number and symbol centered and tightly stacked, uniform padding, bold non-faded number, 4px grid gap, and no hover elevation.

### Fixed
- iOS Safari / Chrome Android no longer auto-zoom the web companion when a form control receives focus. `input`, `select`, `textarea`, `.molar-input`, and `.control-input` are pinned to `16px` inside the `≤480px` breakpoint, defeating the sub-16px zoom heuristic without resorting to `user-scalable=no`.
- Calculators modal on phones now lays out its tabs as a visible 2-column grid (previously a horizontally-scrolling row hid 5 of 8 calculators), the modal title shrinks from 24px to 16px, and `.molar-form` stacks vertically so the input gets full width when the soft keyboard appears.
- Periodic table portrait view no longer scrolls horizontally at iPhone SE (320px) widths: the `min-width: clamp(18px, 5cqi, 40px)` floor introduced for the desktop cell-parity look is now cancelled inside the mobile `@media (max-width: 480px)` block, so the `grid-template-columns: repeat(18, minmax(0, 1fr))` shrink behaviour the portrait layout relies on is preserved.
- `deploy-web.yml` now triggers on changes to `src/app_metadata.py`, so a version-only bump commit (touching only `app_metadata.py` / `pyproject.toml` / `CHANGELOG.md` / `README.md` / docs txt) automatically redeploys the web bundle instead of leaving the Pages header stale until a manual `workflow_dispatch`.

## [1.4.3] - 2026-05-16

### Fixed
- Web companion now lays out correctly on smartphone browsers. Adds a defensive `body { overflow-x: hidden }` so iOS Safari can't expand the visual viewport past `device-width` if a descendant overflows, lets the Calculators modal tabs scroll horizontally on `≤720px` instead of collapsing, and adds a `≤480px` breakpoint that tightens the topbar title, trend buttons, and the "TRANSITION METALS" band.
- Periodic table in smartphone portrait now renders as a compact grid of square symbol-only cells. Below 480px, period/series labels, group headers (IA…VIIIA), the "TRANSITION METALS" overlay, and the per-cell atomic number are hidden; the column gap drops to a new `spacing.grid_gap_mobile = 1` token and cell padding/radius shrink to matching mobile tokens; cells gain `aspect-ratio: 1 / 1` so the previous 2:1 pill effect is gone; the symbol pins to a new `font.size.element_symbol_mobile_floor = 12` and centres in the cell. All 18 columns still fit without horizontal scroll.

## [1.4.2] - 2026-05-16

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

[Unreleased]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.5...HEAD
[1.4.5]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.4...v1.4.5
[1.4.4]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.3...v1.4.4
[1.4.3]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.2...v1.4.3
[1.4.2]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Andrioskij/Periodic-Table-Of-Elements/releases/tag/v1.0.0
