"""Right-side panel that renders Lewis dot diagrams.

Two display paths share the same panel:

- Single atom: ``show_lewis_diagram(element)`` keeps the original
  behaviour of drawing a centred element symbol with valence dots.
- Multi-atom molecule: the user types a formula in the input row at
  the top of the panel and gets back a pre-built Lewis structure from
  ``src.domain.lewis_library.MOLECULE_LIBRARY``.

The panel itself stays self-contained: the formula input slot resolves
unknown formulas first against the molecule library, then against the
elements dataset (single-element fallback), and finally shows a
"not in library" message.
"""

import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.domain.lewis_diagram import (
    distribute_dots,
    get_valence_electrons,
    lookup_molecule,
)
from src.ui.theme import get_theme

_SIDE_NAMES = ("right", "top", "left", "bottom")


def _classify_side(dx: float, dy: float) -> str:
    """Return which side (top/right/bottom/left) of the origin a point lies on.

    Uses the chemistry-Y convention (positive Y is up). Diagonal ties
    are resolved by 45° quadrants centred on each cardinal direction.
    """
    angle = math.degrees(math.atan2(dy, dx)) % 360.0
    idx = int((angle + 45.0) // 90.0) % 4
    return _SIDE_NAMES[idx]


class LewisPanel(QWidget):
    """Right-side panel displaying single-atom or multi-atom Lewis diagrams."""

    def __init__(self, title_text, prompt_text, elements=None):
        super().__init__()
        self.elements = elements or []
        self.setObjectName("lewisPanel")
        self.setFocusPolicy(Qt.StrongFocus)
        self._theme = get_theme("dark")
        # Either ("element", symbol, valence) or ("molecule", formula).
        self._last_render = None
        self._translate = None
        self._format_value = str
        self._not_in_library_message = (
            "Lewis structure for this molecule is not in the library."
        )

        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("diagramTitleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setAccessibleName("Lewis diagram title")

        self.formula_input = QLineEdit()
        self.formula_input.setObjectName("lewisFormulaInput")
        self.formula_input.setAccessibleName("Lewis molecule formula input")
        self.formula_input.setPlaceholderText(
            "Enter a molecule formula (e.g., H2O)"
        )

        self.show_molecule_button = QPushButton("Show")
        self.show_molecule_button.setObjectName("lewisShowMoleculeButton")
        self.show_molecule_button.setAccessibleName("Show Lewis structure")
        self.show_molecule_button.clicked.connect(self._on_molecule_submit)
        self.formula_input.returnPressed.connect(self._on_molecule_submit)

        formula_row = QHBoxLayout()
        formula_row.setContentsMargins(0, 0, 0, 0)
        formula_row.setSpacing(6)
        formula_row.addWidget(self.formula_input, 1)
        formula_row.addWidget(self.show_molecule_button, 0)

        self.diagram_label = QLabel(prompt_text)
        self.diagram_label.setAccessibleName("Lewis diagram display")
        self.diagram_label.setAccessibleDescription(
            "Displays Lewis dot diagram or instructions."
        )
        self.diagram_label.setObjectName("diagramBoxLabel")
        self.diagram_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.diagram_label.setWordWrap(True)
        self.diagram_label.setMinimumHeight(260)

        self.valence_label = QLabel("")
        self.valence_label.setObjectName("lewisValenceLabel")
        self.valence_label.setAlignment(Qt.AlignCenter)
        self.valence_label.setWordWrap(True)

        self.card_widget = QWidget()
        self.card_widget.setObjectName("sidePanelCard")
        self.card_widget.setAttribute(Qt.WA_StyledBackground, True)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        card_layout.addWidget(self.title_label)
        card_layout.addLayout(formula_row)
        card_layout.addWidget(self.diagram_label)
        card_layout.addWidget(self.valence_label)
        self.card_widget.setLayout(card_layout)

        self.setAccessibleName("Lewis Diagram Panel")
        self.setAccessibleDescription(
            "Contains Lewis dot diagram for the selected element or molecule."
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.card_widget)
        layout.addStretch()
        self.setLayout(layout)

    def set_translator(self, translate, format_value=str):
        """Provide the translator the formula-input slot can call later."""
        self._translate = translate
        self._format_value = format_value

    def set_prompt(self, title_text, prompt_text):
        """Show a text prompt instead of a diagram."""
        self.title_label.setText(title_text)
        self.diagram_label.setPixmap(QPixmap())
        self.diagram_label.setText(prompt_text)
        self.valence_label.setText("")
        self._last_render = None

    def apply_theme(self, theme_name):
        """Switch the painter palette and redraw the last diagram, if any."""
        new_theme = get_theme(theme_name)
        if new_theme is self._theme:
            return
        self._theme = new_theme
        self._redraw_last_render()

    def _redraw_last_render(self):
        """Re-render whatever was last shown using the current theme/language."""
        if self._last_render is None:
            return
        kind = self._last_render[0]
        if kind == "element":
            _, symbol, valence = self._last_render
            self.diagram_label.setPixmap(
                self._create_lewis_pixmap(symbol, valence)
            )
        elif kind == "molecule":
            _, formula = self._last_render
            diagram = lookup_molecule(formula)
            if diagram is not None:
                self.diagram_label.setPixmap(self._render_molecule(diagram))

    def show_lewis_diagram(self, element, *, translate, format_value):
        """Generate and display the Lewis dot diagram for the given element."""
        self._translate = translate
        self._format_value = format_value
        symbol = format_value(element.get("symbol"))
        self.title_label.setText(translate("lewis_title"))

        valence = get_valence_electrons(element)
        if valence is None:
            self.diagram_label.setPixmap(QPixmap())
            self.diagram_label.setText(translate("lewis_not_applicable"))
            self.valence_label.setText("")
            self._last_render = None
            return

        pixmap = self._create_lewis_pixmap(symbol, valence)
        self.diagram_label.setText("")
        self.diagram_label.setPixmap(pixmap)
        self.valence_label.setText(
            translate("lewis_valence_electrons", count=valence)
        )
        self._last_render = ("element", symbol, valence)

    def _on_molecule_submit(self):
        """Resolve the typed formula against the molecule library or fall back."""
        text = self.formula_input.text().strip()
        if not text:
            return

        diagram = lookup_molecule(text)
        if diagram is not None:
            self.title_label.setText(self._tr("lewis_title"))
            pixmap = self._render_molecule(diagram)
            self.diagram_label.setText("")
            self.diagram_label.setPixmap(pixmap)
            self.valence_label.setText("")
            self._last_render = ("molecule", diagram.formula)
            return

        element = self._find_element_by_symbol(text)
        if element is not None:
            self.show_lewis_diagram(
                element,
                translate=self._translate or (lambda key, **_: key),
                format_value=self._format_value,
            )
            return

        self.diagram_label.setPixmap(QPixmap())
        self.diagram_label.setText(self._tr("lewis_not_in_library"))
        self.valence_label.setText("")
        self._last_render = None

    def _find_element_by_symbol(self, text: str) -> dict | None:
        """Return an element record whose symbol matches the input casing."""
        symbol = text.strip()
        if not symbol:
            return None
        # Strict case-sensitive match first (Na ≠ NA), then a case-fold
        # fallback to be friendly with lowercase user input.
        for element in self.elements:
            if element.get("symbol") == symbol:
                return element
        lowered = symbol.casefold()
        for element in self.elements:
            sym = element.get("symbol")
            if sym and sym.casefold() == lowered:
                return element
        return None

    def _tr(self, key, **kwargs):
        """Translate via the cached translator, falling back to the key."""
        if self._translate is None:
            fallbacks = {
                "lewis_not_in_library": self._not_in_library_message,
            }
            return fallbacks.get(key, key)
        return self._translate(key, **kwargs)

    def _create_lewis_pixmap(self, symbol, valence_electrons):
        """Render the single-atom Lewis dot diagram as a QPixmap."""
        theme = self._theme
        size = 240
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(theme["painter_bg"]))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw element symbol at center
        symbol_font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(symbol_font)
        painter.setPen(QColor(theme["painter_text"]))
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(symbol)
        text_height = fm.height()
        cx = size // 2
        cy = size // 2
        painter.drawText(
            cx - text_width // 2,
            cy + fm.ascent() // 2 - 2,
            symbol,
        )

        dots = distribute_dots(valence_electrons)
        dot_radius = 5
        dot_color = QColor(theme["painter_dot"])
        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)

        pair_gap = 12

        sym_left = cx - text_width // 2 - 8
        sym_right = cx + text_width // 2 + 8
        sym_top = cy - text_height // 2 + 4
        sym_bottom = cy + text_height // 2 - 4

        count = dots["top"]
        top_y = sym_top - 16
        if count == 1:
            painter.drawEllipse(cx - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(cx - pair_gap // 2 - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(cx + pair_gap // 2 - dot_radius, top_y - dot_radius, dot_radius * 2, dot_radius * 2)

        count = dots["bottom"]
        bottom_y = sym_bottom + 16
        if count == 1:
            painter.drawEllipse(cx - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(cx - pair_gap // 2 - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(cx + pair_gap // 2 - dot_radius, bottom_y - dot_radius, dot_radius * 2, dot_radius * 2)

        count = dots["right"]
        right_x = sym_right + 16
        if count == 1:
            painter.drawEllipse(right_x - dot_radius, cy - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(right_x - dot_radius, cy - pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(right_x - dot_radius, cy + pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)

        count = dots["left"]
        left_x = sym_left - 16
        if count == 1:
            painter.drawEllipse(left_x - dot_radius, cy - dot_radius, dot_radius * 2, dot_radius * 2)
        elif count == 2:
            painter.drawEllipse(left_x - dot_radius, cy - pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)
            painter.drawEllipse(left_x - dot_radius, cy + pair_gap // 2 - dot_radius, dot_radius * 2, dot_radius * 2)

        painter.end()
        return pixmap

    def _render_molecule(self, diagram):
        """Render a multi-atom Lewis structure as a QPixmap."""
        theme = self._theme
        size = 240
        padding = 30
        pixmap = QPixmap(size, size)
        bg_color = QColor(theme["painter_bg"])
        text_color = QColor(theme["painter_text"])
        dot_color = QColor(theme["painter_dot"])
        pixmap.fill(bg_color)

        if not diagram.atoms:
            return pixmap

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        atom_count = len(diagram.atoms)
        font_size = 18 if atom_count <= 4 else 16
        symbol_font = QFont("Segoe UI", font_size, QFont.Bold)
        painter.setFont(symbol_font)
        fm = painter.fontMetrics()

        # Map [-1, 1] (or actual bbox) chemistry coords to pixel coords.
        xs = [a.x for a in diagram.atoms]
        ys = [a.y for a in diagram.atoms]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        x_span = max(x_max - x_min, 0.5)
        y_span = max(y_max - y_min, 0.5)
        # Use whichever axis is larger to keep aspect ratio.
        scale = (size - 2 * padding) / max(x_span, y_span)
        x_offset = size / 2 - (x_min + x_max) / 2 * scale
        y_offset = size / 2 + (y_min + y_max) / 2 * scale

        def to_pixel(x: float, y: float) -> tuple[float, float]:
            # Flip Y: positive chemistry-Y goes up, pixmap-Y goes down.
            return (x * scale + x_offset, -y * scale + y_offset)

        atom_pixels = [to_pixel(a.x, a.y) for a in diagram.atoms]

        # Draw bonds first.
        bond_pen = QPen(text_color)
        bond_pen.setWidth(2)
        bond_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bond_pen)
        atom_clearance = font_size  # px to leave around each symbol
        bond_offset_gap = 4

        for bond in diagram.bonds:
            x1, y1 = atom_pixels[bond.atom1]
            x2, y2 = atom_pixels[bond.atom2]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                continue
            ux, uy = dx / length, dy / length
            # Shrink endpoints to keep the line clear of the atom symbol.
            sx1 = x1 + ux * atom_clearance
            sy1 = y1 + uy * atom_clearance
            sx2 = x2 - ux * atom_clearance
            sy2 = y2 - uy * atom_clearance
            # Perpendicular offset for multi-bond parallel lines.
            px, py = -uy, ux
            for line_idx in self._bond_line_offsets(bond.order):
                ox = px * line_idx * bond_offset_gap
                oy = py * line_idx * bond_offset_gap
                painter.drawLine(
                    int(round(sx1 + ox)),
                    int(round(sy1 + oy)),
                    int(round(sx2 + ox)),
                    int(round(sy2 + oy)),
                )

        # Draw lone-pair dots before symbols so the halo erases any overlap.
        bonds_by_atom = self._build_bonds_by_atom(diagram)
        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)
        dot_radius = 4
        pair_gap = 8
        lone_pair_distance = font_size + 4

        for atom_idx, atom in enumerate(diagram.atoms):
            if atom.lone_pairs <= 0:
                continue
            cx_pix, cy_pix = atom_pixels[atom_idx]
            sides = self._lone_pair_sides(
                atom_idx, atom.lone_pairs, diagram, bonds_by_atom
            )
            for side in sides:
                self._draw_pair(
                    painter, cx_pix, cy_pix, side,
                    dot_radius, pair_gap, lone_pair_distance,
                )

        # Halo + symbol on top.
        halo_w = max(fm.horizontalAdvance("M"), font_size) + 6
        halo_h = fm.height() + 2
        painter.setPen(text_color)
        painter.setBrush(bg_color)
        for atom_idx, atom in enumerate(diagram.atoms):
            cx_pix, cy_pix = atom_pixels[atom_idx]
            sym = atom.symbol
            sym_w = fm.horizontalAdvance(sym)
            painter.fillRect(
                int(round(cx_pix - halo_w / 2)),
                int(round(cy_pix - halo_h / 2)),
                halo_w,
                halo_h,
                bg_color,
            )
            painter.drawText(
                int(round(cx_pix - sym_w / 2)),
                int(round(cy_pix + fm.ascent() / 2 - 2)),
                sym,
            )

        painter.end()
        return pixmap

    @staticmethod
    def _bond_line_offsets(order: int) -> list[float]:
        """Return signed offset multipliers for each parallel line of a bond."""
        if order <= 1:
            return [0.0]
        if order == 2:
            return [-0.5, 0.5]
        return [-1.0, 0.0, 1.0]

    @staticmethod
    def _build_bonds_by_atom(diagram) -> dict[int, list[int]]:
        """Map each atom index to the list of indices it is bonded to."""
        out: dict[int, list[int]] = {i: [] for i in range(len(diagram.atoms))}
        for bond in diagram.bonds:
            out[bond.atom1].append(bond.atom2)
            out[bond.atom2].append(bond.atom1)
        return out

    @staticmethod
    def _lone_pair_sides(atom_idx, lone_pair_count, diagram, bonds_by_atom):
        """Pick which sides of the atom should host the lone pairs."""
        atom = diagram.atoms[atom_idx]
        occupied: set[str] = set()
        for other_idx in bonds_by_atom[atom_idx]:
            other = diagram.atoms[other_idx]
            occupied.add(_classify_side(other.x - atom.x, other.y - atom.y))
        free = [s for s in ("top", "right", "bottom", "left") if s not in occupied]
        if len(free) >= lone_pair_count:
            return free[:lone_pair_count]
        # Fallback: cycle through all four sides if we're out of free ones.
        all_sides = ("top", "right", "bottom", "left")
        return list(all_sides[:lone_pair_count])

    @staticmethod
    def _draw_pair(painter, cx, cy, side, dot_radius, pair_gap, distance):
        """Draw a lone-pair on the chosen side of an atom centred at (cx, cy)."""
        if side == "top":
            base_x, base_y = cx, cy - distance
            d1 = (base_x - pair_gap // 2, base_y)
            d2 = (base_x + pair_gap // 2, base_y)
        elif side == "bottom":
            base_x, base_y = cx, cy + distance
            d1 = (base_x - pair_gap // 2, base_y)
            d2 = (base_x + pair_gap // 2, base_y)
        elif side == "right":
            base_x, base_y = cx + distance, cy
            d1 = (base_x, base_y - pair_gap // 2)
            d2 = (base_x, base_y + pair_gap // 2)
        else:  # left
            base_x, base_y = cx - distance, cy
            d1 = (base_x, base_y - pair_gap // 2)
            d2 = (base_x, base_y + pair_gap // 2)
        for dx, dy in (d1, d2):
            painter.drawEllipse(
                int(round(dx - dot_radius)),
                int(round(dy - dot_radius)),
                dot_radius * 2,
                dot_radius * 2,
            )

    def apply_language(self, *, title, prompt, input_placeholder=None,
                       show_button_text=None, not_in_library_text=None):
        """Update translatable texts when the UI language changes."""
        self.title_label.setText(title)
        if input_placeholder is not None:
            self.formula_input.setPlaceholderText(input_placeholder)
        if show_button_text is not None:
            self.show_molecule_button.setText(show_button_text)
        if not_in_library_text is not None:
            self._not_in_library_message = not_in_library_text
        if not self.diagram_label.pixmap() or self.diagram_label.pixmap().isNull():
            self.diagram_label.setText(prompt)
        else:
            # Refresh the rendered diagram in case any embedded text changed.
            self._redraw_last_render()
