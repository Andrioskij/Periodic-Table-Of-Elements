"""Immutable state containers for the main window's reactive data flow."""

from dataclasses import dataclass, field
from typing import Any


ElementRecord = dict[str, Any]


@dataclass
class SelectionState:
    """Track which element is currently selected and which buttons match a search."""
    element: ElementRecord | None = None
    selected_button: Any = None
    search_matches: set[int] = field(default_factory=set)


@dataclass
class TrendState:
    """Track the active trend-overlay visualization mode."""
    mode: str = "normal"


@dataclass
class CompoundBuilderState:
    """Hold the two elements and their chosen oxidation states for the compound builder."""
    first_element: ElementRecord | None = None
    second_element: ElementRecord | None = None
    first_oxidation: int | None = None
    second_oxidation: int | None = None


@dataclass
class LanguageState:
    """Track the active UI language code."""
    code: str = "en"


@dataclass
class RightPanelState:
    """Track which right-side panel tab is currently visible."""
    mode: str = "info"


__all__ = [
    "CompoundBuilderState",
    "ElementRecord",
    "LanguageState",
    "RightPanelState",
    "SelectionState",
    "TrendState",
]
