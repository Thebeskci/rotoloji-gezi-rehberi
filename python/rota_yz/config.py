from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

VALID_DATA_MODES = {"auto", "api", "snapshot"}


def default_snapshot_path() -> str:
    return str(Path(__file__).resolve().parents[2] / "data" / "live_content.json")


@dataclass(frozen=True)
class Settings:
    strapi_url: str
    strapi_email: str | None = None
    strapi_password: str | None = None
    pollinations_api_key: str | None = None
    wikimedia_user_agent: str = "RotaYZ/0.1 (student@example.com)"
    streamlit_data_mode: str = "auto"
    snapshot_path: str = default_snapshot_path()

    @classmethod
    def from_env(cls, *, require_auth: bool = False) -> "Settings":
        strapi_url = os.getenv("STRAPI_URL", "http://localhost:1337").rstrip("/")
        strapi_email = os.getenv("STRAPI_EMAIL")
        strapi_password = os.getenv("STRAPI_PASSWORD")
        streamlit_data_mode = (os.getenv("STREAMLIT_DATA_MODE", "auto") or "auto").strip().lower()
        snapshot_path = os.getenv("STREAMLIT_SNAPSHOT_PATH") or default_snapshot_path()

        if require_auth and (not strapi_email or not strapi_password):
            raise ValueError("STRAPI_EMAIL and STRAPI_PASSWORD must be defined for ingest.")
        if streamlit_data_mode not in VALID_DATA_MODES:
            raise ValueError(
                f"STREAMLIT_DATA_MODE must be one of {sorted(VALID_DATA_MODES)}."
            )

        return cls(
            strapi_url=strapi_url,
            strapi_email=strapi_email,
            strapi_password=strapi_password,
            pollinations_api_key=os.getenv("POLLINATIONS_API_KEY") or None,
            wikimedia_user_agent=os.getenv(
                "WIKIMEDIA_USER_AGENT", "RotaYZ/0.1 (student@example.com)"
            ),
            streamlit_data_mode=streamlit_data_mode,
            snapshot_path=snapshot_path,
        )
