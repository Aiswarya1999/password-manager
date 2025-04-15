from cryptography.fernet import Fernet
import json
import os

#load encryption key_reads and returns the encryption key
def load_key():
    return open("key.key","rb").read() #rb is read-binary

key = load_key() #read from key.key
fernet = Fernet(key) #ready for encryption or decryption

#load or create the password file

if not os.path.exists("passwords.json"):#checking if the file exists in the directory
    with open("passwords.json","w") as f:#opens in write mode; with makes it properly close after writing
        json.dump({}, f)# writes empty curly braces to file JSON format

#reads and returns the stored passwords
def load_passwords():
    with open("passwords.json","r") as f:
        return json.load(f) #reads file and parses JSON content to python dictionary.

#saves and writes into the password.json file
def save_passwords(passwords):
    with open("passwords.json","w") as f:
        json.dump(passwords, f, indent=4)

#adds a new account name and encrypted password
def add_password():
    name = input("Account Name: ")
    pwd = input("Password: ")
    encrypted_pwd = fernet.encrypt(pwd.encode()).decode()

    passwords = load_passwords()
    passwords[name] = encrypted_pwd
    save_passwords(passwords)
    print(f"Password for '{name}' added.\n")

#display all stored account names and the decrypted passwords
def view_passwords():
    passwords = load_passwords()
    if not passwords:
        print("No passwords stored yet .\n")
        return
    
    for name, encrypted_pwd in passwords.items():
        try:
            decrypted_pwd = fernet.decrypt(encrypted_pwd.encode()).decode()
        except Exception as e:
            decrypted_pwd = "[Decryption Error]"
        print(f"{name} : {decrypted_pwd}")
        print()

#update password
def update_password():
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

def menu():
    while True:
        print("==Password Manager==")
        print("1. Add Password")
        print("2. View Passwords")
        print("3. Update Passwords")
        print("4. Exit")

        choice = input("Choose an option:")

        if choice == "1":
            add_password()
        elif choice == "2":
            view_passwords()
        elif choice == "3":
            update_password()
        elif choice == "4":
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    menu()