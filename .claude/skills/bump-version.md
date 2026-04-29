---
name: bump-version
description: Bump the application version consistently across the repo. Use this whenever the user asks to release vX.Y.Z, bump version, or prepare a release.
---

You are bumping the canonical project version. The single source of truth is `src/app_metadata.py::APP_VERSION`.

## Inputs
The user will give you a target version like `1.3.0` (no `v` prefix).

## Required changes (all in one PR)
1. `src/app_metadata.py`: update `APP_VERSION = "<new>"`.
2. `README.md`: update the line `Release target: \`<new> "Chemistry Tool"\``.
3. `CHANGELOG.md`: open a new section `## [<new>] - YYYY-MM-DD` above `## [Unreleased]` and move the unreleased entries down.
4. `RELEASE_NOTES.md`: prepend a new `## <new> "Chemistry Tool"` section with one-line highlights.
5. `docs/README_release_windows.txt`, `docs/README_release_mac.txt`, `docs/README_release_linux.txt`: update the `Version <new> "Chemistry Tool"` line.
6. (Optional but recommended) `pyproject.toml`: update `version = "<new>"` so the wheel metadata matches.

## Verification
- Run `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`. The test in `tests/test_app_metadata.py` is the safety net.
- Grep for the previous version: `grep -rn "<old>" --include='*.py' --include='*.md' --include='*.txt' --include='*.toml'`. Each remaining hit must be inside a CHANGELOG section, a docstring example, or a release-notes entry — never the live config.

## Out of scope
- Don't tag the release. The maintainer pushes the tag manually; the GitHub Actions release workflow takes over from there.
