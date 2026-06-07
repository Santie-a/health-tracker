"""Request-id middleware + global exception handlers (consistent error shape).

Resilience contract (ARCHITECTURE.md "Resilience"): the gateway logs failures
and keeps serving. Every response carries an ``X-Request-ID``; every error body
echoes it so a user-visible failure maps to an exact log line. No stack trace
ever leaks to the client — but one is always recorded.

Error body shape (consistent across all handlers):
    {"detail": "<message>", "request_id": "<id>"}
validation errors add an ``errors`` list.
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("server")

# Set per request by the middleware; read by handlers and available to any code
# that wants to tag a log line with the current request.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

REQUEST_ID_HEADER = "X-Request-ID"


def current_request_id() -> str:
    return request_id_ctx.get()


def install_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _request_id(request: Request, call_next):
        rid = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = request_id_ctx.set(rid)
        request.state.request_id = rid
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers[REQUEST_ID_HEADER] = rid
        return response


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Expected, intentional errors (401/404/415/...). Log at WARNING for the
        # 4xx, keep the intended status + detail, add the request id.
        rid = current_request_id()
        if exc.status_code >= 500:
            log.error("HTTP %s on %s %s request_id=%s", exc.status_code, request.method, request.url.path, rid)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": rid},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(request: Request, exc: RequestValidationError) -> JSONResponse:
        rid = current_request_id()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error.",
                "errors": jsonable_encoder(exc.errors()),
                "request_id": rid,
            },
        )

    @app.exception_handler(Exception)
    async def _unhandled_exc(request: Request, exc: Exception) -> JSONResponse:
        # Last line of defense: record the failure with context, return a clean
        # 500 so the process keeps serving the next request.
        rid = current_request_id()
        log.exception("Unhandled error on %s %s request_id=%s", request.method, request.url.path, rid)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error.", "request_id": rid},
        )
