import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user
from app.db.mongodb import get_database
from app.receipt_ocr.schemas import (
    ReceiptListResponse, ReceiptProcessResponse, ReceiptResponse,
    ReceiptUpdateRequest, ReceiptUploadResponse,
)
from app.receipt_ocr.services.receipt_service import ReceiptService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/receipts", tags=["receipts"])


def _get_svc(db: AsyncIOMotorDatabase) -> ReceiptService:
    return ReceiptService(db)


@router.post("/upload", response_model=ReceiptUploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptUploadResponse:
    svc = _get_svc(db)
    content = await file.read()
    result = await svc.upload(str(current_user["_id"]), content,
                               file.filename or "receipt.jpg",
                               file.content_type or "image/jpeg")
    if result["errors"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return ReceiptUploadResponse(
        receipt=ReceiptResponse(**svc._receipt_to_dict(result["receipt"])),
        message=result["message"],
    )


@router.post("/{receipt_id}/process", response_model=ReceiptProcessResponse)
async def process_receipt(
    receipt_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptProcessResponse:
    svc = _get_svc(db)
    result = await svc.process(receipt_id, str(current_user["_id"]))
    if not result["receipt"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return ReceiptProcessResponse(
        receipt=ReceiptResponse(**svc._receipt_to_dict(result["receipt"])),
        expense_id=result.get("expense_id", ""),
        message=result["message"],
    )


@router.post("/{receipt_id}/confirm", response_model=ReceiptProcessResponse)
async def confirm_receipt(
    receipt_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptProcessResponse:
    svc = _get_svc(db)
    result = await svc.confirm_and_finalize(receipt_id, str(current_user["_id"]))
    if not result["receipt"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return ReceiptProcessResponse(
        receipt=ReceiptResponse(**svc._receipt_to_dict(result["receipt"])),
        expense_id=result.get("expense_id", ""),
        message=result["message"],
    )


@router.get("", response_model=ReceiptListResponse)
async def list_receipts(
    status: str | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptListResponse:
    svc = _get_svc(db)
    receipts = await svc.get_receipts(str(current_user["_id"]), status)
    return ReceiptListResponse(
        receipts=[ReceiptResponse(**svc._receipt_to_dict(r)) for r in receipts],
        total=len(receipts),
    )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptResponse:
    svc = _get_svc(db)
    receipt = await svc.get_receipt(receipt_id, str(current_user["_id"]))
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse(**svc._receipt_to_dict(receipt))


@router.patch("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: str, body: ReceiptUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ReceiptResponse:
    svc = _get_svc(db)
    data = body.model_dump(exclude_none=True)
    receipt = await svc.update_receipt(receipt_id, str(current_user["_id"]), data)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse(**svc._receipt_to_dict(receipt))


@router.delete("/{receipt_id}", response_model=dict)
async def delete_receipt(
    receipt_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    svc = _get_svc(db)
    deleted = await svc.delete_receipt(receipt_id, str(current_user["_id"]))
    if not deleted:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {"message": "Receipt deleted"}


@router.get("/{receipt_id}/image")
async def get_receipt_image(
    receipt_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    from app.infrastructure.storage import get_storage_backend

    svc = _get_svc(db)
    receipt = await svc.get_receipt(receipt_id, str(current_user["_id"]))
    if not receipt or not receipt.image_path:
        raise HTTPException(status_code=404, detail="Receipt or image not found")

    storage = get_storage_backend()
    data = await storage.read(receipt.image_path)
    if data is None:
        raise HTTPException(status_code=404, detail="Image file not found")
    return Response(content=data, media_type=receipt.mime_type or "image/jpeg")
