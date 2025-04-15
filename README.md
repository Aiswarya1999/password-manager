# 🔐 Password Manager

A simple **Python-based password manager** that encrypts and securely stores passwords using the **Fernet encryption** module. This is a beginner-friendly cybersecurity project that demonstrates **secure password storage, encryption, and JSON-based data handling**.

---

## 🚀 Features

✅ **Secure Storage** – Encrypts passwords before saving them  
✅ **Fernet Encryption** – Ensures strong security using `cryptography` module  
✅ **Add & View Passwords** – Store and retrieve passwords securely  
✅ **Update Passwords** – Easily update existing passwords  
✅ **JSON Database** – Lightweight and easy to manage  
✅ **Command-Line Interface (CLI)** – Simple user input system  

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager

2️⃣ Set Up a Virtual Environment
bash:
python -m venv venv

3️⃣ Install Dependencies
bash:
pip install cryptography

4️⃣ Generate an Encryption Key
Before running the program, generate a secret key:
bash:
python keygen.py

5️⃣ Run the Password Manager
bash
python main.py
