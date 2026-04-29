# Agent guide — Periodic Table Of Elements

Vendor-neutral onboarding for any coding agent (Claude Code, Cursor, Aider,
Codex, Copilot Chat, Cline, Continue, Windsurf). Read this once, then act.

## Stack
- Python 3.14, PySide6 6.11, sympy 1.13.
- PyInstaller 6.19 for portable bundles (Windows, macOS, Linux).
- ruff for lint. Tests are written with `unittest.TestCase` but discovered by pytest.

## Layout (read in this order)
- `src/main.py` — facade re-exports; the real entry point is `src.bootstrap.run`.
- `src/bootstrap.py` — application lifecycle, logging, optional smoke-exit timer.
- `src/app_metadata.py` — **single source of truth for version/name**.
- `src/config/` — static lookups (no I/O, no Qt).
- `src/domain/` — pure logic: parsers, formulas, trends, nomenclature, solubility.
- `src/services/` — JSON loaders, localization, settings, isotopes.
- `src/ui/` — Qt widgets. `main_window.py` is the orchestrator (large, see ARCHITECTURE.md).
- `src/ui/managers/` — search/trend/compound state held outside MainWindow.
- `src/ui/panels/` — right-side detail views.
- `src/ui/widgets/` — reusable widgets (FlowLayout, TrendsOverlay, periodic table grid).
- `data/` — read-only datasets (raw/, reference/, localization/).
- `tests/` — unit tests; `tests/ui/` needs `QT_QPA_PLATFORM=offscreen`.

See `ARCHITECTURE.md` for the layer-import rules and the Manager/Builder/Context patterns.

## Commands

| Action               | Command                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Install (test)       | `python -m pip install -r requirements-test.txt`                              |
| Install (dev)        | `python -m pip install -r requirements-dev.txt -r requirements-test.txt`      |
| Lint                 | `python -m ruff check .`                                                      |
| Test (all)           | `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`                        |
| Test (single)        | `python -m pytest tests/test_compound_builder.py::TestBuildBinaryFormula::test_nacl` |
| Run app              | `python -m src.main`                                                          |
| Audit dataset        | `python tools/audit_elements_dataset.py data/raw/elements.json data/reference/nomenclature_data.json` |
| Build (Windows)      | `powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean`     |
| Build (macOS/Linux)  | `bash tools/build_unix.sh --clean`                                            |

CI uses pytest with `QT_QPA_PLATFORM=offscreen`; do the same locally.

## Conventions
- 4-space indent. ruff-enforced (E, W, F, I, B, UP — `E501` and `B008` are ignored).
- `src/domain/` and `src/config/` MUST stay free of `PySide6` imports.
- New tests should follow pytest style (plain `def test_*`, fixtures); don't add new `unittest.TestCase` classes.
- User-visible strings go through `tr(key)` from `src.services.localization_service`.
- Logging via `logging.getLogger(__name__)` — no `print()` in `src/`.
- `assert` is stripped under `python -O`; use it for invariants only, never for input validation.
- New localization keys must be added to **all 7** JSONs in `data/localization/` (en, it, es, fr, de, zh, ru).

## Versioning
- The canonical version lives at `src/app_metadata.APP_VERSION`.
- When bumping, also update: `README.md` ("Release target" line), `CHANGELOG.md`, `RELEASE_NOTES.md`, `docs/README_release_*.txt`.
- `pyproject.toml` currently lags — opening a PR that fixes it (dynamic version) is welcome but out of scope for routine work.
- Tag format: `v<major>.<minor>.<patch>` (e.g. `v1.2.0`). The release workflow rejects mismatches.

## Don'ts
- Don't introduce new `print(...)` calls in `src/`.
- Don't widen `assert` use as a validation mechanism.
- Don't add a key to one localization JSON without adding all 7.
- Don't import from `src.ui.*` inside `src/domain/*` or `src/services/*`.
- Don't run `tools/build_windows.ps1` outside Windows; use `tools/build_unix.sh` on macOS/Linux.
- Don't commit anything under `dist/`, `build/`, or `.test_runtime/`.

## Parser surface (high-risk for agents)
The functions below are parsers and must keep accepting their full grammar.
Run their dedicated tests **before and after** any change:
- `src.domain.molar_mass.parse_formula` — supports parentheses, nested groups, and hydrate notation (`·` U+00B7 or `.` separator). Tests: `tests/test_molar_mass.py`.
- `src.domain.stoichiometry.parse_equation` — supports `->`, `→`, `=` separators. Tests: `tests/test_stoichiometry.py`.
- `src.domain.compound_builder.parse_oxidation_states` and `build_binary_formula` — non-zero charges only, sorted positive-then-negative. Tests: `tests/test_compound_builder.py`.

## When opening a PR
1. Run lint + tests locally.
2. State the scope in the PR description (what changed and why).
3. If you touched `data/`, run `tools/audit_elements_dataset.py` and paste the diff vs. the prior report.
4. Don't bundle unrelated cleanups; one concern per PR.
