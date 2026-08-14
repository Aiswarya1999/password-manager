"""Encryption for the password vault.

The encryption key is derived fresh from the master password every time the
program runs and is held in memory only for that session. It is never
written to disk -- only the (non-secret) salt used to derive it persists.
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_FILE = "salt.bin"
KDF_ITERATIONS = 480_000  # OWASP-recommended minimum for PBKDF2-SHA256 (2023+)


class VaultCrypto:
    """Derives a session key from the master password and encrypts/decrypts vault data."""

    def __init__(self, salt_path: str = SALT_FILE):
        self.salt_path = salt_path
        self.salt = self._load_or_create_salt()
        self._fernet = None

    def _load_or_create_salt(self) -> bytes:
        if os.path.exists(self.salt_path):
            with open(self.salt_path, "rb") as f:
                return f.read()
        salt = os.urandom(16)
        with open(self.salt_path, "wb") as f:
            f.write(salt)
        return salt

    def unlock(self, master_password: str) -> None:
        """Derive this session's Fernet key from the master password. Key lives in memory only."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=KDF_ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
        self._fernet = Fernet(key)

    def is_unlocked(self) -> bool:
        return self._fernet is not None

    def encrypt(self, plaintext: str) -> str:
        if self._fernet is None:
            raise RuntimeError("Vault is locked. Call unlock() first.")
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        if self._fernet is None:
            raise RuntimeError("Vault is locked. Call unlock() first.")
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            # Wrong master password would produce a key that can't decrypt existing data.
            raise ValueError("Could not decrypt this entry - master password may be wrong.") from exc
