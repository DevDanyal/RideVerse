"""Database seeding script.

Creates initial test data: admin account, sample weapons, and missions.

Usage:
    python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import get_password_hash
from app.database.base import Base
from app.models.auth import AccountStatus, PlayerAccount
from app.models.mission import Mission, MissionDifficulty, MissionType
from app.models.player import Player
from app.models.weapon import Weapon, WeaponType

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_admin_account(session: AsyncSession) -> PlayerAccount:
    account = PlayerAccount(
        id=uuid.uuid4(),
        email="admin@rideverse.com",
        username="admin",
        password_hash=get_password_hash("admin123"),
        email_verified=True,
        account_status=AccountStatus.ACTIVE,
        last_login=datetime.now(timezone.utc),
    )
    session.add(account)
    await session.flush()

    player = Player(
        id=uuid.uuid4(),
        account_id=account.id,
        display_name="Admin",
        level=100,
        experience=999999,
        cash=1000000.0,
        bank_balance=5000000.0,
        reputation=100.0,
    )
    session.add(player)
    return account


async def create_sample_weapons(session: AsyncSession) -> None:
    weapons = [
        Weapon(
            id=uuid.uuid4(),
            weapon_name="Pistol MK2",
            weapon_type=WeaponType.PISTOL,
            damage=25.0,
            range=50.0,
            fire_rate=2.0,
            reload_speed=1.5,
            ammo_capacity=12,
            weight=1.2,
            purchase_price=5000.0,
            sell_price=2500.0,
            required_level=1,
        ),
        Weapon(
            id=uuid.uuid4(),
            weapon_name="AK-47",
            weapon_type=WeaponType.ASSAULT_RIFLE,
            damage=35.0,
            range=80.0,
            fire_rate=8.0,
            reload_speed=2.0,
            ammo_capacity=30,
            weight=3.5,
            purchase_price=25000.0,
            sell_price=12500.0,
            required_level=10,
        ),
        Weapon(
            id=uuid.uuid4(),
            weapon_name="Sniper Rifle",
            weapon_type=WeaponType.SNIPER_RIFLE,
            damage=80.0,
            range=200.0,
            fire_rate=0.5,
            reload_speed=3.0,
            ammo_capacity=5,
            weight=5.0,
            purchase_price=50000.0,
            sell_price=25000.0,
            required_level=20,
        ),
        Weapon(
            id=uuid.uuid4(),
            weapon_name="Combat Knife",
            weapon_type=WeaponType.MELEE,
            damage=40.0,
            range=2.0,
            fire_rate=3.0,
            reload_speed=0.0,
            ammo_capacity=0,
            weight=0.8,
            purchase_price=1000.0,
            sell_price=500.0,
            required_level=1,
        ),
        Weapon(
            id=uuid.uuid4(),
            weapon_name="Shotgun",
            weapon_type=WeaponType.SHOTGUN,
            damage=60.0,
            range=15.0,
            fire_rate=1.0,
            reload_speed=2.5,
            ammo_capacity=8,
            weight=4.0,
            purchase_price=15000.0,
            sell_price=7500.0,
            required_level=5,
        ),
    ]
    session.add_all(weapons)


async def create_sample_missions(session: AsyncSession) -> None:
    missions = [
        Mission(
            id=uuid.uuid4(),
            mission_name="First Ride",
            mission_type=MissionType.TUTORIAL,
            difficulty=MissionDifficulty.EASY,
            minimum_level=1,
            reward_cash=500.0,
            reward_experience=100,
            estimated_time=300,
            repeatable=False,
        ),
        Mission(
            id=uuid.uuid4(),
            mission_name="Pizza Delivery",
            mission_type=MissionType.DELIVERY,
            difficulty=MissionDifficulty.EASY,
            minimum_level=1,
            reward_cash=200.0,
            reward_experience=50,
            estimated_time=180,
            repeatable=True,
        ),
        Mission(
            id=uuid.uuid4(),
            mission_name="Street Race: Downtown",
            mission_type=MissionType.RACING,
            difficulty=MissionDifficulty.NORMAL,
            minimum_level=5,
            reward_cash=5000.0,
            reward_experience=500,
            estimated_time=120,
            repeatable=True,
        ),
        Mission(
            id=uuid.uuid4(),
            mission_name="The Big Heist",
            mission_type=MissionType.STORY,
            difficulty=MissionDifficulty.HARD,
            minimum_level=20,
            reward_cash=100000.0,
            reward_experience=5000,
            estimated_time=1800,
            repeatable=False,
        ),
    ]
    session.add_all(missions)


async def main() -> None:
    async with async_session() as session:
        async with session.begin():
            await create_admin_account(session)
            await create_sample_weapons(session)
            await create_sample_missions(session)
        await session.commit()

    print("Database seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
