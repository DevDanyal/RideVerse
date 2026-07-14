"""Shops and Marketplace API endpoints."""
from __future__ import annotations

import uuid as _uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db_session
from app.schemas.common import SuccessResponse
from app.schemas.shop import (
    MarketplaceListingCreate,
    MarketplaceListingListResponse,
    MarketplaceListingResponse,
    MarketplacePurchaseRequest,
    MarketplacePurchaseResponse,
    ShopBuyRequest,
    ShopDiscountRequest,
    ShopItemResponse,
    ShopItemListResponse,
    ShopListResponse,
    ShopPriceUpdateRequest,
    ShopResponse,
    ShopRestockRequest,
    ShopRestockResponse,
    ShopSellRequest,
    ShopTransactionListResponse,
    ShopTransactionResponse,
)
from app.services.shop import MarketplaceService, ShopService

router = APIRouter(prefix="/shops", tags=["Shops"])
marketplace_router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


def _get_shop_service(session: AsyncSession) -> ShopService:
    return ShopService(session)


def _get_marketplace_service(session: AsyncSession) -> MarketplaceService:
    return MarketplaceService(session)


# ══════════════════════════════════════════════════════════════════════════════
# SHOP ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@router.get("", response_model=SuccessResponse[ShopListResponse])
async def list_shops(
    category: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    shops = await svc.get_shops(category=category, skip=skip, limit=limit)
    return SuccessResponse(
        message="Shops retrieved",
        data=ShopListResponse(
            shops=[ShopResponse.model_validate(s) for s in shops],
            total=len(shops),
        ),
    )


@router.get("/{shop_id}", response_model=SuccessResponse[ShopResponse])
async def get_shop(
    shop_id: _uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    shop = await svc.get_shop(shop_id)
    return SuccessResponse(
        message="Shop retrieved",
        data=ShopResponse.model_validate(shop),
    )


@router.get("/{shop_id}/items", response_model=SuccessResponse[ShopItemListResponse])
async def list_shop_items(
    shop_id: _uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    items = await svc.get_shop_items(shop_id, skip=skip, limit=limit)
    return SuccessResponse(
        message="Shop items retrieved",
        data=ShopItemListResponse(
            items=[ShopItemResponse.model_validate(i) for i in items],
            total=len(items),
        ),
    )


@router.post("/{shop_id}/buy")
async def buy_item(
    shop_id: _uuid.UUID,
    body: ShopBuyRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    result = await svc.buy_item(
        account_id=_uuid.UUID(current_user["sub"]),
        shop_id=shop_id,
        item_id=body.item_id,
        quantity=body.quantity,
        idempotency_key=body.idempotency_key,
    )
    return SuccessResponse(message="Item purchased", data=result)


@router.post("/{shop_id}/sell")
async def sell_item(
    shop_id: _uuid.UUID,
    body: ShopSellRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    result = await svc.sell_item(
        account_id=_uuid.UUID(current_user["sub"]),
        shop_id=shop_id,
        item_id=body.item_id,
        quantity=body.quantity,
    )
    return SuccessResponse(message="Item sold", data=result)


@router.get("/{shop_id}/transactions", response_model=SuccessResponse[ShopTransactionListResponse])
async def get_shop_transactions(
    shop_id: _uuid.UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    txs = await svc.get_player_transactions(
        account_id=_uuid.UUID(current_user["sub"]),
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(
        message="Transactions retrieved",
        data=ShopTransactionListResponse(
            transactions=[ShopTransactionResponse.model_validate(tx) for tx in txs],
            total=len(txs),
        ),
    )


@router.post("/{shop_id}/restock")
async def restock_item(
    shop_id: _uuid.UUID,
    body: ShopRestockRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    result = await svc.restock_item(shop_id, body.item_id, body.amount)
    return SuccessResponse(
        message="Item restocked",
        data=ShopRestockResponse(**result),
    )


@router.post("/{shop_id}/discount")
async def apply_discount(
    shop_id: _uuid.UUID,
    body: ShopDiscountRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    result = await svc.apply_discount(shop_id, body.discount_percent, body.item_id)
    return SuccessResponse(message="Discount applied", data=result)


@router.post("/{shop_id}/price")
async def update_price(
    shop_id: _uuid.UUID,
    body: ShopPriceUpdateRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_shop_service(session)
    result = await svc.update_price(shop_id, body.item_id, body.new_price)
    return SuccessResponse(message="Price updated", data=result)


# ══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════


@marketplace_router.get("", response_model=SuccessResponse[MarketplaceListingListResponse])
async def search_listings(
    item_type: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    listings = await svc.get_active_listings(
        item_type=item_type,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(
        message="Listings retrieved",
        data=MarketplaceListingListResponse(
            listings=[MarketplaceListingResponse.model_validate(l) for l in listings],
            total=len(listings),
        ),
    )


@marketplace_router.get("/my", response_model=SuccessResponse[MarketplaceListingListResponse])
async def get_my_listings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    listings = await svc.get_my_listings(
        account_id=_uuid.UUID(current_user["sub"]),
        skip=skip,
        limit=limit,
    )
    return SuccessResponse(
        message="My listings retrieved",
        data=MarketplaceListingListResponse(
            listings=[MarketplaceListingResponse.model_validate(l) for l in listings],
            total=len(listings),
        ),
    )


@marketplace_router.get("/{listing_id}", response_model=SuccessResponse[MarketplaceListingResponse])
async def get_listing(
    listing_id: _uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    listing = await svc.get_listing(listing_id)
    return SuccessResponse(
        message="Listing retrieved",
        data=MarketplaceListingResponse.model_validate(listing),
    )


@marketplace_router.post("", status_code=201)
async def create_listing(
    body: MarketplaceListingCreate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    listing = await svc.create_listing(
        account_id=_uuid.UUID(current_user["sub"]),
        item_type=body.item_type,
        item_id=body.item_id,
        price=body.price,
    )
    return SuccessResponse(
        message="Listing created",
        data=MarketplaceListingResponse.model_validate(listing),
    )


@marketplace_router.post("/purchase")
async def purchase_listing(
    body: MarketplacePurchaseRequest,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    result = await svc.purchase_listing(
        account_id=_uuid.UUID(current_user["sub"]),
        listing_id=body.listing_id,
    )
    return SuccessResponse(
        message="Purchase successful",
        data=MarketplacePurchaseResponse(**result),
    )


@marketplace_router.delete("/{listing_id}")
async def cancel_listing(
    listing_id: _uuid.UUID,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db_session),
):
    svc = _get_marketplace_service(session)
    result = await svc.cancel_listing(
        account_id=_uuid.UUID(current_user["sub"]),
        listing_id=listing_id,
    )
    return SuccessResponse(message=result["message"], data=result)
