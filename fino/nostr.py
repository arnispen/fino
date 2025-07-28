import json
import time
import base64
import websocket
from typing import List, Optional, Dict

from pynostr.key import PrivateKey, PublicKey
from pynostr.event import Event
from pynostr.message_type import ClientMessageType
from pynostr.encrypted_dm import EncryptedDirectMessage


RELAY_URL = "wss://relay.damus.io"  # Can make configurable later


def encrypt_payload(payload: Dict, sender_nsec: str, recipient_npub: str) -> str:
    """
    Encrypts a payload dictionary using NIP-04.
    """
    sender = PrivateKey.from_nsec(sender_nsec)
    recipient_pubkey = PublicKey.from_npub(recipient_npub)
    plaintext = json.dumps(payload)
    encrypted_content = EncryptedDirectMessage.encrypt(
        sender, recipient_pubkey.hex(), plaintext
    )
    return encrypted_content


def decrypt_payload(ciphertext: str, sender_pubkey: str, recipient_nsec: str) -> Dict:
    """
    Decrypts a NIP-04 ciphertext sent from a known public key.
    """
    recipient = PrivateKey.from_nsec(recipient_nsec)
    plaintext = EncryptedDirectMessage.decrypt(
        recipient, sender_pubkey, ciphertext
    )
    return json.loads(plaintext)


def send_nostr_dm(sender_nsec: str, recipient_npub: str, ciphertext: str, relay_url: str = RELAY_URL):
    """
    Sends a NIP-04 encrypted DM as kind: 4 event to a relay.
    """
    sender = PrivateKey.from_nsec(sender_nsec)
    recipient_pubkey = PublicKey.from_npub(recipient_npub)

    event = Event(
        pubkey=sender.public_key().hex(),
        content=ciphertext,
        kind=4,
        created_at=int(time.time()),
        tags=[["p", recipient_pubkey.hex()]]
    )
    sender.sign_event(event)

    ws = websocket.create_connection(relay_url)
    msg = json.dumps([ClientMessageType.EVENT, event.to_dict()])
    ws.send(msg)
    print(f"📨 Sent encrypted message to {recipient_npub}")
    ws.close()


def receive_dms(nsec: str, relay_url: str = RELAY_URL, limit: int = 5) -> List[Dict]:
    """
    Connects to a Nostr relay and receives encrypted DMs for your pubkey.

    Returns:
        A list of dicts: { cid, key, nonce, sender_npub }
    """
    priv = PrivateKey.from_nsec(nsec)
    pubkey_hex = priv.public_key().hex()
    sender = priv

    # Subscribe to DMs
    sub_id = "fino-sub"
    filter_obj = {
        "kinds": [4],
        "limit": limit,
        "tags": [["p", pubkey_hex]]
    }

    ws = websocket.create_connection(relay_url)
    ws.send(json.dumps(["REQ", sub_id, filter_obj]))

    messages = []
    try:
        while True:
            raw = ws.recv()
            msg = json.loads(raw)

            if msg[0] == "EVENT" and msg[1] == sub_id:
                event = msg[2]
                sender_pubkey = event["pubkey"]
                content = event["content"]

                try:
                    decrypted = decrypt_payload(content, sender_pubkey, nsec)
                    decrypted["sender_npub"] = PublicKey(bytes.fromhex(sender_pubkey)).bech32()
                    messages.append(decrypted)
                    print(f"📩 Received message from {decrypted['sender_npub']}")
                except Exception as e:
                    print(f"❌ Failed to decrypt message: {e}")

            if len(messages) >= limit:
                break
    finally:
        ws.close()

    return messages
