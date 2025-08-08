import typer
from ..nostr import receive_loop, decrypt_payload
from ..ipfs import download
from ..encryption import decrypt_file
from ..utils import build_filename_from_payload

app = typer.Typer(help="Receive and decrypt files via Nostr DMs and IPFS")

@app.command()
def receive(
    from_nsec: str = typer.Option(..., "--from", help="Your nsec (private key)"),
    pinata_jwt: str = typer.Option("default", "--pinata-jwt", help="Pinata JWT token for IPFS storage"),
    relay: str = typer.Option("wss://nos.lol", "--relay", help="Nostr relay URL"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="Directory to save received files (default: current directory)"),
):
    """
    Receive and decrypt files via Nostr DMs and IPFS storage.
    
    This command:
    1. Connects to Nostr relay and listens for DMs
    2. Decrypts received metadata (CID, key, nonce)
    3. Downloads encrypted file from IPFS
    4. Decrypts and saves the file locally
    
    ⚠️  This is experimental software for innovation research only.
    """
    typer.secho("🔐📁 [bold]FiNo File Receiving Process[/bold]", fg=typer.colors.BRIGHT_MAGENTA)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    typer.secho("🎧 [bold]Starting receiver...[/bold]", fg=typer.colors.CYAN)
    typer.secho("   📡 Relay: " + relay, fg=typer.colors.CYAN)
    typer.secho("   💾 Output: " + (output_dir or "current directory"), fg=typer.colors.CYAN)
    typer.secho("   🔍 Only showing NEW files sent to you", fg=typer.colors.CYAN)
    typer.secho("   ⏹️  Press Ctrl+C to stop", fg=typer.colors.CYAN)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    typer.secho("🔄 Connecting to relay...", fg=typer.colors.YELLOW)
    
    def callback(event):
        typer.secho("🔄 [bold]PROCESSING RECEIVED FILE[/bold]", fg=typer.colors.BRIGHT_MAGENTA)
        typer.secho("-" * 40, fg=typer.colors.CYAN)
        
        # Step 1: Decrypt metadata
        typer.secho("🔓 [bold]Step 1:[/bold] Decrypting metadata...", fg=typer.colors.CYAN)
        try:
            p = decrypt_payload(event, from_nsec)
            typer.secho(f"   ✅ Metadata decrypted: CID {p['cid'][:8]}...", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"   ❌ Failed to decrypt metadata: {e}", fg=typer.colors.RED)
            import traceback
            typer.secho(f"   ❌ Traceback: {traceback.format_exc()}", fg=typer.colors.RED)
            return
        
        # Step 2: Download from IPFS
        typer.secho("📥 [bold]Step 2:[/bold] Downloading from IPFS...", fg=typer.colors.CYAN)
        data = download(p["cid"])
        typer.secho(f"   ✅ Downloaded: {len(data):,} bytes", fg=typer.colors.GREEN)
        
        # Step 3: Decrypt file
        typer.secho("🔓 [bold]Step 3:[/bold] Decrypting file...", fg=typer.colors.CYAN)
        plaintext = decrypt_file(data, bytes.fromhex(p["key"]), bytes.fromhex(p["nonce"]))
        typer.secho(f"   ✅ File decrypted: {len(plaintext):,} bytes", fg=typer.colors.GREEN)
        
        # Step 4: Save file
        import os
        
        # Determine output directory
        if output_dir:
            # Use specified output directory
            os.makedirs(output_dir, exist_ok=True)
            save_dir = output_dir
        else:
            # Use current working directory
            save_dir = "."
        
        fname = build_filename_from_payload(p)
        filepath = os.path.join(save_dir, fname)
        typer.secho("💾 [bold]Step 4:[/bold] Saving file...", fg=typer.colors.CYAN)
        typer.secho(f"   📁 Path: {filepath}", fg=typer.colors.CYAN)
        
        with open(filepath, "wb") as f:
            f.write(plaintext)
        
        typer.secho("-" * 40, fg=typer.colors.CYAN)
        typer.secho("🎉 [bold]File received successfully![/bold]", fg=typer.colors.BRIGHT_GREEN)
        typer.secho(f"📁 Saved: {filepath}", fg=typer.colors.GREEN)
        typer.secho(f"📊 Size: {len(plaintext):,} bytes", fg=typer.colors.GREEN)
        typer.secho("⚠️  [italic]This is experimental software for innovation research only.[/italic]", fg=typer.colors.YELLOW)
        typer.secho("=" * 50, fg=typer.colors.CYAN)
    
    receive_loop(from_nsec, [relay], callback)
