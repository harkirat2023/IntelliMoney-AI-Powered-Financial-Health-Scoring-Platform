from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.ml import CategorizeRequest, CategorizeResponse
from app.services.ml_service import categorizer


router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize(
    payload: CategorizeRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CategorizeResponse:
    category, confidence = categorizer.predict(payload.description)
    return CategorizeResponse(category=category, confidence=confidence)
