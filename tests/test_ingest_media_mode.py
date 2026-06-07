from __future__ import annotations

from rota_yz.ingest import _select_image_fields


class DummyImageGenerator:
    def generate(self, prompt: str, fallback_url: str | None = None):
        raise AssertionError("generate should not be called in external mode")


class DummyStrapi:
    def upload_image(self, image):
        raise AssertionError("upload_image should not be called in external mode")


def test_select_image_fields_uses_external_url_without_upload() -> None:
    fields, provider, should_delay = _select_image_fields(
        media_mode="external",
        existing_place=None,
        fallback_url="https://images.example.com/ayasofya.jpg",
        prompt="Ayasofya prompt",
        image_generator=DummyImageGenerator(),
        strapi=DummyStrapi(),
    )

    assert fields == {
        "cover_image": None,
        "external_image_url": "https://images.example.com/ayasofya.jpg",
    }
    assert provider == "external-url"
    assert should_delay is False


def test_select_image_fields_reuses_existing_external_url() -> None:
    existing_place = {
        "id": 1,
        "documentId": "doc-place-1",
        "attributes": {
            "external_image_url": "https://cdn.example.com/existing.jpg",
        },
    }

    fields, provider, should_delay = _select_image_fields(
        media_mode="external",
        existing_place=existing_place,
        fallback_url="https://images.example.com/new.jpg",
        prompt="Ayasofya prompt",
        image_generator=DummyImageGenerator(),
        strapi=DummyStrapi(),
    )

    assert fields["external_image_url"] == "https://cdn.example.com/existing.jpg"
    assert provider == "external-url"
    assert should_delay is False
