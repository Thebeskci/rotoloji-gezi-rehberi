from rota_yz.seed import load_seed_dataset


def test_seed_dataset_loads_expected_scope() -> None:
    cities = load_seed_dataset()
    assert len(cities) == 6
    assert all(len(city.places) >= 5 for city in cities)
    assert sum(len(city.places) for city in cities) == 30
