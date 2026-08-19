"""Account Aggregator (AA) sandbox/demo routes.

This router demonstrates the approved Setu AA Sandbox flow:

    Connect Financial Data
        -> Create Consent
        -> Consent Pending
        -> Approval / Rejection
        -> Notification
        -> Approved
        -> Create Data Session
        -> Data Ready
        -> Fetch Sandbox Data
        -> Normalize
        -> Import Transactions
        -> Existing IntelliMoney Financial Pipeline

It is a SANDBOX / DEMO integration only. It does not claim production
banking connectivity. Setu-specific calls stay behind the
``BankProviderAdapter`` integration boundary (see
``app/infrastructure/bank_integration/setu_sandbox.py``); this router
only orchestrates the demonstration states.

Imported transactions feed the SAME pipeline as manual transactions:
bank transactions -> deterministic categorization -> budgets -> cash flow ->
financial health. No second analytics system is created.
"""

from __future__ import annotations

from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.mongodb import get_database
from app.infrastructure.bank_integration import MockBankProvider
from app.infrastructure.bank_integration.consent_manager import (
    BankProviderRegistry,
)
from app.infrastructure.bank_integration.setu_sandbox import (
    SANDBOX_MODE_LABEL,
    setu_sandbox_provider,
)
from app.services.aa_data_service import import_aa_data_session
from app.utils.date_utils import utc_now

router = APIRouter(prefix="/aa", tags=["account-aggregator"])

SANDBOX_LABEL = SANDBOX_MODE_LABEL


def _get_registry() -> BankProviderRegistry:
    registry = BankProviderRegistry()
    registry.register("setu", setu_sandbox_provider)
    registry.register("mock", MockBankProvider())
    return registry


class AaConsentCreateRequest(BaseModel):
    provider: str = Field(default="setu", pattern="^(setu|mock)$")


class AaDataSessionRequest(BaseModel):
    consent_id: str


class AaNotificationRequest(BaseModel):
    id: str = ""
    type: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


async def _get_consent(db, user_id: str, consent_id: str) -> dict:
    consent = await db.aa_consents.find_one({"_id": ObjectId(consent_id)})
    if not consent:
        raise HTTPException(status_code=404, detail="AA consent not found")
    if consent.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="You do not own this AA consent")
    return consent


async def _get_data_session(db, user_id: str, session_id: str) -> dict:
    session = await db.aa_data_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="AA data session not found")
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="You do not own this data session")
    return session


