from __future__ import annotations

import base64
import json
from pathlib import Path

import requests

from rota_yz.build_pages import build_pages_site, export_asset


def test_build_pages_site_exports_assets_and_locale_bundles(tmp_path: Path) -> None:
    image_data = base64.b64encode(b"fake-jpeg").decode("ascii")
    snapshot_path = tmp_path / "live_content.json"
    pages_source_dir = tmp_path / "pages"
    output_dir = tmp_path / "dist-pages"

    snapshot = {
        "generated_at": "2026-06-07T00:00:00Z",
        "source": "snapshot",
        "locales": {
            "tr": {
                "cities": [
                    {
                        "name": "Istanbul",
                        "slug": "istanbul",
                        "country": "Turkiye",
                        "short_description": "Bogaz sehri",
                        "hero_image_url": f"data:image/jpeg;base64,{image_data}",
                    }
                ],
                "places": [
                    {
                        "name": "Ayasofya",
                        "slug": "ayasofya",
                        "description": "Tarihi yapi",
                        "rating": 4.9,
                        "category": "Tarihi Alan",
                        "source_url": "https://example.com/ayasofya",
                        "generated_prompt": "Golden hour travel photo",
                        "city_name": "Istanbul",
                        "city_slug": "istanbul",
                        "image_url": f"data:image/jpeg;base64,{image_data}",
                    }
                ],
            },
            "en": {
                "cities": [
                    {
                        "name": "Istanbul",
                        "slug": "istanbul",
                        "country": "Turkey",
                        "short_description": "Bosporus city",
                        "hero_image_url": f"data:image/jpeg;base64,{image_data}",
                    }
                ],
                "places": [
                    {
                        "name": "Hagia Sophia",
                        "slug": "ayasofya",
                        "description": "Historic monument",
                        "rating": 4.9,
                        "category": "Historic Site",
                        "source_url": "https://example.com/ayasofya",
                        "generated_prompt": "Golden hour travel photo",
                        "city_name": "Istanbul",
                        "city_slug": "istanbul",
                        "image_url": f"data:image/jpeg;base64,{image_data}",
                    }
                ],
            },
        },
    }

    pages_source_dir.mkdir()
    (pages_source_dir / "index.html").write_text("<!doctype html><title>Rotoloji</title>", encoding="utf-8")
    (pages_source_dir / "styles.css").write_text("body { color: #000; }", encoding="utf-8")
    (pages_source_dir / "app.js").write_text("console.log('rotoloji');", encoding="utf-8")
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    build_pages_site(snapshot_path=snapshot_path, pages_source_dir=pages_source_dir, output_dir=output_dir)

    manifest = json.loads((output_dir / "data" / "manifest.json").read_text(encoding="utf-8"))
    tr_bundle = json.loads((output_dir / "data" / "tr.json").read_text(encoding="utf-8"))
    en_bundle = json.loads((output_dir / "data" / "en.json").read_text(encoding="utf-8"))

    assert manifest["locales"] == ["en", "tr"]
    assert tr_bundle["cities"][0]["hero_image_url"] == "assets/cities/istanbul.jpg"
    assert tr_bundle["places"][0]["image_url"] == "assets/places/ayasofya.jpg"
    assert en_bundle["places"][0]["name"] == "Hagia Sophia"
    assert (output_dir / "assets" / "cities" / "istanbul.jpg").read_bytes() == b"fake-jpeg"
    assert (output_dir / "assets" / "places" / "ayasofya.jpg").read_bytes() == b"fake-jpeg"
    assert (output_dir / "404.html").exists()
    assert (output_dir / ".nojekyll").exists()


def test_export_asset_returns_none_for_unreachable_http_image(monkeypatch, tmp_path: Path) -> None:
    class BrokenSession:
        def get(self, *_args, **_kwargs):
            raise requests.RequestException("blocked")

    result = export_asset("https://example.com/not-an-image", "broken", tmp_path, BrokenSession())
    assert result is None
