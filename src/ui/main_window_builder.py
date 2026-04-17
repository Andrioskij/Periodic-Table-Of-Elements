"""Stateless widget builders extracted from MainWindow.

Each function creates a slice of the widget hierarchy and returns a dict
of references (or the widget itself when a single object suffices).
MainWindow calls them during __init__, assigns the widgets as attributes,
and composes the top-level layouts.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from src.ui.panels.compound_panel import CompoundBuilderPanel
from src.ui.panels.info_panel import InfoPanel
from src.ui.panels.lewis_panel import LewisPanel
from src.ui.panels.molar_mass_panel import MolarMassPanel
from src.ui.panels.orbital_diagram_panel import OrbitalDiagramPanel
from src.ui.panels.solubility_panel import SolubilityPanel
from src.ui.panels.stoichiometry_panel import StoichiometryPanel
from src.ui.widgets.flow_layout import FlowLayout
from src.ui.widgets.periodic_table_widget import PeriodicTableWidget


def wrap_in_scroll_area(widget):
    """Wrap a widget in a QScrollArea with vertical scrolling only."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(widget)
    return scroll


def build_shell():
    """Create the outer layout, scroll area, content widget, and main layout."""
    outer_layout = QVBoxLayout()
    outer_layout.setContentsMargins(0, 0, 0, 0)
    outer_layout.setSpacing(0)

    main_scroll_area = QScrollArea()
    main_scroll_area.setWidgetResizable(True)
    main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    main_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    content_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(8, 8, 8, 8)
    main_layout.setSpacing(6)

    return {
        "outer_layout": outer_layout,
        "main_scroll_area": main_scroll_area,
        "content_widget": content_widget,
        "main_layout": main_layout,
    }


def build_title_row(
    *,
    about_text,
    language_options,
    on_about_clicked,
    on_language_changed,
):
    """Create the title label, About button, and language selector."""
    title_label = QLabel()
    title_label.setObjectName("titleLabel")
    title_label.setAlignment(Qt.AlignCenter)

    about_button = QPushButton(about_text)
    about_button.setObjectName("panelMiniButton")
    about_button.clicked.connect(on_about_clicked)

    language_selector = QComboBox()
    for code, label in language_options:
        language_selector.addItem(label, code)
    language_selector.currentIndexChanged.connect(on_language_changed)

    title_row = QHBoxLayout()
    title_row.setContentsMargins(0, 0, 0, 0)
    title_row.setSpacing(8)
    title_row.addStretch()
    title_row.addWidget(title_label, 1)
    title_row.addWidget(about_button, 0)
    title_row.addWidget(language_selector, 0)

    return {
        "title_label": title_label,
        "about_button": about_button,
        "language_selector": language_selector,
        "title_row": title_row,
    }


def build_search_widget(
    *,
    placeholder,
    search_button_text,
    on_text_changed,
    on_search,
    on_suggestion_clicked,
):
    """Create the element search card (input, button, suggestions, status)."""
    search_widget = QWidget()
    search_widget.setObjectName("searchCard")
    search_widget.setAttribute(Qt.WA_StyledBackground, True)
    layout = QVBoxLayout()
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(6)

    search_title_label = QLabel()
    search_title_label.setObjectName("searchTitleLabel")
    search_help_label = QLabel()
    search_help_label.setObjectName("searchHelpLabel")
    search_help_label.setWordWrap(True)
    search_help_label.hide()

    search_row = QHBoxLayout()
    search_row.setContentsMargins(0, 0, 0, 0)
    search_row.setSpacing(8)

    search_input = QLineEdit()
    search_input.setObjectName("searchInput")
    search_input.setClearButtonEnabled(True)
    search_input.setPlaceholderText(placeholder)
    search_input.textChanged.connect(on_text_changed)
    search_input.returnPressed.connect(on_search)

    search_button = QPushButton(search_button_text)
    search_button.setObjectName("searchButton")
    search_button.clicked.connect(on_search)

    search_row.addWidget(search_input, 1)
    search_row.addWidget(search_button, 0)

    suggestions_list = QListWidget()
    suggestions_list.setMaximumHeight(90)
    suggestions_list.hide()
    suggestions_list.itemClicked.connect(on_suggestion_clicked)

    search_status_label = QLabel("")
    search_status_label.setObjectName("searchStatusLabel")
    search_status_label.hide()

    layout.addWidget(search_title_label)
    layout.addWidget(search_help_label)
    layout.addLayout(search_row)
    layout.addWidget(suggestions_list)
    layout.addWidget(search_status_label)
    search_widget.setLayout(layout)
    search_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    return {
        "search_widget": search_widget,
        "search_title_label": search_title_label,
        "search_help_label": search_help_label,
        "search_input": search_input,
        "search_button": search_button,
        "suggestions_list": suggestions_list,
        "search_status_label": search_status_label,
    }


