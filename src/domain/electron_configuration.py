import re

from src.config.static_data import CORE_CONFIGS

TOKEN_PATTERN = re.compile(r"\[[A-Za-z]{1,2}\]|\d[spdf]\d+")
CONFIG_PATTERN = re.compile(r"(\d)([spdf])(\d+)")


def expand_configuration(config_text):
    """Expand a shorthand electron configuration into individual tokens.

    Replaces noble-gas core abbreviations (e.g. [Ar]) with their full
    subshell list taken from CORE_CONFIGS, so that every orbital token
    is explicit and ready for further parsing.
    """
    if not config_text:
        return []

    tokens = TOKEN_PATTERN.findall(config_text)

    expanded = []
    for token in tokens:
        if token in CORE_CONFIGS:
            expanded.extend(CORE_CONFIGS[token])
        else:
            expanded.append(token)

    return expanded


def configuration_to_map(config_text):
    """Convert an electron configuration string into an occupancy map.

    Parses each subshell token (e.g. '2p6') and builds a dictionary
    mapping orbital labels like '2p' to their electron count.
    """
    expanded_tokens = expand_configuration(config_text)
    occupancy_map = {}

    for token in expanded_tokens:
        match = CONFIG_PATTERN.fullmatch(token)
        if match:
            level = match.group(1)
            subshell = match.group(2)
            electrons = int(match.group(3))
            occupancy_map[f"{level}{subshell}"] = electrons

    return occupancy_map


def fill_boxes(electrons, box_count):
    """Distribute electrons across orbital boxes following Hund's rule.

    First pass: places one electron in each box (spin-up), filling
    left to right. Second pass: adds remaining electrons as spin-down
    partners. This reproduces the maximum-multiplicity principle for
    p, d, and f subshells.
    """
    boxes = [0] * box_count
    remaining = electrons

    for i in range(box_count):
        if remaining > 0:
            boxes[i] += 1
            remaining -= 1

    for i in range(box_count):
        if remaining > 0:
            boxes[i] += 1
            remaining -= 1

    return boxes
