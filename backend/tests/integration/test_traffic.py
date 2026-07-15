"""Integration tests for the Traffic System (TASK 14).

End-to-end API tests covering the full Traffic lifecycle:
register, create zone, create route, create lane, create signal,
emergency override, spawn vehicle, spawn/despawn rules, density,
violation with auto-fine, event reporting and resolution.
Uses in-memory SQLite database.
"""
from __future__ import annotations

import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_TRAFFIC_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "inventories",
        "wallets",
        "traffic_zones",
        "traffic_routes",
        "traffic_lanes",
        "traffic_signals",
        "traffic_spawn_points",
        "traffic_densities",
        "traffic_spawn_rules",
        "traffic_despawn_rules",
        "traffic_vehicles",
        "traffic_emergency_vehicles",
        "traffic_statistics",
        "traffic_speed_limits",
        "traffic_violations",
        "traffic_events",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_TRAFFIC_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_TRAFFIC_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncClient:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _register_user(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"traffic_integ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"traffic_integ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


class TestTrafficLifecycle:
    async def test_full_traffic_lifecycle(self, client: AsyncClient, test_engine):
        """Test full lifecycle: register -> zone -> route -> lane -> signal -> override -> vehicle -> spawn/despawn rules -> density -> violation -> event."""
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create a zone
        resp = await client.post(
            "/api/v1/traffic/zones",
            json={
                "zone_name": "Integration Downtown",
                "zone_type": "city_center",
                "center_x": 100.0,
                "center_y": 200.0,
                "center_z": 0.0,
                "radius": 500.0,
                "speed_limit_kmh": 50.0,
                "max_vehicles": 25,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        zone_id = resp.json()["data"]["id"]

        # Create a route
        resp = await client.post(
            "/api/v1/traffic/routes",
            json={
                "route_name": "Integration Main St",
                "route_type": "city",
                "start_x": 0.0,
                "start_y": 0.0,
                "start_z": 0.0,
                "end_x": 500.0,
                "end_y": 0.0,
                "end_z": 0.0,
                "distance_km": 5.0,
                "speed_limit_kmh": 50.0,
                "lane_count": 2,
                "zone_id": zone_id,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        route_id = resp.json()["data"]["id"]

        # Create lanes
        resp = await client.post(
            "/api/v1/traffic/lanes",
            json={
                "route_id": route_id,
                "lane_number": 1,
                "direction": "forward",
                "speed_limit_kmh": 50.0,
                "width": 3.5,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        lane_id = resp.json()["data"]["id"]

        resp = await client.post(
            "/api/v1/traffic/lanes",
            json={
                "route_id": route_id,
                "lane_number": 2,
                "direction": "reverse",
                "speed_limit_kmh": 50.0,
            },
            headers=headers,
        )
        assert resp.status_code == 201

        # List lanes for route
        resp = await client.get(
            f"/api/v1/traffic/routes/{route_id}/lanes",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 2

        # Create a signal
        resp = await client.post(
            "/api/v1/traffic/signals",
            json={
                "signal_name": "Downtown Signal 1",
                "location_x": 100.0,
                "location_y": 0.0,
                "location_z": 0.0,
                "state": "green",
                "cycle_duration_seconds": 30,
                "route_id": route_id,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        signal_id = resp.json()["data"]["id"]

        # Change signal state
        resp = await client.post(
            f"/api/v1/traffic/signals/{signal_id}/state/yellow",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["state"] == "yellow"

        # Activate emergency override
        resp = await client.post(
            f"/api/v1/traffic/signals/{signal_id}/emergency-on",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["state"] == "emergency_override"
        assert resp.json()["data"]["is_emergency_override"] is True

        # Deactivate emergency override
        resp = await client.post(
            f"/api/v1/traffic/signals/{signal_id}/emergency-off",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["state"] == "green"

        # Create spawn point
        resp = await client.post(
            "/api/v1/traffic/spawn-points",
            json={
                "spawn_name": "Downtown Spawn North",
                "location_x": 0.0,
                "location_y": 100.0,
                "location_z": 0.0,
                "spawn_type": "spawn",
                "max_vehicles": 10,
                "route_id": route_id,
                "zone_id": zone_id,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        spawn_point_id = resp.json()["data"]["id"]

        # Create density config
        resp = await client.post(
            "/api/v1/traffic/density",
            json={
                "density_level": "medium",
                "vehicle_limit": 30,
                "spawn_rate": 2.0,
                "zone_id": zone_id,
                "time_of_day": "afternoon",
                "weather_condition": "clear",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        density_id = resp.json()["data"]["id"]

        # Create spawn rule
        resp = await client.post(
            "/api/v1/traffic/spawn-rules",
            json={
                "rule_name": "Downtown Continuous",
                "rule_type": "continuous",
                "vehicle_type": "sedan",
                "max_spawn_count": 20,
                "spawn_interval_seconds": 5,
                "min_distance_from_player": 100.0,
                "max_distance_from_player": 500.0,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        spawn_rule_id = resp.json()["data"]["id"]

        # Create despawn rule
        resp = await client.post(
            "/api/v1/traffic/despawn-rules",
            json={
                "rule_name": "Distance Despawn",
                "rule_type": "distance",
                "max_distance_from_player": 800.0,
                "max_lifetime_seconds": 300,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        despawn_rule_id = resp.json()["data"]["id"]

        # Spawn a vehicle
        resp = await client.post(
            "/api/v1/traffic/vehicles",
            json={
                "vehicle_type": "sedan",
                "model_name": "Toyota Corolla",
                "speed_kmh": 45.0,
                "max_speed_kmh": 180.0,
                "location_x": 50.0,
                "location_y": 0.0,
                "location_z": 0.0,
                "color": "white",
                "route_id": route_id,
                "lane_id": lane_id,
                "zone_id": zone_id,
                "spawn_point_id": spawn_point_id,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        vehicle_id = resp.json()["data"]["id"]
        assert resp.json()["data"]["model_name"] == "Toyota Corolla"
        assert resp.json()["data"]["spawned_at"] is not None

        # Spawn emergency vehicle
        resp = await client.post(
            "/api/v1/traffic/vehicles",
            json={
                "vehicle_type": "sedan",
                "model_name": "Police Charger",
                "location_x": 0.0,
                "location_y": 0.0,
                "location_z": 0.0,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        emergency_vehicle_id = resp.json()["data"]["id"]

        # Register as emergency vehicle
        resp = await client.post(
            "/api/v1/traffic/emergency-vehicles",
            json={
                "vehicle_id": emergency_vehicle_id,
                "emergency_type": "police",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        ev_id = resp.json()["data"]["id"]

        # Activate siren
        resp = await client.post(
            f"/api/v1/traffic/emergency-vehicles/{ev_id}/siren-on",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["siren_on"] is True

        # Deactivate siren
        resp = await client.post(
            f"/api/v1/traffic/emergency-vehicles/{ev_id}/siren-off",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["siren_on"] is False

        # Record a violation
        resp = await client.post(
            "/api/v1/traffic/violations",
            json={
                "vehicle_id": vehicle_id,
                "violation_type": "speeding",
                "speed_kmh": 120.0,
                "speed_limit_kmh": 50.0,
                "location_x": 100.0,
                "location_y": 0.0,
                "location_z": 0.0,
                "zone_id": zone_id,
            },
            headers=headers,
        )
        assert resp.status_code == 201
        violation_id = resp.json()["data"]["id"]
        assert resp.json()["data"]["fine_amount"] == 500.0

        # Resolve violation
        resp = await client.post(
            f"/api/v1/traffic/violations/{violation_id}/resolve",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_resolved"] is True

        # Report a traffic event
        resp = await client.post(
            "/api/v1/traffic/events",
            json={
                "event_type": "accident",
                "location_x": 200.0,
                "location_y": 0.0,
                "location_z": 0.0,
                "severity": "high",
                "description": "Two-car collision at intersection",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        event_id = resp.json()["data"]["id"]

        # Resolve event
        resp = await client.post(
            f"/api/v1/traffic/events/{event_id}/resolve",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["is_resolved"] is True

        # Create speed limit
        resp = await client.post(
            "/api/v1/traffic/speed-limits",
            json={
                "zone_id": zone_id,
                "road_name": "Main St",
                "speed_limit_kmh": 50.0,
                "vehicle_type_restriction": "bus",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        speed_limit_id = resp.json()["data"]["id"]

        # Create statistics
        resp = await client.post(
            "/api/v1/traffic/statistics",
            json={
                "zone_id": zone_id,
                "total_vehicles_spawned": 500,
                "total_vehicles_despawned": 480,
                "average_speed_kmh": 42.5,
                "peak_density": 35,
                "total_accidents": 2,
                "total_violations": 8,
                "date_recorded": "2026-07-15",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        stats_id = resp.json()["data"]["id"]

        # Get statistics
        resp = await client.get(
            f"/api/v1/traffic/statistics/{stats_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["total_vehicles_spawned"] == 500

        # List all entity types
        resp = await client.get("/api/v1/traffic/zones", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

        resp = await client.get("/api/v1/traffic/routes", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/signals", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/spawn-points", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/density", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/spawn-rules", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/despawn-rules", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/vehicles", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/emergency-vehicles", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/violations", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/events", headers=headers)
        assert resp.status_code == 200

        resp = await client.get("/api/v1/traffic/speed-limits", headers=headers)
        assert resp.status_code == 200

        # Despawn vehicle
        resp = await client.post(
            f"/api/v1/traffic/vehicles/{vehicle_id}/despawn",
            headers=headers,
        )
        assert resp.status_code == 200

        # Verify vehicle is gone
        resp = await client.get(
            f"/api/v1/traffic/vehicles/{vehicle_id}",
            headers=headers,
        )
        assert resp.status_code == 404

        # Delete zone
        resp = await client.delete(
            f"/api/v1/traffic/zones/{zone_id}",
            headers=headers,
        )
        assert resp.status_code == 200
