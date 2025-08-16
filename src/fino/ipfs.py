import subprocess
import time
from pathlib import Path
from rich.console import Console

console = Console()


def upload_to_ipfs(file_path: str) -> str:
    """
    Upload file to IPFS - simple and fast with minimal network announcement
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        # Start IPFS daemon if not running
        _start_ipfs_daemon()

        # Upload file
        result = subprocess.run(
            ["ipfs", "add", str(path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )

        # Extract CID from output
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if "added" in line:
                parts = line.split()
                if len(parts) >= 2:
                    cid = parts[1]  # The CID is the second word
                    console.print(f"   ✅ Uploaded to IPFS: {cid}", style="green")

                    # Pin the file
                    subprocess.run(["ipfs", "pin", "add", cid], capture_output=True)
                    console.print("   📌 File pinned", style="green")

                    # Essential: Announce to DHT so other nodes can find it
                    console.print("   📡 Announcing to network...", style="cyan")
                    try:
                        subprocess.run(
                            ["ipfs", "dht", "provide", cid],
                            capture_output=True,
                            timeout=30,
                        )
                        console.print("   ✅ File announced to network", style="green")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        console.print(
                            "   ⚠️  Announce failed, but file uploaded", style="yellow"
                        )

                    return cid

        raise Exception("Could not extract CID from IPFS output")

    except Exception as e:
        console.print(f"   ❌ IPFS upload failed: {e}", style="red")
        raise


def _start_ipfs_daemon():
    """Start IPFS daemon if not running"""
    try:
        # Check if daemon is already running
        try:
            subprocess.run(["ipfs", "id"], capture_output=True, check=True, timeout=5)
            return
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
        ):
            pass

        # Start daemon in background
        subprocess.Popen(
            ["ipfs", "daemon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        # Wait for daemon to start
        time.sleep(3)

    except Exception as e:
        console.print(f"   ❌ Failed to start IPFS daemon: {e}", style="red")
        raise


def download_from_ipfs(cid: str, output_path: str) -> bool:
    """
    Download file from IPFS
    """
    console.print(f"   🔍 Downloading {cid} from IPFS...", style="cyan")

    # Try local IPFS first
    try:
        result = subprocess.run(
            ["ipfs", "get", cid, "-o", output_path],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            console.print("   ✅ Downloaded from IPFS", style="green")
            return True
        else:
            console.print("   ❌ Local IPFS download failed", style="red")
            return False

    except Exception as e:
        console.print(f"   ❌ IPFS error: {e}", style="red")
        return False
