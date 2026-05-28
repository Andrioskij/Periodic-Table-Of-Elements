"""Localized compound-nomenclature formatting, extracted from MainWindow.

Owns the thin wrappers around the module-level helpers in
``src.domain.compound_builder``, ``src.domain.nomenclature``,
``src.services.localization_service``, and ``src.ui.compound_text``.
Each wrapper takes its language code and nomenclature data from the
controller's bound state instead of from `MainWindow` attributes, so
the formatting logic is testable in isolation with pure-Python fakes.

Does NOT own the orchestration that *uses* these helpers (the
``refresh_compound_panel`` / ``compose_compound_result_text`` fan-out
that touches the compound builder panel + the info card + the search
suggestions). Same call-it-from-outside pattern as
``ThemeController.apply_theme`` and
``AccessibilityController.eventFilter``: the controller exposes a
small, side-effect-free surface; MainWindow keeps the orchestration
that has to reach into many sibling widgets.

The ``MainWindow`` thin methods that used to do this work
(``get_localized_element_name``, ``format_stock_compound_name``, etc.)
become 1-line delegations to this controller; their call sites
across MainWindow don't change.
"""

from src.domain.compound_builder import build_binary_formula, format_formula_part
from src.domain.nomenclature import (
    build_stock_name,
    build_traditional_name,
    int_to_roman,
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
from src.ui.compound_text import (
    compose_compound_result_text as compose_compound_panel_text,
)
from src.ui.compound_text import (
    format_common_compounds_section as format_compound_preview_section,
)
from src.ui.compound_text import (
    get_common_compounds_for_pair,
)
from src.ui.compound_text import (
    get_compound_pair_key as build_compound_pair_key,
)
from src.ui.compound_text import (
    get_localized_common_compound_name as get_localized_common_name,
)


class NomenclatureController:
    """Wraps compound-nomenclature + formula-formatting helpers, bound
    to the current UI language and the nomenclature dataset."""

    def __init__(self, nomenclature_data, language_controller):
        self.nomenclature_data = nomenclature_data
        self.language_controller = language_controller

    # ----- Convenience accessors -----

    @property
    def current_language(self):
        return self.language_controller.current_language

    def tr(self, key, **kwargs):
        return translate_text(self.current_language, key, **kwargs)

    # ----- Localized name lookups -----

    def get_localized_element_name(self, element):
        """Return the element's localized name for the current UI language."""
        return get_element_name_for_language(
            element, self.nomenclature_data, self.current_language,
        )

    def get_localized_anion_name(self, element):
        """Return the element's localized anion name for the current UI language."""
        return get_anion_name_for_language(
            element, self.nomenclature_data, self.current_language,
        )

    def get_support_entry(self, symbol):
        """Look up the nomenclature support entry for a given element symbol."""
        return get_nomenclature_support_entry(self.nomenclature_data, symbol)

    def get_localized_support_text(self, entry, field_prefix):
        """Return a localized nomenclature support text field from an entry."""
        return get_support_text_for_language(
            entry, field_prefix, self.current_language,
        )

    def get_language_naming_rules(self, language_code=None):
        """Return the naming-rule dict for the given (or current) language."""
        return get_naming_rules(
            self.nomenclature_data, language_code or self.current_language,
        )

    # ----- Formatters (low-level building blocks) -----

    def format_formula_part(self, symbol, count):
        """Format a single part of a chemical formula (symbol + optional subscript)."""
        return format_formula_part(symbol, count)

    def format_stock_compound_name(self, anion_name, cation_name, roman=None):
        """Build a localized IUPAC (Stock) name from anion + cation + optional roman."""
        return localize_stock_compound_name(
            self.nomenclature_data,
            self.current_language,
            anion_name,
            cation_name,
            roman,
        )

    def format_traditional_compound_name(self, anion_name, epithet):
        """Build a localized traditional compound name from anion + suffix epithet."""
        return localize_traditional_compound_name(
            self.nomenclature_data,
            self.current_language,
            anion_name,
            epithet,
        )

    def int_to_roman(self, number):
        """Convert an integer to its Roman numeral representation."""
        return int_to_roman(number)

    # ----- Compound builders -----

    def build_binary_formula(
        self, cation_symbol, cation_charge, anion_symbol, anion_charge,
    ):
        """Build the balanced binary formula string from cation + anion + charges."""
        return build_binary_formula(
            cation_symbol, cation_charge, anion_symbol, anion_charge,
            formatter=self.format_formula_part,
        )

    def build_stock_name(self, cation, cation_charge, anion):
        """Build the IUPAC (Stock) name for a binary compound."""
        return build_stock_name(
            anion_name=self.get_localized_anion_name(anion),
            cation_name=self.get_localized_element_name(cation),
            cation_charge=cation_charge,
            oxidation_states=cation.get("oxidation_states"),
            traditional_na=self.tr("traditional_na"),
            format_stock_compound_name=self.format_stock_compound_name,
        )

    def build_traditional_name(self, cation, cation_charge, anion):
        """Build the traditional name for a binary compound (-ous/-ic suffixes)."""
        entry = self.get_support_entry(cation.get("symbol"))
        return build_traditional_name(
            anion_name=self.get_localized_anion_name(anion),
            cation_charge=cation_charge,
            oxidation_states=cation.get("oxidation_states"),
            low_name=self.get_localized_support_text(entry, "traditional_low"),
            high_name=self.get_localized_support_text(entry, "traditional_high"),
            traditional_na=self.tr("traditional_na"),
            format_traditional_compound_name=self.format_traditional_compound_name,
        )

    # ----- Common-compounds preview -----

    def get_compound_pair_key(self, symbol_a, symbol_b):
        """Return a canonical key string for a pair of element symbols."""
        return build_compound_pair_key(symbol_a, symbol_b)

    def get_common_compounds_for_pair(self, compound_a, compound_b):
        """Return common compounds for the given A/B element pair, or [] if either is missing."""
        if compound_a is None or compound_b is None:
            return []
        return get_common_compounds_for_pair(
            self.nomenclature_data,
            compound_a.get("symbol"),
            compound_b.get("symbol"),
        )

    def get_localized_common_compound_name(self, compound_entry):
        """Return the localized display name for a common-compound entry."""
        return get_localized_common_name(compound_entry, self.current_language)

    def format_common_compounds_section(self, compound_a, compound_b):
        """Build the HTML section listing common compounds for the given pair."""
        return format_compound_preview_section(
            self.get_common_compounds_for_pair(compound_a, compound_b),
            translate=self.tr,
            get_localized_name=self.get_localized_common_compound_name,
        )

    # ----- Top-level result text -----

    def compose_compound_result_text(
        self, *, compound_a, compound_b, first_oxidation, second_oxidation,
    ):
        """Compose the full compound-builder result text (formula + names + scope)."""
        common_section = self.format_common_compounds_section(compound_a, compound_b)
        return compose_compound_panel_text(
            compound_a=compound_a,
            compound_b=compound_b,
            first_oxidation=first_oxidation,
            second_oxidation=second_oxidation,
            common_section=common_section,
            translate=self.tr,
            build_binary_formula=self.build_binary_formula,
            build_stock_name=self.build_stock_name,
            build_traditional_name=self.build_traditional_name,
            nomenclature_data=self.nomenclature_data,
            language_code=self.current_language,
        )
