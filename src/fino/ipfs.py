import subprocess
import time
import requests
from pathlib import Path
from .console import console


def upload_to_ipfs(
    file_path: str, announce: bool = True, background_announce: bool = True
) -> str:
    """
    Upload file to IPFS - simple and fast with minimal network announcement
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        # Start IPFS daemon if not running
        _start_ipfs_daemon()

        # Upload file (pin by default; avoid redundant extra pin step)
        result = subprocess.run(
            ["ipfs", "add", "--pin=true", str(path)],
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

                    # Optional: Announce to DHT so other nodes can find it
                    if announce:
                        if background_announce:
                            console.print(
                                "   📡 Announcing to network (background)...",
                                style="cyan",
                            )
                            try:
                                subprocess.Popen(
                                    ["ipfs", "routing", "provide", cid],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                )
                            except Exception:
                                console.print(
                                    "   ⚠️  Background announce failed to start, but file uploaded",
                                    style="yellow",
                                )
                        else:
                            console.print(
                                "   📡 Announcing to network...", style="cyan"
                            )
                            try:
                                subprocess.run(
                                    ["ipfs", "routing", "provide", cid],
                                    capture_output=True,
                                    timeout=30,
                                )
                                console.print(
                                    "   ✅ File announced to network", style="green"
                                )
                            except (
                                subprocess.CalledProcessError,
                                subprocess.TimeoutExpired,
                            ):
                                console.print(
                                    "   ⚠️  Announce failed, but file uploaded",
                                    style="yellow",
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
    Download file from IPFS with fallback to HTTP gateways
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
            console.print("   ✅ Downloaded from local IPFS", style="green")
            return True
        else:
            console.print(
                "   ⚠️  Local IPFS download failed, trying HTTP gateways...",
                style="yellow",
            )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        console.print(
            "   ⚠️  Local IPFS not available, trying HTTP gateways...", style="yellow"
        )
    except Exception as e:
        console.print(
            f"   ⚠️  Local IPFS error: {e}, trying HTTP gateways...", style="yellow"
        )

    # Fallback to HTTP gateways
    gateways = [
        f"https://ipfs.io/ipfs/{cid}",
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}",
        f"https://dweb.link/ipfs/{cid}",
    ]

    for gateway_url in gateways:
        try:
            console.print(f"   🌐 Trying {gateway_url.split('/')[2]}...", style="cyan")

            response = requests.get(gateway_url, stream=True, timeout=30)
            response.raise_for_status()

            # Get file size for progress tracking
            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                downloaded = 0
                last_reported = 0
                last_report_time = time.time()
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MiB chunks
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Throttled progress for large files
                        if total_size > 0:
                            now = time.time()
                            bytes_since = downloaded - last_reported
                            if bytes_since >= 50 * 1024 * 1024 or (now - last_report_time) >= 2.0:
                                progress = (downloaded / total_size) * 100
                                console.print(
                                    f"   📥 Downloaded: {downloaded // (1024 * 1024)}MB / {total_size // (1024 * 1024)}MB ({progress:.1f}%)",
                                    style="cyan",
                                )
                                last_reported = downloaded
                                last_report_time = now

            console.print(
                f"   ✅ Downloaded from {gateway_url.split('/')[2]}", style="green"
            )
            return True

        except Exception as e:
            console.print(
                f"   ❌ {gateway_url.split('/')[2]} failed: {str(e)[:50]}...",
                style="red",
            )
            continue

    console.print("   ❌ All download methods failed", style="red")
    return False
