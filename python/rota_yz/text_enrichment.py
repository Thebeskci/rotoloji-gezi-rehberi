from __future__ import annotations

from urllib.parse import quote

import requests

from rota_yz.text_utils import normalize_text


class AITextEnricher:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.session = session or requests.Session()

    def enrich_city_description(self, base_text: str, *, city_name: str, country: str) -> str:
        prompt = (
            "Expand the following travel guide note into 2 concise editorial sentences in Turkish. "
            "Keep it factual, easy to read, and focused on what a visitor notices. "
            f"City: {city_name}. Country: {country}. Base text: {normalize_text(base_text)}"
        )
        return self._generate(prompt, fallback=base_text)

    def enrich_place_description(
        self,
        base_text: str,
        *,
        city_name: str,
        place_name: str,
        category: str,
        country: str,
    ) -> str:
        prompt = (
            "Expand the following travel guide note into 2 concise editorial sentences in Turkish. "
            "Keep it factual, avoid markdown, and mention the visitor experience without exaggeration. "
            f"Place: {place_name}. City: {city_name}. Country: {country}. Category: {category}. "
            f"Base text: {normalize_text(base_text)}"
        )
        return self._generate(prompt, fallback=base_text)

    def _generate(self, prompt: str, *, fallback: str) -> str:
        encoded_prompt = quote(prompt, safe="")
        url = f"https://gen.pollinations.ai/text/{encoded_prompt}?model=openai&seed=0"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = self.session.get(url, headers=headers, timeout=(10, 35))
            response.raise_for_status()
        except requests.RequestException:
            return normalize_text(fallback)

        text = normalize_text(response.text)
        return text or normalize_text(fallback)
