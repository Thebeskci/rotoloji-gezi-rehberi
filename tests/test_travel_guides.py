from __future__ import annotations

from rota_yz.travel_guides import TravelGuideClient


class MockResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class MockSession:
    def __init__(self, html: str) -> None:
        self.html = html
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return MockResponse(self.html)


def test_travel_guide_client_extracts_city_intro_and_place_excerpt() -> None:
    html = """
    <html>
      <body>
        <div id="mw-content-text">
          <p>Istanbul is a layered city where ferries, monuments, and busy districts overlap.</p>
          <ul>
            <li>Hagia Sophia is one of the city's defining landmarks, known for its massive dome and layered history.</li>
            <li>Grand Bazaar remains a dense shopping maze filled with covered passages.</li>
          </ul>
        </div>
      </body>
    </html>
    """
    client = TravelGuideClient(user_agent="Rotoloji/0.1", session=MockSession(html))
    assert client.fetch_city_intro("https://example.com/istanbul")
    excerpt = client.find_place_excerpt(
        "https://example.com/istanbul",
        ["Hagia Sophia", "Ayasofya"],
    )
    assert excerpt is not None
    assert "massive dome" in excerpt
