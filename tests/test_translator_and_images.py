from __future__ import annotations

import requests

from rota_yz.images import ImageGenerator
from rota_yz.translator import TranslationService


class MockResponse:
    def __init__(self, *, status_code: int = 200, json_data=None, content: bytes = b"", headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.content = content
        self.headers = headers or {}

    def json(self):
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class MockSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_translation_falls_back_to_source_text(monkeypatch) -> None:
    class BrokenTranslator:
        def __init__(self, source: str, target: str) -> None:
            self.source = source
            self.target = target

        def translate(self, text: str) -> str:
            raise RuntimeError("translator unavailable")

    monkeypatch.setattr("rota_yz.translator.GoogleTranslator", BrokenTranslator)
    service = TranslationService()
    assert service.translate_to_english("Merhaba dunya") == "Merhaba dunya"
    assert service.translate_to_turkish("Hello world") == "Hello world"


def test_image_generator_uses_fallback_when_no_api_key() -> None:
    session = MockSession(
        [
            MockResponse(
                content=b"png-bytes",
                headers={"content-type": "image/png"},
            ),
        ]
    )
    generator = ImageGenerator(api_key=None, session=session)
    asset = generator.generate("Ayasofya skyline", fallback_url="https://example.com/image.png")
    assert asset.provider == "wikimedia"
    assert asset.content == b"png-bytes"
