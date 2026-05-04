"""Top-level state for the tools page — only owns the active-tab toggle.

Each tool keeps its own ``rx.State`` subclass in its view module so
its computed vars cache independently. ``ToolsState`` here is the
common parent that holds the selected tab and the validated handler
that drives it.
"""

from __future__ import annotations

import reflex as rx

VALID_TOOLS: frozenset[str] = frozenset(
    {"molar", "stoich", "builder", "solubility"}
)


class ToolsState(rx.State):
    """Active-tab state for the four-tool tab strip on ``/tools``."""

    active_tool: str = "molar"

    @rx.event
    def set_active_tool(self, tool: str) -> None:
        if tool in VALID_TOOLS:
            self.active_tool = tool
