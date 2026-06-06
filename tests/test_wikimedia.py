from __future__ import annotations

from rota_yz.wikimedia import WikimediaClient


class MockResponse:
    def __init__(self, *, status_code: int = 200, json_data=None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

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
        return self.responses.pop(0)


def test_fetch_best_image_url_prefers_source_open_graph() -> None:
    session = MockSession(
        [
            MockResponse(
                text='<html><head><meta property="og:image" content="https://img.example.com/park.jpg"></head></html>'
            )
        ]
    )
    client = WikimediaClient("Rotoloji/0.1", session=session)
    image_url = client.fetch_best_image_url(
        "Central Park",
        source_url="https://tr.wikipedia.org/wiki/Central_Park",
    )
    assert image_url == "https://img.example.com/park.jpg"


def test_parse_wikipedia_source_url_extracts_locale_and_title() -> None:
    client = WikimediaClient("Rotoloji/0.1", session=MockSession([]))
    assert client.parse_wikipedia_source_url(
        "https://en.wikipedia.org/wiki/Shibuya_Crossing"
    ) == ("en", "Shibuya_Crossing")
