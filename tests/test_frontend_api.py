from __future__ import annotations

from rota_yz.frontend_api import FrontendAPI


class MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    def raise_for_status(self) -> None:
        return None


class MockSession:
    def __init__(self, payload):
        self.payload = payload

    def get(self, url, **kwargs):
        return MockResponse(self.payload)


def test_frontend_api_maps_relative_media_urls() -> None:
    payload = {
        "data": [
            {
                "id": 1,
                "documentId": "doc-place-1",
                "attributes": {
                    "name": "Ayasofya",
                    "slug": "istanbul-ayasofya",
                    "description": "Aciklama",
                    "rating": "4.9",
                    "category": "Tarih",
                    "source_url": "https://example.com",
                    "generated_prompt": "prompt",
                    "cover_image": {
                        "data": {
                            "id": 44,
                            "documentId": "media-1",
                            "attributes": {"url": "/uploads/ayasofya.png"},
                        }
                    },
                    "city": {
                        "data": {
                            "id": 2,
                            "documentId": "doc-city-1",
                            "attributes": {"name": "Istanbul", "slug": "istanbul"},
                        }
                    },
                },
            }
        ]
    }

    api = FrontendAPI("https://demo.example.com", session=MockSession(payload))
    places = api.fetch_places("tr")
    assert places[0]["image_url"] == "https://demo.example.com/uploads/ayasofya.png"
    assert places[0]["city_slug"] == "istanbul"
