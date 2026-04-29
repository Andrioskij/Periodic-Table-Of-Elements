# Copilot Chat instructions

This project's full agent contract lives in [`../AGENTS.md`](../AGENTS.md). Read it first.

When suggesting code:
- Prefer pytest-style tests (plain `def test_*`); don't add new `unittest.TestCase` classes.
- Use `logging.getLogger(__name__)` instead of `print()`.
- User-visible strings must go through `tr(key)` from `src.services.localization_service`.
- Versions live in `src/app_metadata.APP_VERSION`; never hard-code a version string elsewhere.
