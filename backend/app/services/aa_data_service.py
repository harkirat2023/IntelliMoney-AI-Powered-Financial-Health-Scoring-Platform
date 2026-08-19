"""Shared Account Aggregator (AA) sandbox data import logic.

Extracted from the AA router so that both the HTTP endpoint and the AI
Copilot executor use exactly the same code path when importing sandbox
data into the standard IntelliMoney pipeline.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.encryption import FieldEncryptor
from app.infrastructure.bank_integration.consent_manager import (
    BankProviderAdapter,
)
from app.services.auto_processing_service import AutoProcessingService
from app.utils.date_utils import utc_now


async def import_aa_data_session(
    db: AsyncIOMotorDatabase,
    user_id: str,
    session: dict,
    adapter: BankProviderAdapter,
) -> dict[str, Any]:
    """Fetch AA sandbox FI data for a data session and import it.

    Mirrors the previous inline router logic exactly: normalize provider
    data, ensure a real bank-account document exists (with encrypted tokens
    and a matching active consent so SyncService works), insert deduplicated
    bank transactions, then run the shared auto-processing pipeline.
    """
    session_id = str(session["_id"])
    consent = await db.aa_consents.find_one({"_id": ObjectId(session["consent_id"])})
    consent_handle = session.get("consent_handle") or consent.get("consent_handle", "")

    provider_accounts = await adapter.fetch_accounts(consent_handle, consent_handle)
    provider_txs = []
    for account in provider_accounts:
        provider_txs.extend(
            await adapter.fetch_transactions(
                consent_handle=consent_handle,
                consent_token=consent_handle,
                account_id=account.provider_account_id,
                from_date=utc_now() - timedelta(days=730),
                to_date=utc_now(),
            )
        )

    account_doc = await db.bank_accounts.find_one({
        "user_id": ObjectId(user_id),
        "consent_handle": consent_handle,
        "provider": session["provider"],
        "source": "aa_sandbox",
    })
    if account_doc:
        bank_account_id = account_doc["_id"]
    else:
        encryptor = FieldEncryptor()
        bank_account_doc = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "provider": session["provider"],
            "consent_handle": consent_handle,
            "provider_account_id": encryptor.encrypt(f"aa-{session_id}"),
            "bank_name": "Setu AA Sandbox",
            "masked_account_number": "••••0000",
            "account_type": "savings",
            "account_holder_name": "Sandbox Demo",
            "ifsc_code": "SANDB000",
            "connection_status": "active",
            "consent_status": "active",
            "consent_token": encryptor.encrypt(consent_handle),
            "consent_version": "1.0",
            "source": "aa_sandbox",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        await db.bank_accounts.insert_one(bank_account_doc)
        bank_account_id = bank_account_doc["_id"]
        now = utc_now()
        await db.consents.insert_one({
            "user_id": ObjectId(user_id),
            "bank_account_id": bank_account_id,
            "consent_status": "granted",
            "consent_version": "1.0",
            "granted_at": now,
            "expires_at": now + timedelta(days=365),
            "created_at": now,
            "updated_at": now,
        })

    imported = 0
    skipped = 0
    seen: set[str] = set()
    for ptx in provider_txs:
        key = f"{ptx.transaction_id}"
        if key in seen:
            skipped += 1
            continue
        seen.add(key)
        existing = await db.bank_transactions.find_one(
            {"provider_account_id": ptx.transaction_id, "transaction_id": ptx.transaction_id}
        )
        if existing:
            skipped += 1
            continue
        await db.bank_transactions.insert_one({
            "user_id": user_id,
            "bank_account_id": bank_account_id,
            "sync_log_id": "",
            "provider_account_id": ptx.transaction_id,
            "transaction_id": ptx.transaction_id,
            "description": ptx.description,
            "amount": ptx.amount,
            "transaction_type": ptx.transaction_type,
            "transaction_date": ptx.transaction_date,
            "category": ptx.category,
            "reference": ptx.reference,
            "source": "aa_sandbox",
            "created_at": utc_now(),
        })
        imported += 1

    await db.aa_data_sessions.update_one(
        {"_id": session["_id"]},
        {"$set": {"data_status": "IMPORTED", "transactions_imported": imported, "updated_at": utc_now()}},
    )

    processing = await AutoProcessingService(db).process_synced(user_id, str(bank_account_id))

    return {
        "session_id": session_id,
        "transactions_fetched": len(provider_txs),
        "transactions_imported": imported,
        "transactions_skipped": skipped,
        "categorized": processing.get("categorized", 0),
        "processed": processing.get("processed", 0),
        "health_recalculated": processing.get("health_recalculated", False),
    }