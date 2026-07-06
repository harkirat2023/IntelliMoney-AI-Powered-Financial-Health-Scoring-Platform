from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str = "", code: str = ""):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code or self._default_code()

    def _default_code(self) -> str:
        return "ERROR"


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code="NOT_FOUND")


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, code="VALIDATION_ERROR")


class AuthException(AppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code="AUTH_ERROR")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="CONFLICT")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="FORBIDDEN")


class BankConnectionException(AppException):
    def __init__(self, detail: str = "Bank connection failed"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail, code="BANK_CONNECTION_ERROR")


class ConsentExpiredException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Consent has expired", code="CONSENT_EXPIRED")


class ConsentDeniedException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="User denied consent", code="CONSENT_DENIED")


class ProviderNotFoundException(AppException):
    def __init__(self, provider: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown provider: {provider}", code="PROVIDER_NOT_FOUND")


class NoActiveConnectionsException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="No active bank connections found", code="NO_ACTIVE_CONNECTIONS")


class ConsentNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found", code="CONSENT_NOT_FOUND")


class ConsentAlreadyRevokedException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Consent already revoked", code="CONSENT_ALREADY_REVOKED")


class ImportPreferenceNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Import preference not found", code="IMPORT_PREFERENCE_NOT_FOUND")


class BankAccountNotActiveException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Bank account is not active", code="BANK_ACCOUNT_NOT_ACTIVE")


class ConsentNotGrantedException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Consent not granted for this account", code="CONSENT_NOT_GRANTED")


class SyncInProgressException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="A sync is already in progress for this account", code="SYNC_IN_PROGRESS")


class SyncRetryLimitExceededException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum retry attempts reached", code="SYNC_RETRY_LIMIT_EXCEEDED")


class FinancialTransactionNotFoundException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Financial transaction not found", code="FINANCIAL_TX_NOT_FOUND")


class DuplicateProcessException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Bank transaction already processed", code="DUPLICATE_PROCESS")


class InvalidReviewStateException(AppException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction is not in review-required state", code="INVALID_REVIEW_STATE")
