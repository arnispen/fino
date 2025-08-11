from typing import List, Callable
import json
import asyncio
import websockets
from pynostr.key import PrivateKey, PublicKey
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.relay_manager import RelayManager
from pynostr.filters import Filters, FiltersList
from pynostr.event import EventKind, Event
from .console import console

DEFAULT_RELAYS = ["wss://nos.lol"]

def encrypt_payload(payload: dict, recipient_npub: str, sender_nsec: str) -> str:
    """Encrypt payload using ECDH shared secret for cross-key communication"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    import base64
    import os
    
    # Get keys
    sender_priv = PrivateKey.from_nsec(sender_nsec)
    recipient_pub = PublicKey.from_npub(recipient_npub)
    
    # Calculate shared secret using ECDH
    shared_secret = sender_priv.ecdh(recipient_pub.hex())
    
    # Derive encryption key
    key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'nostr-dm-payload',
    ).derive(shared_secret)
    
    # Generate random IV
    iv = os.urandom(16)
    
    # Encrypt the JSON payload
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    
    # Pad the data
    json_str = json.dumps(payload)
    data = json_str.encode('utf-8')
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return base64 encoded encrypted data with IV
    encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
    iv_b64 = base64.b64encode(iv).decode('utf-8')
    
    return f"{encrypted_b64}?iv={iv_b64}"

def decrypt_payload(event: Event, your_nsec: str) -> dict:
    """Decrypt payload using ECDH shared secret for cross-key communication"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    import base64
    
    priv = PrivateKey.from_nsec(your_nsec)
    
    console.print(f"🔍 Debug: Event content length: {len(event.content)}", style="cyan")
    console.print(f"🔍 Debug: Event pubkey: {event.pubkey[:8]}...", style="cyan")
    console.print(f"🔍 Debug: Our pubkey: {priv.public_key.hex()[:8]}...", style="cyan")
    
    # Check if it's our custom format (base64?iv=base64)
    if '?iv=' in event.content:
        console.print("🔄 Using custom ECDH decryption...", style="cyan")
        
        # Parse the encrypted content
        encrypted_part, iv_part = event.content.split('?iv=')
        encrypted_data = base64.b64decode(encrypted_part)
        iv_data = base64.b64decode(iv_part)
        
        # Calculate shared secret using ECDH
        sender_pubkey = PublicKey.from_hex(event.pubkey)
        shared_secret = priv.ecdh(event.pubkey)
        
        # Derive decryption key
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'nostr-dm-payload',
        ).derive(shared_secret)
        
        # Decrypt the data
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv_data))
        decryptor = cipher.decryptor()
        
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted_data[-1]
        decrypted_data = decrypted_data[:-padding_length]
        
        # Parse as JSON
        json_str = decrypted_data.decode('utf-8')
        console.print(f"🔍 Debug: Custom decryption successful: {json_str}", style="green")
        return json.loads(json_str)
    
    else:
        # Fallback to pynostr's built-in decryption (for self-send)
        console.print("🔄 Trying pynostr's built-in decryption...", style="cyan")
        try:
            dm = EncryptedDirectMessage()
            dm.encrypted_message = event.content
            dm.pubkey = event.pubkey
            dm.recipient_pubkey = priv.public_key.hex()
            
            dm.decrypt(priv.hex())
            console.print(f"🔍 Debug: Pynostr decryption successful: {dm.cleartext_content}", style="green")
            return json.loads(dm.cleartext_content)
        except Exception as e:
            console.print(f"❌ Debug: Pynostr decryption failed: {e}", style="red")
            raise e

async def send_dm_async(from_nsec: str, to_npub: str, encrypted_content: str, relays: List[str]):
    console.print("🚀 STARTING SEND PROCESS", style="bright_magenta")
    
    priv = PrivateKey.from_nsec(from_nsec)
    console.print(f"🔑 Sender private key: {priv.public_key.hex()[:8]}...", style="cyan")
    
    pub = PublicKey.from_npub(to_npub)
    console.print(f"👤 Recipient public key: {pub.hex()[:8]}...", style="cyan")
    
    dm = EncryptedDirectMessage()
    console.print("🔐 Creating DM event...", style="cyan")
    # The content is already encrypted, just create the event
    dm.encrypted_message = encrypted_content
    dm.pubkey = priv.public_key.hex()
    dm.recipient_pubkey = pub.hex()
    console.print("✅ DM event created successfully", style="green")
    
    ev = dm.to_event()
    ev.sign(priv.hex())
    console.print(f"📝 Event created - ID: {ev.id[:8]}...", style="cyan")
    console.print(f"📝 Event kind: {ev.kind}", style="cyan")
    console.print(f"📝 Event pubkey: {ev.pubkey[:8]}...", style="cyan")
    console.print(f"📝 Event tags: {ev.tags}", style="cyan")
    
    # Send to each relay directly
    chosen_relays = relays if relays else DEFAULT_RELAYS
    for relay_url in chosen_relays:
        console.print(f"🔌 Connecting to {relay_url}...", style="cyan")
        try:
            async with websockets.connect(relay_url, proxy=None) as websocket:
                console.print(f"✅ Connected to {relay_url}", style="green")
                
                # Send the event
                event_data = {
                    "id": ev.id,
                    "pubkey": ev.pubkey,
                    "created_at": ev.created_at,
                    "kind": ev.kind,
                    "tags": ev.tags,
                    "content": ev.content,
                    "sig": ev.sig
                }
                event_msg = json.dumps(["EVENT", event_data])
                console.print(f"📤 Sending event to {relay_url}...", style="cyan")
                await websocket.send(event_msg)
                
                # Wait for OK response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                console.print(f"📨 Response from {relay_url}: {response}", style="cyan")
                
        except Exception as e:
            console.print(f"❌ Failed to send to {relay_url}: {e}", style="red")
    
    console.print("✅ Send process completed", style="green")

