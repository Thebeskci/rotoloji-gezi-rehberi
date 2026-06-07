from __future__ import annotations

import time
from urllib.parse import quote

import requests

from rota_yz.models import ImageAsset
from rota_yz.text_utils import build_placeholder_url, slugify


class ImageGenerator:
    def __init__(
        self,
        api_key: str | None = None,
        user_agent: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key
        self.user_agent = user_agent or "RotaYZ/0.1"
        self.session = session or requests.Session()

    def generate(self, prompt: str, fallback_url: str | None = None) -> ImageAsset:
        try:
            return self._generate_pollinations(prompt)
        except requests.RequestException:
            pass

        if fallback_url:
            try:
                return self._download_image(fallback_url, provider="wikimedia", prompt=prompt)
            except requests.RequestException:
                pass

        placeholder_url = build_placeholder_url(prompt)
        return self._download_image(placeholder_url, provider="placeholder", prompt=prompt)

    def _generate_pollinations(self, prompt: str) -> ImageAsset:
        encoded_prompt = quote(prompt, safe="")
        headers = {"User-Agent": self.user_agent}
        endpoints = []
        if self.api_key:
            endpoints.append(
                (
                    f"https://gen.pollinations.ai/image/{encoded_prompt}"
                    "?width=1024&height=576&model=flux&private=true",
                    {"Authorization": f"Bearer {self.api_key}", **headers},
                )
            )
        endpoints.append(
            (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                "?width=1024&height=576&model=flux&nologo=true",
                headers,
            ),
        )

        response = None
        last_error: requests.RequestException | None = None
        for url, request_headers in endpoints:
            try:
                response = self.session.get(url, headers=request_headers, timeout=(10, 25))
                response.raise_for_status()
                break
            except requests.RequestException as exc:
                last_error = exc
                response = None

        if response is None:
            raise last_error or requests.RequestException("Pollinations image request failed.")

        response.raise_for_status()
        content_type = response.headers.get("content-type", "image/png")
        extension = "jpg" if "jpeg" in content_type else "png"
        return ImageAsset(
            filename=f"{slugify(prompt)[:48]}.{extension}",
            content=response.content,
            content_type=content_type,
            provider="pollinations",
            prompt=prompt,
        )

    def _download_image(self, url: str, provider: str, prompt: str) -> ImageAsset:
        response = None
        for attempt in range(3):
            response = self.session.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=(10, 20),
            )
            if response.status_code not in {429, 503}:
                break
            time.sleep(2 * (attempt + 1))

        if response is None:
            raise requests.RequestException("Image download did not produce a response.")

        response.raise_for_status()
        content_type = response.headers.get("content-type", "image/png")
        extension = "jpg" if "jpeg" in content_type else "png"
        return ImageAsset(
            filename=f"{slugify(prompt)[:48]}.{extension}",
            content=response.content,
            content_type=content_type,
            provider=provider,
            prompt=prompt,
        )
