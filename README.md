
# 🔐 Password Manager (Python)

A simple yet secure command-line password manager built with Python. It allows you to store, retrieve, update, and delete encrypted passwords securely using a master password.

## 🚀 Features

- 🔑 **Master Password Protection**  
  Derives a strong encryption key from your master password using PBKDF2 with SHA256 and a unique salt.

- 🛡️ **Secure Encryption**  
  All passwords are encrypted using `Fernet` symmetric encryption from the `cryptography` module.

- 📂 **JSON-Based Storage**  
  Passwords are stored securely in an encrypted JSON file.

- 🗃️ **Update & Delete Support**  
  Easily update or delete saved entries.

- 📋 **Clipboard Control** *(Planned)*  
  Auto-copy to clipboard and clear after a timer (coming soon).

- ❌ **Account Name Validation**  
  Prevents saving numeric-only account names for better readability and security.

---

## 📦 Requirements

- Python 3.6+
- `cryptography`
- `pyperclip` (optional, for clipboard support)

Install dependencies:
```bash
pip install cryptography pyperclip
```

---

## 🛠️ Usage

### 1. Clone the Repository
```bash
git clone https://github.com/Aiswarya1999/password-manager.git
cd password-manager
```

### 2. Generate Encryption Key
Run the key generator script once:
```bash
python keygen.py
```

### 3. Start the Password Manager
```bash
python main.py
```

You’ll be prompted for a **master password**, which will be used to derive a secure encryption key.

---

## 📁 Project Structure

```
password-manager/
│
├── main.py          # Main application
├── keygen.py        # Generates encryption key
├── passwords.json   # Encrypted password storage (auto-generated)
├── key.key          # Encryption key (auto-generated)
├── README.md        # This file
└── .gitignore       # Prevents key files from being pushed
```

---

## ⚠️ Security Notice

- Never share your `key.key` or `passwords.json` files publicly.
- Use a strong master password — it's critical to protecting your stored data.

---

## 💡 To Do

- [ ] Clipboard auto-clear after copy
- [ ] GUI using Tkinter or PyQt
- [ ] Backup & sync options

---

## 🧑‍💻 Author

Made with ❤️ by [Aiswarya](https://github.com/Aiswarya1999)

---

## 📜 License

This project is licensed under the MIT License.
```

---
