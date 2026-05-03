"""Browser frontend for the Periodic Table app.

The repository root is added to sys.path so this module can import the
shared domain and services layers from src/ without copying any code.
The desktop app's UI layer (src.ui) is intentionally not imported — it
depends on PySide6 and is incompatible with the Reflex runtime.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
