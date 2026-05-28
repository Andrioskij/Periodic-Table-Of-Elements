from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QWidget,
)

from src.app_metadata import build_window_title
from src.config.design_tokens import TOKENS
from src.config.static_data import NUMERIC_TREND_PROPERTIES
from src.domain.compound_builder import (
    parse_oxidation_states,
)
from src.domain.trends import (
    get_macro_class,
    get_macro_class_color,
)
from src.services.localization_service import (
    LANGUAGE_OPTIONS,
)
from src.services.localization_service import (
    get_localized_category_text as get_category_text_for_language,
)
from src.services.localization_service import (
    get_localized_macro_class_text as get_macro_class_text_for_language,
)
from src.services.localization_service import (
    get_localized_standard_state_text as get_standard_state_text_for_language,
)
from src.services.localization_service import (
    tr as translate_text,
)
from src.ui.about_dialog import AboutDialog
from src.ui.compound_text import (
    compose_compound_result_text as compose_compound_panel_text,
)
from src.ui.constants import CalculatorIcons
from src.ui.context import AppContext
from src.ui.controllers.accessibility_controller import AccessibilityController
from src.ui.controllers.language_controller import LanguageController
from src.ui.controllers.nomenclature_controller import NomenclatureController
from src.ui.controllers.responsive_layout_controller import ResponsiveLayoutController
from src.ui.controllers.theme_controller import ThemeController
from src.ui.formatters import format_info_value, format_value
from src.ui.main_window_builder import (
    build_builder_widget,
    build_content_layout,
    build_periodic_table_widget,
    build_right_panel_area,
    build_search_widget,
    build_shell,
    build_title_row,
    build_top_controls_layout,
    build_trend_controls,
)
from src.ui.main_window_language import (
    build_main_window_texts,
)
from src.ui.main_window_panels import (
    build_diagram_panel_state,
    build_info_panel_prompt,
    build_right_panel_mode_state,
    build_tool_area_mode_state,
)
from src.ui.search_helpers import (
    compute_match_score as compute_search_match_score,
)
from src.ui.search_helpers import (
    get_ranked_matches as get_ranked_search_matches,
)
from src.ui.state import (
    LanguageState,
    RightPanelState,
    SelectionState,
)
from src.ui.styles import (
    get_category_color as get_ui_category_color,
)
from src.ui.styles import (
    get_current_button_colors as get_ui_button_colors,
)
from src.ui.styles import (
    get_stylesheet,
)
from src.ui.styles import (
    get_text_color as get_ui_text_color,
)
from src.ui.styles import (
    interpolate_color as interpolate_ui_color,
)

TREND_BUTTON_SPECS = (
    ("normal", "trend_button_normal"),
    ("macroclass", "trend_button_macroclass"),
    ("radius", "trend_button_radius"),
    ("ionization", "trend_button_ionization"),
    ("electronegativity", "trend_button_electronegativity"),
    ("metallic", "trend_button_metallic"),
    ("metalloid", "trend_button_metalloid"),
    ("nonmetallic", "trend_button_nonmetallic"),
)
NUMERIC_TREND_LABEL_KEYS = {
    "radius": "atomic_radius",
    "ionization": "ionization_energy",
    "electronegativity": "electronegativity",
}


