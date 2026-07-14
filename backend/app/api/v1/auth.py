"""Authentication API endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.repositories.auth import AuthRepository
from app.schemas.auth import (
    AccountResponse,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import SuccessResponse
from app.services.auth import AuthenticationService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_auth_service(session: AsyncSession) -> AuthenticationService:
    repo = AuthRepository(session)
    return AuthenticationService(repo)


# ── Register ───────────────────────────────────────────────────────────────────


@router.post("/register", status_code=201, response_model=SuccessResponse[TokenResponse])
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Register a new account."""
    svc = _get_auth_service(session)
    result = await svc.register(
        email=body.email,
        username=body.username,
        password=body.password,
    )
    return SuccessResponse(
        message="Account created successfully",
        data=TokenResponse(**result),
    )


# ── Login ──────────────────────────────────────────────────────────────────────


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(
    body: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Authenticate with email and password."""
    svc = _get_auth_service(session)
    device_info = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    result = await svc.login(
        email=body.email,
        password=body.password,
        device_info=device_info,
        ip_address=ip_address,
    )
    return SuccessResponse(
        message="Login successful",
        data=TokenResponse(**result),
    )


# ── Refresh Token ──────────────────────────────────────────────────────────────


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh_token(
    body: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[TokenResponse]:
    """Exchange a refresh token for a new token pair (rotation)."""
    svc = _get_auth_service(session)
    result = await svc.refresh_token(refresh_token=body.refresh_token)
    return SuccessResponse(
        message="Token refreshed successfully",
        data=TokenResponse(**result),
    )


# ── Logout ─────────────────────────────────────────────────────────────────────


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[None]:
    """Revoke the current session's refresh token."""
    svc = _get_auth_service(session)
    await svc.logout(refresh_token=body.refresh_token)
    return SuccessResponse(message="Logged out successfully")


# ── Current User ───────────────────────────────────────────────────────────────


@router.get("/me", response_model=SuccessResponse[AccountResponse])
async def get_current_user(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[AccountResponse]:
    """Get the authenticated user's account information."""
    svc = _get_auth_service(session)
    account = await svc.get_account(account_id=uuid.UUID(current_user["sub"]))
    return SuccessResponse(
        message="Account retrieved successfully",
        data=AccountResponse(**account),
    )
