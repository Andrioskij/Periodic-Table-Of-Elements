SCIENTIFIC_NOTE_FIELDS = (
    ("electronegativity", "electronegativity"),
    ("ionization_energy", "ionization_energy"),
    ("electron_affinity", "electron_affinity"),
    ("oxidation_states", "oxidation_states"),
    ("atomic_radius", "atomic_radius"),
    ("density", "density"),
    ("melting_point", "melting_point"),
    ("boiling_point", "boiling_point"),
    ("standard_state", "standard_state"),
)


def get_missing_scientific_field_keys(element):
    """Identify which scientific properties are absent for an element.

    Returns a list of translation keys corresponding to fields that
    are None or blank, so the UI can inform the user about missing data.
    """
    missing_fields = []

    for field_name, translation_key in SCIENTIFIC_NOTE_FIELDS:
        value = element.get(field_name)
        if value is None:
            missing_fields.append(translation_key)
            continue

        if isinstance(value, str) and not value.strip():
            missing_fields.append(translation_key)

    return missing_fields


def build_scientific_data_note(element, *, translate, field_limit=3):
    """Build a localized note listing the element's missing scientific data.

    Shows up to field_limit field names explicitly, then appends a
    '+N more' suffix if additional fields are also missing. Returns
    an empty string when no data is missing.
    """
    missing_field_keys = get_missing_scientific_field_keys(element)
    if not missing_field_keys:
        return ""

    visible_labels = [translate(field_key) for field_key in missing_field_keys[:field_limit]]
    visible_fields = ", ".join(visible_labels)
    remaining_count = len(missing_field_keys) - len(visible_labels)

    if remaining_count > 0:
        return translate(
            "scientific_data_partial_note_more",
            fields=visible_fields,
            count=remaining_count,
        )

    return translate("scientific_data_partial_note", fields=visible_fields)
