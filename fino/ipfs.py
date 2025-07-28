import requests
from typing import Optional
import io

PINATA_UPLOAD_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"
PINATA_GATEWAY_TEMPLATE = "https://gateway.pinata.cloud/ipfs/{cid}"


def upload_to_ipfs(file_bytes: bytes, jwt_token: str) -> str:
    """
    Uploads encrypted file bytes to IPFS via Pinata using a JWT.

    Args:
        file_bytes: Encrypted file content
        jwt_token: Pinata JWT token (Bearer)

    Returns:
        CID string

    Raises:
        Exception if upload fails
    """
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    # Use an in-memory file-like object for upload
    files = {
        "file": ("encrypted.bin", io.BytesIO(file_bytes), "application/octet-stream")
    }

    response = requests.post(PINATA_UPLOAD_URL, headers=headers, files=files)

    if response.status_code == 401:
        raise Exception("❌ Unauthorized: Invalid Pinata JWT token")
    elif not response.ok:
        raise Exception(f"❌ Upload failed: {response.status_code} {response.text}")

    cid = response.json().get("IpfsHash")
    if not cid:
        raise Exception("❌ Upload succeeded but no CID returned")

    print(f"📦 Uploaded to IPFS via Pinata. CID: {cid}")
    return cid


def download_from_ipfs(cid: str, gateway_template: Optional[str] = None) -> bytes:
    """
    Downloads file bytes from IPFS via Pinata gateway.

    Args:
        cid: IPFS content identifier
        gateway_template: Optional gateway URL template

    Returns:
        File bytes

    Raises:
        Exception if download fails
    """
    url_template = gateway_template or PINATA_GATEWAY_TEMPLATE
    url = url_template.format(cid=cid)

    response = requests.get(url)
    if response.status_code == 404:
        raise Exception("❌ File not found on IPFS (CID may be invalid)")
    elif not response.ok:
        raise Exception(f"❌ Download failed: {response.status_code} {response.text}")

    return response.content
