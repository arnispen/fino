import typer
import os
from ..nostr import receive_loop, decrypt_payload, DEFAULT_RELAYS
from ..ipfs import download_from_ipfs
from ..encryption import decrypt_file
from ..utils import build_filename_from_payload
from ..console import (
    console,
    print_header,
    print_step,
    print_success_message,
    print_error_message,
    create_progress_bar,
    print_file_info,
)

app = typer.Typer(help="Receive and decrypt files via Nostr DMs and IPFS")


@app.command()
def receive(
    from_nsec: str = typer.Option(..., "--from", help="Your nsec (private key)"),
    output_dir: str = typer.Option(
        ".",
        "--output-dir",
        "-o",
        help="Directory to save received files (default: current directory)",
    ),
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
    # Beautiful header
    print_header("FiNo File Receiving Process", "Listening for encrypted files...")

    # Show receiver info
    console.print(
        f"👤 [bold]Listening for messages from:[/bold] {from_nsec[:8]}...", style="cyan"
    )
    console.print(f"📁 [bold]Output directory:[/bold] {output_dir}", style="cyan")
    console.print(f"📡 [bold]Relay(s):[/bold] {DEFAULT_RELAYS}", style="cyan")
    console.print("🔧 [bold]Download method:[/bold] IPFS", style="cyan")

    console.print("=" * 60, style="cyan")

    # Create output directory if it's not the current directory
    if output_dir != ".":
        os.makedirs(output_dir, exist_ok=True)

    def callback(event):
        console.print("\n" + "=" * 60, style="bright_magenta")
        console.print(
            "📨 [bold]NEW FILE MESSAGE RECEIVED![/bold]", style="bright_green"
        )
        console.print("=" * 60, style="bright_magenta")

        # Step 1: Decrypt metadata
        print_step(1, "Decrypting metadata")
        try:
            with create_progress_bar("Decrypting metadata...") as progress:
                task = progress.add_task("Decrypting", total=100)
                payload = decrypt_payload(event, from_nsec)
                progress.update(task, completed=100)

            print_step(1, "Metadata decryption completed", "success")
            console.print(f"   🔗 IPFS CID: {payload['cid'][:8]}...", style="green")

        except Exception as e:
            print_step(1, "Metadata decryption failed", "error")
            print_error_message("Failed to decrypt metadata", e)
            return

        # Step 2: Download from IPFS
        print_step(2, "Downloading from IPFS")
        try:
            with create_progress_bar("Downloading from IPFS...") as progress:
                task = progress.add_task("Downloading", total=100)

                # Create temporary file for download
                import tempfile

                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file_path = temp_file.name
                temp_file.close()

                try:
                    success = download_from_ipfs(payload["cid"], temp_file_path)
                    if not success:
                        raise Exception("Download failed from all sources")

                    # Read the downloaded data
                    with open(temp_file_path, "rb") as f:
                        data = f.read()

                    progress.update(task, completed=100)
                finally:
                    # Clean up temp file
                    os.unlink(temp_file_path)

            print_step(2, "IPFS download completed", "success")
            console.print(f"   📊 Downloaded: {len(data):,} bytes", style="green")

        except Exception as e:
            print_step(2, "IPFS download failed", "error")
            print_error_message("Failed to download from IPFS", e)
            return

        # Step 3: Decrypt file
        print_step(3, "Decrypting file")
        try:
            with create_progress_bar("Decrypting file...") as progress:
                task = progress.add_task("Decrypting", total=100)
                plaintext = decrypt_file(
                    data, bytes.fromhex(payload["key"]), bytes.fromhex(payload["nonce"])
                )
                progress.update(task, completed=100)

            print_step(3, "File decryption completed", "success")
            console.print(f"   📊 Decrypted: {len(plaintext):,} bytes", style="green")

        except Exception as e:
            print_step(3, "File decryption failed", "error")
            print_error_message("Failed to decrypt file", e)
            return

        # Step 4: Save file
        print_step(4, "Saving file")

        filename = build_filename_from_payload(payload)
        filepath = os.path.join(output_dir, filename)

        # Save file
        with open(filepath, "wb") as f:
            f.write(plaintext)

        print_step(4, "File saved successfully", "success")
        console.print(f"   📁 Saved: {filepath}", style="green")

        print_file_info(filename, len(plaintext), [])

        # Success message
        success_details = {
            "File": filename,
            "Size": f"{len(plaintext):,} bytes",
            "Saved to": filepath,
        }

        print_success_message("File received successfully!", success_details)

        console.print("=" * 60, style="bright_magenta")

    # Start listening
    console.print("🎧 [bold]Starting to listen for Nostr DMs...[/bold]", style="cyan")
    console.print("   📡 Waiting for file transfer messages...", style="cyan")
    console.print("   ⏹️  Press Ctrl+C to stop", style="cyan")
    console.print("=" * 60, style="cyan")

    try:
        receive_loop(from_nsec, DEFAULT_RELAYS, callback)
    except KeyboardInterrupt:
        console.print("\n👋 [bold]Stopping receiver...[/bold]", style="yellow")
    except Exception as e:
        print_error_message("Receiver error", e)
