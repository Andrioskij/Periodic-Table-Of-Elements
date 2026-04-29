"""Extract a single version section from RELEASE_NOTES.md and print to stdout.

Usage: python tools/extract_release_notes.py 1.0.2 RELEASE_NOTES.md
"""
import re
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} VERSION RELEASE_NOTES_PATH", file=sys.stderr)
        return 2
    version, path = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    pattern = rf"^## {re.escape(version)}\b.*?(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.DOTALL | re.MULTILINE)
    if match is None:
        print(f"Version {version} not found in {path}", file=sys.stderr)
        return 1
    sys.stdout.write(match.group(0).strip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