def send_dm(from_nsec: str, to_npub: str, encrypted_content: str, relays: List[str]):
    asyncio.run(send_dm_async(from_nsec, to_npub, encrypted_content, relays))

async def receive_loop_async(your_nsec: str, relays: List[str], callback: Callable):
    console.print("🎧 STARTING RECEIVE PROCESS", style="bright_magenta")
    
    try:
        priv = PrivateKey.from_nsec(your_nsec)
        pub_hex = priv.public_key.hex()
        console.print(f"🔑 Receiver private key: {pub_hex[:8]}...", style="cyan")
        
        default = DEFAULT_RELAYS
        chosen = relays if relays else default
        console.print(f"🌐 Using relays: {chosen}", style="cyan")

        # Connect to the first relay
        relay_url = chosen[0]
        console.print(f"🔌 Connecting to {relay_url}...", style="cyan")
        
        # Record start time to only process recent messages
        import time
        start_time = int(time.time())
        console.print(f"⏰ Started listening at: {start_time}", style="cyan")
    except Exception as e:
        console.print(f"❌ Error initializing receiver: {e}", style="red")
        return
    
    try:
        console.print(f"🔌 Attempting to connect to {relay_url}...", style="cyan")
        async with websockets.connect(relay_url, proxy=None) as websocket:
            console.print(f"✅ Connected to {relay_url}", style="green")
            
            # Subscribe to DMs for our pubkey
            req_msg = json.dumps(["REQ", "dm", {"kinds": [4], "#p": [pub_hex]}])
            console.print(f"📤 Sending subscription: {req_msg}", style="cyan")
            await websocket.send(req_msg)
            
            console.print(f"🔍 Subscribed to DMs for pubkey: {pub_hex[:8]}...", style="blue")
            console.print("⏳ Waiting for incoming messages — press Ctrl+C to exit", style="green")
            
            message_count = 0
            try:
                while True:
                    response = await websocket.recv()
                    message_count += 1
                    
                    try:
                        data = json.loads(response)
                        if data[0] == "EVENT":
                            ev_data = data[2]
                            
                            # Only process Kind 4 (DM) events
                            if ev_data['kind'] != 4:
                                continue
                            
                            # Check if this event is for us
                            tags = ev_data.get('tags', [])
                            our_tag = None
                            for tag in tags:
                                if tag[0] == "p" and tag[1] == pub_hex:
                                    our_tag = tag
                                    break
                            
                            if our_tag:
                                # Check if message is recent (sent after we started listening)
                                message_age = start_time - ev_data['created_at']
                                if message_age < 0:  # Message is newer than when we started
                                    console.print(f"📨 NEW FILE MESSAGE RECEIVED:", style="bright_green")
                                    console.print(f"   📝 Event ID: {ev_data['id'][:8]}...", style="green")
                                    console.print(f"   📝 From: {ev_data['pubkey'][:8]}...", style="green")
                                    console.print(f"   ⏰ Age: {abs(message_age)}s ago", style="green")
                                    
                                    # Create Event object for callback
                                    from pynostr.event import Event
                                    ev = Event(
                                        id=ev_data['id'],
                                        pubkey=ev_data['pubkey'],
                                        created_at=ev_data['created_at'],
                                        kind=ev_data['kind'],
                                        tags=ev_data['tags'],
                                        content=ev_data['content'],
                                        sig=ev_data['sig']
                                    )
                                    callback(ev)
                                else:
                                    # Old message, skip silently
                                    continue
                            else:
                                # Not for us, skip silently
                                continue
                        else:
                            # Non-EVENT messages, skip silently
                            continue
                            
                    except json.JSONDecodeError:
                        # Invalid JSON, skip silently
                        continue
                        
            except KeyboardInterrupt:
                console.print(f"\n👋 Stopping receiver... (processed {message_count} messages)", style="yellow")
            except Exception as e:
                console.print(f"❌ Error in receive loop: {e}", style="red")
                
    except Exception as e:
        console.print(f"❌ Failed to connect to relay: {e}", style="red")
        console.print(f"❌ Exception type: {type(e)}", style="red")
        import traceback
        console.print(f"❌ Traceback: {traceback.format_exc()}", style="red")

def receive_loop(your_nsec: str, relays: List[str], callback: Callable):
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # We're in an event loop, create a task
        task = loop.create_task(receive_loop_async(your_nsec, relays, callback))
        return task
    except RuntimeError:
        # No event loop running, create a new one
        asyncio.run(receive_loop_async(your_nsec, relays, callback))
