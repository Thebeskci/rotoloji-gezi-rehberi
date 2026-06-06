from __future__ import annotations

from rota_yz.models import ImageAsset
from rota_yz.strapi_client import StrapiClient


class MockResponse:
    def __init__(self, *, status_code: int = 200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class MockSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


def test_authenticate_stores_jwt() -> None:
    session = MockSession([MockResponse(json_data={"jwt": "token-123"})])
    client = StrapiClient("http://localhost:1337", email="user@test.com", password="secret", session=session)
    assert client.authenticate() == "token-123"
    assert client.jwt == "token-123"


def test_upload_image_returns_first_uploaded_file() -> None:
    session = MockSession(
        [
            MockResponse(json_data={"jwt": "token-123"}),
            MockResponse(json_data=[{"id": 7, "url": "/uploads/hero.png"}]),
        ]
    )
    client = StrapiClient("http://localhost:1337", email="user@test.com", password="secret", session=session)
    image = ImageAsset(
        filename="hero.png",
        content=b"png",
        content_type="image/png",
        provider="pollinations",
        prompt="hero prompt",
    )
    payload = client.upload_image(image)
    assert payload["id"] == 7


def test_upsert_city_creates_tr_and_en_documents() -> None:
    session = MockSession(
        [
            MockResponse(json_data={"jwt": "token-123"}),
            MockResponse(json_data={"data": []}),
            MockResponse(json_data={"data": {"id": 1, "documentId": "doc-city-1", "attributes": {}}}, status_code=201),
            MockResponse(json_data={"data": {"id": 2, "documentId": "doc-city-1", "attributes": {}}}),
        ]
    )
    client = StrapiClient("http://localhost:1337", email="user@test.com", password="secret", session=session)
    document_id = client.upsert_city(
        {"name": "Istanbul", "slug": "istanbul", "country": "Turkiye", "short_description": "TR"},
        {"name": "Istanbul", "slug": "istanbul", "country": "Turkey", "short_description": "EN"},
    )
    assert document_id == "doc-city-1"
    methods = [call[0] for call in session.calls]
    assert methods == ["POST", "GET", "POST", "PUT"]
