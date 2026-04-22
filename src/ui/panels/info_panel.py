import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.domain.trends import get_macro_class, get_macro_class_color
from src.ui.scientific_data_notes import build_scientific_data_note

_logger = logging.getLogger(__name__)
from src.ui.styles import (
    DEFAULT_UI_COLOR,
    get_category_color,
    get_text_color,
    hex_to_rgba,
    interpolate_color,
)
from src.ui.widgets.flow_layout import FlowLayout


class _InfoSection(QWidget):
    """A labeled card displaying a group of element properties in a grid.

    Each section shows a title and a two-column grid of field labels
    and values. Fields listed in metric_fields also get a progress-bar
    visualization.
    """

    def __init__(self, field_definitions, *, metric_fields=()):
        super().__init__()
        self.field_definitions = field_definitions
        self.metric_fields = set(metric_fields)
        self.setObjectName("infoSectionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setObjectName("infoSectionTitle")

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(12)
        self.grid_layout.setVerticalSpacing(8)
        self.grid_layout.setColumnStretch(1, 1)

        self.field_label_widgets = {}
        self.field_value_widgets = {}
        self.metric_visual_widgets = {}
        self.metric_progress_bars = {}

        for row_index, (field_name, _translation_key) in enumerate(self.field_definitions):
            field_label = QLabel()
            field_label.setObjectName("infoFieldLabel")
            field_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            field_label.setWordWrap(True)

            field_value = QLabel()
            field_value.setObjectName("infoFieldValue")
            field_value.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            field_value.setWordWrap(True)

            self.grid_layout.addWidget(field_label, row_index, 0, Qt.AlignTop)

            if field_name in self.metric_fields:
                value_container = QWidget()
                value_container_layout = QVBoxLayout()
                value_container_layout.setContentsMargins(0, 0, 0, 0)
                value_container_layout.setSpacing(4)
                value_container_layout.addWidget(field_value)

                metric_visual = _MetricVisual()
                value_container_layout.addWidget(metric_visual)
                value_container.setLayout(value_container_layout)

                self.grid_layout.addWidget(value_container, row_index, 1)
                self.metric_visual_widgets[field_name] = metric_visual
                self.metric_progress_bars[field_name] = metric_visual.progress_bar
            else:
                self.grid_layout.addWidget(field_value, row_index, 1)

            self.field_label_widgets[field_name] = field_label
            self.field_value_widgets[field_name] = field_value

        layout.addWidget(self.title_label)
        layout.addLayout(self.grid_layout)
        self.setLayout(layout)

    def set_content(self, *, title, translate, values):
        self.title_label.setText(title)
        for field_name, translation_key in self.field_definitions:
            self.field_label_widgets[field_name].setText(translate(translation_key))
            self.field_value_widgets[field_name].setText(values.get(field_name, "—"))


class _MetricVisual(QWidget):
    """A small progress-bar widget that visualizes a numeric property's relative position.

    Normalizes the value to a 0-1000 scale between the dataset's
    min and max, then renders it as a colored bar with an accent
    color derived from the element's category.
    """

    NORMALIZED_SCALE = 1000

    def __init__(self):
        super().__init__()
        self.setObjectName("infoMetricVisualWidget")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("infoMetricProgressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, self.NORMALIZED_SCALE)
        self.progress_bar.setFixedHeight(8)

        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.normalized_value = 0
        self.has_data = False

        self.set_metric_value(None)
        self.apply_accent_color(DEFAULT_UI_COLOR)

    def set_metric_value(self, value, *, minimum=None, maximum=None):
        has_data = (
            isinstance(value, (int, float))
            and isinstance(minimum, (int, float))
            and isinstance(maximum, (int, float))
        )

        self.has_data = has_data
        self.setProperty("hasData", has_data)
        self.progress_bar.setProperty("hasData", has_data)

        if not has_data:
            self.normalized_value = 0
            self.progress_bar.setValue(0)
            self.progress_bar.hide()
            self.hide()
            return

        ratio = 0.5 if maximum == minimum else (value - minimum) / (maximum - minimum)
        ratio = max(0.0, min(1.0, ratio))
        self.normalized_value = int(round(ratio * self.NORMALIZED_SCALE))
        self.progress_bar.setValue(self.normalized_value)
        self.progress_bar.show()
        self.show()

    def apply_accent_color(self, accent_color):
        track_color = hex_to_rgba(accent_color, 24)
        track_border = interpolate_color("#404854", accent_color, 0.38)
        fill_color = interpolate_color("#7E8EA4", accent_color, 0.78)

        self.progress_bar.setStyleSheet(

                "QProgressBar#infoMetricProgressBar {"
                f"background-color: {track_color};"
                f"border: 1px solid {track_border};"
                "border-radius: 4px;"
                "}"
                "QProgressBar#infoMetricProgressBar::chunk {"
                f"background-color: {fill_color};"
                "border-radius: 4px;"
                "}"

        )


class _IsotopesSection(QWidget):
    """A section displaying common isotopes for an element.

    Shows isotope name, mass number, natural abundance (if stable),
    and half-life (if radioactive) in a list layout.
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("infoSectionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAccessibleName("Isotopes Section")
        self.setAccessibleDescription("Shows common isotopes for the selected element.")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setObjectName("infoSectionTitle")

        self.isotopes_layout = QVBoxLayout()
        self.isotopes_layout.setContentsMargins(0, 0, 0, 0)
        self.isotopes_layout.setSpacing(8)

        layout.addWidget(self.title_label)
        layout.addLayout(self.isotopes_layout)
        layout.addStretch()
        self.setLayout(layout)

    def set_content(self, *, title, isotopes, translate=None):
        # Clear existing isotope labels
        while self.isotopes_layout.count():
            widget = self.isotopes_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        self.title_label.setText(title)

        if not isotopes:
            fallback = "No isotope data available"
            empty_text = translate("no_isotope_data") if translate else fallback
            empty_label = QLabel(empty_text)
            empty_label.setObjectName("infoFieldValue")
            empty_label.setStyleSheet("color: #999;")
            self.isotopes_layout.addWidget(empty_label)
            return

        for iso in isotopes:
            name = iso.get("name", f"Isotope-{iso.get('mass_number', '?')}")
            mass = iso.get("mass_number", "?")
            iso_text = f"{name} (mass {mass})"
            abundance = iso.get("abundance")
            half_life = iso.get("half_life")
            if abundance is not None:
                iso_text += f" — {abundance:.2f}% abundant"
            elif half_life:
                iso_text += f" — Half-life: {half_life}"

            iso_label = QLabel(iso_text)
            iso_label.setObjectName("infoFieldValue")
            iso_label.setWordWrap(True)
            self.isotopes_layout.addWidget(iso_label)


class _IndustrialUsesSection(QWidget):
    """A section displaying industrial and commercial uses for an element.

    Shows use category and description in a list layout.
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("infoSectionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAccessibleName("Industrial Uses Section")
        self.setAccessibleDescription(
            "Shows industrial and commercial applications for the selected element."
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setObjectName("infoSectionTitle")

        self.uses_layout = QVBoxLayout()
        self.uses_layout.setContentsMargins(0, 0, 0, 0)
        self.uses_layout.setSpacing(8)

        layout.addWidget(self.title_label)
        layout.addLayout(self.uses_layout)
        layout.addStretch()
        self.setLayout(layout)

    def set_content(self, *, title, uses, translate=None):
        # Clear existing use labels
        while self.uses_layout.count():
            widget = self.uses_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        self.title_label.setText(title)

        if not uses:
            fallback = "No industrial use data available"
            empty_text = translate("no_industrial_data") if translate else fallback
            empty_label = QLabel(empty_text)
            empty_label.setObjectName("infoFieldValue")
            empty_label.setStyleSheet("color: #999;")
            self.uses_layout.addWidget(empty_label)
            return

        for use in uses:
            use_text = use.get("use", "Unknown")
            raw_category = use.get("category", "General")
            if translate:
                slug = raw_category.lower().replace(" ", "_").replace("-", "_")
                key = f"industrial_category_{slug}"
                localized = translate(key)
                display_category = localized if localized != key else raw_category
            else:
                display_category = raw_category
            use_category = f"[{display_category}]"

            category_label = QLabel(use_category)
            category_label.setObjectName("infoFieldLabel")
            category_label.setStyleSheet("font-weight: bold; font-size: 10px; color: #888;")

            use_label = QLabel(use_text)
            use_label.setObjectName("infoFieldValue")
            use_label.setWordWrap(True)

            self.uses_layout.addWidget(category_label)
            self.uses_layout.addWidget(use_label)


class InfoPanel(QScrollArea):
    """Scrollable panel showing detailed information about the selected element.

    Contains a hero section (symbol, name, badges), multiple property
    sections (identity, chemical, physical), metric progress bars, and
    a footer with data-quality notes. Adapts accent colors to match
    the element's category.
    """

    METRIC_VISUAL_RANGE_KEYS = {
        "electronegativity": "electronegativity",
        "ionization_energy": "ionization",
        "electron_affinity": "affinity",
        "atomic_radius": "radius",
    }
    SECTION_DEFINITIONS = (
        (
            "identity",
            "info_section_identity",
            (
                ("name", "name"),
                ("symbol", "symbol"),
                ("atomic_number", "atomic_number"),
                ("atomic_mass", "atomic_mass"),
                ("year_discovered", "year_discovered"),
            ),
        ),
        (
            "chemical_properties",
            "info_section_chemical_properties",
            (
                ("electronegativity", "electronegativity"),
                ("ionization_energy", "ionization_energy"),
                ("electron_affinity", "electron_affinity"),
                ("oxidation_states", "oxidation_states"),
            ),
        ),
        (
            "physical_properties",
            "info_section_physical_properties",
            (
                ("atomic_radius", "atomic_radius"),
                ("density", "density"),
                ("melting_point", "melting_point"),
                ("boiling_point", "boiling_point"),
                ("standard_state", "standard_state"),
            ),
        ),
    )

    def __init__(self, prompt_text, *, numeric_ranges=None):
        super().__init__()
        self.numeric_ranges = dict(numeric_ranges or {})
        self.setObjectName("infoPanel")
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.setAccessibleName("Info Panel")
        self.setAccessibleDescription("Displays details of the selected element.")

        self.prompt_label = QLabel(prompt_text)
        self.prompt_label.setAccessibleName("Info panel prompt")
        self.prompt_label.setAccessibleDescription("Prompt text shown when no element is selected.")
        self.prompt_label.setObjectName("infoPromptLabel")
        self.prompt_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.prompt_label.setWordWrap(True)

        self.info_label = QLabel(prompt_text)
        self.info_label.setObjectName("infoLabel")
        self.info_label.setAccessibleName("Info label")
        self.info_label.setAccessibleDescription("Displays element information and status updates.")
        self.info_label.hide()

        self.card_widget = QWidget()
        self.card_widget.setObjectName("infoCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(12)

        self.hero_widget = QWidget()
        self.hero_widget.setObjectName("infoHero")
        self.hero_widget.setAttribute(Qt.WA_StyledBackground, True)

        hero_shell_layout = QHBoxLayout()
        hero_shell_layout.setContentsMargins(12, 12, 12, 12)
        hero_shell_layout.setSpacing(12)

        self.hero_accent_bar = QWidget()
        self.hero_accent_bar.setObjectName("infoHeroAccentBar")
        self.hero_accent_bar.setAttribute(Qt.WA_StyledBackground, True)
        self.hero_accent_bar.setFixedWidth(6)

        hero_content_layout = QVBoxLayout()
        hero_content_layout.setContentsMargins(0, 0, 0, 0)
        hero_content_layout.setSpacing(10)

        hero_top_row = QHBoxLayout()
        hero_top_row.setContentsMargins(0, 0, 0, 0)
        hero_top_row.setSpacing(12)

        atomic_number_box = QVBoxLayout()
        atomic_number_box.setContentsMargins(0, 0, 0, 0)
        atomic_number_box.setSpacing(2)
        self.hero_atomic_number_caption_label = QLabel()
        self.hero_atomic_number_caption_label.setObjectName("infoHeroCaptionLabel")
        self.hero_atomic_number_value_label = QLabel()
        self.hero_atomic_number_value_label.setObjectName("infoHeroAtomicNumberLabel")
        atomic_number_box.addWidget(self.hero_atomic_number_caption_label)
        atomic_number_box.addWidget(self.hero_atomic_number_value_label)

        position_box = QVBoxLayout()
        position_box.setContentsMargins(0, 0, 0, 0)
        position_box.setSpacing(2)
        position_box.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.hero_position_caption_label = QLabel()
        self.hero_position_caption_label.setObjectName("infoHeroCaptionLabel")
        self.hero_position_caption_label.setAlignment(Qt.AlignRight)
        self.hero_position_value_label = QLabel()
        self.hero_position_value_label.setObjectName("infoHeroValueLabel")
        self.hero_position_value_label.setAlignment(Qt.AlignRight)
        position_box.addWidget(self.hero_position_caption_label)
        position_box.addWidget(self.hero_position_value_label)

        hero_top_row.addLayout(atomic_number_box)
        hero_top_row.addStretch()
        hero_top_row.addLayout(position_box)

        hero_main_row = QHBoxLayout()
        hero_main_row.setContentsMargins(0, 0, 0, 0)
        hero_main_row.setSpacing(14)

        self.hero_symbol_card = QWidget()
        self.hero_symbol_card.setObjectName("infoHeroSymbolCard")
        self.hero_symbol_card.setAttribute(Qt.WA_StyledBackground, True)
        hero_symbol_card_layout = QVBoxLayout()
        hero_symbol_card_layout.setContentsMargins(12, 10, 12, 10)
        hero_symbol_card_layout.setSpacing(0)
        self.hero_symbol_label = QLabel()
        self.hero_symbol_label.setObjectName("infoHeroSymbolLabel")
        self.hero_symbol_label.setAlignment(Qt.AlignCenter)
        hero_symbol_card_layout.addWidget(self.hero_symbol_label)
        self.hero_symbol_card.setLayout(hero_symbol_card_layout)

        hero_text_column = QVBoxLayout()
        hero_text_column.setContentsMargins(0, 0, 0, 0)
        hero_text_column.setSpacing(6)

        self.hero_name_label = QLabel()
        self.hero_name_label.setObjectName("infoHeroNameLabel")
        self.hero_name_label.setWordWrap(True)

        hero_meta_grid = QGridLayout()
        hero_meta_grid.setContentsMargins(0, 0, 0, 0)
        hero_meta_grid.setHorizontalSpacing(12)
        hero_meta_grid.setVerticalSpacing(6)
        hero_meta_grid.setColumnStretch(1, 1)

        self.hero_macro_class_caption_label = QLabel()
        self.hero_macro_class_caption_label.setObjectName("infoHeroCaptionLabel")
        self.hero_macro_class_value_label = QLabel()
        self.hero_macro_class_value_label.setObjectName("infoHeroValueLabel")
        self.hero_macro_class_value_label.setWordWrap(True)

        self.hero_standard_state_caption_label = QLabel()
        self.hero_standard_state_caption_label.setObjectName("infoHeroCaptionLabel")
        self.hero_standard_state_value_label = QLabel()
        self.hero_standard_state_value_label.setObjectName("infoHeroValueLabel")
        self.hero_standard_state_value_label.setWordWrap(True)

        hero_meta_grid.addWidget(self.hero_macro_class_caption_label, 0, 0, Qt.AlignTop)
        hero_meta_grid.addWidget(self.hero_macro_class_value_label, 0, 1)
        hero_meta_grid.addWidget(self.hero_standard_state_caption_label, 1, 0, Qt.AlignTop)
        hero_meta_grid.addWidget(self.hero_standard_state_value_label, 1, 1)

        hero_text_column.addWidget(self.hero_name_label)
        hero_text_column.addLayout(hero_meta_grid)

        hero_main_row.addWidget(self.hero_symbol_card, 0, Qt.AlignTop)
        hero_main_row.addLayout(hero_text_column, 1)

        self.hero_badges_widget = QWidget()
        self.hero_badges_widget.setStyleSheet("background: transparent;")
        self.hero_badges_layout = FlowLayout(spacing=6)
        self.hero_badges_layout.setContentsMargins(0, 0, 0, 0)
        self.hero_badges_widget.setLayout(self.hero_badges_layout)

        self.hero_badge_labels = {}
        self.hero_category_badge_label = self._create_badge_label("category")
        self.hero_standard_state_badge_label = self._create_badge_label("standard_state")
        self.hero_period_badge_label = self._create_badge_label("period")
        self.hero_group_badge_label = self._create_badge_label("group")

        hero_content_layout.addLayout(hero_top_row)
        hero_content_layout.addLayout(hero_main_row)
        hero_content_layout.addWidget(self.hero_badges_widget)

        hero_shell_layout.addWidget(self.hero_accent_bar)
        hero_shell_layout.addLayout(hero_content_layout, 1)
        self.hero_widget.setLayout(hero_shell_layout)

        card_layout.addWidget(self.hero_widget)

        self.sections = {}
        self.section_title_labels = {}
        self.field_value_labels = {}
        self.metric_visual_widgets = {}
        self.metric_progress_bars = {}

        for section_name, _, field_definitions in self.SECTION_DEFINITIONS:
            section = _InfoSection(
                field_definitions,
                metric_fields=self.METRIC_VISUAL_RANGE_KEYS,
            )
            self.sections[section_name] = section
            self.section_title_labels[section_name] = section.title_label
            self.field_value_labels.update(section.field_value_widgets)
            self.metric_visual_widgets.update(section.metric_visual_widgets)
            self.metric_progress_bars.update(section.metric_progress_bars)
            setattr(self, f"{section_name}_section", section)
            setattr(self, f"{section_name}_title_label", section.title_label)
            card_layout.addWidget(section)

        # Add isotopes section
        self.isotopes_section = _IsotopesSection()
        card_layout.addWidget(self.isotopes_section)

        # Add industrial uses section
        self.industrial_uses_section = _IndustrialUsesSection()
        card_layout.addWidget(self.industrial_uses_section)

        self.footer_label = QLabel()
        self.footer_label.setObjectName("infoFooterLabel")
        self.footer_label.setWordWrap(True)
        card_layout.addWidget(self.footer_label)

        self.card_widget.setLayout(card_layout)
        self.card_widget.hide()

        info_page_inner = QWidget()
        info_page_layout = QVBoxLayout()
        info_page_layout.setContentsMargins(0, 0, 0, 0)
        info_page_layout.setSpacing(8)
        info_page_layout.addWidget(self.prompt_label)
        info_page_layout.addWidget(self.card_widget)
        info_page_layout.addWidget(self.info_label)
        info_page_layout.addStretch()
        info_page_inner.setLayout(info_page_layout)

        self.setWidget(info_page_inner)

    def set_numeric_ranges(self, numeric_ranges):
        self.numeric_ranges = dict(numeric_ranges or {})

    def _create_badge_label(self, badge_name):
        label = QLabel()
        label.setObjectName("infoHeroBadgeLabel")
        label.setAlignment(Qt.AlignCenter)
        self.hero_badge_labels[badge_name] = label
        self.hero_badges_layout.addWidget(label)
        return label

    def set_prompt(self, text, prompt_text=None):
        self._clear_metric_visuals()
        display_text = prompt_text if prompt_text is not None else text
        self.info_label.setText(display_text)
        self.prompt_label.setText(display_text)
        self.prompt_label.show()
        self.card_widget.hide()

    def show_element_info(
        self,
        element,
        *,
        translate,
        get_localized_element_name,
        get_display_category,
        get_display_macro_class,
        get_display_standard_state,
        format_info_value,
    ):
        """Populate all panel sections with data for the given element.

        Formats every property value, updates the hero card, sections,
        metric bars, accent styles, and footer in a single pass.
        """
        values = self._build_rendered_values(
            element,
            translate=translate,
            get_localized_element_name=get_localized_element_name,
            get_display_category=get_display_category,
            get_display_macro_class=get_display_macro_class,
            get_display_standard_state=get_display_standard_state,
            format_info_value=format_info_value,
        )

        self.prompt_label.hide()
        self.card_widget.show()

        self.hero_atomic_number_caption_label.setText(translate("atomic_number"))
        self.hero_atomic_number_value_label.setText(values["atomic_number"])
        self.hero_position_caption_label.setText(f"{translate('period')} / {translate('group')}")
        self.hero_position_value_label.setText(f"{values['period']} / {values['group']}")
        self.hero_symbol_label.setText(values["symbol"])
        self.hero_name_label.setText(values["name"])
        self.hero_macro_class_caption_label.setText(translate("macro_class"))
        self.hero_macro_class_value_label.setText(values["macro_class"])
        self.hero_standard_state_caption_label.setText(translate("standard_state"))
        self.hero_standard_state_value_label.setText(values["standard_state"])

        self.hero_category_badge_label.setText(self._get_primary_category_badge_text(element, values))
        self.hero_standard_state_badge_label.setText(values["standard_state"])
        self.hero_period_badge_label.setText(f"{translate('period')} {values['period']}")
        self.hero_group_badge_label.setText(f"{translate('group')} {values['group']}")

        for section_name, title_key, _ in self.SECTION_DEFINITIONS:
            self.sections[section_name].set_content(
                title=translate(title_key),
                translate=translate,
                values=values,
            )

        # Import here to avoid circular dependency
        try:
            from src.services.element_properties import get_industrial_uses, get_isotopes

            isotopes = get_isotopes(element.get("symbol", ""))
            uses = get_industrial_uses(element.get("symbol", ""))
        except Exception:
            _logger.exception("Failed to load supplementary element data")
            isotopes = []
            uses = []

        # Update isotopes section
        isotopes_title = translate("isotopes")
        self.isotopes_section.set_content(
            title=isotopes_title, isotopes=isotopes, translate=translate,
        )

        # Update industrial uses section
        uses_title = translate("industrial_uses")
        self.industrial_uses_section.set_content(
            title=uses_title, uses=uses, translate=translate,
        )

        self._update_metric_visuals(element)
        self._apply_accent_styles(element, values)
        self.footer_label.setText(self._compose_footer_text(element, translate=translate))
        self.info_label.setText(self._compose_compatibility_text(element, values, translate=translate))

    def _build_rendered_values(
        self,
        element,
        *,
        translate,
        get_localized_element_name,
        get_display_category,
        get_display_macro_class,
        get_display_standard_state,
        format_info_value,
    ):
        na_text = translate("traditional_na")

        return {
            "name": get_localized_element_name(element),
            "symbol": format_info_value("symbol", element.get("symbol"), na_text=na_text),
            "atomic_number": format_info_value("atomic_number", element.get("atomic_number"), na_text=na_text),
            "atomic_mass": format_info_value("atomic_mass", element.get("atomic_mass"), na_text=na_text),
            "macro_class": get_display_macro_class(element.get("category")),
            "category": get_display_category(element.get("category")),
            "period": format_info_value("period", element.get("period"), na_text=na_text),
            "group": format_info_value("group", element.get("group"), na_text=na_text),
            "standard_state": get_display_standard_state(element.get("standard_state")),
            "electronegativity": format_info_value(
                "electronegativity",
                element.get("electronegativity"),
                na_text=na_text,
            ),
            "atomic_radius": format_info_value("atomic_radius", element.get("atomic_radius"), na_text=na_text),
            "ionization_energy": format_info_value(
                "ionization_energy",
                element.get("ionization_energy"),
                na_text=na_text,
            ),
            "electron_affinity": format_info_value(
                "electron_affinity",
                element.get("electron_affinity"),
                na_text=na_text,
            ),
            "oxidation_states": format_info_value(
                "oxidation_states",
                element.get("oxidation_states"),
                na_text=na_text,
            ),
            "melting_point": format_info_value("melting_point", element.get("melting_point"), na_text=na_text),
            "boiling_point": format_info_value("boiling_point", element.get("boiling_point"), na_text=na_text),
            "density": format_info_value("density", element.get("density"), na_text=na_text),
            "year_discovered": format_info_value(
                "year_discovered",
                element.get("year_discovered"),
                na_text=na_text,
            ),
        }

    def _get_primary_category_badge_text(self, element, values):
        if element.get("category"):
            return values["category"]
        return values["macro_class"]

    def _resolve_accent_color(self, element, values):
        category = element.get("category")
        category_color = get_category_color(category)
        if category and category_color != DEFAULT_UI_COLOR:
            return category_color

        macro_color = get_macro_class_color(get_macro_class(category))
        if macro_color != DEFAULT_UI_COLOR:
            return macro_color

        return DEFAULT_UI_COLOR

    def _apply_accent_styles(self, element, values):
        accent_color = self._resolve_accent_color(element, values)
        card_border = interpolate_color("#3C3C3C", accent_color, 0.24)
        hero_border = interpolate_color("#44515B", accent_color, 0.5)
        hero_background = hex_to_rgba(accent_color, 34)
        symbol_background = hex_to_rgba(accent_color, 22)
        symbol_border = interpolate_color("#44515B", accent_color, 0.55)
        meta_text_color = interpolate_color("#F2F2F2", accent_color, 0.26)
        symbol_text_color = interpolate_color("#F2F2F2", accent_color, 0.35)

        self.card_widget.setStyleSheet(
            f"background-color: #252526; border: 1px solid {card_border}; border-radius: 14px;"
        )
        self.hero_widget.setStyleSheet(
            f"background-color: {hero_background}; border: 1px solid {hero_border}; border-radius: 12px;"
        )
        self.hero_accent_bar.setStyleSheet(f"background-color: {accent_color}; border-radius: 3px;")
        self.hero_symbol_card.setStyleSheet(
            f"background-color: {symbol_background}; border: 1px solid {symbol_border}; border-radius: 12px;"
        )
        self.hero_atomic_number_value_label.setStyleSheet(f"color: {accent_color};")
        self.hero_position_value_label.setStyleSheet(f"color: {meta_text_color};")
        self.hero_macro_class_value_label.setStyleSheet(f"color: {meta_text_color};")
        self.hero_standard_state_value_label.setStyleSheet(f"color: {meta_text_color};")
        self.hero_symbol_label.setStyleSheet(f"color: {symbol_text_color};")

        self._apply_badge_styles(accent_color)
        self._apply_metric_visual_styles(accent_color)

    def _update_metric_visuals(self, element):
        for field_name, range_key in self.METRIC_VISUAL_RANGE_KEYS.items():
            minimum, maximum = self.numeric_ranges.get(range_key, (None, None))
            self.metric_visual_widgets[field_name].set_metric_value(
                element.get(field_name),
                minimum=minimum,
                maximum=maximum,
            )

    def _clear_metric_visuals(self):
        for visual_widget in self.metric_visual_widgets.values():
            visual_widget.set_metric_value(None)

    def _apply_badge_styles(self, accent_color):
        category_border = interpolate_color(accent_color, "#FFFFFF", 0.18)
        subtle_background = hex_to_rgba(accent_color, 34)
        subtle_border = interpolate_color("#55606D", accent_color, 0.55)

        self.hero_category_badge_label.setStyleSheet(
            self._build_badge_stylesheet(
                background_color=accent_color,
                border_color=category_border,
                text_color=get_text_color(accent_color),
            )
        )

        for label in (
            self.hero_standard_state_badge_label,
            self.hero_period_badge_label,
            self.hero_group_badge_label,
        ):
            label.setStyleSheet(
                self._build_badge_stylesheet(
                    background_color=subtle_background,
                    border_color=subtle_border,
                    text_color="#F2F2F2",
                )
            )

    def _apply_metric_visual_styles(self, accent_color):
        for visual_widget in self.metric_visual_widgets.values():
            visual_widget.apply_accent_color(accent_color)

    def _build_badge_stylesheet(self, *, background_color, border_color, text_color):
        return (
            "font-size: 11px; "
            "font-weight: bold; "
            "padding: 4px 10px; "
            "border-radius: 11px; "
            f"background-color: {background_color}; "
            f"border: 1px solid {border_color}; "
            f"color: {text_color};"
        )

    def _compose_footer_text(self, element, *, translate):
        footer_lines = [translate("more_info")]
        data_note = build_scientific_data_note(element, translate=translate)
        if data_note:
            footer_lines.append(data_note)
        return "\n".join(footer_lines)

    def _compose_compatibility_text(self, element, values, *, translate):
        lines = [
            f"{translate('name')}: {values['name']}",
            f"{translate('symbol')}: {values['symbol']}",
            f"{translate('atomic_number')}: {values['atomic_number']}",
            f"{translate('atomic_mass')}: {values['atomic_mass']}",
            f"{translate('macro_class')}: {values['macro_class']}",
            f"{translate('category')}: {values['category']}",
            f"{translate('period')}: {values['period']}",
            f"{translate('group')}: {values['group']}",
            f"{translate('standard_state')}: {values['standard_state']}",
            f"{translate('electronegativity')}: {values['electronegativity']}",
            f"{translate('atomic_radius')}: {values['atomic_radius']}",
            f"{translate('ionization_energy')}: {values['ionization_energy']}",
            f"{translate('electron_affinity')}: {values['electron_affinity']}",
            f"{translate('oxidation_states')}: {values['oxidation_states']}",
            f"{translate('melting_point')}: {values['melting_point']}",
            f"{translate('boiling_point')}: {values['boiling_point']}",
            f"{translate('density')}: {values['density']}",
            f"{translate('year_discovered')}: {values['year_discovered']}",
        ]

        return "\n".join(lines + self._compose_footer_text(element, translate=translate).splitlines())
