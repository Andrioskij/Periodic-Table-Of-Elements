"""Export the canonical design tokens to a JSON file for the web frontend.

The desktop UI consumes ``src.config.design_tokens.TOKENS`` directly. The
web frontend cannot import Python modules at runtime, so it loads the same
data as static JSON. This script walks the immutable ``MappingProxyType``
hierarchy produced by ``design_tokens`` and writes a plain JSON tree, so
that ``app.js`` can fetch it once and project the values onto CSS custom
properties.

Run as a CLI:

    python tools/export_design_tokens.py [--output PATH]

Default output path is ``web/design_tokens.json`` relative to the repo root.
"""

import argparse
import json
import sys
from pathlib import Path
from types import MappingProxyType

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config.design_tokens import TOKENS  # noqa: E402

DEFAULT_OUTPUT = REPO_ROOT / "web" / "design_tokens.json"


def to_jsonable(value):
    """Recursively convert MappingProxyType / tuple structures to JSON-safe types."""
    if isinstance(value, MappingProxyType):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    return value


def export_tokens(output_path: Path) -> Path:
    """Write the JSON-serialized tokens to ``output_path`` and return it."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = to_jsonable(TOKENS)
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Destination JSON file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args(argv)
    written = export_tokens(args.output)
    print(f"Wrote design tokens to {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
