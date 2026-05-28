"""Compound-builder orchestration, extracted from MainWindow.

Owns the "drive the compound builder UI" surface: state sync between
the oxidation combos and the domain manager, panel refreshes (status
text, selector summaries, action-control accessibility, result text),
the per-slot search slot handlers, the reset/build callbacks, and the
final result-text composition.

Sits one layer above ``NomenclatureController``: that controller owns
the pure formatters (formula + name builders, common-compounds preview
HTML); this controller owns the orchestration that pulls those
formatters together and reaches into the compound builder widget +
search inputs + oxidation combos to write the result back.

The MainWindow methods that the layout builder wires up
(``_on_search_element_a``, ``update_builder_status``, ``build_compound``,
``reset_builder``) stay on MainWindow as 1-line delegations, so the
widget-builder callbacks don't need to be re-wired.
"""

from src.ui.compound_text import (
    compose_compound_result_text as compose_compound_panel_text,
)


class CompoundController:
    """Drives the compound-builder UI: state sync, panel refresh,
    selection callbacks, result composition. Bound to the domain
    manager, presentation selection state, the nomenclature controller,
    and the widget refs that make up the builder area."""

    def __init__(
        self,
        *,
        builder_manager,
        selection_state,
        nomenclature_controller,
        compound_builder_panel,
        search_a_input,
        search_b_input,
        a_oxidation_combo,
        b_oxidation_combo,
        translate,
        format_oxidation_state,
        populate_oxidation_combo,
        get_ranked_matches,
    ):
        self.builder_manager = builder_manager
        self.selection_state = selection_state
        self.nomenclature_controller = nomenclature_controller
        self.compound_builder_panel = compound_builder_panel
        self.search_a_input = search_a_input
        self.search_b_input = search_b_input
        self.a_oxidation_combo = a_oxidation_combo
        self.b_oxidation_combo = b_oxidation_combo
        self.translate = translate
        self.format_oxidation_state = format_oxidation_state
        self.populate_oxidation_combo = populate_oxidation_combo
        self.get_ranked_matches = get_ranked_matches

    # ----- Convenience accessors -----

    @property
    def compound_a(self):
        return self.selection_state.compound_a

    @compound_a.setter
    def compound_a(self, value):
        self.selection_state.compound_a = value

    @property
    def compound_b(self):
        return self.selection_state.compound_b

    @compound_b.setter
    def compound_b(self, value):
        self.selection_state.compound_b = value

    def get_current_oxidation(self, combo):
        """Return the currently selected oxidation state from a combo box, or None."""
        value = combo.currentData()
        return value if isinstance(value, int) else None

    # ----- Domain<->controls sync -----

    def sync_state_from_controls(self):
        """Push the current oxidation-combo values into the builder manager."""
        oxidation_a = self.get_current_oxidation(self.a_oxidation_combo)
        oxidation_b = self.get_current_oxidation(self.b_oxidation_combo)

        if self.compound_a is not None and oxidation_a is not None:
            self.builder_manager.set_element_a(
                self.compound_a["atomic_number"], oxidation_a,
            )

        if self.compound_b is not None and oxidation_b is not None:
            self.builder_manager.set_element_b(
                self.compound_b["atomic_number"], oxidation_b,
            )

    # ----- Panel refreshes -----

    def refresh_builder_panel(self, *, update_selectors=True):
        """Refresh status text, optional selector labels, and action accessibility."""
        self.sync_state_from_controls()
        self.refresh_builder_status()
        if update_selectors:
            self.refresh_builder_selector_texts()
        self.refresh_builder_action_accessibility()

    def refresh_builder_status(self):
        """Update the status label showing the selected elements + oxidation states."""
        tr = self.translate
        na = tr("traditional_na")

        if self.compound_a is None:
            text_a = tr("not_selected")
        else:
            oxidation_a = self.builder_manager.state.element_a_oxidation
            text_a = (
                f"{self.compound_a['symbol']} "
                f"{self.format_oxidation_state(oxidation_a) if oxidation_a is not None else na}"
            )

        if self.compound_b is None:
            text_b = tr("not_selected")
        else:
            oxidation_b = self.builder_manager.state.element_b_oxidation
            text_b = (
                f"{self.compound_b['symbol']} "
                f"{self.format_oxidation_state(oxidation_b) if oxidation_b is not None else na}"
            )

        self.compound_builder_panel.set_status_text(
            tr("builder_status", a=text_a, b=text_b),
        )

    def refresh_builder_selector_texts(self):
        """Update the A/B selector summary labels with localized names or placeholders."""
        tr = self.translate
        get_name = self.nomenclature_controller.get_localized_element_name

        if self.compound_a is None:
            first_text = tr("first_element")
        else:
            first_text = tr(
                "first_selected",
                name=get_name(self.compound_a),
                symbol=self.compound_a.get("symbol"),
            )

        if self.compound_b is None:
            second_text = tr("second_element")
        else:
            second_text = tr(
                "second_selected",
                name=get_name(self.compound_b),
                symbol=self.compound_b.get("symbol"),
            )

        self.compound_builder_panel.set_selector_texts(first_text, second_text)
        self.compound_builder_panel.selector_a_summary_label.setToolTip(first_text)
        self.compound_builder_panel.selector_b_summary_label.setToolTip(second_text)

    def refresh_builder_action_accessibility(self):
        """Mirror the selector labels onto the search inputs as tooltips + a11y text."""
        for search_input, slot_text in (
            (self.search_a_input,
             self.compound_builder_panel.selector_a_summary_label.text()),
            (self.search_b_input,
             self.compound_builder_panel.selector_b_summary_label.text()),
        ):
            search_input.setToolTip(slot_text)
            search_input.setAccessibleDescription(slot_text)

    def refresh_compound_panel(self, *, rebuild=False):
        """Refresh the nomenclature result text shown in the builder panel."""
        self.sync_state_from_controls()
        has_compound_pair = (
            self.compound_a is not None and self.compound_b is not None
        )

        if rebuild:
            text = self.compose_compound_result_text() or ""
        elif has_compound_pair:
            preview = self.format_common_compounds_section()
            text = self.translate("pair_ready_prompt")
            if preview:
                text += "\n\n" + preview
        else:
            text = ""

        self.compound_builder_panel.set_result_text(text)

    # ----- Common-compounds preview (current pair) -----

    def get_common_compounds_for_current_pair(self):
        """Return common compounds for the currently selected A/B pair."""
        return self.nomenclature_controller.get_common_compounds_for_pair(
            self.compound_a, self.compound_b,
        )

    def format_common_compounds_section(self):
        """Build the HTML preview section for the currently selected pair."""
        return self.nomenclature_controller.format_common_compounds_section(
            self.compound_a, self.compound_b,
        )

    # ----- Result-text composition -----

    def compose_compound_result_text(self):
        """Compose the full result text (formula + IUPAC + traditional names + preview)."""
        nc = self.nomenclature_controller
        manager_state = self.builder_manager.state
        return compose_compound_panel_text(
            compound_a=self.compound_a,
            compound_b=self.compound_b,
            first_oxidation=manager_state.element_a_oxidation,
            second_oxidation=manager_state.element_b_oxidation,
            common_section=self.format_common_compounds_section(),
            translate=self.translate,
            build_binary_formula=nc.build_binary_formula,
            build_stock_name=nc.build_stock_name,
            build_traditional_name=nc.build_traditional_name,
            nomenclature_data=nc.nomenclature_data,
            language_code=nc.current_language,
        )

    # ----- Signal handlers (wired by the layout builder) -----

    def on_search_element_a(self):
        """Search slot A: assign the top-ranked match and refresh the builder."""
        query = self.search_a_input.text().strip()
        if not query:
            return
        matches = self.get_ranked_matches(query, limit=1)
        if not matches:
            self.search_a_input.setText("")
            return

        element = matches[0]
        self.compound_a = element
        self.search_a_input.setText(
            f"{self.nomenclature_controller.get_localized_element_name(element)} "
            f"({element['symbol']})"
        )
        self.populate_oxidation_combo(self.a_oxidation_combo, element)

        self.builder_manager.set_element_a(element["atomic_number"], 1)

        self.refresh_builder_panel()
        self.refresh_compound_panel()

    def on_search_element_b(self):
        """Search slot B: assign the top-ranked match and refresh the builder."""
        query = self.search_b_input.text().strip()
        if not query:
            return
        matches = self.get_ranked_matches(query, limit=1)
        if not matches:
            self.search_b_input.setText("")
            return

        element = matches[0]
        self.compound_b = element
        self.search_b_input.setText(
            f"{self.nomenclature_controller.get_localized_element_name(element)} "
            f"({element['symbol']})"
        )
        self.populate_oxidation_combo(self.b_oxidation_combo, element)

        self.builder_manager.set_element_b(element["atomic_number"], -1)

        self.refresh_builder_panel()
        self.refresh_compound_panel()

    def reset(self):
        """Clear slots, oxidation selections, and reset the builder UI."""
        self.builder_manager.reset()

        self.compound_a = None
        self.compound_b = None
        self.search_a_input.setText("")
        self.search_b_input.setText("")
        self.populate_oxidation_combo(self.a_oxidation_combo, None)
        self.populate_oxidation_combo(self.b_oxidation_combo, None)
        self.refresh_builder_status()
        self.refresh_compound_panel()

    def build_compound(self):
        """Rebuild the formula result in the nomenclature area."""
        self.refresh_compound_panel(rebuild=True)
