"""Manager for element search operations."""

from dataclasses import dataclass, field
from typing import Set

from src.ui.search_helpers import get_ranked_matches


@dataclass
class SearchManager:
    """Manages element search state and operations.

    Maintains the current search query and matching element IDs,
    and provides methods to search, clear, and query the matches.
    """

    elements: list

    _current_query: str = ""
    _matches: Set[int] = field(default_factory=set)

    def search(self, query: str) -> Set[int]:
        """Search elements by name, symbol, or atomic number.

        Args:
            query: Search string (name, symbol, or atomic number)

        Returns:
            Set of atomic numbers of matching elements
        """
        self._current_query = query.strip()
        if not self._current_query:
            self._matches.clear()
            return self._matches

        # Get ranked matches using the search helper
        matches = get_ranked_matches(
            self.elements,
            self._current_query,
            limit=len(self.elements)  # Return all matches, not just top 6
        )

        # Extract atomic numbers from matched elements
        self._matches = {element.get("atomic_number") for element in matches}
        return self._matches

    def clear_search(self) -> None:
        """Clear the current search query and matches."""
        self._current_query = ""
        self._matches.clear()

    @property
    def matches(self) -> Set[int]:
        """Return set of atomic numbers of currently matching elements."""
        return self._matches

    @property
    def current_query(self) -> str:
        """Return the current search query string."""
        return self._current_query
