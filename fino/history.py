import json
from pathlib import Path
from datetime import datetime


def get_history_path(profile: str) -> Path:
    base = Path.home() / ".fino" / "profiles" / profile
    base.mkdir(parents=True, exist_ok=True)
    return base / "history.json"


def log_received_file(profile: str, cid: str, sender_npub: str, filename: str):
    history_path = get_history_path(profile)

    entry = {
        "cid": cid,
        "sender": sender_npub,
        "filename": filename,
        "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{cid}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if history_path.exists():
        with open(history_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)

    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    print(f"📝 Logged to history: {filename}")


def list_received_files(profile: str, limit: int = None):
    history_path = get_history_path(profile)

    if not history_path.exists():
        return []

    with open(history_path, "r") as f:
        history = json.load(f)

    if limit:
        history = history[-limit:]

    return history
