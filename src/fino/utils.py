import os
import typer
import logging

def configure_logging(verbose: bool, quiet: bool, no_color: bool, json_out: bool):
    """Minimal logging setup to satisfy CLI hook and tests.""" 
    level = logging.DEBUG if verbose else logging.INFO
    if quiet:
        level = logging.ERROR
    logging.basicConfig(level=level, format="%(message)s")

def resolve_jwt(alias: str) -> str:
    token = os.getenv(f"PINATA_JWT_{alias}")
    if not token:
        token = alias
    if not token:
        typer.secho("Error: missing Pinata JWT (alias or raw token)", fg=typer.colors.RED)
        raise typer.Exit(1)
    return token

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
