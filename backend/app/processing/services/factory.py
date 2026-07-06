from motor.motor_asyncio import AsyncIOMotorDatabase

from app.processing.services.financial_processing_service import FinancialProcessingService


_service_instance: FinancialProcessingService | None = None


def get_processing_service(db: AsyncIOMotorDatabase) -> FinancialProcessingService:
    global _service_instance
    if _service_instance is not None:
        return _service_instance

    service = FinancialProcessingService(db)
    _service_instance = service
    return service