def build_top_controls_layout(search_widget):
    """Create the top controls layout hosting the search card."""
    top_controls_layout = QBoxLayout(QBoxLayout.LeftToRight)
    top_controls_layout.setContentsMargins(0, 0, 0, 0)
    top_controls_layout.setSpacing(10)
    top_controls_layout.addWidget(search_widget, 0, Qt.AlignTop | Qt.AlignLeft)
    top_controls_layout.addStretch(1)
    return top_controls_layout


def build_builder_widget(
    elements,
    *,
    tr,
    on_tool_mode_clicked,
    on_search_a,
    on_search_b,
    on_oxidation_changed,
    on_build,
    on_reset,
):
    """Create the tool area (compound builder, molar, stoichiometry, solubility)."""
    tool_area_buttons = {}
    tool_area_buttons_widget = QWidget()
    tool_area_buttons_layout = FlowLayout(spacing=6)

    tool_modes = [
        ("compounds", tr("tool_compounds")),
        ("molar", tr("tool_molar")),
        ("stoichiometry", tr("tool_stoichiometry")),
        ("solubility", tr("tool_solubility")),
    ]

    for mode, text_button in tool_modes:
        button = QPushButton(text_button)
        button.setObjectName("panelMiniButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, m=mode: on_tool_mode_clicked(m))
        tool_area_buttons[mode] = button
        tool_area_buttons_layout.addWidget(button)

    tool_area_buttons["compounds"].setChecked(True)
    tool_area_buttons_widget.setLayout(tool_area_buttons_layout)

    compound_builder_panel = CompoundBuilderPanel()
    compound_builder_panel.search_a_input.returnPressed.connect(on_search_a)
    compound_builder_panel.search_b_input.returnPressed.connect(on_search_b)
    compound_builder_panel.a_oxidation_combo.currentIndexChanged.connect(on_oxidation_changed)
    compound_builder_panel.b_oxidation_combo.currentIndexChanged.connect(on_oxidation_changed)
    compound_builder_panel.build_button.clicked.connect(on_build)
    compound_builder_panel.builder_reset_button.clicked.connect(on_reset)

    molar_mass_panel = MolarMassPanel(
        tr("molar_title"),
        tr("molar_prompt"),
        elements,
    )

    stoichiometry_panel = StoichiometryPanel(
        tr("stoichiometry_title"),
        tr("stoichiometry_prompt"),
        elements,
    )

    solubility_panel = SolubilityPanel(
        tr("solubility_title"),
        tr("solubility_prompt"),
    )

    tool_area_stack = QStackedLayout()
    tool_area_stack.setContentsMargins(0, 0, 0, 0)
    tool_area_stack.addWidget(compound_builder_panel)
    tool_area_stack.addWidget(molar_mass_panel)
    tool_area_stack.addWidget(stoichiometry_panel)
    tool_area_stack.addWidget(solubility_panel)

    tool_area_container = QWidget()
    tool_area_layout = QVBoxLayout()
    tool_area_layout.setContentsMargins(0, 0, 0, 0)
    tool_area_layout.setSpacing(6)
    tool_area_layout.addWidget(tool_area_buttons_widget)
    tool_area_layout.addLayout(tool_area_stack)
    tool_area_container.setLayout(tool_area_layout)

    return {
        "tool_area_mode": "compounds",
        "tool_area_buttons": tool_area_buttons,
        "tool_area_buttons_widget": tool_area_buttons_widget,
        "tool_area_buttons_layout": tool_area_buttons_layout,
        "compound_builder_panel": compound_builder_panel,
        "search_a_input": compound_builder_panel.search_a_input,
        "search_b_input": compound_builder_panel.search_b_input,
        "a_oxidation_label": compound_builder_panel.a_oxidation_label,
        "b_oxidation_label": compound_builder_panel.b_oxidation_label,
        "a_oxidation_combo": compound_builder_panel.a_oxidation_combo,
        "b_oxidation_combo": compound_builder_panel.b_oxidation_combo,
        "build_button": compound_builder_panel.build_button,
        "builder_reset_button": compound_builder_panel.builder_reset_button,
        "builder_status_label": compound_builder_panel.builder_status_label,
        "molar_mass_panel": molar_mass_panel,
        "stoichiometry_panel": stoichiometry_panel,
        "solubility_panel": solubility_panel,
        "tool_area_stack": tool_area_stack,
        "builder_widget": tool_area_container,
    }


def build_trend_controls(*, tr, trend_specs, on_trend_clicked):
    """Create the trend-mode toggle buttons and the trend status label."""
    trend_buttons = {}
    trend_container = QWidget()
    trend_flow_layout = FlowLayout(spacing=6)

    for mode, label_key in trend_specs:
        button = QPushButton(tr(label_key))
        button.setObjectName("trendButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, m=mode: on_trend_clicked(m))
        trend_flow_layout.addWidget(button)
        trend_buttons[mode] = button

    trend_buttons["normal"].setChecked(True)
    trend_container.setLayout(trend_flow_layout)

    trend_status_label = QLabel(tr("current_view_normal"))
    trend_status_label.setObjectName("trendStatusLabel")

    return {
        "trend_buttons": trend_buttons,
        "trend_container": trend_container,
        "trend_flow_layout": trend_flow_layout,
        "trend_status_label": trend_status_label,
    }


def build_periodic_table_widget(
    elements,
    element_index,
    *,
    format_value,
    get_macro_class,
    get_display_category,
    get_display_macro_class,
    get_button_colors,
    name_provider,
    on_element_selected,
):
    """Instantiate and wire the PeriodicTableWidget."""
    periodic_table_widget = PeriodicTableWidget(
        elements,
        element_index,
        format_value=format_value,
        get_macro_class=get_macro_class,
        get_display_category=get_display_category,
        get_display_macro_class=get_display_macro_class,
        get_button_colors=get_button_colors,
    )
    periodic_table_widget.set_name_provider(name_provider)
    periodic_table_widget.element_selected.connect(on_element_selected)
    return periodic_table_widget


def build_right_panel_area(*, tr, numeric_ranges, on_right_mode_clicked):
    """Create the right-side panel area (info, diagram, lewis) with mode buttons."""
    right_panel_buttons = {}
    right_panel_buttons_widget = QWidget()
    right_panel_buttons_layout = FlowLayout(spacing=6)

    right_modes = [
        ("info", tr("right_info")),
        ("diagram", tr("right_diagram")),
        ("lewis", tr("right_lewis")),
    ]

    for mode, text_button in right_modes:
        button = QPushButton(text_button)
        button.setObjectName("panelMiniButton")
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, m=mode: on_right_mode_clicked(m))
        right_panel_buttons[mode] = button
        right_panel_buttons_layout.addWidget(button)

    right_panel_buttons_widget.setLayout(right_panel_buttons_layout)

    info_panel = InfoPanel(
        tr("info_prompt"),
        numeric_ranges=numeric_ranges,
    )
    info_page = info_panel
    info_label = info_panel.info_label

    orbital_diagram_panel = OrbitalDiagramPanel(
        tr("diagram_title"),
        tr("diagram_prompt"),
    )
    diagram_page = wrap_in_scroll_area(orbital_diagram_panel)
    diagram_title_label = orbital_diagram_panel.title_label
    diagram_label = orbital_diagram_panel.diagram_label

    lewis_panel = LewisPanel(
        tr("lewis_title"),
        tr("lewis_prompt"),
    )
    lewis_page = wrap_in_scroll_area(lewis_panel)

    right_panel_container = QWidget()
    right_panel_stack = QStackedLayout()
    right_panel_stack.setContentsMargins(0, 0, 0, 0)
    right_panel_stack.addWidget(info_page)
    right_panel_stack.addWidget(diagram_page)
    right_panel_stack.addWidget(lewis_page)
    right_panel_container.setLayout(right_panel_stack)
    right_panel_container.setMinimumHeight(0)

    right_column_widget = QWidget()
    right_column_layout = QVBoxLayout()
    right_column_layout.setContentsMargins(0, 0, 0, 0)
    right_column_layout.setSpacing(8)
    right_column_layout.addWidget(right_panel_buttons_widget)
    right_column_layout.addWidget(right_panel_container, 1)
    right_column_widget.setLayout(right_column_layout)
    right_column_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    return {
        "right_panel_buttons": right_panel_buttons,
        "right_panel_buttons_widget": right_panel_buttons_widget,
        "right_panel_buttons_layout": right_panel_buttons_layout,
        "info_panel": info_panel,
        "info_page": info_page,
        "info_label": info_label,
        "orbital_diagram_panel": orbital_diagram_panel,
        "diagram_page": diagram_page,
        "diagram_title_label": diagram_title_label,
        "diagram_label": diagram_label,
        "lewis_panel": lewis_panel,
        "lewis_page": lewis_page,
        "right_panel_container": right_panel_container,
        "right_panel_stack": right_panel_stack,
        "right_column_widget": right_column_widget,
    }


def build_content_layout(periodic_table_widget, right_column_widget):
    """Create the horizontal/vertical content layout (table + right column)."""
    content_layout = QBoxLayout(QBoxLayout.LeftToRight)
    content_layout.setContentsMargins(0, 0, 0, 0)
    content_layout.setSpacing(12)
    content_layout.addWidget(periodic_table_widget, 0, Qt.AlignTop | Qt.AlignLeft)
    content_layout.addWidget(right_column_widget, 1)
    return content_layout
