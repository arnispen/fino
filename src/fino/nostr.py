from typing import List, Callable
import typer
import json
import asyncio
import websockets
from pynostr.key import PrivateKey, PublicKey
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.relay_manager import RelayManager
from pynostr.filters import Filters, FiltersList
from pynostr.event import EventKind, Event

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
    
    typer.secho(f"🔍 Debug: Event content length: {len(event.content)}", fg=typer.colors.CYAN)
    typer.secho(f"🔍 Debug: Event pubkey: {event.pubkey[:8]}...", fg=typer.colors.CYAN)
    typer.secho(f"🔍 Debug: Our pubkey: {priv.public_key.hex()[:8]}...", fg=typer.colors.CYAN)
    
    # Check if it's our custom format (base64?iv=base64)
    if '?iv=' in event.content:
        typer.secho("🔄 Using custom ECDH decryption...", fg=typer.colors.CYAN)
        
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
        typer.secho(f"🔍 Debug: Custom decryption successful: {json_str}", fg=typer.colors.GREEN)
        return json.loads(json_str)
    
    else:
        # Fallback to pynostr's built-in decryption (for self-send)
        typer.secho("🔄 Trying pynostr's built-in decryption...", fg=typer.colors.CYAN)
        try:
            dm = EncryptedDirectMessage()
            dm.encrypted_message = event.content
            dm.pubkey = event.pubkey
            dm.recipient_pubkey = priv.public_key.hex()
            
            dm.decrypt(priv.hex())
            typer.secho(f"🔍 Debug: Pynostr decryption successful: {dm.cleartext_content}", fg=typer.colors.GREEN)
            return json.loads(dm.cleartext_content)
        except Exception as e:
            typer.secho(f"❌ Debug: Pynostr decryption failed: {e}", fg=typer.colors.RED)
            raise e

async def send_dm_async(from_nsec: str, to_npub: str, encrypted_content: str, relays: List[str]):
    typer.secho("🚀 STARTING SEND PROCESS", fg=typer.colors.BRIGHT_MAGENTA)
    
    priv = PrivateKey.from_nsec(from_nsec)
    typer.secho(f"🔑 Sender private key: {priv.public_key.hex()[:8]}...", fg=typer.colors.CYAN)
    
    pub = PublicKey.from_npub(to_npub)
    typer.secho(f"👤 Recipient public key: {pub.hex()[:8]}...", fg=typer.colors.CYAN)
    
    dm = EncryptedDirectMessage()
    typer.secho("🔐 Creating DM event...", fg=typer.colors.CYAN)
    # The content is already encrypted, just create the event
    dm.encrypted_message = encrypted_content
    dm.pubkey = priv.public_key.hex()
    dm.recipient_pubkey = pub.hex()
    typer.secho("✅ DM event created successfully", fg=typer.colors.GREEN)
    
    ev = dm.to_event()
    ev.sign(priv.hex())
    typer.secho(f"📝 Event created - ID: {ev.id[:8]}...", fg=typer.colors.CYAN)
    typer.secho(f"📝 Event kind: {ev.kind}", fg=typer.colors.CYAN)
    typer.secho(f"📝 Event pubkey: {ev.pubkey[:8]}...", fg=typer.colors.CYAN)
    typer.secho(f"📝 Event tags: {ev.tags}", fg=typer.colors.CYAN)
    
    # Send to each relay directly
    chosen_relays = relays if relays else DEFAULT_RELAYS
    for relay_url in chosen_relays:
        typer.secho(f"🔌 Connecting to {relay_url}...", fg=typer.colors.CYAN)
        try:
            async with websockets.connect(relay_url) as websocket:
                typer.secho(f"✅ Connected to {relay_url}", fg=typer.colors.GREEN)
                
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
                typer.secho(f"📤 Sending event to {relay_url}...", fg=typer.colors.CYAN)
                await websocket.send(event_msg)
                
                # Wait for OK response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                typer.secho(f"📨 Response from {relay_url}: {response}", fg=typer.colors.CYAN)
                
        except Exception as e:
            typer.secho(f"❌ Failed to send to {relay_url}: {e}", fg=typer.colors.RED)
    
    typer.secho("✅ Send process completed", fg=typer.colors.GREEN)

def send_dm(from_nsec: str, to_npub: str, encrypted_content: str, relays: List[str]):
    asyncio.run(send_dm_async(from_nsec, to_npub, encrypted_content, relays))

async def receive_loop_async(your_nsec: str, relays: List[str], callback: Callable):
    typer.secho("🎧 STARTING RECEIVE PROCESS", fg=typer.colors.BRIGHT_MAGENTA)
    
    try:
        priv = PrivateKey.from_nsec(your_nsec)
        pub_hex = priv.public_key.hex()
        typer.secho(f"🔑 Receiver private key: {pub_hex[:8]}...", fg=typer.colors.CYAN)
        
        default = DEFAULT_RELAYS
        chosen = relays if relays else default
        typer.secho(f"🌐 Using relays: {chosen}", fg=typer.colors.CYAN)

        # Connect to the first relay
        relay_url = chosen[0]
        typer.secho(f"🔌 Connecting to {relay_url}...", fg=typer.colors.CYAN)
        
        # Record start time to only process recent messages
        import time
        start_time = int(time.time())
        typer.secho(f"⏰ Started listening at: {start_time}", fg=typer.colors.CYAN)
    except Exception as e:
        typer.secho(f"❌ Error initializing receiver: {e}", fg=typer.colors.RED)
        return
    
    try:
        typer.secho(f"🔌 Attempting to connect to {relay_url}...", fg=typer.colors.CYAN)
        async with websockets.connect(relay_url) as websocket:
            typer.secho(f"✅ Connected to {relay_url}", fg=typer.colors.GREEN)
            
            # Subscribe to DMs for our pubkey
            req_msg = json.dumps(["REQ", "dm", {"kinds": [4], "#p": [pub_hex]}])
            typer.secho(f"📤 Sending subscription: {req_msg}", fg=typer.colors.CYAN)
            await websocket.send(req_msg)
            
            typer.secho(f"🔍 Subscribed to DMs for pubkey: {pub_hex[:8]}...", fg=typer.colors.BLUE)
            typer.secho("⏳ Waiting for incoming messages — press Ctrl+C to exit", fg=typer.colors.GREEN)
            
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
                                    typer.secho(f"📨 NEW FILE MESSAGE RECEIVED:", fg=typer.colors.BRIGHT_GREEN)
                                    typer.secho(f"   📝 Event ID: {ev_data['id'][:8]}...", fg=typer.colors.GREEN)
                                    typer.secho(f"   📝 From: {ev_data['pubkey'][:8]}...", fg=typer.colors.GREEN)
                                    typer.secho(f"   ⏰ Age: {abs(message_age)}s ago", fg=typer.colors.GREEN)
                                    
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
                typer.secho(f"\n👋 Stopping receiver... (processed {message_count} messages)", fg=typer.colors.YELLOW)
            except Exception as e:
                typer.secho(f"❌ Error in receive loop: {e}", fg=typer.colors.RED)
                
    except Exception as e:
        typer.secho(f"❌ Failed to connect to relay: {e}", fg=typer.colors.RED)
        typer.secho(f"❌ Exception type: {type(e)}", fg=typer.colors.RED)
        import traceback
        typer.secho(f"❌ Traceback: {traceback.format_exc()}", fg=typer.colors.RED)

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
