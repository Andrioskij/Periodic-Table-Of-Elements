RIGHT_PANEL_STACK_INDEX = {
    "info": 0,
    "diagram": 1,
    "compound": 2,
    "molar": 3,
    "stoichiometry": 4,
}


def build_info_panel_prompt(*, has_selected_element, translate):
    """Return the info-panel placeholder text, or None when an element is selected.

    Shows a translated prompt asking the user to click an element
    when nothing is selected yet.
    """
    if has_selected_element:
        return None
    return translate("info_prompt")


def build_diagram_panel_state(*, is_diagram_mode, has_selected_element, translate):
    """Decide what the orbital-diagram panel should display.

    Returns a dict with an 'action' key ('show_diagram' or 'set_prompt')
    plus the corresponding title and text, depending on whether the
    diagram tab is active and an element is selected.
    """
    title = translate("diagram_title")

    if is_diagram_mode:
        if has_selected_element:
            return {
                "action": "show_diagram",
                "title": title,
                "text": None,
            }
        return {
            "action": "set_prompt",
            "title": title,
            "text": translate("diagram_prompt"),
        }

    prompt_key = "diagram_prompt" if not has_selected_element else "diagram_switch_prompt"
    return {
        "action": "set_prompt",
        "title": title,
        "text": translate(prompt_key),
    }


def build_compound_panel_state(
    *,
    has_compound_pair,
    rebuild,
    translate,
    preview_text=None,
    rebuilt_result_text=None,
):
    """Decide what the compound-builder panel should display.

    Returns either a prompt (when no pair is ready), the rebuilt
    formula result (on recalculation), or a preview with existing
    pair information.
    """
    if rebuild:
        return {
            "action": "set_result_text",
            "text": rebuilt_result_text or "",
        }

    if not has_compound_pair:
        return {
            "action": "set_prompt",
            "text": translate("compound_prompt"),
        }

    return {
        "action": "set_result_text",
        "text": translate("pair_ready_prompt") + "\n\n" + (preview_text or ""),
    }


def build_right_panel_mode_state(*, mode, has_selected_element):
    """Compute the UI state needed to switch the right-panel tab.

    Returns the stack index to show, which toggle buttons should be
    checked, and which panel modes need a content refresh.
    """
    refresh_modes = ()
    if not has_selected_element:
        refresh_modes = (mode,)
    elif mode == "diagram":
        refresh_modes = ("diagram",)

    return {
        "stack_index": RIGHT_PANEL_STACK_INDEX[mode],
        "checked_modes": {
            panel_mode: panel_mode == mode
            for panel_mode in RIGHT_PANEL_STACK_INDEX
        },
        "refresh_modes": refresh_modes,
    }
