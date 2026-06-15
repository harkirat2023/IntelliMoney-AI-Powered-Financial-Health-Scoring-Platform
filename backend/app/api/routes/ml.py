from fastapi import APIRouter

from app.schemas.ml import CategorizeRequest, CategorizeResponse
from app.services.ml_service import categorizer


router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize(payload: CategorizeRequest) -> CategorizeResponse:
    category, confidence = categorizer.predict(payload.description)
    return CategorizeResponse(category=category, confidence=confidence)
