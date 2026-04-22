from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from src.ui.styles import build_periodic_button_stylesheet
from src.ui.styles import get_text_color as get_ui_text_color

from .trends_overlay import TrendsOverlay


class PeriodicTableWidget(QWidget):
    """Interactive periodic table grid built from QPushButtons.

    Renders all 118 elements in the standard periodic table layout,
    handles element selection, search highlighting, trend-mode coloring,
    and responsive resizing.
    """

    element_selected = Signal(object)

    def __init__(
        self,
        elements,
        element_index,
        *,
        format_value,
        get_macro_class,
        get_display_category,
        get_display_macro_class,
        get_button_colors,
    ):
        super().__init__()
        self.setObjectName("periodicTableWidget")

        self.elements = elements
        self.element_index = element_index
        self.format_value = format_value
        self.get_macro_class = get_macro_class
        self.get_display_category = get_display_category
        self.get_display_macro_class = get_display_macro_class
        self.get_button_colors = get_button_colors

        self.element_buttons = {}
        self.group_header_labels = {}
        self.period_labels = {}
        self.series_labels = {}
        self.corner_label = None
        self.transition_label = None
        self.selected_element_name_label = None
        self.selected_button = None
        self.current_selected_element = None
        self.current_search_matches = set()
        self.active_trend_mode = "normal"

        self.cell_size = 50
        self.header_height = 24
        self.side_width = 48
        self.grid_h_spacing = 4
        self.grid_v_spacing = 4
        self.element_font_size = 12

        self.selected_none_text = "No element selected"
        self.transition_text = "TRANSITION METALS"
        self.name_provider = lambda element: str(element.get("name", ""))

        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        table_base = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(self.grid_h_spacing)
        self.grid_layout.setVerticalSpacing(self.grid_v_spacing)
        table_base.setLayout(self.grid_layout)

        self.add_classic_group_headers()
        self.add_period_headers()
        self.add_series_labels()
        self.add_transition_block_label()
        self.build_periodic_table()

        self.table_stack_container = QWidget()
        table_stack_layout = QStackedLayout()
        table_stack_layout.setStackingMode(QStackedLayout.StackAll)
        table_stack_layout.setContentsMargins(0, 0, 0, 0)

        self.trends_overlay = TrendsOverlay()
        self.trends_overlay.hide()

        table_stack_layout.addWidget(table_base)
        table_stack_layout.addWidget(self.trends_overlay)
        self.table_stack_container.setLayout(table_stack_layout)
        self.table_stack_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        root_layout.addWidget(self.table_stack_container, 0, Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(root_layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_name_provider(self, name_provider):
        self.name_provider = name_provider
        self.refresh_selected_element_name()

    def set_language_texts(self, *, selected_none_text, transition_text, metallic_text, nonmetallic_text):
        self.selected_none_text = selected_none_text
        self.transition_text = transition_text
        if self.transition_label is not None:
            self.transition_label.setText(transition_text)
        self.trends_overlay.set_texts(metallic_text, nonmetallic_text)
        self.refresh_selected_element_name()

    def refresh_selected_element_name(self):
        if self.selected_element_name_label is None:
            return

        if self.current_selected_element is None:
            self.selected_element_name_label.setText(self.selected_none_text)
            self.selected_element_name_label.setAccessibleDescription("No element is currently selected.")
        else:
            self.selected_element_name_label.setText(
                self.name_provider(self.current_selected_element)
            )
            self.selected_element_name_label.setAccessibleDescription(
                f"Currently selected element: {self.name_provider(self.current_selected_element)}."
            )

    def set_trend_mode(self, mode):
        """Switch the color scheme to the given trend visualization mode.

        For directional trends (metallic/nonmetallic), shows the arrow
        overlay. For all modes, repaints every element button with the
        appropriate color mapping.
        """
        self.active_trend_mode = mode
        if mode in {"metallic", "nonmetallic"}:
            self.trends_overlay.set_mode(mode)
            self.trends_overlay.show()
        else:
            self.trends_overlay.set_mode(None)
            self.trends_overlay.hide()
        self.refresh_button_styles()

    def create_grid_label(self, text, object_name, width, height):
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(width, height)
        return label

    def add_classic_group_headers(self):
        self.corner_label = self.create_grid_label("", "headerLabel", self.side_width, self.header_height)
        self.grid_layout.addWidget(self.corner_label, 0, 0)

        group_ia = self.create_grid_label("IA", "headerLabel", self.cell_size, self.header_height)
        group_iia = self.create_grid_label("IIA", "headerLabel", self.cell_size, self.header_height)
        self.grid_layout.addWidget(group_ia, 0, 1)
        self.grid_layout.addWidget(group_iia, 0, 2)
        self.group_header_labels[1] = group_ia
        self.group_header_labels[2] = group_iia

        headers = {13: "IIIA", 14: "IVA", 15: "VA", 16: "VIA", 17: "VIIA", 18: "VIIIA"}
        for column, text in headers.items():
            label = self.create_grid_label(text, "headerLabel", self.cell_size, self.header_height)
            self.grid_layout.addWidget(label, 0, column)
            self.group_header_labels[column] = label

    def add_period_headers(self):
        for period in range(1, 8):
            label = self.create_grid_label(str(period), "sideLabel", self.side_width, self.cell_size)
            self.grid_layout.addWidget(label, period, 0)
            self.period_labels[period] = label

    def add_series_labels(self):
        lanthanides_label = self.create_grid_label("La-Lu", "seriesLabel", self.side_width, self.cell_size)
        actinides_label = self.create_grid_label("Ac-Lr", "seriesLabel", self.side_width, self.cell_size)
        self.grid_layout.addWidget(lanthanides_label, 8, 0)
        self.grid_layout.addWidget(actinides_label, 9, 0)
        self.series_labels[8] = lanthanides_label
        self.series_labels[9] = actinides_label

    def add_transition_block_label(self):
        self.selected_element_name_label = QLabel(self.selected_none_text)
        self.selected_element_name_label.setObjectName("selectedElementNameLabel")
        self.selected_element_name_label.setAlignment(Qt.AlignCenter)
        self.selected_element_name_label.setAccessibleName("Selected element header")
        self.grid_layout.addWidget(self.selected_element_name_label, 1, 3, 2, 10)

        self.transition_label = QLabel(self.transition_text)
        self.transition_label.setObjectName("transitionBlockLabel")
        self.transition_label.setAlignment(Qt.AlignCenter)
        self.transition_label.setAccessibleName("Transition block label")
        self.transition_label.setAccessibleDescription("Label for the transition metals section.")
        self.grid_layout.addWidget(self.transition_label, 3, 3, 1, 10)

    def build_periodic_table(self):
        for element in self.elements:
            button = self.create_element_button(element)
            self.grid_layout.addWidget(button, element["display_row"], element["display_column"])
            self.element_buttons[element["atomic_number"]] = button

    def create_element_button(self, element):
        button_text = f"{element['atomic_number']}\n{element['symbol']}"
        button = QPushButton(button_text)
        button.setCheckable(True)
        button.setFocusPolicy(Qt.StrongFocus)
        button.setCursor(Qt.PointingHandCursor)
        button.setProperty("atomicNumber", element["atomic_number"])
        self.apply_button_style(button, element["atomic_number"], search_match=False)
        button.clicked.connect(
            lambda checked=False, e=element, b=button: self._handle_button_clicked(e, b)
        )
        return button

    def _handle_button_clicked(self, element, button):
        self._apply_selection(element, button)
        self.element_selected.emit(element)

    def _apply_selection(self, element, button):
        self.current_selected_element = element

        previous_button = self.selected_button
        if self.selected_button is not None and self.selected_button is not button:
            self.selected_button.setChecked(False)

        self.selected_button = button
        button.setChecked(True)
        if previous_button is not None and previous_button is not button:
            previous_atomic_number = previous_button.property("atomicNumber")
            self.apply_button_style(
                previous_button,
                previous_atomic_number,
                search_match=(previous_atomic_number in self.current_search_matches),
            )
        self.apply_button_style(
            button,
            element["atomic_number"],
            search_match=(element["atomic_number"] in self.current_search_matches),
        )
        self.refresh_selected_element_name()

    def select_element(self, element):
        button = self.element_buttons.get(element["atomic_number"])
        if button is None:
            return
        self._apply_selection(element, button)

    def get_text_color(self, hex_color):
        return get_ui_text_color(hex_color)

    def apply_button_style(self, button, atomic_number, search_match=False):
        element = self.element_index[atomic_number]
        background_color, text_color = self.get_button_colors(element)
        button.setStyleSheet(
            build_periodic_button_stylesheet(
                background_color=background_color,
                text_color=text_color,
                cell_size=self.cell_size,
                element_font_size=self.element_font_size,
                search_match=search_match,
            )
        )
        self._apply_button_metadata(
            button,
            element,
            search_match=search_match,
        )

    def _apply_button_metadata(self, button, element, *, search_match):
        is_selected = button is self.selected_button
        symbol = element["symbol"]
        localized_name = self.name_provider(element)
        raw_name = str(element.get("name", localized_name))
        category = self.get_display_category(element.get("category"))
        macro_class = self.get_display_macro_class(element.get("category"))
        button.setObjectName(self._build_button_object_name(symbol, is_selected=is_selected, search_match=search_match))
        button.setToolTip(f"{localized_name} - {category} - {macro_class}")

        accessible_name = f"Element {raw_name}, atomic number {element['atomic_number']}"
        if is_selected and search_match:
            accessible_name += ", selected and search highlighted"
        elif is_selected:
            accessible_name += ", selected"
        elif search_match:
            accessible_name += ", search highlighted"
        button.setAccessibleName(accessible_name)

        accessible_description = f"Click to select {raw_name} ({symbol})"
        if is_selected:
            accessible_description += ". Currently selected."
        if search_match:
            accessible_description += " Matches the current search."
        button.setAccessibleDescription(accessible_description)

    def _build_button_object_name(self, symbol, *, is_selected, search_match):
        if is_selected and search_match:
            return f"elementButtonSelectedHighlight_{symbol}"
        if is_selected:
            return f"elementButtonSelected_{symbol}"
        if search_match:
            return f"elementButtonHighlight_{symbol}"
        return f"elementButton_{symbol}"

    def refresh_button_styles(self):
        for atomic_number, button in self.element_buttons.items():
            self.apply_button_style(
                button,
                atomic_number,
                search_match=(atomic_number in self.current_search_matches),
            )

    def highlight_search_matches(self, matches):
        """Apply a visual highlight border to all element buttons that match the search."""
        self.current_search_matches = {element["atomic_number"] for element in matches}
        self.refresh_button_styles()

    def update_metrics(
        self,
        *,
        cell_size,
        header_height,
        side_width,
        grid_h_spacing,
        grid_v_spacing,
        element_font_size,
    ):
        """Resize the entire table grid to match new responsive layout metrics.

        Updates cell sizes, spacing, header dimensions, and repaints
        all buttons to keep the table visually consistent after a
        window resize.
        """
        self.cell_size = cell_size
        self.header_height = header_height
        self.side_width = side_width
        self.grid_h_spacing = grid_h_spacing
        self.grid_v_spacing = grid_v_spacing
        self.element_font_size = element_font_size

        self.grid_layout.setHorizontalSpacing(self.grid_h_spacing)
        self.grid_layout.setVerticalSpacing(self.grid_v_spacing)

        if self.corner_label is not None:
            self.corner_label.setFixedSize(self.side_width, self.header_height)

        for label in self.group_header_labels.values():
            label.setFixedSize(self.cell_size, self.header_height)

        for label in self.period_labels.values():
            label.setFixedSize(self.side_width, self.cell_size)

        for label in self.series_labels.values():
            label.setFixedSize(self.side_width, self.cell_size)

        if self.transition_label is not None:
            self.transition_label.setFixedHeight(self.header_height)

        for button in self.element_buttons.values():
            button.setFixedSize(self.cell_size, self.cell_size)

        self.refresh_button_styles()
        self.table_stack_container.adjustSize()
        self.adjustSize()
