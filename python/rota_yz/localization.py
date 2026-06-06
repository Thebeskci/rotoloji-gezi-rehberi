from __future__ import annotations


CATEGORY_EN = {
    "Tarih": "History",
    "Saray": "Palace",
    "Manzara": "View",
    "Alisveris": "Shopping",
    "Meydan": "Square",
    "Muze": "Museum",
    "Mahalle": "Neighbourhood",
    "Nehir": "River",
    "Cesme": "Fountain",
    "Arkeoloji": "Archaeology",
    "Tapinak": "Temple",
    "Mimari": "Architecture",
    "Bulvar": "Boulevard",
    "Sehir Hayati": "City Life",
    "Park": "Park",
    "Kopru": "Bridge",
    "Yuruyus Rotasi": "Walking Route",
}

COUNTRY_EN = {
    "Turkiye": "Turkey",
    "Fransa": "France",
    "Italya": "Italy",
    "Ispanya": "Spain",
    "Japonya": "Japan",
    "Amerika Birlesik Devletleri": "United States",
}

CITY_NAME_TR = {
    "Istanbul": "Istanbul",
    "Paris": "Paris",
    "Rome": "Roma",
    "Barcelona": "Barselona",
    "Tokyo": "Tokyo",
    "New York": "New York",
}

CITY_NAME_EN = {
    "Istanbul": "Istanbul",
    "Paris": "Paris",
    "Rome": "Rome",
    "Barcelona": "Barcelona",
    "Tokyo": "Tokyo",
    "New York": "New York",
    "Roma": "Rome",
    "Barselona": "Barcelona",
}

PLACE_NAME_EN = {
    "Ayasofya": "Hagia Sophia",
    "Topkapi Sarayi": "Topkapi Palace",
    "Galata Kulesi": "Galata Tower",
    "Kapalicarsi": "Grand Bazaar",
    "Sultanahmet Meydani": "Sultanahmet Square",
    "Eyfel Kulesi": "Eiffel Tower",
    "Louvre Muzesi": "Louvre Museum",
    "Notre-Dame Katedrali": "Notre-Dame Cathedral",
    "Seine Nehri": "Seine River",
    "Kolezyum": "Colosseum",
    "Trevi Cesmesi": "Trevi Fountain",
    "Roma Forumu": "Roman Forum",
    "Vatikan Muzeleri": "Vatican Museums",
    "Gotik Mahalle": "Gothic Quarter",
}

PLACE_NAME_TR = {
    "Brooklyn Bridge": "Brooklyn Koprusu",
    "Metropolitan Museum of Art": "Metropolitan Sanat Muzesi",
}


def _pick(value: str, locale: str, tr_map: dict[str, str] | None, en_map: dict[str, str] | None) -> str:
    if locale == "tr":
        return (tr_map or {}).get(value, value)
    if locale == "en":
        return (en_map or {}).get(value, value)
    return value


def localize_category(value: str, locale: str) -> str:
    return _pick(value, locale, None, CATEGORY_EN)


def localize_country(value: str, locale: str) -> str:
    return _pick(value, locale, None, COUNTRY_EN)


def localize_city_name(value: str, locale: str) -> str:
    return _pick(value, locale, CITY_NAME_TR, CITY_NAME_EN)


def localize_place_name(value: str, locale: str) -> str:
    return _pick(value, locale, PLACE_NAME_TR, PLACE_NAME_EN)
