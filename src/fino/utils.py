import os
import typer
import logging
import json
from pathlib import Path

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

def load_config() -> dict:
    """Load global configuration"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_config(config: dict):
    """Save global configuration"""
    config_file = get_config_file()
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def get_config_value(key: str, default: str = None) -> str:
    """Get a configuration value"""
    config = load_config()
    return config.get(key, default)

def set_config_value(key: str, value: str):
    """Set a configuration value"""
    config = load_config()
    config[key] = value
    save_config(config)

def resolve_jwt() -> str:
    """Get Pinata JWT from global config or environment variable"""
    # First try global config
    jwt = get_config_value("pinata_jwt")
    if jwt:
        return jwt
    
    # Fallback to environment variable
    jwt = os.getenv("PINATA_JWT_DEFAULT")
    if jwt:
        return jwt
    
    # If neither exists, guide user to set it
    typer.secho("❌ Pinata JWT not configured", fg=typer.colors.RED)
    typer.secho("💡 Run 'fino config set pinata-jwt' to configure it", fg=typer.colors.YELLOW)
    typer.secho("   Or set PINATA_JWT_DEFAULT environment variable", fg=typer.colors.YELLOW)
    raise typer.Exit(1)

def build_payload(cid: str, key: bytes, nonce: bytes, original_filename: str = None) -> dict:
    payload = {"cid": cid, "key": key.hex(), "nonce": nonce.hex()}
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
