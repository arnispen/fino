import os
import json
from pathlib import Path

def get_contacts_path(profile: str) -> str:
    """
    Returns the path to the profile-specific contacts.json file.
    Creates the folder if it doesn't exist.
    """
    base = Path.home() / ".fino" / "profiles" / profile
    base.mkdir(parents=True, exist_ok=True)
    return str(base / "contacts.json")


def load_contacts(profile: str) -> dict:
    """
    Load the contact dictionary for a given profile.
    """
    path = get_contacts_path(profile)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_contacts(contacts: dict, profile: str):
    """
    Save the contact dictionary for a given profile.
    """
    path = get_contacts_path(profile)
    with open(path, "w") as f:
        json.dump(contacts, f, indent=2)


def add_contact(name: str, npub: str, profile: str):
    contacts = load_contacts(profile)
    if name in contacts:
        print(f"⚠️ Contact '{name}' already exists. Overwriting.")
    contacts[name] = npub
    save_contacts(contacts, profile)
    print(f"✅ Contact '{name}' saved.")


def remove_contact(name: str, profile: str):
    contacts = load_contacts(profile)
    if name not in contacts:
        raise Exception(f"Contact '{name}' not found")
    del contacts[name]
    save_contacts(contacts, profile)
    print(f"🗑️ Contact '{name}' removed.")


def get_contact(name: str, profile: str) -> str:
    contacts = load_contacts(profile)
    if name not in contacts:
        raise Exception(f"Contact '{name}' not found")
    return contacts[name]


def list_contacts(profile: str) -> dict:
    return load_contacts(profile)


def lookup_contact_or_npub(recipient: str, profile: str) -> str:
    """
    Resolves either a named contact or direct npub string.
    """
    if recipient.startswith("npub1"):
        return recipient
    return get_contact(recipient, profile)
