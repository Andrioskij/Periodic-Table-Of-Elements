---
name: audit-data
description: Run the elements dataset audit and summarise the deltas. Use whenever the user changes data/ or asks for a dataset audit.
---

## Steps
1. Run: `python tools/audit_elements_dataset.py data/raw/elements.json data/reference/nomenclature_data.json`.
2. Read the generated `data/processed/elements_audit_report.md`.
3. If a previous report exists in git history (`git log -p data/processed/elements_audit_report.md`), summarise what changed (counts of duplicates, missing fields, missing nomenclature support).
4. Report back: counts, any new issues, and the location of `data/processed/elements_cleaned.json` for review.

Do not commit `data/processed/` outputs unless the user explicitly asks — they are derived artefacts.
