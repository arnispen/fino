import os
import base64
from fino.encryption import encrypt_file
from fino.ipfs import upload_to_ipfs
from fino.nostr import encrypt_payload_for_npub, send_nostr_dm
from fino.profiles import load_profile
from fino.contacts import get_contact, list_contacts, add_contact


def resolve_recipient(to: str, from_profile: str) -> str:
    """Try to resolve a contact name to npub, or accept a raw npub."""
    try:
        # Try contact first
        return get_contact(to, profile=from_profile)
    except:
        # Fallback: assume it's a raw npub
        if to.startswith("npub1") and len(to) > 10:
            return to
        raise ValueError("Recipient not found and input does not look like a valid npub1 key.")


def send_file(file_path, from_profile, recipient=None, pinata_jwt=None):
    print(f"📤 Preparing to send file: {file_path}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # 🔐 Load PINATA_JWT from env if not provided
    if not pinata_jwt:
        pinata_jwt = os.getenv("PINATA_JWT")

    if not pinata_jwt:
        raise ValueError("❌ Pinata JWT is required. Use --pinata-jwt or set PINATA_JWT in .env or env.")

    # Interactive prompt if recipient not passed
    if not recipient:
        print("\n📤 Who do you want to send the file to?")
        to_input = input("Enter contact name or npub1...: ").strip()
        if not to_input:
            raise ValueError("Recipient is required.")
        recipient = to_input

    # Try resolving contact name or direct npub
    try:
        recipient_npub = resolve_recipient(recipient, from_profile)
    except Exception as e:
        raise ValueError(f"❌ Could not resolve recipient: {e}")

    print(f"🔐 Loading sender profile: {from_profile}")
    nsec, _npub = load_profile(from_profile)

    print(f"🔒 Encrypting file using AES-256-GCM...")
    encrypted_data, key, nonce = encrypt_file(file_path)

    print("🚀 Uploading to IPFS (via Pinata)...")
    cid = upload_to_ipfs(encrypted_data, pinata_jwt)

    print(f"✅ Uploaded! CID: {cid}")
    print(f"🔗 URL: https://gateway.pinata.cloud/ipfs/{cid}")

    print("🔏 Encrypting payload for recipient...")
    encrypted_message = encrypt_payload_for_npub(cid, key, nonce, recipient_npub, sender_nsec=nsec)

    print("📡 Sending Nostr direct message...")
    send_nostr_dm(nsec, recipient_npub, encrypted_message)

    print("✅ File sent successfully.")

    # 🔁 Ask to save recipient if unknown
    contacts = list_contacts(from_profile)
    if recipient_npub not in contacts.values():
        print("🧩 This recipient isn’t in your contacts.")
        confirm = input("💾 Save as a contact? (y/N): ").strip().lower()
        if confirm == "y":
            name = input("👤 Enter a name for this contact: ").strip()
            if name:
                try:
                    add_contact(name, recipient_npub, profile=from_profile)
                    print(f"✅ Contact '{name}' saved.")
                except Exception as e:
                    print(f"❌ Failed to save contact: {e}")
