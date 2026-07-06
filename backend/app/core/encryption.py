from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class FieldEncryptor:
    def __init__(self):
        key = get_settings().bank_encryption_key.encode()
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("Failed to decrypt field: invalid token") from exc
