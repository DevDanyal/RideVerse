"""CORS middleware configuration helper."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(
    app: FastAPI,
    allow_origins: list[str] | None = None,
    allow_credentials: bool = True,
    allow_methods: list[str] | None = None,
    allow_headers: list[str] | None = None,
) -> None:
    """Configure CORS middleware on the FastAPI application.

    Args:
        app: FastAPI application instance.
        allow_origins: List of allowed origins. Defaults to ["*"].
        allow_credentials: Whether to allow credentials.
        allow_methods: Allowed HTTP methods. Defaults to all.
        allow_headers: Allowed headers. Defaults to all.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["*"],
        allow_credentials=allow_credentials,
        allow_methods=allow_methods or ["*"],
        allow_headers=allow_headers or ["*"],
    )
