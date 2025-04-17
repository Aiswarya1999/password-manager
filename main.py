from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

import json
import os
import getpass
import bcrypt
import pyperclip
import threading
import time

#KDF derivation
def derive_key_from_password(password: str, salt:bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length= 32,
        salt= salt,
        iterations= 100_100,
        backend= default_backend()
    )
    return urlsafe_b64encode(kdf.derive(password.encode()))

#load encryption key_reads and returns the encryption key
def load_or_create_salt():
    if not os.path.exists("salt.bin"):
        salt = os.urandom(16)
        with open("salt.bin","wb") as f:
            f.write(salt)
        return salt
    else:
        with open("salt.bin","rb") as f:
            return f.read()
    #return open("key.key","rb").read() #rb is read-binary

#key = load_key() #read from key.key
#fernet = Fernet(key) #ready for encryption or decryption

#load or create the password file
#if not os.path.exists("passwords.json"):#checking if the file exists in the directory
 #   with open("passwords.json","w") as f:#opens in write mode; with makes it properly close after writing
  #      json.dump({}, f)# writes empty curly braces to file JSON format

#reads and returns the stored passwords

def verify_or_create_master():
    if not os.path.exists("master.hash"):
        while True:
            new_pass = getpass.getpass("Create a master password: ")
            confirm_pass = getpass.getpass("Confirm it NOW! : ")
            if new_pass == confirm_pass:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
                with open("master.hash", "wb") as f:
                    f.write(hashed)
                print("Master password set!\n")
                return new_pass
            else:
                print("Passwords don't match bruv! Try again!! Nowwww! \n")
    else:
        with open("master.hash", "rb") as f:
            stored_hash = f.read()
        for attempt in range(3):
            pwd = getpass.getpass("Enter the master password: ")
            if bcrypt.checkpw(pwd.encode(), stored_hash):
                print("You may enter now! \n")
                return pwd
            else:
                print("Nope. Not the correct password! \n")
        print("Bro you failed. Exiting now! Bye.")
        exit()

def copy_and_clear_clipboard(text):
    pyperclip.copy(text)
    print("(Password copied to the clipboard. Will clear it in 10sec.)")
    def clear():
        time.sleep(10)
        pyperclip.copy("")
    threading.Thread(target=clear , daemon= True).start()


def load_passwords():
    if not os.path.exists("passwords.json"):
        with open("passwords.json","w") as f:
            json.dump({}, f)
        return {}
    with open("passwords.json", "r") as f:
        return json.load(f)

#saves and writes into the password.json file
def save_passwords(passwords):
    with open("passwords.json","w") as f:
        json.dump(passwords, f, indent=4)

#adds a new account name and encrypted password
def add_password(fernet):
    name = input("Account Name: ")
    if name.isdigit():
        print("Account name cant be a number. Try again.")
        return

    pwd = getpass.getpass("Password: ")
    encrypted_pwd = fernet.encrypt(pwd.encode()).decode()

    passwords = load_passwords()
    passwords[name] = encrypted_pwd
    save_passwords(passwords)
    print(f"Password for '{name}' added.\n")

#display all stored account names and the decrypted passwords
def view_passwords(fernet):
    passwords = load_passwords()
    if not passwords:
        print("No passwords stored yet .\n")
        return
    
    for name, encrypted_pwd in passwords.items():
        try:
            decrypted_pwd = fernet.decrypt(encrypted_pwd.encode()).decode()
        except Exception:
            decrypted_pwd = "[Decryption Error]"
        print(f"{name} : {decrypted_pwd}")

#update password
def update_password(fernet):
    passwords = load_passwords()

    if not passwords:
        print("No passwords stored yet.\n")
        return
    site = input("Enter the account name to update it's password: ")

    if site not in passwords:
        print(f"No entry for '{site}'.")
        return

    new_pwd = input("Enter the new password: ")
    encrypted_pwd = fernet.encrypt(new_pwd.encode()).decode()
    passwords[site] = encrypted_pwd
    save_passwords(passwords)
    print(f"Password updated for'{site}'.\n")

def delete_password(fernet):
    passwords = load_passwords()

    if not passwords:
        print("No passwords stored yet \n")
        return
    site = input("Enter account name to delete: ")
    if site not in passwords:
        print(f"No entry found for '{site}'.\n")
        return
    confirm = (f"Are you sure you want to delete '{site}'? (y/n): ").lower()
    if confirm == 'y':
        del passwords[site]
        save_passwords(passwords)
        print(f"Deleted password for '{site}'.\n")
    else:
        print("Delete canceled.\n")



def menu(fernet):
    while True:
        print("==Password Manager==")
        print("1. Add Password")
        print("2. View Passwords")
        print("3. Update Passwords")
        print("4. Delete Password")
        print("5. Exit")

        choice = input("Choose an option:")

        if choice == "1":
            add_password(fernet)
        elif choice == "2":
            view_passwords(fernet)
        elif choice == "3":
            update_password(fernet)
        elif choice == "4":
            delete_password(fernet)
        elif choice == "5":
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    salt = load_or_create_salt()
    master_password = getpass.getpass("Enter master password: ")
    key = derive_key_from_password(master_password, salt)
    fernet = Fernet(key)
    menu(fernet)