import base64
import json
import os
import time
from pathlib import Path
from fino.encryption import decrypt_bytes
from fino.ipfs import download_from_ipfs
from fino.nostr import connect_and_receive_dms
from fino.profiles import load_profile
from fino.history import log_received_file
from fino.contacts import list_contacts, add_contact


DEFAULT_RELAY = "wss://relay.damus.io"


def get_received_dir(profile: str) -> Path:
    """Ensure profile's received/ folder exists."""
    path = Path.home() / ".fino" / "profiles" / profile / "received"
    path.mkdir(parents=True, exist_ok=True)
    return path


def receive_file(profile: str, relay_url: str = DEFAULT_RELAY, auto_save: bool = False):
    print(f"📡 Listening for messages for profile '{profile}' via {relay_url}...")

    nsec, npub = load_profile(profile)

    try:
        messages = connect_and_receive_dms(nsec, npub, relay_url)
    except Exception as e:
        print(f"❌ Failed to connect or receive DMs: {e}")
        return

    if not messages:
        print("📭 No new messages received.")
        return

    for i, msg in enumerate(messages, 1):
        print(f"\n📨 Message {i}:")
        try:
            payload = json.loads(msg)

            cid = payload["cid"]
            key = base64.b64decode(payload["key"])
            nonce = base64.b64decode(payload["nonce"])

            print(f"🔐 Decrypted payload: CID={cid}")
            print(f"🔗 IPFS URL: https://gateway.pinata.cloud/ipfs/{cid}")

            encrypted_bytes = download_from_ipfs(cid)
            decrypted = decrypt_bytes(encrypted_bytes, key, nonce)

            timestamp = int(time.time())
            default_filename = f"received_{timestamp}.bin"
            received_dir = get_received_dir(profile)
            output_path = received_dir / default_filename

            if not auto_save:
                prompt = input(
                    f"💾 Save file as [{default_filename}] in 'received/'? (Enter new name or press Enter): "
                ).strip()
                if prompt:
                    output_path = received_dir / prompt

            with open(output_path, "wb") as f:
                f.write(decrypted)

            print(f"✅ File decrypted and saved to: {output_path}")

            # 🔥 Log to history
            log_received_file(profile, cid, msg["pubkey"], output_path.name)

            # 🧠 Save sender if unknown
            sender_npub = msg["pubkey"]
            known_contacts = list_contacts(profile)
            if sender_npub not in known_contacts.values():
                print("🧩 The sender is not in your contacts.")
                confirm = input("💾 Save sender as a contact? (y/N): ").strip().lower()
                if confirm == "y":
                    name = input("👤 Enter a name for this contact: ").strip()
                    if name:
                        try:
                            add_contact(name, sender_npub, profile=profile)
                            print(f"✅ Contact '{name}' saved.")
                        except Exception as e:
                            print(f"❌ Failed to save contact: {e}")

        except Exception as e:
            print(f"❌ Failed to process message: {e}")
