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
from rota_yz.text_enrichment import AITextEnricher
from rota_yz.text_utils import build_placeholder_url, build_place_prompt, normalize_text
from rota_yz.travel_guides import TravelGuideClient
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


def _existing_external_image_url(document: dict | None) -> str | None:
    attrs = _get_attrs(document)
    image_url = attrs.get("external_image_url")
    if not isinstance(image_url, str):
        return None
    image_url = image_url.strip()
    return image_url or None


def _select_image_fields(
    *,
    media_mode: str,
    existing_place: dict | None,
    fallback_url: str | None,
    prompt: str,
    image_generator: ImageGenerator,
    strapi: StrapiClient,
) -> tuple[dict[str, object], str, bool]:
    if media_mode == "external":
        return (
            {
                "cover_image": None,
                "external_image_url": (
                    _existing_external_image_url(existing_place)
                    or fallback_url
                    or build_placeholder_url(prompt)
                ),
            },
            "external-url",
            False,
        )

    existing_image_id = _existing_image_id(existing_place)
    if _is_usable_existing_image(existing_place) and existing_image_id is not None:
        return (
            {
                "cover_image": existing_image_id,
                "external_image_url": None,
            },
            "existing",
            False,
        )

    image = image_generator.generate(
        prompt,
        fallback_url=fallback_url,
    )
    uploaded_image = strapi.upload_image(image)
    return (
        {
            "cover_image": uploaded_image["id"],
            "external_image_url": None,
        },
        image.provider,
        True,
    )


def _safe_fetch_summary(
    wikimedia: WikimediaClient, title: str | None, locale: str
) -> dict | None:
    if not title:
        return None

    try:
        return wikimedia.fetch_summary(title, locale=locale)
    except Exception:
        return None


def _safe_fetch_city_intro(travel_guides: TravelGuideClient, url: str | None) -> str | None:
    if not url:
        return None

    try:
        return travel_guides.fetch_city_intro(url)
    except Exception:
        return None


def _safe_fetch_place_excerpt(
    travel_guides: TravelGuideClient,
    url: str | None,
    search_terms: list[str],
) -> str | None:
    if not url:
        return None

    try:
        return travel_guides.find_place_excerpt(url, search_terms)
    except Exception:
        return None


def _place_search_terms(place_name_tr: str, place_name_en: str, wikipedia_title: str | None) -> list[str]:
    terms = [place_name_en, place_name_tr]
    if wikipedia_title:
        terms.append(wikipedia_title)
        if "," in wikipedia_title:
            terms.append(wikipedia_title.split(",", 1)[0])

    unique_terms = []
    for term in terms:
        if term and term not in unique_terms:
            unique_terms.append(term)
    return unique_terms


def ingest(seed_path: Path | None = None, city_limit: int | None = None) -> None:
    settings = Settings.from_env(require_auth=True)
    cities = load_seed_dataset(seed_path)

    if city_limit is not None:
        cities = cities[:city_limit]

    translator = TranslationService()
    wikimedia = WikimediaClient(settings.wikimedia_user_agent)
    travel_guides = TravelGuideClient(user_agent=settings.wikimedia_user_agent)
    enricher = AITextEnricher(api_key=settings.pollinations_api_key)
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
        city_guide_intro = _safe_fetch_city_intro(travel_guides, city.travel_guide_url)
        if city_guide_intro:
            city_description_tr_seed = translator.translate_to_turkish(city_guide_intro)
        else:
            city_description_tr_seed = normalize_text(city.short_description)

        city_name_tr = localize_city_name(city.name, "tr")
        city_name_en = localize_city_name(city.name, "en")
        country_tr = localize_country(city.country, "tr")
        country_en = localize_country(city.country, "en")
        city_description_tr = enricher.enrich_city_description(
            city_description_tr_seed,
            city_name=city_name_tr,
            country=country_tr,
        )
        city_description_en = translator.translate_to_english(city_description_tr)
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
            place_name_tr = localize_place_name(place.name, "tr")
            place_name_en = localize_place_name(place.name, "en")
            category_tr = localize_category(place.category, "tr")
            category_en = localize_category(place.category, "en")
            travel_excerpt = _safe_fetch_place_excerpt(
                travel_guides,
                city.travel_guide_url,
                _place_search_terms(place_name_tr, place_name_en, place.wikipedia_title),
            )

            if travel_excerpt:
                description_tr_seed = translator.translate_to_turkish(travel_excerpt)
            elif tr_summary:
                description_tr_seed = normalize_text(tr_summary.extract)
            elif en_summary:
                description_tr_seed = translator.translate_to_turkish(en_summary.extract)
            else:
                description_tr_seed = normalize_text(place.seed_description)

            if tr_summary:
                source_url = city.travel_guide_url if travel_excerpt else tr_summary.page_url
            elif en_summary:
                source_url = city.travel_guide_url if travel_excerpt else en_summary.page_url
            else:
                source_url = city.travel_guide_url if travel_excerpt else place.source_url

            description_tr = enricher.enrich_place_description(
                description_tr_seed,
                city_name=city_name_tr,
                place_name=place_name_tr,
                category=category_tr,
                country=country_tr,
            )
            description_en = translator.translate_to_english(description_tr)
            prompt = build_place_prompt(city_name_en, place_name_en, category_en, country_en)
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
            image_fields, provider, should_delay = _select_image_fields(
                media_mode=settings.strapi_media_mode,
                existing_place=existing_place,
                fallback_url=fallback_url,
                prompt=prompt,
                image_generator=image_generator,
                strapi=strapi,
            )

            relation = {"documentId": city_document_id}
            tr_payload = {
                "name": place_name_tr,
                "slug": place.slug,
                "description": description_tr,
                "rating": place.rating,
                "category": category_tr,
                "source_url": source_url or place.source_url,
                "generated_prompt": prompt,
                "city": relation,
                **image_fields,
            }
            en_payload = {
                "name": place_name_en,
                "slug": place.slug,
                "description": description_en,
                "rating": place.rating,
                "category": category_en,
                "source_url": source_url or place.source_url,
                "generated_prompt": prompt,
                "city": relation,
                **image_fields,
            }

            strapi.upsert_place(tr_payload, en_payload)
            created_places += 1
            print(f"[OK] {city.name} / {place.name} -> using {provider}")
            if should_delay:
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
