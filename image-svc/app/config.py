"""Service configuration, loaded from environment / .env.

Single source of truth for tunables. See .env.example for the documented set.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import nutrition_core
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Macro table now lives in the shared nutrition_core package (single source of
# truth shared with the gateway). Installed editable, so it's a local file.
_DEFAULT_MACRO_TABLE = nutrition_core.default_macro_csv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="IMAGE_SVC_",
        extra="ignore",
    )

    # --- auth -------------------------------------------------------------
    # Shared bearer token the gateway sends. Empty string disables auth
    # (dev only; the service must stay on the LAN/VPN regardless).
    api_token: str = ""

    # --- estimator backend ------------------------------------------------
    # "stub" returns a deterministic placeholder so the gateway can integrate
    # before the model is wired. "vlm" runs the local vision-LLM.
    backend: Literal["stub", "vlm"] = "stub"

    # --- model (vlm backend) ---------------------------------------------
    # 3B fits in 12 GB (RTX 5070) at bf16 without quantization; 7B needs 4-bit.
    model_name: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    # Optional local model dir / HF cache override. Empty -> default HF cache.
    model_dir: str = ""
    # "auto" picks cuda when available, else cpu.
    device: Literal["auto", "cuda", "cpu"] = "auto"
    # Load the model eagerly at startup instead of on first request.
    preload_model: bool = False
    # Load 7B-class models in 4-bit to fit 12 GB (needs bitsandbytes).
    load_in_4bit: bool = False

    # --- nutrition mapping ------------------------------------------------
    macro_table_path: Path = Field(default=_DEFAULT_MACRO_TABLE)

    # --- versioning (recorded on every estimate) -------------------------
    model_version: str = "stub-0"
    table_version: str = nutrition_core.TABLE_VERSION

    # --- limits -----------------------------------------------------------
    max_image_mb: float = 15.0
    # Decoded-pixel ceiling (decompression-bomb guard). The MB cap bounds bytes,
    # not decoded size; 100 MP is generous for high-res phone photos.
    max_image_pixels: int = 100_000_000

    # --- observability ----------------------------------------------------
    log_level: str = "INFO"  # DEBUG | INFO | WARNING | ERROR


@lru_cache
def get_settings() -> Settings:
    return Settings()
