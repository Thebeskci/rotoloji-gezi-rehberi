from __future__ import annotations

from typing import Any

import requests

from rota_yz.models import ImageAsset


class StrapiClient:
    def __init__(
        self,
        base_url: str,
        *,
        email: str | None = None,
        password: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.session = session or requests.Session()
        self.jwt: str | None = None

    def authenticate(self) -> str:
        if self.jwt:
            return self.jwt

        if not self.email or not self.password:
            raise ValueError("Email and password are required to authenticate with Strapi.")

        response = self.session.post(
            f"{self.base_url}/api/auth/local",
            json={"identifier": self.email, "password": self.password},
            timeout=30,
        )
        response.raise_for_status()
        self.jwt = response.json()["jwt"]
        return self.jwt

    def upload_image(self, image: ImageAsset) -> dict[str, Any]:
        response = self._request(
            "POST",
            "/api/upload",
            files={"files": (image.filename, image.content, image.content_type)},
            expected_status=200,
        )
        payload = response.json()
        if isinstance(payload, list):
            return payload[0]
        return payload

    def find_document(
        self,
        collection: str,
        *,
        slug: str,
        locale: str = "tr",
        populate: list[str] | None = None,
    ) -> dict[str, Any] | None:
        params: list[tuple[str, str]] = [
            ("locale", locale),
            ("filters[slug][$eq]", slug),
        ]

        for index, field in enumerate(populate or []):
            params.append((f"populate[{index}]", field))

        response = self._request("GET", f"/api/{collection}", params=params, expected_status=200)
        records = response.json().get("data", [])
        return records[0] if records else None

    def create_document(self, collection: str, *, locale: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self._request(
            "POST",
            f"/api/{collection}",
            params={"locale": locale},
            json={"data": data},
            expected_status=201,
        )
        return response.json()["data"]

    def update_document(
        self,
        collection: str,
        *,
        document_id: str,
        locale: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._request(
            "PUT",
            f"/api/{collection}/{document_id}",
            params={"locale": locale},
            json={"data": data},
            expected_status=200,
        )
        return response.json()["data"]

    def upsert_city(self, tr_payload: dict[str, Any], en_payload: dict[str, Any]) -> str:
        existing = self.find_document("cities", slug=tr_payload["slug"], locale="tr")
        if existing:
            document_id = existing["documentId"]
            self.update_document("cities", document_id=document_id, locale="tr", data=tr_payload)
        else:
            created = self.create_document("cities", locale="tr", data=tr_payload)
            document_id = created["documentId"]

        self.update_document("cities", document_id=document_id, locale="en", data=en_payload)
        return document_id

    def upsert_place(self, tr_payload: dict[str, Any], en_payload: dict[str, Any]) -> str:
        existing = self.find_document("places", slug=tr_payload["slug"], locale="tr")
        if existing:
            document_id = existing["documentId"]
            self.update_document("places", document_id=document_id, locale="tr", data=tr_payload)
        else:
            created = self.create_document("places", locale="tr", data=tr_payload)
            document_id = created["documentId"]

        self.update_document("places", document_id=document_id, locale="en", data=en_payload)
        return document_id

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        **kwargs: Any,
    ) -> requests.Response:
        headers = kwargs.pop("headers", {})
        if path != "/api/auth/local":
            headers["Authorization"] = f"Bearer {self.authenticate()}"

        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=kwargs.pop("timeout", 60),
            **kwargs,
        )
        if response.status_code != expected_status:
            response.raise_for_status()
        return response
