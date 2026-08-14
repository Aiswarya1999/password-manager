"""Terminal menu for the password vault."""

import getpass
import os
import time

from master_auth import MasterAuth, LockedOutError
from vault_crypto import VaultCrypto
from vault_store import VaultStore

REVEAL_SECONDS = 15


def _countdown_reveal(username: str, password: str, seconds: int = REVEAL_SECONDS) -> None:
    """Show a username/password, counting down to auto-hide. Press 0 or e to hide early (Windows)."""
    print(f"\nUsername: {username}")
    print(f"Password: {password}")
    print("(press 0 or e to hide early)\n")

    try:
        import msvcrt

        start = time.time()
        while time.time() - start < seconds:
            remaining = seconds - int(time.time() - start)
            print(f"\rHiding in {remaining:2d}s... ", end="", flush=True)
            if msvcrt.kbhit():
                key = msvcrt.getch().decode(errors="ignore").lower()
                if key in ("0", "e"):
                    break
            time.sleep(0.1)
    except ImportError:
        # Non-Windows fallback: no abortable single-keypress read without extra
        # dependencies, so just wait out the timer (Ctrl+C still works to bail).
        try:
            time.sleep(seconds)
        except KeyboardInterrupt:
            pass

    print("\n")
    os.system("cls" if os.name == "nt" else "clear")


class VaultCLI:
    def __init__(self):
        self.crypto = VaultCrypto()
        self.auth = MasterAuth()
        self.store = None

    # --- entry point ---------------------------------------------------
    def run(self) -> None:
        try:
            self._run()
        except (EOFError, KeyboardInterrupt):
            print("\nc ya!")

    def _run(self) -> None:
        if not self._login():
            return
        self.store = VaultStore(self.crypto)

        while True:
            self._show_menu()
            choice = input("Choice: ").strip()

            if choice == "1":
                self._view()
            elif choice == "2":
                self._add()
            elif choice == "3":
                self._update()
            elif choice == "4":
                self._delete()
            else:
                print("Not a valid choice.")
                continue

            again = input("\nIs that all? (y/n): ").strip().lower()
            if again == "y":
                print("c ya!")
                break
            # anything else ('n' or otherwise) loops back to the menu

    # --- login / first run ---------------------------------------------------
    def _login(self) -> bool:
        if self.auth.is_first_run():
            print("No master password set yet - let's create one.")
            while True:
                pw = getpass.getpass("Choose a master password: ")
                confirm = getpass.getpass("Confirm master password: ")
                if pw and pw == confirm:
                    self.auth.set_master_password(pw)
                    self.crypto.unlock(pw)
                    return True
                print("Those didn't match (or were empty) - try again.\n")

        attempt = 0
        while True:
            pw = getpass.getpass("Master password: ")
            try:
                if self.auth.verify(pw):
                    self.crypto.unlock(pw)
                    return True
                print("Incorrect master password.\n")
            except LockedOutError as e:
                print(f"{e}\n")
                return False

    def _show_menu(self) -> None:
        print("\n1. View\n2. Add\n3. Update\n4. Delete")

    # --- helpers ---------------------------------------------------
    def _locate_entry(self, action_label: str):
        """Ask for a website (and username, if ambiguous). Returns (website, username) or (None, None)."""
        website = input("Website name: ").strip()
        usernames = self.store.usernames(website)
        if not usernames:
            print("No entry found for that website.")
            return None, None

        if len(usernames) > 1:
            print("Multiple accounts found:", ", ".join(usernames))
            username = input("Which username? ").strip()
        else:
            username = usernames[0]

        if not self.store.has_entry(website, username):
            print("No entry found for that username.")
            return None, None

        return website, username

    # --- actions ---------------------------------------------------
    def _view(self) -> None:
        website, username = self._locate_entry("view")
        if website is None:
            return
        password = self.store.get_password(website, username)
        _countdown_reveal(username, password)

    def _add(self) -> None:
        website = input("Website name: ").strip()
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        print(f"\nWebsite: {website}\nUsername: {username}\nPassword: {'*' * len(password)}")
        confirm = input("Save this? (y/n): ").strip().lower()
        if confirm == "y":
            self.store.add_entry(website, username, password)
            print("yay!")
        else:
            print("Not saved.")

    def _update(self) -> None:
        website, username = self._locate_entry("update")
        if website is None:
            return

        while True:
            field = input("Update (w)ebsite name, (u)sername, (p)assword, or (d)one editing? ").strip().lower()

            if field == "w":
                new_site = input("New website name: ").strip()
                if self.store.rename_entry(website, username, new_website=new_site):
                    website = new_site
                    print("Website name updated.")
            elif field == "u":
                new_user = input("New username: ").strip()
                if self.store.rename_entry(website, username, new_username=new_user):
                    username = new_user
                    print("Username updated.")
            elif field == "p":
                new_pw = getpass.getpass("New password: ")
                self.store.update_password(website, username, new_pw)
                print("Password updated.")
            elif field == "d":
                break
            else:
                print("Not a valid choice.")
                continue

            again = input("Update something else? (y/n): ").strip().lower()
            if again != "y":
                break

        print("yay! Entry updated.")

    def _delete(self) -> None:
        website, username = self._locate_entry("delete")
        if website is None:
            return

        print(f"About to delete: {website} / {username}")
        pw = getpass.getpass("Confirm your master password to delete: ")
        try:
            if not self.auth.verify(pw):
                print("Incorrect master password - deletion cancelled.")
                return
        except LockedOutError as e:
            print(f"{e} - deletion cancelled.")
            return

        siblings = [u for u in self.store.usernames(website) if u != username]
        if siblings:
            choice = input(
                f"Delete just '{username}', or the entire '{website}' website "
                f"({len(siblings) + 1} accounts)? (u/w): "
            ).strip().lower()
            if choice == "w":
                self.store.delete_website(website)
                print(f"yay! Deleted all accounts under {website}.")
                return

        self.store.delete_username(website, username)
        print("yay! Deleted.")
