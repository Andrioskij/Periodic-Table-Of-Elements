# Contributing

Thanks for considering a contribution. This file is the human counterpart of
[`AGENTS.md`](AGENTS.md); the two are intentionally aligned.

## Quick start

```bash
python -m pip install -r requirements-test.txt
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q
python -m ruff check .
python -m src.main
```

## Pull request checklist

- [ ] `ruff` clean and the full test suite passes (`pytest tests/ -q`).
- [ ] If you touched a parser (`molar_mass`, `stoichiometry`, `compound_builder`), add at least one new edge-case test.
- [ ] If you touched anything user-visible, all 7 language JSONs under `data/localization/` are in sync.
- [ ] If you touched `data/`, the audit report diff is in the PR description.
- [ ] CHANGELOG.md updated under `## [Unreleased]`.

## Common pitfalls

A few traps that have bitten this codebase before and aren't obvious from the file structure.

- **Adding a key to one localization JSON without the other six.** `data/localization/` ships `en.json`, `it.json`, `es.json`, `fr.json`, `de.json`, `zh.json`, `ru.json`. The lookup falls back to the raw token at runtime, so a missing key doesn't crash — it just renders the literal string (e.g. `"trend_button_metalloid"`) in the UI for users of the missing language. The bug is silent and hard to spot in EN-only review. **Always add the new key to all 7 files, even if you only translate it for EN and leave the others as TODOs**: a placeholder English value is still better than a raw token leaking through.

- **Using `assert` for input validation.** AGENTS.md forbids this and CI now enforces it: the `lint-test` job runs pytest twice, once normally and once with `python -O`. Asserts are stripped under `-O`, so a load-bearing `assert isinstance(x, int)` becomes a no-op in optimized builds (PyInstaller bundles often run optimized). If your `-O` pytest step fails while the regular one passes, you have an assert that's silently doing real work — replace it with `if not ...: raise ValueError(...)`. Reserve `assert` for invariants the type system can't express ("this dict was just populated by a function that always returns the same keys").

- **The `·` (U+00B7) vs `.` hydrate separator in `molar_mass.parse_formula`.** Both `CuSO4·5H2O` and `CuSO4.5H2O` are accepted, but the UI placeholder only shows one. If you add a hydrate-related test or example, prefer the U+00B7 form (it's what chemistry textbooks use); copy it from existing tests rather than typing it, since middle-dot is easy to mistype as a period.

- **Importing from `src.ui.*` inside `src/domain/` or `src/services/`.** The layer rule in AGENTS.md is one-directional: UI can depend on services and domain, but not the other way around. A violation usually doesn't fail tests immediately but breaks the Pyodide web build (which imports domain modules in a Qt-less environment). Run `python -c "from src.domain import molar_mass"` to spot-check there's no transitive PySide6 import.

- **Bumping `pyproject.toml` by hand.** Don't. `pyproject.toml` reads its version dynamically from `src.app_metadata.APP_VERSION`. If you change one and not the other, the contract test in `tests/test_app_metadata.py` catches it — but the cleaner workflow is to only ever edit `APP_VERSION` and let the dynamic resolver do the rest. The `bump-version` skill walks you through all the other files that *do* need updating (README, CHANGELOG, release docs).

## Versioning
The canonical version is `src/app_metadata.APP_VERSION`. Don't hand-edit version strings elsewhere; reach for the `bump-version` skill (or open an issue) instead.

## Reporting a bug
Open a GitHub issue with the steps to reproduce, the expected behaviour, and the contents of the most recent log file under `%LOCALAPPDATA%\T_P_python\PeriodicTableApp\logs\` (Windows) or the equivalent platform path (see `docs/README_release_linux.txt` / `docs/README_release_mac.txt`).
