"""TASK 4 — Core Player System: Player, Characters, Inventory, Economy, Achievements, Bank.

Revision ID: 004_player_system
Revises: 003_auth_system
Create Date: 2026-07-14

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_player_system"
down_revision: Union[str, None] = "003_auth_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Players ────────────────────────────────────────────────────────────────
    op.create_table(
        "players",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("player_accounts.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column("level", sa.Integer, server_default="1", nullable=False),
        sa.Column("experience", sa.Integer, server_default="0", nullable=False),
        sa.Column("cash", sa.Float, server_default="1000.0", nullable=False),
        sa.Column("bank_balance", sa.Float, server_default="0.0", nullable=False),
        sa.Column("reputation", sa.Float, server_default="0.0", nullable=False),
        sa.Column("health", sa.Integer, server_default="100", nullable=False),
        sa.Column("stamina", sa.Integer, server_default="100", nullable=False),
        sa.Column("energy", sa.Integer, server_default="100", nullable=False),
        sa.Column("wanted_level", sa.Integer, server_default="0", nullable=False),
        sa.Column("current_server", sa.String(100), nullable=True),
        sa.Column("current_region", sa.String(100), nullable=True),
        comment="Core player profile data",
    )

    # ── Player Statistics ───────────────────────────────────────────────────────
    op.create_table(
        "player_statistics",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("total_play_time", sa.Float, server_default="0.0", nullable=False),
        sa.Column("distance_walked", sa.Float, server_default="0.0", nullable=False),
        sa.Column("distance_driven", sa.Float, server_default="0.0", nullable=False),
        sa.Column("missions_completed", sa.Integer, server_default="0", nullable=False),
        sa.Column("races_won", sa.Integer, server_default="0", nullable=False),
        sa.Column("vehicles_owned", sa.Integer, server_default="0", nullable=False),
        sa.Column("weapons_owned", sa.Integer, server_default="0", nullable=False),
        sa.Column("money_earned", sa.Float, server_default="0.0", nullable=False),
        sa.Column("money_spent", sa.Float, server_default="0.0", nullable=False),
        sa.Column("highest_speed", sa.Float, server_default="0.0", nullable=False),
        sa.Column("highest_wheelie_score", sa.Float, server_default="0.0", nullable=False),
        sa.Column("daily_login_streak", sa.Integer, server_default="0", nullable=False),
    )

    # ── Player Settings ─────────────────────────────────────────────────────────
    op.create_table(
        "player_settings",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("language", sa.String(10), server_default="en", nullable=False),
        sa.Column("graphics_quality", sa.String(20), server_default="medium", nullable=False),
        sa.Column("audio_volume", sa.Integer, server_default="80", nullable=False),
        sa.Column("music_volume", sa.Integer, server_default="60", nullable=False),
        sa.Column("voice_chat", sa.Boolean, server_default=sa.text("1"), nullable=False),
        sa.Column("notifications", sa.Boolean, server_default=sa.text("1"), nullable=False),
        sa.Column("control_layout", sa.String(50), server_default="default", nullable=False),
        sa.Column("camera_mode", sa.String(50), server_default="third_person", nullable=False),
        sa.Column("theme", sa.String(20), server_default="dark", nullable=False),
    )

    # ── Characters ──────────────────────────────────────────────────────────────
    op.create_table(
        "characters",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("height", sa.Float, nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("current_health", sa.Integer, server_default="100", nullable=False),
        sa.Column("current_stamina", sa.Integer, server_default="100", nullable=False),
        sa.Column("current_hunger", sa.Integer, server_default="100", nullable=False),
        sa.Column("current_thirst", sa.Integer, server_default="100", nullable=False),
        sa.Column("spawn_location", sa.String(100), nullable=True),
    )

    # ── Character Appearances ───────────────────────────────────────────────────
    op.create_table(
        "character_appearances",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("hair_style", sa.String(50), nullable=True),
        sa.Column("hair_color", sa.String(20), nullable=True),
        sa.Column("eye_color", sa.String(20), nullable=True),
        sa.Column("skin_tone", sa.String(20), nullable=True),
        sa.Column("face_type", sa.String(50), nullable=True),
        sa.Column("beard_style", sa.String(50), nullable=True),
        sa.Column("tattoos", postgresql.JSON, nullable=True),
        sa.Column("glasses", sa.Boolean, server_default=sa.text("0"), nullable=False),
        sa.Column("mask", sa.Boolean, server_default=sa.text("0"), nullable=False),
        sa.Column("helmet", sa.Boolean, server_default=sa.text("0"), nullable=False),
    )

    # ── Inventories ─────────────────────────────────────────────────────────────
    op.create_table(
        "inventories",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("max_slots", sa.Integer, server_default="50", nullable=False),
        sa.Column("used_slots", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_weight", sa.Float, server_default="0.0", nullable=False),
    )

    # ── Inventory Items ─────────────────────────────────────────────────────────
    op.create_table(
        "inventory_items",
        sa.Column("inventory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("item_id", sa.String(100), nullable=False),
        sa.Column("item_name", sa.String(100), nullable=False),
        sa.Column("item_type", sa.String(20), nullable=False, index=True),
        sa.Column("quantity", sa.Integer, server_default="1", nullable=False),
        sa.Column("rarity", sa.String(20), nullable=False, index=True),
        sa.Column("weight", sa.Float, server_default="0.0", nullable=False),
        sa.Column("durability", sa.Float, server_default="100.0", nullable=False),
        sa.Column("stackable", sa.Boolean, nullable=False),
        sa.Column("equipped", sa.Boolean, server_default=sa.text("0"), nullable=False),
        comment="Individual items within a player's inventory",
    )

    # ── Inventory History ───────────────────────────────────────────────────────
    op.create_table(
        "inventory_history",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("item_id", sa.String(100), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("destination", sa.String(255), nullable=True),
        comment="Audit trail for inventory changes",
    )

    # ── Wallets ─────────────────────────────────────────────────────────────────
    op.create_table(
        "wallets",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False, index=True),
        sa.Column("cash", sa.Float, server_default="1000.0", nullable=False),
        sa.Column("bank_balance", sa.Float, server_default="0.0", nullable=False),
        sa.Column("last_transaction", sa.DateTime(timezone=True), nullable=True),
    )

    # ── Transactions ────────────────────────────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("transaction_type", sa.String(20), nullable=False, index=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("balance_before", sa.Float, nullable=False),
        sa.Column("balance_after", sa.Float, nullable=False),
        sa.Column("reference", sa.String(255), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
    )

    # ── Daily Rewards ───────────────────────────────────────────────────────────
    op.create_table(
        "daily_rewards",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("day_number", sa.Integer, nullable=False),
        sa.Column("reward_amount", sa.Float, nullable=False),
        sa.Column("claimed", sa.Boolean, server_default=sa.text("0"), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── Bank Accounts ───────────────────────────────────────────────────────────
    op.create_table(
        "bank_accounts",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("account_number", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("account_type", sa.String(20), server_default="checking", nullable=False),
        sa.Column("balance", sa.Float, server_default="0.0", nullable=False),
        sa.Column("interest_rate", sa.Float, server_default="0.01", nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("1"), nullable=False),
        comment="Bank accounts for players",
    )

    # ── Achievements ────────────────────────────────────────────────────────────
    op.create_table(
        "achievements",
        sa.Column("achievement_name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("reward", postgresql.JSON, nullable=True),
    )

    # ── Player Achievements ─────────────────────────────────────────────────────
    op.create_table(
        "player_achievements",
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("achievement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        comment="Achievements unlocked by players",
    )


def downgrade() -> None:
    op.drop_table("player_achievements")
    op.drop_table("achievements")
    op.drop_table("bank_accounts")
    op.drop_table("daily_rewards")
    op.drop_table("transactions")
    op.drop_table("wallets")
    op.drop_table("inventory_history")
    op.drop_table("inventory_items")
    op.drop_table("inventories")
    op.drop_table("character_appearances")
    op.drop_table("characters")
    op.drop_table("player_settings")
    op.drop_table("player_statistics")
    op.drop_table("players")
