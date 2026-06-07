from __future__ import annotations

import requests

from rota_yz.text_enrichment import AITextEnricher


class MockResponse:
    def __init__(self, *, status_code: int = 200, text: str = "") -> None:
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class MockSession:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_text_enricher_returns_ai_output_when_available() -> None:
    session = MockSession([MockResponse(text="Ayasofya, ziyaretciye hem tarih hem de olcek duygusu verir.")])
    enricher = AITextEnricher(session=session)
    enriched = enricher.enrich_place_description(
        "Ayasofya tarihi bir yapidir.",
        city_name="Istanbul",
        place_name="Ayasofya",
        category="Tarih",
        country="Turkiye",
    )
    assert "tarih" in enriched.lower()


def test_text_enricher_falls_back_to_source_text_on_error() -> None:
    session = MockSession([requests.RequestException("network error")])
    enricher = AITextEnricher(session=session)
    enriched = enricher.enrich_city_description(
        "Paris yogun bir sehir deneyimi sunar.",
        city_name="Paris",
        country="Fransa",
    )
    assert enriched == "Paris yogun bir sehir deneyimi sunar."
