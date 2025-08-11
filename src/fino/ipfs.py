import requests
import subprocess
import tempfile
import os
from pathlib import Path
from .console import console

def upload_to_ipfs(data: bytes, filename: str) -> str:
    """
    Upload file to IPFS using local daemon
    
    Uses the local IPFS daemon for true decentralized storage.
    Files are accessible globally via IPFS network.
    """
    console.print("📤 Uploading to IPFS...", style="cyan")
    
    # Check if IPFS daemon is running
    if not _is_ipfs_daemon_running():
        console.print("   🔧 Starting IPFS daemon...", style="yellow")
        _start_ipfs_daemon()
    
    console.print("   🔗 Using local IPFS daemon", style="green")
    return _upload_via_ipfs_daemon(data, filename)

def download(cid: str) -> bytes:
    """
    Download file from IPFS
    
    Uses local IPFS daemon first, then falls back to public gateways.
    """
    console.print(f"📥 Downloading from IPFS: {cid[:8]}...", style="cyan")
    
    # Try local IPFS daemon first
    if _is_ipfs_daemon_running():
        try:
            console.print("   🔗 Using local IPFS daemon", style="green")
            return _download_via_ipfs_daemon(cid)
        except Exception as e:
            console.print(f"   ❌ Local IPFS failed: {str(e)[:50]}...", style="red")
    
    # Fallback to public gateways
    console.print("   🌐 Using public IPFS gateways", style="yellow")
    
    gateways = [
        "https://ipfs.io/ipfs/",
        "https://gateway.pinata.cloud/ipfs/",
        "https://cloudflare-ipfs.com/ipfs/",
        "https://dweb.link/ipfs/",
        "https://ipfs.fleek.co/ipfs/"
    ]
    
    for i, gateway in enumerate(gateways):
        try:
            url = f"{gateway}{cid}"
            console.print(f"   🔗 Trying gateway {i+1}/{len(gateways)}", style="cyan")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            console.print(f"   ✅ Downloaded successfully", style="green")
            return response.content
            
        except Exception as e:
            console.print(f"   ❌ Gateway {i+1} failed: {str(e)[:50]}...", style="red")
            continue
    
    raise Exception("All download methods failed")



def _is_ipfs_daemon_running() -> bool:
    """Check if IPFS daemon is running"""
    try:
        result = subprocess.run(
            ["ipfs", "id"], 
            capture_output=True, 
            timeout=5,
            text=True
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def _start_ipfs_daemon():
    """Start IPFS daemon in background"""
    try:
        # Start daemon in background
        subprocess.Popen(
            ["ipfs", "daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a moment for daemon to start
        import time
        time.sleep(3)
        
        console.print("   ✅ IPFS daemon started", style="green")
    except Exception as e:
        console.print(f"   ❌ Failed to start IPFS daemon: {e}", style="red")
        raise

def _upload_via_ipfs_daemon(data: bytes, filename: str) -> str:
    """Upload using IPFS daemon"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name
        
        # Upload to IPFS
        result = subprocess.run(
            ["ipfs", "add", "--quiet", temp_file_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if result.returncode == 0:
            cid = result.stdout.strip()
            console.print(f"   ✅ Uploaded to IPFS: {cid}", style="green")
            return cid
        else:
            raise Exception(f"IPFS add failed: {result.stderr}")
            
    except Exception as e:
        console.print(f"   ❌ IPFS upload failed: {e}", style="red")
        raise

def _download_via_ipfs_daemon(cid: str) -> bytes:
    """Download using IPFS daemon"""
    try:
        # Download from IPFS
        result = subprocess.run(
            ["ipfs", "cat", cid],
            capture_output=True,
            timeout=60
        )
        
        if result.returncode == 0:
            console.print(f"   ✅ Downloaded from IPFS daemon", style="green")
            return result.stdout
        else:
            raise Exception(f"IPFS cat failed: {result.stderr}")
            
    except Exception as e:
        console.print(f"   ❌ IPFS download failed: {e}", style="red")
        raise

def get_ipfs_info() -> dict:
    """Get information about IPFS setup"""
    info = {
        "daemon_running": _is_ipfs_daemon_running(),
        "storage_method": "ipfs_daemon" if _is_ipfs_daemon_running() else "public_gateways"
    }
    return info
