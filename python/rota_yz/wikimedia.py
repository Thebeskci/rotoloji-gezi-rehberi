from __future__ import annotations

import re
import time
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlparse

import requests

from rota_yz.models import WikimediaSummary
from rota_yz.text_utils import normalize_text


OG_IMAGE_RE = re.compile(r'<meta property="og:image" content="([^"]+)"')


class WikimediaClient:
    def __init__(self, user_agent: str, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()
        self.user_agent = user_agent

    def fetch_summary(self, title: str, locale: str = "tr") -> WikimediaSummary | None:
        encoded_title = quote(title, safe="")
        url = f"https://{locale}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
        response = self._get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=30,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        payload = response.json()

        extract = normalize_text(payload.get("extract") or "")
        if not extract:
            return None

        content_urls = payload.get("content_urls", {})
        desktop = content_urls.get("desktop", {})
        thumbnail = payload.get("thumbnail", {})
        page_image = self.fetch_page_image(title, locale=locale)

        return WikimediaSummary(
            title=payload.get("title") or title,
            extract=extract,
            page_url=desktop.get("page"),
            thumbnail_url=page_image or thumbnail.get("source"),
        )

    def fetch_best_summary(self, title: str) -> WikimediaSummary | None:
        fallback = None
        for locale in ("tr", "en"):
            try:
                summary = self.fetch_summary(title, locale=locale)
            except requests.RequestException:
                summary = None

            if summary is not None and summary.thumbnail_url:
                return summary
            if summary is not None and fallback is None:
                fallback = summary

        return fallback

    def fetch_best_image_url(self, title: str | None, source_url: str | None = None) -> str | None:
        if source_url:
            try:
                open_graph = self.fetch_open_graph_image(source_url)
            except requests.RequestException:
                open_graph = None
            if open_graph:
                return open_graph

            parsed_source = self.parse_wikipedia_source_url(source_url)
            if parsed_source is not None:
                locale, parsed_title = parsed_source
                try:
                    page_image = self.fetch_page_image(parsed_title, locale=locale)
                except requests.RequestException:
                    page_image = None
                if page_image:
                    return page_image

        if not title:
            return None

        for locale in ("tr", "en"):
            try:
                page_image = self.fetch_page_image(title, locale=locale)
            except requests.RequestException:
                page_image = None
            if page_image:
                return page_image

        return None

    def fetch_open_graph_image(self, url: str) -> str | None:
        response = self._get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=30,
        )
        match = OG_IMAGE_RE.search(response.text)
        return match.group(1) if match else None

    def parse_wikipedia_source_url(self, url: str) -> tuple[str, str] | None:
        parsed = urlparse(url)
        if not parsed.netloc.endswith(".wikipedia.org"):
            return None
        if "/wiki/" not in parsed.path:
            return None
        locale = parsed.netloc.split(".", 1)[0]
        title = unquote(parsed.path.split("/wiki/", 1)[1])
        return locale, title

    def fetch_page_image(self, title: str, locale: str = "tr") -> str | None:
        response = self._get(
            f"https://{locale}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "pageimages",
                "titles": title,
                "format": "json",
                "pithumbsize": "1200",
            },
            headers={"User-Agent": self.user_agent},
            timeout=30,
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            pageimage = page.get("pageimage")
            if isinstance(pageimage, str) and pageimage.lower().endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".svg")
            ):
                return (
                    "https://commons.wikimedia.org/wiki/Special:FilePath/"
                    f"{quote(pageimage, safe='')}?width=1280"
                )
            thumbnail = page.get("thumbnail", {})
            source = thumbnail.get("source")
            if source:
                return source
        return None

    def _get(self, url: str, **kwargs) -> requests.Response:
        response = None
        for attempt in range(3):
            response = self.session.get(url, **kwargs)
            if response.status_code not in {429, 503}:
                return response
            time.sleep(2 * (attempt + 1))

        if response is None:
            raise requests.RequestException("Wikimedia request did not produce a response.")

        return response
