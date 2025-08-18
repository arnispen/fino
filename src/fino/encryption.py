import os
import gzip
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(filepath: str):
    data = open(filepath, "rb").read()
    # Compress before encrypting to reduce size and speed up upload
    compressed = gzip.compress(data, compresslevel=6)
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, compressed, None)
    return ciphertext, key, nonce


def decrypt_file(ciphertext: bytes, key: bytes, nonce: bytes):
    aesgcm = AESGCM(key)
    compressed = aesgcm.decrypt(nonce, ciphertext, None)
    # Decompress after decrypting
    return gzip.decompress(compressed)
