"""Business logic for the Shop & Marketplace system."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.economy import TransactionType
from app.models.marketplace import ListingStatus, MarketplaceItemType
from app.models.shop import ShopTransactionType
from app.repositories.economy import EconomyRepository
from app.repositories.player import PlayerRepository
from app.repositories.shop import MarketplaceRepository, ShopRepository

logger = logging.getLogger(__name__)

MAX_MARKETPLACE_LISTINGS = 10
MARKETPLACE_FEE_PERCENT = 0.05
SELL_PRICE_FACTOR = 0.5


# ── Helper serializers ──────────────────────────────────────────────────


def _shop_to_dict(shop) -> dict:
    return {
        "id": shop.id,
        "name": shop.name,
        "description": shop.description,
        "location": shop.location,
        "category": shop.category,
        "owner_player_id": shop.owner_player_id,
        "is_open": shop.is_open,
        "tax_rate": shop.tax_rate,
        "discount_percent": shop.discount_percent,
        "min_player_level": shop.min_player_level,
        "created_at": shop.created_at,
        "updated_at": shop.updated_at,
    }


def _shop_item_to_dict(item) -> dict:
    return {
        "id": item.id,
        "shop_id": item.shop_id,
        "item_id": item.item_id,
        "item_name": item.item_name,
        "item_type": item.item_type,
        "base_price": item.base_price,
        "current_price": item.current_price,
        "stock": item.stock,
        "max_stock": item.max_stock,
        "restock_amount": item.restock_amount,
        "restock_interval_hours": item.restock_interval_hours,
        "last_restock": item.last_restock,
        "is_available": item.is_available,
        "min_player_level": item.min_player_level,
        "max_purchases_per_player": item.max_purchases_per_player,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def _transaction_to_dict(tx) -> dict:
    return {
        "id": tx.id,
        "shop_id": tx.shop_id,
        "player_id": tx.player_id,
        "item_id": tx.item_id,
        "item_name": tx.item_name,
        "quantity": tx.quantity,
        "price_per_unit": tx.price_per_unit,
        "total_price": tx.total_price,
        "discount_applied": tx.discount_applied,
        "transaction_type": tx.transaction_type,
        "idempotency_key": tx.idempotency_key,
        "created_at": tx.created_at,
        "updated_at": tx.updated_at,
    }


def _listing_to_dict(listing) -> dict:
    return {
        "id": listing.id,
        "seller_id": listing.seller_id,
        "item_type": listing.item_type,
        "item_id": listing.item_id,
        "price": listing.price,
        "listing_status": listing.listing_status,
        "created_at": listing.created_at,
        "updated_at": listing.updated_at,
    }


def _sale_to_dict(sale) -> dict:
    return {
        "id": sale.id,
        "listing_id": sale.listing_id,
        "buyer_id": sale.buyer_id,
        "seller_id": sale.seller_id,
        "sale_price": sale.sale_price,
        "sold_at": sale.sold_at,
        "created_at": sale.created_at,
        "updated_at": sale.updated_at,
    }


# ═══════════════════════════════════════════════════════════════════════
# ShopService
# ═══════════════════════════════════════════════════════════════════════


class ShopService:
    """Business logic for NPC-owned shop interactions."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.shop_repo = ShopRepository(session)
        self.economy_repo = EconomyRepository(session)
        self.player_repo = PlayerRepository(session)
        self.marketplace_repo = MarketplaceRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _get_wallet_or_raise(self, player_id: uuid.UUID):
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        return wallet

    # ── List shops ──────────────────────────────────────────────────────

    async def get_shops(
        self,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        if category:
            shops = await self.shop_repo.get_shops_by_category(category, skip, limit)
        else:
            shops = await self.shop_repo.get_all_shops(skip, limit)
        return [_shop_to_dict(s) for s in shops]

    # ── Get shop ────────────────────────────────────────────────────────

    async def get_shop(self, shop_id: uuid.UUID) -> dict:
        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")
        return _shop_to_dict(shop)

    # ── List shop items ─────────────────────────────────────────────────

    async def get_shop_items(
        self, shop_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[dict]:
        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")
        items = await self.shop_repo.get_available_items_by_shop(shop_id, skip, limit)
        return [_shop_item_to_dict(i) for i in items]

    # ── Buy item ────────────────────────────────────────────────────────

    async def buy_item(
        self,
        account_id: uuid.UUID,
        shop_id: uuid.UUID,
        item_id: str,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> dict:
        if quantity <= 0:
            raise ValidationError("Quantity must be at least 1")

        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)

        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")
        if not shop.is_open:
            raise ValidationError("Shop is currently closed")

        if player.level < shop.min_player_level:
            raise ValidationError(
                f"Player level {player.level} does not meet shop "
                f"minimum level {shop.min_player_level}"
            )

        item = await self.shop_repo.get_item_by_shop_and_item_id(shop_id, item_id)
        if item is None:
            raise NotFoundError("Item not found in this shop")
        if not item.is_available:
            raise ValidationError("Item is currently unavailable")

        if player.level < item.min_player_level:
            raise ValidationError(
                f"Player level {player.level} does not meet item "
                f"minimum level {item.min_player_level}"
            )

        if item.stock != -1 and item.stock < quantity:
            raise ValidationError(
                f"Insufficient stock. Available: {item.stock}, requested: {quantity}"
            )

        if idempotency_key:
            existing = await self.shop_repo.check_idempotency(idempotency_key)
            if existing:
                raise ConflictError("This transaction has already been processed")

        if item.max_purchases_per_player > 0:
            total_purchased = await self.shop_repo.count_player_purchases(
                player.id, item.item_id
            )
            if total_purchased + quantity > item.max_purchases_per_player:
                raise ValidationError(
                    f"Purchase limit exceeded. Already bought: {total_purchased}, "
                    f"max allowed: {item.max_purchases_per_player}"
                )

        price_per_unit = item.current_price * quantity
        discount_amount = price_per_unit * (shop.discount_percent / 100)
        discounted_price = price_per_unit - discount_amount
        tax_amount = discounted_price * shop.tax_rate
        total_cost = round(discounted_price + tax_amount, 2)

        if wallet.cash < total_cost:
            raise ValidationError(
                f"Insufficient cash. Need: ${total_cost}, have: ${wallet.cash}"
            )

        balance_before = wallet.cash
        new_cash = round(wallet.cash - total_cost, 2)
        await self.economy_repo.update_wallet(
            player.id,
            cash=new_cash,
            last_transaction=datetime.now(timezone.utc),
            total_spent=wallet.total_spent + total_cost,
        )

        if item.stock != -1:
            updated_item = await self.shop_repo.decrement_stock(item.id, quantity)
            if updated_item is None:
                raise ValidationError("Failed to decrement stock — concurrent purchase")

        tx_data = {
            "shop_id": shop.id,
            "player_id": player.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "quantity": quantity,
            "price_per_unit": item.current_price,
            "total_price": total_cost,
            "discount_applied": discount_amount,
            "transaction_type": ShopTransactionType.BUY,
            "idempotency_key": idempotency_key,
        }
        shop_tx = await self.shop_repo.record_transaction(tx_data)

        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.SPEND,
            "amount": total_cost,
            "balance_before": balance_before,
            "balance_after": new_cash,
            "reference": f"shop_buy:{shop.id}:{item.item_id}",
            "description": f"Bought {quantity}x {item.item_name} from {shop.name}",
            "idempotency_key": idempotency_key,
        })

        logger.info(
            "Player %s bought %dx %s from shop %s for $%s",
            player.id, quantity, item.item_name, shop.id, total_cost,
        )
        return {
            "transaction_id": shop_tx.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "quantity": quantity,
            "price_per_unit": item.current_price,
            "discount_applied": discount_amount,
            "tax": tax_amount,
            "total_cost": total_cost,
            "new_cash_balance": new_cash,
            "shop_name": shop.name,
        }

    # ── Sell item ───────────────────────────────────────────────────────

    async def sell_item(
        self,
        account_id: uuid.UUID,
        shop_id: uuid.UUID,
        item_id: str,
        quantity: int,
    ) -> dict:
        if quantity <= 0:
            raise ValidationError("Quantity must be at least 1")

        player = await self._get_player_or_raise(account_id)
        wallet = await self._get_wallet_or_raise(player.id)

        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")
        if not shop.is_open:
            raise ValidationError("Shop is currently closed")

        item = await self.shop_repo.get_item_by_shop_and_item_id(shop_id, item_id)
        if item is None:
            raise NotFoundError("Item not found in this shop")

        sell_price_per_unit = item.base_price * SELL_PRICE_FACTOR
        total_earnings = round(sell_price_per_unit * quantity, 2)

        if wallet.cash + total_earnings > wallet.max_cash:
            raise ValidationError("Cash limit would be exceeded")

        balance_before = wallet.cash
        new_cash = round(wallet.cash + total_earnings, 2)
        await self.economy_repo.update_wallet(
            player.id,
            cash=new_cash,
            last_transaction=datetime.now(timezone.utc),
            total_earned=wallet.total_earned + total_earnings,
        )

        if item.stock != -1:
            await self.shop_repo.increment_stock(item.id, quantity)

        tx_data = {
            "shop_id": shop.id,
            "player_id": player.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "quantity": quantity,
            "price_per_unit": sell_price_per_unit,
            "total_price": total_earnings,
            "discount_applied": 0.0,
            "transaction_type": ShopTransactionType.SELL,
        }
        shop_tx = await self.shop_repo.record_transaction(tx_data)

        await self.economy_repo.record_transaction({
            "player_id": player.id,
            "transaction_type": TransactionType.SALE,
            "amount": total_earnings,
            "balance_before": balance_before,
            "balance_after": new_cash,
            "reference": f"shop_sell:{shop.id}:{item.item_id}",
            "description": f"Sold {quantity}x {item.item_name} to {shop.name}",
        })

        logger.info(
            "Player %s sold %dx %s to shop %s for $%s",
            player.id, quantity, item.item_name, shop.id, total_earnings,
        )
        return {
            "transaction_id": shop_tx.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "quantity": quantity,
            "price_per_unit": sell_price_per_unit,
            "total_earnings": total_earnings,
            "new_cash_balance": new_cash,
            "shop_name": shop.name,
        }

    # ── Player transaction history ──────────────────────────────────────

    async def get_player_transactions(
        self, account_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[dict]:
        player = await self._get_player_or_raise(account_id)
        txs = await self.shop_repo.get_transactions_by_player(player.id, skip, limit)
        return [_transaction_to_dict(t) for t in txs]

    # ── Restock item ────────────────────────────────────────────────────

    async def restock_item(
        self, shop_id: uuid.UUID, item_id: str, amount: int
    ) -> dict:
        if amount <= 0:
            raise ValidationError("Restock amount must be positive")

        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")

        item = await self.shop_repo.get_item_by_shop_and_item_id(shop_id, item_id)
        if item is None:
            raise NotFoundError("Item not found in this shop")

        if item.max_stock != -1 and item.stock + amount > item.max_stock:
            raise ValidationError(
                f"Restock would exceed max stock ({item.max_stock}). "
                f"Current: {item.stock}, requested: {amount}"
            )

        old_stock = item.stock
        updated = await self.shop_repo.increment_stock(item.id, amount)
        if updated is None:
            raise ValidationError("Failed to restock item")

        now = datetime.now(timezone.utc)
        await self.shop_repo.update_item(item.id, last_restock=now)

        logger.info(
            "Restocked %dx %s in shop %s (new stock: %d)",
            amount, item.item_name, shop.id, updated.stock,
        )
        return {
            "item_id": item.item_id,
            "item_name": item.item_name,
            "old_stock": old_stock,
            "new_stock": updated.stock,
            "message": f"Successfully restocked {amount}x {item.item_name}",
        }

    # ── Apply discount ──────────────────────────────────────────────────

    async def apply_discount(
        self,
        shop_id: uuid.UUID,
        discount_percent: float,
        item_id: str | None = None,
    ) -> dict:
        if discount_percent < 0 or discount_percent > 100:
            raise ValidationError("Discount percent must be between 0 and 100")

        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")

        if item_id:
            item = await self.shop_repo.get_item_by_shop_and_item_id(shop_id, item_id)
            if item is None:
                raise NotFoundError("Item not found in this shop")
            new_price = round(item.base_price * (1 - discount_percent / 100), 2)
            await self.shop_repo.update_item(item.id, current_price=new_price)
            logger.info(
                "Applied %s%% discount to item %s in shop %s (new price: $%s)",
                discount_percent, item.item_name, shop.id, new_price,
            )
            return {
                "item_id": item.item_id,
                "item_name": item.item_name,
                "discount_percent": discount_percent,
                "new_price": new_price,
            }
        else:
            await self.shop_repo.update_shop(shop.id, discount_percent=discount_percent)
            logger.info(
                "Applied %s%% discount to shop %s", discount_percent, shop.id,
            )
            return {
                "shop_id": shop.id,
                "shop_name": shop.name,
                "discount_percent": discount_percent,
            }

    # ── Dynamic pricing ─────────────────────────────────────────────────

    async def update_price(
        self, shop_id: uuid.UUID, item_id: str, new_price: float
    ) -> dict:
        if new_price < 0:
            raise ValidationError("Price cannot be negative")

        shop = await self.shop_repo.get_shop_by_id(shop_id)
        if shop is None:
            raise NotFoundError("Shop not found")

        item = await self.shop_repo.get_item_by_shop_and_item_id(shop_id, item_id)
        if item is None:
            raise NotFoundError("Item not found in this shop")

        old_price = item.current_price
        await self.shop_repo.update_item(item.id, current_price=new_price)

        logger.info(
            "Updated price of item %s in shop %s: $%s -> $%s",
            item.item_name, shop.id, old_price, new_price,
        )
        return {
            "item_id": item.item_id,
            "item_name": item.item_name,
            "old_price": old_price,
            "new_price": new_price,
            "shop_name": shop.name,
        }


# ═══════════════════════════════════════════════════════════════════════
# MarketplaceService
# ═══════════════════════════════════════════════════════════════════════


class MarketplaceService:
    """Business logic for the player-to-player marketplace."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.shop_repo = ShopRepository(session)
        self.economy_repo = EconomyRepository(session)
        self.player_repo = PlayerRepository(session)
        self.marketplace_repo = MarketplaceRepository(session)

    async def _get_player_or_raise(self, account_id: uuid.UUID):
        player = await self.player_repo.get_by_account_id(account_id)
        if player is None:
            raise NotFoundError("Player profile not found")
        return player

    async def _get_wallet_or_raise(self, player_id: uuid.UUID):
        wallet = await self.economy_repo.get_wallet(player_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        return wallet

    # ── Create listing ──────────────────────────────────────────────────

    async def create_listing(
        self,
        account_id: uuid.UUID,
        item_type: str,
        item_id: str,
        price: float,
    ) -> dict:
        if price <= 0:
            raise ValidationError("Listing price must be positive")

        player = await self._get_player_or_raise(account_id)

        try:
            MarketplaceItemType(item_type)
        except ValueError:
            raise ValidationError(
                f"Invalid item type '{item_type}'. "
                f"Valid types: {[t.value for t in MarketplaceItemType]}"
            )

        active_count = await self.marketplace_repo.count_active_listings(player.id)
        if active_count >= MAX_MARKETPLACE_LISTINGS:
            raise ValidationError(
                f"Maximum active listings ({MAX_MARKETPLACE_LISTINGS}) reached"
            )

        listing = await self.marketplace_repo.create_listing({
            "seller_id": player.id,
            "item_type": item_type,
            "item_id": item_id,
            "price": price,
            "listing_status": ListingStatus.ACTIVE,
        })

        logger.info(
            "Player %s created marketplace listing %s (%s:%s) for $%s",
            player.id, listing.id, item_type, item_id, price,
        )
        return _listing_to_dict(listing)

    # ── Purchase listing ────────────────────────────────────────────────

    async def purchase_listing(
        self,
        account_id: uuid.UUID,
        listing_id: uuid.UUID,
    ) -> dict:
        buyer = await self._get_player_or_raise(account_id)
        buyer_wallet = await self._get_wallet_or_raise(buyer.id)

        listing = await self.marketplace_repo.get_listing_by_id(listing_id)
        if listing is None:
            raise NotFoundError("Listing not found")
        if listing.listing_status != ListingStatus.ACTIVE:
            raise ValidationError("Listing is no longer available")
        if listing.seller_id == buyer.id:
            raise ValidationError("Cannot purchase your own listing")

        if buyer_wallet.cash < listing.price:
            raise ValidationError(
                f"Insufficient cash. Need: ${listing.price}, have: ${buyer_wallet.cash}"
            )

        seller_wallet = await self.economy_repo.get_wallet(listing.seller_id)
        if not seller_wallet:
            raise NotFoundError("Seller wallet not found")

        fee = round(listing.price * MARKETPLACE_FEE_PERCENT, 2)
        seller_proceeds = round(listing.price - fee, 2)

        buyer_balance_before = buyer_wallet.cash
        new_buyer_cash = round(buyer_wallet.cash - listing.price, 2)
        await self.economy_repo.update_wallet(
            buyer.id,
            cash=new_buyer_cash,
            last_transaction=datetime.now(timezone.utc),
            total_spent=buyer_wallet.total_spent + listing.price,
        )

        seller_balance_before = seller_wallet.cash
        new_seller_cash = round(seller_wallet.cash + seller_proceeds, 2)
        if new_seller_cash > seller_wallet.max_cash:
            raise ValidationError("Seller cash limit would be exceeded")
        await self.economy_repo.update_wallet(
            listing.seller_id,
            cash=new_seller_cash,
            last_transaction=datetime.now(timezone.utc),
            total_earned=seller_wallet.total_earned + seller_proceeds,
        )

        await self.marketplace_repo.update_listing(
            listing.id, listing_status=ListingStatus.SOLD,
        )

        now = datetime.now(timezone.utc)
        sale = await self.marketplace_repo.record_sale({
            "listing_id": listing.id,
            "buyer_id": buyer.id,
            "seller_id": listing.seller_id,
            "sale_price": listing.price,
            "sold_at": now,
        })

        await self.economy_repo.record_transaction({
            "player_id": buyer.id,
            "transaction_type": TransactionType.SPEND,
            "amount": listing.price,
            "balance_before": buyer_balance_before,
            "balance_after": new_buyer_cash,
            "source_player_id": buyer.id,
            "destination_player_id": listing.seller_id,
            "reference": f"marketplace_buy:{listing.id}",
            "description": f"Marketplace purchase from seller {listing.seller_id}",
        })
        await self.economy_repo.record_transaction({
            "player_id": listing.seller_id,
            "transaction_type": TransactionType.SALE,
            "amount": seller_proceeds,
            "balance_before": seller_balance_before,
            "balance_after": new_seller_cash,
            "source_player_id": buyer.id,
            "destination_player_id": listing.seller_id,
            "reference": f"marketplace_sell:{listing.id}",
            "description": f"Marketplace sale to buyer {buyer.id} (fee: ${fee})",
        })

        logger.info(
            "Player %s purchased listing %s from player %s for $%s (fee: $%s)",
            buyer.id, listing.id, listing.seller_id, listing.price, fee,
        )
        return {
            "sale_id": sale.id,
            "listing_id": listing.id,
            "buyer_id": buyer.id,
            "seller_id": listing.seller_id,
            "item_type": listing.item_type,
            "item_id": listing.item_id,
            "sale_price": listing.price,
            "marketplace_fee": fee,
            "seller_proceeds": seller_proceeds,
            "buyer_new_cash": new_buyer_cash,
            "seller_new_cash": new_seller_cash,
            "message": "Purchase successful",
        }

    # ── Cancel listing ──────────────────────────────────────────────────

    async def cancel_listing(
        self,
        account_id: uuid.UUID,
        listing_id: uuid.UUID,
    ) -> dict:
        player = await self._get_player_or_raise(account_id)

        listing = await self.marketplace_repo.get_listing_by_id(listing_id)
        if listing is None:
            raise NotFoundError("Listing not found")
        if listing.seller_id != player.id:
            raise ConflictError("You can only cancel your own listings")
        if listing.listing_status != ListingStatus.ACTIVE:
            raise ValidationError("Only active listings can be cancelled")

        updated = await self.marketplace_repo.update_listing(
            listing.id, listing_status=ListingStatus.CANCELLED,
        )

        logger.info("Player %s cancelled listing %s", player.id, listing.id)
        result = _listing_to_dict(updated)
        result["message"] = "Listing cancelled successfully"
        return result

    # ── Search / filter active listings ─────────────────────────────────

    async def get_active_listings(
        self,
        item_type: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        listings = await self.marketplace_repo.get_active_listings(
            item_type=item_type,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )
        return [_listing_to_dict(l) for l in listings]

    # ── My listings ─────────────────────────────────────────────────────

    async def get_my_listings(
        self, account_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[dict]:
        player = await self._get_player_or_raise(account_id)
        listings = await self.marketplace_repo.get_listings_by_seller(
            player.id, skip, limit,
        )
        return [_listing_to_dict(l) for l in listings]

    # ── Single listing ──────────────────────────────────────────────────

    async def get_listing(self, listing_id: uuid.UUID) -> dict:
        listing = await self.marketplace_repo.get_listing_by_id(listing_id)
        if listing is None:
            raise NotFoundError("Listing not found")
        return _listing_to_dict(listing)
