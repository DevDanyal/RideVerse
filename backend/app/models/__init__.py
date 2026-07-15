"""Models package — import all models so SQLAlchemy can discover them for migrations."""
from __future__ import annotations

# Auth & Sessions
from app.models.auth import AccountRole, AccountStatus, PlayerAccount, PlayerSession, RefreshToken

# Player
from app.models.player import Player, PlayerSettings, PlayerStatistics

# Character
from app.models.character import Character, CharacterAppearance

# Vehicles
from app.models.vehicle import Vehicle, VehicleType
from app.models.bike import Bike
from app.models.bike_variant import BikeVariant
from app.models.bike_insurance import BikeInsurance
from app.models.car import Car
from app.models.car_variant import CarVariant
from app.models.car_insurance import CarInsurance
from app.models.repair_history import RepairHistory
from app.models.fuel import FuelStation, FuelTransaction

# Inventory
from app.models.inventory import Inventory, InventoryHistory, InventoryItem, InventoryAction, ItemRarity, ItemType

# Weapons
from app.models.weapon import (
    AmmoType,
    PlayerWeapon,
    Weapon,
    WeaponAmmunition,
    WeaponAttachment,
    WeaponType,
)

# Economy
from app.models.economy import ATM, DailyReward, Transaction, Wallet, TransactionType

# Missions
from app.models.mission import (
    Mission,
    MissionCategory,
    MissionCooldown,
    MissionDifficulty,
    MissionHistory,
    MissionStatistics,
    MissionStatus,
    ObjectiveType,
    MissionObjective,
    PlayerMission,
    PlayerObjectiveProgress,
)

# Garage
from app.models.garage import Garage, GarageSlot

# Bank
from app.models.bank import BankAccount, AccountType

# Property
from app.models.property import Property, PropertyType

# Business
from app.models.business import Business, BusinessIncome, BusinessType

# Marketplace
from app.models.marketplace import MarketplaceListing, MarketplaceSale

# Shops
from app.models.shop import Shop, ShopCategory, ShopItem, ShopTransaction, ShopTransactionType

# Social
from app.models.friend import Friend, FriendStatus
from app.models.club import Club, ClubMember, ClubMemberRole

# Communication
from app.models.chat import ChatChannel, ChatMessage, ChannelType
from app.models.notification import Notification, NotificationType

# Achievements & Leaderboards
from app.models.achievement import Achievement, PlayerAchievement
from app.models.leaderboard import Leaderboard, LeaderboardEntry, LeaderboardType

# World
from app.models.police import CrimeHistory, PoliceRecord
from app.models.traffic import TrafficEvent, TrafficSeverity
from app.models.npc import Npc, NpcDialogue, NpcType

# Analytics & Logging
from app.models.analytics import AnalyticsEvent
from app.models.log import AuditLog, ErrorLog, LogSeverity

__all__ = [
    # Auth
    "AccountRole",
    "AccountStatus",
    "PlayerAccount",
    "PlayerSession",
    "RefreshToken",
    # Player
    "Player",
    "PlayerSettings",
    "PlayerStatistics",
    # Character
    "Character",
    "CharacterAppearance",
    # Vehicles
    "Vehicle",
    "VehicleType",
    "Bike",
    "BikeVariant",
    "BikeInsurance",
    "Car",
    "CarVariant",
    "CarInsurance",
    "RepairHistory",
    "FuelStation",
    "FuelTransaction",
    # Inventory
    "Inventory",
    "InventoryItem",
    "InventoryHistory",
    "ItemType",
    "ItemRarity",
    "InventoryAction",
    # Weapons
    "Weapon",
    "WeaponType",
    "AmmoType",
    "PlayerWeapon",
    "WeaponAttachment",
    "WeaponAmmunition",
    # Economy
    "Wallet",
    "Transaction",
    "TransactionType",
    "DailyReward",
    "ATM",
    # Missions
    "Mission",
    "MissionCategory",
    "MissionDifficulty",
    "MissionStatus",
    "MissionObjective",
    "ObjectiveType",
    "PlayerMission",
    "PlayerObjectiveProgress",
    "MissionHistory",
    "MissionCooldown",
    "MissionStatistics",
    # Garage
    "Garage",
    "GarageSlot",
    # Bank
    "BankAccount",
    "AccountType",
    # Property
    "Property",
    "PropertyType",
    # Business
    "Business",
    "BusinessIncome",
    "BusinessType",
    # Marketplace
    "MarketplaceListing",
    "MarketplaceSale",
    # Shops
    "Shop",
    "ShopCategory",
    "ShopItem",
    "ShopTransaction",
    "ShopTransactionType",
    # Social
    "Friend",
    "FriendStatus",
    "Club",
    "ClubMember",
    "ClubMemberRole",
    # Communication
    "ChatChannel",
    "ChatMessage",
    "ChannelType",
    "Notification",
    "NotificationType",
    # Achievements & Leaderboards
    "Achievement",
    "PlayerAchievement",
    "Leaderboard",
    "LeaderboardEntry",
    "LeaderboardType",
    # World
    "PoliceRecord",
    "CrimeHistory",
    "TrafficEvent",
    "TrafficSeverity",
    "Npc",
    "NpcDialogue",
    "NpcType",
    # Analytics & Logging
    "AnalyticsEvent",
    "AuditLog",
    "ErrorLog",
    "LogSeverity",
]
