from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from rota_yz.text_utils import normalize_text


def _normalize_lookup(value: str) -> str:
    compact = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^a-zA-Z0-9]+", " ", compact).strip().lower()
    return compact


@dataclass(frozen=True)
class TravelGuidePage:
    url: str
    intro: str | None
    blocks: list[str]


class TravelGuideClient:
    def __init__(
        self,
        *,
        user_agent: str,
        session: requests.Session | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.session = session or requests.Session()
        self._cache: dict[str, TravelGuidePage] = {}

    def fetch_city_intro(self, url: str | None) -> str | None:
        if not url:
            return None
        return self._fetch_page(url).intro

    def find_place_excerpt(self, url: str | None, search_terms: list[str]) -> str | None:
        if not url:
            return None

        page = self._fetch_page(url)
        normalized_blocks = [(block, _normalize_lookup(block)) for block in page.blocks]

        for term in search_terms:
            normalized_term = _normalize_lookup(term)
            if len(normalized_term) < 4:
                continue

            matches = [
                block
                for block, normalized_block in normalized_blocks
                if normalized_term in normalized_block
            ]
            if matches:
                return min(matches, key=len)

        return None

    def _fetch_page(self, url: str) -> TravelGuidePage:
        cached = self._cache.get(url)
        if cached is not None:
            return cached

        response = self.session.get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=30,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content = soup.select_one("#mw-content-text")
        if content is None:
            content = soup

        for selector in [
            "script",
            "style",
            "sup.reference",
            "table",
            ".thumb",
            ".infobox",
            ".navbox",
            ".metadata",
            ".mw-editsection",
        ]:
            for node in content.select(selector):
                node.decompose()

        intro = None
        blocks: list[str] = []
        for node in content.select("p, li, dd"):
            text = normalize_text(node.get_text(" ", strip=True))
            if len(text) < 45:
                continue
            blocks.append(text)
            if intro is None and node.name == "p":
                intro = text

        page = TravelGuidePage(url=url, intro=intro, blocks=blocks)
        self._cache[url] = page
        return page
