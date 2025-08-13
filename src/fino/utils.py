import logging
import json
from pathlib import Path
from typing import Any, Dict, Optional


def configure_logging(verbose: bool, quiet: bool, no_color: bool, json_out: bool):
    """Minimal logging setup to satisfy CLI hook and tests."""
    level = logging.DEBUG if verbose else logging.INFO
    if quiet:
        level = logging.ERROR
    logging.basicConfig(level=level, format="%(message)s")


def get_config_dir() -> Path:
    """Get the directory for storing global configuration"""
    config_dir = Path.home() / ".fino"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the global configuration file"""
    return get_config_dir() / "config.json"


def load_config() -> Dict[str, Any]:
    """Load global configuration"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save global configuration"""
    config_file = get_config_file()
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value"""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: str) -> None:
    """Set a configuration value"""
    config = load_config()
    config[key] = value
    save_config(config)


def build_payload(
    cid: str, key: bytes, nonce: bytes, original_filename: Optional[str] = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"cid": cid, "key": key.hex(), "nonce": nonce.hex()}
    if original_filename:
        payload["filename"] = original_filename
    return payload


def build_filename_from_payload(payload: dict) -> str:
    """Build filename from payload, using original filename if available"""
    if "filename" in payload:
        return payload["filename"]
    else:
        # Fallback to CID-based filename
        return f"{payload['cid'][:8]}.bin"
