from __future__ import annotations

import json
from pathlib import Path

from rota_yz.models import CitySeed, PlaceSeed
from rota_yz.text_utils import slugify


def default_seed_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "seed_places.json"


def load_seed_dataset(path: Path | None = None) -> list[CitySeed]:
    dataset_path = path or default_seed_path()
    raw = json.loads(dataset_path.read_text(encoding="utf-8"))
    cities: list[CitySeed] = []

    for city_item in raw.get("cities", []):
        city_slug = city_item.get("slug") or slugify(city_item["name"])
        places: list[PlaceSeed] = []

        for place_item in city_item.get("places", []):
            place_slug = place_item.get("slug") or slugify(f"{city_slug}-{place_item['name']}")
            places.append(
                PlaceSeed(
                    name=place_item["name"],
                    category=place_item["category"],
                    rating=float(place_item["rating"]),
                    seed_description=place_item["seed_description"],
                    source_url=place_item["source_url"],
                    wikipedia_title=place_item.get("wikipedia_title"),
                    image_source_url=place_item.get("image_source_url"),
                    slug=place_slug,
                )
            )

        cities.append(
            CitySeed(
                name=city_item["name"],
                country=city_item["country"],
                short_description=city_item["short_description"],
                slug=city_slug,
                places=places,
            )
        )

    validate_seed_dataset(cities)
    return cities


def validate_seed_dataset(cities: list[CitySeed]) -> None:
    if not cities:
        raise ValueError("Seed dataset is empty.")

    city_slugs: set[str] = set()

    for city in cities:
        if city.slug in city_slugs:
            raise ValueError(f"Duplicate city slug: {city.slug}")

        city_slugs.add(city.slug)

        if len(city.places) < 5:
            raise ValueError(f"City {city.name} must have at least 5 places.")

        place_slugs: set[str] = set()
        for place in city.places:
            if not 0 <= place.rating <= 5:
                raise ValueError(f"Invalid rating for {place.name}: {place.rating}")
            if place.slug in place_slugs:
                raise ValueError(f"Duplicate place slug in {city.name}: {place.slug}")
            place_slugs.add(place.slug)
