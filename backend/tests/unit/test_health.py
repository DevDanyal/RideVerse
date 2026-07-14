from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_response_structure(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_returns_200(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_response_contains_project_name(client: AsyncClient) -> None:
    response = await client.get("/")
    data = response.json()
    assert "name" in data
    assert data["name"] == "RideVerse"
    assert "version" in data


@pytest.mark.asyncio
async def test_docs_available_in_debug(client: AsyncClient) -> None:
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_nonexistent_route_returns_404(client: AsyncClient) -> None:
    response = await client.get("/nonexistent")
    assert response.status_code in (404, 405)
