"""Repository layer for shop and marketplace database operations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.marketplace import MarketplaceListing, MarketplaceSale, ListingStatus
from app.models.shop import Shop, ShopItem, ShopTransaction


class ShopRepository:
    """Data-access layer for Shop, ShopItem, and ShopTransaction models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Shop CRUD ─────────────────────────────────────────────────────────

    async def get_shop_by_id(self, shop_id: uuid.UUID) -> Shop | None:
        stmt = select(Shop).where(
            Shop.id == shop_id,
            Shop.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_shops_by_category(
        self, category: str, skip: int = 0, limit: int = 50
    ) -> list[Shop]:
        stmt = (
            select(Shop)
            .where(
                Shop.category == category,
                Shop.is_deleted.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_shops(self, skip: int = 0, limit: int = 50) -> list[Shop]:
        stmt = (
            select(Shop)
            .where(Shop.is_deleted.is_(False))
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_shop(self, data: dict) -> Shop:
        shop = Shop(**data)
        self._session.add(shop)
        await self._session.flush()
        return shop

    async def update_shop(self, shop_id: uuid.UUID, **kwargs) -> Shop | None:
        stmt = (
            update(Shop)
            .where(Shop.id == shop_id, Shop.is_deleted.is_(False))
            .values(**kwargs)
            .returning(Shop)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── ShopItem CRUD ─────────────────────────────────────────────────────

    async def get_item_by_id(self, item_id: uuid.UUID) -> ShopItem | None:
        stmt = select(ShopItem).where(
            ShopItem.id == item_id,
            ShopItem.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_item_by_shop_and_item_id(
        self, shop_id: uuid.UUID, item_id: str
    ) -> ShopItem | None:
        stmt = select(ShopItem).where(
            ShopItem.shop_id == shop_id,
            ShopItem.item_id == item_id,
            ShopItem.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items_by_shop(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ShopItem]:
        stmt = (
            select(ShopItem)
            .where(
                ShopItem.shop_id == shop_id,
                ShopItem.is_deleted.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_available_items_by_shop(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ShopItem]:
        stmt = (
            select(ShopItem)
            .where(
                ShopItem.shop_id == shop_id,
                ShopItem.is_available.is_(True),
                ShopItem.is_deleted.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_item(self, data: dict) -> ShopItem:
        item = ShopItem(**data)
        self._session.add(item)
        await self._session.flush()
        return item

    async def update_item(self, item_id: uuid.UUID, **kwargs) -> ShopItem | None:
        stmt = (
            update(ShopItem)
            .where(ShopItem.id == item_id, ShopItem.is_deleted.is_(False))
            .values(**kwargs)
            .returning(ShopItem)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def decrement_stock(self, item_id: uuid.UUID, amount: int = 1) -> ShopItem | None:
        stmt = (
            update(ShopItem)
            .where(
                ShopItem.id == item_id,
                ShopItem.is_deleted.is_(False),
                ShopItem.stock >= amount,
            )
            .values(stock=ShopItem.stock - amount)
            .returning(ShopItem)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_stock(self, item_id: uuid.UUID, amount: int = 1) -> ShopItem | None:
        stmt = (
            update(ShopItem)
            .where(ShopItem.id == item_id, ShopItem.is_deleted.is_(False))
            .values(stock=ShopItem.stock + amount)
            .returning(ShopItem)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── ShopTransaction CRUD ──────────────────────────────────────────────

    async def record_transaction(self, data: dict) -> ShopTransaction:
        tx = ShopTransaction(**data)
        self._session.add(tx)
        await self._session.flush()
        return tx

    async def check_idempotency(self, idempotency_key: str) -> ShopTransaction | None:
        stmt = select(ShopTransaction).where(
            ShopTransaction.idempotency_key == idempotency_key
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_transactions_by_player(
        self, player_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ShopTransaction]:
        stmt = (
            select(ShopTransaction)
            .where(
                ShopTransaction.player_id == player_id,
                ShopTransaction.is_deleted.is_(False),
            )
            .order_by(ShopTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_transactions_by_shop(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ShopTransaction]:
        stmt = (
            select(ShopTransaction)
            .where(
                ShopTransaction.shop_id == shop_id,
                ShopTransaction.is_deleted.is_(False),
            )
            .order_by(ShopTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_player_purchases(
        self, player_id: uuid.UUID, item_id: str
    ) -> int:
        stmt = select(func.count(ShopTransaction.id)).where(
            ShopTransaction.player_id == player_id,
            ShopTransaction.item_id == item_id,
            ShopTransaction.transaction_type == "buy",
            ShopTransaction.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0


class MarketplaceRepository:
    """Data-access layer for marketplace listing and sale models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_listing_by_id(self, listing_id: uuid.UUID) -> MarketplaceListing | None:
        stmt = select(MarketplaceListing).where(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_listings(
        self,
        item_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 50,
    ) -> list[MarketplaceListing]:
        filters = [
            MarketplaceListing.listing_status == ListingStatus.ACTIVE,
            MarketplaceListing.is_deleted.is_(False),
        ]
        if item_type:
            filters.append(MarketplaceListing.item_type == item_type)
        if min_price is not None:
            filters.append(MarketplaceListing.price >= min_price)
        if max_price is not None:
            filters.append(MarketplaceListing.price <= max_price)

        sort_col = getattr(MarketplaceListing, sort_by, MarketplaceListing.created_at)
        if sort_order == "asc":
            order = sort_col.asc()
        else:
            order = sort_col.desc()

        stmt = (
            select(MarketplaceListing)
            .where(*filters)
            .order_by(order)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_listings_by_seller(
        self, seller_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[MarketplaceListing]:
        stmt = (
            select(MarketplaceListing)
            .where(
                MarketplaceListing.seller_id == seller_id,
                MarketplaceListing.is_deleted.is_(False),
            )
            .order_by(MarketplaceListing.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_listing(self, data: dict) -> MarketplaceListing:
        listing = MarketplaceListing(**data)
        self._session.add(listing)
        await self._session.flush()
        return listing

    async def update_listing(self, listing_id: uuid.UUID, **kwargs) -> MarketplaceListing | None:
        stmt = (
            update(MarketplaceListing)
            .where(
                MarketplaceListing.id == listing_id,
                MarketplaceListing.is_deleted.is_(False),
            )
            .values(**kwargs)
            .returning(MarketplaceListing)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def record_sale(self, data: dict) -> MarketplaceSale:
        sale = MarketplaceSale(**data)
        self._session.add(sale)
        await self._session.flush()
        return sale

    async def count_active_listings(self, seller_id: uuid.UUID) -> int:
        stmt = select(func.count(MarketplaceListing.id)).where(
            MarketplaceListing.seller_id == seller_id,
            MarketplaceListing.listing_status == ListingStatus.ACTIVE,
            MarketplaceListing.is_deleted.is_(False),
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
