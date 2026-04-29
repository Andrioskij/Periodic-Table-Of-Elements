See [`AGENTS.md`](AGENTS.md) for layout, commands, and conventions.

Claude-specific notes:
- Always set `QT_QPA_PLATFORM=offscreen` in the Bash tool when touching PySide6.
- The full test suite is fast (~30s); prefer running it over guessing — `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
- For dataset changes, run `tools/audit_elements_dataset.py` and include the report diff in your final message.
- Three project skills are available under `.claude/skills/`: `bump-version`, `audit-data`, `verify-localization`.
