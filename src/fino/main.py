import typer
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fino.commands.send import send as send_cmd
from fino.commands.receive import receive as receive_cmd
from fino.commands.gen_key import gen_key as gen_key_cmd
from fino.commands.config import app as config_cmd

app = typer.Typer(
    help="🔐📁 FiNo: Proof-of-Concept Secure File Sharing via IPFS + Nostr DMs",
    add_completion=False,
    rich_markup_mode="rich"
)

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """
    [bold blue]FiNo[/bold blue] - [italic]File + Nostr[/italic]
    
    [yellow]Proof-of-Concept:[/yellow] Secure, decentralized file sharing using Nostr DMs and IPFS storage.
    
    [red]⚠️  This is experimental software for innovation research only.[/red]
    """
    if ctx.invoked_subcommand is None:
        typer.echo("\n[bold blue]🔐📁 Welcome to FiNo![/bold blue]")
        typer.echo("[italic]Secure File Sharing via IPFS + Nostr DMs[/italic]")
        typer.echo("\n[bold cyan]🚀 Quick Start:[/bold cyan]")
        typer.echo("  1. [green]fino gen-key[/green]                    - Generate your Nostr keys")
        typer.echo("  2. [green]fino send --file <file> --to <npub> --from <nsec>[/green]")
        typer.echo("  3. [green]fino receive --from <nsec>[/green]       - Listen for incoming files")
        typer.echo("\n[bold cyan]📖 Available Commands:[/bold cyan]")
        typer.echo("  [green]fino send[/green]     - Send encrypted files via Nostr DMs")
        typer.echo("  [green]fino receive[/green]  - Receive and decrypt files")
        typer.echo("  [green]fino gen-key[/green]  - Generate new Nostr key pair")
        typer.echo("  [green]fino config[/green]   - Manage global configuration")
        typer.echo("\n[bold cyan]💡 Pro Tips:[/bold cyan]")
        typer.echo("  • Use [yellow]--help[/yellow] with any command for detailed options")
        typer.echo("  • Files are saved to current directory by default")
        typer.echo("  • Only NEW files sent after starting receive are shown")
        typer.echo("\n[red]⚠️  For innovation research only - not for production use[/red]")
        raise typer.Exit(0)
    import fino.utils as utils
    utils.configure_logging(verbose, quiet, no_color, json_out)

app.command()(gen_key_cmd)
app.command()(send_cmd)
app.command()(receive_cmd)
app.add_typer(config_cmd, name="config", help="Manage global configuration")

def main():
    app()

if __name__ == "__main__":
    main()
