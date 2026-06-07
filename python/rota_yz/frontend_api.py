from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


class FrontendAPI:
    def __init__(self, base_url: str, session: requests.Session | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()

    def fetch_bundle(self, locale: str) -> dict[str, Any]:
        return {
            "cities": self.fetch_cities(locale),
            "places": self.fetch_places(locale),
            "source": "api",
        }

    def fetch_cities(self, locale: str) -> list[dict[str, Any]]:
        params = [
            ("locale", locale),
            ("sort[0]", "name:asc"),
            ("pagination[pageSize]", "100"),
            ("populate[hero_image][fields][0]", "url"),
        ]
        response = self.session.get(f"{self.base_url}/api/cities", params=params, timeout=30)
        response.raise_for_status()
        return [self._map_city(item) for item in response.json().get("data", [])]

    def fetch_places(self, locale: str) -> list[dict[str, Any]]:
        params = [
            ("locale", locale),
            ("sort[0]", "rating:desc"),
            ("pagination[pageSize]", "100"),
            ("populate[cover_image][fields][0]", "url"),
            ("populate[city][fields][0]", "name"),
            ("populate[city][fields][1]", "slug"),
        ]
        response = self.session.get(f"{self.base_url}/api/places", params=params, timeout=30)
        response.raise_for_status()
        return [self._map_place(item) for item in response.json().get("data", [])]

    def _map_city(self, item: dict[str, Any]) -> dict[str, Any]:
        attrs = self._get_attrs(item)
        media = self._get_relation_payload(attrs.get("hero_image"))
        return {
            "id": attrs["id"],
            "documentId": attrs["documentId"],
            "name": attrs["name"],
            "slug": attrs["slug"],
            "country": attrs["country"],
            "short_description": attrs["short_description"],
            "hero_image_url": self._extract_media_url(media),
        }

    def _map_place(self, item: dict[str, Any]) -> dict[str, Any]:
        attrs = self._get_attrs(item)
        city_attrs = self._get_attrs(self._get_relation_payload(attrs.get("city")))
        media = self._get_relation_payload(attrs.get("cover_image"))

        return {
            "id": attrs["id"],
            "documentId": attrs["documentId"],
            "name": attrs["name"],
            "slug": attrs["slug"],
            "description": attrs["description"],
            "rating": float(attrs["rating"]),
            "category": attrs["category"],
            "source_url": attrs["source_url"],
            "generated_prompt": attrs.get("generated_prompt", ""),
            "image_url": attrs.get("external_image_url") or self._extract_media_url(media),
            "city_name": city_attrs.get("name"),
            "city_slug": city_attrs.get("slug"),
        }

    def _extract_media_url(self, media: dict[str, Any] | None) -> str | None:
        if not media:
            return None

        media_attrs = self._get_attrs(media)
        url = media_attrs.get("url")
        if not url:
            return None
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self.base_url}{url}"

    def _get_attrs(self, item: dict[str, Any] | None) -> dict[str, Any]:
        if not item:
            return {}

        attrs = item.get("attributes")
        if isinstance(attrs, dict):
            return {"id": item.get("id"), "documentId": item.get("documentId"), **attrs}

        return item

    def _get_relation_payload(self, value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        if isinstance(value, dict) and "data" in value:
            return value.get("data")
        if isinstance(value, dict):
            return value
        return None


class SnapshotFrontendAPI:
    def __init__(self, snapshot_path: str | Path) -> None:
        self.snapshot_path = Path(snapshot_path)
        self.payload = json.loads(self.snapshot_path.read_text(encoding="utf-8"))

    def fetch_bundle(self, locale: str) -> dict[str, Any]:
        localized = self._get_locale_payload(locale)
        return {
            "cities": [dict(item) for item in localized.get("cities", [])],
            "places": [dict(item) for item in localized.get("places", [])],
            "source": "snapshot",
        }

    def fetch_cities(self, locale: str) -> list[dict[str, Any]]:
        return self.fetch_bundle(locale)["cities"]

    def fetch_places(self, locale: str) -> list[dict[str, Any]]:
        return self.fetch_bundle(locale)["places"]

    def _get_locale_payload(self, locale: str) -> dict[str, Any]:
        locales = self.payload.get("locales", {})
        localized = locales.get(locale)
        if localized is None:
            raise ValueError(f"Snapshot locale is missing: {locale}")
        return localized


def load_frontend_bundle(
    *,
    base_url: str,
    locale: str,
    data_mode: str,
    snapshot_path: str | Path,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    if data_mode not in {"auto", "api", "snapshot"}:
        raise ValueError(f"Unsupported data mode: {data_mode}")

    if data_mode in {"auto", "api"}:
        try:
            return FrontendAPI(base_url, session=session).fetch_bundle(locale)
        except requests.RequestException:
            if data_mode == "api":
                raise

    return SnapshotFrontendAPI(snapshot_path).fetch_bundle(locale)
