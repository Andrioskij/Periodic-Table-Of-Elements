"""Canonical public entry point and compatibility facade for the application."""

from PySide6.QtWidgets import QApplication

from src.app_metadata import (
    APP_DISPLAY_NAME,
    APP_EXECUTABLE_NAME,
    APP_ID,
    APP_RELEASE_NAME,
    APP_VENDOR,
    APP_VERSION,
)
from src.bootstrap import run as run_application
from src.config.static_data import (
    NUMERIC_TREND_PROPERTIES,
    ORBITAL_BOX_COUNTS,
    VALID_SUBSHELLS,
)
from src.domain.compound_builder import (
    build_binary_formula,
    format_formula_part,
    parse_oxidation_states,
)
from src.domain.electron_configuration import (
    configuration_to_map,
    expand_configuration,
    fill_boxes,
)
from src.domain.nomenclature import (
    build_stock_name,
    build_traditional_name,
    int_to_roman,
)
from src.domain.trends import (
    compute_numeric_ranges,
    get_macro_class,
    get_macro_class_color,
)
from src.services.data_loader import (
    DATA_DIR,
    ELEMENTS_DATA_PATH,
    NOMENCLATURE_DATA_PATH,
    PROJECT_ROOT,
    load_elements,
    load_nomenclature_data,
)
from src.services.localization_service import (
    LANGUAGE_OPTIONS,
    UI_TEXTS,
)
from src.services.localization_service import (
    format_stock_compound_name as localize_stock_compound_name,
)
from src.services.localization_service import (
    format_traditional_compound_name as localize_traditional_compound_name,
)
from src.services.localization_service import (
    get_language_naming_rules as get_naming_rules,
)
from src.services.localization_service import (
    get_localized_anion_name as get_anion_name_for_language,
)
from src.services.localization_service import (
    get_localized_element_name as get_element_name_for_language,
)
from src.services.localization_service import (
    get_localized_support_text as get_support_text_for_language,
)
from src.services.localization_service import (
    get_support_entry as get_nomenclature_support_entry,
)
from src.services.localization_service import (
    tr as translate_text,
)
from src.ui.main_window import MainWindow, format_value
from src.ui.widgets.flow_layout import FlowLayout
from src.ui.widgets.trends_overlay import TrendsOverlay


def main():
    return run_application()


__all__ = [
    "APP_DISPLAY_NAME",
    "APP_EXECUTABLE_NAME",
    "APP_ID",
    "APP_RELEASE_NAME",
    "APP_VENDOR",
    "APP_VERSION",
    "DATA_DIR",
    "ELEMENTS_DATA_PATH",
    "FlowLayout",
    "LANGUAGE_OPTIONS",
    "MainWindow",
    "NOMENCLATURE_DATA_PATH",
    "NUMERIC_TREND_PROPERTIES",
    "ORBITAL_BOX_COUNTS",
    "PROJECT_ROOT",
    "QApplication",
    "TrendsOverlay",
    "UI_TEXTS",
    "VALID_SUBSHELLS",
    "build_binary_formula",
    "build_stock_name",
    "build_traditional_name",
    "compute_numeric_ranges",
    "configuration_to_map",
    "expand_configuration",
    "fill_boxes",
    "format_formula_part",
    "format_value",
    "get_anion_name_for_language",
    "get_element_name_for_language",
    "get_macro_class",
    "get_macro_class_color",
    "get_naming_rules",
    "get_nomenclature_support_entry",
    "get_support_text_for_language",
    "int_to_roman",
    "load_elements",
    "load_nomenclature_data",
    "localize_stock_compound_name",
    "localize_traditional_compound_name",
    "main",
    "parse_oxidation_states",
    "translate_text",
]


if __name__ == "__main__":
    raise SystemExit(main())
