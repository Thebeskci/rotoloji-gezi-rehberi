from __future__ import annotations

import base64
import json
import mimetypes
import sqlite3
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any

from rota_yz.seed import default_seed_path
from rota_yz.seed import load_seed_dataset


def default_database_path() -> Path:
    return Path(__file__).resolve().parents[2] / "backend" / ".tmp" / "data.db"


def default_snapshot_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "live_content.json"


def load_snapshot(path: Path | str | None = None) -> dict[str, Any]:
    snapshot_path = Path(path or default_snapshot_path())
    return json.loads(snapshot_path.read_text(encoding="utf-8"))


def write_snapshot(
    *,
    database_path: Path | str | None = None,
    snapshot_path: Path | str | None = None,
) -> Path:
    target_path = Path(snapshot_path or default_snapshot_path())
    payload = build_snapshot(database_path=database_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target_path


def build_snapshot(
    *,
    database_path: Path | str | None = None,
) -> dict[str, Any]:
    db_path = Path(database_path or default_database_path())
    uploads_root = db_path.parents[1] / "public"
    seed_lookup = _build_seed_lookup()

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        locales = {
            locale: _build_locale_payload(
                connection=connection,
                locale=locale,
                seed_lookup=seed_lookup,
                uploads_root=uploads_root,
            )
            for locale in ("tr", "en")
        }

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source": "sqlite+local-media",
        "locales": locales,
    }


def _build_seed_lookup() -> dict[str, dict[str, str | None]]:
    lookup: dict[str, dict[str, str | None]] = {}
    for city in load_seed_dataset(default_seed_path()):
        for place in city.places:
            lookup[place.slug] = {
                "source_url": place.source_url,
                "wikipedia_title": place.wikipedia_title,
                "image_source_url": place.image_source_url,
            }
    return lookup


def _build_locale_payload(
    *,
    connection: sqlite3.Connection,
    locale: str,
    seed_lookup: dict[str, dict[str, str | None]],
    uploads_root: Path,
) -> dict[str, Any]:
    cities = _fetch_cities(connection, locale)
    places = _fetch_places(connection, locale)

    for place in places:
        seed_item = seed_lookup.get(place["slug"], {})
        place["image_url"] = _resolve_image_url(
            current_image_url=place.get("image_url"),
            image_source_url=seed_item.get("image_source_url"),
            uploads_root=uploads_root,
        )

    hero_by_city = {}
    for place in places:
        city_slug = place.get("city_slug")
        if city_slug and place.get("image_url") and city_slug not in hero_by_city:
            hero_by_city[city_slug] = place["image_url"]

    for city in cities:
        city["hero_image_url"] = hero_by_city.get(city["slug"])

    return {"cities": cities, "places": places}


def _fetch_cities(connection: sqlite3.Connection, locale: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            c.id,
            c.document_id,
            c.name,
            c.slug,
            c.country,
            c.short_description
        FROM cities c
        WHERE c.locale = ?
        ORDER BY c.name ASC
    """
    return [
        {
            "id": row["id"],
            "documentId": row["document_id"],
            "name": row["name"],
            "slug": row["slug"],
            "country": row["country"],
            "short_description": row["short_description"],
            "hero_image_url": None,
        }
        for row in connection.execute(query, (locale,))
    ]


def _fetch_places(connection: sqlite3.Connection, locale: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            p.id,
            p.document_id,
            p.name,
            p.slug,
            p.description,
            p.rating,
            p.category,
            p.source_url,
            p.generated_prompt,
            c.name AS city_name,
            c.slug AS city_slug,
            f.url AS image_url
        FROM places p
        LEFT JOIN places_city_lnk pcl
            ON pcl.place_id = p.id
        LEFT JOIN cities c
            ON c.id = pcl.city_id
        LEFT JOIN files_related_mph frm
            ON frm.related_id = p.id
            AND frm.related_type = 'api::place.place'
            AND frm.field = 'cover_image'
        LEFT JOIN files f
            ON f.id = frm.file_id
        WHERE p.locale = ?
        ORDER BY p.rating DESC, p.name ASC
    """
    return [
        {
            "id": row["id"],
            "documentId": row["document_id"],
            "name": row["name"],
            "slug": row["slug"],
            "description": row["description"],
            "rating": float(row["rating"]),
            "category": row["category"],
            "source_url": row["source_url"],
            "generated_prompt": row["generated_prompt"] or "",
            "image_url": row["image_url"],
            "city_name": row["city_name"],
            "city_slug": row["city_slug"],
        }
        for row in connection.execute(query, (locale,))
    ]


def _resolve_image_url(
    *,
    current_image_url: str | None,
    image_source_url: str | None,
    uploads_root: Path,
) -> str | None:
    if current_image_url and current_image_url.startswith(("http://", "https://")):
        return current_image_url

    if image_source_url:
        return image_source_url

    if current_image_url and current_image_url.startswith("/"):
        local_file = uploads_root / current_image_url.lstrip("/")
        inlined = _inline_local_image(local_file)
        if inlined:
            return inlined

    return current_image_url


def _inline_local_image(path: Path) -> str | None:
    if not path.exists():
        return None

    mime_type, _ = mimetypes.guess_type(path.name)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type or 'application/octet-stream'};base64,{encoded}"


def main() -> None:
    snapshot_path = write_snapshot()
    print(f"Snapshot written to {snapshot_path}")


if __name__ == "__main__":
    main()
