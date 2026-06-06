from __future__ import annotations

import argparse
import time
from pathlib import Path

from rota_yz.config import Settings
from rota_yz.images import ImageGenerator
from rota_yz.localization import localize_category
from rota_yz.localization import localize_city_name
from rota_yz.localization import localize_country
from rota_yz.localization import localize_place_name
from rota_yz.seed import load_seed_dataset
from rota_yz.strapi_client import StrapiClient
from rota_yz.text_utils import build_place_prompt, normalize_text
from rota_yz.translator import TranslationService
from rota_yz.wikimedia import WikimediaClient


def _get_attrs(item: dict | None) -> dict:
    if not item:
        return {}

    attrs = item.get("attributes")
    if isinstance(attrs, dict):
        return {"id": item.get("id"), "documentId": item.get("documentId"), **attrs}

    return item


def _get_relation_payload(value: object) -> dict | None:
    if value is None:
        return None
    if isinstance(value, dict) and "data" in value:
        return value.get("data")
    if isinstance(value, dict):
        return value
    return None


def _is_usable_existing_image(document: dict | None) -> bool:
    attrs = _get_attrs(document)
    media = _get_relation_payload(attrs.get("cover_image"))
    media_attrs = _get_attrs(media)
    mime = media_attrs.get("mime")
    size = float(media_attrs.get("size") or 0)
    return bool(media_attrs.get("id")) and (mime == "image/jpeg" or size >= 20)


def _existing_image_id(document: dict | None) -> int | None:
    attrs = _get_attrs(document)
    media = _get_relation_payload(attrs.get("cover_image"))
    media_attrs = _get_attrs(media)
    media_id = media_attrs.get("id")
    return int(media_id) if media_id is not None else None


def _safe_fetch_summary(
    wikimedia: WikimediaClient, title: str | None, locale: str
) -> dict | None:
    if not title:
        return None

    try:
        return wikimedia.fetch_summary(title, locale=locale)
    except Exception:
        return None


def ingest(seed_path: Path | None = None, city_limit: int | None = None) -> None:
    settings = Settings.from_env(require_auth=True)
    cities = load_seed_dataset(seed_path)

    if city_limit is not None:
        cities = cities[:city_limit]

    translator = TranslationService()
    wikimedia = WikimediaClient(settings.wikimedia_user_agent)
    image_generator = ImageGenerator(
        api_key=settings.pollinations_api_key,
        user_agent=settings.wikimedia_user_agent,
    )
    strapi = StrapiClient(
        settings.strapi_url,
        email=settings.strapi_email,
        password=settings.strapi_password,
    )

    created_places = 0

    for city in cities:
        city_description_tr = normalize_text(city.short_description)
        city_description_en = translator.translate_to_english(city_description_tr)
        city_name_tr = localize_city_name(city.name, "tr")
        city_name_en = localize_city_name(city.name, "en")
        country_tr = localize_country(city.country, "tr")
        country_en = localize_country(city.country, "en")
        city_document_id = strapi.upsert_city(
            {
                "name": city_name_tr,
                "slug": city.slug,
                "country": country_tr,
                "short_description": city_description_tr,
            },
            {
                "name": city_name_en,
                "slug": city.slug,
                "country": country_en,
                "short_description": city_description_en,
            },
        )

        for place in city.places:
            tr_summary = _safe_fetch_summary(wikimedia, place.wikipedia_title, "tr")
            en_summary = _safe_fetch_summary(wikimedia, place.wikipedia_title, "en")
            existing_place = strapi.find_document(
                "places",
                slug=place.slug,
                locale="tr",
                populate=["cover_image"],
            )
            if tr_summary:
                description_tr = normalize_text(tr_summary.extract)
            elif en_summary:
                description_tr = translator.translate_to_turkish(en_summary.extract)
            else:
                description_tr = normalize_text(place.seed_description)

            if en_summary:
                description_en = normalize_text(en_summary.extract)
            elif tr_summary:
                description_en = translator.translate_to_english(tr_summary.extract)
            else:
                description_en = translator.translate_to_english(description_tr)

            place_name_tr = localize_place_name(place.name, "tr")
            place_name_en = localize_place_name(place.name, "en")
            category_tr = localize_category(place.category, "tr")
            category_en = localize_category(place.category, "en")
            prompt = build_place_prompt(city_name_en, place_name_en, category_en, country_en)
            provider = "existing"
            existing_image_id = _existing_image_id(existing_place)
            image_source_url = place.image_source_url or (
                tr_summary.page_url
                if tr_summary and tr_summary.page_url
                else en_summary.page_url
                if en_summary and en_summary.page_url
                else place.source_url
            )
            fallback_url = (
                tr_summary.thumbnail_url
                if tr_summary and tr_summary.thumbnail_url
                else en_summary.thumbnail_url
                if en_summary and en_summary.thumbnail_url
                else wikimedia.fetch_best_image_url(
                    place.wikipedia_title,
                    source_url=image_source_url,
                )
            )

            if _is_usable_existing_image(existing_place) and existing_image_id is not None:
                image_id = existing_image_id
            else:
                image = image_generator.generate(
                    prompt,
                    fallback_url=fallback_url,
                )
                uploaded_image = strapi.upload_image(image)
                image_id = uploaded_image["id"]
                provider = image.provider

            relation = {"documentId": city_document_id}
            tr_payload = {
                "name": place_name_tr,
                "slug": place.slug,
                "description": description_tr,
                "rating": place.rating,
                "category": category_tr,
                "source_url": tr_summary.page_url if tr_summary and tr_summary.page_url else place.source_url,
                "generated_prompt": prompt,
                "cover_image": image_id,
                "city": relation,
            }
            en_payload = {
                "name": place_name_en,
                "slug": place.slug,
                "description": description_en,
                "rating": place.rating,
                "category": category_en,
                "source_url": en_summary.page_url if en_summary and en_summary.page_url else place.source_url,
                "generated_prompt": prompt,
                "cover_image": image_id,
                "city": relation,
            }

            strapi.upsert_place(tr_payload, en_payload)
            created_places += 1
            print(f"[OK] {city.name} / {place.name} -> using {provider}")
            if provider != "existing":
                time.sleep(1)

    print(f"Completed ingest for {len(cities)} cities and {created_places} places.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RotaYZ Strapi ingest runner")
    parser.add_argument("--seed", type=Path, default=None, help="Optional seed JSON path")
    parser.add_argument("--city-limit", type=int, default=None, help="Limit the number of cities")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ingest(seed_path=args.seed, city_limit=args.city_limit)


if __name__ == "__main__":
    main()
