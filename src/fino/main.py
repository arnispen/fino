from dotenv import load_dotenv
import typer
from fino.commands.send import send as send_cmd
from fino.commands.receive import receive as receive_cmd
from fino.commands.gen_key import gen_key as gen_key_cmd

load_dotenv()

app = typer.Typer(
    help="🔐📁 FiNo: Decentralized Secure File Sharing via IPFS + Nostr",
    add_completion=False,
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all output"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """
    FiNo - File + Nostr

    Decentralized, secure file sharing using IPFS storage and Nostr messaging.
    No central servers, no API keys, completely free and censorship-resistant.

    ⚠️  This is experimental software for innovation research only.
    """
    if ctx.invoked_subcommand is None:
        from fino.console import console
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align

        welcome_text = Text("🔐📁 Welcome to FiNo!", style="bold blue")
        subtitle = Text("Secure File Sharing via IPFS + Nostr DMs", style="italic")

        panel = Panel(
            Align.center(welcome_text + "\n" + subtitle),
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)

        console.print("\n[bold cyan]🚀 Quick Start:[/bold cyan]")
        console.print(
            "  1. [green]fino gen-key[/green]                    - Generate your Nostr keys"
        )
        console.print("  2. [green]fino send {file} --to {npub} --from {nsec}[/green]")
        console.print(
            "  3. [green]fino receive --from {nsec}[/green]       - Listen for incoming files"
        )
        console.print("\n[bold cyan]📖 Available Commands:[/bold cyan]")
        console.print(
            "  [green]fino send[/green]     - Send encrypted files via IPFS + Nostr"
        )
        console.print("  [green]fino receive[/green]  - Receive and decrypt files")
        console.print("  [green]fino gen-key[/green]  - Generate new Nostr key pair")
        console.print("\n[bold cyan]💡 Pro Tips:[/bold cyan]")
        console.print(
            "  • Use [yellow]--help[/yellow] with any command for detailed options"
        )

        console.print("  • Files work globally - no central servers needed!")
        console.print(
            "\n[red]⚠️  For innovation research only - not for production use[/red]"
        )
        raise typer.Exit(0)
    import fino.utils as utils

    utils.configure_logging(verbose, quiet, no_color, json_out)


app.command()(gen_key_cmd)
app.command()(send_cmd)
app.command()(receive_cmd)


def main():
    app()


if __name__ == "__main__":
    main()
