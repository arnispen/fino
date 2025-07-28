import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(filepath: str) -> Tuple[bytes, bytes, bytes]:
    """
    Encrypts a file using AES-256-GCM.

    Returns:
        - ciphertext (bytes): Encrypted file content
        - key (bytes): AES key (32 bytes)
        - nonce (bytes): Nonce used for encryption (12 bytes)
    """
    with open(filepath, "rb") as f:
        plaintext = f.read()

    key = AESGCM.generate_key(bit_length=256)  # 32 bytes
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 12 bytes for AES-GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return ciphertext, key, nonce


def decrypt_file(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
    """
    Decrypts AES-256-GCM encrypted bytes.

    Returns:
        - plaintext (bytes): Original file content
    Raises:
        - cryptography.exceptions.InvalidTag: if decryption fails
    """
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted_data, None)
