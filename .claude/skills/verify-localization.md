---
name: verify-localization
description: Verify all 7 localization JSONs share the same keyset. Use after any localization change or when the user asks to check translations.
---

## Steps
1. Load every file under `data/localization/*.json` (expected: en, it, es, fr, de, zh, ru).
2. Take English (`en.json`) as the reference set.
3. For each other language, compute:
   - `missing = en_keys - lang_keys`
   - `extra   = lang_keys - en_keys`
4. Report a markdown table: `| lang | missing | extra |`.
5. If everything is in sync, say so in one line.

Don't modify the files; surface the diff so the maintainer (or another agent) can fix the gaps.
