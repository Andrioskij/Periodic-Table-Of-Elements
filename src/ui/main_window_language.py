RIGHT_PANEL_TEXT_KEYS = {
    "info": "right_info",
    "diagram": "right_diagram",
    "compound": "right_compound",
    "molar": "right_molar",
    "stoichiometry": "right_stoichiometry",
}

RIGHT_PANEL_SHORTCUTS = {
    "info": "Ctrl+1",
    "diagram": "Ctrl+2",
    "compound": "Ctrl+3",
    "molar": "Ctrl+4",
    "stoichiometry": "Ctrl+5",
}


def build_main_window_texts(translate, trend_button_specs):
    """Collect every translatable UI string needed by the main window.

    Builds a flat dictionary of label texts keyed by widget role,
    plus nested dicts for trend buttons and right-panel buttons,
    so the window can apply all translations in one pass.
    """
    return {
        "title": translate("title"),
        "about_button": translate("about_button"),
        "search_title": translate("search_title"),
        "search_helper": translate("search_helper"),
        "search_placeholder": translate("search_placeholder"),
        "search_button": translate("search_button"),
        "builder_title": translate("builder_title"),
        "builder_scope_note": translate("builder_scope_note"),
        "builder_selection_title": translate("builder_selection_title"),
        "builder_selection_hint": translate("builder_selection_hint"),
        "builder_use_selected_a": translate("builder_use_selected_a"),
        "builder_use_selected_b": translate("builder_use_selected_b"),
        "builder_slot_a_title": translate("builder_slot_a_title"),
        "builder_slot_b_title": translate("builder_slot_b_title"),
        "oxidation_first": translate("oxidation_first"),
        "oxidation_second": translate("oxidation_second"),
        "calculate_formula": translate("calculate_formula"),
        "reset": translate("reset"),
        "formula_title": translate("formula_title"),
        "compound_scope_note": translate("compound_scope_note"),
        "selected_none": translate("selected_none"),
        "transition_metals": translate("transition_metals"),
        "metallic_arrow": translate("metallic_arrow"),
        "nonmetallic_arrow": translate("nonmetallic_arrow"),
        "trend_buttons": {
            mode: translate(label_key)
            for mode, label_key in trend_button_specs
        },
        "right_panel_buttons": {
            mode: translate(label_key)
            for mode, label_key in RIGHT_PANEL_TEXT_KEYS.items()
        },
    }


def build_accessibility_specs(
    *,
    about_text,
    search_placeholder,
    search_button_text,
    build_button_text,
    reset_button_text,
    trend_button_texts,
    right_panel_button_texts,
):
    """Build accessibility metadata (name, description, tooltip) for all interactive widgets.

    Returns a nested dictionary keyed by widget role, consumed by
    the main window to set screen-reader attributes and tooltips
    on buttons and inputs.
    """
    return {
        "about_button": {
            "name": about_text,
            "description": about_text,
            "tooltip": about_text,
        },
        "search_input": {
            "name": search_placeholder,
            "description": f"{search_placeholder} (Ctrl+F)",
            "tooltip": f"{search_placeholder} (Ctrl+F)",
        },
        "search_button": {
            "name": search_button_text,
            "description": f"{search_button_text} (Enter)",
            "tooltip": f"{search_button_text} (Enter)",
        },
        "build_button": {
            "name": build_button_text,
            "description": build_button_text,
            "tooltip": build_button_text,
        },
        "builder_reset_button": {
            "name": reset_button_text,
            "description": f"{reset_button_text} (Ctrl+L)",
            "tooltip": f"{reset_button_text} (Ctrl+L)",
        },
        "trend_buttons": {
            mode: {
                "name": text,
                "description": f"Activates the {text} view.",
                "tooltip": text,
            }
            for mode, text in trend_button_texts.items()
        },
        "right_panel_buttons": {
            mode: {
                "name": text,
                "description": (
                    f"Switches to {text}. Shortcut {RIGHT_PANEL_SHORTCUTS[mode]}."
                ),
                "tooltip": f"{text} ({RIGHT_PANEL_SHORTCUTS[mode]})",
            }
            for mode, text in right_panel_button_texts.items()
        },
    }
