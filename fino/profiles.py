import os
import json
import base64
import getpass
import hashlib
from typing import Optional, Tuple
from pathlib import Path

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes

from ecdsa import SigningKey, SECP256k1
from fino.utils import bech32_encode, bech32_decode


DEFAULT_CONFIG_PATH = os.path.expanduser("~/.fino/profiles")
KDF_ITERATIONS = 100_000


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def generate_keypair() -> Tuple[bytes, str, str]:
    sk = SigningKey.generate(curve=SECP256k1)
    privkey = sk.to_string()
    pubkey = sk.verifying_key.to_string("compressed")
    nsec = bech32_encode("nsec", privkey)
    npub = bech32_encode("npub", pubkey)
    return privkey, nsec, npub


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password.encode())


def encrypt_nsec(nsec_bytes: bytes, password: str) -> Tuple[str, str, str]:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, nsec_bytes, None)
    return (
        base64.b64encode(encrypted).decode(),
        base64.b64encode(salt).decode(),
        base64.b64encode(nonce).decode()
    )


def decrypt_nsec(encrypted: str, password: str, salt: str, nonce: str) -> bytes:
    try:
        encrypted_bytes = base64.b64decode(encrypted)
        salt_bytes = base64.b64decode(salt)
        nonce_bytes = base64.b64decode(nonce)
        key = derive_key(password, salt_bytes)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce_bytes, encrypted_bytes, None)
    except Exception:
        raise ValueError("❌ Incorrect password or corrupted profile.")


def get_profile_path(name: str, config_path: Optional[str]) -> str:
    base = config_path or DEFAULT_CONFIG_PATH
    ensure_dir(base)
    return os.path.join(base, f"{name}.json")


def init_profile(name: str, config_path: Optional[str] = None):
    print(f"🔐 Creating profile '{name}'")
    password = getpass.getpass("Set password to protect your key (leave blank for no encryption): ")

    privkey, nsec, npub = generate_keypair()
    data = {
        "name": name,
        "npub": npub
    }

    if password:
        enc_nsec, salt, nonce = encrypt_nsec(privkey, password)
        data.update({
            "nsec_enc": enc_nsec,
            "salt": salt,
            "nonce": nonce
        })
    else:
        data["nsec_plain"] = base64.b64encode(privkey).decode()

    path = get_profile_path(name, config_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("\n✅ Profile created.")
    print(f"🔑 Public Key (share this): {npub}")
    print(f"🔒 Private Key (KEEP SECRET): {nsec}")
    print(f"📁 Saved to: {path}")


def load_profile(name: str, config_path: Optional[str] = None) -> Tuple[bytes, str]:
    path = get_profile_path(name, config_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Profile '{name}' not found at {path}")

    with open(path, "r") as f:
        data = json.load(f)

    npub = data["npub"]

    if "nsec_plain" in data:
        nsec_bytes = base64.b64decode(data["nsec_plain"])
        return nsec_bytes, npub

    if "nsec_enc" in data:
        password = getpass.getpass(f"Enter password for profile '{name}': ")
        return decrypt_nsec(
            data["nsec_enc"],
            password,
            data["salt"],
            data["nonce"]
        ), npub

    raise ValueError("❌ Invalid profile format.")


def list_profiles(config_path: Optional[str] = None) -> list:
    base = config_path or DEFAULT_CONFIG_PATH
    if not os.path.exists(base):
        return []
    return [f[:-5] for f in os.listdir(base) if f.endswith(".json")]
