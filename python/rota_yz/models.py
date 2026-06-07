from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceSeed:
    name: str
    category: str
    rating: float
    seed_description: str
    source_url: str
    wikipedia_title: str | None
    image_source_url: str | None
    slug: str


@dataclass(frozen=True)
class CitySeed:
    name: str
    country: str
    short_description: str
    travel_guide_url: str | None
    slug: str
    places: list[PlaceSeed]


@dataclass(frozen=True)
class WikimediaSummary:
    title: str
    extract: str
    page_url: str | None = None
    thumbnail_url: str | None = None


@dataclass(frozen=True)
class ImageAsset:
    filename: str
    content: bytes
    content_type: str
    provider: str
    prompt: str
