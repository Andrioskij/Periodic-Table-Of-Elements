"""Immutable state containers for the main window's presentation layer.

These classes maintain UI/presentation state only. Domain state (search matches,
active trend mode, compound builder selections) is managed by the respective managers
and accessed via properties in MainWindow.
"""

from dataclasses import dataclass
from typing import Any


ElementRecord = dict[str, Any]


@dataclass
class SelectionState:
    """Track UI presentation state for element selection (for display purposes only).

    Domain state (search_matches) is maintained by SearchManager, not here.
    Domain state (compound builder state) is maintained by CompoundBuilderManager.
    This state tracks UI-specific info like which button widget is selected,
    and the element records for presentation (e.g., showing names in search fields).
    """
    element: ElementRecord | None = None
    selected_button: Any = None
    compound_a: ElementRecord | None = None
    compound_b: ElementRecord | None = None


@dataclass
class LanguageState:
    """Track the active UI language code."""
    code: str = "en"


@dataclass
class RightPanelState:
    """Track which right-side panel tab is currently visible."""
    mode: str = "info"


__all__ = [
    "ElementRecord",
    "LanguageState",
    "RightPanelState",
    "SelectionState",
]
