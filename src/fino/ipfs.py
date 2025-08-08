import requests
from .utils import resolve_jwt

UPLOAD_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

def upload_to_pinata(data: bytes, filename: str) -> str:
    token = resolve_jwt()
    resp = requests.post(UPLOAD_URL, files={"file": (filename, data)}, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()["IpfsHash"]

def download(cid: str) -> bytes:
    # Use public IPFS gateway
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.content
