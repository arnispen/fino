import typer
from pynostr.key import PrivateKey

app = typer.Typer(help="Generate new Nostr key pairs for file sharing")

@app.command()
def gen_key():
    """
    Generate a new Nostr key pair for secure file sharing.
    
    This command creates a new private/public key pair in the Nostr format:
    - nsec: Private key (keep secret!)
    - npub: Public key (share with others)
    
    ⚠️  This is experimental software for innovation research only.
    """
    typer.secho("🔐📁 [bold]FiNo Key Generation[/bold]", fg=typer.colors.BRIGHT_MAGENTA)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    
    # Generate new key pair
    typer.secho("🔑 [bold]Generating new Nostr key pair...[/bold]", fg=typer.colors.CYAN)
    private_key = PrivateKey()
    
    # Display results
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    typer.secho("🎉 [bold]Key pair generated successfully![/bold]", fg=typer.colors.BRIGHT_GREEN)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    
    typer.secho("🔐 [bold]Private Key (nsec):[/bold]", fg=typer.colors.RED)
    typer.secho(f"   {private_key.bech32()}", fg=typer.colors.RED)
    typer.secho("   [italic]⚠️  Keep this secret! Never share it with anyone.[/italic]", fg=typer.colors.RED)
    
    typer.secho("\n🔓 [bold]Public Key (npub):[/bold]", fg=typer.colors.GREEN)
    typer.secho(f"   {private_key.public_key.bech32()}", fg=typer.colors.GREEN)
    typer.secho("   [italic]Share this with others to receive files.[/italic]", fg=typer.colors.GREEN)
    
    typer.secho("\n" + "=" * 50, fg=typer.colors.CYAN)
    typer.secho("📝 [bold]Usage Examples:[/bold]", fg=typer.colors.CYAN)
    typer.secho("   Send file: [green]fino send --file document.pdf --to <npub> --from <nsec>[/green]", fg=typer.colors.CYAN)
    typer.secho("   Receive files: [green]fino receive --from <nsec>[/green]", fg=typer.colors.CYAN)
    typer.secho("=" * 50, fg=typer.colors.CYAN)
    typer.secho("⚠️  [italic]This is experimental software for innovation research only.[/italic]", fg=typer.colors.YELLOW)
