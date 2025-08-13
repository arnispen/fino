import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(filepath: str):
    data = open(filepath, "rb").read()
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return ciphertext, key, nonce


def decrypt_file(ciphertext: bytes, key: bytes, nonce: bytes):
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
