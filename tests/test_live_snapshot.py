from __future__ import annotations

import json

import requests

from rota_yz.frontend_api import SnapshotFrontendAPI
from rota_yz.frontend_api import load_frontend_bundle


def test_snapshot_frontend_api_reads_localized_payload(tmp_path) -> None:
    snapshot_path = tmp_path / "live_content.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "locales": {
                    "tr": {
                        "cities": [{"name": "Istanbul", "slug": "istanbul"}],
                        "places": [{"name": "Ayasofya", "city_slug": "istanbul"}],
                    },
                    "en": {
                        "cities": [{"name": "Istanbul", "slug": "istanbul"}],
                        "places": [{"name": "Hagia Sophia", "city_slug": "istanbul"}],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    api = SnapshotFrontendAPI(snapshot_path)

    assert api.fetch_cities("tr")[0]["name"] == "Istanbul"
    assert api.fetch_places("en")[0]["name"] == "Hagia Sophia"


class FailingSession:
    def get(self, url, **kwargs):
        raise requests.ConnectionError(f"offline: {url}")


def test_load_frontend_bundle_falls_back_to_snapshot(tmp_path) -> None:
    snapshot_path = tmp_path / "live_content.json"
    snapshot_path.write_text(
        json.dumps(
            {
                "locales": {
                    "tr": {
                        "cities": [{"name": "Istanbul", "slug": "istanbul"}],
                        "places": [{"name": "Ayasofya", "city_slug": "istanbul"}],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    payload = load_frontend_bundle(
        base_url="http://localhost:1337",
        locale="tr",
        data_mode="auto",
        snapshot_path=snapshot_path,
        session=FailingSession(),
    )

    assert payload["source"] == "snapshot"
    assert payload["cities"][0]["slug"] == "istanbul"
