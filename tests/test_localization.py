from rota_yz.localization import localize_category
from rota_yz.localization import localize_city_name
from rota_yz.localization import localize_country
from rota_yz.localization import localize_place_name


def test_localize_category_uses_curated_english_terms() -> None:
    assert localize_category("Muze", "en") == "Museum"
    assert localize_category("Yuruyus Rotasi", "en") == "Walking Route"
    assert localize_category("Kopru", "en") == "Bridge"


def test_localize_city_and_place_names() -> None:
    assert localize_city_name("Rome", "tr") == "Roma"
    assert localize_place_name("Ayasofya", "en") == "Hagia Sophia"
    assert localize_place_name("Brooklyn Bridge", "tr") == "Brooklyn Koprusu"
    assert localize_place_name("Gotik Mahalle", "en") == "Gothic Quarter"
    assert localize_country("Ispanya", "en") == "Spain"