class MainWindow(QWidget):
    """Main application window for the interactive periodic table.

    Orchestrates the periodic table grid, element search, trend overlays,
    right-side info/diagram/compound panels, compound builder, and
    responsive layout.  Persists user preferences (language, window
    geometry, trend mode, panel mode) via a SettingsService.
    """

    def __init__(self, context: AppContext):
        """Initialize the main window with AppContext.

        Args:
            context: AppContext containing elements, nomenclature_data,
                settings_service, localization_service, and all managers.
        """
        super().__init__()

        self.context = context
        self.elements = sorted(context.elements, key=lambda element: element["atomic_number"])
        assert len({e["atomic_number"] for e in self.elements}) == len(self.elements), (
            "Duplicate atomic_number values detected in element data"
        )
        self.element_index = {element["atomic_number"]: element for element in self.elements}
        self.nomenclature_data = context.nomenclature_data

        self.selection_state = SelectionState()
        self.right_panel_state = RightPanelState()
        self.language_state = LanguageState()

        self.settings_service = context.settings_service
        self.theme_controller = ThemeController(
            current_theme=self.settings_service.get_theme(),
            settings_service=self.settings_service,
        )
        self.about_dialog = None

        self.cell_size = 50
        self.header_height = 24
        self.side_width = 48
        self.grid_h_spacing = TOKENS["spacing"]["grid_gap_desktop"]
        self.grid_v_spacing = TOKENS["spacing"]["grid_gap_desktop"]
        self.element_font_size = TOKENS["font"]["size"]["button_default"]

        self._configure_window()
        # Created before _assemble_layout because the layout builder
        # calls accessibility_controller.refresh_control_accessibility()
        # while wiring the trend controls. The controller holds only a
        # window ref; its methods resolve widget attributes lazily, so
        # an early construction is safe.
        self.accessibility_controller = AccessibilityController(self)
        self._assemble_layout()
        self.accessibility_controller.configure_focus_and_shortcuts()
        self._finalize_layout()

        self.layout_controller = ResponsiveLayoutController(self)
        self.language_controller = LanguageController(
            language_state=self.language_state,
            settings_service=self.settings_service,
            language_selector=self.language_selector,
        )
        # Bind nomenclature helpers to the active language + dataset so
        # the formatters are testable in isolation. MainWindow keeps
        # 1-line passthrough methods for backward compatibility with
        # the existing call sites (~60 across the file).
        self.nomenclature_controller = NomenclatureController(
            nomenclature_data=self.nomenclature_data,
            language_controller=self.language_controller,
        )

        self.populate_oxidation_combo(self.a_oxidation_combo, None)
        self.populate_oxidation_combo(self.b_oxidation_combo, None)

        self.load_preferences()
        self.apply_language()
        self.update_responsive_layout()

    def _assemble_layout(self):
        """Invoke stateless builders and wire the returned widgets into the window."""
        shell = build_shell()
        self.outer_layout = shell["outer_layout"]
        self.main_scroll_area = shell["main_scroll_area"]
        self.content_widget = shell["content_widget"]
        self.main_layout = shell["main_layout"]

        title = build_title_row(
            about_text=self.tr("about_button"),
            theme_button_text=self.theme_controller.button_text(),
            theme_button_tooltip=self.theme_controller.button_tooltip(),
            language_options=LANGUAGE_OPTIONS,
            on_about_clicked=self.open_about_dialog,
            on_theme_toggle=self.toggle_theme,
            on_language_changed=self.change_language,
        )
        self.title_label = title["title_label"]
        self.about_button = title["about_button"]
        self.theme_button = title["theme_button"]
        self.language_selector = title["language_selector"]
        self.main_layout.addLayout(title["title_row"])

        search = build_search_widget(
            placeholder=self.tr("search_placeholder"),
            search_button_text=self.tr("search_button"),
            on_text_changed=self.update_search_suggestions,
            on_search=self.search_element,
            on_suggestion_clicked=self.handle_suggestion_clicked,
        )
        self.search_widget = search["search_widget"]
        self.search_title_label = search["search_title_label"]
        self.search_help_label = search["search_help_label"]
        self.search_input = search["search_input"]
        self.search_button = search["search_button"]
        self.suggestions_list = search["suggestions_list"]
        self.search_status_label = search["search_status_label"]

        builder = build_builder_widget(
            self.elements,
            tr=self.tr,
            on_tool_mode_clicked=self.set_tool_area_mode,
            on_search_a=self._on_search_element_a,
            on_search_b=self._on_search_element_b,
            on_oxidation_changed=self.update_builder_status,
            on_build=self.build_compound,
            on_reset=self.reset_builder,
        )
        self.tool_area_mode = builder["tool_area_mode"]
        self.tool_area_buttons = builder["tool_area_buttons"]
        self.tool_area_buttons_widget = builder["tool_area_buttons_widget"]
        self.tool_area_buttons_layout = builder["tool_area_buttons_layout"]
        self.compound_builder_panel = builder["compound_builder_panel"]
        self.search_a_input = builder["search_a_input"]
        self.search_b_input = builder["search_b_input"]
        self.a_oxidation_label = builder["a_oxidation_label"]
        self.b_oxidation_label = builder["b_oxidation_label"]
        self.a_oxidation_combo = builder["a_oxidation_combo"]
        self.b_oxidation_combo = builder["b_oxidation_combo"]
        self.build_button = builder["build_button"]
        self.builder_reset_button = builder["builder_reset_button"]
        self.builder_status_label = builder["builder_status_label"]
        self.molar_mass_panel = builder["molar_mass_panel"]
        self.stoichiometry_panel = builder["stoichiometry_panel"]
        self.solubility_panel = builder["solubility_panel"]
        self.tool_area_stack = builder["tool_area_stack"]
        self.builder_widget = builder["builder_widget"]

        self.top_controls_layout = build_top_controls_layout(self.search_widget)
        self.main_layout.addLayout(self.top_controls_layout)

        trend = build_trend_controls(
            tr=self.tr,
            trend_specs=TREND_BUTTON_SPECS,
            on_trend_clicked=self.set_trend_mode,
        )
        self.trend_buttons = trend["trend_buttons"]
        self.trend_container = trend["trend_container"]
        self.trend_flow_layout = trend["trend_flow_layout"]
        self.trend_status_label = trend["trend_status_label"]
        self.main_layout.addWidget(self.trend_container)
        self.main_layout.addWidget(self.trend_status_label)
        self.accessibility_controller.refresh_control_accessibility()

        self.periodic_table_widget = build_periodic_table_widget(
            self.elements,
            self.element_index,
            format_value=format_value,
            get_macro_class=self.get_macro_class,
            get_display_category=self.get_display_category,
            get_display_macro_class=self.get_display_macro_class,
            get_button_colors=self.get_current_button_colors,
            get_accent_color=self._get_current_accent_color,
            name_provider=self.get_localized_element_name,
            on_element_selected=self._handle_table_selection,
        )
        self.element_buttons = self.periodic_table_widget.element_buttons
        self.group_header_labels = self.periodic_table_widget.group_header_labels
        self.period_labels = self.periodic_table_widget.period_labels
        self.series_labels = self.periodic_table_widget.series_labels
        self.corner_label = self.periodic_table_widget.corner_label
        self.transition_label = self.periodic_table_widget.transition_label
        self.selected_element_name_label = self.periodic_table_widget.selected_element_name_label
        self.trends_overlay = self.periodic_table_widget.trends_overlay
        self.table_stack_container = self.periodic_table_widget.table_stack_container
        self.grid_layout = self.periodic_table_widget.grid_layout

        right = build_right_panel_area(
            tr=self.tr,
            numeric_ranges=self.context.trend_manager.numeric_ranges,
            on_right_mode_clicked=self.set_right_panel_mode,
            elements=self.elements,
        )
        self.right_panel_buttons = right["right_panel_buttons"]
        self.right_panel_buttons_widget = right["right_panel_buttons_widget"]
        self.right_panel_buttons_layout = right["right_panel_buttons_layout"]
        self.info_panel = right["info_panel"]
        self.info_page = right["info_page"]
        self.info_label = right["info_label"]
        self.orbital_diagram_panel = right["orbital_diagram_panel"]
        self.diagram_page = right["diagram_page"]
        self.diagram_title_label = right["diagram_title_label"]
        self.diagram_label = right["diagram_label"]
        self.lewis_panel = right["lewis_panel"]
        self.lewis_panel.set_translator(self.tr, format_value)
        self.molar_mass_panel.set_translator(self.tr)
        self.stoichiometry_panel.set_translator(self.tr)
        self.lewis_page = right["lewis_page"]
        self.right_panel_container = right["right_panel_container"]
        self.right_panel_stack = right["right_panel_stack"]
        self.right_column_widget = right["right_column_widget"]

        self.content_layout = build_content_layout(
            self.periodic_table_widget, self.right_column_widget,
        )
        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addWidget(self.builder_widget)
        self.accessibility_controller.refresh_control_accessibility()

    @property
    def selected_button(self):
        """Return the currently selected element button widget."""
        return self.selection_state.selected_button

    @selected_button.setter
    def selected_button(self, value):
        """Set the currently selected element button widget."""
        self.selection_state.selected_button = value

    @property
    def current_selected_element(self):
        """Return the element dict for the currently selected element."""
        return self.selection_state.element

    @current_selected_element.setter
    def current_selected_element(self, value):
        """Set the currently selected element dict."""
        self.selection_state.element = value

    @property
    def current_search_matches(self):
        """Return the set of atomic numbers matching the current search."""
        return self.context.search_manager.matches

    @property
    def active_trend_mode(self):
        """Return the active trend-coloring mode (e.g. 'normal', 'radius')."""
        return self.context.trend_manager.current_mode

    @active_trend_mode.setter
    def active_trend_mode(self, value):
        """Set the active trend-coloring mode (delegates to TrendManager)."""
        self.context.trend_manager.set_trend_mode(value)

    @property
    def right_panel_mode(self):
        """Return the active right-panel mode ('info', 'diagram', or 'compound')."""
        return self.right_panel_state.mode

    @right_panel_mode.setter
    def right_panel_mode(self, value):
        """Set the active right-panel mode."""
        self.right_panel_state.mode = value

    @property
    def compound_a(self):
        """Return the first element chosen for the compound builder (for presentation)."""
        return self.selection_state.compound_a

    @compound_a.setter
    def compound_a(self, value):
        """Set the first element for the compound builder (for presentation)."""
        self.selection_state.compound_a = value

    @property
    def compound_b(self):
        """Return the second element chosen for the compound builder (for presentation)."""
        return self.selection_state.compound_b

    @compound_b.setter
    def compound_b(self, value):
        """Set the second element for the compound builder (for presentation)."""
        self.selection_state.compound_b = value

    @property
    def current_language(self):
        """Return the active UI language code (e.g. 'en', 'it')."""
        return self.language_state.code

    @current_language.setter
    def current_language(self, value):
        """Set the active UI language code, ignoring falsy values."""
        if value:
            self.language_state.code = value

    def _configure_window(self):
        """Set window title, icon, initial size, minimum size, and stylesheet."""
        self.setWindowTitle(build_window_title(self.tr("title")))
        app = QApplication.instance()
        if app is not None and not app.windowIcon().isNull():
            self.setWindowIcon(app.windowIcon())
        self.resize(1500, 960)
        self.setMinimumSize(560, 480)
        self.setStyleSheet(get_stylesheet(self.current_theme))

    def _finalize_layout(self):
        """Finalize the widget tree by attaching the content widget to the scroll area."""
        self.content_widget.setLayout(self.main_layout)
        self.main_scroll_area.setWidget(self.content_widget)
        self.outer_layout.addWidget(self.main_scroll_area)
        self.setLayout(self.outer_layout)

    def eventFilter(self, obj, event):
        """Activate a trend or panel mode when its button receives focus."""
        if event.type() == QEvent.FocusIn:
            if obj in self.trend_buttons.values():
                for mode, button in self.trend_buttons.items():
                    if obj is button:
                        self.set_trend_mode(mode)
                        break
            if obj in self.right_panel_buttons.values():
                for mode, button in self.right_panel_buttons.items():
                    if obj is button:
                        self.set_right_panel_mode(mode)
                        break

        return super().eventFilter(obj, event)

    def tr(self, key, **kwargs):
        """Translate a localization key using the current UI language."""
        return translate_text(self.current_language, key, **kwargs)

    def load_preferences(self):
        """Load persisted user preferences (language, trend mode, panel mode, window geometry)."""
        self.language_controller.load_from_settings()
        self.active_trend_mode = self.settings_service.get_trend_mode()
        self.right_panel_mode = self.settings_service.get_right_panel_mode()
        self.restore_window_preferences()

    def restore_window_preferences(self):
        """Restore window size, position, and maximized state from persisted settings."""
        geometry = self.settings_service.get_window_geometry()
        if geometry:
            self.resize(geometry["width"], geometry["height"])
            self.move(geometry["x"], geometry["y"])

        if self.settings_service.get_window_state() == "maximized":
            self.setWindowState(self.windowState() | Qt.WindowMaximized)

    def persist_window_preferences(self):
        """Save current window geometry and maximized state to the settings service."""
        self.settings_service.set_window_geometry(
            {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height(),
            }
        )
        self.settings_service.set_window_state("maximized" if self.isMaximized() else "normal")

    def sync_builder_state_from_controls(self):
        """Read the currently selected oxidation states from the combo boxes and sync with manager."""
        oxidation_a = self.get_current_oxidation(self.a_oxidation_combo)
        oxidation_b = self.get_current_oxidation(self.b_oxidation_combo)

        # Delegate to manager if both elements are selected
        if self.compound_a is not None and oxidation_a is not None:
            self.context.compound_builder_manager.set_element_a(
                self.compound_a["atomic_number"],
                oxidation_a
            )

        if self.compound_b is not None and oxidation_b is not None:
            self.context.compound_builder_manager.set_element_b(
                self.compound_b["atomic_number"],
                oxidation_b
            )

    def refresh_selection_header(self):
        """Sync the selection state from the table widget and update the builder header."""
        self.selection_state.selected_button = self.periodic_table_widget.selected_button
        self.periodic_table_widget.refresh_selected_element_name()

    def change_language(self, index):
        """Handle language selector change: persist the choice and re-apply all UI text."""
        code = self.language_selector.currentData()
        if self.language_controller.change_to(code):
            self.apply_language()

    @property
    def current_theme(self) -> str:
        """Active theme name (`'dark'` or `'light'`), owned by `self.theme_controller`."""
        return self.theme_controller.current_theme

    def toggle_theme(self):
        """Swap the active theme, persist the choice, and re-apply styles live."""
        self.theme_controller.toggle_and_persist()
        self.apply_theme()

    def apply_theme(self):
        """Reload the stylesheet and refresh every widget that paints with theme colors."""
        self.setStyleSheet(get_stylesheet(self.current_theme))
        if hasattr(self, "theme_button"):
            self.theme_button.setText(self.theme_controller.button_text())
            self.theme_button.setToolTip(self.theme_controller.button_tooltip())

        self.orbital_diagram_panel.apply_theme(self.current_theme)
        self.lewis_panel.apply_theme(self.current_theme)
        self.solubility_panel.apply_theme(self.current_theme)

        self.periodic_table_widget.refresh_button_styles()
        self.refresh_info_panel()
        self.refresh_diagram_panel()
        self.refresh_lewis_panel()

    def open_about_dialog(self):
        """Open (or reuse) the About dialog, applying the current language."""
        if self.about_dialog is None:
            self.about_dialog = AboutDialog(translate=self.tr, parent=self)

        self.about_dialog.apply_language()
        self.about_dialog.show()
        self.about_dialog.activateWindow()

    def apply_language(self):
        """Re-apply all localized texts, refresh panels, and update the responsive layout."""
        self.language_controller.sync_selector()
        texts = build_main_window_texts(self.tr, TREND_BUTTON_SPECS)
        self._apply_main_window_language_texts(texts)

        self.refresh_status_labels(clear_search=True)
        self.refresh_right_panel_mode()

        if self.about_dialog is not None:
            self.about_dialog.apply_language()

        self.accessibility_controller.refresh_control_accessibility()
        self.periodic_table_widget.refresh_button_styles()
        self.refresh_info_panel()
        self.refresh_diagram_panel()
        self.refresh_lewis_panel()

        if self.compound_a is not None and self.compound_b is not None:
            self.build_compound()
        else:
            self.refresh_compound_panel()

        self.update_responsive_layout()

    def _apply_main_window_language_texts(self, texts):
        """Apply a dict of translated strings to every label, button, and panel in the window."""
        self.setWindowTitle(build_window_title(texts["title"]))
        self.title_label.setText(texts["title"])
        self.about_button.setText(texts["about_button"])
        self.search_title_label.setText(texts["search_title"])
        self.search_help_label.setText(texts["search_helper"])
        self.search_input.setPlaceholderText(texts["search_placeholder"])
        self.search_button.setText(texts["search_button"])
        help_close = self.tr("close_dialog")
        example_text = self.tr("example_button")
        self.compound_builder_panel.apply_language(
            title=f"{CalculatorIcons.BUILDER}  {self.tr('builder_title')}",
            selector_a_title=texts["builder_slot_a_title"],
            selector_b_title=texts["builder_slot_b_title"],
            search_placeholder_a=texts["builder_search_placeholder_a"],
            search_placeholder_b=texts["builder_search_placeholder_b"],
            oxidation_first=texts["oxidation_first"],
            oxidation_second=texts["oxidation_second"],
            calculate_formula=texts["calculate_formula"],
            reset=texts["reset"],
            help_body=self.tr("builder_help_body"),
            help_close_text=help_close,
            example_text=example_text,
        )
        self.molar_mass_panel.apply_language(
            title=f"{CalculatorIcons.MOLAR}  {self.tr('molar_title')}",
            prompt=self.tr("molar_prompt"),
            button_text=self.tr("molar_calculate"),
            error_prefix=self.tr("molar_error"),
            help_body=self.tr("molar_help_body"),
            help_close_text=help_close,
            example_text=example_text,
        )
        self.stoichiometry_panel.apply_language(
            title=f"{CalculatorIcons.STOICHIOMETRY}  {self.tr('stoichiometry_title')}",
            prompt=self.tr("stoichiometry_prompt"),
            balance_text=self.tr("stoichiometry_balance"),
            calc_masses_text=self.tr("stoichiometry_calc_masses"),
            mass_section_text=self.tr("stoichiometry_mass_section"),
            error_prefix=self.tr("stoichiometry_error"),
            help_body=self.tr("stoichiometry_help_body"),
            help_close_text=help_close,
            example_text=example_text,
        )
        self.lewis_panel.apply_language(
            title=self.tr("lewis_title"),
            prompt=self.tr("lewis_prompt"),
            input_placeholder=self.tr("lewis_input_placeholder"),
            show_button_text=self.tr("lewis_show_button"),
            not_in_library_text=self.tr("lewis_not_in_library"),
        )
        self.solubility_panel.apply_language(
            title=f"{CalculatorIcons.SOLUBILITY}  {self.tr('solubility_title')}",
            prompt=self.tr("solubility_prompt"),
            cation_label=self.tr("solubility_cation_label"),
            anion_label=self.tr("solubility_anion_label"),
            check_text=self.tr("solubility_check"),
            soluble_text=self.tr("solubility_soluble"),
            insoluble_text=self.tr("solubility_insoluble"),
            slightly_text=self.tr("solubility_slightly_soluble"),
            rule_label=self.tr("solubility_rule_label"),
            exceptions_label=self.tr("solubility_exceptions_label"),
            legend_title=self.tr("solubility_legend_title"),
            rule_alkali=self.tr("solubility_rule_alkali"),
            rule_nitrate_acetate=self.tr("solubility_rule_nitrate_acetate"),
            rule_halide=self.tr("solubility_rule_halide"),
            rule_sulfate=self.tr("solubility_rule_sulfate"),
            rule_hydroxide=self.tr("solubility_rule_hydroxide"),
            rule_carbonate_phosphate_sulfide=self.tr("solubility_rule_carbonate_phosphate_sulfide"),
            rule_default=self.tr("solubility_rule_default"),
            help_body=self.tr("solubility_help_body"),
            help_close_text=help_close,
            example_text=example_text,
        )
        self.periodic_table_widget.set_language_texts(
            selected_none_text=texts["selected_none"],
            transition_text=texts["transition_metals"],
            metallic_text=texts["metallic_arrow"],
            nonmetallic_text=texts["nonmetallic_arrow"],
            metalloid_text=texts["metalloid_arrow"],
        )

        for mode, text in texts["trend_buttons"].items():
            self.trend_buttons[mode].setText(text)

        for mode, text in texts["right_panel_buttons"].items():
            self.right_panel_buttons[mode].setText(text)

        for mode, text in texts["tool_area_buttons"].items():
            self.tool_area_buttons[mode].setText(text)

    def refresh_status_labels(self, *, search_text=None, clear_search=False):
        """Refresh search status, builder panel, and trend status labels."""
        if clear_search:
            self.set_search_status_text("")
        elif search_text is not None:
            self.set_search_status_text(search_text)

        self.refresh_builder_panel()
        self.refresh_trend_status()

    def set_search_status_text(self, text):
        """Set and show/hide the search status label based on text content."""
        message = (text or "").strip()
        self.search_status_label.setText(message)
        self.search_status_label.setVisible(bool(message))

    def refresh_trend_status(self):
        """Update the trend status label text to describe the currently active trend mode."""
        mode = self.active_trend_mode
        if mode == "normal":
            self.trend_status_label.setText(self.tr("current_view_normal"))
        elif mode == "macroclass":
            self.trend_status_label.setText(self.tr("current_view_macro"))
        elif mode == "metallic":
            self.trend_status_label.setText(self.tr("current_view_metallic"))
        elif mode == "nonmetallic":
            self.trend_status_label.setText(self.tr("current_view_nonmetallic"))
        elif mode == "metalloid":
            self.trend_status_label.setText(self.tr("current_view_metalloid"))
        else:
            trend_title = self.tr(NUMERIC_TREND_LABEL_KEYS.get(mode, NUMERIC_TREND_PROPERTIES[mode][1]))
            self.trend_status_label.setText(self.tr("current_view_metric", name=trend_title))

    def refresh_info_panel(self):
        """Refresh the info panel: show a prompt if no element is selected, otherwise show element details."""
        element = self.current_selected_element
        prompt_text = build_info_panel_prompt(
            has_selected_element=element is not None,
            translate=self.tr,
        )
        if prompt_text is not None:
            self.info_panel.set_prompt(prompt_text)
            return

        self.show_element_info(element)

    def refresh_diagram_panel(self):
        """Refresh the orbital diagram panel based on the selected element and panel mode."""
        element = self.current_selected_element
        state = build_diagram_panel_state(
            is_diagram_mode=self.right_panel_mode == "diagram",
            has_selected_element=element is not None,
            translate=self.tr,
        )

        if state["action"] == "show_diagram":
            self.show_orbital_diagram(element)
            return

        self.orbital_diagram_panel.set_prompt(
            state["title"],
            state["text"],
        )

    def refresh_builder_panel(self, *, update_selectors=True):
        """Refresh all compound builder UI: selection text, status, selectors, and action buttons."""
        self.sync_builder_state_from_controls()
        self.refresh_builder_status()
        if update_selectors:
            self.refresh_builder_selector_texts()
        self.refresh_builder_action_accessibility()

    def refresh_builder_status(self):
        """Update the builder status label showing selected elements and their oxidation states."""
        if self.compound_a is None:
            text_a = self.tr("not_selected")
        else:
            oxidation_a = self.context.compound_builder_manager.state.element_a_oxidation
            text_a = (
                f"{self.compound_a['symbol']} "
                f"{self.format_oxidation_state(oxidation_a) if oxidation_a is not None else self.tr('traditional_na')}"
            )

        if self.compound_b is None:
            text_b = self.tr("not_selected")
        else:
            oxidation_b = self.context.compound_builder_manager.state.element_b_oxidation
            text_b = (
                f"{self.compound_b['symbol']} "
                f"{self.format_oxidation_state(oxidation_b) if oxidation_b is not None else self.tr('traditional_na')}"
            )

        self.compound_builder_panel.set_status_text(self.tr("builder_status", a=text_a, b=text_b))

    def refresh_builder_selector_texts(self):
        """Update the A/B selector summary labels with localized element names or placeholder text."""
        if self.compound_a is None:
            first_text = self.tr("first_element")
        else:
            first_text = self.tr(
                "first_selected",
                name=self.get_localized_element_name(self.compound_a),
                symbol=self.compound_a.get("symbol"),
            )

        if self.compound_b is None:
            second_text = self.tr("second_element")
        else:
            second_text = self.tr(
                "second_selected",
                name=self.get_localized_element_name(self.compound_b),
                symbol=self.compound_b.get("symbol"),
            )

        self.compound_builder_panel.set_selector_texts(first_text, second_text)
        self.compound_builder_panel.selector_a_summary_label.setToolTip(first_text)
        self.compound_builder_panel.selector_b_summary_label.setToolTip(second_text)

    def refresh_builder_action_accessibility(self):
        """Update tooltips and accessible descriptions on the search inputs."""
        for search_input, slot_text in (
            (self.search_a_input, self.compound_builder_panel.selector_a_summary_label.text()),
            (self.search_b_input, self.compound_builder_panel.selector_b_summary_label.text()),
        ):
            search_input.setToolTip(slot_text)
            search_input.setAccessibleDescription(slot_text)

    def refresh_compound_panel(self, *, rebuild=False):
        """Refresh the nomenclature result shown in the builder panel."""
        self.sync_builder_state_from_controls()
        has_compound_pair = self.compound_a is not None and self.compound_b is not None

        if rebuild:
            text = self.compose_compound_result_text() or ""
        elif has_compound_pair:
            preview = self.format_common_compounds_section()
            text = self.tr("pair_ready_prompt")
            if preview:
                text += "\n\n" + preview
        else:
            text = ""

        self.compound_builder_panel.set_result_text(text)

    def compose_compound_result_text(self):
        """Build the full compound result text (formula + IUPAC + traditional names)."""
        manager_state = self.context.compound_builder_manager.state
        return compose_compound_panel_text(
            compound_a=self.compound_a,
            compound_b=self.compound_b,
            first_oxidation=manager_state.element_a_oxidation,
            second_oxidation=manager_state.element_b_oxidation,
            common_section=self.format_common_compounds_section(),
            translate=self.tr,
            build_binary_formula=self.build_binary_formula,
            build_stock_name=self.build_stock_name,
            build_traditional_name=self.build_traditional_name,
            nomenclature_data=self.nomenclature_data,
            language_code=self.current_language,
        )

    def refresh_lewis_panel(self):
        """Refresh the Lewis dot diagram panel based on the selected element and panel mode."""
        element = self.current_selected_element
        is_lewis_mode = self.right_panel_mode == "lewis"
        title = self.tr("lewis_title")

        if is_lewis_mode and element is not None:
            self.lewis_panel.show_lewis_diagram(
                element,
                translate=self.tr,
                format_value=format_value,
            )
        elif is_lewis_mode:
            self.lewis_panel.set_prompt(title, self.tr("lewis_prompt"))
        elif element is not None:
            self.lewis_panel.set_prompt(title, self.tr("lewis_switch_prompt"))
        else:
            self.lewis_panel.set_prompt(title, self.tr("lewis_prompt"))

    def _refresh_panel_by_mode(self, mode):
        """Refresh a single right-panel page identified by its mode string."""
        if mode == "info":
            self.refresh_info_panel()
        elif mode == "diagram":
            self.refresh_diagram_panel()
        elif mode == "lewis":
            self.refresh_lewis_panel()

    def _refresh_panel_modes(self, modes):
        """Refresh multiple right-panel pages given an iterable of mode strings."""
        for mode in modes:
            self._refresh_panel_by_mode(mode)

    def refresh_right_panel_mode(self):
        """Switch the stacked layout to the active panel page and update button checked states."""
        state = build_right_panel_mode_state(
            mode=self.right_panel_mode,
            has_selected_element=self.current_selected_element is not None,
        )
        self.right_panel_stack.setCurrentIndex(state["stack_index"])

        for button_mode, button in self.right_panel_buttons.items():
            button.blockSignals(True)
            button.setChecked(state["checked_modes"][button_mode])
            button.blockSignals(False)

        self._refresh_panel_modes(state["refresh_modes"])

    def update_trend_status_text(self):
        """Convenience wrapper that delegates to refresh_trend_status."""
        self.refresh_trend_status()

    def get_localized_element_name(self, element):
        """Return the element name localized to the current UI language."""
        return self.nomenclature_controller.get_localized_element_name(element)

    def get_localized_anion_name(self, element):
        """Return the anion name of an element localized to the current UI language."""
        return self.nomenclature_controller.get_localized_anion_name(element)

    def interpolate_color(self, color1, color2, t):
        """Linearly interpolate between two hex colors by factor *t* (0..1)."""
        return interpolate_ui_color(color1, color2, t)

    def get_macro_class(self, category):
        """Map an element category to its macro-class label (metal / nonmetal / metalloid)."""
        return get_macro_class(category, traditional_na=self.tr("traditional_na"))

    def get_display_macro_class(self, category):
        """Return the localized display string for an element's macro-class."""
        return get_macro_class_text_for_language(
            self.get_macro_class(category),
            self.current_language,
            traditional_na=self.tr("traditional_na"),
        )

    def get_display_category(self, category):
        """Return the localized display string for an element category."""
        return get_category_text_for_language(
            category,
            self.current_language,
            traditional_na=self.tr("traditional_na"),
        )

    def get_display_standard_state(self, standard_state):
        """Return the localized display string for a standard state (solid/liquid/gas)."""
        return get_standard_state_text_for_language(
            standard_state,
            self.current_language,
            traditional_na=self.tr("traditional_na"),
        )

    def get_macro_class_color(self, macro_class):
        """Return the hex color associated with a macro-class label."""
        return get_macro_class_color(macro_class)

    def set_trend_mode(self, mode):
        """Activate a trend mode: delegate to manager, update UI, and refresh overlays."""
        # Delegate to manager (validates and sets the mode)
        self.context.trend_manager.set_trend_mode(mode)

        # Persist the choice
        self.settings_service.set_trend_mode(mode)

        # Update UI buttons
        for button_mode, button in self.trend_buttons.items():
            button.blockSignals(True)
            button.setChecked(button_mode == mode)
            button.blockSignals(False)

        # Update periodic table visual
        self.periodic_table_widget.set_trend_mode(mode)
        self.update_trend_status_text()

        # Refresh search highlights with new colors
        self.highlight_search_matches(
            [self.element_index[atomic_number] for atomic_number in self.current_search_matches]
        )

    def get_category_color(self, category):
        """Return the hex background color for a given element category."""
        return get_ui_category_color(category, theme=self.current_theme)

    def get_current_button_colors(self, element):
        """Compute the background and text colors for an element button under the active trend."""
        return get_ui_button_colors(
            element,
            trend_mode=self.active_trend_mode,
            numeric_ranges=self.context.trend_manager.numeric_ranges,
            get_macro_class=self.get_macro_class,
            get_macro_class_color=self.get_macro_class_color,
            theme=self.current_theme,
        )

    def _get_current_accent_color(self):
        """Return the accent hex for the active theme (used by the selected-cell halo)."""
        return TOKENS["color"]["theme"][self.current_theme]["accent"]

    def get_text_color(self, hex_color):
        """Return a contrasting text color (black or white) for a given hex background."""
        return get_ui_text_color(hex_color)

    def highlight_search_matches(self, matches):
        """Store matched atomic numbers and highlight the corresponding table buttons."""
        self.context.search_manager.matches = {element["atomic_number"] for element in matches}
        self.periodic_table_widget.highlight_search_matches(matches)

    def create_element_button(self, element):
        """Delegate element button creation to the periodic table widget."""
        return self.periodic_table_widget.create_element_button(element)

    def update_search_suggestions(self, text):
        """Update the suggestion dropdown and search highlights as the user types."""
        # Delegate to SearchManager to track search state
        matches_atomic_numbers = self.context.search_manager.search(text.strip())
        self.suggestions_list.clear()

        if not matches_atomic_numbers:
            self.suggestions_list.hide()
            self.set_search_status_text("")
            self.highlight_search_matches([])
            return

        # Convert atomic numbers to elements and rank for display
        matched_elements = [self.element_index[num] for num in matches_atomic_numbers if num in self.element_index]
        ranked_matches = self.get_ranked_matches(text.strip())

        # Show top matches in ranked order
        for element in ranked_matches:
            item_text = (
                f"{element['atomic_number']} - "
                f"{self.get_localized_element_name(element)} ({element['symbol']})"
            )
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, element["atomic_number"])
            self.suggestions_list.addItem(item)

        self.suggestions_list.show()
        self.highlight_search_matches(matched_elements)

    def compute_match_score(self, element, query):
        """Compute a relevance score for an element against a search query string."""
        localized_name = self.get_localized_element_name(element)
        return compute_search_match_score(
            element,
            query,
            localized_name=localized_name,
        )

    def get_ranked_matches(self, query, limit=6):
        """Return up to *limit* elements ranked by relevance to *query*."""
        return get_ranked_search_matches(
            self.elements,
            query,
            localized_name_getter=self.get_localized_element_name,
            limit=limit,
        )

    def handle_suggestion_clicked(self, item):
        """Select the element corresponding to a clicked suggestion list item."""
        atomic_number = item.data(Qt.UserRole)
        element = self.element_index.get(atomic_number)
        if element is not None:
            self.activate_element(element)
            self.search_input.setText(self.get_localized_element_name(element))
            self.suggestions_list.hide()
            self.set_search_status_text(
                self.tr(
                    "search_found",
                    name=self.get_localized_element_name(element),
                    symbol=element["symbol"],
                )
            )

    def search_element(self):
        """Execute a search: select the best match and update highlights and status text."""
        query = self.search_input.text().strip()
        if not query:
            self.set_search_status_text("")
            self.suggestions_list.hide()
            self.highlight_search_matches([])
            return

        matches = self.get_ranked_matches(query, limit=1)
        if matches:
            element = matches[0]
            self.activate_element(element)
            self.search_input.setText(self.get_localized_element_name(element))
            self.suggestions_list.hide()
            self.set_search_status_text(
                self.tr(
                    "search_found",
                    name=self.get_localized_element_name(element),
                    symbol=element["symbol"],
                )
            )
            self.highlight_search_matches([element])
        else:
            self.set_search_status_text(self.tr("search_not_found"))
            self.suggestions_list.hide()
            self.highlight_search_matches([])

    def _handle_table_selection(self, element):
        """Slot connected to the periodic table widget's element_selected signal."""
        self._apply_selected_element(element)

    def activate_element(self, element):
        """Programmatically select an element (convenience entry point)."""
        self.select_element(element)

    def select_element(self, element, button=None):
        """Select an element in the table widget and apply it as the active selection."""
        self.periodic_table_widget.select_element(element)
        self._apply_selected_element(element)

    def _apply_selected_element(self, element):
        """Store the selected element and refresh the header and info/diagram panels."""
        self.current_selected_element = element
        self.refresh_selection_header()
        self._refresh_panel_modes(("info", "diagram", "lewis"))
        symbol = element.get("symbol", "") if element else ""
        if symbol:
            self.solubility_panel.highlight_element(symbol)
        else:
            self.solubility_panel.clear_highlight()

    def parse_oxidation_states(self, oxidation_data):
        """Parse raw oxidation-state data into a sorted list of integers."""
        return parse_oxidation_states(oxidation_data)

    def format_oxidation_state(self, value):
        """Format an oxidation state integer as a signed string, or N/A if None."""
        return self.tr("traditional_na") if value is None else f"{value:+d}"

    def populate_oxidation_combo(self, combo, element):
        """Fill an oxidation-state combo box with states from *element*, or a single N/A entry."""
        combo.blockSignals(True)
        combo.clear()

        if element is None:
            combo.addItem(self.tr("traditional_na"), None)
            combo.setEnabled(False)
            combo.blockSignals(False)
            return

        states = self.parse_oxidation_states(element.get("oxidation_states"))
        if not states:
            combo.addItem(self.tr("traditional_na"), None)
        else:
            for state in states:
                combo.addItem(self.format_oxidation_state(state), state)

        combo.setEnabled(bool(states))
        combo.blockSignals(False)

    def get_current_oxidation(self, combo):
        """Return the currently selected oxidation state from a combo box, or None."""
        value = combo.currentData()
        return value if isinstance(value, int) else None

    def _on_search_element_a(self):
        """Search for an element by name/symbol and assign it to compound slot A."""
        query = self.search_a_input.text().strip()
        if not query:
            return
        matches = self.get_ranked_matches(query, limit=1)
        if matches:
            element = matches[0]
            self.compound_a = element
            self.search_a_input.setText(
                f"{self.get_localized_element_name(element)} ({element['symbol']})"
            )
            self.populate_oxidation_combo(self.a_oxidation_combo, element)

            # Delegate to manager (without oxidation state yet)
            self.context.compound_builder_manager.set_element_a(element["atomic_number"], 1)

            self.refresh_builder_panel()
            self.refresh_compound_panel()
        else:
            self.search_a_input.setText("")

    def _on_search_element_b(self):
        """Search for an element by name/symbol and assign it to compound slot B."""
        query = self.search_b_input.text().strip()
        if not query:
            return
        matches = self.get_ranked_matches(query, limit=1)
        if matches:
            element = matches[0]
            self.compound_b = element
            self.search_b_input.setText(
                f"{self.get_localized_element_name(element)} ({element['symbol']})"
            )
            self.populate_oxidation_combo(self.b_oxidation_combo, element)

            # Delegate to manager (without oxidation state yet)
            self.context.compound_builder_manager.set_element_b(element["atomic_number"], -1)

            self.refresh_builder_panel()
            self.refresh_compound_panel()
        else:
            self.search_b_input.setText("")

    def reset_builder(self):
        """Clear both compound slots, oxidation selections, and reset the builder UI."""
        # Delegate reset to manager
        self.context.compound_builder_manager.reset()

        # Clear MainWindow presentation state
        self.compound_a = None
        self.compound_b = None
        self.search_a_input.setText("")
        self.search_b_input.setText("")
        self.populate_oxidation_combo(self.a_oxidation_combo, None)
        self.populate_oxidation_combo(self.b_oxidation_combo, None)
        self.refresh_builder_status()
        self.refresh_compound_panel()

    def get_support_entry(self, symbol):
        """Look up the nomenclature support entry for a given element symbol."""
        return self.nomenclature_controller.get_support_entry(symbol)

    def get_language_naming_rules(self, language_code=None):
        """Return the naming-rule dict for the given (or current) language."""
        return self.nomenclature_controller.get_language_naming_rules(language_code)

    def get_localized_support_text(self, entry, field_prefix):
        """Return a localized nomenclature support text field from an entry."""
        return self.nomenclature_controller.get_localized_support_text(entry, field_prefix)

    def format_stock_compound_name(self, anion_name, cation_name, roman=None):
        """Build a localized IUPAC (Stock) compound name from anion/cation names and optional roman numeral."""
        return self.nomenclature_controller.format_stock_compound_name(
            anion_name, cation_name, roman,
        )

    def format_traditional_compound_name(self, anion_name, epithet):
        """Build a localized traditional compound name from anion name and suffix epithet."""
        return self.nomenclature_controller.format_traditional_compound_name(
            anion_name, epithet,
        )

    def int_to_roman(self, number):
        """Convert an integer to its Roman numeral representation."""
        return self.nomenclature_controller.int_to_roman(number)

    def update_builder_status(self, *args):
        """Signal handler that refreshes the builder panel when oxidation combos change."""
        self.refresh_builder_panel()

    def update_builder_selector_texts(self):
        """Signal handler that refreshes the builder selector labels."""
        self.refresh_builder_selector_texts()

    def get_compound_pair_key(self, symbol_a, symbol_b):
        """Return a canonical key string for a pair of element symbols."""
        return self.nomenclature_controller.get_compound_pair_key(symbol_a, symbol_b)

    def get_common_compounds_for_current_pair(self):
        """Return common compounds for the currently selected A/B element pair."""
        return self.nomenclature_controller.get_common_compounds_for_pair(
            self.compound_a, self.compound_b,
        )

    def get_localized_common_compound_name(self, compound_entry):
        """Return the localized display name for a common-compound entry."""
        return self.nomenclature_controller.get_localized_common_compound_name(compound_entry)

    def format_common_compounds_section(self):
        """Build the HTML section listing common compounds for the current pair."""
        return self.nomenclature_controller.format_common_compounds_section(
            self.compound_a, self.compound_b,
        )

    def update_compound_suggestions_preview(self):
        """Refresh the compound panel to update the common-compound preview."""
        self.refresh_compound_panel()

    def format_formula_part(self, symbol, count):
        """Format a single part of a chemical formula (symbol with optional subscript)."""
        return self.nomenclature_controller.format_formula_part(symbol, count)

    def build_binary_formula(self, cation_symbol, cation_charge, anion_symbol, anion_charge):
        """Build the balanced binary formula string from cation/anion symbols and charges."""
        return self.nomenclature_controller.build_binary_formula(
            cation_symbol, cation_charge, anion_symbol, anion_charge,
        )

    def build_stock_name(self, cation, cation_charge, anion):
        """Build the IUPAC (Stock) name for a binary compound from cation, charge, and anion."""
        return self.nomenclature_controller.build_stock_name(
            cation, cation_charge, anion,
        )

    def build_traditional_name(self, cation, cation_charge, anion):
        """Build the traditional name for a binary compound using suffix nomenclature."""
        return self.nomenclature_controller.build_traditional_name(
            cation, cation_charge, anion,
        )

    def build_compound(self):
        """Rebuild the formula result in the nomenclature area."""
        self.refresh_compound_panel(rebuild=True)

    def set_right_panel_mode(self, mode):
        """Activate a right-panel mode, persist the choice, and refresh the panel stack."""
        self.right_panel_mode = mode
        self.settings_service.set_right_panel_mode(mode)
        self.refresh_right_panel_mode()

    def set_tool_area_mode(self, mode):
        """Switch the tool area to a different mode (compounds, molar, stoichiometry)."""
        self.tool_area_mode = mode
        self.refresh_tool_area_mode()

    def refresh_tool_area_mode(self):
        """Switch the tool area stacked layout and update button checked states."""
        state = build_tool_area_mode_state(mode=self.tool_area_mode)
        self.tool_area_stack.setCurrentIndex(state["stack_index"])

        for button_mode, button in self.tool_area_buttons.items():
            button.blockSignals(True)
            button.setChecked(state["checked_modes"][button_mode])
            button.blockSignals(False)

    def show_element_info(self, element):
        """Render the full element-info view in the info panel."""
        self.info_panel.show_element_info(
            element,
            translate=self.tr,
            get_localized_element_name=self.get_localized_element_name,
            get_display_category=self.get_display_category,
            get_display_macro_class=self.get_display_macro_class,
            get_display_standard_state=self.get_display_standard_state,
            format_info_value=format_info_value,
        )

    def show_orbital_diagram(self, element):
        """Render the orbital diagram for the given element in the diagram panel."""
        self.orbital_diagram_panel.show_orbital_diagram(
            element,
            translate=self.tr,
            cell_size=self.cell_size,
            format_value=format_value,
        )

    def create_orbital_diagram_pixmap(self, config_text, symbol):
        """Create a QPixmap rendering of an orbital diagram from config text and symbol."""
        return self.orbital_diagram_panel.create_orbital_diagram_pixmap(
            config_text,
            symbol,
            self.cell_size,
        )

    def update_responsive_layout(self):
        """Recompute and apply the responsive layout policy based on the current window width."""
        self.layout_controller.apply()

    def resizeEvent(self, event):
        """Handle window resize by recomputing the responsive layout."""
        super().resizeEvent(event)
        self.update_responsive_layout()

    def showEvent(self, event):
        """Handle window show by applying the responsive layout."""
        super().showEvent(event)
        self.update_responsive_layout()

    def closeEvent(self, event):
        """Persist window preferences before the window closes."""
        self.persist_window_preferences()
        super().closeEvent(event)
