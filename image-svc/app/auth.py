"""Single shared bearer token, checked as a FastAPI dependency.

Uses the HTTPBearer security scheme so Swagger (/docs) shows an "Authorize"
button — paste just the token there and the UI sends the `Bearer ` prefix.

Single-user service. If the token is unset the check is skipped (dev only);
the service is expected to stay on the LAN/VPN regardless.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings, get_settings

# auto_error=False so we handle the missing-credentials case ourselves (401, and
# the dev bypass below) instead of HTTPBearer's automatic 403.
_bearer = HTTPBearer(auto_error=False, description="Shared image-svc token (no 'Bearer ' prefix).")


def require_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.api_token:
        return  # auth disabled (dev)

    token = credentials.credentials if credentials else ""
    if not token or not secrets.compare_digest(token, settings.api_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
