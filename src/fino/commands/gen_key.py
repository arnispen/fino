import typer
from pynostr.key import PrivateKey
from ..console import console, print_header, print_success_message, print_warning_message

app = typer.Typer(help="Generate new Nostr key pairs for file sharing")

@app.command()
def gen_key():
    """
    Generate a new Nostr key pair for secure file sharing with advanced features.
    
    This command creates a new private/public key pair in the Nostr format:
    - nsec: Private key (keep secret!)
    - npub: Public key (share with others)
    
    ⚠️  This is experimental software for innovation research only.
    """
    print_header("FiNo Key Generation", "Cryptographically Secure Key Pair")
    
    # Generate new key pair
    console.print("🔑 [bold]Generating cryptographically secure key pair...[/bold]", style="cyan")
    
    private_key = PrivateKey()
    
    # Display results
    console.print("\n✅ [bold]Key pair generated successfully![/bold]", style="bright_green")
    console.print("=" * 60, style="cyan")
    
    # Private key (red for security)
    console.print("🔐 [bold]Private Key (nsec):[/bold]", style="bright_red")
    console.print(f"   {private_key.bech32()}", style="red")
    console.print("   [italic]⚠️  Keep this secret! Never share it with anyone.[/italic]", style="red")
    console.print()
    
    # Public key (green for sharing)
    console.print("🔓 [bold]Public Key (npub):[/bold]", style="bright_green")
    console.print(f"   {private_key.public_key.bech32()}", style="green")
    console.print("   [italic]Share this with others to receive files.[/italic]", style="green")
    console.print()
    
    console.print("=" * 60, style="cyan")
    
    # Usage examples
    console.print("📝 [bold]Usage Examples:[/bold]", style="cyan")
    console.print("   Send file: [green]fino send document.pdf --to <npub> --from <nsec>[/green]", style="cyan")
    console.print("   Receive files: [green]fino receive --from <nsec>[/green]", style="cyan")

    
    console.print("=" * 60, style="cyan")
    
    # Security warnings
    print_warning_message("IMPORTANT: Keep your private key secure!")
    console.print("   🚫 Never share your nsec with anyone!", style="yellow")
    console.print("   ✅ You can share your npub with others.", style="green")
    console.print("   💾 Store your nsec in a secure password manager.", style="cyan")
    console.print("   🔄 Use this nsec with --from flag in send/receive commands.", style="cyan")
    
    console.print("\n⚠️  [italic]This is experimental software for innovation research only.[/italic]", style="yellow")
