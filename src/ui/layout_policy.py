from dataclasses import dataclass


UNBOUNDED_MAX_WIDTH = 16777215
MIN_WINDOW_WIDTH = 560
WIDE_BREAKPOINT = 1500
MEDIUM_BREAKPOINT = 1100
NARROW_BREAKPOINT = 800
HORIZONTAL = "horizontal"
VERTICAL = "vertical"


@dataclass(frozen=True)
class ResponsiveLayoutPolicy:
    mode: str
    top_controls_direction: str
    content_direction: str
    builder_max_width: int
    right_column_max_width: int
    search_max_width: int
    cell_size: int
    header_height: int
    side_width: int
    grid_h_spacing: int
    grid_v_spacing: int
    element_font_size: int


def resolve_responsive_mode(window_width):
    """Determine the responsive layout tier for the given window width.

    Returns one of 'wide', 'medium', 'narrow', or 'compact', used
    to select panel arrangement and sizing parameters.
    """
    width = max(MIN_WINDOW_WIDTH, window_width)

    if width >= WIDE_BREAKPOINT:
        return "wide"
    if width >= MEDIUM_BREAKPOINT:
        return "medium"
    if width >= NARROW_BREAKPOINT:
        return "narrow"
    return "compact"


def compute_responsive_layout(window_width):
    """Build a complete ResponsiveLayoutPolicy for the current window width.

    Calculates cell size, spacing, font size, column widths and layout
    directions so the periodic table adapts smoothly from compact
    phone-like sizes up to wide desktop monitors.
    """
    width = max(MIN_WINDOW_WIDTH, window_width)
    mode = resolve_responsive_mode(width)

    if mode == "wide":
        top_controls_direction = HORIZONTAL
        content_direction = HORIZONTAL
        builder_max_width = 760
        right_column_max_width = 390
        search_max_width = 540
        table_available_width = max(900, width - 450)
        max_cell = 58
    elif mode == "medium":
        top_controls_direction = HORIZONTAL
        content_direction = HORIZONTAL
        builder_max_width = 660
        right_column_max_width = 340
        search_max_width = 470
        table_available_width = max(760, width - 390)
        max_cell = 50
    elif mode == "narrow":
        top_controls_direction = VERTICAL
        content_direction = VERTICAL
        builder_max_width = UNBOUNDED_MAX_WIDTH
        right_column_max_width = UNBOUNDED_MAX_WIDTH
        search_max_width = UNBOUNDED_MAX_WIDTH
        table_available_width = max(680, width - 40)
        max_cell = 46
    else:
        top_controls_direction = VERTICAL
        content_direction = VERTICAL
        builder_max_width = UNBOUNDED_MAX_WIDTH
        right_column_max_width = UNBOUNDED_MAX_WIDTH
        search_max_width = UNBOUNDED_MAX_WIDTH
        table_available_width = max(520, width - 30)
        max_cell = 36

    cell_size = int(max(22, min(max_cell, table_available_width / 20.4)))

    return ResponsiveLayoutPolicy(
        mode=mode,
        top_controls_direction=top_controls_direction,
        content_direction=content_direction,
        builder_max_width=builder_max_width,
        right_column_max_width=right_column_max_width,
        search_max_width=search_max_width,
        cell_size=cell_size,
        header_height=max(18, int(cell_size * 0.48)),
        side_width=max(24, int(cell_size * 0.85)),
        grid_h_spacing=max(2, int(cell_size * 0.08)),
        grid_v_spacing=max(2, int(cell_size * 0.08)),
        element_font_size=max(8, int(cell_size * 0.24)),
    )
