from __future__ import annotations

import base64
import json
import mimetypes
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests


ROOT_DIR = Path(__file__).resolve().parents[2]
PAGES_SOURCE_DIR = ROOT_DIR / "pages"
DEFAULT_SNAPSHOT_PATH = ROOT_DIR / "data" / "live_content.json"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "dist-pages"

CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}


def infer_extension(content_type: str | None, url: str | None = None) -> str:
    normalized = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized in CONTENT_TYPES:
        return CONTENT_TYPES[normalized]

    if url:
        suffix = Path(urlparse(url).path).suffix.lower()
        if suffix:
            return suffix

    guessed = mimetypes.guess_extension(normalized) if normalized else None
    return guessed or ".bin"


def export_asset(raw_value: str | None, slug: str, folder: Path, session: requests.Session) -> str | None:
    if not raw_value:
        return None

    folder.mkdir(parents=True, exist_ok=True)

    if raw_value.startswith("data:"):
        header, encoded = raw_value.split(",", 1)
        mime_type = header.split(";", 1)[0].removeprefix("data:")
        extension = infer_extension(mime_type)
        target = folder / f"{slug}{extension}"
        target.write_bytes(base64.b64decode(encoded))
        return target.relative_to(folder.parents[1]).as_posix()

    if raw_value.startswith("http://") or raw_value.startswith("https://"):
        try:
            response = session.get(raw_value, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            return None

        content_type = response.headers.get("content-type", "")
        if not content_type.lower().startswith("image/"):
            return None

        extension = infer_extension(content_type, raw_value)
        target = folder / f"{slug}{extension}"
        target.write_bytes(response.content)
        return target.relative_to(folder.parents[1]).as_posix()

    return raw_value


def first_media_map(payload: dict, collection: str, field: str) -> dict[str, str | None]:
    media: dict[str, str | None] = {}
    for localized in payload["locales"].values():
        for item in localized[collection]:
            slug = item["slug"]
            if slug not in media or not media[slug]:
                media[slug] = item.get(field)
    return media


def normalize_locale_bundle(payload: dict, locale: str, city_assets: dict[str, str | None], place_assets: dict[str, str | None]) -> dict:
    localized = payload["locales"][locale]

    cities = [
        {
            "name": city["name"],
            "slug": city["slug"],
            "country": city["country"],
            "short_description": city["short_description"],
            "hero_image_url": city_assets.get(city["slug"]),
        }
        for city in localized["cities"]
    ]

    places = [
        {
            "name": place["name"],
            "slug": place["slug"],
            "description": place["description"],
            "rating": place["rating"],
            "category": place["category"],
            "source_url": place["source_url"],
            "generated_prompt": place.get("generated_prompt", ""),
            "city_name": place["city_name"],
            "city_slug": place["city_slug"],
            "image_url": place_assets.get(place["slug"]),
        }
        for place in localized["places"]
    ]

    return {
        "generated_at": payload["generated_at"],
        "source": payload["source"],
        "locale": locale,
        "cities": cities,
        "places": places,
    }


def build_pages_site(
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
    pages_source_dir: Path = PAGES_SOURCE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))

    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.copytree(pages_source_dir, output_dir)

    data_dir = output_dir / "data"
    city_asset_dir = output_dir / "assets" / "cities"
    place_asset_dir = output_dir / "assets" / "places"
    data_dir.mkdir(parents=True, exist_ok=True)

    city_media = first_media_map(payload, "cities", "hero_image_url")
    place_media = first_media_map(payload, "places", "image_url")

    city_assets: dict[str, str | None] = {}
    place_assets: dict[str, str | None] = {}

    with requests.Session() as session:
        for slug, raw_value in city_media.items():
            city_assets[slug] = export_asset(raw_value, slug, city_asset_dir, session)
        for slug, raw_value in place_media.items():
            place_assets[slug] = export_asset(raw_value, slug, place_asset_dir, session)

    manifest = {
        "generated_at": payload["generated_at"],
        "source": payload["source"],
        "locales": sorted(payload["locales"].keys()),
    }
    (data_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    for locale in sorted(payload["locales"].keys()):
        bundle = normalize_locale_bundle(payload, locale, city_assets, place_assets)
        (data_dir / f"{locale}.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

    index_html = output_dir / "index.html"
    (output_dir / "404.html").write_text(index_html.read_text(encoding="utf-8"), encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    return output_dir


def main() -> None:
    output_dir = build_pages_site()
    print(output_dir)


if __name__ == "__main__":
    main()
