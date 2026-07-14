"""API v1 router — central registration point for all versioned endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import health

api_v1_router = APIRouter(
    tags=["api-v1"],
)

# ── Health ─────────────────────────────────────────────────────────────────────

api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])

# ── Authentication ─────────────────────────────────────────────────────────────

from app.api.v1.auth import router as auth_router  # noqa: E402

api_v1_router.include_router(auth_router)

# ── Player Profile, Statistics, Settings ───────────────────────────────────────

from app.api.v1.players import router as players_router  # noqa: E402

api_v1_router.include_router(players_router)

# ── Characters ─────────────────────────────────────────────────────────────────

from app.api.v1.characters import router as characters_router  # noqa: E402

api_v1_router.include_router(characters_router)

# ── Inventory ──────────────────────────────────────────────────────────────────

from app.api.v1.inventory import router as inventory_router  # noqa: E402

api_v1_router.include_router(inventory_router)

# ── Economy (Wallet) ───────────────────────────────────────────────────────────

from app.api.v1.economy import router as economy_router  # noqa: E402

api_v1_router.include_router(economy_router)

# ── Achievements ───────────────────────────────────────────────────────────────

from app.api.v1.achievements import router as achievements_router  # noqa: E402

api_v1_router.include_router(achievements_router)

# ── Bank Accounts ──────────────────────────────────────────────────────────────

from app.api.v1.bank import router as bank_router  # noqa: E402

api_v1_router.include_router(bank_router)

# ── Vehicles ──────────────────────────────────────────────────────────────────

from app.api.v1.vehicles import router as vehicles_router  # noqa: E402

api_v1_router.include_router(vehicles_router)

# ── Garages ───────────────────────────────────────────────────────────────────

from app.api.v1.garages import router as garages_router  # noqa: E402

api_v1_router.include_router(garages_router)

# ── Bikes (Honda 125 System) ─────────────────────────────────────────────────

from app.api.v1.bikes import router as bikes_router  # noqa: E402

api_v1_router.include_router(bikes_router)

# ── Cars (Car System) ──────────────────────────────────────────────────────

from app.api.v1.cars import router as cars_router  # noqa: E402

api_v1_router.include_router(cars_router)

# ── Weapons (Weapon System) ──────────────────────────────────────────────

from app.api.v1.weapons import router as weapons_router  # noqa: E402

api_v1_router.include_router(weapons_router)