@router.post("/consents")
async def create_consent(
    req: AaConsentCreateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Start an AA connection and create a consent request (sandbox)."""
    registry = _get_registry()
    adapter = registry.get(req.provider)
    settings = get_settings()
    redirect_url = f"{settings.bank_consent_redirect_base}?provider={req.provider}"
    init = await adapter.initiate_consent(str(user["_id"]), "1.0", redirect_url)

    consent_doc = {
        "_id": ObjectId(),
        "user_id": str(user["_id"]),
        "provider": req.provider,
        "consent_handle": init.consent_handle,
        "consent_url": init.consent_url,
        "consent_status": "PENDING",
        "sandbox": True,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    await db.aa_consents.insert_one(consent_doc)
    return {
        "id": str(consent_doc["_id"]),
        "consent_handle": init.consent_handle,
        "consent_url": init.consent_url,
        "consent_status": "PENDING",
        "sandbox": True,
        "label": SANDBOX_LABEL,
        "message": "Consent created. Approve the consent to continue (sandbox demo).",
    }


@router.get("/consents")
async def list_consents(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[dict[str, Any]]:
    cursor = db.aa_consents.find({"user_id": str(user["_id"])}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append({
            "id": str(doc["_id"]),
            "provider": doc.get("provider"),
            "consent_handle": doc.get("consent_handle"),
            "consent_status": doc.get("consent_status"),
            "created_at": doc.get("created_at"),
            "sandbox": doc.get("sandbox", True),
        })
    return items


@router.get("/consents/{consent_id}")
async def get_consent_status(
    consent_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    consent = await _get_consent(db, str(user["_id"]), consent_id)
    return {
        "id": str(consent["_id"]),
        "provider": consent.get("provider"),
        "consent_handle": consent.get("consent_handle"),
        "consent_status": consent.get("consent_status"),
        "created_at": consent.get("created_at"),
        "sandbox": consent.get("sandbox", True),
    }


@router.post("/consents/{consent_id}/approve")
async def approve_consent(
    consent_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Demonstrate consent approval (sandbox only)."""
    consent = await _get_consent(db, str(user["_id"]), consent_id)
    registry = _get_registry()
    adapter = registry.get(consent["provider"])
    status = await adapter.check_consent_status(consent["consent_handle"])
    new_status = "APPROVED" if status.status in ("ACTIVE", "PENDING") else "REJECTED"
    await db.aa_consents.update_one(
        {"_id": consent["_id"]},
        {"$set": {"consent_status": new_status, "updated_at": utc_now()}},
    )
    return {
        "id": str(consent["_id"]),
        "consent_status": new_status,
        "sandbox": True,
        "label": SANDBOX_LABEL,
        "message": "Consent approved. You can now create a data session (sandbox demo).",
    }


@router.post("/consents/{consent_id}/reject")
async def reject_consent(
    consent_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Demonstrate consent rejection (sandbox only)."""
    consent = await _get_consent(db, str(user["_id"]), consent_id)
    await db.aa_consents.update_one(
        {"_id": consent["_id"]},
        {"$set": {"consent_status": "REJECTED", "updated_at": utc_now()}},
    )
    return {
        "id": str(consent["_id"]),
        "consent_status": "REJECTED",
        "sandbox": True,
        "label": SANDBOX_LABEL,
        "message": "Consent rejected. No data session can be created.",
    }


@router.post("/notifications")
async def aa_notifications(
    req: AaNotificationRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Handle sandbox notification events (consent status updates).

    SANDBOX / DEMO: this is a simulated notification endpoint used by the
    sandbox demo flow. It is NOT a production Setu webhook and does not
    validate Setu signatures. In production the Setu webhook callback
    would be an unauthenticated public endpoint verified via Setu's
    signature headers; that is intentionally out of scope here.
    """
    data = req.data or {}
    consent_handle = req.id or data.get("id") or data.get("consentHandle") or ""
    event_type = (req.type or data.get("type") or "").upper()
    status_mapping = {
        "CONSENT_APPROVED": "APPROVED",
        "CONSENT_REVOKED": "REVOKED",
        "CONSENT_EXPIRED": "EXPIRED",
        "CONSENT_DENIED": "REJECTED",
    }
    new_status = status_mapping.get(event_type)
    matched = 0
    if consent_handle and new_status:
        result = await db.aa_consents.update_many(
            {"user_id": str(user["_id"]), "consent_handle": consent_handle},
            {"$set": {"consent_status": new_status, "updated_at": utc_now()}},
        )
        matched = result.modified_count
    return {
        "received": True,
        "event_type": event_type,
        "matched": matched,
        "sandbox": True,
        "label": SANDBOX_LABEL,
        "message": "Sandbox demo notification processed (not a real Setu webhook).",
    }


@router.post("/data-sessions")
async def create_data_session(
    req: AaDataSessionRequest,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Create a data session for an approved consent (sandbox)."""
    consent = await _get_consent(db, str(user["_id"]), req.consent_id)
    if consent["consent_status"] != "APPROVED":
        raise HTTPException(status_code=400, detail="Consent is not approved yet")

    registry = _get_registry()
    adapter = registry.get(consent["provider"])
    session_info = await adapter.create_data_session(consent["consent_handle"])

    session_doc = {
        "_id": ObjectId(),
        "user_id": str(user["_id"]),
        "consent_id": str(consent["_id"]),
        "consent_handle": consent["consent_handle"],
        "provider": consent["provider"],
        "session_id": session_info.get("session_id", ""),
        "data_status": "READY",
        "sandbox": True,
        "created_at": utc_now(),
    }
    await db.aa_data_sessions.insert_one(session_doc)
    return {
        "id": str(session_doc["_id"]),
        "session_id": session_doc["session_id"],
        "data_status": "READY",
        "sandbox": True,
        "label": SANDBOX_LABEL,
        "message": "Data session ready (sandbox demo). In this demo the data-ready transition is simulated; production AA would wait for a real data-ready notification.",
    }


@router.get("/data-sessions")
async def list_data_sessions(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[dict[str, Any]]:
    cursor = db.aa_data_sessions.find({"user_id": str(user["_id"])}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append({
            "id": str(doc["_id"]),
            "session_id": doc.get("session_id"),
            "consent_id": doc.get("consent_id"),
            "data_status": doc.get("data_status"),
            "created_at": doc.get("created_at"),
            "sandbox": doc.get("sandbox", True),
        })
    return items


@router.post("/data-sessions/{session_id}/fetch")
async def fetch_sandbox_data(
    session_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Fetch sandbox data, normalize, import into the existing pipeline.

    The fetched data is persisted as bank transactions and then runs the
    same deterministic categorization / budget / cash-flow / financial-health
    engine used for every other transaction source.
    """
    session = await _get_data_session(db, str(user["_id"]), session_id)

    registry = _get_registry()
    adapter = registry.get(session["provider"])

    result = await import_aa_data_session(db, str(user["_id"]), session, adapter)
    result["sandbox"] = True
    result["label"] = SANDBOX_LABEL
    return result


@router.get("/status")
async def aa_status(
    user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict[str, Any]:
    """Return the current AA sandbox demonstration status."""
    settings = get_settings()
    consent_count = await db.aa_consents.count_documents({"user_id": str(user["_id"])})
    session_count = await db.aa_data_sessions.count_documents({"user_id": str(user["_id"])})
    return {
        "mode": "sandbox",
        "label": SANDBOX_LABEL,
        "provider": "setu" if settings.setu_client_id else "mock-demo",
        "setu_configured": bool(settings.setu_client_id and settings.setu_client_secret),
        "demo_fallback_enabled": settings.aa_allow_demo_fallback,
        "consents_created": consent_count,
        "data_sessions_created": session_count,
        "message": "This is a Setu Account Aggregator SANDBOX / DEMO integration, not production banking connectivity.",
    }