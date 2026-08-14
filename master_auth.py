"""Master password setup and verification, with brute-force lockout.

Uses its own salt/hash files, separate from vault_crypto.py's salt.bin,
so a compromise of one doesn't automatically compromise the other.
"""

import hmac
import os
import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VERIFY_HASH_FILE = "master.hash"
VERIFY_SALT_FILE = "master.salt"
KDF_ITERATIONS = 480_000
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 30


class MasterAuthError(Exception):
    """Base class for master-auth related errors."""


class LockedOutError(MasterAuthError):
    """Raised when too many failed attempts have triggered a temporary lockout."""


class MasterAuth:
    def __init__(self, hash_path: str = VERIFY_HASH_FILE, salt_path: str = VERIFY_SALT_FILE):
        self.hash_path = hash_path
        self.salt_path = salt_path
        self._attempts = 0
        self._locked_until = 0.0

    @staticmethod
    def _derive(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=KDF_ITERATIONS)
        return kdf.derive(password.encode("utf-8"))

    def is_first_run(self) -> bool:
        return not (os.path.exists(self.hash_path) and os.path.exists(self.salt_path))

    def set_master_password(self, password: str) -> None:
        salt = os.urandom(16)
        digest = self._derive(password, salt)
        with open(self.salt_path, "wb") as f:
            f.write(salt)
        with open(self.hash_path, "wb") as f:
            f.write(digest)

    def verify(self, password: str) -> bool:
        """Returns True/False for a correct/incorrect password. Raises LockedOutError if locked out."""
        if time.time() < self._locked_until:
            remaining = int(self._locked_until - time.time()) + 1
            raise LockedOutError(f"Too many attempts. Try again in {remaining}s.")

        with open(self.salt_path, "rb") as f:
            salt = f.read()
        with open(self.hash_path, "rb") as f:
            stored = f.read()

        candidate = self._derive(password, salt)
        ok = hmac.compare_digest(candidate, stored)  # constant-time comparison

        if ok:
            self._attempts = 0
            return True

        self._attempts += 1
        if self._attempts >= MAX_ATTEMPTS:
            self._locked_until = time.time() + LOCKOUT_SECONDS
            self._attempts = 0
        return False
