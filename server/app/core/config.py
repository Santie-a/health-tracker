"""Service configuration, loaded from environment / .env.

Single source of truth for tunables. See .env.example for the documented set.
Mirrors image-svc's pattern (pydantic-settings + cached accessor) but uses
unprefixed names matching DEPLOY.md (DATABASE_URL, API_TOKEN, IMAGE_SVC_URL).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- database ---------------------------------------------------------
    # asyncpg driver URL. Lazy: the engine doesn't connect until first query,
    # so a wrong/unreachable DB fails at request time (clean 503), not at boot.
    database_url: str = "postgresql+asyncpg://health:health@localhost:5432/health_tracker"

    # --- auth -------------------------------------------------------------
    # Shared bearer token the frontend sends. Empty string disables auth
    # (dev only; keep the service on the LAN/VPN regardless).
    api_token: str = ""

    # --- image-svc bridge -------------------------------------------------
    # URL of the GPU image service; the SAME api_token is sent to it.
    image_svc_url: str = "http://localhost:8001"
    # Seconds to wait before falling back to the manual-entry path.
    image_svc_timeout: float = 30.0

    # --- observability ----------------------------------------------------
    log_level: str = "INFO"  # DEBUG | INFO | WARNING | ERROR


@lru_cache
def get_settings() -> Settings:
    return Settings()
