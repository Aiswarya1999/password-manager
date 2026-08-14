import os
import sys

# Anchor to this script's own folder, so the vault files (salt.bin, master.hash,
# passwords.json, etc.) always live next to main.py -- regardless of which
# directory the user was in when they typed "pass".
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import VaultCLI


def main():
    VaultCLI().run()


if __name__ == "__main__":
    main()
