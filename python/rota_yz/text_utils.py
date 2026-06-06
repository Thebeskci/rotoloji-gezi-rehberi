from __future__ import annotations

import re
import unicodedata
from urllib.parse import quote_plus


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return normalized or "item"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def build_place_prompt(city_name: str, place_name: str, category: str, country: str) -> str:
    prompt = (
        f"Cinematic travel photo of {place_name} in {city_name}, {country}; "
        f"{category.lower()} destination, clear daylight, inviting atmosphere, "
        "high detail, editorial travel magazine style, no text, no watermark"
    )
    return normalize_text(prompt)


def build_placeholder_url(label: str) -> str:
    return f"https://placehold.co/1280x720/png?text={quote_plus(label[:60])}"
