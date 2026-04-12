from difflib import SequenceMatcher


def compute_match_score(element, query, localized_name=None):
    """Score how well an element matches a search query (0-100).

    Checks exact matches on symbol, atomic number, and name first
    (highest scores), then prefix and substring matches, and finally
    falls back to fuzzy SequenceMatcher similarity for typo tolerance.
    """
    query = query.strip().lower()
    if not query:
        return 0

    name = str(element.get("name", "")).lower()
    localized_name = str(localized_name if localized_name is not None else element.get("name", "")).lower()
    symbol = str(element.get("symbol", "")).lower()
    atomic_number = str(element.get("atomic_number", ""))

    if query == symbol:
        return 100
    if query == atomic_number:
        return 98
    if query == name:
        return 96
    if query == localized_name:
        return 95
    if name.startswith(query):
        return 90
    if localized_name.startswith(query):
        return 89
    if symbol.startswith(query):
        return 88
    if atomic_number.startswith(query):
        return 86
    if query in name:
        return 78
    if query in localized_name:
        return 77
    if query in symbol:
        return 74

    fuzzy_name = SequenceMatcher(None, query, name).ratio()
    fuzzy_localized_name = SequenceMatcher(None, query, localized_name).ratio()
    fuzzy_symbol = SequenceMatcher(None, query, symbol).ratio()
    fuzzy_best = max(fuzzy_name, fuzzy_localized_name, fuzzy_symbol)
    return int(fuzzy_best * 60) if fuzzy_best >= 0.55 else 0


def get_ranked_matches(elements, query, *, localized_name_getter=None, limit=6):
    """Return the top-scoring elements for a search query.

    Scores every element against the query, filters out non-matches,
    and returns up to 'limit' results sorted by descending score
    (ties broken by ascending atomic number).
    """
    ranked = []
    for element in elements:
        localized_name = (
            localized_name_getter(element)
            if localized_name_getter is not None
            else element.get("name", "")
        )
        score = compute_match_score(element, query, localized_name=localized_name)
        if score > 0:
            ranked.append((score, element))

    ranked.sort(key=lambda item: (-item[0], item[1]["atomic_number"]))
    return [element for score, element in ranked[:limit]]
