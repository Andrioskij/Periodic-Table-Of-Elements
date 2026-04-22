"""Dependency injection container for the application."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.settings_service import SettingsService
    from src.ui.managers.compound_builder_manager import CompoundBuilderManager
    from src.ui.managers.search_manager import SearchManager
    from src.ui.managers.trend_manager import TrendManager


@dataclass
class AppContext:
    """Dependency injection container for the entire application.

    Centralizes access to data, services, and managers, allowing
    UI components to receive a single context object instead of
    multiple scattered dependencies.
    """

    # Data
    elements: list
    nomenclature_data: dict

    # Services
    settings_service: SettingsService

    # Managers
    search_manager: SearchManager
    trend_manager: TrendManager
    compound_builder_manager: CompoundBuilderManager

    @classmethod
    def create(
        cls,
        elements: list,
        nomenclature_data: dict,
        settings_service: SettingsService,
    ) -> AppContext:
        """Factory method to create AppContext with all managers initialized.

        Args:
            elements: List of element records
            nomenclature_data: Nomenclature reference data
            settings_service: Settings persistence service

        Returns:
            Fully initialized AppContext
        """
        from src.ui.managers.compound_builder_manager import CompoundBuilderManager
        from src.ui.managers.search_manager import SearchManager
        from src.ui.managers.trend_manager import TrendManager

        search_mgr = SearchManager(elements)
        trend_mgr = TrendManager(elements)
        builder_mgr = CompoundBuilderManager(elements)

        return cls(
            elements=elements,
            nomenclature_data=nomenclature_data,
            settings_service=settings_service,
            search_manager=search_mgr,
            trend_manager=trend_mgr,
            compound_builder_manager=builder_mgr,
        )
