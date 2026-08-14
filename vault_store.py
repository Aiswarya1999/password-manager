"""Storage for the password vault.

Data model (passwords.json):
{
    "example.com": {
        "alice": "<encrypted password>",
        "alice_work": "<encrypted password>"
    },
    ...
}

One website can hold several accounts. Deleting the last username under a
website automatically removes the website entry too.
"""

import json
import os

VAULT_FILE = "passwords.json"


class VaultStore:
    def __init__(self, crypto, path: str = VAULT_FILE):
        self.crypto = crypto
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}

    def _save(self) -> None:
        """Write atomically: temp file + rename, so an interrupted write can't corrupt the vault."""
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp_path, self.path)

    # --- queries ---------------------------------------------------
    def websites(self) -> list:
        return list(self.data.keys())

    def usernames(self, website: str) -> list:
        return list(self.data.get(website, {}).keys())

    def has_entry(self, website: str, username: str) -> bool:
        return website in self.data and username in self.data[website]

    def get_password(self, website: str, username: str) -> str | None:
        enc = self.data.get(website, {}).get(username)
        return self.crypto.decrypt(enc) if enc is not None else None

    # --- mutations ---------------------------------------------------
    def add_entry(self, website: str, username: str, password: str) -> None:
        self.data.setdefault(website, {})[username] = self.crypto.encrypt(password)
        self._save()

    def update_password(self, website: str, username: str, new_password: str) -> bool:
        if not self.has_entry(website, username):
            return False
        self.data[website][username] = self.crypto.encrypt(new_password)
        self._save()
        return True

    def rename_entry(self, website: str, username: str, new_website: str = None, new_username: str = None) -> bool:
        """Move an entry to a new website and/or username, keeping its encrypted password."""
        if not self.has_entry(website, username):
            return False
        enc = self.data[website].pop(username)
        if not self.data[website]:
            del self.data[website]

        target_site = new_website if new_website else website
        target_user = new_username if new_username else username
        self.data.setdefault(target_site, {})[target_user] = enc
        self._save()
        return True

    def delete_username(self, website: str, username: str) -> bool:
        """Delete one username (and its password) from a website. Removes the website too if it was the last one."""
        if not self.has_entry(website, username):
            return False
        del self.data[website][username]
        if not self.data[website]:
            del self.data[website]
        self._save()
        return True

    def delete_website(self, website: str) -> bool:
        """Delete a website and every username/password stored under it (cascade)."""
        if website not in self.data:
            return False
        del self.data[website]
        self._save()
        return True
