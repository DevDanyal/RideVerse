"""Pydantic schemas for the Shop and Marketplace system."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------

class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    location: str
    category: str
    is_open: bool = True
    tax_rate: float = Field(ge=0, le=1)
    discount_percent: float = Field(ge=0, le=100)
    min_player_level: int = Field(ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class ShopListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    shops: list[ShopResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Shop Item
# ---------------------------------------------------------------------------

class ShopItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    shop_id: uuid.UUID
    item_id: str
    item_name: str
    item_type: str
    base_price: float = Field(ge=0)
    current_price: float = Field(ge=0)
    stock: int
    is_available: bool = True
    min_player_level: int = Field(ge=1)
    max_purchases_per_player: int = Field(ge=0)


class ShopItemListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: list[ShopItemResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Buy / Sell
# ---------------------------------------------------------------------------

class ShopBuyRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1, le=100)
    idempotency_key: str | None = Field(default=None, max_length=255)


class ShopSellRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=1, le=100)


class ShopTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    shop_id: uuid.UUID
    player_id: uuid.UUID
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: float
    total_price: float
    discount_applied: float
    transaction_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class ShopTransactionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    transactions: list[ShopTransactionResponse] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Restock
# ---------------------------------------------------------------------------

class ShopRestockRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: str = Field(..., min_length=1, max_length=100)
    amount: int = Field(..., ge=1)


class ShopRestockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: str
    item_name: str
    old_stock: int
    new_stock: int
    message: str


# ---------------------------------------------------------------------------
# Discount
# ---------------------------------------------------------------------------

class ShopDiscountRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    discount_percent: float = Field(..., ge=0, le=100)
    item_id: str | None = Field(default=None, max_length=100)


# ---------------------------------------------------------------------------
# Dynamic Pricing
# ---------------------------------------------------------------------------

class ShopPriceUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: str = Field(..., min_length=1, max_length=100)
    new_price: float = Field(..., gt=0)


# ---------------------------------------------------------------------------
# Marketplace
# ---------------------------------------------------------------------------

class MarketplaceListingCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_type: str = Field(..., min_length=1, max_length=50)
    item_id: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)


class MarketplaceListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    seller_id: uuid.UUID
    item_type: str
    item_id: str
    price: float
    listing_status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class MarketplaceListingListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    listings: list[MarketplaceListingResponse] = Field(default_factory=list)
    total: int = 0


class MarketplacePurchaseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    listing_id: uuid.UUID


class MarketplacePurchaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    item_type: str
    item_id: str
    sale_price: float
    message: str


class MarketplaceSearchRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_type: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    sort_by: str = Field(default="created_at", max_length=50)
    sort_order: str = Field(default="desc", max_length=4)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)
