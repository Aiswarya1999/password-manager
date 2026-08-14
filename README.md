🔐 Password Manager (Python)

A simple, secure command-line password manager. Stores, retrieves, updates, and deletes encrypted passwords behind a single master password.

🚀 Features

🔑 Master Password Protection — the master password is never stored directly. Only a PBKDF2-SHA256 hash (480,000 iterations) is kept, checked with a constant-time comparison, with a 30-second lockout after 5 failed attempts.
🛡️ No Key Ever Touches Disk — the actual encryption key is derived fresh from your master password every time the program starts (PBKDF2-SHA256 → Fernet key) and lives in memory only for that session. Only a non-secret salt is persisted.
📂 Encrypted, Atomic Storage — passwords are encrypted with Fernet (from the cryptography library) and written to passwords.json atomically (temp file + rename), so an interrupted write can't corrupt the vault.
🗂️ Multiple Accounts Per Website — each website can hold several username/password pairs, not just one.
🗃️ Full CRUD — view, add, update, and delete entries from a simple menu.
⏱️ Timed Reveal — viewing a password shows it in the terminal with a 15-second countdown; press 0 or e to hide it early (Windows).
🧹 Cascading Delete — deleting the last username under a website removes the website entry too; deleting one of several usernames leaves the others intact, with a prompt to delete the whole website instead if you want.
📦 Requirements
Python 3.10+
cryptography

Install:

pip install -r requirements.txt
🛠️ Usage

1. Clone the repository

git clone https://github.com/Aiswarya1999/password-manager.git
cd password-manager

2. Install dependencies

pip install -r requirements.txt

3. Run it

python main.py

On first run, you'll be asked to set a master password. After that, you'll be asked to enter it each time to unlock the vault.

Optional — run it as pass from anywhere (Windows):

Create a pass.bat file in a folder that's on your PATH (e.g. %USERPROFILE%\bin), containing:

@python C:\path\to\password-manager\main.py %*

Then open a new terminal and just type pass from any directory.

Menu
1. View
2. Add
3. Update
4. Delete

After each action you'll be asked "Is that all? (y/n)" — y exits, anything else loops back to the menu.

📁 Project Structure
password-manager/
│
├── main.py            # Entry point
├── cli.py              # Menu loop and all four actions (view/add/update/delete)
├── vault_crypto.py     # Key derivation + encrypt/decrypt (key never persisted)
├── master_auth.py      # Master password set/verify + brute-force lockout
├── vault_store.py       # Atomic, nested JSON storage
├── requirements.txt
├── .gitignore           # Excludes all generated secrets (see below)
└── README.md

# Generated at runtime, never committed:
├── salt.bin            # Non-secret salt for the encryption key
├── master.salt          # Non-secret salt for the master password hash
├── master.hash          # Master password hash (not the password itself)
└── passwords.json        # Your encrypted vault
⚠️ Security Notice
passwords.json, salt.bin, master.hash, and master.salt are all listed in .gitignore and should never be committed. If you fork or clone this repo, these files will be generated fresh on your machine the first time you run it.
Losing your master password means losing access to your vault — there is no recovery mechanism, by design.
This is a personal, single-user, local-only tool. It hasn't been audited and shouldn't be treated as a substitute for an established password manager for anything you can't afford to lose.
💡 To Do
Session auto-lock after a period of inactivity
GUI (Tkinter or PyQt)
Backup/export options
🧑‍💻 Author

Made with ❤️ by Aiswarya

📜 License

This project is licensed under the MIT License.
