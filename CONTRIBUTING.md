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

## Versioning
The canonical version is `src/app_metadata.APP_VERSION`. Don't hand-edit version strings elsewhere; reach for the `bump-version` skill (or open an issue) instead.

## Reporting a bug
Open a GitHub issue with the steps to reproduce, the expected behaviour, and the contents of the most recent log file under `%LOCALAPPDATA%\T_P_python\PeriodicTableApp\logs\` (Windows) or the equivalent platform path (see `docs/README_release_linux.txt` / `docs/README_release_mac.txt`).
