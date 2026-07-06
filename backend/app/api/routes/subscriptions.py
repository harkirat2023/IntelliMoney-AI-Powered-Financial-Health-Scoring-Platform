from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.schemas.subscription import Subscription, SubscriptionCreate, SubscriptionInsights, SubscriptionSuggestion, SubscriptionUpdate
from app.services.subscription_service import (
    create_subscription,
    delete_subscription,
    detect_subscriptions,
    get_subscription,
    get_subscription_insights,
    get_subscriptions,
    record_payment,
    update_subscription,
)


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("", response_model=list[Subscription])
async def list_subscriptions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[Subscription]:
    items = await get_subscriptions(db, current_user["_id"])
    return [Subscription(**item) for item in items]


@router.post("", response_model=Subscription)
async def add_subscription(
    payload: SubscriptionCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Subscription:
    item = await create_subscription(db, current_user["_id"], payload.model_dump())
    return Subscription(**item)


@router.get("/{subscription_id}", response_model=Subscription)
async def read_subscription(
    subscription_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Subscription:
    item = await get_subscription(db, current_user["_id"], subscription_id)
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return Subscription(**item)


@router.put("/{subscription_id}", response_model=Subscription)
async def edit_subscription(
    subscription_id: str,
    payload: SubscriptionUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Subscription:
    item = await update_subscription(db, current_user["_id"], subscription_id, payload.model_dump(exclude_none=True))
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return Subscription(**item)


@router.delete("/{subscription_id}")
async def remove_subscription(
    subscription_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, str]:
    deleted = await delete_subscription(db, current_user["_id"], subscription_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"status": "deleted"}


@router.get("/suggestions/detect", response_model=list[SubscriptionSuggestion])
async def suggest_subscriptions(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[SubscriptionSuggestion]:
    suggestions = await detect_subscriptions(db, current_user["_id"])
    return [SubscriptionSuggestion(**item) for item in suggestions]


@router.get("/insights", response_model=SubscriptionInsights)
async def get_insights(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> SubscriptionInsights:
    return await get_subscription_insights(db, current_user["_id"])


@router.post("/{subscription_id}/record-payment", response_model=Subscription)
async def record_subscription_payment(
    subscription_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Subscription:
    item = await record_payment(db, current_user["_id"], subscription_id)
    if not item:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return Subscription(**item)