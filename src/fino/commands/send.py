import typer
from pathlib import Path
from ..encryption import encrypt_file
from ..ipfs import upload_to_ipfs
from ..nostr import encrypt_payload, send_dm, DEFAULT_RELAYS
from ..utils import build_payload
from ..console import (
    console,
    print_header,
    print_step,
    print_file_info,
    print_success_message,
    create_progress_bar,
)

app = typer.Typer(help="Send encrypted files via Nostr DMs and IPFS storage")


@app.command()
def send(
    file: Path = typer.Argument(..., exists=True, help="File to send"),
    to: str = typer.Option(..., "--to", help="Recipient's npub (public key)"),
    from_nsec: str = typer.Option(..., "--from", help="Your nsec (private key)"),
):
    """
    Send an encrypted file via Nostr DMs and IPFS storage.

    This command:
    1. Encrypts the file with AES-256-CBC
    2. Uploads the encrypted file to IPFS
    3. Sends the decryption metadata via Nostr DMs
    4. Recipient can download and decrypt the file

    ⚠️  This is experimental software for innovation research only.
    """
    # Beautiful header
    print_header("FiNo File Sending Process", "Secure, Anonymous, Decentralized")

    # Show file info
    file_size = file.stat().st_size
    print_file_info(file.name, file_size, [])

    console.print("=" * 60, style="cyan")

    # Step 1: File encryption
    print_step(1, "Encrypting file with AES-256-CBC")
    with create_progress_bar("Encrypting file...") as progress:
        task = progress.add_task("Encrypting", total=100)
        ciphertext, key, nonce = encrypt_file(str(file))
        progress.update(task, completed=100)

    print_step(1, "File encryption completed", "success")
    console.print(f"   📊 Encrypted size: {len(ciphertext):,} bytes", style="green")

    # Step 2: IPFS upload
    print_step(2, "Uploading to IPFS")
    with create_progress_bar("Uploading to IPFS...") as progress:
        task = progress.add_task("Uploading", total=100)

        # Create temporary file for upload
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f"_{file.name}"
        ) as temp_file:
            temp_file.write(ciphertext)
            temp_file_path = temp_file.name

        try:
            cid = upload_to_ipfs(temp_file_path)
            progress.update(task, completed=100)
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    print_step(2, "IPFS upload completed", "success")
    console.print(f"   🔗 IPFS CID: {cid}", style="green")

    # Step 3: Metadata preparation
    print_step(3, "Preparing encrypted metadata")

    # Build payload
    payload = build_payload(cid, key, nonce, file.name)

    print_step(3, "Metadata preparation completed", "success")

    # Step 4: Send via Nostr
    print_step(4, "Sending via Nostr DM")
    with create_progress_bar("Sending encrypted metadata...") as progress:
        task = progress.add_task("Sending", total=100)
        enc = encrypt_payload(payload, to, from_nsec)
        send_dm(from_nsec, to, enc, DEFAULT_RELAYS)
        progress.update(task, completed=100)

    print_step(4, "Nostr transmission completed", "success")

    # Success message
    success_details = {
        "File": file.name,
        "Size": f"{file_size:,} bytes",
        "IPFS CID": cid,
        "Recipient": f"{to[:8]}...",
    }

    print_success_message("File sent successfully!", success_details)

    console.print(
        "\n⚠️  [italic]This is experimental software for innovation research only.[/italic]",
        style="yellow",
    )
