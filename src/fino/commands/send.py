import typer
from pathlib import Path
from ..encryption import encrypt_file
from ..ipfs import upload_to_pinata
from ..nostr import encrypt_payload, send_dm
from ..utils import build_payload

app = typer.Typer(help="Send encrypted files via Nostr DMs and IPFS storage")

@app.command()
def send(
    file: Path = typer.Argument(..., exists=True, help="File to send"),
    to: str = typer.Option(..., "--to", help="Recipient's npub (public key)"),
    from_nsec: str = typer.Option(..., "--from", help="Your nsec (private key)"),
    pinata_jwt: str = typer.Option("default", "--pinata-jwt", help="Pinata JWT token for IPFS storage"),
    relay: str = typer.Option("wss://nos.lol", "--relay", help="Nostr relay URL"),
):
    """
    Send an encrypted file via Nostr DMs and IPFS storage.
    
    This command:
    1. Encrypts the file with AES-256-CBC
    2. Uploads encrypted file to IPFS via Pinata
    3. Encrypts metadata (CID, key, nonce) with recipient's public key
    4. Sends encrypted metadata via Nostr DM
    
    ⚠️  This is experimental software for innovation research only.
    """
    typer.secho("🔐📁 [bold]FiNo File Sending Process[/bold]", fg=typer.colors.BRIGHT_MAGENTA)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    
    # Show file info
    file_size = file.stat().st_size
    typer.secho(f"📁 File: {file.name} ({file_size:,} bytes)", fg=typer.colors.CYAN)
    typer.secho(f"👤 Recipient: {to[:8]}...", fg=typer.colors.CYAN)
    typer.secho(f"📡 Relay: {relay}", fg=typer.colors.CYAN)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    
    # Step 1: File encryption
    typer.secho("🔒 [bold]Step 1:[/bold] Encrypting file...", fg=typer.colors.CYAN)
    ciphertext, key, nonce = encrypt_file(str(file))
    typer.secho(f"   ✅ File encrypted: {len(ciphertext):,} bytes", fg=typer.colors.GREEN)
    
    # Step 2: IPFS upload
    typer.secho("🌐 [bold]Step 2:[/bold] Uploading to IPFS...", fg=typer.colors.CYAN)
    cid = upload_to_pinata(ciphertext, file.name, pinata_jwt)
    typer.secho(f"   ✅ Uploaded to IPFS: {cid}", fg=typer.colors.GREEN)
    
    # Step 3: Metadata encryption and sending
    typer.secho("📡 [bold]Step 3:[/bold] Sending via Nostr DM...", fg=typer.colors.CYAN)
    payload = build_payload(cid, key, nonce, file.name)
    enc = encrypt_payload(payload, to, from_nsec)
    send_dm(from_nsec, to, enc, [relay])
    
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    typer.secho("🎉 [bold]File sent successfully![/bold]", fg=typer.colors.BRIGHT_GREEN)
    typer.secho(f"📁 File: {file.name}", fg=typer.colors.GREEN)
    typer.secho(f"📊 Size: {file_size:,} bytes", fg=typer.colors.GREEN)
    typer.secho(f"🔗 IPFS CID: {cid}", fg=typer.colors.GREEN)
    typer.secho(f"👤 Recipient: {to[:8]}...", fg=typer.colors.GREEN)
    typer.secho("⚠️  [italic]This is experimental software for innovation research only.[/italic]", fg=typer.colors.YELLOW)
