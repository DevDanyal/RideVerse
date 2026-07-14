from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_returns_201(client: AsyncClient, sample_register_payload: dict) -> None:
    response = await client.post("/api/v1/auth/register", json=sample_register_payload)
    assert response.status_code in (200, 201)


@pytest.mark.asyncio
async def test_register_response_structure(client: AsyncClient, sample_register_payload: dict) -> None:
    response = await client.post("/api/v1/auth/register", json=sample_register_payload)
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient, sample_register_payload: dict) -> None:
    await client.post("/api/v1/auth/register", json=sample_register_payload)
    response = await client.post("/api/v1/auth/register", json=sample_register_payload)
    assert response.status_code in (400, 409, 422)


@pytest.mark.asyncio
async def test_login_returns_token(client: AsyncClient, sample_register_payload: dict, sample_login_payload: dict) -> None:
    await client.post("/api/v1/auth/register", json=sample_register_payload)
    response = await client.post("/api/v1/auth/login", json=sample_login_payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)
