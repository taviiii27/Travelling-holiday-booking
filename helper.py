def filter_destinations(destinations, preferences):
    """
    Filters a list of destination dicts based on comma-separated preference keywords.

    Args:
        destinations (list): List of dicts, each representing a destination with a "features" field.
        preferences (str): Comma-separated string of keywords to match in destination features.

    Returns:
        list: Filtered list of destinations matching any of the preferences.
    """
    if not preferences:
        return destinations

    prefs = [pref.strip().lower() for pref in preferences.split(",") if pref.strip()]
    if not prefs:
        return destinations

    filtered = []
    for dest in destinations:
        features = dest.get("features", "").lower()
        if any(pref in features for pref in prefs):
            filtered.append(dest)
    return filtered
