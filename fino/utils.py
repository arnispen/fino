import bech32
from typing import Tuple


def bech32_encode(prefix: str, data: bytes) -> str:
    """Encode bytes into NIP-19 bech32 string (e.g. npub1..., nsec1...)"""
    five_bit_data = bech32.convertbits(data, 8, 5, True)
    return bech32.bech32_encode(prefix, five_bit_data)


def bech32_decode(bech32_key: str) -> Tuple[str, bytes]:
    """Decode NIP-19 bech32 string into (prefix, bytes)"""
    prefix, data = bech32.bech32_decode(bech32_key)
    if data is None:
        raise ValueError("Invalid bech32 string")
    byte_data = bech32.convertbits(data, 5, 8, False)
    return prefix, bytes(byte_data)
