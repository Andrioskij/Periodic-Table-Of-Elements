# Cursor rules

This project's full agent contract lives in [`AGENTS.md`](../../AGENTS.md). Read it first.

Quick reminders:
- Test command: `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
- Lint command: `python -m ruff check .`.
- Layer rule: no `PySide6` imports inside `src/domain/` or `src/config/`.
- Localization: any new key must be added to all 7 JSONs under `data/localization/`.
